#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline integrity, analytic scoring and pairwise agreement verification."""
from pathlib import Path
import hashlib,json,re
from itertools import combinations
import numpy as np
from PIL import Image
from score import expected
ROOT=Path(__file__).resolve().parent

def main():
 manifest=json.loads((ROOT/'manifest.json').read_text());cases={c['id']:c for c in manifest['cases']}
 renders=json.loads((ROOT/'reference-renders.json').read_text())['records']
 results=json.loads((ROOT/'reference-results.json').read_text())
 assert len(cases)==8 and len(renders)==48 and len(results['rows'])==48
 digests=[]
 for case in cases.values():
  data=(ROOT/case['file']).read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==case['sha256'];digests.append(digest)
  assert data.startswith(b'%PDF-2.0\n') and data.endswith(b'%%EOF\n')
  xref=int(re.search(rb'startxref\n([0-9]+)\n',data).group(1));assert data[xref:].startswith(b'xref\n')
  stream=re.search(rb'/Length ([0-9]+) >>\nstream\n(.*?)\nendstream',data,re.S);assert len(stream.group(2))==int(stream.group(1))
  association=case['upstream_association'];assert association['upstream_id'] is None and not association['upstream_input_executed'] and not association['exact_upstream_scope_established']
 assert len(set(digests))==8
 bykey={}
 for record in renders:
  output=ROOT/record['output'];assert hashlib.sha256(output.read_bytes()).hexdigest()==record['sha256']
  assert record['input_sha256']==cases[record['id']]['sha256']
  bykey[(record['id'],record['dpi'],record['engine'])]=np.asarray(Image.open(output).convert('RGB'))
 assert len(bykey)==48 and all(r['status']=='passed' for r in results['rows'])
 samples=sum(len(r.get('samples',[])) for r in results['rows']);assert samples==198
 pairs=[]
 for case in cases.values():
  for dpi in case['dpis']:
   analytic,mask=expected(case,dpi)
   for engine in ['pdfium','mupdf','pdfjs']:
    image=bykey[(case['id'],dpi,engine)];assert image.shape==analytic.shape and np.array_equal(image[mask],analytic[mask])
   for a,b in combinations(['pdfium','mupdf','pdfjs'],2):
    left=bykey[(case['id'],dpi,a)];right=bykey[(case['id'],dpi,b)]
    wrong=int(np.any(left!=right,axis=2)[mask].sum());assert wrong==0
    pairs.append(dict(id=case['id'],dpi=dpi,engines=[a,b],scored_pixels=int(mask.sum()),unscored_boundary_pixels=int((~mask).sum()),disagreeing_scored_pixels=wrong,status='passed'))
 output=dict(unique_original_pdfs=8,reference_outputs=48,analytic_reference_passed=48,analytic_reference_failed=0,sample_checks_passed=samples,pairwise_checks_passed=len(pairs),pairwise_checks_failed=0,boundaries='One device-pixel band around analytic region boundaries is unscored, declared before rendering',upstream_inputs_executed=0,upstream_rows_validated=0,rows=pairs)
 (ROOT/'agreement-results.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:v for k,v in output.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
