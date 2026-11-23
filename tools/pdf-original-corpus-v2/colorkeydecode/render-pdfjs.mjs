// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Our adapter only. Install the official PDF.js runtime outside this repository.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const [runtimeRoot, input, output, dpiText = '72', mode = 'view'] = process.argv.slice(2);
if (!runtimeRoot || !input || !output) throw new Error('Usage: render-pdfjs.mjs /external/node_modules/pdfjs-dist input.pdf output.png [dpi]');
const require = createRequire(path.join(runtimeRoot, 'package.json'));
const canvas = require('@napi-rs/canvas');
globalThis.DOMMatrix = canvas.DOMMatrix;
globalThis.ImageData = canvas.ImageData;
globalThis.Path2D = canvas.Path2D;
const diagnostics = [];
const outputLog = console.log.bind(console);
console.log = (...items) => { const text = items.map(String).join(' '); diagnostics.push(text); console.error(text); };
console.warn = console.log;
const pdfjs = await import(pathToFileURL(path.join(runtimeRoot, 'legacy/build/pdf.mjs')));
if (pdfjs.version !== '6.5.438' || pdfjs.build !== '0a4153349' || require('@napi-rs/canvas/package.json').version !== '1.1.1' || process.version !== 'v24.22.3') throw new Error('Reference PDF.js/build/Canvas/Node pin mismatch');
const bytes = fs.readFileSync(input);
if (bytes.length > 1_048_576) throw new Error('Fixture exceeds the 1 MiB reference bound');
const loading = pdfjs.getDocument({
  data: new Uint8Array(bytes), isEvalSupported: false, useSystemFonts: false,
  enableXfa: false, useWorkerFetch: false,
  standardFontDataUrl: path.join(runtimeRoot, 'standard_fonts') + path.sep,
  cMapUrl: path.join(runtimeRoot, 'cmaps') + path.sep, cMapPacked: true,
  wasmUrl: path.join(runtimeRoot, 'wasm') + path.sep,
});
const document = await loading.promise;
if (document.numPages !== 1) throw new Error('This initial corpus expects one page per PDF');
const page = await document.getPage(1);
const viewport = page.getViewport({ scale: Number(dpiText) / 72 });
if (viewport.width * viewport.height > 512 * 512) throw new Error('Reference page exceeds pixel bound');
const target = canvas.createCanvas(Math.ceil(viewport.width), Math.ceil(viewport.height));
await page.render({ canvas: target, viewport, background: 'rgb(255,255,255)', annotationMode: mode === "none" ? pdfjs.AnnotationMode.DISABLE : pdfjs.AnnotationMode.ENABLE }).promise;
fs.writeFileSync(output, target.toBuffer('image/png'));
outputLog(JSON.stringify({ pdfjs: pdfjs.version, build: pdfjs.build, backend: '@napi-rs/canvas (Node Canvas; NOT browser Canvas)', canvasVersion: require('@napi-rs/canvas/package.json').version, node: process.version, width: target.width, height: target.height, dpi: Number(dpiText), annotations: mode === 'none' ? 'DISABLE' : 'ENABLE static appearances', background: 'rgb(255,255,255)', useSystemFonts: false, isEvalSupported: false, xfa: false, useWorkerFetch: false, icc: false, iccReason: 'PDF.js Node worker-fetch gate disables ICC WASM; ICC-based inputs would fall back', deviceCmyk: 'Polynomial fallback, not ICC-managed CMYK', diagnostics }));
page.cleanup();
await loading.destroy();
