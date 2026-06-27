"""Refine the bridge. Two questions:
(1) Per-level isoperimetry: for overload superlevel A_c={z:T(z)>=c}, c>N, is |A_c| <= dB(A_c)?
    (sufficient for U_over<=HV_B by coarea). Test census-wide; report failures.
(2) Find an intermediate X with U_over <= X <= N^2-Gamma census-wide (HV_B fails the 2nd).
    Candidates per level s (o-superlevel A_s={o>s}): contribute to X via different per-level bounds.
    Test X2 = sum_s [min(|A_s|, dB(A_s))]  (= U_over if isoperimetry holds), and
    X3 = sum_s (dB(A_s)-dM(A_s))  (=HV, CD coarea gap on o), and
    print the 3 N=11 graphs where HV_B>N2mG with full per-level breakdown."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def superlevels_o(info):
    """distinct positive values of o=(T-N)+; return sorted thresholds and sets A_s={o>=v}."""
    n=info['n']; T=info['T']; N=n
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    vals=sorted(set(v for v in o if v>0))
    return o,vals

def dB_dM(info,A):
    Aset=set(A)
    dB=sum(1 for (a,b) in info['Bset'] if (a in Aset)!=(b in Aset))
    dM=sum(1 for (a,b) in info['Mset'] if (a in Aset)!=(b in Aset))
    return dB,dM

def iso_fail(info):
    """returns max(|A_c|-dB(A_c)) over overload superlevels (>0 => isoperimetry fails)."""
    n=info['n']; T=info['T']; N=n
    o,vals=superlevels_o(info)
    worst=None; arg=None
    prev=F(0)
    # superlevel by load value c=N+v
    for v in vals:
        A=[z for z in range(n) if o[z]>=v]
        dB,dM=dB_dM(info,A)
        g=len(A)-dB
        if worst is None or g>worst: worst=g; arg=(float(v),len(A),dB)
    return (worst if worst is not None else 0),arg

def probe(info):
    n=info['n']; T=info['T']; N=n; G=info['G']; N2mG=N*N-G
    o,vals=superlevels_o(info)
    Uover=sum(v for v in o)
    HV_B=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    HV_M=sum(abs(o[a]-o[b]) for (a,b) in info['Mset'])
    return dict(Uover=Uover,N2mG=N2mG,HV_B=HV_B,HV_M=HV_M,HV=HV_B-HV_M)

def run_census(Nmax,Nmin=8):
    print("--- isoperimetry |A|<=dB(A) on overload superlevels + intermediate search ---")
    fails11=[]
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; iso_bad=0; iso_worst=None; HVB_gt=0
        HV_ge_U=0; HV_le_N=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            w,arg=iso_fail(info)
            if w>0: iso_bad+=1
            if iso_worst is None or w>iso_worst: iso_worst=w
            d=probe(info)
            if d['HV']>=d['Uover']: HV_ge_U+=1
            if d['HV']<=d['N2mG']: HV_le_N+=1
            if d['HV_B']>d['N2mG']:
                HVB_gt+=1
                if nn==11 and len(fails11)<6: fails11.append(g6)
        print(f"  N={nn}: cfg={nt} | iso |A|<=dB(A) FAILS:{iso_bad} (max |A|-dB={iso_worst}) | HV>=U_over:{HV_ge_U}/{nt} | HV<=N2mG:{HV_le_N}/{nt} | HV_B>N2mG:{HVB_gt}",flush=True)
    return fails11

def detail(g6):
    n,E=dec(g6); info=loads(n,E); N=n
    o,vals=superlevels_o(info); d=probe(info)
    print(f"\n=== detail {g6} N={n} Gamma={info['G']} | U_over={float(d['Uover']):.3f} N2mG={float(d['N2mG'])} HV_B={float(d['HV_B']):.3f} HV_M={float(d['HV_M']):.3f} HV={float(d['HV']):.3f} ===")
    print(f"  T = {[float(t) for t in info['T']]}")
    for v in vals:
        A=[z for z in range(n) if o[z]>=v]
        dB,dM=dB_dM(info,A)
        print(f"   level o>={float(v):.3f}: A={sorted(A)} |A|={len(A)} dB={dB} dM={dM} (|A|<=dB:{len(A)<=dB})")

if __name__=="__main__":
    fails=run_census(11,8)
    print("\n3 graphs where HV_B>N2mG (chain-2 break):", fails[:4])
    for g6 in fails[:4]:
        detail(g6)
