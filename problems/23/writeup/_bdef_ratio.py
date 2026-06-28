"""For every Q-only K-component (disjoint from O) over the census, record:
  deficit = N|C|-mass, |C|(N-|C|) [the Erdos lower bound on deficit], dB, and check:
    (A) deficit >= |C|(N-|C|)   [follows from mass=Gamma(C)<=|C|^2]
    (B) dB <= |C|(N-|C|)        [if TRUE always, then deficit>=dB always -> lemma PROVED via this route]
    (C) deficit >= dB           [the lemma]
Report worst (smallest) margins for each, exact. Include ALL Q-only comps (even T=0 trivial) for (B).
Run from E:/Projects/ErdosProblems/problems/23/writeup."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import build_K_T, Kcomponents

def scan(Nmin,Nmax,stride=1):
    minA=None; wA=None      # deficit - |C|(N-|C|)
    minB=None; wB=None      # |C|(N-|C|) - dB
    minC=None; wC=None      # deficit - dB
    maxdB_ratio=None; wR=None  # dB / (|C|(N-|C|)) where denom>0
    cntO_coexist=0
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,T,M,ell,N=build_K_T(info)
            O=set(v for v in range(n) if T[v]>N)
            Bset=info['Bset']
            for C in Kcomponents(K,n):
                Cs=set(C)
                if Cs & O: continue
                sz=len(C); mass=sum(T[v] for v in C)
                deficit=F(N*sz)-mass
                dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
                erdos=sz*(N-sz)  # |C|(N-|C|)
                if O: cntO_coexist+=1
                a=deficit-erdos
                if minA is None or a<minA: minA=a; wA=(g6,N,sz,float(deficit),erdos)
                b=F(erdos)-dB
                if minB is None or b<minB: minB=b; wB=(g6,N,sz,erdos,dB,tuple(C))
                c=deficit-dB
                if minC is None or c<minC: minC=c; wC=(g6,N,sz,float(deficit),dB,tuple(C),bool(O))
                if erdos>0:
                    r=F(dB,erdos)
                    if maxdB_ratio is None or r>maxdB_ratio: maxdB_ratio=r; wR=(g6,N,sz,dB,erdos,float(r))
        print(f"  done N={nn}",flush=True)
    print("\n=== RATIO/BOUND SUMMARY ===")
    print(f"  (A) min(deficit - |C|(N-|C|)) = {float(minA)} @ {wA}   [>=0 confirms Erdos lower bound on deficit]")
    print(f"  (B) min(|C|(N-|C|) - dB)     = {float(minB)} @ {wB}   [>=0 would PROVE deficit>=dB]")
    print(f"  (C) min(deficit - dB)        = {float(minC)} @ {wC}   [the lemma itself]")
    print(f"  max dB/(|C|(N-|C|))          = {float(maxdB_ratio) if maxdB_ratio else 'na'} @ {wR}")
    print(f"  #(Q-only comps coexisting with O nonempty) = {cntO_coexist}")

if __name__=="__main__":
    import sys
    Nmin=int(sys.argv[1]) if len(sys.argv)>1 else 5
    Nmax=int(sys.argv[2]) if len(sys.argv)>2 else 11
    stride=int(sys.argv[3]) if len(sys.argv)>3 else 1
    print(f"=== census {Nmin}..{Nmax} stride={stride} bounds (A)(B)(C) ===")
    scan(Nmin,Nmax,stride)
