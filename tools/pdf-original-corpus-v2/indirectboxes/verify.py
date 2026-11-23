#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib,subprocess,sys
R=Path(__file__).resolve().parent;subprocess.run([sys.executable,str(R/'verify-structure.py')],check=True);m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());a=json.loads((R/'region-agreement.json').read_text());calls=json.loads((R/'invocations.json').read_text());assert r['reference_runs']==18 and r['skipped']==0 and calls['renderer_subprocess_invocations']==18 and calls['by_engine']==dict(pdfium=6,mupdf=6,pdfjs=6)
for row in r['rows']:
 if row['exit_code']==0:assert hashlib.sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
assert len(a['accepted_fixture_ids'])+len(a['held_fixture_ids'])==3
print(json.dumps(dict(unique_pdfs=3,reference_executed=18,reference_passed=r['passed'],reference_failed=r['failed'],reference_skipped=0,agreed=a['accepted_fixture_ids'],held=a['held_fixture_ids'],upstream_credited=0,product_executed=0)))
