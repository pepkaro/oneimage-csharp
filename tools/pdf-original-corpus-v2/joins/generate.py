#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Three original ordinary line-join PDFs, no external inputs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent

def pdf(style):
 content=f'1 0 0 RG 20 w 0 J {style} j 10 M 30 30 m 70 30 l 70 70 l S'.encode('ascii')
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 120 100] /Resources << >> /Contents 4 0 R >>',f'<< /Length {len(content)} >>\nstream\n'.encode()+content+b'\nendstream']
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(out);out.extend(b'xref\n0 5\n0000000000 65535 f \n')
 for off in offsets:out.extend(f'{off:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(out)

def main():
 (ROOT/'inputs').mkdir(exist_ok=True);cases=[]
 for style,name in [(0,'miter'),(1,'round'),(2,'bevel')]:
  id='stroke-join-'+name;data=pdf(style);file='inputs/'+id+'.pdf';(ROOT/file).write_bytes(data)
  samples=[('horizontal-body',45,30,True),('vertical-body',70,55,True),('outside',90,20,False),('miter-only-corner',78,22,style==0),('round-or-miter',76,24,style in (0,1)),('all-join-interior',73,27,True)]
  cases.append(dict(id=id,file=file,sha256=hashlib.sha256(data).hexdigest(),license='MIT',fixture_version='1.7',contract='Ordinary 90-degree '+name+' line join',join_style=style,cap_style=0,path_points=[[30,30],[70,30],[70,70]],line_width=20,miter_limit=10,analytic_shape='Union of stroke rectangles [30,20,70,40] and [60,30,80,70], plus southeast join sector: square/miter, radius10 quarter-circle/round, or dx-dy<=10 triangle/bevel',display_width_points=120,display_height_points=100,user_unit=1,rotation=0,pages=[0],page_count=1,dpis=[72,144],background=[255,255,255],stroke_rgb=[255,0,0],annotations='none',sample_coordinates='upright display points x right/y up; image row=floor((100-y)*dpi/72)',samples=[dict(id=t,x=x,y=y,rgb=([255,0,0] if inside else [255,255,255]),tolerance=0) for t,x,y,inside in samples],predeclared_mask='Common conservative mask: exclude one-device-pixel bands around constituent rectangle edges, southeast square edges, radius10 circle and bevel diagonal before any renderer is read',legacy_verified_clause='ISO 32000-1:2008 8.4.3.4/Table55 Line Join Styles; 8.4.3.5 Miter Limit; 8.4.3.3 butt caps',official_2020_coarse_index='8.5 Path construction and painting; 8.5.3.1 Path-painting operators, general',narrow_2020_rule_status='Pending full official 2020 text access; no exact line-join clause or wording verified from errata',source_urls=['https://pdfa.org/resource/iso-32000-2','https://pdf-issues.pdfa.org/32000-2-2020/clause08.html'],upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,slice='ISO-GEOMETRY-STROKE-02',owner='mozilla_originals',independently_authored=True,upstream_fixture_bytes_read=0,case_count=3,cases=cases),indent=2)+'\n')
 print(json.dumps(dict(unique_pdfs=len(cases),bytes=sum((ROOT/c['file']).stat().st_size for c in cases))))
if __name__=='__main__':main()
