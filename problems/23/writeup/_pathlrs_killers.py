"""Confirm PATH-LRS(c1) avg_P T <= N + N^2/25 - |M| SURVIVES exactly where the spectral BLOCK-SBC/BUNDLE-SBC died:
  - H?AFBo] N=9 (BLOCK-SBC killer: K-comp nC=7 mC=2 rho=8>budget).
  - C5 nonuniform/alternating blow-ups (2,1,2,1,2), (3,2,3,2,3), (3,1,3,1,3), (4,3,4,3,4) (BUNDLE-SBC killers).
  - two-lane L=8,12 (rho(O)<=N killer).
Per-path EXACT. Report worst (min margin) per graph over ALL gamma-min cuts."""
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane

def pathlrs_c1(name,n,adj,cuts):
    worst=None
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st
        if not M: continue
        m=len(M); rhs=F(n)+F(n*n,25)-m
        for f in M:
            for P in cyc[f]:
                avg=sum(T[v] for v in P)/ell[f]
                margin=rhs-avg
                if worst is None or margin<worst[0]:
                    worst=(margin,m,str(f),str(avg),str(rhs),[str(T[v]) for v in P])
    if worst is None:
        print("  %-22s: no bad edges"%name); return
    ok = worst[0]>=0
    print("  %-22s: min margin=%s=%s  m=%s f=%s avg=%s rhs=%s  -> %s"%(
        name,str(worst[0]),str(float(worst[0]))[:8],worst[1],worst[2],worst[3],worst[4],
        "HOLDS" if ok else "*** FAILS ***"))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    print("PATH-LRS(c1) on the spectral-route KILLERS:")
    n,E=dec('H?AFBo]'); adj,cuts=gmins(n,E); pathlrs_c1("H?AFBo] N=9",n,adj,cuts)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4]):
        n,E=blowup(parts)
        adj,cuts=gmins(n,E)
        pathlrs_c1("C5%s N=%d"%(parts,n),n,adj,cuts)
    for L in (8,12):
        n,E,side,bad=build_two_lane(L)
        pathlrs_c1("two-lane L=%d N=%d"%(L,n),n,adj_of(n,E),[side])
    print("=== if all HOLD, PATH-LRS(c1) survives where spectral BLOCK/BUNDLE-SBC died ===")
