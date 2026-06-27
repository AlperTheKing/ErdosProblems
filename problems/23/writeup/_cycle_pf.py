"""GPT's DECISIVE test A (cycle-level PF). The exact identity:
   PF(f) = (ell_f/n_f) * sum_{C in C_f} Delta(C),
   Delta(C) := sum_{z in C} [ (N-T(z))_+ - 2*(T(z)-N)_+ ] / T(z).
If Delta(C) >= 0 for EVERY shortest B-geodesic odd cycle C (of every bad edge, every graph),
then PF(f)>=0 for all f => COUPLE => delta=0 => #23, with a fully LOCAL per-cycle proof
(no global Hall, no threshold cancellation). A single Delta(C)<0 => cycle route dead, fall to
layer-level (test B). Exact rational arithmetic.
Also reports, when Delta(C)<0 somewhere, whether PF(f) still holds (integral over cycles)."""
from fractions import Fraction as F
import subprocess
from census_GPI import dec, GENG
from _ph_mincut import loads

def cycle_delta(info):
    """returns (min Delta(C) over all cycles/edges, witness, PF-min over f)."""
    n=info['n']; T=info['T']; M=info['M']; cyc=info['cyc']; ell=info['ell']; N=n
    worstC=None; wit=None; pf_worst=None
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        pf_sum=F(0)
        for C in Ps:
            d=F(0)
            for z in C:
                Tz=T[z]
                if Tz<N:   d+= F(N-Tz)/Tz
                elif Tz>N: d-= 2*F(Tz-N)/Tz
                # Tz==N contributes 0
            if worstC is None or d<worstC: worstC=d; wit=(f,tuple(C),float(d))
            pf_sum+=d
        PF=F(ell[f],nf)*pf_sum   # = PF(f) exactly
        if pf_worst is None or PF<pf_worst: pf_worst=PF
    return worstC, wit, pf_worst

def run_named(names):
    print("=== cycle-level Delta(C) on named graphs ===")
    for g6 in names:
        n,E=dec(g6); info=loads(n,E)
        if info is None:
            print(f"  {g6}: not bad-connected / skipped"); continue
        wC,wit,pf=cycle_delta(info)
        print(f"  {g6:13} N={n} | min Delta(C)={float(wC):+.4f} ({'cycle>=0' if wC>=0 else 'CYCLE<0 at f='+str(wit[0])+' C='+str(wit[1])}) | min PF(f)={float(pf):+.4f} ({'PF OK' if pf>=0 else 'PF FAILS'})")

def run_census(Nmax,Nmin=5):
    print("--- census: cycle-level Delta(C)>=0 ? ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=cycviol=pfviol=0; gmin=None; gg=None; pfmin=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; wC,wit,pf=cycle_delta(info)
            if gmin is None or wC<gmin: gmin=wC; gg=g6
            if pfmin is None or pf<pfmin: pfmin=pf
            if wC<0: cycviol+=1
            if pf<0: pfviol+=1
        print(f"  N={nn}: configs={nt} | Delta(C)<0 graphs={cycviol} (global min Delta={float(gmin):+.4f} @ {gg}) | PF-fail graphs={pfviol} (min PF={float(pfmin):+.4f})",flush=True)

if __name__=="__main__":
    run_named(["I?BF@zWF_","I?BD@g]Qo","J?AADagROl?","J??CE?{{?]?","J?BD@g]Qvo?"])
    run_census(11,5)
