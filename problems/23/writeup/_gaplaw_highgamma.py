"""Stress-test the gap law  ellmax(w)*R(w) - N <= N^2 - Gamma  (i.e. U) on HIGH-Gamma families
where deficit is small & positive (the real stress regime). Use unbalanced C5/C7 blow-ups (analytic
seam cut) + small tri-free perturbations. Report max ratio (prod-N)/deficit among deficit>0."""
from fractions import Fraction as F
from collections import deque
import itertools, random

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def has_tri(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return True
    return False

# We need the GENUINE gamma-min cut for perturbed graphs -> use brute maxcut (cap N<=16).
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import maxcut_all, gmin, geos

def worstvertex(n,E):
    adj=adj_of(n,E)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    N=n; deficit=N*N-G
    best=None
    for w in range(n):
        R=F(0);L=0
        for (u,v) in M:
            Ps=geos(adj,side,u,v); nf=len(Ps); thru=sum(1 for P in Ps if w in P)
            if thru: R+=F(thru,nf); L=max(L,ell[(u,v)])
        if L==0: continue
        if best is None or L*R>best[0]: best=(L*R,R,L)
    if best is None: return None
    return dict(N=N,deficit=deficit,prod=best[0],K=N+deficit)

def c_blow_parts(m, parts):
    off=[0]
    for s in parts: off.append(off[-1]+s)
    n=off[-1]; E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(parts[i]):
            for b in range(parts[j]):
                E.append((off[i]+a, off[j]+b))
    return n,E

rng=random.Random(7)
worst_ratio=None; nviol=0; nchk=0
def feed(label,n,E):
    global worst_ratio,nviol,nchk
    if n>16: return
    d=worstvertex(n,E)
    if d is None: return
    nchk+=1
    if d['prod']>d['K']: nviol+=1; print("VIOLATION",label,d)
    if d['deficit']>0 and d['prod']>d['N']:
        ratio=F(d['prod']-d['N'], d['deficit'])
        if worst_ratio is None or ratio>worst_ratio[0]: worst_ratio=(ratio,label,d)

# unbalanced C5,C7 blowups
for m in (5,7):
    for parts in itertools.product(range(1,4),repeat=m):
        N=sum(parts)
        if N>16: continue
        feed(f"C{m}{parts}",*c_blow_parts(m,list(parts)))
# perturbations of C5 blowups
for bp in [(2,2,2,2,2),(3,2,2,2,2),(2,3,2,2,2),(3,3,2,2,1),(2,2,2,2,1)]:
    n0,E0=c_blow_parts(5,list(bp))
    if n0>16: continue
    Eset0=set(tuple(sorted(e)) for e in E0)
    for _ in range(800):
        adj=adj_of(n0,E0); Eset=set(Eset0)
        es=list(Eset); rng.shuffle(es)
        for e in es[:rng.randint(0,2)]:
            adj[e[0]].discard(e[1]); adj[e[1]].discard(e[0]); Eset.discard(e)
        non=[(i,j) for i in range(n0) for j in range(i+1,n0) if j not in adj[i]]
        rng.shuffle(non); add=0
        for (i,j) in non:
            if add>=rng.randint(0,2): break
            if adj[i]&adj[j]: continue
            adj[i].add(j); adj[j].add(i); add+=1
        E2=[(a,b) for a in range(n0) for b in adj[a] if b>a]
        if has_tri(n0,adj_of(n0,E2)): continue
        feed(f"pert{bp}",n0,E2)

print(f"checked={nchk} violations(prod>K)={nviol}")
if worst_ratio:
    ratio,label,d=worst_ratio
    print(f"max (prod-N)/deficit among deficit>0 = {float(ratio):.4f}={ratio} @ {label} N={d['N']} deficit={d['deficit']} prod={d['prod']} K={d['K']}")
    print("target for U: ratio<=1 (gap-law). margin factor =",float(1/ratio) if ratio>0 else "inf")
