#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
"""Offline maintainer audit of our original PDFs. Never rewrites expected values.
Install the pinned reference tools OUTSIDE the repository; see the corpus README.
Each engine is run in a fresh child with a timeout. No actions/events are executed.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'tests/testdata/pdf-novel-mit'
ENGINES = ('mupdf', 'pdfium', 'pdfjs')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def worker(engine, source, target):
    if source.stat().st_size > 1 << 20:
        raise ValueError('Input exceeds 1 MiB')
    if engine == 'mupdf':
        import fitz
        assert fitz.VersionBind == '1.26.6' and fitz.VersionFitz == '1.26.11'
        with fitz.open(source) as doc:
            assert len(doc) == 1 and doc[0].rect.width * doc[0].rect.height <= 512 * 512
            doc[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False, annots=True).save(target)
        print(json.dumps(dict(engine=fitz.VersionFitz, wrapper=fitz.VersionBind,
                             dpi=72, annotations=True, alpha=False)))
    elif engine == 'pdfium':
        import pypdfium2 as pdfium
        assert str(pdfium.PYPDFIUM_INFO) == '5.13.0' and str(pdfium.PDFIUM_INFO) == '153.0.7999.0'
        with pdfium.PdfDocument(source) as doc:
            assert len(doc) == 1
            # Static widget appearances require a form environment. XFA is disabled;
            # no JS platform is supplied and no page/document actions are dispatched.
            doc.init_forms(config=pdfium.raw.FPDF_FORMFILLINFO(version=2, xfa_disabled=True))
            page = doc[0]
            try:
                width, height = page.get_size()
                assert width * height <= 512 * 512
                bitmap = page.render(scale=1, draw_annots=True)
                try:
                    bitmap.to_pil().convert('RGB').save(target)
                finally:
                    bitmap.close()
            finally:
                page.close()
        print(json.dumps(dict(engine=str(pdfium.PDFIUM_INFO), wrapper=str(pdfium.PYPDFIUM_INFO),
                             dpi=72, annotations=True, forms='static appearances', xfa=False)))
    else:
        raise ValueError(engine)


def check_pixels(path, expected):
    from PIL import Image
    image = Image.open(path).convert('RGB')
    failures = []
    if image.size != (expected['renderWidth'], expected['renderHeight']):
        return ['wrong dimensions: ' + str(image.size)]
    for probe in expected['probes']:
        actual = image.getpixel((probe['x'], probe['y']))
        if any(abs(a-b) > probe['tolerance'] for a, b in zip(actual, probe['rgb'])):
            failures.append(dict(probe=probe, actual=actual))
    for check in expected.get('channelChecks', []):
        actual = image.getpixel((check['x'], check['y']))
        if any(not lo <= a <= hi for a, (lo, hi) in zip(actual, check['ranges'])):
            failures.append(dict(channelCheck=check, actual=actual))
    ink = 0
    outside = 0
    x0, y0, x1, y1 = expected['inkBounds']
    for y in range(image.height):
        for x in range(image.width):
            if min(image.getpixel((x, y))) < 235:
                ink += 1
                outside += not (x0 <= x <= x1 and y0 <= y <= y1)
    if not expected['inkMin'] <= ink <= expected['inkMax']:
        failures.append(dict(ink=ink, allowed=[expected['inkMin'], expected['inkMax']]))
    if outside:
        failures.append(dict(inkOutsideBounds=outside))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdfjs-runtime', type=Path, help='External node_modules/pdfjs-dist directory')
    parser.add_argument('--output', type=Path, help='New output directory outside this checkout')
    parser.add_argument('--worker', choices=('mupdf', 'pdfium'), help=argparse.SUPPRESS)
    parser.add_argument('--input', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--png', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.input, args.png)
        return
    if not args.output or not args.pdfjs_runtime:
        parser.error('--output and --pdfjs-runtime are required')
    output, runtime = args.output.resolve(), args.pdfjs_runtime.resolve()
    if output.is_relative_to(ROOT) or runtime.is_relative_to(ROOT):
        parser.error('Reference runtimes and output must remain outside the checkout')
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((DATA / 'manifest.json').read_text())
    package = json.loads((runtime / 'package.json').read_text())
    assert package['version'] == '6.5.438'
    assert sha(ROOT / manifest['generator']) == manifest['generatorSha256']
    rows = []
    for fixture in manifest['fixtures']:
        source = DATA / fixture['file']
        assert fixture['license'] == 'MIT' and sha(source) == fixture['sha256']
        for engine in ENGINES:
            target = output / (fixture['id'] + '-' + engine + '.png')
            row = dict(id=fixture['id'], engine=engine, inputSha256=fixture['sha256'], attempted=True, rendered=False)
            command = (['node', str(Path(__file__).with_name('render-pdfjs.mjs')), str(runtime), str(source), str(target), '72']
                       if engine == 'pdfjs' else [sys.executable, str(Path(__file__)), '--worker', engine, '--input', str(source), '--png', str(target)])
            try:
                process = subprocess.run(command, capture_output=True, text=True, timeout=20)
                if process.returncode:
                    raise RuntimeError(process.stderr[-4000:])
                row['settings'] = json.loads(process.stdout.strip().splitlines()[-1])
                if engine == 'pdfjs':
                    assert row['settings']['pdfjs'] == '6.5.438' and row['settings']['canvasVersion'] == '1.1.1'
                row['outputSha256'] = sha(target)
                row['rendered'] = True
                row['failures'] = check_pixels(target, fixture['pages'][0])
                row['status'] = 'fail' if row['failures'] else 'pass'
                if (fixture['id'] == 'zero-length-dash-on' and engine == 'pdfjs' and row['failures']
                        and all(f.get('actual') in (None, (255, 255, 255)) and 'inkOutsideBounds' not in f for f in row['failures'])
                        and any(f.get('ink') == 0 for f in row['failures'])):
                    row['status'] = 'known-reference-disagreement'
                    row['reason'] = 'Node Canvas backend omits the on-phase zero-length round cap; browser behavior not established.'
            except (subprocess.TimeoutExpired, RuntimeError, AssertionError, OSError) as error:
                row.update(status='error', error=str(error))
            rows.append(row)
            print(f"{fixture['id']}: {engine}: {row['status']}", flush=True)
    counts = {status: sum(r['status'] == status for r in rows)
              for status in ('pass', 'fail', 'known-reference-disagreement', 'error')}
    report = dict(schemaVersion=1, inputs=len(manifest['fixtures']), engineExecutionsAttempted=len(rows), actualRenders=sum(r['rendered'] for r in rows),
                  pixelPolicy='Manifest semantic/interior assertions, not byte equality or blanket cross-engine parity',
                  counts=counts, results=rows)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(counts))
    if counts['fail'] or counts['error']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
