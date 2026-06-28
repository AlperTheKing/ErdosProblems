"""Candidate clean lemma that PROVES link-I isoperimetry:
   (L)  for A = overload superlevel {v:T(v)>=c}, c>N:   sum_{v in A} T(v) <= N * delta_B(A).
Then c|A| <= sum_A T <= N*delta_B(A) => |A| <= (N/c) delta_B(A) < delta_B(A). QED link I.
Test (L) census N<=11. Also test the STRONGER universal form sum_{v in A}(T(v)-N) <= ??? and
the variant sum_{v in A}(T(v)-N)_+ <= N*delta_B(A) restricted to A=overload-set-superlevels.
Also test: does (L) hold for the overload set O={T>N} itself, and for ALL its superlevels."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def test(info):
    n=info['n']; T=info['T']; N=n
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    vals=sorted(set(v for v in o if v>0))
    worst=None  # min over levels of (N*dB - sum_A T)
    worst_o=None  # min of (N*dB - sum_A o)  [weaker target sum o = U_over-ish]
    for v in vals:
        A=set(z for z in range(n) if o[z]>=v)
        dB=sum(1 for (a,b) in info['Bset'] if (a in A)!=(b in A))
        sT=sum(T[z] for z in A)
        sO=sum(o[z] for z in A)
        g = N*dB - sT
        g2= N*dB - sO
        if worst is None or g<worst: worst=g
        if worst_o is None or g2<worst_o: worst_o=g2
    return worst,worst_o

def run(Nmax,Nmin=8):
    print("--- (L) sum_{v in A}T(v) <= N*delta_B(A) for overload superlevels A ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; Lbad=0; Lmin=None; Lg=None; L2bad=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; w,w2=test(info)
            if w is not None:
                if Lmin is None or w<Lmin: Lmin=w; Lg=g6
                if w<0: Lbad+=1
                if w2<0: L2bad+=1
        print(f"  N={nn}: cfg={nt} | (L) N*dB>=sumA T  violations:{Lbad} (min slack={float(Lmin) if Lmin is not None else 0:+.3f}@{Lg}) | weaker N*dB>=sumA o viol:{L2bad}",flush=True)

if __name__=="__main__":
    run(11,8)
