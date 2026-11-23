# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Reuse owned original Type3 design; scale/rise glyph matrices independently calculated."""
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
def pose(glyph,x,y,h=1,rise=0):
 return dict(glyph=glyph,text_matrix=[1,0,0,1,x,y],glyph_matrix=[h,0,0,1,x,y+rise],horizontal_scale=h,text_rise=rise)
CASES=[('textscale-tz-shape-advance','Tz scales original glyph width and horizontal advancement, retaining vertical size.','0 g\nBT /F0 40 Tf 100 Tz 0 Ts 1 0 0 1 30 120 Tm (AB) Tj 150 Tz 1 0 0 1 30 60 Tm (AB) Tj ET\n',[pose('A',30,120),pose('B',54,120),pose('A',30,60,1.5),pose('B',66,60,1.5)],['9.3.4 Horizontal Scaling','9.4.4 Text Space Details'],['At 100%, AB x origins=30,54; glyph ink has normal horizontal size.','At 150%, AB x origins=30,30+24*1.5=66; all glyph x distances scale1.5 and y distances remain unchanged.']),('textscale-ts-baselines','Positive/negative Ts shifts glyph baselines without changing text-matrix origins or horizontal advances.','0 g\nBT /F0 40 Tf 100 Tz 0 Ts 1 0 0 1 30 80 Tm (AB) Tj 12 Ts 1 0 0 1 110 80 Tm (AB) Tj -8 Ts 1 0 0 1 170 80 Tm (AB) Tj ET\n',[pose('A',30,80),pose('B',54,80),pose('A',110,80,1,12),pose('B',134,80,1,12),pose('A',170,80,1,-8),pose('B',194,80,1,-8)],['9.3.7 Text Rise','9.4.4 Text Space Details'],['All raw text baselines are y80; rise0/+12/-8 paints at y80/92/72.','A-to-B x advance remains24 for every rise.']),('textscale-tz-spacing','Tz scales character spacing and single-byte word spacing together with glyph advancement.','0 g\nBT /F0 40 Tf 3 Tc 7 Tw 100 Tz 0 Ts 30 120 Td (A B) Tj 150 Tz 0 -60 Td (A B) Tj ET\n',[pose('A',30,120),pose('B',77,120),pose('A',30,60,1.5),pose('B',100.5,60,1.5)],['9.3.4 Horizontal Scaling','9.3.2 Character Spacing','9.3.3 Word Spacing'],['Normal A-space-B second visible origin x=30+(24+3)+(10+3+7)=77.','At150%, x=30+((24+3)+(10+3+7))*1.5=100.5.']),('textscale-tz-tj-rise','Tz scales signed TJ displacements and character spacing; Ts shifts painting independently.','0 g\nBT /F0 40 Tf 8 Tc 100 Tz 0 Ts 30 120 Td [(A) 100 (B) -250 (A)] TJ 150 Tz 10 Ts 0 -60 Td [(A) 100 (B) -250 (A)] TJ ET\n',[pose('A',30,120),pose('B',58,120),pose('A',96,120),pose('A',30,60,1.5,10),pose('B',72,60,1.5,10),pose('A',129,60,1.5,10)],['9.3.4 Horizontal Scaling','9.3.7 Text Rise','9.4.3 Text-Showing Operators','9.4.4 Text Space Details'],['Normal row origins x30,58,96 with Tc8 and TJ100/-250.','At150%, Bx=30+(24+8-4)*1.5=72; Ax=72+(20+8+10)*1.5=129.','Second text baseline y60, painted y70 due to rise10; horizontal scale does not multiply rise.'])]
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
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract=contract,layout_math=math,spec='ISO 32000-1:2008',spec_clauses=clauses+['9.6.5 Type 3 Fonts'],route='page BT/ET owned original Type3 CharProcs, Tz/Ts and named positioning controls',width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],sha256=sha(data),font=dict(kind='Type3',original_design_reused=True,external_font_bytes=0,size=40,font_matrix=[.001,0,0,.001,0,0],glyph_stream_sha256={'A':sha(A),'B':sha(B),'space':sha(SPACE)}),expected_glyphs=positions,expected_samples=samples,expected_regions=regions,region_rule='Original glyph ink/counter rectangles transformed from explicit effective glyph matrices, inset 1 PDF point before references; boundaries unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No matching upstream scene scope established.')))
(R/'original-font.json').write_text(json.dumps(dict(license='MIT',authoring='Owned original design reused from ISO-TEXT-POSITION-01; numeric outlines/metrics, zero external/system font bytes.',glyphs=GLYPHS,space_width=250),indent=2)+'\n')
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-TEXT-SCALE-RISE-01',fixture_count=4,cases=cases),indent=2)+'\n')
print('Generated4 unique PDFs, reused1 original font, four named scale/rise contracts.')
