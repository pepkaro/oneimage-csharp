# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Owned original Type3 font; Tr3 ink suppression, advancement and nonclipping controls."""
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
def pose(glyph,x,y,lx,ly,mode,tc=0,tw=0):
 return dict(glyph=glyph,text_matrix=[1,0,0,1,x,y],line_matrix=[1,0,0,1,lx,ly],glyph_matrix=[1,0,0,1,x,y],horizontal_scale=1,text_rise=0,leading=45,character_spacing=tc,word_spacing=tw,render_mode=mode)
CASES=[('text-invisible-advance','Tr3 paints no ink but advances current text before later Tr0 glyphs.','0 g\nBT /F0 40 Tf 45 TL 30 90 Td 3 Tr (AB) Tj 0 Tr (BA) Tj ET\n',[pose('A',30,90,30,90,3),pose('B',54,90,30,90,3),pose('B',74,90,30,90,0),pose('A',94,90,30,90,0)],['Invisible AB advances24+20 points; visible BA begins at x74,94.','Line matrix stays(30,90) through both strings.']),('text-invisible-spacing-tj','Invisible Tj/TJ honors character/word spacing and signed TJ shifts before visible text.','0 g\nBT /F0 40 Tf 45 TL 3 Tc 7 Tw 30 130 Td 3 Tr [(A ) 100 (B) -250 (A)] TJ 0 Tr (B) Tj ET\nBT /F0 40 Tf 45 TL 3 Tc 7 Tw 133 60 Td 0 Tr (B) Tj ET\n',[pose('A',30,130,30,130,3,3,7),pose('B',73,130,30,130,3,3,7),pose('A',106,130,30,130,3,3,7),pose('B',133,130,30,130,0,3,7),pose('B',133,60,133,60,0,3,7)],['A plus space advances27+20 to77; TJ100 subtracts4 to place invisible B at73.','B advances23, TJ-250 adds10: invisible A at106; its27-point advance places visible B at133.','A separate visible control is explicitly positioned at x133,y60.']),('text-invisible-object-state','Tr3 persists across BT/ET while matrices reset; switching to Tr0 uses accumulated second-object advancement.','0 g\nBT /F0 40 Tf 45 TL 3 Tr 30 130 Td (AB) Tj ET\nBT /F0 40 Tf 45 TL 90 80 Td (BA) Tj 0 Tr (AB) Tj ET\n',[pose('A',30,130,30,130,3),pose('B',54,130,30,130,3),pose('B',90,80,90,80,3),pose('A',110,80,90,80,3),pose('A',134,80,90,80,0),pose('B',158,80,90,80,0)],['Second BT resets matrices to identity; Td90,80 positions invisible BA there while Tr3 persists.','Invisible BA advances20+24, so visible AB starts at x134,158.']),('text-invisible-no-clip','Tr3 adds no glyph clipping: subsequent ordinary page graphics remain fully painted.','0 g\nBT /F0 40 Tf 45 TL 3 Tr 30 80 Td (AB) Tj ET\n0 0 1 rg 20 70 100 60 re f\n',[pose('A',30,80,30,80,3),pose('B',54,80,30,80,3)],['The subsequent blue rectangle remains visible throughout its declared interior, including areas outside every glyph.','This case tests later nontext painting, not invisibility beneath the overpainted rectangle. No Tr7 is used.'])]
def transformed(rect,m):
 x,y,w,h=rect;a,b,c,d,e,f=m
 points=[(a*u*.04+c*v*.04+e,b*u*.04+d*v*.04+f) for u,v in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]]
 loX=min(x for x,y in points);hiX=max(x for x,y in points);loY=min(y for x,y in points);hiY=max(y for x,y in points)
 return [round(loX+1,6),round(loY+1,6),round(hiX-loX-2,6),round(hiY-loY-2,6)]
cases=[]
for fid,contract,content,positions,math in CASES:
 data=pdf(content);(OUT/(fid+'.pdf')).write_bytes(data);regions=[]
 if fid=='text-invisible-no-clip':
  regions=[dict(id='later-blue-paint-interior',rect=[22,72,96,56],rgb=[0,0,255],tolerance=0),dict(id='outside-blue-left',rect=[12,80,6,40],rgb=[255]*3,tolerance=0)]
 else:
  for n,position in enumerate(positions):
   glyph=position['glyph'];m=position['glyph_matrix']
   for kind in ['ink','counter']:
    rgb=[0,0,0] if kind=='ink' and position['render_mode']==0 else [255]*3
    for k,rect in enumerate(GLYPHS[glyph][kind]):regions.append(dict(id=f'glyph-{n}-{glyph}-{kind}-{k}-Tr{position["render_mode"]}',rect=transformed(rect,m),rgb=rgb,tolerance=0))
 regions.append(dict(id='paper',rect=[4,4,16,16],rgb=[255]*3,tolerance=0))
 samples=[dict(id=v['id'],point=[round(v['rect'][0]+v['rect'][2]/2,6),round(v['rect'][1]+v['rect'][3]/2,6)],rgb=v['rgb'],tolerance=0) for v in regions]
 cases.append(dict(id=fid,fixture_id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract=contract,layout_math=math,spec='ISO 32000-1:2008',spec_clauses=['9.3.6 Text Rendering Mode, Table 106, Type3 mode3 exception','9.3.1 Text-state retention','9.4.3 Text-Showing Operators','9.4.4 Text Space Details','9.6.5 Type 3 Fonts'],route='page BT/ET original owned Type3 procedures, Tr3/Tr0 only; independent advancement/spacing/state/nontext controls',width=240,height=180,page=0,page_count=1,dpis=[72,144],rotation=0,annotations='none',background=[255]*3,sha256=sha(data),sha=sha(data),font=dict(kind='Type3',original_design_reused=True,external_font_bytes=0,size=40,font_matrix=[.001,0,0,.001,0,0],glyph_stream_sha256={'A':sha(A),'B':sha(B),'space':sha(SPACE)}),expected_glyphs=positions,expected_samples=samples,expected_regions=regions,region_rule='Original glyph ink/counter rectangles inset1point; invisible would-be ink is white. Later-paint case scores separate analytic rectangle interiors. All boundaries unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream invisible-text scene assertion established.')))
(R/'original-font.json').write_text(json.dumps(dict(license='MIT',authoring='Owned numeric design reused from ISO-TEXT-POSITION-01; no external/system font bytes.',glyphs=GLYPHS,space_width=250),indent=2)+'\n')
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-TEXT-INVISIBLE-01',fixture_count=4,scope='Tr3/Tr0 only; no Tr7 or clipping-mode parity claim.',cases=cases),indent=2)+'\n')
print('Generated 4 original PDFs: Tr3/Tr0 only; no external font bytes.')
