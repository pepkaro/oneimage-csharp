#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
PDFJS_RUNTIME=${1:?Provide the pinned pdfjs-dist directory}
python generate.py
python verify-structure.py
python run-references.py "$PDFJS_RUNTIME"
python verify-regions.py
python verify.py
