"""Edge-load decomposition toward proving (L) [=> link I].
mu(e) for cut edge e = sum_f sum_{P shortest geo of f, e in P} ell(f)/n_f.
Handshake identity (claim): sum_{e in B, e incident v} mu(e) = 2 T(v) - E(v),
  E(v) = sum_{bad edges f incident to v} ell(f)  (v is endpoint of all n_f geodesics).
Tests:
 1. VERIFY the identity sum_{e~v} mu(e) = 2T(v)-E(v) exactly (sanity).
 2. Is mu(e) <= N for every cut edge?  (clean per-edge bound; would help prove (L)).
 3. report max mu(e)/N.
Also: with A=overload superlevel, sum_{v in A}T(v) = sum_{e in A}mu + (1/2)sum_{dA}mu + (1/2)sum_{v in A}E(v);
 check this identity and whether RHS <= N*delta_B(A)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def edge_loads(info):
    """returns mu: dict (min,max)->Fraction for cut edges; E: dict v->ell-sum of bad edges at v."""
    n=info['n']; M=info['M']; cyc=info['cyc']; ell=info['ell']; side=info['side']
    mu={}
    for f in M:
        Ps=cyc[f]; nf=len(Ps); sh=F(ell[f],nf)
        for P in Ps:
            for i in range(len(P)-1):
                a,b=P[i],P[i+1]; e=(min(a,b),max(a,b))
                mu[e]=mu.get(e,F(0))+sh
    E={v:F(0) for v in range(n)}
    for f in M:
        E[f[0]]+=ell[f]; E[f[1]]+=ell[f]
    return mu,E

def run(Nmax,Nmin=8):
    print("--- edge-load mu(e): identity check + per-edge bound mu(e)<=N ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; id_bad=0; mu_over=0; max_ratio=None; mr_g=None; Lid_bad=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; mu,Ev=edge_loads(info); T=info['T']; N=n
            adjB={v:[] for v in range(n)}
            for (a,b) in info['Bset']: adjB[a].append((a,b)); adjB[b].append((a,b))
            # identity 1
            for v in range(n):
                s=sum(mu.get((min(a,b),max(a,b)),F(0)) for (a,b) in adjB[v])
                if s != 2*T[v]-Ev[v]: id_bad+=1; break
            # per-edge bound
            for e,val in mu.items():
                if val>N: mu_over+=1
                r=val/N
                if max_ratio is None or r>max_ratio: max_ratio=r; mr_g=(g6,e,float(val))
        print(f"  N={nn}: cfg={nt} | identity sum_e~v mu = 2T-E  FAILS:{id_bad} | mu(e)>N count:{mu_over} | max mu(e)/N={float(max_ratio):.4f} @ {mr_g}",flush=True)

if __name__=="__main__":
    run(11,8)
