"""Codex block 39: ZCOMP-BOUNDARY-O (implies C-alltie). For a gamma-min connected-B max cut:
Z = connected component of the B-graph induced on T=0 vertices; B_N(Z) = {w notin Z, T(w)>0, w B-adjacent to some z in Z}.
ZCOMP-BOUNDARY-O: if O nonempty and B_N(Z) nonempty, then all of B_N(Z) lies in ONE positive-K component, and it meets O.
Violation: B_N(Z) spans >1 K-component, OR (O nonempty) its K-component disjoint from O. Test over ALL gamma-min cuts.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def zcomp_viol(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    comp, find = kcomponents(n, cyc)
    T0=[v for v in range(N) if T[v]==0]
    T0set=set(T0)
    # zero-load B-components: B-adjacency among T=0 vertices
    seen=set(); viol=[]
    for s in T0:
        if s in seen: continue
        # BFS over T=0 vertices via B-edges
        Z=set(); stack=[s]; seen.add(s)
        while stack:
            x=stack.pop(); Z.add(x)
            for y in adj[x]:
                if y in T0set and side[y]!=side[x] and y not in seen:
                    seen.add(y); stack.append(y)
        # positive boundary
        BN=set()
        for z in Z:
            for w in adj[z]:
                if w not in Z and side[w]!=side[z] and T[w]>0: BN.add(w)
        if not BN: continue
        if not O: continue   # ZCOMP-BOUNDARY-O premise requires O nonempty
        kc=set(find(w) for w in BN)
        if len(kc)>1:
            viol.append(('spans-multi-Kcomp', sorted(Z)[:5], sorted(BN), len(kc)))
            continue
        Kc=comp[next(iter(kc))]
        if not (Kc & O):
            viol.append(('Kcomp-misses-O', sorted(Z)[:5], sorted(BN), sorted(Kc)[:6], sorted(O)))
    return viol

def allcuts(n,E):
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
        v=zcomp_viol(n,adj,side)
        if v: tot+=len(v); first=first or (side,v[0])
    return tot,first

if __name__=="__main__":
    print("=== ZCOMP-BOUNDARY-O over ALL gamma-min cuts ===")
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    t,f=allcuts(12,E12); print(f"  N=12 leaf caveat: viol={t}"+(f" {f}" if f else ""))
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; first=None
        for g6 in outg:
            n,E=dec(g6); t,f=allcuts(n,E); tot+=t
            if f and first is None: first=(g6,f)
        print(f"  census N={nn} (all gamma-min cuts): ZCOMP-BOUNDARY-O viol={tot}"+(f" FIRST {first}" if first else ""),flush=True)
    # loads-cut N=11 + Mycielskians + blowups
    from _superphi import blow
    print("--- loads-cut: N=11 census + Mycielskians + blowups ---")
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    def myc(n,E):
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        N2=2*n+1; E2=list(E)
        for u in range(n):
            for v in adj[u]:
                if v>u: E2.append((u,n+v)); E2.append((v,n+u))
        for u in range(n): E2.append((n+u,2*n))
        return N2,E2
    n1,E1=myc(*C5); n2,E2=myc(n1,E1)
    for nm,(nn,EE) in [("MycGrotzsch N=23",(n2,E2))]:
        info=loads(nn,EE)
        if info: print(f"  {nm}: viol={len(zcomp_viol(info['n'],info['adj'],info['side']) or [])}")
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    tot=0
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        v=zcomp_viol(info['n'],info['adj'],info['side'])
        if v: tot+=len(v)
    print(f"  census N=11 LOADS-cut: ZCOMP-BOUNDARY-O viol={tot}",flush=True)
