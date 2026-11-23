// SPDX-License-Identifier: MIT
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const [root,input,output,dpi]=process.argv.slice(2);
if(process.version!=='v24.22.3')throw Error('Node pin mismatch');
const require=createRequire(path.join(root,'package.json')),canvas=require('@napi-rs/canvas');
if(require('@napi-rs/canvas/package.json').version!=='1.1.1')throw Error('Canvas pin mismatch');
globalThis.DOMMatrix=canvas.DOMMatrix;globalThis.ImageData=canvas.ImageData;globalThis.Path2D=canvas.Path2D;
const pdfjs=await import(pathToFileURL(path.join(root,'legacy/build/pdf.mjs')));
if(pdfjs.version!=='6.5.438'||pdfjs.build!=='0a4153349')throw Error('PDF.js pin mismatch');
const load=pdfjs.getDocument({data:new Uint8Array(fs.readFileSync(input)),isEvalSupported:false,useSystemFonts:false,enableXfa:false,useWorkerFetch:false});
const doc=await load.promise;if(doc.numPages!==1)throw Error('Page count mismatch');const page=await doc.getPage(1),viewport=page.getViewport({scale:Number(dpi)/72});
const target=canvas.createCanvas(Math.ceil(viewport.width),Math.ceil(viewport.height));
await page.render({canvas:target,viewport,background:'rgb(255,255,255)',annotationMode:pdfjs.AnnotationMode.DISABLE}).promise;
fs.writeFileSync(output,target.toBuffer('image/png'));
console.log(JSON.stringify({engine:'PDF.js',version:pdfjs.version,build:pdfjs.build,canvas:'1.1.1',node:process.version,width:target.width,height:target.height,dpi:Number(dpi),page:0,background:'white',annotations:'none',page_bounds:'visibleCropBox',rotation:0,user_unit:1,backend:'Node Canvas, not native browser'}));
page.cleanup();await load.destroy();
