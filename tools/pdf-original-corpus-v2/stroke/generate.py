#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Three original ordinary line-cap PDFs, no external inputs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent

def pdf(style):
 content=f'1 0 0 RG 20 w {style} J 30 50 m 90 50 l S'.encode('ascii')
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 120 100] /Resources << >> /Contents 4 0 R >>',f'<< /Length {len(content)} >>\nstream\n'.encode()+content+b'\nendstream']
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(out);out.extend(b'xref\n0 5\n0000000000 65535 f \n')
 for off in offsets:out.extend(f'{off:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(out)

def main():
 (ROOT/'inputs').mkdir(exist_ok=True);cases=[]
 for style,name in [(0,'butt'),(1,'round'),(2,'projecting-square')]:
  id='stroke-cap-'+name;data=pdf(style);file='inputs/'+id+'.pdf';(ROOT/file).write_bytes(data)
  # (22,58) distinguishes the square corner from round; (22,50) distinguishes extended caps from butt.
  samples=[('body',60,50,True),('outside',15,50,False),('beyond-end',22,50,style!=0),('extension-corner',22,58,style==2),('above',60,65,False),('right-extension',98,50,style!=0)]
  cases.append(dict(id=id,file=file,sha256=hashlib.sha256(data).hexdigest(),license='MIT',fixture_version='1.7',contract='Open horizontal subpath line cap '+name,cap_style=style,segment=[[30,50],[90,50]],line_width=20,analytic_shape=('rectangle [30,40,90,60]' if style==0 else 'capsule: distance to segment <=10' if style==1 else 'rectangle [20,40,100,60]'),display_width_points=120,display_height_points=100,user_unit=1,rotation=0,pages=[0],page_count=1,dpis=[72,144],background=[255,255,255],stroke_rgb=[255,0,0],annotations='none',sample_coordinates='upright display points x right/y up; image row=floor((100-y)*dpi/72)',samples=[dict(id=s,x=x,y=y,rgb=([255,0,0] if inside else [255,255,255]),tolerance=0) for s,x,y,inside in samples],predeclared_mask='Exclude all pixel centers within 1 device pixel of analytic shape boundary; score every remaining interior and exterior pixel',legacy_verified_clause='ISO 32000-1:2008 8.4.3.3, Table 54 Line Cap Styles',official_2020_coarse_index='8.5 Path construction and painting; 8.5.3.1 Path-painting operators, general',narrow_2020_rule_status='Pending full official 2020 text access; no claim line-cap clause or wording verified from errata',source_urls=['https://pdfa.org/resource/iso-32000-2','https://pdf-issues.pdfa.org/32000-2-2020/clause08.html'],upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,slice='ISO-GEOMETRY-STROKE-01',owner='mozilla_originals',independently_authored=True,upstream_fixture_bytes_read=0,case_count=3,cases=cases),indent=2)+'\n')
 print(json.dumps(dict(unique_pdfs=len(cases),bytes=sum((ROOT/c['file']).stat().st_size for c in cases))))
if __name__=='__main__':main()
