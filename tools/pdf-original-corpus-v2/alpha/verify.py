# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil
from pypdf import PdfReader
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());refs=json.loads((R/'reference-results.json').read_text());assert len(m['cases'])==7 and len({c['sha256'] for c in m['cases']})==7
for c in m['cases']:
 p=R/c['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];doc=PdfReader(p,strict=True);assert len(doc.pages)==1
 page=doc.pages[0];assert page.get('/Annots') is None;assert page['/Resources'].get('/XObject') is None;assert page['/Resources'].get('/Font') is None
 for state in page['/Resources']['/ExtGState'].values():assert state['/BM']=='/Normal' and state['/AIS'].value is False and state.get('/SMask') is None
for r in refs['rows']:assert hashlib.sha256((R/r['file']).read_bytes()).hexdigest()==r['sha256']
assert (refs['reference_runs'],refs['passed'],refs['failed'],refs['skipped'])==(42,30,12,0)
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);shutil.copy(R/'generate.py',tmp/'generate.py');subprocess.run([sys.executable,str(tmp/'generate.py')],check=True)
 for c in m['cases']:assert (R/c['file']).read_bytes()==(tmp/c['file']).read_bytes()
print('7 deterministic valid original alpha PDFs;42 verified capture digests;3 agreed /4 held;0 upstream credit')
