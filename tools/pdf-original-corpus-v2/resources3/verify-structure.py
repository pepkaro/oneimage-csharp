#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Parse original page trees without flattening and check inherited resource owners."""
from pathlib import Path
import json,hashlib,pypdf
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
assert pypdf.__version__=='6.21.4'

def main():
 m=json.loads((ROOT/'manifest.json').read_text());rows=[];fixtures=[]
 for fixture in m['fixtures']:
  src=ROOT/fixture['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==fixture['sha256'];reader=PdfReader(src,strict=True);pages=[];seen=set();nodes=[]
  def walk(ref,parent=None,effective=None):
   number=ref.idnum;assert number not in seen;seen.add(number);node=ref.get_object()
   if parent is None:assert '/Parent' not in node
   else:assert node.raw_get('/Parent').idnum==parent
   local=node.get('/Resources')
   if local is not None:effective=(number,local.get_object())
   assert effective is not None
   if node['/Type']=='/Pages':
    count=sum(walk(child,number,effective) for child in node['/Kids']);assert count==node['/Count'];nodes.append(dict(object=number,count=count,has_local_resources=local is not None));return count
   assert node['/Type']=='/Page';owner,res=effective;mark=res['/XObject'].raw_get('/Mark');leaf=mark.get_object();assert leaf['/Subtype']=='/Form' and len(leaf['/Resources'])==0
   assert leaf.get_data() in [b'1 0 0 rg 0 0 30 25 re f',b'0 0 1 rg 0 0 30 25 re f'];assert b'/Mark Do' in node['/Contents'].get_object().get_data()
   pages.append(dict(page=len(pages),page_object=number,resource_owner_object=owner,mark_leaf_object=mark.idnum,has_explicit_page_resources=local is not None));return 1
  count=walk(reader.trailer['/Root'].raw_get('/Pages'));assert count==fixture['page_count'];fixtures.append(dict(fixture_id=fixture['id'],file=fixture['file'],page_count=count,page_tree_nodes=nodes,parsed_pages=pages))
  for case in [c for c in m['cases'] if c['fixture_id']==fixture['id']]:
   actual=pages[case['page']];assert actual['resource_owner_object']==case['expected_resource_owner_object'] and actual['mark_leaf_object']==case['expected_leaf_object'];assert actual['has_explicit_page_resources']==(case['id']=='resource-explicit-page')
   rows.append(dict(id=case['id'],fixture_id=case['fixture_id'],file=case['file'],page=case['page'],passed=True,**{k:v for k,v in actual.items() if k!='page'}))
 result=dict(parser='pypdf',parser_version=pypdf.__version__,unique_pdfs=3,page_views=5,passed=len(rows),failed=0,fixtures=fixtures,rows=rows);assert len(rows)==5;(ROOT/'structure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows','fixtures']},indent=2))
if __name__=='__main__':main()
