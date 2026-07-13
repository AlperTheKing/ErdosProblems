"""Exact cross-lane referee for the K??E@cyjFgWk defect-13 fixture."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; PIVOT=HERE.parent
LANES={'A':PIVOT/'laneA_replay','B':PIVOT/'laneB_vertex_slack','C':PIVOT/'laneC_door','D':PIVOT/'laneD_prune'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def nofloat(x,path='$'):
 if isinstance(x,float): raise AssertionError('float at '+path)
 if isinstance(x,dict):
  for k,v in x.items(): nofloat(v,path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x): nofloat(v,f'{path}[{i}]')
def load(label):
 lane=LANES[label]; checked={}
 for line in (lane/'MANIFEST.sha256').read_text().splitlines():
  digest,name=line.split(None,1); name=name.strip().lstrip('*'); p=lane/name
  assert p.is_file() and sha(p)==digest; checked[name]=digest
 assert 'REPORT.md' in checked and 'result.json' in checked
 data=json.loads((lane/'result.json').read_text()); nofloat(data); return data,checked
def main():
 z={x:load(x) for x in LANES}; a,b,c,d=(z[x][0] for x in 'ABCD')
 assert a['g6']=='K??E@cyjFgWk' and a['choice']==[0,4,5,7] and a['familySizes']==[6,5,8,10] and a['tupleIndex']==377
 assert (a['collisionDemand'],a['hitNeedSlots'],a['microDemand'])==(28,2,78)
 assert (a['maxFlow'],a['defect'],a['deficientOwners'])==(65,13,[10,11])
 for x in (b['fixture'],c,d): assert x['g6']==a['g6'] and x['choice']==a['choice'] and x['familySizes']==a['familySizes']
 assert b['shore']['rawVertexSlackCapQ']==50 and b['shore']['alreadySpentVertexSlackCapQ']==50
 assert b['shore']['residualVertexSlackCapQ']==0 and b['shore']['paysDefect13'] is False
 assert c['rawGraph']['sigma']==6 and c['aggregateDoorIfCapQEquals25Sigma']['capQ']==150
 assert c['aggregateDoorIfCapQEquals25Sigma']['hallCapacity']==6
 assert c['typedDoor']['literalKeysConstructedByCanonicalGraphRowCode']==[]
 assert c['typedDoor']['legalPortIncidence']==[] and c['typedDoor']['checkedNoDoubleSpendAssignments']==[]
 inv=d['legalPruneInventory']; assert inv['count']==0 and inv['typedSourceKeys']==[] and inv['portIncidences']==[] and inv['capQ']==0
 assert d['paymentDecision']['requiredRawCapQ']==325 and d['paymentDecision']['pays13'] is False
 out={'schema':'N12_DEFECT13_TYPED_REFEREE_V1','verdict':'DEFECT13_NOT_REPAIRED_BY_AUDITED_FULLBANK_CLASSES',
 'fixture':{'g6':a['g6'],'choice':a['choice'],'familySizes':a['familySizes'],'tupleIndex':377,'collisionDemand':28,'hitNeedSlots':2,'microDemand':78,'maxFlow':65,'defect':13,'deficientOwners':[10,11],'deficientShoreDemand':72,'deficientShoreReach':59},
 'scale':{'hallCapacity':'capQ/25','requiredAdditionalCapQ':325},
 'certifiedCapacity':{'vertexSlackResidualCapQ':0,'doorTypedResidualCapQ':0,'pruneTypedResidualCapQ':0,'totalCertifiedAdditionalCapQ':0,'totalCertifiedAdditionalHallUnits':0},
 'rejections':['vertexSlack(11) raw capQ 50 is already spent in HitNeed prepayment','raw door sigma 6 is not a typed token inventory and is below defect 13 even in aggregate','no production prune provider supplies typed source keys or legal port incidence','FullBankPortSinks partitions aggregate tokens but supplies no legal edge-to-token incidence'],
 'exactAdditionalCondition':{'name':'residual typed cut augmentation','statement':'Add a source-disjoint typed residual flow of value 13 across the lane-A minimum cut for owners {10,11}; equivalently add spend variables totaling 325 capQ, each incident to a legal deficient-shore port, with per-(component,kind,payload) spend at most capQ and with no key or underlying FreeHalf reused by collision, HitNeed, c5Base, Door, vertexSlack, or prune charges.','whyExact':'The certified shore has demand 72 and neighbor capacity 59. A legal residual augmentation of 13 saturates it; any value at most 12 leaves this same cut deficient. Aggregate capacity without cut incidence does not imply the augmentation.'},
 'laneManifestHashes':{x:z[x][1] for x in LANES}}
 (HERE/'result.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'verdict':out['verdict'],'defect':13,'certifiedAdditionalHallUnits':0},sort_keys=True))
if __name__=='__main__': main()
