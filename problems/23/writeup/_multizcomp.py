"""Codex block 40: MULTI-ZCOMP-EXTREMAL. If a zero-load B-component Z's positive boundary B_N(Z) meets >=2 distinct
positive-K components, then every touched component C_j is internally EXTREMAL: T(v)=|C_j| for all v in C_j.
Violation = a touched component (when >=2 are touched) with some v having T(v) != |C_j|. Exact Fraction. All gamma-min cuts."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def multi_viol(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    comp, find = kcomponents(n, cyc)
    # positive-K component sizes (count only T>0 vertices in each root's set)
    possize={}
    for root,vs in comp.items():
        pv=[v for v in vs if T[v]>0]
        if pv: possize[root]=pv
    T0=[v for v in range(N) if T[v]==0]; T0set=set(T0)
    seen=set(); viol=[]
    for s in T0:
        if s in seen: continue
        Z=set(); stack=[s]; seen.add(s)
        while stack:
            x=stack.pop(); Z.add(x)
            for y in adj[x]:
                if y in T0set and side[y]!=side[x] and y not in seen:
                    seen.add(y); stack.append(y)
        BN=set()
        for z in Z:
            for w in adj[z]:
                if w not in Z and side[w]!=side[z] and T[w]>0: BN.add(w)
        if not BN: continue
        roots=set(find(w) for w in BN)
        if len(roots)<2: continue   # only the multi-component case
        for r in roots:
            Cj=possize.get(r,[])
            sz=len(Cj)
            for v in Cj:
                if T[v]!=sz:
                    viol.append((sorted(Z)[:4], sorted(BN), sz, v, float(T[v])))
                    break
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
    gm=min(G for _,G in cand); tot=0; first=None; nmulti=0
    for side,G in cand:
        if G!=gm: continue
        v=multi_viol(n,adj,side)
        if v is None: continue
        # count multi cases regardless of violation (for coverage)
        tot+=len(v);
        if v and first is None: first=(side,v[0])
    return tot,first

if __name__=="__main__":
    print("=== MULTI-ZCOMP-EXTREMAL over ALL gamma-min cuts ===")
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    t,f=allcuts(12,E12); print(f"  N=12 leaf caveat: viol={t}"+(f" {f}" if f else ""))
    # the O-empty multi witness
    n,E=dec("J?AAD@OJ?s?"); info=loads(n,E)
    print(f"  J?AAD@OJ?s? loads-cut: multi-viol={len(multi_viol(info['n'],info['adj'],info['side']) or [])} (expect 0 -- islands extremal)")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; first=None
        for g6 in outg:
            n,E=dec(g6); t,f=allcuts(n,E); tot+=t
            if f and first is None: first=(g6,f)
        print(f"  census N={nn} (all gamma-min cuts): MULTI-ZCOMP-EXTREMAL viol={tot}"+(f" FIRST {first}" if first else ""),flush=True)
    # loads-cut N=11
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    tot=0; first=None
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        v=multi_viol(info['n'],info['adj'],info['side'])
        if v: tot+=len(v); first=first or (g6,v[0])
    print(f"  census N=11 LOADS-cut: MULTI-ZCOMP-EXTREMAL viol={tot}"+(f" FIRST {first}" if first else ""),flush=True)
