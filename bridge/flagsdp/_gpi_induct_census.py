#!/usr/bin/env python3
"""
Broader test of the GPI induction step. For each connected-B tri-free max-cut config (census N<=10 via flag_engine
if available; plus Mycielskians), and EACH peel C (shortest geodesic of a bad edge):
  (P0) does G-C satisfy the IH hypotheses?  CD' (cut-dom on survivors), tri-free (automatic), B'-connected per bad comp.
  (P1) BND inequality:  LHS_full - LHS_sub <= (K-K') sum_{V'} phi + K sum_C phi   over many phi>=0.
  (P2) GPI_sub itself:  LHS_sub <= K' sum_{V'} phi    (sanity that IH would hold).
Report worst violations, separating Gamma>=N^2 (the only regime needed) from Gamma<N^2.
We want: does there EXIST a peel for which (P0) holds AND (P1) holds for all phi? If yes for every non-base graph,
the induction closes (modulo proving P1+P0 existence).
"""
import sys, random
from collections import deque
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of, mycielskian

def Bcomp_dist(n, adj, side, banned, s):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d:
                d[v]=d[u]+1; q.append(v)
    return d

def all_geos_banned(n,adj,side,banned,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v] and v not in banned:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return out

def m_phi(geos, phi): return min(sum(phi[v] for v in P) for P in geos)

def gpi_lhs(N,adj,side,M,phi,banned):
    s=0.0
    for (u,v) in M:
        geos=all_geos_banned(N,adj,side,banned,u,v)
        if not geos: return None
        h=len(geos[0]); s+=h*m_phi(geos,phi)
    return s

def cut_dom_survivors(N,adj,side,M,Cset):
    K=[v for v in range(N) if v not in Cset]; m=len(K)
    if m>20: return None
    idx={v:i for i,v in enumerate(K)}; kset=set(K)
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM>dB: return False
    return True

def analyze(name,N,adj,verbose=False):
    E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: return None
    side,G,M=res
    if len(M)<2: return ("base",name,N,len(M),G)
    K=N+N*N-G
    rng=random.Random(999)
    phis=[[rng.random() for _ in range(N)] for _ in range(120)]
    for _ in range(120):
        S=set(rng.sample(range(N), rng.randint(1,N)))
        phis.append([1.0 if v in S else 0.0 for v in range(N)])
    # for each peel record: P0_ok, worst BND viol, worst GPIsub viol
    peels=[]
    for (bu,bv) in M:
        for C in all_shortest_geos(N,adj,side,bu,bv):
            Cset=set(C); h=len(C)
            keep=[v for v in range(N) if v not in Cset]
            if not keep: continue
            Mp=[(a,b) for (a,b) in M if a not in Cset and b not in Cset]
            ok=True; Gp=0
            for (a,b) in Mp:
                d=Bcomp_dist(N,adj,side,Cset,a).get(b,-1)
                if d<0: ok=False; break
                Gp+=(d+1)**2
            cd=cut_dom_survivors(N,adj,side,M,Cset) if ok else None
            Np=N-h; Kp=Np+Np*Np-Gp if ok else None
            P0=bool(ok and (cd is True))
            wbnd=-1e9; wsub=-1e9
            if ok:
                for phi in phis:
                    lf=gpi_lhs(N,adj,side,M,phi,set())
                    ls=gpi_lhs(N,adj,side,Mp,phi,Cset)
                    if lf is None or ls is None: continue
                    sumV=sum(phi); sumC=sum(phi[v] for v in C); sumVp=sumV-sumC
                    wbnd=max(wbnd,(lf-ls)-((K-Kp)*sumVp+K*sumC))
                    wsub=max(wsub, ls - Kp*sumVp)
            peels.append((P0,wbnd,wsub,h,Gp,Kp))
    # does a GOOD peel exist? (P0 ok and BND holds for all sampled phi, i.e. wbnd<=1e-9)
    good=[p for p in peels if p[0] and p[1]<=1e-9]
    any_good=len(good)>0
    worst_bnd_overall=max((p[1] for p in peels if p[0]), default=None)
    return ("nonbase",name,N,len(M),G,K,G>=N*N,any_good,worst_bnd_overall,len(peels),len([p for p in peels if p[0]]))

def run(name,N,adj):
    r=analyze(name,N,adj)
    if r is None: print("%s: no config"%name); return
    if r[0]=="base": print("%s: BASE (beta=%d)"%(r[1],r[3])); return
    _,nm,N,beta,G,K,tight,any_good,wbnd,npeel,nP0=r
    print("%s: N=%d beta=%d Gamma=%d K=%d Gamma>=N^2:%s | GOOD-peel-exists(P0&BND):%s  worstBNDoverP0=%s  peels=%d P0ok=%d"
          %(nm,N,beta,G,K,tight,any_good,("%.4f"%wbnd if wbnd is not None else None),npeel,nP0))

if __name__=="__main__":
    def C5q(q):
        n=5*q
        def vid(i,j): return i*q+j
        side=[0]*n
        for i in range(5):
            for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
        adj=[set() for _ in range(n)]
        for i in range(5):
            for a in range(q):
                for b in range(q):
                    u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
        return n,adj
    for q in (2,3,4): run("C5[%d]"%q,*( (lambda nq: (nq[0],nq[1]))(C5q(q)) ))
    # Mycielskians
    C5=[(i,(i+1)%5) for i in range(5)]
    gN,gadj=mycielskian(5,C5)
    run("M(C5)=Grotzsch11",gN,gadj)
    pet=[set() for _ in range(10)]
    for i in range(5):
        for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet[a].add(b); pet[b].add(a)
    pN,padj=mycielskian(10,edges_of(pet)); run("M(Petersen)21",pN,padj)
