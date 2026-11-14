#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
"""Newly authored PDF behavior cases. No upstream PDF, font, art, text or test source is an input."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/'tests/testdata/pdf-novel-mit'

def stream(content, entries=''):
    data=content.encode('ascii') if isinstance(content,str) else content
    return f'<< {entries} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'

class Document:
    def __init__(self):self.objects=[b'',b'',b''];self.resources='';self.page_entries='';self.catalog_entries=''
    def add(self,value):
        self.objects.append(value.encode('ascii') if isinstance(value,str) else value)
        return len(self.objects)
    def finish(self,content):
        ref=self.add(stream(content))
        self.objects[0]=f'<< /Type /Catalog /Pages 2 0 R {self.catalog_entries} >>'.encode()
        self.objects[1]=b'<< /Type /Pages /Count 1 /Kids [3 0 R] >>'
        self.objects[2]=f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 320 240] /Resources << {self.resources} >> /Contents {ref} 0 R {self.page_entries} >>'.encode()
        data=bytearray(b'%PDF-1.7\n% independently authored MIT behavior fixture\n');offsets=[]
        for n,obj in enumerate(self.objects,1):offsets.append(len(data));data.extend(f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n')
        xref=len(data);data.extend(f'xref\n0 {len(self.objects)+1}\n0000000000 65535 f \n'.encode());data.extend(''.join(f'{x:010d} 00000 n \n' for x in offsets).encode())
        data.extend(f'trailer\n<< /Size {len(self.objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode());return bytes(data)

def cases():
    result={}
    def emit(name,feature,content,doc=None,**extra):
        d=doc or Document();result[name]=(d.finish(content),dict(feature=feature,**extra))
    emit('rgb-triptych','DeviceRGB independent channels','0.85 0.1 0.2 rg 24 32 72 176 re f 0.1 0.8 0.25 rg 124 32 72 176 re f 0.15 0.25 0.9 rg 224 32 72 176 re f')
    emit('gray-staircase','DeviceGray levels',''.join(f'{i/4:g} g {20+i*58} 40 48 160 re f\n' for i in range(5)))
    emit('cmyk-corners','DeviceCMYK channel order and chromatic geometry','1 0 0 0 k 25 25 115 80 re f 0 1 0 0 k 180 25 115 80 re f 0 0 1 0 k 25 135 115 80 re f 0 0 0 1 k 180 135 115 80 re f',policy='DeviceCMYK profile/engine differences are not exact RGB parity claims.')
    # All tiny raster samples below are authored here as numbers, never obtained from an image.
    samples=bytes([255,40,20, 25,220,70, 30,65,245, 240,210,30, 190,35,200, 25,210,210])
    for name,feature,entries,data in [
      ('indexed-six-tiles','Indexed lookup and sample order','/Width 3 /Height 2 /BitsPerComponent 8 /ColorSpace [/Indexed /DeviceRGB 5 <ff281419dc461e41f5f0d21ebe23c819d2d2>]',bytes(range(6))),
      ('decode-inverted-gray','Image Decode inversion','/Width 3 /Height 2 /BitsPerComponent 8 /ColorSpace /DeviceGray /Decode [1 0]',bytes([0,60,120,160,220,255])),
      ('rgb-nearest','Magnified RGB image with Interpolate false','/Width 3 /Height 2 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Interpolate false',samples),
      ('rgb-smoothed','Magnified RGB image with Interpolate true','/Width 3 /Height 2 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Interpolate true',samples),
      ('stencil-checks','ImageMask polarity and current nonstroking color','/Width 4 /Height 4 /BitsPerComponent 1 /ImageMask true /Decode [1 0]',bytes([0x90,0x60,0x60,0x90]))]:
        d=Document();n=d.add(stream(data,'/Type /XObject /Subtype /Image '+entries));d.resources=f'/XObject << /Raster {n} 0 R >>'
        emit(name,feature,'0.15 0.3 0.8 rg 20 20 280 200 re f q 0.9 0.2 0.1 rg 264 0 0 180 28 30 cm /Raster Do Q',d)
    emit('inline-rgb-stripes','Inline ASCIIHex RGB samples','q 270 0 0 180 25 30 cm BI /W 3 /H 1 /BPC 8 /CS /RGB /F /AHx ID 20c040d030805040e0> EI Q')
    emit('inline-gray-stripes','Inline Gray samples and BPC','q 270 0 0 180 25 30 cm BI /W 3 /H 1 /BPC 8 /CS /G /F /AHx ID 2060c0> EI Q')
    for name,rule in [('clip-nonzero','W'),('clip-evenodd','W*')]:
        emit(name,'Nested rectangles with '+rule+' clip rule',f'q 30 25 260 190 re 90 70 140 100 re {rule} n 0.1 0.65 0.35 rg 0 0 320 240 re f Q')
    emit('clip-crossed-transforms','Intersecting clips with transformed fill','q 40 30 240 180 re W n 1 0.25 -0.15 1 20 -10 cm 70 10 150 230 re W n 0.15 0.4 0.85 rg 0 0 320 240 re f Q')
    for name,cap in [('dash-round-cap',1),('dash-square-cap',2)]:
        emit(name,'Dashed stroke cap geometry',f'0.15 0.25 0.75 RG 14 w {cap} J [31 17] 8 d 34 70 m 286 170 l S')
    for name,phase in [('zero-length-dash-gap',19),('zero-length-dash-on',3)]:
        emit(name,'Zero-length round cap at '+('off' if phase==19 else 'on')+' dash phase',f'24 w 1 J [13 14] {phase} d 160 120 m 160 120 l S',expectedBlank=phase==19,knownFailure='Dash off-phase currently paints a disc.' if phase==19 else None)
    quadrants='0.8 0.15 0.25 rg 20 30 140 90 re f 0.15 0.75 0.3 rg 160 30 140 90 re f 0.15 0.25 0.85 rg 20 120 140 90 re f 0.9 0.75 0.15 rg 160 120 140 90 re f'
    for angle in (0,90,180,270):
        d=Document();d.page_entries=f'/CropBox [20 30 300 210] /Rotate {angle}';emit(f'crop-rotation-{angle}','Translated CropBox and rotation '+str(angle),quadrants,d)
    for name,matrix in [('form-translated','1 0 0 1 55 45'),('form-reflected','-1 0 0 1 260 45'),('form-skewed','1 0.22 0.3 1 25 25')]:
        d=Document();n=d.add(stream('0.75 0.15 0.65 rg -30 -30 260 200 re f 0.1 0.7 0.75 rg 35 25 95 70 re f','/Type /XObject /Subtype /Form /BBox [0 0 180 120] /Resources << >>'))
        d.resources=f'/XObject << /Shape {n} 0 R >>';emit(name,'Form matrix plus BBox clips content outside its bounds',f'q {matrix} cm /Shape Do Q',d)
    d=Document();d.resources='/ExtGState << /Fade << /ca 0.4 >> >>';emit('alpha-painted-backdrop','Constant alpha over explicit colored background','0.1 0.3 0.8 rg 25 25 270 190 re f /Fade gs 0.9 0.2 0.15 rg 80 55 180 130 re f',d)
    d=Document();d.resources='/ExtGState << /S << /BM /Screen >> /D << /BM /ColorDodge >> >>';emit('blend-empty-backdrop','Unpainted PDF backdrop is transparent before display background','/S gs 0.1 0.2 0.3 rg 30 40 95 160 re f /D gs 0.1 0.2 0.3 rg 195 40 95 160 re f',d,knownFailure='Page display background participates in blend before page compositing.')
    d=Document();d.resources='/ExtGState << /Mix << /BM /Multiply >> >>';emit('multiply-painted-backdrop','Multiply over an explicit RGB backdrop','0.3 0.8 0.6 rg 20 20 280 200 re f /Mix gs 0.8 0.3 0.5 rg 70 60 180 120 re f',d)
    for name,knockout in [('isolated-group',False),('knockout-group',True)]:
        d=Document();n=d.add(stream('/G gs 0.85 0.2 0.15 rg 15 20 125 110 re f 0.1 0.25 0.9 rg 75 45 125 110 re f',f'/Type /XObject /Subtype /Form /BBox [0 0 220 180] /Group << /S /Transparency /I true /K {str(knockout).lower()} >> /Resources << /ExtGState << /G << /ca 0.6 >> >> >>'))
        d.resources=f'/XObject << /Layer {n} 0 R >>';emit(name,'Isolated transparency group, knockout '+str(knockout),'0.25 0.7 0.3 rg 20 20 280 200 re f q 1 0 0 1 45 30 cm /Layer Do Q',d)
    for name,kind,mask in [('luminosity-soft-mask','Luminosity','0.25 g 0 0 160 240 re f 0.75 g 160 0 160 240 re f'),('alpha-soft-mask','Alpha','/Half gs 0 g 0 0 160 240 re f /Full gs 0 g 160 0 160 240 re f')]:
        d=Document();n=d.add(stream(mask,'/Type /XObject /Subtype /Form /BBox [0 0 320 240] /Group << /S /Transparency /CS /DeviceGray >> /Resources << /ExtGState << /Half << /ca 0.25 >> /Full << /ca 0.75 >> >> >>'))
        d.resources=f'/ExtGState << /Mask << /SMask << /S /{kind} /G {n} 0 R >> >> >>';emit(name,kind+' soft mask values','/Mask gs 0.8 0.1 0.3 rg 30 35 260 170 re f',d)
    for name,kind,coords in [('axial-gradient',2,'35 120 285 120'),('radial-gradient',3,'160 120 0 160 120 100')]:
        d=Document();d.resources=f'/Shading << /Shade << /ShadingType {kind} /ColorSpace /DeviceRGB /Coords [{coords}] /Extend [true true] /Function << /FunctionType 2 /Domain [0 1] /C0 [0.9 0.15 0.1] /C1 [0.1 0.25 0.9] /N 1 >> >> >>'
        emit(name,'Analytic Type2 function in '+name,'q 35 25 250 190 re W n /Shade sh Q',d)
    for name,paint,content,paintop in [('colored-pattern',1,'0.2 0.7 0.6 rg 0 0 13 9 re f 0.8 0.2 0.5 rg 13 9 13 9 re f','/Pattern cs /Tiles scn'),('uncolored-pattern',2,'0 0 13 9 re f 13 9 13 9 re f','/TilePaint cs 0.2 0.35 0.8 /Tiles scn')]:
        d=Document();n=d.add(stream(content,f'/Type /Pattern /PatternType 1 /PaintType {paint} /TilingType 1 /BBox [0 0 26 18] /XStep 26 /YStep 18 /Resources << >>'));d.resources=f'/Pattern << /Tiles {n} 0 R >>'+(' /ColorSpace << /TilePaint [/Pattern /DeviceRGB] >>' if paint==2 else '');emit(name,'Tiling pattern PaintType '+str(paint),paintop+' 30 30 260 180 re f',d)
    for name,colored in [('type3-outlined-shapes',False),('type3-colored-shapes',True)]:
        d=Document();prefix='700 0 d0 0.75 0.15 0.5 rg ' if colored else '700 0 0 0 600 800 d1 '
        a=d.add(stream(prefix+'70 80 460 640 re 150 170 300 460 re f*'))
        b=d.add(stream(prefix+'40 60 m 560 60 l 300 740 l h f'))
        f=d.add(f'<< /Type /Font /Subtype /Type3 /FontBBox [0 0 600 800] /FontMatrix [0.001 0 0 0.001 0 0] /CharProcs << /A {a} 0 R /B {b} 0 R >> /Encoding << /Type /Encoding /Differences [65 /A /B] >> /FirstChar 65 /LastChar 66 /Widths [700 700] /Resources << >> >>')
        d.resources=f'/Font << /Shapes {f} 0 R >>';emit(name,'Self-authored Type3 glyph procedures; '+('colored d0' if colored else 'uncolored d1'),'0.1 0.4 0.8 rg BT /Shapes 80 Tf 45 75 Td (ABBA) Tj ET',d,textContains='ABBA')
    for name,flags in [('annotation-visible',4),('annotation-hidden',6)]:
        d=Document();ap=d.add(stream('0.2 0.7 0.35 rg 0 0 80 60 re f 0.8 0.15 0.3 rg 15 15 50 30 re f','/Type /XObject /Subtype /Form /BBox [0 0 80 60] /Resources << >>'))
        ann=d.add(f'<< /Type /Annot /Subtype /Square /Rect [75 55 235 175] /F {flags} /AP << /N {ap} 0 R >> >>');d.page_entries=f'/Annots [{ann} 0 R]';emit(name,'Static annotation appearance and Hidden flag','0.15 0.3 0.8 rg 20 20 25 25 re f',d)
    d=Document();on=d.add(stream('0.25 0.65 0.85 rg 0 0 50 50 re f 0.1 g 8 20 m 20 8 l 43 40 l 36 45 l 19 22 l 13 28 l h f','/Type /XObject /Subtype /Form /BBox [0 0 50 50] /Resources << >>'));off=d.add(stream('0.9 g 0 0 50 50 re f','/Type /XObject /Subtype /Form /BBox [0 0 50 50] /Resources << >>'))
    widget=d.add(f'<< /Type /Annot /Subtype /Widget /FT /Btn /T (novel-choice) /Rect [110 70 210 170] /F 4 /V /On /AS /On /AP << /N << /On {on} 0 R /Off {off} 0 R >> >> >>');d.page_entries=f'/Annots [{widget} 0 R]';d.catalog_entries=f'/AcroForm << /Fields [{widget} 0 R] /NeedAppearances false >>';emit('button-explicit-appearance','Static button field with explicit On appearance','0.15 0.3 0.8 rg 20 20 25 25 re f',d)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args();items=cases();assert len(items)==40,len(items)
    for name,(data,description) in items.items():
        path=ROOT/'pdf'/f'{name}.pdf'
        if args.write:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        elif not path.exists() or path.read_bytes()!=data:raise SystemExit(f'Not reproducible: {path}')
    if args.write:(ROOT/'features.json').write_text(json.dumps({name:detail for name,(_,detail) in items.items()},indent=2)+'\n')
    print(f'{len(items)} independently authored MIT PDFs '+('written' if args.write else 'verified'))

if __name__=='__main__':main()
