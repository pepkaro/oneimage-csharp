# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Eight independent ordinary image contracts; no input file/font/image is read."""
from pathlib import Path
import json,hashlib,zlib
R=Path(__file__).resolve().parent
OUT=R/"inputs";OUT.mkdir(exist_ok=True)
def stream(data,entries=""):
 return f"<< {entries} /Length {len(data)} >>\nstream\n".encode()+data+b"\nendstream"
def pdf(image,content):
 objs=[b"<< /Type /Catalog /Pages 2 0 R >>",b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 180] /CropBox [0 0 240 180] /Rotate 0 /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>",stream(content.encode()),image]
 p=bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n");offset=[]
 for i,o in enumerate(objs,1):offset.append(len(p));p.extend(f"{i} 0 obj\n".encode()+o+b"\nendobj\n")
 pos=len(p);p.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode())
 for n in offset:p.extend(f"{n:010d} 00000 n \n".encode())
 p.extend(f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n".encode());return bytes(p)
def packed(rows,bpc,components=1):
 data=bytearray()
 for row in rows:
  bits="".join(f"{v:0{bpc}b}" for v in row);bits+="0"*((-len(bits))%8)
  data.extend(int(bits[i:i+8],2) for i in range(0,len(bits),8))
 return bytes(data)
SPEC={'img-gray2-packed-padding': ['8.9.3 Sample Representation', '8.9.5.1 Image Dictionaries, Table 89'], 'img-gray4-inverted-decode': ['8.9.3 Sample Representation', '8.9.5.2 Decode Arrays'], 'img-gray8-restricted-decode': ['8.9.5.2 Decode Arrays, Table 90'], 'img-rgb8-channel-decode': ['8.9.3 Sample Representation', '8.9.5.2 Decode Arrays'], 'img-indexed2-lookup-padding': ['8.6.6.3 Indexed Colour Spaces', '8.9.3 Sample Representation', '8.9.5.2 Table 90 default Indexed Decode'], 'img-indexed4-reversed-decode': ['8.6.6.3 Indexed Colour Spaces', '8.9.5.2 Decode Arrays'], 'img-rgb16-big-endian': ['8.9.3 Sample Representation, 16-bit byte ordering', '8.9.5.1 Image Dictionaries, Table 89'], 'img-rgb8-mirrored-placement': ['8.9.4 Image Coordinate System', '8.9.5.3 Image Interpolation']}
cases=[]
def add(id,contract,bpc,cs,rows,rgb,decode=None,mirror=False):
 h=len(rows);w=len(rgb[0]);raw=packed(rows,bpc)
 assert len(raw)==h*((w*(3 if cs=="/DeviceRGB" else 1)*bpc+7)//8)
 data=zlib.compress(raw,9)
 entries=f"/Type /XObject /Subtype /Image /Width {w} /Height {h} /BitsPerComponent {bpc} /ColorSpace {cs} /Filter /FlateDecode /Interpolate false"
 if decode:entries+=" /Decode ["+" ".join(map(str,decode))+"]"
 ix,iy=32,40;iw,ih=w*24,h*24
 content=f"q {'-'+str(iw) if mirror else iw} 0 0 {ih} {ix+iw if mirror else ix} {iy} cm /Im Do Q\n"
 p=pdf(stream(data,entries),content);f=OUT/(id+".pdf");f.write_bytes(p)
 samples=[]
 for y,row in enumerate(rgb):
  for x,c in enumerate(row):
   posx=ix+(w-x-.5 if mirror else x+.5)*24;posy=iy+(h-y-.5)*24
   samples.append(dict(id=f"cell-{x}-{y}",point=[posx,posy],rgb=list(c),tolerance=0))
 samples.extend([dict(id="paper",point=[12,12],rgb=[255,255,255],tolerance=0)])
 regions=[dict(id=s["id"],rect=([4,4,16,16] if s["id"]=="paper" else [s["point"][0]-10,s["point"][1]-10,20,20]),rgb=s["rgb"],tolerance=0) for s in samples]
 cases.append(dict(id=id,file="inputs/"+f.name,license="MIT",contract=contract,spec="ISO 32000-1:2008",spec_clauses=SPEC[id],route="page image XObject /FlateDecode /Interpolate false",width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations="none",background=[255,255,255],image=dict(width=w,height=h,bpc=bpc,color_space=cs,decode=decode,ctm=[-iw if mirror else iw,0,0,ih,ix+iw if mirror else ix,iy],raw_sha256=hashlib.sha256(raw).hexdigest()),sha256=hashlib.sha256(p).hexdigest(),expected_samples=samples,expected_regions=regions,region_rule="Each authored24-point cell is inset2PDFpoints on all sides; outer/cell boundary bands are unscored. Paper uses a separate16-point rectangle.",association=dict(scope="standard-contract-only",upstream_id=None,upstream_entry_validated=False,reason="No reviewed metadata-only scene capsule establishes a full matching upstream contract.")))
gray2=[[0,1,2,3,1],[3,2,0,1,2]]
add("img-gray2-packed-padding","Two-bit DeviceGray samples are MSB-first and each five-sample row starts at a new byte.",2,"/DeviceGray",gray2,[[[v*85]*3 for v in row] for row in gray2])
gray4=[[0,2,5,7,10,13,15],[15,12,9,6,3,1,0]]
add("img-gray4-inverted-decode","Four-bit DeviceGray Decode [1 0] reverses tone after unpacking, with independent row padding.",4,"/DeviceGray",gray4,[[[(15-v)*17]*3 for v in row] for row in gray4],[1,0])
gray8=[[0,85,170,255],[255,170,85,0]]
add("img-gray8-restricted-decode","DeviceGray Decode [0.2 0.8] maps encoded endpoints and exact thirds into the restricted component range.",8,"/DeviceGray",gray8,[[[51+v*3//5]*3 for v in row] for row in gray8],[0.2,0.8])
rgb8=[[[17,51,204],[240,136,68],[0,255,119]],[[255,0,0],[0,0,255],[85,170,34]]]
add("img-rgb8-channel-decode","RGB Decode independently reverses red/blue while preserving green; samples stay interleaved RGB.",8,"/DeviceRGB",[[v for c in row for v in c] for row in rgb8],[[[255-c[0],c[1],255-c[2]] for c in row] for row in rgb8],[1,0,0,1,1,0])
palette=[[13,67,211],[251,137,29],[47,229,113],[173,31,191]]
lookup="".join(bytes(c).hex() for c in palette)
idx2=[[0,3,1,2,3],[2,1,0,3,1],[1,0,2,1,3]]
add("img-indexed2-lookup-padding","Two-bit indices select a nonmonotone RGB lookup directly; five-index scanlines have independent padding.",2,f"[/Indexed /DeviceRGB 3 <{lookup}>]",idx2,[[palette[v] for v in row] for row in idx2])
idx4=[[0,5,10,15],[15,10,5,0]]
add("img-indexed4-reversed-decode","Indexed four-bit Decode [3 0] maps four exact encoded values to palette indices 3,2,1,0 before lookup.",4,f"[/Indexed /DeviceRGB 3 <{lookup}>]",idx4,[[palette[3-v//5] for v in row] for row in idx4],[3,0])
rgb16=[[[1,128,240],[17,204,51],[255,0,170]],[[34,85,136],[221,68,187],[0,255,255]]]
add("img-rgb16-big-endian","Sixteen-bit RGB components use big-endian bytes; replicated-byte samples normalize exactly to their eight-bit values.",16,"/DeviceRGB",[[v*257 for c in row for v in c] for row in rgb16],rgb16)
mirror=[[[221,17,85],[51,187,238]],[[119,255,34],[170,68,204]]]
add("img-rgb8-mirrored-placement","A negative-x image CTM mirrors columns once while retaining top-to-bottom source row orientation.",8,"/DeviceRGB",[[v for c in row for v in c] for row in mirror],mirror,mirror=True)
(R/"manifest.json").write_text(json.dumps(dict(schema_version=1,batch="ordinary-image-contracts-01",purpose="Original standard-contract coverage; zero upstream input executions or full entry matches.",fixture_count=len(cases),cases=cases),indent=2)+"\n")
print(json.dumps(dict(unique_pdfs=len({c["sha256"] for c in cases}),ids=[c["id"] for c in cases]),indent=2))
