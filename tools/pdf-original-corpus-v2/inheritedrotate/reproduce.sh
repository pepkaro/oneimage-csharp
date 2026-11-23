#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
cd -- "$(dirname -- "$0")"
python generator.py
python verify-structure.py
python references.py
python score.py
python verify.py
python verify-regions.py
