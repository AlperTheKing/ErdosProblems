"""Check the J_t dilution claim against the SHARP CUT inequality form, which is what
the referee (strategy A) says is the surviving-but-refuted crux.

The two candidate "open lemmas" differ and it matters which one is being tested:

  (Q-RATE)  single-rate congestion:   rho* * Gamma <= N^2      [DILUTION-VULNERABLE: refuted by J_t]
  (Q-CUT)   per-cut sharp inequality:  for every B-edge cut F,  X_F/|F| <= N^2/(25 t)
            where t = perimeter ratio = (sum_e ell_e)/m  (a GLOBAL scalar, not local),
            X_F = sum_e (min #F-crossings on a B-geodesic of e).

The referee's J_t counterexample (K23 gadget bridged to a big balanced C5[t] block) attacks (Q-RATE):
local congestion rho* stays high while Gamma,m grow additively, so rho*Gamma overshoots.

KEY QUESTION the lead must resolve: does the SAME J_t also break (Q-CUT)?  If the cut inequality has the
GLOBAL t in the denominator (t grows when you add the big balanced block), the denominator grows too and may
absorb the dilution. We test the structural fact: is X_F/|F| <= N^2/(25 t) preserved under disjoint union /
bridging with a balanced C5[q] block?

We can't easily build J_t here, but we CAN test the decisive sub-question on the available extremals:
whether X_F/|F| (max over cuts) for C5[q] equals N^2/(25 t) with equality (t=1 there, so bound = N^2/25,
and X_F/|F| should hit (N/5)^2... ) -- i.e. whether the constant/normalization is even internally consistent.

We directly recompute, for C5[q] and K23 and odd cycles, the quantity max_F X_F/|F| via the brute cut search
already in cut_inequality_verify, and compare to N^2/(25 t).
"""
import numpy as np
from itertools import combinations
from collections import deque

def c5q(q):
    """Balanced blow-up C5[q]: 5 parts of size q, part i ~ part i+1 mod 5."""
    N=5*q
    part=[i//q for i in range(N)]
    adj=[[] for _ in range(N)]
    E=[]
    for i in range(N):
        for j in range(i+1,N):
            if (part[i]-part[j])%5 in (1,4):
                adj[i].append(j); adj[j].append(i); E.append((i,j))
    return N,adj,E,part

def odd_cycle(L):
    N=L; adj=[[] for _ in range(N)]; E=[]
    for i in range(N):
        j=(i+1)%N
        adj[i].append(j); adj[j].append(i); E.append((min(i,j),max(i,j)))
    return N,adj,E

def maxcut(N,E):
    best=-1;bs=None
    for mask in range(1<<(N-1)):
        side=[(mask>>i)&1 for i in range(N)]
        v=sum(1 for (a,b) in E if side[a]!=side[b])
        if v>best:best=v;bs=side[:]
    return best,bs

def bfs(N,adjB,s):
    d=[-1]*N;d[s]=0;q=deque([s])
    while q:
        u=q.popleft()
        for v in adjB[u]:
            if d[v]<0:d[v]=d[u]+1;q.append(v)
    return d

def geodesic_min_cross(N,adjB,u,v,Fset):
    """min over B-geodesics u..v of #F-edges used. BFS layered DAG + DP."""
    d=bfs(N,adjB,u)
    if d[v]<0: return None
    # DP over layers: best[x] = min F-crossings on a shortest u->x path
    INF=10**9
    best=[INF]*N; best[u]=0
    order=sorted(range(N),key=lambda x:d[x] if d[x]>=0 else INF)
    for x in order:
        if best[x]==INF: continue
        for y in adjB[x]:
            if d[y]==d[x]+1:
                w=1 if (frozenset((x,y)) in Fset) else 0
                if best[x]+w<best[y]: best[y]=best[x]+w
    return best[v]

def analyze(N,adj,E,label):
    mc,side=maxcut(N,E)
    Bset=set(); M=[]
    for (a,b) in E:
        if side[a]!=side[b]: Bset.add(frozenset((a,b)))
        else: M.append((a,b))
    if not M:
        print(f"{label}: no bad edges (perfect cut)"); return
    adjB=[[] for _ in range(N)]
    for fe in Bset:
        a,b=tuple(fe); adjB[a].append(b); adjB[b].append(a)
    ells=[]
    for (a,b) in M:
        d=bfs(N,adjB,a); ells.append(d[b]+1)
    m=len(M); S1=sum(ells); t=S1/m; Gamma=sum(l*l for l in ells)
    # brute max over vertex-bipartition cuts F=E_B(W,~W) of X_F/|F|
    Blist=list(Bset)
    bestratio=0.0; bestW=None
    rng=range(1,1<<(N-1)) if N<=14 else []
    for wm in rng:
        W=set(i for i in range(N) if (wm>>i)&1)
        F=set(fe for fe in Bset if (len(fe & W)==1))
        if not F: continue
        X=0; ok=True
        for (a,b) in M:
            c=geodesic_min_cross(N,adjB,a,b,F)
            if c is None: ok=False;break
            X+=c
        if not ok: continue
        r=X/len(F)
        if r>bestratio: bestratio=r; bestW=W
    bound=N*N/(25*t)
    print(f"{label}: N={N} m={m} t={t:.3f} Gamma={Gamma} N^2={N*N} Gamma/N^2={Gamma/(N*N):.3f}")
    print(f"   max_F X_F/|F| = {bestratio:.4f}   vs   N^2/(25 t) = {bound:.4f}   "
          f"{'OK <=' if bestratio<=bound+1e-9 else 'VIOLATION >'}")

if __name__=="__main__":
    print("=== sharp CUT inequality  max_F X_F/|F| <= N^2/(25 t)  on extremals ===")
    for q in [1,2]:
        N,adj,E,part=c5q(q); analyze(N,adj,E,f"C5[{q}]")
    for L in [5,7,9]:
        N,adj,E=odd_cycle(L); analyze(N,adj,E,f"C_{L}")
