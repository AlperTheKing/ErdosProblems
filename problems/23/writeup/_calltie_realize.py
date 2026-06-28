"""Is the C-alltie HYPOTHESIS ever realized? (O nonempty, T(z)=0, z B-adj v, T(v)=N)
over ALL gamma-min cuts census N<=10 + N=12 caveat + blow-ups + Mycielskians.
Also relax: O nonempty + T(z)=0 + z B-adj v with T(v)=N, ANY cut (not just gamma-min)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def realize_side(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return 0,0
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    if not O: return 0,0
    comp, find = kcomponents(n, cyc)
    cases=0; viol=0
    for v in range(N):
        if T[v]!=N: continue
        for z in adj[v]:
            if side[z]!=side[v] and T[z]==0:
                cases+=1
                Cv=comp[find(v)]
                if not (Cv & O): viol+=1
    return cases, viol

def allcuts_realize(n,E):
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
    tc=0; tv=0
    for side,G in cand:
        if G!=gm: continue
        c,v=realize_side(n,adj,side); tc+=c; tv+=v
    return tc,tv

if __name__=="__main__":
    print("=== C-alltie HYPOTHESIS realization census (all gamma-min cuts) ===")
    # N=12 caveat
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    c,v=allcuts_realize(12,E12); print(f"  N=12 caveat: cases={c} viol={v}")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tc=0; tv=0; first=None
        for g6 in outg:
            n,E=dec(g6); c,v=allcuts_realize(n,E); tc+=c; tv+=v
            if c and first is None: first=g6
        print(f"  census N={nn}: hypothesis cases={tc} viol={tv}"+(f" FIRST realizing {first}" if first else " (NEVER realized)"),flush=True)
