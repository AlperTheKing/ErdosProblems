#!/usr/bin/env python3
"""STRATEGY C probe: resistance / spectral interpretation of Gamma = sum_{uv in M}(d_B(u,v)+1)^2.

Goal: find a SPECTRAL/METRIC quadratic form Q on the bipartite graph B whose value
(i) upper-bounds Gamma, (ii) is provably <= N^2 from B bipartite+triangle-free, and
(iii) is TIGHT at C5[q]. Test several candidate spectral objects and report, per instance:
  - Gamma, N, Gamma/N^2
  - For each bad edge: d_B(u,v) (graph dist in B), R_B(u,v) (effective resistance in B),
    and the relation ell^2 = (d_B+1)^2 vs resistance.
  - Sum of squared B-distances vs sum over ALL pairs; spectral gap lambda_2(L_B).
  - The KEY candidate: A "Dirichlet/coarea" identity.  For unit length on B edges,
    d_B(u,v) = number of cut-levels of a shortest-path metric separating u,v. We test
    whether  sum_{uv in M} d_B(u,v)  relates to a sum over B-edge "level cuts" via CD.

We focus on the named tight/obstruction instances: C5[q], C_{2k+1}, Petersen, K23-N13, theta46.
"""
import itertools, math
import numpy as np
from collections import deque

# ---------- named graphs ----------
def c5_blowup(q):
    # 5 parts of size q, part i fully joined to part i+1 (mod 5). Triangle-free.
    N = 5*q
    part = lambda i: list(range(i*q, (i+1)*q))
    adj = [[0]*N for _ in range(N)]
    for i in range(5):
        for a in part(i):
            for b in part((i+1)%5):
                adj[a][b]=adj[b][a]=1
    return N, adj

def odd_cycle(L):
    adj=[[0]*L for _ in range(L)]
    for i in range(L):
        adj[i][(i+1)%L]=adj[(i+1)%L][i]=1
    return L, adj

def petersen():
    N=10
    edges=[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),
           (5,7),(7,9),(9,6),(6,8),(8,5)]
    adj=[[0]*N for _ in range(N)]
    for u,v in edges: adj[u][v]=adj[v][u]=1
    return N,adj

def theta46():
    # bad edge u-v plus two B-paths of lengths 4 and 6 between u,v (even). One bad edge.
    # vertices: 0=u,1=v ; path A length4: u-a1-a2-a3-v ; path B length6: u-b1..b5-v
    edges=[]
    u,v=0,1
    a=[2,3,4]            # a1,a2,a3
    b=[5,6,7,8,9]        # b1..b5
    pA=[u]+a+[v]
    pB=[u]+b+[v]
    for i in range(len(pA)-1): edges.append((pA[i],pA[i+1]))
    for i in range(len(pB)-1): edges.append((pB[i],pB[i+1]))
    edges.append((u,v))  # bad edge
    N=10
    adj=[[0]*N for _ in range(N)]
    for x,y in edges: adj[x][y]=adj[y][x]=1
    return N,adj

def k23_n13():
    # GPT Section-2 obstruction: K_{2,3} with within-part pairs subdivided. 13 vertices, m=4.
    # Build per the memory description: U={2 vtx}, W={3 vtx}; 4 within-part pairs each
    # subdivided x-a-b(M)-y. We just need SOME tri-free graph w/ nu*<tau; use explicit edges.
    # Use the recorded structure loosely; if not matching, it still serves as a stress graph.
    # Simpler: take K_{2,3} core (bipartite, no bad edges) -> not useful. We instead skip exact
    # reconstruction and rely on the enumerated tri-free graphs below for obstructions.
    return None

# ---------- cut / B / M ----------
def all_maxcuts(n, adj):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and side[u]!=side[v])
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts

def build_B_M(n, adj, side):
    adjB=[set() for _ in range(n)]
    M=[]
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                if side[u]!=side[v]:
                    adjB[u].add(v); adjB[v].add(u)
                else:
                    M.append((u,v))
    return adjB, M

def bdist_all(n, adjB):
    D=[[-1]*n for _ in range(n)]
    for s in range(n):
        D[s][s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for w in adjB[u]:
                if D[s][w]<0:
                    D[s][w]=D[s][u]+1; q.append(w)
    return D

def laplacian_B(n, adjB):
    L=np.zeros((n,n))
    for u in range(n):
        for w in adjB[u]:
            if w>u:
                L[u][u]+=1; L[w][w]+=1; L[u][w]-=1; L[w][u]-=1
    return L

def eff_resistance_matrix(n, adjB, comp):
    """effective resistance within a connected component 'comp' (list of vertices)."""
    idx={v:i for i,v in enumerate(comp)}
    k=len(comp)
    L=np.zeros((k,k))
    for u in comp:
        for w in adjB[u]:
            if w in idx and w>u:
                iu,iw=idx[u],idx[w]
                L[iu][iu]+=1;L[iw][iw]+=1;L[iu][iw]-=1;L[iw][iu]-=1
    # pseudoinverse
    Lp=np.linalg.pinv(L)
    R=np.zeros((k,k))
    for i in range(k):
        for j in range(k):
            R[i][j]=Lp[i][i]+Lp[j][j]-2*Lp[i][j]
    return R, idx

def components(n, adjB):
    seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        comp=[]; q=deque([s]); seen[s]=True
        while q:
            u=q.popleft(); comp.append(u)
            for w in adjB[u]:
                if not seen[w]: seen[w]=True; q.append(w)
        comps.append(comp)
    return comps

def analyze(name, n, adj, restrict_side=None):
    mc,cuts=all_maxcuts(n,adj)
    # pick max cut minimizing Gamma (struct), as in verify_cosystole
    best=None
    for side in cuts:
        adjB,M=build_B_M(n,adj,side)
        D=bdist_all(n,adjB)
        G=0; ok=True; details=[]
        for (u,v) in M:
            d=D[u][v]
            if d<0 or d%2 or d<4: ok=False
            ell=(d+1)
            G+=ell*ell
            details.append((u,v,d))
        if best is None or G<best[0]:
            best=(G,M,adjB,D,details,side,ok)
    G,M,adjB,D,details,side,ok=best
    comps=components(n,adjB)
    # effective resistance per bad edge (within its component)
    comp_of={}
    for ci,comp in enumerate(comps):
        for v in comp: comp_of[v]=ci
    Rrows=[]
    for ci,comp in enumerate(comps):
        if len(comp)<2: continue
        R,idx=eff_resistance_matrix(n,adjB,comp)
        for (u,v) in M:
            if u in idx and v in idx:
                Rrows.append((u,v,D[u][v], R[idx[u]][idx[v]]))
    # spectral gap of B (per largest component)
    big=max(comps,key=len)
    R,idx=eff_resistance_matrix(n,adjB,big) if len(big)>=2 else (None,None)
    Lbig=np.zeros((len(big),len(big)))
    iv={v:i for i,v in enumerate(big)}
    for u in big:
        for w in adjB[u]:
            if w in iv and w>u:
                a,b=iv[u],iv[w]; Lbig[a][a]+=1;Lbig[b][b]+=1;Lbig[a][b]-=1;Lbig[b][a]-=1
    ev=np.linalg.eigvalsh(Lbig)
    lam2=ev[1] if len(ev)>1 else 0.0
    lammax=ev[-1]
    print(f"\n=== {name}: N={n}, |M|={len(M)}, Gamma={G}, Gamma/N^2={G/(n*n):.4f}, "
          f"B-comp sizes={sorted(len(c) for c in comps)}")
    print(f"    B big-comp: |V|={len(big)}, lambda2(L_B)={lam2:.4f}, lambda_max={lammax:.4f}")
    print(f"    bad-edge (u,v,d_B,R_eff):")
    for (u,v,d,r) in Rrows[:12]:
        print(f"      ({u},{v}) d_B={d} R_eff={r:.4f}  d_B*R_eff={d*r:.4f}  (d+1)^2={(d+1)**2}")
    # KEY tests on big component (single-component-dominated instances):
    nb=len(big)
    # sum of effective resistances among bad edges
    if Rrows:
        sumR=sum(r for (_,_,_,r) in Rrows)
        sumdR=sum(d*r for (_,_,d,r) in Rrows)
        print(f"    sum R_eff(M)={sumR:.4f}, sum d_B*R_eff={sumdR:.4f}, N={n}")
    return G, n

if __name__=="__main__":
    print("STRATEGY C spectral/resistance probe")
    # tight families
    for q in [1,2,3]:
        N,adj=c5_blowup(q); analyze(f"C5[{q}]",N,adj)
    for L in [5,7,9]:
        N,adj=odd_cycle(L); analyze(f"C_{L}",N,adj)
    N,adj=petersen(); analyze("Petersen",N,adj)
    N,adj=theta46(); analyze("theta46",N,adj)
    print("\nDONE")
