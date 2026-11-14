// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Direct Node Canvas control, no PDF interpreter and no upstream test source.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(path.resolve(process.argv[2],'package.json'));
const {createCanvas,Path2D}=require('@napi-rs/canvas');
const results=[];
for(const delta of [0,1]) for(const api of ['Path2D','context']) for(const phase of [null,0,3,19,-3]) {
 const canvas=createCanvas(320,240),ctx=canvas.getContext('2d');
 ctx.fillStyle='white';ctx.fillRect(0,0,320,240);ctx.strokeStyle='black';ctx.lineWidth=24;ctx.lineCap='round';
 if(phase!==null){ctx.setLineDash([13,14]);ctx.lineDashOffset=phase;}
 if(api==='Path2D'){const p=new Path2D();p.moveTo(160,120);p.lineTo(160+delta,120);ctx.stroke(p);}
 else{ctx.beginPath();ctx.moveTo(160,120);ctx.lineTo(160+delta,120);ctx.stroke();}
 const data=ctx.getImageData(0,0,320,240).data;let ink=0;for(let i=0;i<data.length;i+=4)if(data[i]<235||data[i+1]<235||data[i+2]<235)ink++;
 const name=`${api}-${delta}-${phase===null?'solid':phase}.png`;fs.writeFileSync(new URL(name,import.meta.url),canvas.toBuffer('image/png'));
 results.push({api,phase,dash:phase===null?[]:[13,14],lineWidth:24,lineCap:'round',segment:[160,120,160+delta,120],delta,ink,file:name});
}
const report={node:process.version,canvas:require('@napi-rs/canvas/package.json').version,pdfInterpreter:'None',results};
fs.writeFileSync(new URL('report.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
