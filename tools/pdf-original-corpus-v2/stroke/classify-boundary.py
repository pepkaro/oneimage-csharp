#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read existing product/reference evidence; emit classification only. Never alter expectations."""
from pathlib import Path
import hashlib,json,math,os,subprocess
import numpy as np
from PIL import Image
from score import expected
ROOT=Path(__file__).resolve().parent;BATCH=ROOT.parent.parent;MAIN='eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 report=BATCH/'product-expanded/results.json';data=json.loads(report.read_text());assert data['oneimage_source_head']==MAIN
 assert (data['executed'],data['passed'],data['failed'])==(42,41,1)
 row=next(r for r in data['rows'] if r['id']=='stroke-cap-round' and r['dpi']==72)
 assert row['different_pixels']==0 and not row['passed']
 assert all(r['different_pixels']==0 for r in data['rows'])
 c=next(c for c in json.loads((ROOT/'manifest.json').read_text())['cases'] if c['id']=='stroke-cap-round')
 _,mask=expected(c,72);column,row_index=22,42;assert not bool(mask[row_index,column])
 product=BATCH/'product-expanded/stroke-cap-round-72.png';actual=np.asarray(Image.open(product).convert('RGB'))[row_index,column].tolist();assert actual==[255,253,253]
 references=[]
 for engine in ['pdfium','mupdf','pdfjs']:
  f=ROOT/'references'/('stroke-cap-round-72-'+engine+'.png');value=np.asarray(Image.open(f).convert('RGB'))[row_index,column].tolist();assert value==[255,255,255]
  references.append(dict(engine=engine,path=str(f),sha256=digest(f),rgb=value))
 lo=-math.sqrt(51);hi=-7
 integral=lambda x:.5*(x*math.sqrt(100-x*x)+100*math.asin(x/10))-7*x
 area=integral(hi)-integral(lo)
 source=[]
 for path,start,end,role in [('src/OneImage.Pdf/Render/CanvasDevice.cs',157,180,'Converts the ordinary PDF path to a stroke outline; nondegenerate round-cap path uses StrokeUserPath.'),('src/OneImage.Pdf/Render/CanvasDevice.cs',257,270,'Maps state.LineCap1 to StrokeCap.Round, calls StrokeBuilder.Build, then transforms the outline.'),('src/OneImage/Drawing/StrokeBuilder.cs',341,393,'Builds round caps with Arc; Arc emits cubic pieces of at most90degrees.'),('src/OneImage/Drawing/FillPlan.cs',222,245,'Consumes raster coverage and dispatches RGB/RGBA painting. Exact discrepancy attribution was not instrumented.')]:
  env=dict(os.environ,GIT_NO_LAZY_FETCH='1');raw=subprocess.check_output(['git','-C',str(BATCH/'repo'),'show',MAIN+':'+path],env=env)
  source.append(dict(commit=MAIN,path=path,line_start=start,line_end=end,file_sha256=hashlib.sha256(raw).hexdigest(),participation=role))
 result=dict(schema_version=1,id='stroke-cap-round-72-extension-corner',classification='boundary-compatibility-probe-outside-accepted-mask',accepted_mask_result='passed: zero differing scored pixels',strict_result='failed: preserve named sample mismatch',original_strict_ledger=dict(executed=42,passed=41,failed=1,skipped=data['skipped'],skip_reason=data['skip_reason']),separate_masked_ledger=dict(executed=42,passed=42,failed=0,skipped=data['skipped'],scope='Existing declared masks only; no assertion expectation changed'),report=dict(path=str(report),sha256=digest(report),acceptance_commit=data['acceptance_commit']),probe=dict(declared_pdf_position=[22,58],device_pixel_index=[column,row_index],pdf_space_pixel_center=[22.5,57.5],pdf_space_pixel_footprint=[22,57,23,58],ideal_left_cap_center=[30,50],radius=10,center_distance=math.hypot(22.5-30,57.5-50),signed_center_distance=math.hypot(22.5-30,57.5-50)-10,exclusion_band_device_pixels=1,accepted_mask=False,product_rgb=actual,expected_rgb=[255,255,255],product_png_sha256=digest(product),references=references),independent_area_control=dict(method='Integrate sqrt(100-x*x)-7 for local x from -sqrt(51) to -7 over the unit pixel footprint',ideal_circle_covered_area=area,interpretation='Pixel center is exterior, but its finite area intersects the ideal circle. Pixel-center binary expectation is not an ISO-mandated antialiasing rule. This area calculation classifies the probe; it does not replace the preserved RGB expectation or claim exact product coverage.'),source_participation=source,parser_assessment=dict(declared_dependency=data['onepdf_declared_package'],scope='The PDF parser/interpreter necessarily supplies path and line-cap state, but exact package source/instrumented parse state were not audited here. Actual OneImage main maps cap1 to round and constructs its outline. Interior and style controls pass. No evidence establishes a parser fault; no definitive ownership is assigned.'),limits=['No antialiasing or quantization conformance verdict from this unscored pixel','No renderer fix proposed','No product, PDF, manifest, expectation, reference, prior score or checkpoint modified','No upstream fixture input executed or upstream parity claimed'],next_action='Retain strict probe mismatch beside42masked passes. A future independently scoped edge study would require subpixel area/curve approximation and compositing controls before any implementation diagnosis.')
 target=ROOT/'boundary-classification.json';target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(classification=result['classification'],strict=[42,41,1],masked=[42,42,0],accepted_mask=False,ideal_circle_covered_area=area,file=str(target),sha256=digest(target)),indent=2))
if __name__=='__main__':main()
