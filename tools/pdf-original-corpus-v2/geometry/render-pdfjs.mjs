// SPDX-License-Identifier: MIT
import fs from "node:fs";
import path from "node:path";
import {pathToFileURL} from "node:url";
import {createRequire} from "node:module";
const [runtimeRoot,input,output,dpiText]=process.argv.slice(2);
const require=createRequire(path.join(runtimeRoot,"package.json"));
const canvas=require("@napi-rs/canvas");
if(require("@napi-rs/canvas/package.json").version!=="1.1.1")throw Error("Canvas version pin mismatch");
globalThis.DOMMatrix=canvas.DOMMatrix;globalThis.ImageData=canvas.ImageData;globalThis.Path2D=canvas.Path2D;
const pdfjs=await import(pathToFileURL(path.join(runtimeRoot,"legacy/build/pdf.mjs")));
if(pdfjs.version!=="6.5.438"||pdfjs.build!=="0a4153349")throw Error("PDF.js version pin mismatch");
const load=pdfjs.getDocument({data:new Uint8Array(fs.readFileSync(input)),isEvalSupported:false,useSystemFonts:false,enableXfa:false,useWorkerFetch:false,standardFontDataUrl:path.join(runtimeRoot,"standard_fonts")+path.sep,cMapUrl:path.join(runtimeRoot,"cmaps")+path.sep,cMapPacked:true,wasmUrl:path.join(runtimeRoot,"wasm")+path.sep});
const doc=await load.promise;if(doc.numPages!==1)throw Error("Original fixture page count changed");
const page=await doc.getPage(1);const viewport=page.getViewport({scale:Number(dpiText)/72});const target=canvas.createCanvas(Math.ceil(viewport.width),Math.ceil(viewport.height));
await page.render({canvas:target,viewport,background:"rgb(255,255,255)",annotationMode:pdfjs.AnnotationMode.DISABLE}).promise;
fs.writeFileSync(output,target.toBuffer("image/png"));
console.log(JSON.stringify({engine:"PDF.js",version:pdfjs.version,build:pdfjs.build,canvas:"@napi-rs/canvas1.1.1",runtime:process.version,backend:"Node Canvas, not native browser",width:target.width,height:target.height,dpi:Number(dpiText),page:0,annotations:"none",background:"white",rotation:"page-declared",systemFonts:false,xfa:false,eval:false}));
page.cleanup();await load.destroy();
