#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Three original valid PDF1.7 page-tree resource fixtures; five independent page views."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
def stream(content,entries=''):
 data=content.encode();return f'<< {entries} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'
def leaf(rgb):return stream(rgb+' rg 0 0 30 25 re f','/Type /XObject /Subtype /Form /BBox [0 0 30 25] /Resources << >>')
def page(parent,resources=''):return f'<< /Type /Page /Parent {parent} 0 R /MediaBox [0 0 160 100] {resources} /Contents 4 0 R >>'.encode()
def make(kind):
 content=stream('q 1 0 0 1 20 20 cm /Mark Do Q q 1 0 0 1 90 55 cm /Mark Do Q')
 if kind=='siblings':
  objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R 7 0 R 9 0 R] /Count 3 /Resources << /XObject << /Mark 5 0 R >> >> >>',page(2),content,leaf('1 0 0'),leaf('0 0 1'),b'<< /Type /Pages /Parent 2 0 R /Kids [8 0 R] /Count 1 /Resources << /XObject << /Mark 6 0 R >> >> >>',page(7),page(2)]
 else:
  objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 /Resources << /XObject << /Mark 5 0 R >> >> >>',page(2,'/Resources << /XObject << /Mark 6 0 R >> >>' if kind=='explicit' else ''),content,leaf('1 0 0')]
  if kind=='explicit':objects.append(leaf('0 0 1'))
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(out);out.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
 for offset in offsets:out.extend(f'{offset:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(out)
def main():
 (ROOT/'inputs').mkdir(exist_ok=True);fixtures=[]
 for kind in ['root','explicit','siblings']:
  file='inputs/resource-inheritance-'+kind+'.pdf';data=make(kind);(ROOT/file).write_bytes(data);fixtures.append(dict(id='resource-inheritance-'+kind,file=file,sha256=hashlib.sha256(data).hexdigest(),page_count=3 if kind=='siblings' else 1))
 views=[('resource-inherit-root',0,0,'red',2,'Page without Resources inherits root binding'),('resource-explicit-page',1,0,'blue',3,'Complete explicit page Resources overrides root binding'),('resource-sibling-root-before',2,0,'red',2,'First root sibling inherits root binding'),('resource-nearest-ancestor',2,1,'blue',7,'Nested page inherits nearer intermediate Pages binding'),('resource-sibling-root-after',2,2,'red',2,'Later root sibling retains root binding after nested subtree')];cases=[]
 for id,index,page_index,color,owner,contract in views:
  fixture=fixtures[index];rgb=[255,0,0] if color=='red' else [0,0,255];rects=[[20,20,30,25,rgb],[90,55,30,25,rgb]]
  samples=[dict(id='left-binding',x=35,y=32,rgb=rgb,tolerance=0),dict(id='right-binding',x=105,y=67,rgb=rgb,tolerance=0)]+[dict(id='paper-'+str(i),x=x,y=y,rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate([(5,5),(60,30),(30,80),(140,50)])]
  regions=[dict(id='left-binding',rect=[22,22,26,21],rgb=rgb,tolerance=0),dict(id='right-binding',rect=[92,57,26,21],rgb=rgb,tolerance=0)]+[dict(id=s['id'],rect=[s['x']-2,s['y']-2,4,4],rgb=s['rgb'],tolerance=0) for s in samples[2:]]
  cases.append(dict(id=id,fixture_id=fixture['id'],file=fixture['file'],sha256=fixture['sha256'],license='MIT',fixture_version='1.7',contract=contract,spec='ISO32000-1:2008',spec_clauses=['7.7.3.4 Inheritance of Page Attributes','7.8.3 Resource Dictionaries','7.7.3.3/Table30 Resources'],primary_iso_2020='7.8.3 Resource dictionaries',secondary_iso_2020=['7.7.3.4 referenced by verified public7.8.3; full nearest-ancestor wording pending','7.7.3.2 Page tree nodes / Table30 Count'],route='ordinary page tree inherited Resources resolving /Mark to an explicit self-contained leaf Form',width=160,height=100,display_width_points=160,display_height_points=100,user_unit=1,rotation=0,page=page_index,pages=[page_index],page_count=fixture['page_count'],dpis=[72,144],background=[255,255,255],annotations='none',expected_resource_owner_object=owner,expected_leaf_object=5 if color=='red' else 6,shape_rectangles=rects,samples=samples,expected_samples=[dict(id=s['id'],point=[s['x'],s['y']],rgb=s['rgb'],tolerance=0) for s in samples],expected_regions=regions,sample_coordinates='PDF page points x right/y up; row=floor((100-y)*dpi/72)',mask='One-device-pixel band around analytic rectangle boundaries excluded before images read',upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-PAGE-RESOURCE-03',owner='mozilla_originals',fixture_count=3,case_count=5,page_view_count=5,independently_authored=True,upstream_fixture_bytes_read=0,fixtures=fixtures,cases=cases),indent=2)+'\n');print(json.dumps(dict(unique_pdfs=3,page_views=5,bytes=sum((ROOT/f['file']).stat().st_size for f in fixtures))))
if __name__=='__main__':main()
