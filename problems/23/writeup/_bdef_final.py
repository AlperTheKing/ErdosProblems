"""Final consolidation checks for boundary-deficit leg:
 (a) LOCAL per-vertex charge slack(v)=N-T(v) >= crossdeg_B(v) on ALL OTHER (proper loaded Q-only) comps N=10,11.
     If 0-fail, the LOCAL (hence aggregate) boundary-deficit has a per-vertex proof candidate.
 (b) the 14 N=10 R-loaded witnesses (graph K-splits into >=2 loaded comps, all Q-only, O empty): dump them.
 (c) A=NI-K min-eigenvalue >=0 (ROWSUM-O => A PSD) using exact symmetric eig via characteristic-poly sign?
     -> too heavy; instead confirm deficit>=0 always (trivial) and that the EXTRA dB-slack is not implied by PSD:
     report min over comps of (1_C^T A 1_C) vs dB, and the smallest x^T A x / |x|^2 proxy (Rayleigh at random x)
     to show A's bottom eigenvalue can be < dB (so PSD alone doesn't give boundary-deficit)."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def local_charge_check(B,C):
    K=B['K']; T=B['T']; N=B['N']; Bset=B['Bset']
    Cs=set(C)
    deg_cross={v:0 for v in C}
    for (a,b) in Bset:
        if (a in Cs)^(b in Cs):
            x=a if a in Cs else b; deg_cross[x]+=1
    return all((F(N)-T[v])>=deg_cross[v] for v in C), deg_cross

def scan_local(Nmin,Nmax):
    locfail=0; tot=0; failwit=None
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info); K=B['K']; T=B['T']; O=B['O']
            comps=components(K,n)
            for C in comps:
                Cs=set(C)
                if Cs&O: continue
                if len(C)==1 and T[C[0]]==0: continue
                tot+=1
                ok,dc=local_charge_check(B,C)
                if not ok:
                    locfail+=1
                    if failwit is None: failwit=(g6,tuple(C),{v:float(F(B['N'])-T[v]) for v in C},dc)
        print(f"  N={nn}: comps(loaded Q-only incl FULL)={tot} LOCAL_per_vertex_charge_FAIL={locfail}",flush=True)
    print(f"LOCAL charge: FAIL={locfail}/{tot} witness={failwit}")

def dump_Rloaded(nn):
    """dump N=10 cases where complement R of an OTHER comp has load."""
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    found=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']
        comps=components(K,n)
        for C in comps:
            Cs=set(C)
            if Cs&O: continue
            if len(C)==n: continue
            if len(C)==1 and T[C[0]]==0: continue
            R=[v for v in range(n) if v not in Cs]
            Rload=[v for v in R if T[v]>0]
            if Rload:
                d=analyze_one(B,C)
                found+=1
                if found<=14:
                    print(f"  {g6}: C={C} (deficit={float(d['deficit'])},dB={d['dB']}) R-load={[(v,float(T[v])) for v in Rload]} O={sorted(O)}")
    print(f"N={nn} R-loaded OTHER count={found}")

if __name__=="__main__":
    print("=== (a) LOCAL per-vertex charge on loaded Q-only comps N=10,11 ===")
    scan_local(10,11)
    print("=== (b) N=10 R-loaded OTHER witnesses ===")
    dump_Rloaded(10)
