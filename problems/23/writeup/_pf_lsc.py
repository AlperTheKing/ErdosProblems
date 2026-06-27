"""GPT's diagnostics 2+3: (a) PF(f) proportional-flow per-edge test -- each underloaded z splits capacity u(z)
proportionally among edges with z on their cycles (share u(z)phi_f(z)/T(z)); edge f needs 2 O_f. PF(f)>=0 for all f
=> explicit proportional flow => EDGE-Hall => COUPLE, NO global Hall redistribution. (b) LSC true binding (min over
NONEMPTY F of sum_{S_F} w, w=u or -2o), to see if LSC is tight or slack."""
from fractions import Fraction as F
from itertools import combinations
import subprocess
from census_GPI import dec, GENG
from _ph_mincut import loads

def phi(info):
    """phi_f(z) = ell_f * (count f-geodesics thru z)/n_f ; returns dict f-> {z: phi}."""
    M=info['M']; cyc=info['cyc']; ell=info['ell']; out={}
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for P in Ps:
            for z in P: cnt[z]=cnt.get(z,0)+1
        out[f]={z: F(ell[f]*c, nf) for z,c in cnt.items()}
    return out

def pf_min(info):
    n=info['n']; T=info['T']; M=info['M']; N=n; ph=phi(info)
    o={z:(T[z]-N if T[z]>N else F(0)) for z in range(n)}
    u={z:(N-T[z] if T[z]<N else F(0)) for z in range(n)}
    worst=None
    for f in M:
        recv=sum(u[z]*ph[f][z]/T[z] for z in ph[f] if T[z]<N)
        need=2*sum(o[z]*ph[f][z]/T[z] for z in ph[f] if T[z]>N)
        d=float(recv-need)
        if worst is None or d<worst: worst=d
    return worst   # PF holds (all f) iff >=0

def lsc_bind(info):
    n=info['n']; T=info['T']; M=info['M']; cyc=info['cyc']; N=n
    w={z:(float(N-T[z]) if T[z]<N else (-2.0*float(T[z]-N) if T[z]>N else 0.0)) for z in range(n)}
    Sf=[set(z for C in cyc[f] for z in C) for f in M]; m=len(M)
    best=None
    if m<=18:
        for r in range(1,m+1):
            for comb in combinations(range(m),r):
                S=set()
                for i in comb: S|=Sf[i]
                v=sum(w[z] for z in S)
                if best is None or v<best: best=v
    else:
        S=set(); cur=0.0; used=[False]*m
        for _ in range(m):
            bi=-1; bd=1e9
            for i in range(m):
                if not used[i]:
                    nv=sum(w[z] for z in (S|Sf[i]))
                    if nv<bd: bd=nv; bi=i
            if bi<0: break
            used[bi]=True; S|=Sf[bi]; cur=sum(w[z] for z in S)
            if best is None or cur<best: best=cur
    return best

if __name__=="__main__":
    fails=["I?BD@g]Qo","J?AADagROl?","J??CE?{{?]?","J?BD@g]Qvo?"]
    print("=== PF(f) min + LSC binding on failing/binding graphs ===")
    for g6 in fails:
        n,E=dec(g6); info=loads(n,E)
        print(f"  {g6:13} N={n} | PF min over f = {pf_min(info):+.4f} ({'PF HOLDS' if pf_min(info)>=-1e-9 else 'PF FAILS'}) | LSC binding (min nonempty F) = {lsc_bind(info):+.4f}")
    print("--- census N=10,11: PF violations + LSC true binding ---")
    for nn in (10,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=pfv=lscv=0; pworst=9e9; lworst=9e9
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            pm=pf_min(info); lb=lsc_bind(info)
            if pm<pworst: pworst=pm
            if lb is not None and lb<lworst: lworst=lb
            if pm<-1e-9: pfv+=1
            if lb is not None and lb<-1e-9: lscv+=1
        print(f"  N={nn}: configs={nt} | PF-fail(some f)={pfv} (worst PF={pworst:+.4f}) | LSC-viol={lscv} (true binding min={lworst:+.4f})",flush=True)
