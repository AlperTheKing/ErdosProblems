"""Exact replay of N=12 deficient-shore vertexSlack accounting."""
from collections import Counter
from fractions import Fraction
import hashlib, itertools, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'tmp/fanout/pht_n12_direct'))
import n12_pht as n12
G6='K??E@cyjFgWk'; CHOICE=(0,4,5,7); DEFICIENT=(10,11)

def norm(x,y): return (x,y) if x<y else (y,x)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 n,edges=n12.dec(G6); assert n==12
 info=n12.loads(n,edges); assert info is not None
 families=n12.shortest_row_families(info); assert tuple(map(len,families))==(6,5,8,10)
 assert list(itertools.product(*(range(len(f)) for f in families))).index(CHOICE)==377
 rows=tuple(tuple(r) for r in n12.rows_for_choice(families,CHOICE))
 occ=Counter(); pair=Counter(); support=set()
 for row in rows:
  assert len(row)==5
  for x in row: occ[x]+=1
  for x in row:
   for y in row: pair[x,y]+=1
  support.update(norm(x,y) for x,y in zip(row,row[1:]))
 selected=set(occ)
 active={e for e in info['Bset'] if set(e)<=selected and e not in support}
 parent={v:v for v in selected}
 def find(v):
  while parent[v]!=v: parent[v]=parent[parent[v]]; v=parent[v]
  return v
 def union(x,y):
  x,y=find(x),find(y)
  if x!=y: parent[max(x,y)]=min(x,y)
 for e in active: union(*e)
 roots={find(x) for x,y in info['Mset'] if x in selected and y in selected and find(x)==find(y)}
 active_vertices={v for v in selected if find(v) in roots}
 demanded={e for e in active if find(e[0]) in roots}
 degree=Counter(x for e in demanded for x in e)
 table=[]
 for v in DEFICIENT:
  selected_load=5*occ[v]
  raw=max(0,n-selected_load)
  hit=max(0,degree[v]-raw)
  spent=min(raw,degree[v])
  residual=raw-spent
  incident=sorted(e for e in demanded if v in e)
  collision=2*sum(m-1 for (x,_),m in pair.items() if x==v and m>=2)
  table.append({'owner':v,'typedSourceKey':f'vertexSlack({v})','rowOccurrences':occ[v],
   'selectedLoad':selected_load,'rawGraphSlack':raw,'rawCapQ':25*raw,
   'rawHallCapacity':str(Fraction(25*raw,25)),'activeDegree':degree[v],
   'legalPorts':[list(e) for e in incident],'legalPortCostHallEach':'1',
   'spentInsideHitNeedPrepayment':spent,'spentCapQ':25*spent,'hitNeedUnits':hit,
   'residualNonDoubleCountedHallCapacity':str(Fraction(residual)),'residualCapQ':25*residual,
   'collisionMicroDemand':collision})
 assert [(x['owner'],x['rawGraphSlack'],x['activeDegree'],x['hitNeedUnits'],x['residualCapQ']) for x in table]==[(10,0,2,2,0),(11,2,2,0,0)]
 assert table[0]['legalPorts']==[[0,10],[2,10]] and table[1]['legalPorts']==[[0,11],[1,11]]
 shore_collision=sum(x['collisionMicroDemand'] for x in table)
 shore_hit=sum(x['hitNeedUnits'] for x in table)
 assert shore_collision==22 and shore_hit==2
 payload={'schema':'N12_DEFICIENT_SHORE_VERTEXSLACK_V1','fixture':{'g6':G6,'n':n,'familySizes':list(map(len,families)),'choice':list(CHOICE),'tupleIndex':377,'rows':[list(r) for r in rows],'deficientOwners':list(DEFICIENT),'reportedDefectMicrocopies':13},
 'scale':{'microcopiesPerHitNeed':25,'hallCapacityDefinition':'capQ/25'},'perOwner':table,
 'shore':{'collisionMicroDemand':shore_collision,'hitNeedUnits':shore_hit,'hitNeedMicroDemand':25*shore_hit,'microDemand':shore_collision+25*shore_hit,'rawVertexSlackCapQ':sum(x['rawCapQ'] for x in table),'alreadySpentVertexSlackCapQ':sum(x['spentCapQ'] for x in table),'residualVertexSlackCapQ':sum(x['residualCapQ'] for x in table),'residualVertexSlackHallCapacity':'0','paysDefect13':False},
 'noDoubleSpend':'raw slack at owner 11 is consumed by its two legal active-edge ports before hitNeedUnits is formed; reusing capQ 50 against the deficient micro-shore would double spend it.',
 'productionFullBankAdapter':{'typedLabelExists':True,'globalVertexSlackTokenInstantiated':False,'globalLegalIncidenceCheckerExists':False,'localEll5EndpointQCostPerIncidentEdge':'1/2','microHitNeedPrepaymentCostPerActiveEndpoint':'1','zeroResidualConclusionDependsOnMissingAdapter':False},
 'verdict':'NO_VERTEXSLACK_PAYMENT'}
 sources=[ROOT/'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean',ROOT/'tmp/fanout/pht_n12_direct/n12_pht.py']
 payload['sourceSha256']={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sources}
 out=HERE/'result.json'; out.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'verdict':payload['verdict'],'residualCapQ':0,'pays13':False},sort_keys=True))
if __name__=='__main__': main()

