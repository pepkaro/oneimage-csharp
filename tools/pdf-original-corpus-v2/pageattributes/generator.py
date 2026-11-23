#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Original valid MediaBox inheritance controls; no external inputs."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
ROOT_BOX=[10,20,170,120];LOCAL_BOX=[0,0,120,80];NEAR_BOX=[-10,-10,130,80]
CONTENT='1 0 0 rg 30 40 20 15 re f 0 0 1 rg 80 60 20 15 re f'
def box(values):return '['+' '.join(map(str,values))+']'
def page(parent,media=None):return f'<< /Type /Page /Parent {parent} 0 R /Resources << >> '+('' if media is None else '/MediaBox '+box(media)+' ' )+'/Contents 4 0 R >>'
def make(kind):
 stream=f'<< /Length {len(CONTENT)} >>\nstream\n{CONTENT}\nendstream'
 if kind=='siblings':
  objects=['<< /Type /Catalog /Pages 2 0 R >>',f'<< /Type /Pages /Kids [3 0 R 5 0 R 7 0 R] /Count 3 /MediaBox {box(ROOT_BOX)} >>',page(2),stream,f'<< /Type /Pages /Parent 2 0 R /Kids [6 0 R] /Count 1 /MediaBox {box(NEAR_BOX)} >>',page(5),page(2)]
 else:
  objects=['<< /Type /Catalog /Pages 2 0 R >>',f'<< /Type /Pages /Kids [3 0 R] /Count 1 /MediaBox {box(ROOT_BOX)} >>',page(2,LOCAL_BOX if kind=='explicit' else None),stream]
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n{obj}\nendobj\n'.encode())
 start=len(out);out.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
 for offset in offsets:out.extend(f'{offset:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(out)
def main():
 (ROOT/'inputs').mkdir(exist_ok=True);fixtures=[]
 for kind in ['root','explicit','siblings']:
  file='inputs/mediabox-inheritance-'+kind+'.pdf';data=make(kind);(ROOT/file).write_bytes(data);fixtures.append(dict(id='mediabox-inheritance-'+kind,file=file,sha256=hashlib.sha256(data).hexdigest(),page_count=3 if kind=='siblings' else 1))
 views=[('mediabox-inherit-root',0,0,ROOT_BOX,2,'Page inherits offset root MediaBox'),('mediabox-explicit-page',1,0,LOCAL_BOX,3,'Explicit local MediaBox overrides inherited root dimensions and origin'),('mediabox-sibling-root-before',2,0,ROOT_BOX,2,'First sibling inherits root MediaBox'),('mediabox-nearest-ancestor',2,1,NEAR_BOX,5,'Nested page inherits the nearer Pages MediaBox'),('mediabox-sibling-root-after',2,2,ROOT_BOX,2,'Later sibling keeps root dimensions after the nested subtree')];cases=[]
 for id,index,page_index,media,owner,contract in views:
  fixture=fixtures[index];x0,y0,x1,y1=media;width=x1-x0;height=y1-y0
  rects=[[30-x0,40-y0,20,15,[255,0,0]],[80-x0,60-y0,20,15,[0,0,255]]]
  samples=[dict(id='red-placement',x=40-x0,y=47-y0,rgb=[255,0,0],tolerance=0),dict(id='blue-placement',x=90-x0,y=67-y0,rgb=[0,0,255],tolerance=0)]+[dict(id='paper-'+str(i),x=x,y=y,rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate([(5,5),(width-5,5),(5,height-5),(width-5,height-5)])]
  regions=[dict(id='red-placement',rect=[32-x0,42-y0,16,11],rgb=[255,0,0],tolerance=0),dict(id='blue-placement',rect=[82-x0,62-y0,16,11],rgb=[0,0,255],tolerance=0)]+[dict(id=s['id'],rect=[s['x']-2,s['y']-2,4,4],rgb=s['rgb'],tolerance=0) for s in samples[2:]]
  cases.append(dict(id=id,fixture_id=fixture['id'],file=fixture['file'],sha256=fixture['sha256'],license='MIT',fixture_version='1.7',contract=contract,spec='ISO32000-1:2008',spec_clauses=['7.7.3.3/Table30 MediaBox and CropBox','7.7.3.4 Inheritance of Page Attributes','8.3.2.3 User Space'],primary_iso_2020='7.7.3.4 Inheritance of page attributes (cross-reference verified; full rule text pending)',secondary_iso_2020=['7.7.3.3/Table31 Page objects: heading verified; MediaBox row pending','7.8.3 cross-reference to inheritance verified'],route='Direct numeric vector page content; inherited or explicit MediaBox; absent CropBox defaults to effective MediaBox; explicit empty Resources',width=width,height=height,display_width_points=width,display_height_points=height,user_unit=1,rotation=0,page=page_index,pages=[page_index],page_count=fixture['page_count'],dpis=[72,144],background=[255,255,255],annotations='none',expected_media_box=media,expected_media_owner_object=owner,expected_visible_box=media,expected_device_transform_at_72=[1,0,0,-1,-x0,y1],shape_rectangles=rects,samples=samples,expected_samples=[dict(id=s['id'],point=[s['x'],s['y']],rgb=s['rgb'],tolerance=0) for s in samples],expected_regions=regions,sample_coordinates='Upright visible page points after subtracting MediaBox lower-left; x right/y up; row=floor((height-y)*dpi/72)',mask='One-device-pixel band around analytic rectangle boundaries excluded before images read',upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-PAGE-ATTRIBUTE-INHERIT-01',owner='mozilla_originals',fixture_count=3,case_count=5,page_view_count=5,independently_authored=True,upstream_fixture_bytes_read=0,fixtures=fixtures,cases=cases),indent=2)+'\n');print(json.dumps(dict(unique_pdfs=3,page_views=5,bytes=sum((ROOT/f['file']).stat().st_size for f in fixtures))))
if __name__=='__main__':main()
