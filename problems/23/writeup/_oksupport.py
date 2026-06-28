"""Codex block 42: O-K-SUPPORT (cleanest cond(1) form). For a gamma-min connected-B max cut, if O nonempty then every
positive-K component (a K-component with some T>0 vertex) intersects O. Equivalently: no positive-load K-component is
disjoint from O. Implies C-alltie + ZCOMP-BOUNDARY-O part 2. Violation: a positive-K component disjoint from O (O nonempty).
Also (block 41) ALLMAX-ZERO-SAT-CONN: same C-alltie conclusion over ALL connected maxcuts (Codex did N<=11; I confirm
O-K-SUPPORT over all gamma-min cuts here). Exact Fraction; no mu needed."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def ok_viol(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    if not O: return []   # O empty: cond(1) trivial
    comp, find = kcomponents(n, cyc)
    viol=[]
    for root,vs in comp.items():
        pos=[v for v in vs if T[v]>0]
        if not pos: continue   # positive-K component = has a T>0 vertex
        if not (set(pos) & O):
            viol.append((sorted(pos)[:6], [float(T[v]) for v in sorted(pos)[:6]], sorted(O)))
    return viol

def allcuts_ok(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); cand=[]
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
    if not cand: return 0,None
    gm=min(G for _,G in cand); tot=0; first=None
    for side,G in cand:
        if G!=gm: continue
        v=ok_viol(n,adj,side)
        if v: tot+=len(v); first=first or (side,v[0])
    return tot,first

if __name__=="__main__":
    print("=== O-K-SUPPORT (no positive-K component disjoint from O) over ALL gamma-min cuts ===")
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    t,f=allcuts_ok(12,E12); print(f"  N=12 leaf caveat: viol={t}"+(f" {f}" if f else ""))
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; first=None
        for g6 in outg:
            n,E=dec(g6); t,f=allcuts_ok(n,E); tot+=t
            if f and first is None: first=(g6,f)
        print(f"  census N={nn} (all gamma-min cuts): O-K-SUPPORT viol={tot}"+(f" FIRST {first}" if first else ""),flush=True)
    # loads-cut N=11 + Mycielskians + blowups
    from _superphi import blow
    def myc(n,E):
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        N2=2*n+1; E2=list(E)
        for u in range(n):
            for v in adj[u]:
                if v>u: E2.append((u,n+v)); E2.append((v,n+u))
        for u in range(n): E2.append((n+u,2*n))
        return N2,E2
    C5=(5,[(i,(i+1)%5) for i in range(5)]); n1,E1=myc(*C5); n2,E2=myc(n1,E1); m1,F1=myc(7,[(i,(i+1)%7) for i in range(7)])
    print("--- loads-cut: Mycielskians + blowups ---")
    for nm,(nn,EE) in [("MycGrotzsch N=23",(n2,E2)),("MycC7 N=15",(m1,F1))]:
        info=loads(nn,EE)
        if info: print(f"  {nm}: O-K-SUPPORT viol={len(ok_viol(info['n'],info['adj'],info['side']) or [])}")
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info: print(f"  {g6}[{t}] N={nn}: viol={len(ok_viol(info['n'],info['adj'],info['side']) or [])}")
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    tot=0
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        v=ok_viol(info['n'],info['adj'],info['side'])
        if v: tot+=len(v)
    print(f"  census N=11 LOADS-cut: O-K-SUPPORT viol={tot}",flush=True)
