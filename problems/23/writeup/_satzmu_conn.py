"""Codex block 35: SAT-ZMU-CONN (tie-invariant). For ANY gamma-min connected-B max cut, if O nonempty and a zero-mu
B-edge uv has T(u)=N, then u lies in a K-component meeting O (NOT a Q-only critical component). => cond(1) directly.
Violation: a zero-mu B-edge uv, T[u]=N, O nonempty, but Kcomp(u) disjoint from O. Test loads-gate + ALL gamma-min cuts
census N<=10 + N=12 leaf caveat. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos, loads

def struct_for_side(n, adj, side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    mu={}
    for u in range(n):
        for v in adj[u]:
            if side[u]!=side[v] and u<v: mu[(u,v)]=F(0)
    for f in M:
        Ps=cyc[f]; w=F(ell[f],len(Ps))
        for P in Ps:
            for i in range(len(P)-1):
                a,b=P[i],P[i+1]; e=(min(a,b),max(a,b))
                if e in mu: mu[e]+=w
    return M,ell,T,mu,cyc

def kcomponents(n, cyc):
    # union-find over geodesic paths (each path is a K-clique)
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: par[ra]=rb
    for f,Ps in cyc.items():
        for P in Ps:
            for i in range(1,len(P)): union(P[0],P[i])
    comp={}
    for v in range(n): comp.setdefault(find(v),set()).add(v)
    return comp, find

def conn_viol(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    if not O: return []   # O empty: SAT-ZMU-CONN vacuous (cond1 trivial)
    comp, find = kcomponents(n, cyc)
    viol=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=e
        for a in (u,v):
            if T[a]==N:
                Ca=comp[find(a)]
                if not (Ca & O): viol.append((a, e, float(T[a]), sorted(Ca)[:6], sorted(O)))
    return viol

def analyze_allcuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)
    cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((side,G))
    if not cand: return None
    gm=min(G for _,G in cand)
    allv=[]
    for side,G in cand:
        if G!=gm: continue
        v=conn_viol(n,adj,side)
        if v: allv.append((side,v))
    return allv

if __name__=="__main__":
    print("=== SAT-ZMU-CONN: saturated endpoint of zero-mu edge must lie in K-comp meeting O ===")
    # loads-gate
    print("--- loads() selected gate ---")
    gate=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","I??CABoNo","I??CF@wFo"]
    for g6 in gate:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        v=conn_viol(info['n'], info['adj'], info['side'])
        print(f"  {g6}: SAT-ZMU-CONN viol on loads-cut = {v if v else 'NONE'}")
    # N=12 leaf caveat: ALL gamma-min cuts
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    av=analyze_allcuts(12,E12)
    print(f"  N=12 leaf(J?AADBWM_}}?+11~8): ALL gamma-min cuts with a CONN-violation = {len(av) if av is not None else 'NA'}")
    for side,v in (av or [])[:3]: print(f"     side={side} viol={v}")
    # census N=7..10 ALL gamma-min cuts
    print("--- census N=7..10, ALL gamma-min cuts ---")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nbad=0; first=None
        for g6 in outg:
            n,E=dec(g6); av=analyze_allcuts(n,E)
            if av: nbad+=1; first=first or (g6,av[0])
        print(f"  census N={nn}: graphs with a gamma-min cut violating SAT-ZMU-CONN = {nbad}"+(f" FIRST {first}" if first else ""),flush=True)
