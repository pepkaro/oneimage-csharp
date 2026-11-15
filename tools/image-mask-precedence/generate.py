# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
"""Original numerical PDFs and analytic expectations; no external assets.
Regeneration requires Python 3 and Pillow with OpenJPEG support for two JPX cases.
The tests consume committed PDFs, so these are not test/runtime dependencies.
"""
import hashlib
import io
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'testdata/pdf/image-mask-precedence'
B = [51, 102, 153]
C = [230, 52, 76]


def stream(entries, data):
    if isinstance(data, str):
        data = data.encode('ascii')
    return f'<< {entries} /Length {len(data)} >>\nstream\n'.encode() + data + b'\nendstream'


def pdf(objects):
    out = bytearray(b'%PDF-1.7\n% Original MIT numerical mask precedence regression\n')
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        if isinstance(obj, str):
            obj = obj.encode('ascii')
        out += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
    offset = len(out)
    out += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    out += b''.join(f'{p:010} 00000 n \n'.encode() for p in offsets[1:])
    out += f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{offset}\n%%EOF\n'.encode()
    return out


def blend(mode, b, c):
    return b * c / 255 if mode == 'Multiply' else b + c - b * c / 255 if mode == 'Screen' else c


def color(alpha, mode='Normal'):
    return [b + alpha * (blend(mode, b, c) - b) for b, c in zip(B, C)]


def make(name, kind, state=0, ca=.5, mode='Normal', clipped=False):
    # Four 40-point image bands. No antialiasing boundary enters an asserted region.
    mask = [0, 64, 128, 255] if kind in ('smask', 'smask-key', 'jpx', 'jpx-ignored') else [255] * 4
    source = bytes(C * 4)
    extra = ''
    bpc = 8
    space = '/ColorSpace /DeviceRGB'
    mask_entries = '/ColorSpace /DeviceGray /BitsPerComponent 8'
    mask_data = bytes(mask)
    overrides = kind not in ('plain', 'stencil', 'jpx-ignored')
    if kind == 'opaque-smask':
        extra = '/SMask 6 0 R'
    elif kind in ('smask', 'smask-key'):
        extra = '/SMask 6 0 R'
        if kind == 'smask-key':
            extra += ' /Mask [230 230 52 52 76 76]'
    elif kind == 'explicit':
        extra = '/Mask 6 0 R'
        mask_entries = '/ImageMask true /BitsPerComponent 1'
        mask_data = bytes([0x50])
        mask = [255, 0, 255, 0]
    elif kind == 'key':
        extra = '/Mask [230 230 52 52 76 76]'
        source = bytes([230, 52, 76, 230, 52, 77] * 2)
        mask = [0, 255, 0, 255]
    elif kind == 'stencil':
        extra = '/ImageMask true'
        space = ''
        bpc = 1
        source = bytes([0x50])
        mask = [255, 0, 255, 0]
    elif kind in ('jpx', 'jpx-ignored'):
        im = Image.new('RGBA', (4, 1))
        im.putdata([tuple(C + [v]) for v in mask])
        encoded = io.BytesIO()
        im.save(encoded, format='JPEG2000', irreversible=False, num_resolutions=1)
        source = encoded.getvalue()
        extra = '/Filter /JPXDecode /SMaskInData ' + ('1' if kind == 'jpx' else '0')
        if kind == 'jpx-ignored':
            mask = [255] * 4
    state_entry = '' if state is None else '/SMask << /S /Luminosity /G 7 0 R >>'
    resources = f'/XObject << /Main 5 0 R /Plain 8 0 R >> /ExtGState << /M << {state_entry} >> /A << /ca {ca} /BM /{mode} >> >>'
    clip = '32 40 128 80 re W n ' if clipped else ''
    # Both following objects use the same persistent state, without a gs reset.
    content = f'0.2 0.4 0.6 rg 0 0 320 160 re f /M gs /A gs {230/255:.12f} {52/255:.12f} {76/255:.12f} rg q {clip}160 0 0 96 16 32 cm /Main Do Q q 48 0 0 96 192 32 cm /Plain Do Q 256 32 48 96 re f'
    objects = [
        '<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 320 160] /Contents 4 0 R /Resources << {resources} >> >>',
        stream('', content),
        stream(f'/Type /XObject /Subtype /Image /Width 4 /Height 1 {space} /BitsPerComponent {bpc} {extra}', source),
        stream('/Type /XObject /Subtype /Image /Width 4 /Height 1 ' + mask_entries, mask_data),
        stream('/Type /XObject /Subtype /Form /BBox [0 0 320 160] /Group << /S /Transparency /CS /DeviceGray /I true >> /Resources << /ExtGState << /Reset << /ca 1 /CA 1 /BM /Normal /SMask /None >> >> >>', f'/Reset gs {state or 0} g 0 0 320 160 re f'),
        stream('/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8', bytes(C)),
    ]
    data = pdf(objects)
    (OUT / (name + '.pdf')).write_bytes(data)
    regions = []
    for band in range(4):
        alpha = mask[band] / 255 * ca * (1 if overrides or state is None else state)
        rgb = color(alpha, mode)
        if kind == 'key' and band % 2:
            rgb[2] = B[2] + alpha * (blend(mode, B[2], 77) - B[2])
        x = 16 + band * 40
        l, r = max(x+4, 36 if clipped else x+4), min(x+36, 156 if clipped else x+36)
        regions.append(dict(rect=[l, 52, r-l, 56], rgb=rgb, tolerance=2, purpose=f'image band {band}'))
    persistent = color(ca * (1 if state is None else state), mode)
    for x, purpose in [(196, 'following plain image'), (260, 'following path')]:
        regions.append(dict(rect=[x, 40, 40, 80], rgb=persistent, tolerance=2, purpose=purpose))
    regions.append(dict(rect=[4, 4, 312, 20], rgb=B, tolerance=0, purpose='untouched backdrop'))
    if clipped:
        regions.extend([dict(rect=[18, 48, 10, 64], rgb=B, tolerance=0, purpose='outside left clip'), dict(rect=[164, 48, 10, 64], rgb=B, tolerance=0, purpose='outside right clip')])
    return dict(id=name, file=name+'.pdf', sha256=hashlib.sha256(data).hexdigest(), width=320, height=160, kind=kind, stateMask=state, constantAlpha=ca, blendMode=mode, clipped=clipped, expectedRegions=regions)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        ('smask-opaque-zero-state', 'opaque-smask', 0, .5, 'Normal', False),
        ('smask-partial-zero-state', 'smask', 0, .5, 'Normal', False),
        ('smask-partial-half-state-multiply-clip', 'smask', .5, .5, 'Multiply', True),
        ('smask-partial-half-state-screen', 'smask', .5, .5, 'Screen', False),
        ('smask-partial-no-state', 'smask', None, .5, 'Normal', False),
        ('smask-partial-no-state-multiply', 'smask', None, .5, 'Multiply', True),
        ('smask-partial-no-state-screen', 'smask', None, .5, 'Screen', False),
        ('smask-zero-constant-alpha', 'smask', 0, 0, 'Normal', False),
        ('smask-over-key-zero-state', 'smask-key', 0, .5, 'Normal', False),
        ('explicit-zero-state', 'explicit', 0, .5, 'Normal', False),
        ('key-zero-state', 'key', 0, .5, 'Normal', False),
        ('plain-zero-state', 'plain', 0, .5, 'Normal', False),
        ('plain-half-state', 'plain', .5, .5, 'Normal', False),
        ('stencil-zero-state', 'stencil', 0, .5, 'Normal', False),
        ('stencil-half-state', 'stencil', .5, .5, 'Normal', False),
        ('jpx-alpha-no-state', 'jpx', None, .5, 'Normal', False),
        ('jpx-ignored-alpha-zero-state', 'jpx-ignored', 0, .5, 'Normal', False),
    ]
    (OUT / 'manifest.json').write_text(json.dumps(dict(license='MIT', provenance='Original numerical samples and PDF syntax authored for these regressions. Expectations computed from input alpha, source and backdrop, not rendered snapshots.', fixtures=[make(*case) for case in cases]), indent=2)+'\n')
