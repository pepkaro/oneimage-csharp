# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
import hashlib
import html
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).parent
cases = json.loads((root / 'repro-inputs/cases.json').read_text())
records = []
gallery = ['<!doctype html><meta charset="utf-8"><title>Zero-length dash cap evidence</title>',
           '<style>body{font:16px sans-serif}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #aaa}img{display:block}</style>',
           '<h1>Zero-length dash cap: full-page evidence</h1>',
           '<p>All panels are raw 384×288 PNGs at 144 DPI, opaque white, full matching CropBox, rotation 0. ',
           'No scaling, alignment, cropping or retouching. Captions are outside images. ',
           'Reference disagreement is recorded, not treated as a vote. See ANALYSIS.md.</p>']
engines = {'before': 'before', 'head': 'head', 'PDFium': 'repro-references/pdfium', 'MuPDF': 'repro-references/mupdf'}
for case in cases:
    name = case['name']
    row = {'case': name, 'input_sha256': case['input_sha256']}
    pixels = {}
    gallery.append('<h2>' + html.escape(name) + '</h2><p>' + html.escape(case['content']) + '</p><table><tr>')
    for engine in engines:
        gallery.append('<th>' + engine + '</th>')
    gallery.append('</tr><tr>')
    for engine, directory in engines.items():
        path = root / directory / (name + '.png')
        image = Image.open(path).convert('RGB')
        assert image.size == (384, 288), (path, image.size)
        data = image.tobytes()
        pixels[engine] = data
        row[engine] = {'png_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'rgb_sha256': hashlib.sha256(data).hexdigest(),
                       'ink_pixels': sum(min(data[i:i+3]) < 255 for i in range(0, len(data), 3)),
                       'black_area_square_points': sum(255 - r for r in data[::3]) / (255 * 4)}
        gallery.append('<td><img width="384" height="288" src="' + directory + '/' + name + '.png" alt="' +
                       html.escape(engine + ' ' + name) + '"></td>')
    gallery.append('</tr></table>')
    row['before_head_changed_pixels'] = sum(pixels['before'][i:i+3] != pixels['head'][i:i+3] for i in range(0, len(pixels['head']), 3))
    for candidate in ('before', 'head'):
        for reference in ('PDFium', 'MuPDF'):
            row[candidate + '_vs_' + reference] = {'mae_rgb_levels': sum(abs(a-b) for a,b in zip(pixels[candidate], pixels[reference])) / len(pixels[candidate]),
                'different_pixels': sum(pixels[candidate][i:i+3] != pixels[reference][i:i+3] for i in range(0, len(pixels[candidate]), 3))}
    records.append(row)
by_name = {row['case']: row for row in records}
# Independently classified OFF intervals, spelled out rather than inferred from either engine's pixels.
expected_changed = {
    'even-11', 'even-11.001', 'even-19', 'even-27.999', 'even-39',
    'odd-7', 'odd-21', 'odd-23', 'odd-33', 'odd-41', 'odd-49',
    'zero-0_17_1', 'zero-0_17_11', 'zero-0_17_28',
    'zero-0_0_11_17_11', 'zero-0_0_11_17_17', 'zero-11_0_0_17_17',
    'zero-0_0_0_17_1', 'zero-0_0_0_17_11', 'zero-0_0_0_17_28',
    'zero-0_17_0_1', 'zero-0_17_0_11',
    'close-19', 'closedline-19', 'curve-19', 'rectangle-19',
    'transform-19', 'hairline-19', 'transformed-hairline-19', 'reset-19',
    'odd-doubled-21', 'odd-doubled-23', 'odd-doubled-33', 'odd-doubled-41',
}
assert {r['case'] for r in records if r['before_head_changed_pixels']} == expected_changed
for name in expected_changed - {'reset-19'}:
    assert by_name[name]['head']['ink_pixels'] == 0, name
assert by_name['even-19']['before']['ink_pixels'] > 0
assert by_name['even-19']['head']['ink_pixels'] == 0
assert by_name['even-19']['PDFium']['ink_pixels'] == 0
assert by_name['even-19']['MuPDF']['ink_pixels'] == 0
for name in ('solid', 'even-3', 'tiny-3', 'tiny-19', 'ordinary-3', 'ordinary-19', 'zero-interior-tiny', 'gap-near-end-tiny'):
    assert by_name[name]['before_head_changed_pixels'] == 0, name
(root / 'image-metrics.json').write_text(json.dumps(records, indent=2) + '\n')
(root / 'gallery.html').write_text('\n'.join(gallery) + '\n')
print(json.dumps({'cases': len(records), 'changed': sum(r['before_head_changed_pixels'] != 0 for r in records),
                  'main_defect': by_name['even-19'], 'on_control': by_name['even-3']}, indent=2))
