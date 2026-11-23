#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
MEDIA=[0,0,220,180];CROP=[24,18,184,138]
# Original vectors; absolute coordinates intentionally distinguish CropBox origin and dimensions.
CONTENT=b'''0 0 1 rg 0 8 220 20 re f
1 0 0 rg 32 28 28 20 re f
0 1 0 rg 130 94 40 26 re f
1 1 0 rg 170 36 30 18 re f
0 0 0 rg 195 30 15 90 re f
'''
REGIONS=[('blue-cropped-bottom',[2,2,156,6],[0,0,255]),('red-origin-marker',[10,12,24,16],[255,0,0]),('green-upper-marker',[108,78,36,22],[0,255,0]),('yellow-clipped-right',[148,20,10,14],[255,255,0]),('paper-upper-left',[3,108,8,8],[255,255,255]),('paper-center',[65,45,20,16],[255,255,255]),('paper-right',[148,50,8,8],[255,255,255]),('paper-upper-center',[72,108,16,8],[255,255,255])]
def pdf(mode):
 arrays=['['+' '.join(map(str,v))+']' for v in [MEDIA,CROP]];extra=[]
 if mode=='arrays':extra=[s.encode() for s in arrays];boxes=['5 0 R','6 0 R']
 elif mode=='coordinates':
  extra=[str(v).encode() for v in MEDIA+CROP];boxes=['['+' '.join(f'{i} 0 R' for i in range(start,start+4))+']' for start in [5,9]]
 else:boxes=arrays
 page=f'<< /Type /Page /Parent 2 0 R /MediaBox {boxes[0]} /CropBox {boxes[1]} /Resources << >> /Contents 4 0 R >>'.encode()
 objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',page,b'<< /Length '+str(len(CONTENT)).encode()+b' >>\nstream\n'+CONTENT+b'endstream',*extra]
 out=bytearray(b'%PDF-1.7\n% Original MIT indirect page-box fixture\n');offsets=[0]
 for i,obj in enumerate(objs,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(out);out.extend(f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode())
 for off in offsets[1:]:out.extend(f'{off:010} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(out)
def main():
 (R/'inputs').mkdir(exist_ok=True);cases=[]
 for id,mode,contract in [('boxes-direct-control','direct','Direct numeric MediaBox and CropBox arrays establish the independently computed visible viewport.'),('boxes-indirect-arrays','arrays','Whole-array indirect references for BOTH MediaBox and CropBox resolve to the same boxes, crop origin and vectors as the direct control.'),('boxes-indirect-coordinates','coordinates','All four coordinate elements in EACH MediaBox and CropBox array are indirect numeric objects; resolution preserves both boxes and the visible viewport.')]:
  data=pdf(mode);file='inputs/'+id+'.pdf';(R/file).write_bytes(data);regions=[dict(id=n,rect=rect,rgb=rgb,tolerance=0) for n,rect,rgb in REGIONS];samples=[dict(id=r['id'],point=[r['rect'][0]+r['rect'][2]/2,r['rect'][1]+r['rect'][3]/2],rgb=r['rgb'],tolerance=0) for r in regions]
  cases.append(dict(id=id,fixture_id=id,file=file,sha256=hashlib.sha256(data).hexdigest(),license='MIT',fixture_version='1.7',contract=contract,primary_iso_2020='7.3.10 Indirect objects',secondary_iso_2020=['7.7.3.3 Page objects','7.9.5 rectangle cross-reference only'],spec='ISO32000-1:2008',spec_clauses=['7.3.6 Array Objects','7.3.10 Indirect Objects','7.7.3.3/Page-object Table30 MediaBox/CropBox','7.9.5 Rectangles'],route='Single ordinary static page; resolve both box values; visible CropBox rendering',width=160,height=120,display_width_points=160,display_height_points=120,page=0,page_count=1,dpis=[72,144],rotation=0,user_unit=1,background=[255,255,255],annotations='none',box_form=mode,expected_media_box=MEDIA,expected_crop_box=CROP,expected_visible_origin=[24,18],expected_visible_size=[160,120],expected_samples=samples,expected_regions=regions,scope_limits=['Single page, no inheritance or page reordering','No malformed, missing or cyclic references','Positive normalized boxes; no rotated or negative-origin boxes','All paint boundaries and page edge pixels outside declared interiors unscored','No source scene/setting or issue7872 parity claim'],upstream_association=dict(scope='spec-derived-only',upstream_id=None,discovery_only='mozilla:issue7872',exact_upstream_scope_established=False,upstream_input_executed=False)))
  assert len(data)<2000
 manifest=dict(schema_version=1,slice='ISO-PAGE-BOX-INDIRECT-01',owner='upstream_match5',fixture_count=3,unique_pdfs=3,case_count=3,cases=cases,source_vectors_sha256=hashlib.sha256(CONTENT).hexdigest())
 (R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(unique_pdfs=3,bytes=sum((R/c['file']).stat().st_size for c in cases))))
if __name__=='__main__':main()
