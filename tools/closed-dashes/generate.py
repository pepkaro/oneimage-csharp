# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Independently authored numeric geometry. No input PDFs, fonts, images or vendor assets.
import argparse, hashlib, json
from pathlib import Path

def document(content):
    data = content.encode('ascii')
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 192 144] /CropBox [0 0 192 144] /Rotate 0 /Resources << >> /Contents 4 0 R >>',
        b'<< /Length '+str(len(data)).encode()+b' >>\nstream\n'+data+b'\nendstream']
    out = b'%PDF-1.7\n'
    offsets=[]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out)); out+=f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref=len(out)
    out+=b'xref\n0 5\n0000000000 65535 f \n'+b''.join(f'{p:010d} 00000 n \n'.encode() for p in offsets)
    return out+f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()

def cases():
    result=[]
    def add(name, body, group): result.append(dict(name=name, content=body, group=group))
    shapes={'tiny':'48 36 m 48.125 36 l h', 'cubic':'48 36 m 49 36 47 36 48 36 c h',
        'rectangle':'24 24 8 6 re', 'triangle':'22 24 m 35 25 l 29 37 l h'}
    for shape,path in shapes.items():
        for join in range(3):
            for label,dash in [('solid','[] 0 d'),('whole-on','[200 17] 3 d'),('all-off','[200 200] 220 d'),('ordinary','[4 3] 1 d')]:
                add(f'{shape}-j{join}-{label}',f'0 G 18 w 1 J {join} j {dash} {path} S',label)
    for cap in range(3):
        for label,body in [('initial-gap','[60 20] 65 d 20 20 10 10 re'),('explicit-gap','30 25 m 30 30 l 20 30 l 20 20 l')]:
            add(f'{label}-c{cap}',f'0 G 4 w {cap} J {body} S',label)
    for phase in [0,3,10.749,10.75,10.751,11,19,27.875,28,31]:
        add('tiny-phase-'+str(phase).replace('.','_'),f'0 G 18 w 1 J [11 17] {phase} d {shapes["tiny"]} S','phase-boundary')
    for label,ctm,width in [('skew','1.5 .3 .25 .8 -33 -7.2 cm',18),('reflect','-1 0 0 1 96 0 cm',18),('hairline','',0),('skew-hairline','1.5 .3 .25 .8 -33 -7.2 cm',0),('minimum','',.01)]:
        for dashname,dash in [('solid','[] 0 d'),('whole-on','[200 17] 3 d')]:
            add(f'{label}-{dashname}',f'0 G {ctm} {width} w 1 J {dash} 24 24 8 6 re S',dashname)
    for label,path in [('open','20 20 m 80 35 l 35 70 l'),('multi','20 20 10 10 re 70 60 25 20 re'),('stationary','48 36 m 48 36 l h')]:
        for name,dash in [('solid','[] 0 d'),('whole-on','[200 17] 3 d'),('crossing','[4 3] 1 d'),('odd','[7 5 9] 12 d'),('zero','[0 17] 0 d')]:
            add(f'{label}-{name}',f'0 G 4 w 1 J {dash} {path} S','unchanged' if label in ('open','stationary') or name not in ('whole-on',) else 'whole-on')
    for label,dash in [("solid","[] 0 d"),("whole-on","[200 17] 3 d")]:
        add("explicit-repeated-return-"+label,f"0 G 18 w 1 J {dash} 48 36 m 48.125 36 l 48 36 l 48 36 l h S",label)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('output',type=Path); args=parser.parse_args()
    root=args.output; (root/'pdf').mkdir(parents=True,exist_ok=True)
    items=cases()
    for item in items:
        data=document(item['content']); (root/'pdf'/(item['name']+'.pdf')).write_bytes(data)
        item['input_sha256']=hashlib.sha256(data).hexdigest()
    (root/'cases.json').write_text(json.dumps(items,indent=2)+'\n')
    (root/'inputs.txt').write_text(''.join(str((root/'pdf'/(c['name']+'.pdf')).resolve())+'\t'+c['name']+'\n' for c in items))
    print(f'Generated {len(items)} original MIT numeric-geometry PDFs.')
