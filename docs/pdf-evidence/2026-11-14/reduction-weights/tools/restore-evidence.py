#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original, lossless evidence reconstruction; no network access or renderer required.
from pathlib import Path, PurePosixPath
import gzip, hashlib, json, sys

def checked_path(root, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts or not name.parts:
        raise ValueError(f'Unsafe relative path: {relative!r}')
    result = root.joinpath(*name.parts)
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes package: {relative!r}')
    return result

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python tools/restore-evidence.py /new/empty/output-directory')
    root = Path(__file__).resolve().parents[1]
    target = Path(sys.argv[1]).resolve()
    if target == root or target.is_relative_to(root) or root.is_relative_to(target):
        raise SystemExit('Choose an output directory separate from the transport package.')
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise SystemExit('Refusing to overwrite: output must be absent or empty.')
    description = json.loads((root/'transport-manifest.json').read_text())
    if description['format'] != 'oneimage-lossless-evidence-transport-v1':
        raise SystemExit('Unknown transport format.')
    decoded = []
    seen = set()
    for entry in description['originalFiles']:
        if entry['originalPath'] in seen:
            raise SystemExit('Duplicate destination path.')
        seen.add(entry['originalPath'])
        source = checked_path(root, entry['storedPath'])
        destination = checked_path(target, entry['originalPath'])
        packed = source.read_bytes()
        if len(packed) != entry['storedBytes'] or digest(packed) != entry['storedSha256']:
            raise SystemExit(f'Stored byte/hash mismatch: {entry["storedPath"]}')
        if entry['encoding'] == 'gzip':
            data = gzip.decompress(packed)
        elif entry['encoding'] == 'identity':
            data = packed
        else:
            raise SystemExit(f'Unsupported encoding: {entry["encoding"]}')
        if len(data) != entry['originalBytes'] or digest(data) != entry['originalSha256']:
            raise SystemExit(f'Reconstructed byte/hash mismatch: {entry["originalPath"]}')
        decoded.append((destination, data))
    # Verify every source before writing any destination.
    for destination, data in decoded:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    print(json.dumps({'reconstructedFiles':len(decoded),'everyOriginalSha256Verified':True,'outputDirectory':str(target)},indent=2))

if __name__ == '__main__':
    main()
