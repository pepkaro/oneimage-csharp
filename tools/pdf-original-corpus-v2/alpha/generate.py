# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Original ordinary constant alpha scenes; no external input is read."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parent
W,H=240,160
CASES=[
 ('alpha-fill-endpoints','Nonstroking ca0 leaves the opaque backdrop unchanged; ca1 replaces it.', '0 0 1 rg 20 30 80 60 re f 140 30 80 60 re f q /A0 gs 1 0 0 rg 20 30 80 60 re f Q q /A1 gs 1 0 0 rg 140 30 80 60 re f Q', [('ca-zero-preserves-blue',[24,34,72,52],[0,0,255]),('ca-one-opaque-red',[144,34,72,52],[255,0,0])]),
 ('alpha-stroke-endpoints','Stroking CA0 is invisible; CA1 is opaque, and CA does not suppress an ordinary fill.', 'q /S0 gs 1 0 0 RG 20 w 20 60 m 100 60 l S 0 0 1 rg 30 110 40 25 re f Q q /S1 gs 1 0 0 RG 20 w 140 60 m 220 60 l S Q', [('CA-zero-invisible',[24,54,72,12],[255,255,255]),('CA-one-opaque',[144,54,72,12],[255,0,0]),('fill-independent-of-CA',[34,114,32,17],[0,0,255])]),
 ('alpha-ca-state-restore','Balanced q/Q restores the prior nonstroking alpha after a ca0 scope.', 'q /A0 gs 1 0 0 rg 20 30 80 60 re f Q 1 0 0 rg 140 30 80 60 re f', [('scoped-transparent-fill',[24,34,72,52],[255,255,255]),('restored-opaque-fill',[144,34,72,52],[255,0,0])]),
 ('alpha-fill-fraction06','Normal nonstroking alpha0.6 composites an ordinary red fill over white; byte quantization is measured separately from normative real-valued blending.', 'q /A6 gs 1 0 0 rg 20 30 80 60 re f Q 0 0 1 rg 140 30 80 60 re f', [('fractional-red',[24,34,72,52],[255,102,102]),('opaque-blue-control',[144,34,72,52],[0,0,255])]),
 ('alpha-stroke-fraction06','Normal stroking alpha0.6 composites an ordinary blue stroke over white while a nonstroking fill remains opaque.', 'q /S6 gs 0 0 1 RG 20 w 20 60 m 100 60 l S 1 0 0 rg 140 30 80 60 re f Q', [('fractional-blue',[24,54,72,12],[102,102,255]),('opaque-red-independent-ca',[144,34,72,52],[255,0,0])])]
# Separate binary-exact fractional control; original0.6 findings remain unchanged.
CASES.extend([
 ('alpha-fill-fraction025','A separate binary-exact ca0.25 control composites red over white; nearest8bit analytic samples are191 for the backdrop channels.', 'q /AQ gs 1 0 0 rg 20 30 80 60 re f Q 0 0 1 rg 140 30 80 60 re f', [('quarter-red',[24,34,72,52],[255,191,191]),('opaque-blue-control',[144,34,72,52],[0,0,255])]),
 ('alpha-stroke-fraction025','A separate binary-exact CA0.25 control composites blue over white while the ordinary fill remains opaque.', 'q /SQ gs 0 0 1 RG 20 w 20 60 m 100 60 l S 1 0 0 rg 140 30 80 60 re f Q', [('quarter-blue',[24,54,72,12],[191,191,255]),('opaque-red-independent-ca',[144,34,72,52],[255,0,0])])])
def stream(b):return f'<< /Length {len(b)} >>\nstream\n'.encode()+b+b'\nendstream'
def pdf(content):
 gs=b'/AQ << /Type /ExtGState /ca 0.25 /BM /Normal /AIS false >> /SQ << /Type /ExtGState /CA 0.25 /BM /Normal /AIS false >> /A0 << /Type /ExtGState /ca 0 /BM /Normal /AIS false >> /A1 << /Type /ExtGState /ca 1 /BM /Normal /AIS false >> /A6 << /Type /ExtGState /ca 0.6 /BM /Normal /AIS false >> /S0 << /Type /ExtGState /CA 0 /BM /Normal /AIS false >> /S1 << /Type /ExtGState /CA 1 /BM /Normal /AIS false >> /S6 << /Type /ExtGState /CA 0.6 /BM /Normal /AIS false >>'
 names=set(re.findall(r'/([AS][A-Za-z0-9]+) gs',content));parts=re.findall(rb'/([AS][A-Za-z0-9]+) (<<.*?>>)',gs);gs=b' '.join(b'/'+name+b' '+entry for name,entry in parts if name.decode() in names)
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Count 1 /Kids [3 0 R] >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 160] /Resources << /ExtGState << '+gs+b' >> >> /Contents 4 0 R >>',stream(content.encode())]
 data=bytearray(b'%PDF-1.7\n');offsets=[]
 for n,obj in enumerate(objects,1):offsets.append(len(data));data.extend(f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n')
 pos=len(data);data.extend(b'xref\n0 5\n0000000000 65535 f \n')
 for offset in offsets:data.extend(f'{offset:010d} 00000 n \n'.encode())
 data.extend(f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n'.encode());return bytes(data)
def main():
 (R/'inputs').mkdir(exist_ok=True);cases=[]
 for id,contract,content,regions in CASES:
  data=pdf(content);p=R/'inputs'/(id+'.pdf');p.write_bytes(data);regions=[dict(id=i,rect=r,rgb=c,tolerance=0) for i,r,c in regions]+[dict(id='paper',rect=[4,4,12,12],rgb=[255,255,255],tolerance=0)]
  samples=[dict(id=r['id'],point=[r['rect'][0]+r['rect'][2]/2,r['rect'][1]+r['rect'][3]/2],rgb=r['rgb'],tolerance=0) for r in regions]
  cases.append(dict(id=id,file='inputs/'+p.name,sha256=hashlib.sha256(data).hexdigest(),license='MIT',pdf_version='1.7',contract=contract,width=W,height=H,page=0,dpis=[72,144],rotation=0,background=[255,255,255],annotations='none',spec='ISO 32000-1:2008',spec_clauses=['11.6.4.4 Constant Shape and Opacity','8.4.5 Graphics State Parameter Dictionaries, Table57 CA/ca','11.3.3 Basic Compositing Formula'],expected_regions=regions,expected_samples=samples,association=dict(scope='spec-derived-only',upstream_id=None,upstream_entry_validated=False),scope_limits=['Normal blend only','No groups/soft masks/images/text','White backdrop except explicitly authored opaque blue endpoint backdrop','Exact8-bit quantization is an observed route criterion, not an ISO bit-exact requirement']))
 (R/'manifest.json').write_text(json.dumps(dict(schema_version=1,slice='ISO-TRANSPARENCY-01',owner='root',independently_authored=True,upstream_assets_read=0,cases=cases),indent=2)+'\n')
if __name__=='__main__':main()
