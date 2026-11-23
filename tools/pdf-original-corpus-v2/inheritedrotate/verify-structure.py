#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Raw-tree inherited Rotate plus independently transformed parsed rectangle corners."""
from pathlib import Path
import json,hashlib,math,pypdf
from pypdf import PdfReader
from pypdf.generic import ContentStream
ROOT=Path(__file__).resolve().parent
assert pypdf.__version__=='6.21.4'

def main():
 m=json.loads((ROOT/'manifest.json').read_text());fixture_rows=[];rows=[]
 for fixture in m['fixtures']:
  src=ROOT/fixture['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==fixture['sha256'];reader=PdfReader(src,strict=True);pages=[];seen=set();nodes=[]
  def walk(ref,parent=None,inherited=None):
   number=ref.idnum;assert number not in seen;seen.add(number);node=ref.get_object()
   if parent is None:assert '/Parent' not in node
   else:assert node.raw_get('/Parent').idnum==parent
   local=node.get('/Rotate')
   if local is not None:inherited=(number,int(local))
   assert inherited is not None
   if node['/Type']=='/Pages':
    count=sum(walk(child,number,inherited) for child in node['/Kids']);assert count==node['/Count'];nodes.append(dict(object=number,count=count,local_rotation=None if local is None else int(local)));return count
   assert node['/Type']=='/Page' and len(node['/Resources'])==0 and '/UserUnit' not in node
   media=[float(v) for v in node['/MediaBox']];crop=[float(v) for v in node['/CropBox']];assert media==crop==[10,20,170,120]
   owner,rotation=inherited;assert rotation in [0,90,270];x0,y0,x1,y1=crop;w=x1-x0;h=y1-y0
   angle=math.radians(rotation);cos=round(math.cos(angle));sin=round(math.sin(angle))
   turn=lambda x,y:(cos*x+sin*y,-sin*x+cos*y)
   corners=[turn(x,y) for x,y in [(0,0),(w,0),(0,h),(w,h)]];minx=min(x for x,y in corners);maxx=max(x for x,y in corners);miny=min(y for x,y in corners);maxy=max(y for x,y in corners);width=maxx-minx;height=maxy-miny
   operations=ContentStream(node['/Contents'],reader).operations;assert [op for _,op in operations]==[b'rg',b're',b'f',b'rg',b're',b'f'];rects=[];color=None
   for operands,op in operations:
    if op==b'rg':color=[round(float(v)*255) for v in operands]
    if op==b're':
     x,y,rw,rh=map(float,operands);points=[turn(a-x0,b-y0) for a,b in [(x,y),(x+rw,y),(x,y+rh),(x+rw,y+rh)]];left=min(a for a,b in points)-minx;bottom=min(b for a,b in points)-miny;rects.append([left,bottom,max(a for a,b in points)-min(a for a,b in points),max(b for a,b in points)-min(b for a,b in points),color])
   transform=[cos,sin,sin,-cos,-cos*x0-sin*y0-minx,height-sin*x0+cos*y0+miny]
   pages.append(dict(page=len(pages),page_object=number,rotate_owner_object=owner,rotation=rotation,media_box=media,crop_box=crop,width=width,height=height,has_explicit_page_rotation=local is not None,transformed_rectangles=rects,device_transform_72=transform));return 1
  count=walk(reader.trailer['/Root'].raw_get('/Pages'));assert count==fixture['page_count'];fixture_rows.append(dict(fixture_id=fixture['id'],file=fixture['file'],page_count=count,page_tree_nodes=nodes,parsed_pages=pages))
  for case in [c for c in m['cases'] if c['fixture_id']==fixture['id']]:
   actual=pages[case['page']];assert actual['rotate_owner_object']==case['expected_rotate_owner_object'] and actual['rotation']==case['rotation'];assert actual['width']==case['width'] and actual['height']==case['height'];assert actual['transformed_rectangles']==case['shape_rectangles'] and actual['device_transform_72']==case['expected_device_transform_at_72'];assert actual['has_explicit_page_rotation']==(case['id']=='rotate-explicit-page0')
   rows.append(dict(id=case['id'],fixture_id=case['fixture_id'],file=case['file'],page=case['page'],passed=True,**{k:v for k,v in actual.items() if k!='page'}))
 result=dict(parser='pypdf',parser_version=pypdf.__version__,unique_pdfs=3,page_views=5,passed=len(rows),failed=0,fixtures=fixture_rows,rows=rows);assert len(rows)==5;(ROOT/'structure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows','fixtures']},indent=2))
if __name__=='__main__':main()
