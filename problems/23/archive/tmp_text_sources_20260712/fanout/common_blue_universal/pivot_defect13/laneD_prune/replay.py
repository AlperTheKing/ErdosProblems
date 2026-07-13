"""Exact prune-provider audit for graph6 K??E@cyjFgWk, choice (0,4,5,7)."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path[:0]=[str(ROOT/'tmp/fanout/pht_n12_direct'),str(ROOT/'problems/23/writeup')]
import n12_pht as n12
G6='K??E@cyjFgWk'; CHOICE=(0,4,5,7); SHORE=(10,11)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 n,edges=n12.dec(G6); assert n==12
 info=n12.loads(n,edges); assert info and all(x==5 for x in info['ell'].values())
 fam=n12.shortest_row_families(info); assert tuple(map(len,fam))==(6,5,8,10)
 rows=tuple(n12.rows_for_choice(fam,CHOICE)); old=n12.scoped_score(n,info,rows)
 candidates=[]
 for i,F in enumerate(fam):
  for j,row in enumerate(F):
   if j==CHOICE[i]: continue
   nr=rows[:i]+(row,)+rows[i+1:]
   score=n12.scoped_score(n,info,nr)
   candidates.append({'coordinate':i,'replacement':j,'oldRow':list(rows[i]),'newRow':list(row),'oldScopedRank':old,'newScopedRank':score,'rankDelta':score-old,'strictDecrease':score<old})
 lean=ROOT/'problems/23/lean'
 needles=['structure CheckedPruneStep','inductive CheckedTransferEdge','def checkedPruneReachability','localRankDecrease','moveSound','slotTransport','pruneTransport']
 hits={q:[] for q in needles}
 for p in (lean/'Erdos23Delta0').glob('*.lean'):
  s=p.read_text(encoding='utf-8')
  for q in needles:
   if q in s: hits[q].append(str(p.relative_to(ROOT)).replace('\\','/'))
 assert not any(hits.values())
 fixture=json.loads((ROOT/'tmp/fanout/r29_fullbank_local/n12_first_micro_fixture.json').read_text())
 cut=next(x for x in fixture['cuts'] if x['shore']==list(SHORE)); assert cut['defect']==13
 strict=sum(x['strictDecrease'] for x in candidates)
 result={'schema':'N12_DEFECT13_PRUNE_PROVIDER_AUDIT_V1','g6':G6,'choice':list(CHOICE),'familySizes':list(map(len,fam)),'rows':[list(r) for r in rows],'deficientShore':list(SHORE),'shoreDemand':cut['demand'],'shoreExistingReach':cut['reach'],'defect':cut['defect'],'rawGraph':{'vertices':n,'edges':len(edges),'blueEdges':len(info['Bset']),'badEdges':len(info['Mset']),'selectedVertices':fixture['selected'],'activeComponents':fixture['activeComponents']},'rewritePreUniverse':{'hammingOneCandidates':len(candidates),'strictScopedRankDecreases':strict,'candidates':candidates},'productionProviderSearch':hits,'legalPruneInventory':{'count':0,'typedSourceKeys':[],'componentOwners':[],'portIncidences':[],'capQ':0,'hallCapQ':'0/25 = 0','spendQ':0,'noDoubleSpend':'0 <= 0 (vacuous)'},'paymentDecision':{'requiredHallSlots':13,'requiredRawCapQ':325,'providedHallSlots':0,'providedRawCapQ':0,'pays13':False,'reason':'provider_absent_not_graph_level_zero_theorem'},'sourceHashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [ROOT/'problems/23/lean/Erdos23Delta0/Gamma/CommonBlueExtendedMatching.lean',ROOT/'problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean',ROOT/'problems/23/lean/Erdos23Delta0/Ell5DistancePrune.lean',ROOT/'tmp/fanout/pht_n12_direct/n12_pht.py']}}
 (HERE/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'defect':13,'candidates':len(candidates),'strictScopedRankDecreases':strict,'legalPruneSources':0,'pays13':False},sort_keys=True))
if __name__=='__main__': main()

