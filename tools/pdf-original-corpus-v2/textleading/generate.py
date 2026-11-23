# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Reuse owned original Type3 design; leading/line matrices independently calculated."""
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
def pose(glyph,x,y,leading):
 return dict(glyph=glyph,text_matrix=[1,0,0,1,x,y],glyph_matrix=[1,0,0,1,x,y],horizontal_scale=1,text_rise=0,leading=leading)
def line(text,x,y,leading):
 return [pose(text[0],x,y,leading),pose(text[1],x+(24 if text[0]=='A' else 20),y,leading)]
CASES=[('textleading-tl-nextline','T* uses negative TL and the line origin after Tj advances the current text matrix.','0 g\nBT /F0 40 Tf 40 TL 30 135 Td (AB) Tj T* (BA) Tj T* (AB) Tj ET\n',line('AB',30,135,40)+line('BA',30,95,40)+line('AB',30,55,40),['9.3.5 Leading','9.4.2 Text-Positioning Operators'],['Leading40 gives baselines135,95,55.','Tj advances do not affect the next line x30; BA second glyph x50 and AB second glyph x54.']),('textleading-td-sets-leading','TD moves the line origin and sets leading to negative ty for a subsequent T*.','0 g\nBT /F0 40 Tf 20 TL 30 135 Td (AB) Tj 10 -45 TD (BA) Tj T* (AB) Tj ET\n',line('AB',30,135,20)+line('BA',40,90,45)+line('AB',40,45,45),['9.3.5 Leading','9.4.2 Text-Positioning Operators, Table 108'],['Initial leading20 is replaced by45 because TD ty=-45.','TD offset from line (30,135) gives (40,90); T* gives (40,45), independent of preceding Tj advancement.']),('textleading-td-preserves-leading','Td changes the line origin but preserves TL for a subsequent T*.','0 g\nBT /F0 40 Tf 40 TL 30 140 Td (AB) Tj 15 -35 Td (BA) Tj T* (AB) Tj ET\n',line('AB',30,140,40)+line('BA',45,105,40)+line('AB',45,65,40),['9.3.5 Leading','9.4.2 Text-Positioning Operators, Table 108'],['Td (15,-35) from (30,140) gives (45,105).','Leading remains40, so T* gives (45,65), not (45,70).']),('textleading-bt-reset-leading-persists','New BT resets text and line matrices while leading persists as text state across objects.','0 g\nBT /F0 40 Tf 45 TL 30 130 Td (AB) Tj ET\nBT /F0 40 Tf 70 90 Td (BA) Tj T* (AB) Tj ET\n',line('AB',30,130,45)+line('BA',70,90,45)+line('AB',70,45,45),['9.3.1 General, text-state retention','9.4.1 General, text object operators','9.4.2 Text-Positioning Operators'],['Second BT resets both matrices to identity; Td (70,90) gives that absolute origin.','Leading45 persists from the first text object; T* gives (70,45).'])]
def transformed(rect,m):
 x,y,w,h=rect;a,b,c,d,e,f=m
 points=[(a*u*.04+c*v*.04+e,b*u*.04+d*v*.04+f) for u,v in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]]
 loX=min(x for x,y in points);hiX=max(x for x,y in points);loY=min(y for x,y in points);hiY=max(y for x,y in points)
 return [round(loX+1,6),round(loY+1,6),round(hiX-loX-2,6),round(hiY-loY-2,6)]
cases=[]
for fid,contract,content,positions,clauses,math in CASES:
 data=pdf(content);(OUT/(fid+'.pdf')).write_bytes(data);regions=[]
 for n,position in enumerate(positions):
  glyph=position['glyph'];m=position['glyph_matrix']
  for kind,color in [('ink',[0,0,0]),('counter',[255,255,255])]:
   for k,rect in enumerate(GLYPHS[glyph][kind]):regions.append(dict(id=f'glyph-{n}-{glyph}-{kind}-{k}',rect=transformed(rect,m),rgb=color,tolerance=0))
 regions.append(dict(id='paper',rect=[4,4,16,16],rgb=[255,255,255],tolerance=0))
 samples=[dict(id=v['id'],point=[round(v['rect'][0]+v['rect'][2]/2,6),round(v['rect'][1]+v['rect'][3]/2,6)],rgb=v['rgb'],tolerance=0) for v in regions]
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract=contract,layout_math=math,spec='ISO 32000-1:2008',spec_clauses=clauses+['9.6.5 Type 3 Fonts'],route='page BT/ET owned original Type3 CharProcs, TL/T*/TD/Td and Tj line-origin controls',width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],sha256=sha(data),font=dict(kind='Type3',original_design_reused=True,external_font_bytes=0,size=40,font_matrix=[.001,0,0,.001,0,0],glyph_stream_sha256={'A':sha(A),'B':sha(B),'space':sha(SPACE)}),expected_glyphs=positions,expected_samples=samples,expected_regions=regions,region_rule='Original glyph ink/counter rectangles transformed from explicit effective glyph matrices, inset 1 PDF point before references; boundaries unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='Metadata review establishes no exact upstream leading-contract scope.')))
(R/'original-font.json').write_text(json.dumps(dict(license='MIT',authoring='Owned original design reused from ISO-TEXT-POSITION-01; numeric outlines/metrics, zero external/system font bytes.',glyphs=GLYPHS,space_width=250),indent=2)+'\n')
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-TEXT-LEADING-01',fixture_count=4,cases=cases),indent=2)+'\n')
print('Generated 4 original PDFs, 1 reused original font, 4 named leading contracts.')
