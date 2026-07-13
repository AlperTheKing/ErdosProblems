import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
r=json.loads((H/'result.json').read_text()); a=json.loads((H/'r29_common_blue_micro_allocation.json').read_text()); c=json.loads((H/'n3892_certificate.json').read_text())
assert r['verdict']=='PASS' and r['coverage']['skipped']==0
flat=[]
for o,xs in a['ownerSources'].items():
 assert len(xs)==6675
 flat += [tuple(x) for x in xs]
assert len(flat)==len(set(flat))==20025
flat2=[]
for o,xs in c['microAllocation'].items():
 assert len(xs)==25
 flat2 += [tuple(x) for x in xs]
assert len(flat2)==len(set(flat2))==50
for rec in c['records']:
 assert rec['commonBlue'] and rec['permanentlyFree'] and rec['adjustedSurplus']==56 and rec['blueBoundary']==58 and rec['badBoundary']==0
assert len(c['records'])==81
print(json.dumps({'verified':True,'r29Keys':len(flat),'n3892Keys':len(flat2),'n3892Records':len(c['records'])},sort_keys=True))
