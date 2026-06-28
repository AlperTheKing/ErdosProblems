"""Is link II (HV_B<=U_under) "free" (true for GENERAL graphs, not just triangle-free)?
If yes => the triangle-free content of Gamma<=N^2 is ISOLATED in link I (overload isoperimetry).
Run on ALL connected graphs N<=8 (geng WITHOUT -t, so triangles allowed). loads() still builds the
Gamma-min connected-B max cut + shortest B-geodesic-cycle load T (now ell can be 3 for triangles).
Report link II violations + also link I (isoperimetry) violations on general graphs."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def check(info):
    n=info['n']; T=info['T']; N=n
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    u=[(N-T[z] if T[z]<N else F(0)) for z in range(n)]
    Uo=sum(o); Uu=sum(u)
    HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    # link I isoperimetry on overload superlevels
    vals=sorted(set(v for v in o if v>0)); iso_ok=True
    for v in vals:
        A=set(z for z in range(n) if o[z]>=v)
        dB=sum(1 for (a,b) in info['Bset'] if (a in A)!=(b in A))
        if len(A)>dB: iso_ok=False; break
    return (Uo<=HVB),(HVB<=Uu),iso_ok,(Uo,Uu,HVB)

def run(Nmax,Nmin=5):
    print("--- link I/II on GENERAL connected graphs (triangles allowed), geng -c ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-c",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; I_bad=II_bad=iso_bad=0; worstII=None; wII=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; L1,L2,iso,(Uo,Uu,HVB)=check(info)
            if not L1: I_bad+=1
            if not L2: II_bad+=1
            if not iso: iso_bad+=1
            slk=Uu-HVB
            if worstII is None or slk<worstII: worstII=slk; wII=g6
        print(f"  N={nn}: cfg={nt} | link-I(U<=HVB) viol:{I_bad} | link-II(HVB<=Uu) viol:{II_bad} (min slack={float(worstII):+.3f}@{wII}) | iso viol:{iso_bad}",flush=True)

if __name__=="__main__":
    run(8,5)
