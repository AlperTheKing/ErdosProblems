"""Data-driven probe for the TV->COUPLE bridge. COUPLE = U_over <= N^2-Gamma.
For each graph compute candidate intermediate quantities and look for a clean chain
   U_over <= X <= N^2-Gamma   with X a CD/TV-derived quantity (provable from CD).
Candidates X:
  O = {z:T>N} overload set.  dB(O),dM(O) = cut/mono boundary of O.
  half-weighted TV on (T-N)_+ :  HV = sum_B|o(x)-o(y)| - sum_M|o(x)-o(y)|  (>=0 by CD), o=(T-N)_+
  boundary-overload  BO = sum over B-edges xy with exactly one endpoint in O of |o(x)-o(y)|
  Poincare RHS using B-graph.
Report, per graph, U_over, N2mG=N^2-Gamma, and the candidates; flag any candidate X with
U_over<=X<=N2mG always."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def probe(info):
    n=info['n']; T=info['T']; N=n
    o={z:(T[z]-N if T[z]>N else F(0)) for z in range(n)}      # overload
    u={z:(N-T[z] if T[z]<N else F(0)) for z in range(n)}      # underload
    Uover=sum(o.values()); Uunder=sum(u.values())
    G=info['G']; N2mG=N*N-G
    O=set(z for z in range(n) if T[z]>N)
    # boundaries of O
    dB=sum(1 for (a,b) in info['Bset'] if (a in O)!=(b in O))
    dM=sum(1 for (a,b) in info['Bset'] if False)  # placeholder
    dMo=sum(1 for (a,b) in info['Mset'] if (a in O)!=(b in O))
    dBo=dB
    # weighted TV on overload function o (provable >=0 by CD-coarea on o-superlevel)
    HV_B=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    HV_M=sum(abs(o[a]-o[b]) for (a,b) in info['Mset'])
    HV=HV_B-HV_M
    # weighted TV on full T
    TV_B=sum(abs(T[a]-T[b]) for (a,b) in info['Bset'])
    TV_M=sum(abs(T[a]-T[b]) for (a,b) in info['Mset'])
    TV=TV_B-TV_M
    return dict(Uover=Uover,N2mG=N2mG,Uunder=Uunder,dBo=dBo,dMo=dMo,HV_B=HV_B,HV_M=HV_M,HV=HV,TV=TV,TV_B=TV_B)

def run_named(names):
    print("=== bridge probe: U_over vs N^2-Gamma vs CD/TV candidates ===")
    print(f"  {'graph':13} {'U_over':>8} {'N2-G':>8} {'HV_B':>8} {'HV_M':>8} {'TV_B':>8} {'dBo':>4} {'dMo':>4}")
    for g6 in names:
        n,E=dec(g6); info=loads(n,E)
        if info is None: print(f"  {g6}: skip"); continue
        d=probe(info)
        print(f"  {g6:13} {float(d['Uover']):8.3f} {float(d['N2mG']):8.3f} {float(d['HV_B']):8.3f} {float(d['HV_M']):8.3f} {float(d['TV_B']):8.3f} {d['dBo']:4d} {d['dMo']:4d}")

def run_census(Nmax,Nmin=8):
    print("--- census: check candidate chains U_over<=X<=N2mG ---")
    # candidates: X1=HV_B (overload-TV cut side), X2=HV_B/2, X3=TV_B/2 ...
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0
        # track: max ratio U_over/(N2mG); and whether HV_B in [U_over, ?]; and U_over<=HV_B always
        c_HVB_ge_U=c_HVB_le_N=c_HV_ge=0; worst_U_over_minus_HVB=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; d=probe(info)
            U=d['Uover']; HVB=d['HV_B']; N2mG=d['N2mG']
            if HVB>=U: c_HVB_ge_U+=1
            if HVB<=N2mG: c_HVB_le_N+=1
            if d['HV']>=0: c_HV_ge+=1
            g=U-HVB
            if worst_U_over_minus_HVB is None or g>worst_U_over_minus_HVB: worst_U_over_minus_HVB=g
        print(f"  N={nn}: cfg={nt} | HV_B>=U_over:{c_HVB_ge_U}/{nt} | HV_B<=N2mG:{c_HVB_le_N}/{nt} | HV(coarea on o)>=0:{c_HV_ge}/{nt} | max(U_over-HV_B)={float(worst_U_over_minus_HVB):+.3f}",flush=True)

if __name__=="__main__":
    run_named(["I?BD@g]Qo","I?BF@zWF_","J?AADagROl?","J??CE?{{?]?","J?BD@g]Qvo?"])
    run_census(11,8)
