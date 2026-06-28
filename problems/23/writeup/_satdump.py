"""Dump saturated zero-mu cases at N=10 to understand WHY v ends up dead (T(v)=0).
For each (sat u, zero-mu v): list ALL bad edges, T over vertices, and for v: confirm v on no geodesic.
Then characterize: is u 'surrounded' by saturated structure that leaves no room for v?
Look at u's K-component and v's relation."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _satzmu_conn import kcomponents

def dump(g6, maxshow=2):
    n,E=dec(g6); info=loads(n,E)
    if info is None: return 0
    N=info['n']; T=info['T']; side=info['side']; adj=info['adj']; M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    comp,find=kcomponents(N, cyc)
    shown=0
    for e,val in mu.items():
        if val!=0: continue
        a0,b0=tuple(e)
        for (u,v) in [(a0,b0),(b0,a0)]:
            if T[u]!=N: continue
            if shown>=maxshow: return shown
            shown+=1
            Cu=sorted(comp[find(u)])
            print(f"  {g6}: u={u}(T=N={N}) -- v={v}(T={str(T[v])}) zero-mu. side {side[u]}/{side[v]}")
            print(f"     T: {[str(t) for t in T]}")
            print(f"     Kcomp(u)={Cu}  v in Kcomp(u)? {v in Cu}  |Kcomp(u)|={len(Cu)}")
            # u's bad-edge structure
            fu=[(f,str(sum(F(1,len(cyc[f])) for P in cyc[f] if u in P)),ell[f]) for f in M if any(u in P for P in cyc[f])]
            print(f"     bad edges thru u: {fu}")
            # is v adjacent to many high-T vertices?
            vnb=[(w,str(T[w])) for w in adj[v] if side[w]!=side[v]]
            print(f"     v's B-nbrs (w,T(w)): {vnb}")
    return shown

if __name__=="__main__":
    print("=== saturated zero-mu dumps (mechanism for T(v)=0) ===")
    outg=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
    cnt=0
    for g6 in outg:
        s=dump(g6, maxshow=1)
        if s>0: cnt+=1
        if cnt>=8: break
