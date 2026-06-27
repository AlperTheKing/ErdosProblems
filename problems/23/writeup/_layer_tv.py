"""Tests B/C (layer-PF, prefix-layer-PF) + the CD-derived TV inequality on the load T.
For bad edge f=(u,v): phi_f(z)=ell_f*cnt_f(z)/n_f, layer(z)=B-dist from f[0]. Contribution
  c_f(z) = [ (N-T(z))_+ - 2(T(z)-N)_+ ] * phi_f(z)/T(z),  PF(f)=sum_z c_f(z).
B  (layer):  K_i(f)=sum_{z:layer=i} c_f(z) >=0  for all i?
C  (prefix): P_k(f)=sum_{i<=k} K_i(f) >=0 and suffix S_k=sum_{i>=k} K_i >=0 for all k?
TV (CD-coarea, PROVABLE from CD): sum_{xy in M}|T(x)-T(y)| <= sum_{xy in B}|T(x)-T(y)|.
All exact rational. A pass on B => layerwise proof; on C => prefix-monotone proof; TV is the CD input."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def contribs(info, f):
    """return dict layer-> sum c_f(z), and per-z (layer, c)."""
    n=info['n']; T=info['T']; ell=info['ell']; N=n
    Ps=info['cyc'][f]; nf=len(Ps); d=info['dist'][f]
    cnt={}
    for P in Ps:
        for z in P: cnt[z]=cnt.get(z,0)+1
    perlayer={}
    for z,c in cnt.items():
        phi=F(ell[f]*c, nf); Tz=T[z]
        if Tz<N: cz= F(N-Tz)*phi/Tz
        elif Tz>N: cz= -2*F(Tz-N)*phi/Tz
        else: cz=F(0)
        L=d[z]; perlayer[L]=perlayer.get(L,F(0))+cz
    return perlayer

def test_layer(info):
    """return (min K_i over all f,i), (min prefix), (min suffix)."""
    mK=mP=mS=None
    for f in info['M']:
        pl=contribs(info,f)
        Ls=sorted(pl)
        for L in Ls:
            if mK is None or pl[L]<mK: mK=pl[L]
        # prefix / suffix in layer order
        acc=F(0)
        for L in Ls:
            acc+=pl[L]
            if mP is None or acc<mP: mP=acc
        acc=F(0)
        for L in reversed(Ls):
            acc+=pl[L]
            if mS is None or acc<mS: mS=acc
    return mK,mP,mS

def tv_gap(info):
    """sum_B|dT| - sum_M|dT| (>=0 means TV inequality holds)."""
    T=info['T']
    sB=sum(abs(T[a]-T[b]) for (a,b) in info['Bset'])
    sM=sum(abs(T[a]-T[b]) for (a,b) in info['Mset'])
    return sB-sM

def run_named(names):
    print("=== layer-PF (B), prefix/suffix (C), TV inequality on named graphs ===")
    for g6 in names:
        n,E=dec(g6); info=loads(n,E)
        if info is None: print(f"  {g6}: skipped"); continue
        mK,mP,mS=test_layer(info); tv=tv_gap(info)
        print(f"  {g6:13} N={n} | min K_i={float(mK):+.4f} ({'B OK' if mK>=0 else 'B FAILS'}) | min prefix={float(mP):+.4f} ({'C-pre OK' if mP>=0 else 'C-pre FAILS'}) min suffix={float(mS):+.4f} | TV gap(B-M)={float(tv):+.4f} ({'TV OK' if tv>=0 else 'TV FAILS'})")

def run_census(Nmax,Nmin=5):
    print("--- census: layer K_i, prefix, suffix, TV ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=Kv=Pv=Sv=Tv=0; Kmin=Pmin=Smin=Tmin=None; Kg=Pg=Tg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; mK,mP,mS=test_layer(info); tv=tv_gap(info)
            if Kmin is None or mK<Kmin: Kmin=mK; Kg=g6
            if Pmin is None or mP<Pmin: Pmin=mP; Pg=g6
            if Smin is None or mS<Smin: Smin=mS
            if Tmin is None or tv<Tmin: Tmin=tv; Tg=g6
            if mK<0: Kv+=1
            if mP<0: Pv+=1
            if mS<0: Sv+=1
            if tv<0: Tv+=1
        print(f"  N={nn}: cfg={nt} | K_i<0:{Kv} (min {float(Kmin):+.3f}@{Kg}) | prefix<0:{Pv} (min {float(Pmin):+.3f}@{Pg}) | suffix<0:{Sv} (min {float(Smin):+.3f}) | TV<0:{Tv} (min {float(Tmin):+.3f}@{Tg})",flush=True)

if __name__=="__main__":
    run_named(["I?BD@g]Qo","I?BF@zWF_","J?AADagROl?","J??CE?{{?]?","J?BD@g]Qvo?"])
    run_census(11,5)
