from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT/'problems'/'23'/'writeup'))
from _codex_r19_global_base_census import dec,loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow
from _codex_scoped_variation_anatomy import scoped_state,owner_shore_source_count
G6='I?`fBO]]?'
def choice_at(i,sizes):
 a=[]
 for s in reversed(sizes): a.append(i%s); i//=s
 return tuple(reversed(a))
def abstract(old,owners,by,alts,oldrow,newrows):
 out=[]; O=set(owners)
 for aid,new in enumerate(alts):
  for owner,amt in sorted(new['demand'].items()):
   if not amt: continue
   comp=new['activeComponent'].get(owner); V={v for v,c in new['activeComponent'].items() if c==comp}
   inherited={a for a in O if any(old['activeComponent'].get(v)==old['activeComponent'].get(a) for v in V)}
   anchors=set(inherited); touched=bool(V&(set(oldrow)|set(newrows[aid])))
   if touched: anchors|=O
   eligible=sorted(set().union(*(by[a] for a in anchors)) if anchors else set())
   out.append({'alternative':aid,'owner':owner,'demand':amt,'anchors':sorted(anchors),'eligible':[list(x) for x in eligible],'touched':touched})
 return out
def shores(groups,caps,outcap,scale,limit=22):
 m=len(groups)
 if m>limit:return None
 ans=[]
 def gap(mask):
  d=sum(groups[i]['demand'] for i in range(m) if mask>>i&1)
  N={tuple(c) for i in range(m) if mask>>i&1 for c in groups[i]['eligible']}
  return d-(outcap+scale*sum(caps.get(c,0) for c in N)),d,N
 for mask in range(1,1<<m):
  g,d,N=gap(mask)
  if g<=0:continue
  if all(gap(mask^(1<<i))[0]<=0 for i in range(m) if mask>>i&1):
   ans.append({'groups':[i for i in range(m) if mask>>i&1],'demand':d,'rhs':d-g,'gap':g,'neighbors':[list(x) for x in sorted(N)]})
 return ans
def main():
 n,E=dec(G6); info=loads(n,E); blue,bad=set(info['Bset']),set(info['Mset']); fam=shortest_row_families(info); sizes=tuple(map(len,fam)); total=1
 for s in sizes:total*=s
 records=[]; hf=ct=mt=skip=0; smallest=None; surv={'coordinate_shared_hall':0,'all_coordinate_shared_hall':0,'owner_demand_le_source':0}
 for ti in range(total):
  ch=choice_at(ti,sizes); rows=tuple(fam[i][ch[i]] for i in range(len(fam)))
  flow=full_owner_flow(n,blue,bad,rows,G6,require_full=False,quiet=True,scope='active',include_outside=False)
  if flow['full']:continue
  hf+=1; old=scoped_state(n,blue,bad,rows); owners=flow['deficientOwners']; source,by,caps=owner_shore_source_count(n,blue,bad,old,owners)
  od=sum(old['demand'].get(v,0) for v in owners); outside=old['score']-od
  if od<=source:surv['owner_demand_le_source']+=1
  cr=[]; AG=[]; AS=0
  for k,F in enumerate(fam):
   alts=[]; nr=[]
   for j,r in enumerate(F):
    if j==ch[k]:continue
    alts.append(scoped_state(n,blue,bad,rows[:k]+(r,)+rows[k+1:])); nr.append(r)
   G=abstract(old,owners,by,alts,rows[k],nr); sc=len(alts); S=shores(G,caps,outside,1); ct+=1
   if S is None:skip+=1
   elif not S:surv['coordinate_shared_hall']+=1
   else:
    w={'tupleIndex':ti,'choice':list(ch),'coordinate':k,'familySize':len(F),'groups':G,'capacities':{f'{x},{y}':v for (x,y),v in sorted(caps.items())},'outsideCapacity':sc*outside,'minimalDeficientShores':S}
    key=(len(S[0]['groups']),sum(x['demand'] for x in G),ti,k)
    if smallest is None or key<smallest[0]:smallest=(key,w)
   cr.append({'coordinate':k,'groupCount':len(G),'minimalDeficientCount':None if S is None else len(S),'maxGap':None if S is None or not S else max(x['gap'] for x in S)})
   AG.extend(G);AS+=sc
  S=shores(AG,caps,outside,1);mt+=1
  if S is None:skip+=1
  elif not S:surv['all_coordinate_shared_hall']+=1
  records.append({'tupleIndex':ti,'choice':list(ch),'deficiency':flow['deficiency'],'owners':owners,'ownerDemand':od,'sourceCapacity':source,'coordinates':cr,'allCoordinateGroupCount':len(AG),'allCoordinateMinimalDeficientCount':None if S is None else len(S),'allCoordinateMaxGap':None if S is None or not S else max(x['gap'] for x in S)})
 result={'parameters':{'g6':G6,'n':n,'familySizes':sizes,'tupleCount':total,'subsetLimit':22,'arithmetic':'exact integers'},'counts':{'hallFailures':hf,'coordinateTests':ct,'multiCoordinateTests':mt,'subsetEnumerationsSkipped':skip},'survivors':surv,'records':records,'smallestWitness':None if smallest is None else smallest[1]}
 Path(__file__).with_name('results_unscaled.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8');print(result['counts']);print(surv)
if __name__=='__main__':main()

