# SPDX-License-Identifier: MIT
"""Independently authored mathematical ICC/PDF controls. No imported asset bytes.
Run with Python's standard library. All newly generated inputs are MIT licensed.
"""
from pathlib import Path
import struct, zlib, json, hashlib
ROOT=Path(__file__).resolve().parent
for sub in ('profiles','fixtures','renders'):(ROOT/sub).mkdir(exist_ok=True)
RGB=[(0,0,0),(255,255,255),(128,128,128),(32,32,32),(255,0,0),(0,255,0),(0,0,255),(200,100,50),(64,128,192),(192,128,64),(128,200,128),(220,180,200),(30,90,60),(180,80,120),(80,160,200),(100,120,140)]
U=lambda n:struct.pack('>I',n)
H=lambda n:struct.pack('>H',n)
F=lambda n:struct.pack('>i',round(n*65536))
def multiply(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def solve(a,b):
    # Generic Gaussian elimination, independent of the renderer's profile builder.
    rows=[list(row)+[v] for row,v in zip(a,b)]
    for i in range(3):
        pivot=max(range(i,3),key=lambda j:abs(rows[j][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
        scale=rows[i][i];rows[i]=[x/scale for x in rows[i]]
        for j in range(3):
            if j!=i:
                scale=rows[j][i];rows[j]=[x-scale*y for x,y in zip(rows[j],rows[i])]
    return [row[3] for row in rows]
def white(x,y):return [x/y,1,(1-x-y)/y]
# Published chromaticity/transfer facts, not copied profile/fixture content.
primaries=[(.64,.33),(.21,.71),(.15,.06)]
columns=[white(x,y) for x,y in primaries];p=[list(x) for x in zip(*columns)]
d65=white(.3127,.3290);d50=[.9642,1,.8249]
scales=solve(p,d65);matrix=[[x*scales[j] for j,x in enumerate(row)] for row in p]
bradford=[[.8951,.2664,-.1614],[-.7502,1.7135,.0367],[.0389,-.0685,1.0296]]
source=[sum(x*y for x,y in zip(row,d65)) for row in bradford];target=[sum(x*y for x,y in zip(row,d50)) for row in bradford]
cone=multiply(bradford,matrix);cone=[[v*target[i]/source[i] for v in row] for i,row in enumerate(cone)]
adapted_columns=[solve(bradford,list(c)) for c in zip(*cone)]
def xyz(v):return b'XYZ '+b'\0'*4+b''.join(F(x) for x in v)
def text(s):
    b=s.encode('utf-16-be');return b'mluc'+b'\0'*4+U(1)+U(12)+b'enUS'+U(len(b))+U(28)+b
curve=b'curv'+b'\0'*4+U(1)+H(563) # gamma563/256
original_name='Original mathematical RGB control'
renamed_name='sRGB description-only test'.ljust(len(original_name))
def profile(name):
    tags={'desc':text(name),'cprt':text('MIT licensed original test asset'),'wtpt':xyz(d50),'rXYZ':xyz(adapted_columns[0]),'gXYZ':xyz(adapted_columns[1]),'bXYZ':xyz(adapted_columns[2]),'rTRC':curve,'gTRC':curve,'bTRC':curve}
    header=bytearray(128);header[8:12]=bytes([4,0x30,0,0]);header[12:24]=b'mntrRGB XYZ ';header[24:36]=struct.pack('>6H',2026,11,14,0,0,0);header[36:40]=b'acsp';header[64:68]=U(1);header[68:80]=b''.join(F(v) for v in d50)
    at=132+12*len(tags);table=bytearray();body=bytearray();ranges={}
    for sig,payload in tags.items():
        ranges[sig]=[at,at+len(payload)];table+=sig.encode()+U(at)+U(len(payload));padding=(-len(payload))%4;body+=payload+b'\0'*padding;at+=len(payload)+padding
    out=header+U(len(tags))+table+body;out[:4]=U(len(out));return bytes(out),ranges
wide,ranges=profile(original_name);renamed,_=profile(renamed_name)
changes=[i for i,(a,b) in enumerate(zip(wide,renamed)) if a!=b]
assert changes and len(wide)==len(renamed) and all(ranges['desc'][0]<=i<ranges['desc'][1] for i in changes)
(ROOT/'profiles/wide-original.icc').write_bytes(wide);(ROOT/'profiles/wide-renamed.icc').write_bytes(renamed)
def stream(meta,data):return f'<< {meta} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'
content=b'/RelativeColorimetric ri /CS cs\n'
for i,p in enumerate(RGB):content+=(' '.join(f'{v/255:.12f}' for v in p)+f' scn {i*22.5} 45 22.5 45 re f\n').encode()
content+=b'q 360 0 0 45 0 0 cm /Im Do Q\n'
def pdf(icc):
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 360 90] /Contents 4 0 R /Resources << /ColorSpace << /CS [/ICCBased 5 0 R] >> /XObject << /Im 6 0 R >> >> >>',stream('',content),stream('/N 3 /Alternate /DeviceRGB',icc),stream('/Type /XObject /Subtype /Image /Width 16 /Height 1 /BitsPerComponent 8 /ColorSpace [/ICCBased 5 0 R] /Filter /FlateDecode',zlib.compress(bytes(v for p in RGB for v in p)))]
    out=bytearray(b'%PDF-2.0\n');offsets=[]
    for i,o in enumerate(objs,1):offsets.append(len(out));out+=f'{i} 0 obj\n'.encode()+o+b'\nendobj\n'
    off=len(out);out+=f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()
    for o in offsets:out+=f'{o:010d} 00000 n \n'.encode()
    return bytes(out+f'trailer\n<< /Root 1 0 R /Size {len(objs)+1} >>\nstartxref\n{off}\n%%EOF\n'.encode())
for name,icc in [('wide-original',wide),('wide-renamed',renamed)]:(ROOT/'fixtures'/f'{name}.pdf').write_bytes(pdf(icc))
paths=[ROOT/sub/f'{name}.{ext}' for sub,ext in [('profiles','icc'),('fixtures','pdf')] for name in ('wide-original','wide-renamed')]
manifest={'license':'MIT','authorship':'Independently authored generator, shapes, sample values, PDF structure and mathematical ICC profiles; no upstream fixture, profile bytes, fonts, art, text or expected-image input.','numeric_basis':'RGB primaries(.64,.33),(.21,.71),(.15,.06), D65 white(.3127,.3290), gamma563/256; Bradford adaptation to ICC D50(.9642,1,.8249).','pdf_version':'2.0','icc_version':'4.3','description_tag_range':ranges['desc'],'changed_profile_byte_offsets':changes,'profile_equal_length':len(wide)==len(renamed),'rgb_samples':RGB,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(ROOT/'fixture-manifest.json').write_text(json.dumps(manifest,indent=2));print('Generated original MIT profiles/PDFs;',len(changes),'description bytes differ')
