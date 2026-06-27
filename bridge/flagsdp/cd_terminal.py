#!/usr/bin/env python3
"""AUDIT of GPT's CD-preservation answer (terminal minimum-exposure geodesic + prefix-transport).
(1) Verify GPT's two concrete counterexamples (non-shortest fails CD; shortest fails CD at Gamma<N^2).
(2) Implement residual CD-defect D(C)=max_{S subset R}(delta_{M'}(S)-delta_{B'}(S))_+  [D=0 <=> CD preserved].
(3) For each bad edge's SHORTEST geodesic compute D(C); see if non-terminal (D>0) shortest geodesics ever
    occur in the TIGHT regime (Gamma=N^2) or only at low Gamma. Verify prefix-transport on an obstruction."""
from collections import deque
from itertools import combinations
import sys

def maxcut_all(n, adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for (u,v) in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return best,cuts

def is_max_cut(n,adj,side):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    mc,_=maxcut_all(n,adj)
    return sum(1 for (u,v) in edges if side[u]!=side[v])==mc

def cd_holds(n,adj,side):
    """check global cut-domination: for all S, delta_M(S)<=delta_B(S). brute (n<=~20)."""
    Be=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v]]
    Me=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if n>22: return None
    for mask in range(1<<n):
        dM=sum(1 for (u,v) in Me if ((mask>>u)&1)!=((mask>>v)&1))
        dB=sum(1 for (u,v) in Be if ((mask>>u)&1)!=((mask>>v)&1))
        if dM>dB: return False
    return True

def bdistB(n,adj,side,src,banned=None):
    banned=banned or set(); d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d: d[v]=d[u]+1; q.append(v)
    return d

def shortest_geodesics(n,adj,side,s,t):
    """ALL shortest B-paths s..t (as vertex lists)."""
    d=bdistB(n,adj,side,s);
    if t not in d: return []
    D=d[t]; out=[]
    def back(v,path):
        if v==s: out.append([s]+path[::-1] if False else None); return
    # build via layer BFS predecessors
    pred={s:[]}
    layer=[s]; seen={s}; dist={s:0}
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist:
                        dist[v]=dist[u]+1; pred[v]=[u];
                        if v not in seen: seen.add(v); nxt.append(v)
                    elif dist[v]==dist[u]+1:
                        pred[v].append(u)
        layer=nxt
    paths=[]
    def rec(v,acc):
        if v==s: paths.append([s]+acc[::-1]); return
        for p in pred.get(v,[]): rec(p,acc+[v])
    if t in dist and dist[t]==D: rec(t,[])
    return paths

def gamma_of(n,adj,side,M):
    G=0
    for (a,b) in M:
        dd=bdistB(n,adj,side,a).get(b,-1)
        if dd<0: return None
        G+=(dd+1)**2
    return G

def D_of(n,adj,side,M,C):
    """residual CD-defect of peeling vertex-set C: max over S subset R of (delta_{M'}(S)-delta_{B'}(S))_+.
    Also recompute Gamma' and report disconnection. Returns dict."""
    Cset=set(C); keep=[v for v in range(n) if v not in Cset]
    K=sorted(keep); idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K)
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    # Gamma'
    Gp=0; disc=False
    for (a,b) in Mp:
        dd=bdistB(n,adj,side,a,banned=Cset).get(b,-1)
        if dd<0: disc=True; break
        Gp+=(dd+1)**2
    res={"keep":m,"disconnected":disc,"gammap":None if disc else Gp}
    if m>22: res["D"]=None; return res
    best=0; arg=None
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        defect=dM-dB
        if defect>best: best=defect; arg=[u for u in K if (mask>>idx[u])&1]
    res["D"]=best; res["argS"]=arg
    return res

# ---------- GPT's two counterexamples ----------
def gpt_a():
    n=11; side=[0]*5+[1]*6
    B=[(4,10),(3,7),(1,8),(0,9),(4,6),(2,9),(1,7),(3,6),(1,10),(0,5),(2,5),(4,7),(3,5),(2,8)]
    M=[(0,4),(7,9)]
    adj=[set() for _ in range(n)]
    for (u,v) in B+M: adj[u].add(v); adj[v].add(u)
    return n,adj,side,M,B

def gpt_b():
    n=8; side=[0,0]+[1]*6
    B=[(1,2),(0,4),(1,5),(0,6),(0,2),(1,7),(0,5),(1,3)]
    M=[(6,7),(3,4)]
    adj=[set() for _ in range(n)]
    for (u,v) in B+M: adj[u].add(v); adj[v].add(u)
    return n,adj,side,M,B

def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def audit_gpt(name,builder,explicit_C=None):
    n,adj,side,M,B=builder()
    tf=tri_free(n,adj); mc=is_max_cut(n,adj,side); cd=cd_holds(n,adj,side); G=gamma_of(n,adj,side,M)
    print(f"\n=== {name}: N={n} tri_free={tf} side_is_maxcut={mc} CD_holds={cd} Gamma={G} N^2={n*n} (tight={G==n*n}) M={M} ===")
    for (u,v) in M:
        geos=shortest_geodesics(n,adj,side,u,v)
        dB=bdistB(n,adj,side,u).get(v,-1)
        if not geos: print(f"  bad edge ({u},{v}): NO B-path (disconnected)"); continue
        C0=geos[0]
        r=D_of(n,adj,side,M,C0)
        print(f"  bad edge ({u},{v}): d_B={dB} ell={dB+1} #shortest_geos={len(geos)} | first shortest C={C0} -> D(C)={r['D']} (CD {'OK' if r['D']==0 else 'FAILS'}) disc={r['disconnected']} Gamma'={r['gammap']} argS={r.get('argS')}")
    if explicit_C is not None:
        r=D_of(n,adj,side,M,explicit_C)
        print(f"  [GPT's explicit NON-shortest path C={explicit_C}] -> D(C)={r['D']} (CD {'OK' if r['D']==0 else 'FAILS'}) disc={r['disconnected']} Gamma'={r['gammap']} argS={r.get('argS')}")

# ---------- C5[q] and c5_paths ----------
def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]
    return n,adj,side,M

def audit_family(name,n,adj,side,M):
    G=gamma_of(n,adj,side,M); tf=tri_free(n,adj); cd=cd_holds(n,adj,side) if n<=20 else "n/a"
    Ds=[]
    terminal=0; nonterminal=0
    for (u,v) in M:
        geos=shortest_geodesics(n,adj,side,u,v)
        if not geos: continue
        # min D over the shortest geodesics of this bad edge
        best=None
        for C in geos:
            r=D_of(n,adj,side,M,C)
            if r["D"] is None: continue
            if best is None or r["D"]<best: best=r["D"]
        if best is None: continue
        Ds.append(best)
        if best==0: terminal+=1
        else: nonterminal+=1
    print(f"\n=== {name}: N={n} m={len(M)} Gamma={G} N^2={n*n} tight={G==n*n} tri_free={tf} CD={cd} ===")
    print(f"   per-bad-edge min D over its shortest geodesics: {sorted(set(Ds))}  | terminal(D=0)={terminal} nonterminal(D>0)={nonterminal} of {len(Ds)}")

if __name__=="__main__":
    # GPT's non-shortest path in (a): 0-5-2-8-1-10-4
    audit_gpt("GPT (a) non-shortest fails CD", gpt_a, explicit_C=[0,5,2,8,1,10,4])
    audit_gpt("GPT (b) shortest fails CD (Gamma<N^2)", gpt_b)
    for q in (2,3,4):
        n,adj,side,M=C5q(q); audit_family(f"C5[{q}] balanced blow-up", n,adj,side,M)
    # c5_paths(4) and theta_witness via ear_invariant
    from ear_invariant import c5_paths, theta_witness
    n,adj,side,M,idx=c5_paths(4); audit_family("c5_paths(4) (subdivided-C5, GPT 'c5paths20')", n,[set(a) for a in adj],side,M)
    n,adj,side,M,idx=theta_witness(); audit_family("theta_witness (m=1)", n,[set(a) for a in adj],side,M)
    print("\nDONE")
