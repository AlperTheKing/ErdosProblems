"""Enumerate ALL Q-only K-components coexisting with O nonempty across census N<=11, and classify:
bad-carrying? deficit, dB, slack. Find the smallest-deficit and smallest-slack ones (these are the
closest approaches to a critical/violating Q-only component). EXACT."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import build_K_T, Kcomponents

def run(Nmin,Nmax):
    recs=[]
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,T,M,ell,N=build_K_T(info)
            O=set(v for v in range(n) if T[v]>N)
            if not O: continue
            Bset=info['Bset']
            for C in Kcomponents(K,n):
                Cs=set(C)
                if Cs & O: continue
                sz=len(C); mass=sum(T[v] for v in C)
                deficit=F(N*sz)-mass
                dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
                badC=[f for f in M if f[0] in Cs and f[1] in Cs]
                recs.append((g6,N,sz,deficit,dB,len(badC),mass))
    # classify
    bad=[r for r in recs if r[5]>0]
    print(f"  total Q-only-with-O comps = {len(recs)}; bad-carrying = {len(bad)}")
    if recs:
        # smallest deficit overall (any)
        rmin=min(recs,key=lambda r:r[3])
        print(f"  smallest deficit (any) = {float(rmin[3])} dB={rmin[4]} |C|={rmin[2]} nbad={rmin[5]} g6={rmin[0]} N={rmin[1]}")
        rsl=min(recs,key=lambda r:r[3]-r[4])
        print(f"  smallest slack (deficit-dB) (any) = {float(rsl[3]-rsl[4])} deficit={float(rsl[3])} dB={rsl[4]} |C|={rsl[2]} nbad={rsl[5]} g6={rsl[0]} N={rsl[1]}")
        viol=[r for r in recs if r[3]<r[4]]
        print(f"  VIOLATIONS (deficit<dB) among Q-only-with-O = {len(viol)}  {viol[:5]}")
    if bad:
        bmin=min(bad,key=lambda r:r[3])
        print(f"  [bad-carrying] smallest deficit = {float(bmin[3])} dB={bmin[4]} |C|={bmin[2]} g6={bmin[0]} N={bmin[1]}")

if __name__=="__main__":
    import sys
    Nmin=int(sys.argv[1]) if len(sys.argv)>1 else 5
    Nmax=int(sys.argv[2]) if len(sys.argv)>2 else 11
    print(f"=== Q-only-with-O coexistence enumeration census {Nmin}..{Nmax} ===")
    run(Nmin,Nmax)
