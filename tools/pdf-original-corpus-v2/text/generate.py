# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Original Type3 rectangle glyphs and manually calculated text origins; no input font/file."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
OUT=R/'inputs';OUT.mkdir(exist_ok=True)
# Original unhinted vector designs, in glyph units. No external glyph outline is used.
GLYPHS={'A':dict(name='gA',code=65,width=600,bbox=[0,0,600,700],ink=[[0,0,120,580],[480,0,120,580],[0,580,600,120]],counter=[[120,0,360,580]]),'B':dict(name='gB',code=66,width=500,bbox=[0,0,480,700],ink=[[0,0,120,700],[120,0,360,120],[120,290,360,120],[120,580,360,120]],counter=[[120,120,360,170],[120,410,360,170]])}
def sha(x):return hashlib.sha256(x).hexdigest()
def stream(data):return f'<< /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'
def glyph_bytes(key):
 g=GLYPHS[key];s=f"{g['width']} 0 {' '.join(map(str,g['bbox']))} d1\n"
 return (s+''.join(' '.join(map(str,rect))+' re f\n' for rect in g['ink'])).encode()
A=glyph_bytes('A');B=glyph_bytes('B');SPACE=b'250 0 d0\n'
CMAP=b'/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n/CIDSystemInfo << /Registry (Original) /Ordering (Corpus) /Supplement 0 >> def\n/CMapName /OriginalBarsUnicode def\n/CMapType 2 def\n1 begincodespacerange\n<00> <FF>\nendcodespacerange\n3 beginbfchar\n<20> <0020>\n<41> <0041>\n<42> <0042>\nendbfchar\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n'
widths=[250 if code==32 else 600 if code==65 else 500 if code==66 else 0 for code in range(32,67)]
font=('<< /Type /Font /Subtype /Type3 /Name /OriginalBars /FontBBox [0 0 600 700] /FontMatrix [0.001 0 0 0.001 0 0] /CharProcs << /gA 6 0 R /gB 7 0 R /space 8 0 R >> /Encoding << /Type /Encoding /Differences [32 /space 65 /gA /gB] >> /FirstChar 32 /LastChar 66 /Widths ['+' '.join(map(str,widths))+'] /Resources << >> /ToUnicode 9 0 R >>').encode()
def pdf(content):
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 180] /CropBox [0 0 240 180] /Rotate 0 /Resources << /Font << /F0 5 0 R >> >> /Contents 4 0 R >>',stream(content.encode()),font,stream(A),stream(B),stream(SPACE),stream(CMAP)]
 b=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offset=[]
 for i,obj in enumerate(objects,1):offset.append(len(b));b.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(b);b.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
 for n in offset:b.extend(f'{n:010d} 00000 n \n'.encode())
 b.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(b)
def matrix(x,y,rotated=False):return [0,1,-1,0,x,y] if rotated else [1,0,0,1,x,y]
CASES=[('text-td-line-origin','Td restores the line origin after Tj advances the text matrix.', '0 g\nBT /F0 40 Tf 1 0 0 1 30 120 Tm (AB) Tj 0 -55 Td (BA) Tj ET\n',[('A',matrix(30,120)),('B',matrix(54,120)),('B',matrix(30,65)),('A',matrix(50,65))],['9.4.2 Text-Positioning Operators, Table 108','9.4.3 Text-Showing Operators']),('text-tc-tw-spacing','Independent default/Tc/Tw controls distinguish character advancement from single-byte space advancement.','0 g\nBT /F0 40 Tf 30 130 Td (AB) Tj 3 Tc 0 -50 Td (AB) Tj 7 Tw 0 -50 Td (A B) Tj ET\n',[('A',matrix(30,130)),('B',matrix(54,130)),('A',matrix(30,80)),('B',matrix(57,80)),('A',matrix(30,30)),('B',matrix(77,30))],['9.3.2 Character Spacing','9.3.3 Word Spacing','9.4.2 Text-Positioning Operators']),('text-tj-signed-adjustment','TJ positive/negative adjustments subtract their thousandths-of-font-size displacement, separate from Tc.','0 g\nBT /F0 40 Tf 8 Tc 1 0 0 1 30 80 Tm [(A) 100 (B) -250 (A)] TJ ET\n',[('A',matrix(30,80)),('B',matrix(58,80)),('A',matrix(96,80))],['9.4.3 Text-Showing Operators, Table 109','9.3.2 Character Spacing']),('text-tm-rotate-replace','Tm rotates glyph shape/advance, then replaces both text matrices with a new ordinary matrix.','0 g\nBT /F0 40 Tf 0 1 -1 0 160 40 Tm (AB) Tj 1 0 0 1 30 120 Tm (BA) Tj ET\n',[('A',matrix(160,40,True)),('B',matrix(160,64,True)),('B',matrix(30,120)),('A',matrix(50,120))],['9.4.2 Text-Positioning Operators, Table 108','9.4.4 Text Space Details'])]
def transformed(rect,m):
 x,y,w,h=rect;a,b,c,d,e,f=m
 points=[(a*u*.04+c*v*.04+e,b*u*.04+d*v*.04+f) for u,v in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]]
 loX=min(x for x,y in points);hiX=max(x for x,y in points);loY=min(y for x,y in points);hiY=max(y for x,y in points)
 return [round(loX+1,6),round(loY+1,6),round(hiX-loX-2,6),round(hiY-loY-2,6)]
LAYOUT={'text-td-line-origin': ['Font-size 40 advances A=24 and B=20 points.', 'First line origins (30,120),(54,120). Tj leaves text matrix advanced; Td uses text LINE matrix.', 'Td (0,-55) sets next line origin (30,65); BA origins (30,65),(50,65).'], 'text-tc-tw-spacing': ['Default AB origins x=30,54 at y=130.', 'Tc=3 makes AB origins x=30,57 at y=80.', 'With Tc=3,Tw=7, A-space-B gives B x=30+(24+3)+(10+3+7)=77 at y=30.'], 'text-tj-signed-adjustment': ['At size40,Tc8: A x=30; B x=30+24+8-100*40/1000=58.', 'A after B: x=58+20+8-(-250)*40/1000=96.'], 'text-tm-rotate-replace': ['Rotated Tm [0,1,-1,0,160,40] maps A origin to (160,40), B to (160,64).', 'Replacement Tm [1,0,0,1,30,120] sets BA origins (30,120),(50,120). It does not concatenate.']}
cases=[]
for fid,contract,content,positions,clauses in CASES:
 data=pdf(content);(OUT/(fid+'.pdf')).write_bytes(data);regions=[]
 for n,(glyph,m) in enumerate(positions):
  for kind,color in [('ink',[0,0,0]),('counter',[255,255,255])]:
   for k,rect in enumerate(GLYPHS[glyph][kind]):regions.append(dict(id=f'glyph-{n}-{glyph}-{kind}-{k}',rect=transformed(rect,m),rgb=color,tolerance=0))
 regions.append(dict(id='paper',rect=[4,4,16,16],rgb=[255,255,255],tolerance=0))
 samples=[dict(id=v['id'],point=[round(v['rect'][0]+v['rect'][2]/2,6),round(v['rect'][1]+v['rect'][3]/2,6)],rgb=v['rgb'],tolerance=0) for v in regions]
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract=contract,layout_math=LAYOUT[fid],spec='ISO 32000-1:2008',spec_clauses=clauses+['9.6.5 Type 3 Fonts'],route='page BT/ET original embedded Type3 CharProcs, '+fid.removeprefix('text-'),width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],sha256=sha(data),font=dict(kind='Type3',external_font_bytes=0,size=40,font_matrix=[.001,0,0,.001,0,0],glyph_stream_sha256={'A':sha(A),'B':sha(B),'space':sha(SPACE)}),expected_glyphs=[dict(glyph=a,text_matrix=b) for a,b in positions],expected_samples=samples,expected_regions=regions,region_rule='Original glyph ink/counter rectangles transformed from explicit text matrices, inset 1 PDF point before reference generation; boundaries unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No matching upstream scene scope established.')))
(R/'original-font.json').write_text(json.dumps(dict(license='MIT',authoring='All vector rectangles and metrics independently defined from numeric constants. No font file or external glyph outline read.',glyphs=GLYPHS,space_width=250),indent=2)+'\n')
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-TEXT-POSITION-01',fixture_count=4,cases=cases),indent=2)+'\n')
print('Generated 4 unique original-font text-positioning PDFs; no external/system font bytes.')
