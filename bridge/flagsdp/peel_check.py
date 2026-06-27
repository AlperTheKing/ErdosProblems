#!/usr/bin/env python3
"""Single-call harness for the SAFE-PEEL EXISTENCE LEMMA (Erdos #23, delta=0 / Connected-B Gamma-lemma).

LEMMA (being adversarially tested): every triangle-free graph G with a MAX cut whose cross-graph B is
connected on all N vertices, with Gamma = sum_{ab in M}(d_B(a,b)+1)^2 >= N^2 and m=|M|>=2 (NOT an
odd-cycle base case), has SOME bad edge uv whose shortest B-geodesic C=V(P) is a SAFE peel:
  (i)  CD preserved on G-C:  delta_{B'}(S) >= delta_{M'}(S)  for all S subset V\\C   (B',M' = restricted)
  (ii) every remaining bad edge ab in M' stays B'-connected (d_{B'}(a,b) < inf)
  (iii) L = Gamma - Gamma' <= 2|C|N - |C|^2.

A CONCRETE triangle-free instance with a connected-B max cut, m>=2, Gamma>=N^2, and NO safe peel for ANY
bad edge = a VERIFIED counterexample/obstruction. (Numerically Gamma<=N^2 always, so 'Gamma>=N^2' means
TIGHT Gamma=N^2; we also report near-tight.)

USAGE:
  from peel_check import check_instance
  adj = [set(),...]   # adjacency as list of neighbor-sets, vertices 0..n-1 (undirected, no self-loops)
  res = check_instance(n, adj)             # auto: max cut MINIMIZING Gamma over all max cuts
  # res = check_instance(n, adj, side=[0,1,...])  # or force a specific 2-coloring (must be a max cut)
  # res keys: ok(bool, True if triangle-free+valid), triangle_free, N, maxcut, side, B_connected,
  #           m, gamma, n2, tight(gamma==n2), ge_n2(gamma>=n2), has_safe_peel(bool|None), detail(str)
A genuine obstruction has: ok and triangle_free and B_connected and ge_n2 and m>=2 and has_safe_peel False.
"""
from collections import deque

def is_triangle_free(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v>u:
                if adj[u] & adj[v]: return False
    return True

def maxcut_all(n, adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for (u,v) in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return best, cuts

def bdistB(n, adj, side, src, banned=None):
    banned=banned or set()
    d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d:
                d[v]=d[u]+1; q.append(v)
    return d

def Bconnected(n, adj, side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def gamma_of(n, adj, side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    G=0
    for (u,v) in M:
        d=bdistB(n,adj,side,u).get(v,-1)
        if d<0: return None, M   # bad edge disconnected in B -> Gamma infinite (exclude)
        G+=(d+1)**2
    return G, M

def shortest_path_B(n, adj, side, s, t):
    par={s:None}; q=deque([s])
    while q:
        u=q.popleft()
        if u==t: break
        for v in adj[u]:
            if side[u]!=side[v] and v not in par: par[v]=u; q.append(v)
    if t not in par: return None
    p=[]; x=t
    while x is not None: p.append(x); x=par[x]
    return p[::-1]

def cut_dom(keep, n, adj, side, M):
    """exact: for all S subset keep, delta_{B'}(S) >= delta_{M'}(S). keep small (<=22)."""
    K=sorted(keep); kset=set(K); idx={v:i for i,v in enumerate(K)}; m=len(K)
    if m>22: return None
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Me=[(u,v) for (u,v) in M if u in kset and v in kset]
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Me if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dB<dM: return False
    return True

def has_safe_peel(n, adj, side, M, Gamma, NN):
    for (u,v) in M:
        P=shortest_path_B(n,adj,side,u,v)
        if P is None: continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        if not keep: continue
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; ok=True
        for (a,b) in Mp:
            d=bdistB(n,adj,side,a,banned=C).get(b,-1)
            if d<0: ok=False; break
            Gp+=(d+1)**2
        if not ok: continue            # (ii) fails: a bad edge disconnected
        L=Gamma-Gp; bound=2*s*NN-s*s
        if L>bound: continue           # (iii) fails
        cd=cut_dom(keep,n,adj,side,Mp)
        if cd is True: return True,(u,v,s,Gp,L,bound)
    return False,None

def check_instance(n, adj, side=None):
    adj=[set(a) for a in adj]
    for u in range(n):
        adj[u].discard(u)
    tf=is_triangle_free(n,adj)
    res={"ok":False,"triangle_free":tf,"N":n}
    if not tf:
        res["detail"]="NOT triangle-free"; return res
    mc,cuts=maxcut_all(n,adj)
    res["maxcut"]=mc
    if side is not None:
        edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
        c=sum(1 for (u,v) in edges if side[u]!=side[v])
        if c!=mc:
            res["detail"]=f"given side is NOT a max cut (cut={c}<maxcut={mc})"; res["side"]=side; return res
        chosen=[side]
    else:
        chosen=cuts
    # pick the max cut MINIMIZING Gamma (per the lemma 'for some max cut')
    best=None
    for sd in chosen:
        if not Bconnected(n,adj,sd): continue
        G,M=gamma_of(n,adj,sd)
        if G is None: continue
        if best is None or G<best[0]: best=(G,M,sd)
    if best is None:
        res["detail"]="no connected-B max cut with finite Gamma"; res["B_connected"]=False; return res
    G,M,sd=best
    res.update({"ok":True,"B_connected":True,"side":sd,"m":len(M),"gamma":G,"n2":n*n,
                "tight":G==n*n,"ge_n2":G>=n*n})
    if len(M)<2:
        res["has_safe_peel"]=None; res["detail"]=f"base case m={len(M)} (odd cycle); lemma excludes m<2"; return res
    sp,info=has_safe_peel(n,adj,sd,M,G,n)
    res["has_safe_peel"]=sp
    res["detail"]=(f"SAFE peel via bad-edge {info[0:2]} |C|={info[2]} Gamma'={info[3]} L={info[4]}<=bound{info[5]}"
                   if sp else "NO safe peel for any bad edge")
    return res

if __name__=="__main__":
    # self-test: C5[2] (N=10, tight, m=4) must have a safe peel; C5 (base) excluded
    def C5q(q):
        n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
        for i in range(5):
            for a in range(q):
                for b in range(q):
                    u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
        return n,adj
    for q in (2,3):
        n,adj=C5q(q); r=check_instance(n,adj)
        print(f"C5[{q}]: N={r['N']} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} tight={r.get('tight')} has_safe_peel={r.get('has_safe_peel')} | {r['detail']}")
    # C5 base case
    n=5; adj=[set() for _ in range(5)]
    for i in range(5): adj[i].add((i+1)%5); adj[(i+1)%5].add(i)
    r=check_instance(5,adj); print(f"C5 base: m={r.get('m')} has_safe_peel={r.get('has_safe_peel')} | {r['detail']}")
