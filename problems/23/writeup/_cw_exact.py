"""EXACT (Fraction) verification of the Collatz-Wielandt certificate with weight T:
   (CW-T)  for every vertex v:  (K T)_v <= N * T_v,   K_vw=sum_f p_f(v)p_f(w), T_w=sum_g ell(g)p_g(w).
This is the Collatz-Wielandt upper bound rho(K)<=N witnessed by the nonneg vector T (Perron-ish).
Since K>=0 entrywise and T>0, (CW-T) ALONE => rho(K)=rho(O)<=N => (SPEC) => Gamma<=N^2.  [Perron-Frobenius / CW]

We ALSO unpack (KT)_v combinatorially:
   (K T)_v = sum_w (sum_f p_f(v)p_f(w)) T_w = sum_f p_f(v) sum_w p_f(w) T_w = sum_f p_f(v) <p_f, T>.
And note <p_f,T> = sum_w p_f(w) T_w = (O ell)_f / ... wait: T_w = sum_g ell(g) p_g(w), so
   <p_f,T> = sum_g ell(g) sum_w p_f(w)p_g(w) = sum_g ell(g) O_fg = (O ell)_f.
So (KT)_v = sum_f p_f(v) (O ell)_f.   And Cycle-SM says (O ell)_f <= N ell(f).  If THAT holds then
   (KT)_v = sum_f p_f(v)(O ell)_f <= N sum_f p_f(v) ell(f) = N T_v.   => (CW-T) is IMPLIED BY Cycle-SM.
Conversely (CW-T) => rho<=N => Cycle-SM (since ell^T O ell <=N ell^T ell and equality forces). So they are
both equivalent to SPEC. The question: is (CW-T), or better Cycle-SM (O ell)_f<=N ell(f), PROVABLE directly?

Report EXACT max over all (graph,v) of (KT)_v - N*T_v (must be <=0) and EXACT max over (graph,f) of
(O ell)_f - N ell(f) (Cycle-SM residual, must be <=0). Both census N<=11 + blowups + tight graphs."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow

def pf_exact(info):
    n=info['n']; M=info['M']; cyc=info['cyc']
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    return pf

def quantities(info):
    """returns lists of exact Fractions:
       maxCW = max_v ((KT)_v - N T_v),  maxCSM = max_f ((O ell)_f - N ell(f))."""
    n=info['n']; N=n; M=info['M']; ell=info['ell']
    pf=pf_exact(info)
    T=info['T']  # list of Fraction, T[v]=sum_g ell(g)p_g(v); verify
    # recompute T exactly to be safe: T[v]=sum_g ell[M[g]] * pf[g].get(v,0)
    Tr=[F(0)]*n
    Tr=[sum(ell[M[g]]*pf[g].get(v,F(0)) for g in range(len(M))) for v in range(n)]
    # O ell exact: (O ell)_f = sum_g O_fg ell(g) = sum_g (<p_f,p_g>) ell(g) = sum_g ell(g) sum_w p_f(w)p_g(w)
    m=len(M)
    # <p_f,p_g>
    def ip(a,b):
        s=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: s+=av*bv
        return s
    O=[[ip(pf[i],pf[j]) for j in range(m)] for i in range(m)]
    Oell=[sum(O[i][j]*ell[M[j]] for j in range(m)) for i in range(m)]
    # CSM residual
    maxCSM=max(Oell[i]-N*ell[M[i]] for i in range(m)) if m else F(-1)
    # (KT)_v = sum_f p_f(v)(O ell)_f
    KT=[sum(pf[i].get(v,F(0))*Oell[i] for i in range(m)) for v in range(n)]
    maxCW=max(KT[v]-N*Tr[v] for v in range(n)) if n else F(-1)
    Tcheck=max(abs(Tr[v]-T[v]) for v in range(n)) if n else F(0)
    return maxCW, maxCSM, Tcheck

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; wCW=None; wCW_g=None; wCSM=None; wCSM_g=None; viol=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        cw,csm,tc=quantities(info)
        if tc!=0: print(f"   !! T mismatch {g6}: {tc}")
        if wCW is None or cw>wCW: wCW=cw; wCW_g=g6
        if wCSM is None or csm>wCSM: wCSM=csm; wCSM_g=g6
        if cw>0 or csm>0: viol+=1
    print(f"N={nn}: cfg={nt} | EXACT max (KT-N T)={wCW}={float(wCW):+.4f}@{wCW_g} | max (Oell-N ell)={wCSM}={float(wCSM):+.4f}@{wCSM_g} | #viol={viol}")

if __name__=="__main__":
    print("=== EXACT Collatz-Wielandt (CW-T) and Cycle-SM residuals over census ===")
    for nn in [7,8,9,10,11]:
        census(nn, limit=(None if nn<=10 else 1200))
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        cw,csm,tc=quantities(info)
        print(f"  C5[{t}] N={nn}: max(KT-N T)={cw}={float(cw):+.4f} | max(Oell-N ell)={csm}={float(csm):+.4f} (Tcheck={tc})")
    print("\n=== tight graphs ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        cw,csm,tc=quantities(info)
        print(f"  {g6} N={n}: max(KT-N T)={cw} | max(Oell-N ell)={csm} (Tcheck={tc})")
