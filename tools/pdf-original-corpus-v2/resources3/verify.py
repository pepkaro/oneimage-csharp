#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json,re
import numpy as np
from PIL import Image
from score import expected
ROOT=Path(__file__).resolve().parent

def main():
 m=json.loads((ROOT/'manifest.json').read_text());cases={c['id']:c for c in m['cases']};renders=json.loads((ROOT/'reference-renders.json').read_text())['records'];results=json.loads((ROOT/'reference-results.json').read_text());digests=[]
 assert len(cases)==5 and len(renders)==30 and len(m['fixtures'])==3
 for c in cases.values():
  data=(ROOT/c['file']).read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==c['sha256'];digests.append(digest);assert data.startswith(b'%PDF-1.7\n') and data.endswith(b'%%EOF\n')
  xref=int(re.search(rb'startxref\n([0-9]+)\n',data).group(1));assert data[xref:].startswith(b'xref\n')
  for entry in re.finditer(rb'/Length ([0-9]+) >>\nstream\n(.*?)\nendstream',data,re.S):assert len(entry.group(2))==int(entry.group(1))
  assert c['upstream_association']['upstream_id'] is None
 assert len(set(digests))==3;keys=set()
 for r in renders:
  f=ROOT/r['output'];assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];assert r['input_sha256']==cases[r['id']]['sha256'] and r['page']==cases[r['id']]['page'];key=(r['id'],r['dpi'],r['engine']);assert key not in keys;keys.add(key)
  a=np.asarray(Image.open(f).convert('RGB'));rgb,mask=expected(cases[r['id']],r['dpi']);assert a.shape==rgb.shape and np.array_equal(a[mask],rgb[mask])
 assert results['executed']==results['passed']==30 and results['failed']==results['skipped']==0
 assert results['sample_passes']==results['sample_checks']==180 and results['pairwise_passes']==30 and results['pairwise_failures']==0
 print(json.dumps(dict(unique_pdfs=3,page_views=5,selected_references=30,analytic_passes=30,sample_passes=180,pairwise_passes=30,upstream_entries_validated=0),indent=2))
if __name__=='__main__':main()
