// SPDX-License-Identifier: MIT
// Original direct Canvas controls. No PDF is read or constructed.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const [runtimeRoot,out] = process.argv.slice(2);
const require=createRequire(path.join(runtimeRoot,'package.json'));
const canvas=require('@napi-rs/canvas');
if(require('@napi-rs/canvas/package.json').version!=='1.1.1'||process.version!=='v24.22.3')throw Error('Canvas/Node pin mismatch');
fs.mkdirSync(out,{recursive:true});let records=[];
for(const alpha of [0.25,0.6])for(const kind of ['fill','stroke'])for(const dpi of [72,144]){
 const s=dpi/72,c=canvas.createCanvas(80*s,60*s),ctx=c.getContext('2d');ctx.scale(s,s);ctx.fillStyle='white';ctx.fillRect(0,0,80,60);ctx.globalAlpha=alpha;
 if(kind==='fill'){ctx.fillStyle='rgb(255,0,0)';ctx.fillRect(10,10,60,40);}else{ctx.strokeStyle='rgb(0,0,255)';ctx.lineWidth=20;ctx.beginPath();ctx.moveTo(10,30);ctx.lineTo(70,30);ctx.stroke();}
 const actual=Array.from(ctx.getImageData(40*s,30*s,1,1).data);const file=`canvas-${kind}-${alpha}-${dpi}.png`;fs.writeFileSync(path.join(out,file),c.toBuffer('image/png'));records.push({alpha,kind,dpi,actual,file,scope:'direct backend control; not a PDF golden or upstream case'});
}
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({runtime:process.version,canvas:'1.1.1',pdf_used:false,records},null,2)+'\n');
