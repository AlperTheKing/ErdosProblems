"""Erdos #1159 small-case census: for the Desarguesian projective plane PG(2,q),
compute minC(q) = min over point-sets S of  max_line |S ∩ line|,  subject to
every line meeting S (1 <= |S∩l|) — i.e. the minimum max-line-intersection of a
blocking set. Verifiable finite computation. q=2,3,4 by exact search; reports
min-C and a witness set.
"""
import itertools, sys
def pg(q):
    # points = normalized nonzero vectors in F_q^3 (first nonzero coord =1)
    pts=[]
    for v in itertools.product(range(q),repeat=3):
        if v==(0,0,0): continue
        # normalize: first nonzero entry to 1 (q prime so inverse = pow trick; q in {2,3,4} -> 2,3 prime, 4=GF(4))
        pts.append(v)
    # dedup projectively
    def norm(v):
        for x in v:
            if x!=0:
                inv=pow(x,q-2,q) if q in (2,3,5,7) else None
                if inv is None: return None
                return tuple((c*inv)%q for c in v)
        return None
    seen={}; P=[]
    for v in pts:
        n=norm(v)
        if n and n not in seen: seen[n]=len(P); P.append(n)
    # lines: a line is {points p : a·p=0} for a nonzero covector a (projective)
    def dot(a,p): return sum(x*y for x,y in zip(a,p))%q
    Lset=set()
    for a in pts:
        na=norm(a)
        if not na: continue
        line=frozenset(seen[p] for p in P if dot(na,p)==0)
        if line: Lset.add(line)
    return P, [set(l) for l in Lset]
def minC(q):
    P,L=pg(q); n=len(P)
    if q in (2,3,4): assert n==q*q+q+1, (q,n)
    best=None; witness=None
    # search subsets by increasing size won't directly minimize max-intersection;
    # iterate all subsets (q=2:128, q=3:8192, q=4:2^21=2.1M) and track min max-int among blocking sets
    for mask in range(1,1<<n):
        S=[i for i in range(n) if mask>>i&1]
        Sset=set(S)
        mx=0; ok=True
        for l in L:
            c=len(l & Sset)
            if c==0: ok=False; break
            if c>mx: mx=c
        if ok and (best is None or mx<best):
            best=mx; witness=S
            if best==1: break  # cannot do better than 1 (some line would need a point)
    return n,len(L),best,witness
for q in (2,3,4):
    n,nl,b,w=minC(q)
    print(f"q={q} PG(2,{q}): points={n} lines={nl}  minC={b}  |witness|={len(w)} witness={w}",flush=True)
