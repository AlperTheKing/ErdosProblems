"""Exact Door-lane replay for the first N=12 micro-Hall fixture."""
from __future__ import annotations
import json, sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'tmp/fanout/pht_n12_direct'))
import n12_pht as n12
G6='K??E@cyjFgWk'; CHOICE=(0,4,5,7); SHORE={10,11}
def norm(x,y): return (x,y) if x<y else (y,x)
def main():
 n,edges=n12.dec(G6); info=n12.loads(n,edges)
 assert n==12 and info is not None
 families=n12.shortest_row_families(info); rows=tuple(n12.rows_for_choice(families,CHOICE))
 assert tuple(map(len,families))==(6,5,8,10)
 blue,bad=set(info['Bset']),set(info['Mset'])
 bb=sorted(e for e in blue if (e[0] in SHORE)!=(e[1] in SHORE)); mb=sorted(e for e in bad if (e[0] in SHORE)!=(e[1] in SHORE))
 dB,dM=len(bb),len(mb); sigma=dB-dM
 pair=Counter(); rc=Counter(); support=set()
 for row in rows:
  for x in row:
   rc[x]+=1
   for y in row: pair[x,y]+=1
  support.update(norm(x,y) for x,y in zip(row,row[1:]))
 selected=set().union(*map(set,rows)); active={e for e in blue if set(e)<=selected and e not in support}; ad=Counter(v for e in active for v in e)
 collision={o:2*sum(m-1 for (x,_),m in pair.items() if x==o and m>=2) for o in SHORE}
 hit={o:max(0,ad[o]-max(0,n-5*rc[o])) for o in SHORE}
 demand=sum(collision[o]+25*hit[o] for o in SHORE); reach=59; defect=demand-reach
 assert (demand,defect)==(72,13) and (dB,dM,sigma)==(8,2,6)
 result={'schema':'N12_DEFECT13_DOOR_AUDIT_V1','g6':G6,'choice':list(CHOICE),'familySizes':list(map(len,families)),'deficientShore':sorted(SHORE),'microDemand':demand,'existingReach':reach,'defect':defect,'rawGraph':{'blueBoundaryKeys':[list(e) for e in bb],'badBoundaryKeys':[list(e) for e in mb],'dB':dB,'dM':dM,'sigma':sigma},'aggregateDoorIfCapQEquals25Sigma':{'capQ':25*sigma,'hallCapacity':sigma,'comparisonToDefect':sigma-defect},'typedDoor':{'literalKeysConstructedByCanonicalGraphRowCode':[],'candidateExitEdgeKeysNotTypedTokens':[list(e) for e in bb],'legalPortIncidence':[],'checkedNoDoubleSpendAssignments':[],'reason':'no production extractor adapter constructs OwnEdgeDoorSourceData from this fixture'},'decision':'DOOR_DOES_NOT_PAY_13','basis':'even aggregate Hall capacity is 6 < 13; typed legal incidence is additionally absent'}
 (HERE/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
