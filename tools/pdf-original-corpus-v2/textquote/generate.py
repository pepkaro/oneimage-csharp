# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Owned original Type3 font; quote-operator matrices and state independently calculated."""
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
def pose(glyph,x,y,lx,ly,tc=0,tw=0):
 return dict(glyph=glyph,text_matrix=[1,0,0,1,x,y],line_matrix=[1,0,0,1,lx,ly],glyph_matrix=[1,0,0,1,x,y],horizontal_scale=1,text_rise=0,leading=45,character_spacing=tc,word_spacing=tw)
def pair(text,x,y,tc=0,tw=0,space=False):
 second=x+(24 if text[0]=='A' else 20)+tc+(10+tc+tw if space else 0)
 return [pose(text[0],x,y,x,y,tc,tw),pose(text[1],second,y,x,y,tc,tw)]
CASES=[('textquote-single-equivalent','Single quote matches explicit T* plus Tj and ignores prior current-matrix advancement.', '''0 g
BT /F0 40 Tf 45 TL 0 Tc 0 Tw 25 130 Td (AB) Tj (BA) ' ET
BT /F0 40 Tf 45 TL 0 Tc 0 Tw 125 130 Td (AB) Tj T* (BA) Tj ET
''',pair('AB',25,130)+pair('BA',25,85)+pair('AB',125,130)+pair('BA',125,85),['Quote and explicit controls have line origins x25/x125 and baselines130,85.','On each BA line, A begins20 points after B; prior AB advancement does not enter next-line x.']),('textquote-double-equivalent','Double quote sets Tw then Tc, advances one line, and matches explicit spacing/T*/Tj controls.', '''0 g
BT /F0 40 Tf 45 TL 0 Tc 0 Tw 25 135 Td (AB) Tj 7 3 (A B) " ET
BT /F0 40 Tf 45 TL 0 Tc 0 Tw 125 135 Td (AB) Tj 7 Tw 3 Tc T* (A B) Tj ET
''',pair('AB',25,135)+pair('AB',25,90,3,7,True)+pair('AB',125,135)+pair('AB',125,90,3,7,True),['Double quote operands aw7/ac3 set Tw7/Tc3 before showing.','Second-line B origins are25+24+3+10+3+7=72 and172 in the explicit column.']),('textquote-spacing-persists','Double-quote spacing persists into a subsequent Tj and single quote; each quote uses the line origin.', '''0 g
BT /F0 40 Tf 45 TL 0 Tc 0 Tw 30 140 Td (AB) Tj 7 3 (A B) " (AB) Tj (BA) ' ET
''',pair('AB',30,140)+pair('AB',30,95,3,7,True)+[pose('A',100,95,30,95,3,7),pose('B',127,95,30,95,3,7)]+pair('BA',30,50,3,7),['Quote A-space-B origins x30,77 at y95; it leaves current x100.','Following Tj AB paints at x100,127 while line x remains30.','Single quote paints BA at x30,53,y50 and preserves Tc3/Tw7.']),('textquote-shift-and-object-state','Double quote follows a shifted line matrix; its spacing survives ET/BT while the matrices reset.', '''0 g
BT /F0 40 Tf 45 TL 0 Tc 0 Tw 30 140 Td (AB) Tj 20 -40 Td 5 2 (BA) " ET
BT /F0 40 Tf 45 TL 115 80 Td (A B) Tj ET
''',pair('AB',30,140)+pair('BA',50,55,2,5)+pair('AB',115,80,2,5,True),['Td shifts line origin to(50,100); double quote uses leading45 to paint BA at(50,55),(72,55).','New BT resets matrices; Td115,80 starts there, retaining Tc2/Tw5.','A-space-B then has Bx115+24+2+10+2+5=158.'])]
def transformed(rect,m):
 x,y,w,h=rect;a,b,c,d,e,f=m
 points=[(a*u*.04+c*v*.04+e,b*u*.04+d*v*.04+f) for u,v in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]]
 loX=min(x for x,y in points);hiX=max(x for x,y in points);loY=min(y for x,y in points);hiY=max(y for x,y in points)
 return [round(loX+1,6),round(loY+1,6),round(hiX-loX-2,6),round(hiY-loY-2,6)]
cases=[]
for fid,contract,content,positions,math in CASES:
 data=pdf(content);(OUT/(fid+'.pdf')).write_bytes(data);regions=[]
 for n,position in enumerate(positions):
  glyph=position['glyph'];m=position['glyph_matrix']
  for kind,color in [('ink',[0,0,0]),('counter',[255,255,255])]:
   for k,rect in enumerate(GLYPHS[glyph][kind]):regions.append(dict(id=f'glyph-{n}-{glyph}-{kind}-{k}',rect=transformed(rect,m),rgb=color,tolerance=0))
 regions.append(dict(id='paper',rect=[4,4,16,16],rgb=[255,255,255],tolerance=0))
 samples=[dict(id=v['id'],point=[round(v['rect'][0]+v['rect'][2]/2,6),round(v['rect'][1]+v['rect'][3]/2,6)],rgb=v['rgb'],tolerance=0) for v in regions]
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract=contract,layout_math=math,spec='ISO 32000-1:2008',spec_clauses=['9.4.3 Text-Showing Operators, Table 109','9.4.2 Text-Positioning Operators','9.3.1 Text-state retention','9.6.5 Type 3 Fonts'],route='page BT/ET owned original Type3 CharProcs; quote operators and explicit equivalent controls',width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],sha256=sha(data),font=dict(kind='Type3',original_design_reused=True,external_font_bytes=0,size=40,font_matrix=[.001,0,0,.001,0,0],glyph_stream_sha256={'A':sha(A),'B':sha(B),'space':sha(SPACE)}),expected_glyphs=positions,expected_samples=samples,expected_regions=regions,region_rule='Original glyph ink/counter rectangles transformed from explicit effective glyph matrices, inset 1 PDF point before references; boundaries unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream quote-operator scene scope established from metadata.')))
(R/'original-font.json').write_text(json.dumps(dict(license='MIT',authoring='Owned original design reused from ISO-TEXT-POSITION-01; numeric outlines/metrics, zero external/system font bytes.',glyphs=GLYPHS,space_width=250),indent=2)+'\n')
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-TEXT-QUOTE-01',fixture_count=4,cases=cases),indent=2)+'\n')
print('Generated 4 original quote PDFs, 1 reused original font, 4 named contracts.')
