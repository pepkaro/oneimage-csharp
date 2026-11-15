# SPDX-License-Identifier: MIT
# Independently authored 2026-11-14. No external fixture content.
import pathlib, json, hashlib, argparse
parser = argparse.ArgumentParser(description="Generate original MIT zero-length dash controls.")
parser.add_argument("output", type=pathlib.Path)
root = parser.parse_args().output.resolve()
pdfdir = root / "pdf"
pdfdir.mkdir(parents=True, exist_ok=True)
def pdf(content):
    data=content.encode('ascii')
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 192 144] /CropBox [0 0 192 144] /Rotate 0 /Resources << >> /Contents 4 0 R >>',b'<< /Length '+str(len(data)).encode()+b' >>\nstream\n'+data+b'\nendstream']
    out=b'%PDF-1.7\n'; offsets=[0]
    for i,o in enumerate(objs,1):
        offsets.append(len(out));out+=f'{i} 0 obj\n'.encode()+o+b'\nendobj\n'
    x=len(out);out+=b'xref\n0 5\n0000000000 65535 f \n'+b''.join(f'{v:010d} 00000 n \n'.encode() for v in offsets[1:])+f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n'.encode()
    return out
cases=[]
def add(name,dash,phase,path='96 72 m 96 72 l',cap=1,width=18,transform='',marks=None):
    cases.append(dict(name=name,dash=dash,phase=phase,path=path,cap=cap,width=width,transform=transform,marks=marks))
add('solid',[],0,marks=True)
for p in (0,3,10.999,11,11.001,19,27.999,28,31,39,56,59):
    add('even-'+str(p),[11,17],p)
for p in (0,6,7,12,20,21,23,28,33,41,42,49,54):
    add('odd-'+str(p),[7,5,9],p)
for d in ([0,17],[11,0],[0,0,11,17],[11,0,0,17],[0,0,0,17],[0,17,0]):
    for p in (0,1,11,17,28,34):add('zero-'+''.join(str(v)+'_' for v in d)+str(p),d,p)
for name,path in [('close','96 72 m h'),('closedline','96 72 m 96 72 l h'),('curve','96 72 m 96 72 96 72 96 72 c'),('move','96 72 m'),('rectangle','96 72 0 0 re'),('tiny','96 72 m 96.125 72 l'),('ordinary','25 72 m 166 72 l')]:
    for p in (3,19):add(name+'-'+str(p),[11,17],p,path=path)
for cap in (0,2):
    for p in (3,19):add('cap'+str(cap)+'-'+str(p),[11,17],p,cap=cap)
for name,transform,w in [('transform','1.5 0.3 0.25 0.8 -66 -14.4 cm',18),('hairline','',0),('transformed-hairline','1.5 0.3 0.25 0.8 -66 -14.4 cm',0)]:
    for p in (3,19):add(name+'-'+str(p),[11,17],p,width=w,transform=transform)
for p in (3,19):add('reset-'+str(p),[11,17],p,path='26 36 m 43 36 l 96 72 m 96 72 l 153 108 m 153 108 l')
for p in (21,23,28,33,41):add('odd-doubled-'+str(p),[7,5,9,7,5,9],p)
add('zero-interior-tiny',[11,0,0,17],11,path='96 72 m 96.125 72 l')
add('gap-boundary-tiny',[11,17],11,path='96 72 m 96.125 72 l')
add('gap-near-end-tiny',[11,17],27.999,path='96 72 m 96.000125 72 l')
add('gap-cross-end-tiny',[11,17],27.999,path='96 72 m 96.125 72 l')
for c in cases:
    content=f"q 0 G {c['transform']} {c['width']} w {c['cap']} J [{' '.join(map(str,c['dash']))}] {c['phase']} d {c['path']} S Q"
    data=pdf(content)
    p=pdfdir/(c['name']+'.pdf')
    p.write_bytes(data)
    c['input_sha256']=hashlib.sha256(data).hexdigest()
    c['content']=content
    c.pop('marks')
(root/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
(root/'batch.txt').write_text(''.join(str(pdfdir/(c['name']+'.pdf'))+'\n' for c in cases))
print(f"Wrote {len(cases)} original MIT PDFs to {pdfdir}")
