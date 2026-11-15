# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original numeric geometry and Type 3 glyph program. No external fixture inputs.
import argparse
import hashlib
import json
from pathlib import Path


def document(content, type3=False):
    resources = '/Font << /F 5 0 R >>' if type3 else ''
    glyph = content
    if type3:
        content = 'BT /F 1 Tf 1 0 0 1 0 0 Tm (a) Tj ET'
    def stream(s):
        data = s.encode('ascii')
        return b'<< /Length ' + str(len(data)).encode() + b' >>\nstream\n' + data + b'\nendstream'
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 192 144] /CropBox [0 0 192 144] /Rotate 0 /Resources << ' + resources + ' >> /Contents 4 0 R >>').encode(), stream(content)]
    if type3:
        objects += [b'<< /Type /Font /Subtype /Type3 /FontBBox [0 0 100 80] /FontMatrix [1 0 0 1 0 0] /CharProcs << /a 6 0 R >> /Encoding << /Type /Encoding /Differences [97 /a] >> /FirstChar 97 /LastChar 97 /Widths [100] /Resources << >> >>', stream('100 0 d0 ' + glyph)]
    data = b'%PDF-1.7\n'
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(data))
        data += f'{number} 0 obj\n'.encode() + body + b'\nendobj\n'
    xref = len(data)
    data += f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{position:010d} 00000 n \n'.encode() for position in offsets)
    return data + f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()


def cases():
    result = []
    def add(name, path, dash='[] 0 d', width=18, cap=1, transform='', type3=False, change=False):
        result.append(dict(name=name, content=f'0 G {transform} {width} w {cap} J {dash} {path} S', type3=type3, expected_change=change))
    paths = {'open':'48 36 m 48 36 l', 'closed':'48 36 m 48 36 l h', 'rectangle':'48 36 0 0 re',
        'close-only':'48 36 m h', 'repeated':'48 36 m 48 36 l 48 36 l h',
        'cubic':'48 36 m 48 36 48 36 48 36 c h', 'reclosed':'48 36 m 48 36 l h h',
        'close-line-close':'48 36 m 48 36 l h 48 36 l h', 'move-only':'48 36 m'}
    for shape,path in paths.items():
        for label,dash in [('solid','[] 0 d'),('on','[11 17] 3 d'),('off','[11 17] 19 d'),('zero-on','[0 17] 0 d')]:
            add(shape+'-'+label, path, dash, change=label=='solid' and shape not in ('open','close-only','move-only'))
    for label,transform,width in [('skew','1.5 0.3 0.25 0.8 -33 -7.2 cm',18),('reflect','-1 0 0 1 96 0 cm',18),
        ('hairline','',0),('skew-hairline','1.5 0.3 0.25 0.8 -33 -7.2 cm',0),('minimum','',0.01)]:
        for shape in ('open','closed'):
            add(label+'-'+shape,paths[shape],width=width,transform=transform,change=shape=='closed')
    for cap in (0,2):
        for shape in ('open','closed','close-only'):
            add(f'cap-{cap}-'+shape,paths[shape],cap=cap)
    for shape,path in [('positive','48 36 m 65 36 l'),('ordinary-closed','20 20 m 35 20 l 35 30 l h'),
        ('tiny','48 36 m 48.125 36 l h'),('float-collapse','48 36 m 48.00000001 36 l h'),
        ('moving-cubic','48 36 m 49 36 47 36 48 36 c h')]:
        for label,dash in [('solid','[] 0 d'),('on','[11 17] 3 d'),('off','[11 17] 19 d')]:
            add(shape+'-'+label,path,dash)
    for label,dash in [('all-zero','[0 0] 0 d'),('tiny-fallback','[0.00001 0.00001] 0 d')]:
        for shape in ('open','closed'):
            add(label+'-'+shape,paths[shape],dash,change=shape=='closed')
    for label,path in [('incomplete-line','48 36 m 48 36 l h 2 l'),('incomplete-curve','48 36 m 48 36 l h 48 36 48 c'),
        ('prefix','48 36 m 48 36 l h 68 36 l'),('mixed','9 12 m 29 12 l 29 22 l h 48 36 0 0 re 130 95 m')]:
        add(label,path,change=True)
    for label,dash in [('solid','[] 0 d'),('on','[11 17] 3 d'),('off','[11 17] 19 d')]:
        for shape in ('open','closed'):
            add('type3-'+shape+'-'+label,paths[shape],dash,type3=True,change=shape=='closed' and label=='solid')
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    pdf=args.output/'pdf';pdf.mkdir(exist_ok=True)
    rows=cases()
    for row in rows:
        data=document(row['content'],row['type3'])
        (pdf/(row['name']+'.pdf')).write_bytes(data)
        row['input_sha256']=hashlib.sha256(data).hexdigest()
    (args.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    (args.output/'batch.txt').write_text(''.join(str((pdf/(row['name']+'.pdf')).resolve())+'\n' for row in rows))
    print(f'Wrote {len(rows)} original MIT control PDFs.')

if __name__=='__main__': main()
