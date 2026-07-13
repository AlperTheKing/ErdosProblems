from fractions import Fraction
from itertools import combinations,product
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; FIXTURE=ROOT/'tmp/fanout/transport_dual/accounting/default.json'
def ps(x):
 x=tuple(x)
 for r in range(len(x)+1): yield from map(frozenset,combinations(x,r))
def dem(A,w): return sum((w[a] for a in A),Fraction())
def nb(A,n): return frozenset().union(*(n[a] for a in A)) if A else frozenset()
def df(A,w,n): return dem(A,w)-len(nb(A,n))
def minimal(A,w,n): return df(A,w,n)>0 and all(df(B,w,n)<=0 for B in ps(A) if B!=A)
def verify(O,w,n):
 S=list(ps(O)); M=[A for A in S if minimal(A,w,n)]
 for A in M:
  delta=df(A,w,n)
  for a in A: assert len(nb(A,n)-nb(A-{a},n))<=w[a]-delta and delta<=w[a]
  for B in S: assert df(A,w,n)+df(B,w,n)<=df(A|B,w,n)+df(A&B,w,n)
 return len(M)
def exhaustive():
 O=range(3); N=list(ps(range(4))); c=m=0
 for ws in product((1,2),repeat=4):
  w=dict(zip(O,map(Fraction,ws)))
  for ns in product(N,repeat=3): m+=verify(O,w,dict(zip(O,ns))); c+=1
 return c,m
def fixture():
 d=json.loads(FIXTURE.read_text()); O=tuple(map(str,d['deficientOwnerShore'])); w={a:Fraction(d['old']['demandByOwner'][a]) for a in O}; cap={tuple(map(int,k.split(','))):int(v) for k,v in d['sourceCellCapacity'].items()}; n={a:frozenset((tuple(c),h) for c in d['eligibleCellsByOwner'][a] for h in range(cap[tuple(c)])) for a in O}; A=frozenset(O); assert minimal(A,w,n); verify(O,w,n); delta=df(A,w,n); q={}
 for a in O:
  q[a]={'demand':str(w[a]),'neighbors':len(n[a]),'private':len(nb(A,n)-nb(A-{a},n)),'private_bound':str(w[a]-delta),'deletion_slack':str(len(nb(A-{a},n))-dem(A-{a},w))}
 return {'shore':sorted(O),'demand':str(dem(A,w)),'sources':len(nb(A,n)),'defect':str(delta),'owners':q}
if __name__=='__main__':
 c,m=exhaustive(); print(json.dumps({'arithmetic':'Fraction/integer only','abstract_instances':c,'minimal_shores_checked':m,'fixture':fixture(),'fixture_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest()},indent=2,sort_keys=True))

