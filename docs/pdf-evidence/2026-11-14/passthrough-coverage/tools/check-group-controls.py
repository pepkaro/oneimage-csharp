# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1];out={}
for n in ['group-backdrop-alpha','passthrough-coverage','patterned-stencil-coverage']:
 if not (R/'fixtures'/f'{n}.pdf').exists():continue
 arrays={s:np.asarray(Image.open(R/('renders' if s in ['before','after'] else 'references')/f'{n}-{s}.png').convert('RGB')).astype(float) for s in ['before','after','pdfium','mupdf','pdfjs']}
 point=lambda a,x,y:a[int(256-y*2),int(x*2)].tolist()
 if n=='group-backdrop-alpha':
  bg=np.array([.75,.5,.2]);red=np.array([.8,.15,.3]);green=np.array([.1,.65,.45]);aa=.55;ag=1-(1-aa)**2;cg=(green*aa+red*aa*(1-aa))/ag
  rows=[]
  for col,mode in enumerate(['Normal','Multiply','Screen']):
   for x,y,a,c,label in [(22,40,aa,red,'red only'),(35,70,ag,cg,'overlap'),(50,80,aa,green,'green only')]:
    blend=c if mode=='Normal' else bg*c if mode=='Multiply' else 1-(1-bg)*(1-c)
    exp=(bg*(1-.65*a)+blend*(.65*a))*255
    samples={s:point(im,x+64*col,y) for s,im in arrays.items()}
    rows.append({'mode':mode,'region':label,'pdfPoint':[x+64*col,y],'idealContinuousRGB':exp.tolist(),'observed':samples,'beforeMaxChannelError':float(np.max(np.abs(samples['before']-exp))),'afterMaxChannelError':float(np.max(np.abs(samples['after']-exp)))})
  out[n]={'samples':rows,'maxBeforeError':max(r['beforeMaxChannelError'] for r in rows),'maxAfterError':max(r['afterMaxChannelError'] for r in rows)}
 elif n=='passthrough-coverage':
  out[n]={}
  for s,a in arrays.items():
   d=np.abs(a[:124]-a[124:248]);out[n][s]={'translatedRowsChangedPixels':int(np.any(d,axis=2).sum()),'maxChannelDifference':float(d.max()),'samples':[{'alpha':al,'top':point(a,30+64*i,90),'bottom':point(a,30+64*i,28),'idealContinuousRGB':(((1-al)+al*np.array([.05,.55,.75]))*255).tolist()} for i,al in enumerate([.25,.6,.85])]}
 else:
  out[n]={}
  for s,a in arrays.items():
   d=np.abs(a[:,:192]-a[:,192:]);out[n][s]={'translatedPanelsChangedPixels':int(np.any(d,axis=2).sum()),'maxChannelDifference':float(d.max()),'left':point(a,15,100),'right':point(a,111,100)}
  out[n]['idealContinuousRGB']=(((1-.65*.6)+.65*.6*np.array([.65,.12,.75]))*255).tolist()
print(json.dumps(out,indent=2))
