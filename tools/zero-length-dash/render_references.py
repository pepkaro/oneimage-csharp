# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Reference runtimes are external dependencies, not copied test assets.
import argparse
import hashlib
import json
from pathlib import Path
import platform
import pypdfium2 as pdfium
import pymupdf
import PIL
from PIL import Image

parser = argparse.ArgumentParser(description='Render the original zero-length dash controls with pinned references.')
parser.add_argument('inputs', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
versions = {'pypdfium2': str(pdfium.PYPDFIUM_INFO.version), 'pdfium': str(pdfium.PDFIUM_INFO.version),
            'PyMuPDF': pymupdf.VersionBind, 'MuPDF': pymupdf.VersionFitz, 'Pillow': PIL.__version__,
            'python': platform.python_version()}
assert versions['pypdfium2'] == '5.13.0', versions
assert versions['pdfium'] == '153.0.7999.0', versions
assert versions['PyMuPDF'] == '1.26.6' and versions['MuPDF'] == '1.26.11', versions
assert versions['Pillow'] == '13.0.0', versions
for engine in ('pdfium', 'mupdf'):
    (args.output / engine).mkdir(parents=True, exist_ok=True)
records = []
for case in json.loads((args.inputs / 'cases.json').read_text()):
    data = (args.inputs / 'pdf' / (case['name'] + '.pdf')).read_bytes()
    assert hashlib.sha256(data).hexdigest() == case['input_sha256']
    with pdfium.PdfDocument(data) as doc:
        image = doc[0].render(scale=2, rotation=0, fill_color=(255, 255, 255, 255), draw_annots=False).to_pil().convert('RGB')
        image.save(args.output / 'pdfium' / (case['name'] + '.png'))
    with pymupdf.open(stream=data, filetype='pdf') as doc:
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False, annots=False)
        Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(args.output / 'mupdf' / (case['name'] + '.png'))
    row = {'case': case['name'], 'input_sha256': case['input_sha256']}
    for engine in ('pdfium', 'mupdf'):
        output = args.output / engine / (case['name'] + '.png')
        image = Image.open(output)
        assert image.size == (384, 288)
        pixels = list(image.get_flattened_data())
        row[engine] = {'png_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                       'ink_pixels': sum(min(p) < 255 for p in pixels),
                       'black_area_square_points': sum(255 - p[0] for p in pixels) / (255 * 4)}
    records.append(row)
(args.output / 'reference-results.json').write_text(json.dumps({'versions': versions,
    'settings': {'dpi': 144, 'box': 'CropBox = MediaBox [0 0 192 144]', 'rotation': 0,
                 'background': 'opaque white', 'annotations': False, 'image_edits': 'none'},
    'results': records}, indent=2) + '\n')
print(f'Rendered {len(records)} cases with each pinned reference.')
