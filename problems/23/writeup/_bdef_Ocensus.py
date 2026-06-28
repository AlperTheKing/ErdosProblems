"""Census restricted to graphs where O is nonempty (the ONLY graphs that can host a critical Q-only comp).
For each such graph, find Q-only K-components carrying a bad edge and check boundary-deficit exactly.
Reports: #graphs with O nonempty, # that ALSO have a Q-only bad-carrying K-comp (the coexistence we seek),
worst slack, any violation, any critical. EXACT.  Run from .../problems/23/writeup."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import build_K_T, Kcomponents

def scan(Nmin,Nmax,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nO=0; coexist=0; viol=0; crit=0; worst=None; wg=None; mindef=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,T,M,ell,N=build_K_T(info)
            O=set(v for v in range(n) if T[v]>N)
            if not O: continue
            nO+=1
            Bset=info['Bset']
            for C in Kcomponents(K,n):
                Cs=set(C)
                if Cs & O: continue
                badC=[f for f in M if f[0] in Cs and f[1] in Cs]
                if not badC: continue
                coexist+=1
                sz=len(C); mass=sum(T[v] for v in C)
                deficit=F(N*sz)-mass
                dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
                slack=deficit-dB
                if worst is None or slack<worst: worst=slack; wg=(g6,N,sz,float(deficit),dB,tuple(C))
                if mindef is None or deficit<mindef: mindef=deficit
                if deficit<dB: viol+=1
                if deficit==0: crit+=1
        print(f"  N={nn}(str{stride}): graphs w/ O!=0 = {nO} | Q-only-bad coexist = {coexist} | "
              f"viol={viol} crit={crit} worst slack={float(worst) if worst is not None else 'na'} "
              f"mindef={float(mindef) if mindef is not None else 'na'} @ {wg}",flush=True)

if __name__=="__main__":
    import sys
    Nmin=int(sys.argv[1]) if len(sys.argv)>1 else 7
    Nmax=int(sys.argv[2]) if len(sys.argv)>2 else 12
    stride=int(sys.argv[3]) if len(sys.argv)>3 else 1
    print(f"=== O-nonempty census {Nmin}..{Nmax} stride={stride} ===")
    scan(Nmin,Nmax,stride)
