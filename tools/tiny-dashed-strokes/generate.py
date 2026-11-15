# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
"""Original numeric PDF controls. No fonts, images, external inputs, or reference pixels."""
import argparse
import hashlib
import json
from pathlib import Path


def pdf(content):
    stream = content.encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 128 96] /CropBox [0 0 128 96] /Rotate 0 /Resources << >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.7\n% Original MIT numeric stroke controls\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n")
    start = len(output)
    output.extend(b"xref\n0 5\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(f"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode("ascii"))
    return bytes(output)


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    tiny = "64 48 m 64.00000002 48 l"
    cases = [
        ("closed-on", tiny + " h", "[9 13] 2 d", 1),
        ("open-on", tiny, "[9 13] 2 d", 1),
        ("closed-off", tiny + " h", "[9 13] 11 d", 1),
        ("closed-solid", tiny + " h", "[] 0 d", 1),
        ("stationary-on", "64 48 m 64 48 l h", "[9 13] 2 d", 1),
        ("ordinary-on", "64 48 m 64.25 48 l h", "[9 13] 2 d", 1),
        ("reverse-on", "64 48 m 63.99999998 48 l h", "[9 13] 2 d", 1),
        ("cubic-on", "64 48 m 64.00000002 48 64.00000002 48 64 48 c h", "[9 13] 2 d", 1),
        ("square-on", tiny + " h", "[9 13] 2 d", 2),
        ("butt-on", tiny + " h", "[9 13] 2 d", 0),
        ("odd-on", tiny + " h", "[9 13 7] 2 d", 1),
        ("zero-on", tiny + " h", "[0 13] 0 d", 1),
        ("normalized-solid", tiny + " h", "[.00001 .00001] 0 d", 1),
    ]
    manifest = []
    for name, path, dash, cap in cases:
        content = f"0 G 16 w {cap} J {dash} {path} S"
        data = pdf(content)
        (directory / (name + ".pdf")).write_bytes(data)
        manifest.append({"name": name, "content": content, "sha256": hashlib.sha256(data).hexdigest()})
    (directory / "cases.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
