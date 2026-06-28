"""Codex block 34: EXIST-SAT-ZMU. Among ALL gamma-min connected-B max cuts, does there EXIST one with 0
saturated-zero-mu incidences (a zero-mu cut edge incident to a T=N vertex)? For O-nonempty configs that = SAT-ZMU-CLASS.
The reduction only needs ONE good gamma-min cut (beta=|M| is cut-independent; all gamma-min cuts share Gamma; Gamma<=N^2
for one => the bound). Enumerate cuts; report total gamma-min cuts, min saturated-zero-mu incidences over them, first
graph with min>0. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos

def struct_for_side(n, adj, side):
    """Build M, ell, T, mu for a GIVEN side. Returns None if invalid (no M, or geodesic broken)."""
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0])  # geodesic vertex count = ell
        sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    # mu per cut edge (B-edge)
    mu={}
    for u in range(n):
        for v in adj[u]:
            if side[u]!=side[v] and u<v: mu[(u,v)]=F(0)
    for f in M:
        Ps=cyc[f]; k=len(Ps); w=F(ell[f],k)
        for P in Ps:
            for i in range(len(P)-1):
                a,b=P[i],P[i+1]; e=(min(a,b),max(a,b))
                if e in mu: mu[e]+=w
    return M,ell,T,mu

def gamma_of(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G

def analyze(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    cuts=maxcut_all(n,adj)
    # connected-B cuts with M nonempty, compute Gamma
    cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        G=gamma_of(n,adj,side)
        if G is None: continue
        cand.append((side,G))
    if not cand: return None
    gmin_val=min(G for _,G in cand)
    gmins=[side for side,G in cand if G==gmin_val]
    # for each gamma-min cut, count saturated-zero-mu incidences
    counts=[]
    for side in gmins:
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu=st
        N=n
        O=[v for v in range(N) if T[v]>N]
        incid=0
        for e,val in mu.items():
            if val!=0: continue
            u,v=e
            if T[u]==N or T[v]==N: incid+=1
        counts.append((incid,len(O)))
    if not counts: return None
    return gmin_val, len(gmins), min(c[0] for c in counts), counts

if __name__=="__main__":
    print("=== EXIST-SAT-ZMU: min saturated-zero-mu incidences over all gamma-min cuts ===")
    # N=12 leaf caveat graph
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    r=analyze(12,E12)
    if r: print(f"  N=12 leaf(J?AADBWM_}}?+11~8): gamma-min={r[0]} #gamma-min-cuts={r[1]} MIN-incid={r[2]} (EXIST-SAT-ZMU {'OK' if r[2]==0 else 'FAILS'})  counts(incid,|O|)={r[3][:8]}")
    # census full multi-cut enumeration N=7..10
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        worst=None; ngr=0; nbad=0
        for g6 in outg:
            n,E=dec(g6); r=analyze(n,E)
            if r is None: continue
            ngr+=1
            if r[2]>0:
                nbad+=1
                if worst is None: worst=(g6,r)
        print(f"  census N={nn}: graphs={ngr} | graphs with EXIST-SAT-ZMU FAIL (min-incid>0 over all gamma-min cuts)={nbad}"+(f" FIRST {worst}" if worst else ""),flush=True)
