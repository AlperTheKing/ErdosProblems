import json,sys,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'problems'/'23'/'writeup'))
from _codex_r19_global_base_census import dec,loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow
from _codex_scoped_variation_anatomy import scoped_state,owner_shore_source_count
from exact_probe import choice_at,G6
n,E=dec(G6);info=loads(n,E);B,M=set(info['Bset']),set(info['Mset']);F=shortest_row_families(info);sizes=tuple(map(len,F));T=1
for s in sizes:T*=s
out=[]
for ti in range(T):
 ch=choice_at(ti,sizes);rows=tuple(F[i][ch[i]] for i in range(len(F)));fl=full_owner_flow(n,B,M,rows,G6,require_full=False,quiet=True,scope='active',include_outside=False)
 if fl['full']:continue
 old=scoped_state(n,B,M,rows);O=fl['deficientOwners'];src,by,cap=owner_shore_source_count(n,B,M,old,O); shores=[]; allineq=[]
 for mask in range(1,1<<len(O)):
  S=[O[i] for i in range(len(O)) if mask>>i&1];N=set().union(*(by[o] for o in S));d=sum(old['demand'].get(o,0) for o in S);c=sum(cap[x] for x in N);g=d-c
  rec={'owners':S,'demand':d,'capacity':c,'gap':g,'neighbors':[list(x) for x in sorted(N)]};allineq.append(rec)
  if g>0 and all(next(z['gap'] for z in allineq if z['owners']==[o])<=0 for o in S):shores.append(rec)
 out.append({'tupleIndex':ti,'choice':list(ch),'owners':O,'capacities':{f'{x},{y}':v for (x,y),v in sorted(cap.items())},'inequalities':allineq,'inclusionMinimalDeficientShores':shores,'exactMaxGap':max(x['gap'] for x in allineq),'exactMinSlack':min(x['capacity']-x['demand'] for x in allineq)})
Path(__file__).with_name('base_shores.json').write_text(json.dumps({'arithmetic':'exact integers','fixtures':out},sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps(out,indent=2))
