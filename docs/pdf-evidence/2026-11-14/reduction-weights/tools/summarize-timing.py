# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original analysis of all six processes; no sample trimming.
from pathlib import Path
import json, statistics
R=Path(__file__).resolve().parents[1]
files=sorted((R/'measurements').glob('run-*.json'))
assert len(files)==6
rows=[]
for f in files:
 d=json.loads(f.read_text());side=f.stem.split('-')[-1]
 assert d['metadata']['processorCount']==2
 assert d['metadata']['environment']['DOTNET_TieredCompilation']=='0'
 assert d['metadata']['environment']['DOTNET_TieredPGO']=='0'
 assert d['areaSha256']=='737646b1833eea52c03b0e714988df80149770f0d5a968a205d7291817bf250d'
 assert d['rgbaSha256']=='10c746d1fc254190a534195cb5c1358e5a9a2166477c168363ee32133d862445'
 for rec in d['records']:
  expected=d['areaSha256'] if rec['boundary']=='production-area-only' else d['rgbaSha256']
  assert len(rec['allIterations'])==35 and all(it['rgbaSha256']==expected for it in rec['allIterations'])
  assert sum(it['phase']=='warmup' for it in rec['allIterations'])==10
  assert sum(it['phase']=='measured' for it in rec['allIterations'])==25
  assert len(rec['elapsedMsPerOperation'])==25
  assert statistics.median(rec['elapsedMsPerOperation'])==rec['medianMs']
  rows.append({'process':f.name,'side':side,'boundary':rec['boundary'],'medianMs':rec['medianMs'],'minMeasuredMs':rec['minMs'],'maxMeasuredMs':rec['maxMs'],'minCurrentThreadAllocatedBytes':min(rec['currentThreadAllocatedBytesPerOperation']),'maxCurrentThreadAllocatedBytes':max(rec['currentThreadAllocatedBytesPerOperation'])})
summary={}
for boundary in ['production-area-only','fresh-pdf-load-and-render']:
 medians={side:[r['medianMs'] for r in rows if r['side']==side and r['boundary']==boundary] for side in ['before','after']}
 before,after=[statistics.median(medians[side]) for side in ['before','after']]
 summary[boundary]={'processMedians':medians,'medianOfBeforeProcessMediansMs':before,'medianOfAfterProcessMediansMs':after,'percentLowerMedianOfMedians':100*(1-after/before),'beforeOverAfterRatio':before/after,'processMedianRangesOverlap':not(max(medians['before'])<min(medians['after']) or max(medians['after'])<min(medians['before']))}
output={'license':'MIT','method':'Median of three independent process medians per side, 25 measured operations per boundary/process after 10 retained warmup operations. No samples removed. Fixed sequence before,after,after,before,before,after.','windowStartUtc':(R/'measurements/window-start-utc.txt').read_text().strip(),'windowEndUtc':(R/'measurements/window-end-utc.txt').read_text().strip(),'windowExitStatus':int((R/'measurements/window-exit-status.txt').read_text()),'warmupRecords':120,'measuredRecords':300,'all420OutputHashesMatch':True,'rows':rows,'summary':summary,'interpretation':'Controlled steady-state Area-only improvement on this input, not default-runtime or native-viewer performance. Fresh-PDF process median ranges overlap; do not claim a clear end-to-end gain. Current-thread allocation is not total allocation, pool capacity, or peak memory.'}
(R/'timing-summary.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(summary,indent=2))
