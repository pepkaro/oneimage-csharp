# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original numeric controls, reusing only our original MIT PDF writer.
import argparse, hashlib, json, runpy
from pathlib import Path
writer=runpy.run_path(str(Path(__file__).resolve().parent.parent/'closed-dashes/generate.py'))['document']
shapes={
 'tiny':('48 36 m 48.125 36 l h','48 36 m 48.125 36 l 48 36 l'),
 'cubic':('48 36 m 49 36 47 36 48 36 c h','48 36 m 49 36 47 36 48 36 c'),
 'rectangle':('24 24 8 6 re','24 24 m 32 24 l 32 30 l 24 30 l 24 24 l'),
 'triangle':('22 24 m 35 25 l 29 37 l h','22 24 m 35 25 l 29 37 l 22 24 l'),
 'repeated-return':('48 36 m 48.125 36 l 48 36 l 48 36 l h','48 36 m 48.125 36 l 48 36 l 48 36 l')}
items=[]
def pair(name,closed,open,style):
 for label,path in [('closed',closed),('open',open)]:
  items.append(dict(name=name+'-'+label,content=style+' '+path+' S',equivalent_pair=name))
for name,(closed,open) in shapes.items():
 for cap in (0,1,2):pair(f'{name}-cap{cap}',closed,open,f'0 G 18 w {cap} J [200 17] 3 d')
for label,dash in [('crossing','[12 7] 3 d'),('odd','[7 5 9] 12 d'),('zero','[0 7] 0 d'),('zero-gap','[12 0] 0 d'),('initial-gap','[60 20] 65 d')]:
 pair(label,*shapes['rectangle'],'0 G 4 w 1 J '+dash)
for label,matrix,width in [('plain','',18),('skew','1.5 .3 .25 .8 -33 -7.2 cm',18),('reflect','-1 0 0 1 96 0 cm',18),('hairline','',0),('skew-hairline','1.5 .3 .25 .8 -33 -7.2 cm',0),('minimum','',.01)]:
 pair(label,*shapes['rectangle'],f'0 G {matrix} {width} w 1 J [200 17] 3 d')
for label,closed,open in [('after-close-line','24 24 8 6 re 50 20 l','24 24 m 32 24 l 32 30 l 24 30 l 24 24 l 24 24 m 50 20 l'),('after-close-move','24 24 8 6 re 60 30 m 80 40 l','24 24 m 32 24 l 32 30 l 24 30 l 24 24 l 60 30 m 80 40 l'),('next-rectangle','24 24 8 6 re 40 40 8 6 re','24 24 m 32 24 l 32 30 l 24 30 l 24 24 l 40 40 m 48 40 l 48 46 l 40 46 l 40 40 l')]:
 pair(label,closed,open,'0 G 4 w 1 J [12 7] 3 d')
for label,dash in [('solid','[] 0 d'),('all-zero','[0 0] 0 d'),('tiny-pattern','[.00001 .00001] 0 d')]:
 items.append(dict(name='fallback-'+label,content=f'0 G 4 w 1 J {dash} 24 24 8 6 re S',equivalent_pair='normalized-solid-fallback'))
parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);root=parser.parse_args().output;(root/'pdf').mkdir(parents=True,exist_ok=True)
for item in items:
 data=writer(item['content']);(root/'pdf'/(item['name']+'.pdf')).write_bytes(data);item['input_sha256']=hashlib.sha256(data).hexdigest()
(root/'cases.json').write_text(json.dumps(items,indent=2)+'\n')
(root/'inputs.txt').write_text(''.join(str((root/'pdf'/(c['name']+'.pdf')).resolve())+'\t'+c['name']+'\n' for c in items))
print(f'Generated {len(items)} original MIT seam controls.')
