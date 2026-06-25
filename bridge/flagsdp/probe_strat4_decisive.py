#!/usr/bin/env python3
"""DECISIVE Strategy-4 test: the spectral mechanism for QFC25.

Established (prior probe):
 - rho <= Gamma/(25m) is FALSE (K23-N13: rho=4/3 > 1). So the L2 unit-geodesic spread
   does NOT dominate rho. The non-L1 worst metric ell can beat the unit metric.
 - QFC25 (rho <= N^2/(25m)) holds with slack on obstructions.

The spectral route must therefore bound the worst-metric congestion rho directly.
Multicommodity flow-cut duality: rho = max_{ell>=0} sum_M d_ell(u,v) / sum_B ell_b.
The classical Rayleigh/spectral bound on rho (Leighton-Rao / spectral) is:
     rho <= O(log N) * (sparsest cut of (B with demands M))^{-1}  -- TOO WEAK (log N).
We want the density factor N^2/(25m) to REPLACE the log N.

DECISIVE TEST. The spectral certificate that WOULD prove QFC25 with the right constant:
 Define the demand graph H on V with an edge for each bad pair uv in M (the M-graph).
 The flow-cut bound (Leighton-Rao spectral form):
     rho  <=  C * max_S  (e_M(S,~S)) / (e_B(S,~S))    [the "sparsity" of B vs demands M]
 By CD/(Sep), e_M(S,~S) <= e_B(S,~S) for ALL S, so the sparsity ratio <= 1, giving rho<=C.
 The flow-cut GAP C is the multiplicative loss. For general graphs C=Theta(log N).
 QFC25 says C can be taken <= max{1, N^2/(25m)} HERE (triangle-free).

So the decisive quantity is the FLOW-CUT GAP of the (B, demands=M) instance:
     gap := rho / (min cut-ratio)  where min cut-ratio = min_S e_B(S,~S)/e_M(S,~S) >= 1 by CD.
 Equivalently, since CD gives min cut-ratio>=1, we test:  is rho itself <= N^2/(25m), and how
 does rho compare to log N (to see if the gap is genuinely sub-logarithmic here)?

We compute, per triangle-free obstruction instance:
   rho, the flow-cut gap = rho / sparsity^{-1}, log2(N), and N^2/(25m),
to confirm: (i) CD => sparsity-ratio>=1 (cut side gives rho<=gap), (ii) the gap stays
BELOW N^2/(25m), NOT growing like log N -- the heart of why Strategy 4's density factor works.
"""
import itertools, math
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N,A): return [set(v for v in range(N) if (A[u]>>v)&1) for u in range(N)]
def maxcut(N,adj):
    best=-1; bs=None
    for mask in range(1<<(N-1)):
        side=[(mask>>u)&1 for u in range(N)]
        c=sum(1 for u in range(N) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; bs=side
    return best,bs
def rho_mcf(N,adjB,demands):
    Be=sorted(set(tuple(sorted((u,v))) for u in range(N) for v in adjB[u] if v>u))
    nB=len(Be)
    if nB==0 or not demands: return 0.0
    arcs=[]
    for (x,y) in Be: arcs.append((x,y)); arcs.append((y,x))
    nA=len(arcs); arc_idx={a:i for i,a in enumerate(arcs)}; K=len(demands)
    def fvar(k,ai): return k*nA+ai
    nf=K*nA; KAP=nf; nvar=nf+1
    c=np.zeros(nvar); c[KAP]=1.0
    A_eq=[]; b_eq=[]
    for k,(s,t) in enumerate(demands):
        for v in range(N):
            row=np.zeros(nvar)
            for ai,(a,b) in enumerate(arcs):
                if a==v: row[fvar(k,ai)]+=1.0
                if b==v: row[fvar(k,ai)]-=1.0
            A_eq.append(row); b_eq.append(1.0 if v==s else (-1.0 if v==t else 0.0))
    A_ub=[]; b_ub=[]
    for ei,(x,y) in enumerate(Be):
        row=np.zeros(nvar); a1=arc_idx[(x,y)]; a2=arc_idx[(y,x)]
        for k in range(K): row[fvar(k,a1)]+=1.0; row[fvar(k,a2)]+=1.0
        row[KAP]=-1.0; A_ub.append(row); b_ub.append(0.0)
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),
                bounds=[(0,None)]*nf+[(0,None)],method="highs")
    return res.fun

def min_cut_ratio(N,adjB,M):
    """min_S e_B(S,~S)/e_M(S,~S) over S with e_M(S,~S)>0 (the sparsity; CD => >=1)."""
    best=float('inf'); witnessed=False
    Mset=M
    for mask in range(1,1<<N):
        S=set(u for u in range(N) if (mask>>u)&1)
        eM=sum(1 for (u,v) in Mset if (u in S)!=(v in S))
        if eM==0: continue
        eB=sum(1 for u in range(N) for v in adjB[u] if v>u and ((u in S)!=(v in S)))
        r=eB/eM; witnessed=True
        if r<best: best=r
    return best if witnessed else float('inf')

def main():
    def petersen():
        verts=list(itertools.combinations(range(5),2)); A=[0]*10
        for i,a in enumerate(verts):
            for j,b in enumerate(verts):
                if i<j and not set(a)&set(b): A[i]|=1<<j; A[j]|=1<<i
        return 10,A
    def c5n(k):
        N=5*k; A=[0]*N; part=lambda v:v//k
        for u in range(N):
            for v in range(u+1,N):
                if (part(u)-part(v))%5 in (1,4): A[u]|=1<<v; A[v]|=1<<u
        return N,A
    def gpt_k23():
        N=13; A=[0]*N
        def add(u,v): A[u]|=1<<v; A[v]|=1<<u
        for i in (0,1):
            for j in (2,3,4): add(i,j)
        nxt=5
        for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
            a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
        return N,A
    insts=[(petersen,"Petersen"),(gpt_k23,"K23-N13"),(lambda:c5n(1),"C5[1]"),
           (lambda:c5n(2),"C5[2]"),(lambda:c5n(3),"C5[3]")]
    print("=== DECISIVE: rho vs cut-sparsity (CD), flow-cut gap, vs density bound & log N ===")
    print(f"{'label':12s} {'N':>2s} {'m':>2s} {'rho':>6s} {'minCutRatio':>11s} {'gap=rho*ratio':>13s} {'N2/25m':>7s} {'log2N':>6s}")
    for f,lab in insts:
        N,A=f(); adj=adjset(N,A)
        edges=[frozenset((u,v)) for u in range(N) for v in adj[u] if v>u]
        mc,side=maxcut(N,adj)
        M=[tuple(sorted((u,v))) for u in range(N) for v in adj[u] if v>u and side[u]==side[v]]
        adjB=[set() for _ in range(N)]
        for u in range(N):
            for v in adj[u]:
                if side[u]!=side[v]: adjB[u].add(v)
        m=len(M)
        if m==0: continue
        rho=rho_mcf(N,adjB,M)
        mcr=min_cut_ratio(N,adjB,M)
        gap=rho*mcr   # rho / (1/mcr) = rho*mcr ; the multiplicative flow-cut gap
        bound=max(1.0,N*N/(25.0*m))
        print(f"{lab:12s} {N:2d} {m:2d} {rho:6.3f} {mcr:11.4f} {gap:13.4f} {bound:7.3f} {math.log2(N):6.3f}")
    print("\nINTERPRETATION: minCutRatio>=1 confirms CD/(Sep) (cut side controls rho). The flow-cut")
    print("gap = rho*minCutRatio is the multiplicative loss the density factor must absorb. If gap")
    print("stays well below N^2/25m AND does not grow with log N, the spectral mechanism is plausible.")
    print("DONE")

if __name__=="__main__": main()
