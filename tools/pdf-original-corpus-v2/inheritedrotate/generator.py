#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Original PDF1.7 Rotate inheritance controls. No external inputs."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
BOX=[10,20,170,120]
CONTENT='1 0 0 rg 30 40 20 15 re f 0 0 1 rg 120 80 30 20 re f'
def page(parent,rotation=None):return f'<< /Type /Page /Parent {parent} 0 R /MediaBox [10 20 170 120] /CropBox [10 20 170 120] /Resources << >> '+('' if rotation is None else f'/Rotate {rotation} ')+'/Contents 4 0 R >>'
def make(kind):
 stream=f'<< /Length {len(CONTENT)} >>\nstream\n{CONTENT}\nendstream'
 if kind=='siblings':
  objects=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R 5 0 R 7 0 R] /Count 3 /Rotate 90 >>',page(2),stream,'<< /Type /Pages /Parent 2 0 R /Kids [6 0 R] /Count 1 /Rotate 270 >>',page(5),page(2)]
 else:
  objects=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R] /Count 1 /Rotate 90 >>',page(2,0 if kind=='explicit' else None),stream]
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n{obj}\nendobj\n'.encode())
 start=len(out);out.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
 for offset in offsets:out.extend(f'{offset:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(out)
def display_rect(rect,rotation):
 x,y,w,h,color=rect;u=x-10;v=y-20
 if rotation==0:return [u,v,w,h,color]
 if rotation==90:return [v,160-u-w,h,w,color]
 if rotation==270:return [100-v-h,u,h,w,color]
 raise ValueError('Only authored ordinary rotations supported')
def main():
 (ROOT/'inputs').mkdir(exist_ok=True);fixtures=[]
 for kind in ['root','explicit','siblings']:
  file='inputs/rotate-inheritance-'+kind+'.pdf';data=make(kind);(ROOT/file).write_bytes(data);fixtures.append(dict(id='rotate-inheritance-'+kind,file=file,sha256=hashlib.sha256(data).hexdigest(),page_count=3 if kind=='siblings' else 1))
 views=[('rotate-inherit-root90',0,0,90,2,'Page inherits clockwise90degree root rotation'),('rotate-explicit-page0',1,0,0,3,'Explicit local Rotate0 overrides root90'),('rotate-sibling-root-before',2,0,90,2,'First root sibling inherits90degree rotation'),('rotate-nearest-ancestor270',2,1,270,5,'Nested page inherits nearer Pages270degree rotation'),('rotate-sibling-root-after',2,2,90,2,'Later root sibling keeps90degree rotation after nested270 subtree')];cases=[]
 for id,index,page_index,rotation,owner,contract in views:
  fixture=fixtures[index];width,height=(160,100) if rotation==0 else (100,160)
  rects=[display_rect([30,40,20,15,[255,0,0]],rotation),display_rect([120,80,30,20,[0,0,255]],rotation)]
  samples=[dict(id=name,x=x+w/2,y=y+h/2,rgb=rgb,tolerance=0) for name,(x,y,w,h,rgb) in zip(['red-placement','blue-placement'],rects)]+[dict(id='paper-'+str(i),x=x,y=y,rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate([(5,5),(width-5,5),(5,height-5),(width-5,height-5)])]
  regions=[dict(id=name,rect=[x+2,y+2,w-4,h-4],rgb=rgb,tolerance=0) for name,(x,y,w,h,rgb) in zip(['red-placement','blue-placement'],rects)]+[dict(id=s['id'],rect=[s['x']-2,s['y']-2,4,4],rgb=s['rgb'],tolerance=0) for s in samples[2:]]
  transform={0:[1,0,0,-1,-10,120],90:[0,1,1,0,-20,-10],270:[0,-1,-1,0,120,170]}[rotation]
  cases.append(dict(id=id,fixture_id=fixture['id'],file=fixture['file'],sha256=fixture['sha256'],license='MIT',fixture_version='1.7',contract=contract,spec='ISO32000-1:2008',spec_clauses=['7.7.3.3/Table30 Rotate: inheritable clockwise multiples of90','7.7.3.4 Inheritance of Page Attributes','8.3.2.3 User Space'],primary_iso_2020='7.7.3.4 Inheritance of page attributes (cross-reference verified; full rule text pending)',secondary_iso_2020=['7.7.3.3/Table31 Page objects: heading verified; complete Rotate row pending','7.8.3 cross-reference to inheritance verified'],route='Direct vector rectangles on a page with explicit MediaBox/CropBox and empty Resources; Rotate inherited or explicitly overridden',width=width,height=height,display_width_points=width,display_height_points=height,user_unit=1,rotation=rotation,page=page_index,pages=[page_index],page_count=fixture['page_count'],dpis=[72,144],background=[255,255,255],annotations='none',expected_media_box=BOX,expected_crop_box=BOX,expected_rotate_owner_object=owner,expected_device_transform_at_72=transform,shape_rectangles=rects,samples=samples,expected_samples=[dict(id=s['id'],point=[s['x'],s['y']],rgb=s['rgb'],tolerance=0) for s in samples],expected_regions=regions,sample_coordinates='Upright visible display points after CropBox origin and page Rotate; x right/y up; image row=floor((height-y)*dpi/72)',mask='One-device-pixel boundary band around analytic rectangle boundaries excluded before images read',upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-PAGE-ATTRIBUTE-INHERIT-02',owner='mozilla_originals',fixture_count=3,case_count=5,page_view_count=5,independently_authored=True,upstream_fixture_bytes_read=0,fixtures=fixtures,cases=cases),indent=2)+'\n');print(json.dumps(dict(unique_pdfs=3,page_views=5,bytes=sum((ROOT/f['file']).stat().st_size for f in fixtures))))
if __name__=='__main__':main()
