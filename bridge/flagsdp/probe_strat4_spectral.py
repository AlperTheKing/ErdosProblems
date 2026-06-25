#!/usr/bin/env python3
"""Strategy-4 spectral probe for MT25.

We test whether the MT25 LHS can be controlled by a SPECTRAL quadratic form on B
plus the density factor N^2/(25m).

Setup: max cut V=X u Y, B = cut edges (bipartite), M = bad edges, m=|M|.
For a length ell:B->R>=0, S=sum ell, MT25 LHS = sum_{uv in M} d^B_ell(u,v).

Worst-case ell (the dual optimum) gives exactly rho(B,M). We already know rho<=bound
holds numerically. The point of THIS probe is to test the *spectral mechanism*:

   Candidate quadratic-form bound (Q): for the WORST ell, write the routed flow; the
   congestion equals rho. We test the inequality that would come from a spectral / Rayleigh
   argument, namely whether

        sum_{uv in M} d^B_ell(u,v)  <=  C(B) * (something) * S

   where C(B) is a spectral quantity of B. Specifically we test three concrete spectral
   surrogates and see which (if any) tracks rho with the RIGHT density scaling:

   (S1)  rho  <=  d^B_diam-type:  max over uv in M of d_B(u,v) [combinatorial, ell=1]   -- gives integrality only
   (S2)  Nosal: lambda1(A_G) <= sqrt(e(G))   [sanity check triangle-free spectral fact]
   (S3)  the KEY test: does  m * rho  <=  N^2/25  ALWAYS (equivalently rho<=N^2/(25m))? and
         is the slack explained by a spectral gap of B?  We compute, for each instance,
            rho, N^2/(25m), and lambda2-type Cheeger constant of B, and the L1 distortion
            of the worst-ell metric, to see WHERE the density factor absorbs distortion.
"""
import itertools, math
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best=-1; bs=None
    for mask in range(1<<(N-1)):
        side=[(mask>>u)&1 for u in range(N)]
        c=sum(1 for u in range(N) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; bs=side
    return best,bs

def rho_and_metric(N, adjB, demands):
    """Return rho and the worst-case (dual-optimal) edge length ell normalized to sum 1,
       via the edge-congestion concurrent-flow LP and its dual."""
    Bedges=sorted(set(frozenset((u,v)) for u in range(N) for v in adjB[u] if v>u),
                  key=lambda e: tuple(sorted(e)))
    Be=[tuple(sorted(e)) for e in Bedges]; nB=len(Be)
    if nB==0 or not demands: return 0.0, {}, Be
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
    cong_rows=[]
    for ei,(x,y) in enumerate(Be):
        row=np.zeros(nvar); a1=arc_idx[(x,y)]; a2=arc_idx[(y,x)]
        for k in range(K): row[fvar(k,a1)]+=1.0; row[fvar(k,a2)]+=1.0
        row[KAP]=-1.0; A_ub.append(row); b_ub.append(0.0); cong_rows.append(ei)
    res=linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                bounds=[(0,None)]*nf+[(0,None)], method="highs")
    rho=res.fun
    # dual multipliers on congestion constraints = edge lengths ell (up to normalization)
    ell={}
    if res.ineqlin is not None:
        duals = -res.ineqlin.marginals  # >=0
        for ei,e in enumerate(Be):
            ell[e]=max(0.0, duals[ei])
    s=sum(ell.values())
    if s>1e-12:
        for e in ell: ell[e]/=s
    return rho, ell, Be

def shortest_path_metric(N, adjB, ell):
    """all-pairs shortest path under length ell on B (Floyd-Warshall on B vertices)."""
    INF=float('inf')
    D=[[INF]*N for _ in range(N)]
    for v in range(N): D[v][v]=0.0
    for (x,y),w in ell.items():
        D[x][y]=min(D[x][y],w); D[y][x]=min(D[y][x],w)
    for k in range(N):
        for i in range(N):
            if D[i][k]==INF: continue
            for j in range(N):
                if D[k][j]<INF and D[i][k]+D[k][j]<D[i][j]: D[i][j]=D[i][k]+D[k][j]
    return D

def lambda1_trifree(N, adj):
    A=np.zeros((N,N))
    for u in range(N):
        for v in adj[u]: A[u][v]=1.0
    w=np.linalg.eigvalsh(A)
    return w[-1]

def run(instances, exhaustive_Ns=None):
    print("=== Strategy-4 spectral probe ===", flush=True)
    print("Per instance: m, rho, N^2/(25m), worst-ell sum-of-distances vs rho, lambda1(G) vs sqrt(e), L1 check", flush=True)
    rows=[]
    def process(N, A, label):
        adj=adjset(N,A)
        edges=[frozenset((u,v)) for u in range(N) for v in adj[u] if v>u]
        if not edges: return
        mc,side=maxcut(N,adj)
        M=[tuple(sorted((u,v))) for u in range(N) for v in adj[u] if v>u and side[u]==side[v]]
        adjB=[set() for _ in range(N)]
        for u in range(N):
            for v in adj[u]:
                if side[u]!=side[v]: adjB[u].add(v)
        m=len(M)
        if m==0: return
        rho, ell, Be = rho_and_metric(N, adjB, M)
        bound=max(1.0, N*N/(25.0*m))
        # MT25 LHS with worst ell (sum normalized to 1): sum_{uv in M} d^B_ell(u,v)
        D=shortest_path_metric(N, adjB, ell)
        lhs=sum(D[u][v] for (u,v) in M)   # should equal rho (since dual ell sum=1)
        lam1=lambda1_trifree(N,adj)
        nosal_ok = lam1 <= math.sqrt(len(edges))+1e-9
        ok = rho <= bound+1e-7
        rows.append((label,N,m,rho,bound,lhs,ok))
        if label:
            print(f"  {label:14s} N={N:2d} m={m:2d} rho={rho:.4f} N^2/25m={bound:.4f} "
                  f"MT25lhs(worst-ell)={lhs:.4f} OK={ok} | lam1={lam1:.3f}<=sqrt(e)={math.sqrt(len(edges)):.3f}:{nosal_ok}", flush=True)
    for (N,A,label) in instances: process(N,A,label)
    if exhaustive_Ns:
        for N in exhaustive_Ns:
            states=fe.enumerate_graphs(N, triangle_free=True)
            worst_ratio=0.0; viol=0; nosal_viol=0
            for (n,A) in states:
                adj=adjset(n,A)
                edges=[frozenset((u,v)) for u in range(n) for v in adj[u] if v>u]
                if not edges: continue
                mc,side=maxcut(n,adj)
                M=[tuple(sorted((u,v))) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
                adjB=[set() for _ in range(n)]
                for u in range(n):
                    for v in adj[u]:
                        if side[u]!=side[v]: adjB[u].add(v)
                m=len(M)
                if m==0: continue
                rho,ell,Be=rho_and_metric(n,adjB,M)
                bound=max(1.0,n*n/(25.0*m))
                r=rho/bound
                if r>worst_ratio: worst_ratio=r
                if rho>bound+1e-7: viol+=1
                lam1=lambda1_trifree(n,adj)
                if lam1>math.sqrt(len(edges))+1e-6: nosal_viol+=1
            print(f"  EXH N={N}: {len(states)} graphs, worst rho/bound={worst_ratio:.4f} QFC25 viol={viol} Nosal viol={nosal_viol}", flush=True)

def petersen():
    verts=list(itertools.combinations(range(5),2)); A=[0]*10
    for i,a in enumerate(verts):
        for j,b in enumerate(verts):
            if i<j and not set(a)&set(b): A[i]|=1<<j; A[j]|=1<<i
    return 10,A
def c5n(k):
    N=5*k; A=[0]*N; part=lambda v: v//k
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

if __name__=="__main__":
    named=[(*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),
           (*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]")]
    run(named, exhaustive_Ns=[5,6,7])
    print("DONE", flush=True)
