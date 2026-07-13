"""Exact integer/Fraction gate for CommonBlue owner-shore reductions."""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent; ROOT=H.parents[3]
R29=ROOT/'tmp/fanout/r29_fullbank_repair/common_blue_absorber_gate.json'
N12=ROOT/'tmp/fanout/r29_fullbank_repair/n12_common_blue_gate.json'
def ps(xs):
 xs=tuple(xs)
 for r in range(len(xs)+1):
  for z in combinations(xs,r): yield frozenset(z)
def nb(A,N): return frozenset().union(*(N[a] for a in A)) if A else frozenset()
def dem(A,w): return sum((w[a] for a in A),Fraction(0))
def df(A,w,N): return dem(A,w)-len(nb(A,N))
def abstract_gate():
 O=tuple(range(3)); SS=tuple(ps(range(3))); systems=shores=minimal=0
 for ws in product((1,2,3),repeat=3):
  w=dict(zip(O,map(Fraction,ws)))
  for ns in product(SS,repeat=3):
   N=dict(zip(O,ns)); systems+=1; P=tuple(ps(O))
   for A in P:
    shores+=1
    for B in P: assert df(A,w,N)+df(B,w,N)<=df(A|B,w,N)+df(A&B,w,N)
    if df(A,w,N)>0 and all(df(B,w,N)<=0 for B in ps(A) if B!=A):
     minimal+=1; delta=df(A,w,N)
     for a in A:
      assert len(nb(A,N)-nb(A-{a},N))<=w[a]-delta and delta<=w[a]
    C=A|frozenset(a for a in O if N[a]<=nb(A,N))
    assert nb(C,N)==nb(A,N) and df(C,w,N)>=df(A,w,N)
 return {'systems':systems,'shores':shores,'minimalDeficientShores':minimal}
def countermodels():
 D=('d0','d1','d2'); N={d:frozenset({'s'}) for d in D}; A=frozenset(D[:2])
 assert len(A)-len(nb(A,N))==1 and all(len(B)<=len(nb(B,N)) for B in ps(A) if B!=A)
 w={'a':Fraction(2),'b':Fraction(1)}; M={'a':frozenset({'x'}),'b':frozenset({'y','z'})}
 assert df(frozenset({'a'}),w,M)==1 and df(frozenset({'a','b'}),w,M)==0
 return {'minimalDemandShoreNotOwnerComplete':{'fiber':3,'shore':2,'reach':1,'defect':1},'componentClosureDestroysDeficiency':{'before':[2,1,1],'after':[3,3,0]}}
def pinned():
 r=json.loads(R29.read_text()); cuts={x['shoreMask']:x for x in r['cuts']}
 assert r['demandByOwner']=={'0':6651,'1':6651,'2':6651} and len(cuts)==8
 assert cuts[7]['demand']==19953 and cuts[7]['neighborhood']==20141 and cuts[7]['defect']==-188
 assert all(x['defect']<=0 for x in cuts.values())
 n=json.loads(N12.read_text()); expected={'graphs':22291,'oldFailures':8224,'remaining':0,'repaired':8224,'tuples':18961358}
 assert n['totals']==expected and n['coverage']['generatedGraphs']==1144061 and n['verdict']=='PASS_ALL_OLD_FAILURES_REPAIRED'
 return {'R29':{'ownerShores':8,'minimumSlack':0,'fullDemand':19953,'fullReach':20141},'N12':expected,'sha256':{'R29':hashlib.sha256(R29.read_bytes()).hexdigest(),'N12':hashlib.sha256(N12.read_bytes()).hexdigest()}}
if __name__=='__main__':
 out=json.dumps({'schema':'COMMON_BLUE_MINIMAL_SHORE_GATE_V1','arithmetic':'integers/Fraction only','abstract':abstract_gate(),'countermodels':countermodels(),'completeDbCensus':pinned()},indent=2,sort_keys=True)+'\n'; (H/'result.json').write_text(out); print(out,end='')

