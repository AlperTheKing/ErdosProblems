#!/usr/bin/env python3
"""High-chromatic / routing-choice-essential test of the UNIFORM-SPLIT claim (U):
  for the gamma-min connected-B max cut of triangle-free G,
  max_v T_uniform(v) <= K = N + (N^2 - Gamma),
where T_uniform(v) = sum_{bad edge f} ell(f) * (#shortest cycles of f through v)/(#shortest cycles of f).
EXACT Fractions only. Targets: Mycielskians M(C5)=Grotzsch, M(C7), M(Petersen), M(Grotzsch),
and generalized Mycielskians M_r(C5) for small r (N<=20).
Each candidate violation is RE-CONFIRMED by an independent recompute."""
from fractions import Fraction
from collections import deque
import itertools

# ---- pure helpers (re-implemented self-contained; cross-checked vs census_GPI) ----
def build_adj(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def maxcut_all(n, adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]; best=-1; cuts=[]
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return cuts

def Bconn(n, adj, side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def bdist_restr(adj, side, s, t):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
    return d.get(t,-1)

def geos(adj, side, s, t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    P=[]
    def rec(v, acc):
        if v==s: P.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p, acc+[v])
    rec(t, [])
    return P

def gmin(n, adj, cuts):
    best=None
    for side in cuts:
        if not Bconn(n, adj, side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True; ell={}
        for (u,v) in M:
            d=bdist_restr(adj, side, u, v)
            if d<0: ok=False; break
            ell[(u,v)]=d+1; G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M,ell)
    return best

def T_uniform(n, adj, side, M, ell):
    """EXACT Fraction T_uniform per vertex."""
    T=[Fraction(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj, side, f[0], f[1])
        nf=len(Ps)
        assert nf>0
        share=Fraction(ell[f], nf)
        for P in Ps:
            for v in P:
                T[v]+=share
    return T

def is_triangle_free(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v>u:
                if adj[u] & adj[v]: return False
    return True

# ---- graph constructions ----
def cycle(k):
    return k, [(i,(i+1)%k) for i in range(k)]

def petersen():
    # outer 0..4, inner 5..9 (pentagram)
    E=[]
    for i in range(5): E.append((i,(i+1)%5))          # outer C5
    for i in range(5): E.append((5+i,5+(i+2)%5))      # inner pentagram
    for i in range(5): E.append((i,5+i))              # spokes
    return 10, E

def mycielskian(n, E):
    """Standard Mycielskian: u_0..u_{n-1}, w_0..w_{n-1}, apex z=2n.
    edges: u_i u_j for ij in E; u_i w_j & w_i u_j for ij in E; z w_i for all i."""
    NE=[]
    for (a,b) in E:
        NE.append((a,b))
        NE.append((a, n+b))
        NE.append((b, n+a))
    z=2*n
    for i in range(n): NE.append((z, n+i))
    return 2*n+1, NE

def gen_mycielskian(n, E, r):
    """Generalized Mycielskian M_r(G): r shadow layers + apex.
    Layers L_0 (original) .. L_{r-1}, apex z.
    Vertex (layer t, index i) -> id t*n+i for t in 0..r-1; z=r*n.
    Edges: within L_0: original E. Between consecutive layers L_t,L_{t+1}:
      for each ij in E: (t,i)-(t+1,j) and (t,j)-(t+1,i).
    Apex z connected to all of top layer L_{r-1}.
    (This is the standard generalized/cones Mycielski M_r; r=1 -> ordinary Mycielskian.)"""
    def vid(t,i): return t*n+i
    NE=[]
    for (a,b) in E: NE.append((vid(0,a), vid(0,b)))
    for t in range(r-1):
        for (a,b) in E:
            NE.append((vid(t,a), vid(t+1,b)))
            NE.append((vid(t,b), vid(t+1,a)))
    z=r*n
    for i in range(n): NE.append((z, vid(r-1,i)))
    return r*n+1, NE

def chromatic_number_ub(n, adj, cap=12):
    # greedy / exact small check not needed; just report
    return None

# ---- test driver ----
def test_graph(name, n, E, expect_chi=None):
    adj=build_adj(n, E)
    tf = is_triangle_free(n, adj)
    res={'name':name, 'N':n, 'triangle_free':tf}
    if not tf:
        res['error']='NOT triangle-free'
        return res
    if n>22:
        res['error']=f'N={n} too large for brute maxcut'
        return res
    cuts=maxcut_all(n, adj)
    r=gmin(n, adj, cuts)
    if r is None:
        res['error']='no connected-B monochromatic-edge max cut'
        return res
    side,G,M,ell=r
    K = n + (n*n - G)
    T=T_uniform(n, adj, side, M, ell)
    maxT=max(T)
    res.update({'Gamma':G, 'K':K, 'maxT':maxT, 'maxcut':sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])})
    res['slack']=Fraction(K)-maxT
    res['violation']= maxT > K
    res['side']=side; res['M_count']=len(M)
    return res

def reconfirm(name, n, E):
    """Independent recompute path: rebuild adjacency from scratch, recompute everything,
    and additionally verify the gamma-min cut's Gamma against ALL connected-B cuts directly."""
    adj=build_adj(n, E)
    cuts=maxcut_all(n, adj)
    # independent: enumerate connected-B cuts, find min Gamma manually
    best=None
    for side in cuts:
        if not Bconn(n, adj, side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        ell={}; G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj, side, u, v)
            if d<0: ok=False; break
            ell[(u,v)]=d+1; G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M,ell)
    side,G,M,ell=best
    K=n+(n*n-G)
    # recompute T with explicit cycle counting
    T=[Fraction(0)]*n
    for f in M:
        Ps=geos(adj, side, f[0], f[1])
        nf=len(Ps); share=Fraction(ell[f], nf)
        for P in Ps:
            for v in P: T[v]+=share
    maxT=max(T)
    return G,K,maxT,(maxT>K)

if __name__=='__main__':
    print("="*70)
    print("UNIFORM-SPLIT (U) audit: high-chromatic Mycielskian family")
    print("="*70)
    targets=[]
    # M(C5) = Grotzsch (N=11)
    n,E=cycle(5); targets.append(('M(C5)=Grotzsch', mycielskian(n,E)))
    # M(C7)  N=15
    n,E=cycle(7); targets.append(('M(C7)', mycielskian(n,E)))
    # M(Petersen) N=21
    n,E=petersen(); targets.append(('M(Petersen)', mycielskian(n,E)))
    # M(Grotzsch) N=23 -- too big for brute 2^22; will be flagged
    gn,gE=mycielskian(*cycle(5))  # Grotzsch
    targets.append(('M(Grotzsch)', mycielskian(gn,gE)))
    # generalized Mycielskians M_r(C5), N=5r+1 <=20 -> r<=3 (r=1 dup of Grotzsch); do r=2,3
    for r in (2,3):
        n,E=cycle(5); targets.append((f'M_{r}(C5)', gen_mycielskian(n,E,r)))
    # also M_2(C7) N=15, M_3(C7) N=22(too big); M_2(Petersen) N=21
    for r in (2,):
        n,E=cycle(7); targets.append((f'M_{r}(C7)', gen_mycielskian(n,E,r)))

    results=[]
    minslack=None
    for name,(N,EE) in targets:
        res=test_graph(name, N, EE)
        results.append(res)
        if 'error' in res:
            print(f"[{name}] N={res['N']} tri-free={res.get('triangle_free')} -> {res['error']}")
            continue
        sl=res['slack']
        flag='*** VIOLATION ***' if res['violation'] else 'OK'
        print(f"[{name}] N={res['N']} chi-target  Gamma={res['Gamma']} K={res['K']} "
              f"maxcut={res['maxcut']} maxT={res['maxT']} (~{float(res['maxT']):.4f}) "
              f"slack=K-maxT={sl} (~{float(sl):.4f})  {flag}")
        if minslack is None or sl<minslack:
            minslack=sl; minslack_name=name
        if res['violation']:
            G2,K2,mT2,v2=reconfirm(name, res['N'], EE)
            print(f"    RECONFIRM[{name}]: Gamma={G2} K={K2} maxT={mT2} violation={v2}")
    print("-"*70)
    if minslack is not None:
        print(f"MIN SLACK over tested family: {minslack} (~{float(minslack):.6f}) at {minslack_name}")
    print("DONE.")
