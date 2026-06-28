"""Codex block 38: all-tie split of SAT-ZMU-CONN.
A-alltie (ZMU-SAT-T0): for every zero-mu B-edge uv, T(u)=N => T(v)=0 (symmetric). [pure geodesic, no O]
C-alltie (ZERO-SAT-CONN): if O nonempty, T(z)=0, z B-adjacent to v with T(v)=N, then Kcomp(v) meets O. [mu-free]
A + C => SAT-ZMU-CONN. Test over ALL gamma-min cuts. Exact Fraction. Reuses _satzmu_conn machinery."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def testAC_side(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    comp, find = kcomponents(n, cyc)
    Aviol=[]; Cviol=[]
    # A-alltie
    for e,val in mu.items():
        if val!=0: continue
        u,v=e
        if T[u]==N and T[v]!=0: Aviol.append((u,v,float(T[u]),float(T[v])))
        if T[v]==N and T[u]!=0: Aviol.append((v,u,float(T[v]),float(T[u])))
    # C-alltie (needs O nonempty)
    if O:
        adjset=adj
        for v in range(N):
            if T[v]!=N: continue
            for z in adjset[v]:
                if side[z]!=side[v] and T[z]==0:
                    Cv=comp[find(v)]
                    if not (Cv & O): Cviol.append((z,v,sorted(Cv)[:6],sorted(O)))
    return Aviol, Cviol

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
    if not cand: return 0,0
    gm=min(G for _,G in cand)
    av=0; cv=0
    for side,G in cand:
        if G!=gm: continue
        r=testAC_side(n,adj,side)
        if r is None: continue
        av+=len(r[0]); cv+=len(r[1])
    return av,cv

if __name__=="__main__":
    print("=== A-alltie + C-alltie over ALL gamma-min cuts ===")
    # N=12 caveat
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    a,c=allcuts(12,E12)
    print(f"  N=12 leaf caveat: A-viol={a} C-viol={c}")
    # census all gamma-min cuts N=7..10
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tA=0; tC=0; bad=None
        for g6 in outg:
            n,E=dec(g6); a,c=allcuts(n,E)
            tA+=a; tC+=c
            if (a or c) and bad is None: bad=(g6,a,c)
        print(f"  census N={nn} (all gamma-min cuts): A-viol={tA} C-viol={tC}"+(f" FIRST {bad}" if bad else ""),flush=True)
    print("  (full N=11 all-cut: Codex's parallel run; loads-cut N=11 below)")
    # loads-cut census N=11 quick
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    tA=0; tC=0
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        r=testAC_side(info['n'],info['adj'],info['side'])
        if r: tA+=len(r[0]); tC+=len(r[1])
    print(f"  census N=11 LOADS-cut: A-viol={tA} C-viol={tC}",flush=True)
