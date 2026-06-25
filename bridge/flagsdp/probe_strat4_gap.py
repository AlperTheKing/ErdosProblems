#!/usr/bin/env python3
"""Strategy-4: does the density factor N^2/(25m) come from a SPECTRAL GAP of B?

Critical test of the spectral mechanism. The worst case for MT25 is when the
shortest-path metric d^B_ell is FAR from L1 (non-L1, odd-K5 phenomenon). For an
expander B this distortion is Theta(log N), unbounded. The hope of Strategy 4:
triangle-free + cycle-degree (6) forces a relation

      m * rho  <=  N^2 / 25        (equivalently QFC25 in the m<=N^2/25 regime)

We test whether rho can be UPPER bounded by a spectral surrogate of B:
   - lambda_2-based Cheeger / sparsest cut of B
   - the "spread" sum_{uv in M} d_B(u,v)^2 (the Gamma invariant, ell=1 case)
and whether the product (#bad edges m) x (spectral diameter surrogate) stays <= N^2/25.

Key diagnostic: the Gamma invariant Gamma = sum_{uv in M} (d_B(u,v)+1)^2 <= N^2 (the
cut-geometry breakthrough). If Gamma<=N^2 always, then since each term >=25, m<=N^2/25.
We re-verify Gamma<=N^2 and compute how rho relates to Gamma/(25m) (the per-edge spectral
length squared). This tells us whether a Rayleigh/Cauchy bound on Gamma gives MT25.
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
def bfs_dist(N,adjB,s):
    d=[-1]*N; d[s]=0; q=[s]
    while q:
        nq=[]
        for u in q:
            for v in adjB[u]:
                if d[v]<0: d[v]=d[u]+1; nq.append(v)
        q=nq
    return d

def gamma_invariant(N,adjB,M):
    """Gamma = sum_{uv in M} (d_B(u,v)+1)^2 = sum ell(uv)^2."""
    G=0.0; ok=True
    for (u,v) in M:
        d=bfs_dist(N,adjB,u)[v]
        if d<0:  # not same component -> shouldn't happen under max-cut
            ok=False; continue
        ell=d+1
        G+=ell*ell
    return G, ok

def rho_mcf(N,adjB,demands):
    Bedges=sorted(set(frozenset((u,v)) for u in range(N) for v in adjB[u] if v>u),key=lambda e:tuple(sorted(e)))
    Be=[tuple(sorted(e)) for e in Bedges]; nB=len(Be)
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

def process(N,A,label,store):
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
    G,ok=gamma_invariant(N,adjB,M)
    rho=rho_mcf(N,adjB,M)
    bound=max(1.0,N*N/(25.0*m))
    # Two candidate spectral/geometric upper bounds on rho:
    #  (a) Gamma/(25m): average squared length /25 -- the L2 "spread" surrogate
    #  (b) max_uv ell(uv)=diam-type
    a_surr=G/(25.0*m)
    maxell=max((bfs_dist(N,adjB,u)[v]+1) for (u,v) in M)
    store.append((label,N,m,rho,bound,G,N*N,a_surr,maxell,ok))

def main():
    named=[]
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
    store=[]
    for f,lab in [(petersen,"Petersen"),(gpt_k23,"K23-N13"),(lambda:c5n(1),"C5[1]"),
                  (lambda:c5n(2),"C5[2]"),(lambda:c5n(3),"C5[3]")]:
        N,A=f(); process(N,A,lab,store)
    print("=== Gamma invariant + rho vs spectral surrogates ===")
    print(f"{'label':14s} {'N':>2s} {'m':>2s} {'rho':>6s} {'N2/25m':>7s} {'Gamma':>6s} {'N^2':>5s} {'G/25m':>6s} {'maxL':>4s}")
    for (lab,N,m,rho,bound,G,N2,a,maxell,ok) in store:
        flag = "" if G<=N2+1e-9 else "  <<< Gamma>N^2!"
        print(f"{lab:14s} {N:2d} {m:2d} {rho:6.3f} {bound:7.3f} {G:6.1f} {N2:5d} {a:6.3f} {maxell:4d}{flag}")
    # exhaustive: Gamma<=N^2 and rho<=Gamma/(25m)? and rho<=bound?
    print("\n=== exhaustive: Gamma<=N^2 ? and is rho<=Gamma/(25m)? ===")
    for N in [5,6,7,8]:
        states=fe.enumerate_graphs(N,triangle_free=True)
        gam_viol=0; rho_le_a=0; tot=0; worst_rho_over_a=0.0; worst_gamma_ratio=0.0
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
            tot+=1
            G,ok=gamma_invariant(n,adjB,M)
            if G>n*n+1e-9: gam_viol+=1
            worst_gamma_ratio=max(worst_gamma_ratio,G/(n*n))
            rho=rho_mcf(n,adjB,M)
            a=G/(25.0*m)
            if rho<=a+1e-7: rho_le_a+=1
            if a>1e-12: worst_rho_over_a=max(worst_rho_over_a,rho/a)
        print(f"  N={N}: {tot} M>0 graphs | Gamma>N^2 viol={gam_viol} (worst Gamma/N^2={worst_gamma_ratio:.4f}) | "
              f"rho<=Gamma/25m holds {rho_le_a}/{tot} (worst rho/(G/25m)={worst_rho_over_a:.4f})")
    print("DONE")

if __name__=="__main__": main()
