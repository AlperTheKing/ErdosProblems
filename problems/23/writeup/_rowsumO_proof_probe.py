"""Probe toward a PROOF of (ROWSUM-O): <p_f, s> <= N, s(v)=sum_g p_g(v).
Reformulations to test exactly:
  (R-avg)  <p_f,s>/ell(f) = p_f-weighted avg of s  <= N/ell(f).   [avg of incidence field over f's geodesic]
  (R-tot)  sum_v s(v) = L (total length sum_g ell(g)).  And sum_v s(v)^2 = sum_{f,g}O_fg = 1^T O 1.
           Note <p_f,s> = (O 1)_f, so max_f (O1)_f <= N is what we want; 1^T O 1 = sum_f (O1)_f <= N*m? weak.
  (R-CS)   <p_f,s> <= ||p_f|| ||s||. ||p_f||^2=O_ff<=ell(f). ||s||^2=1^T O 1. Likely too weak; test.
  (R-dom)  Is s(v) <= 1 + (something)? On blowups s(v)=L/N=const. Check max_v s(v) and where.
  (R-key)  The DUAL meaning: (O1)_f = sum_v p_f(v) s(v). Decompose by geodesic layers of f. Since p_f(v)
           counts fraction of f-geodesics through v, and s(v) counts total geodesic incidence, this is the
           expected total-incidence seen along a random f-geodesic. Bounded by N = #vertices because a single
           geodesic visits ell(f) vertices and ... test layer-decomposition: sum over layers.
  (R-int)  Integral/per-vertex: is s(v) <= deg_B-ish? Compute s(v) vs B-degree and vs #bad-edges-through-v.
Report: max_v s(v) and the graph; (R-CS) residual (||p_f|| ||s|| - N, want maybe <=0? probably >0 = CS too weak);
        whether (O1)_f <= max_v s(v) * ell(f) (a weak sufficient bound) ever certifies."""
import numpy as np
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow

def pf_exact(info):
    M=info['M']; cyc=info['cyc']; pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    return pf

def probe(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; m=len(M)
    pf=pf_exact(info)
    s=[sum(pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    maxs=max(s)
    L=sum(s)  # = sum_g ell(g)
    def ip(a,b):
        ss=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: ss+=av*bv
        return ss
    O1=[sum(ip(pf[i],pf[j]) for j in range(m)) for i in range(m)]
    res=[O1[i]-N for i in range(m)]
    # weak bound: (O1)_f <= maxs * ell(f) ?  certifies if maxs*ell(f)<=N
    weak_ok=all(maxs*ell[M[i]]<=N for i in range(m))
    return maxs, L, max(res), weak_ok, ell, M, N

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; mxs=None; mxsg=None; wr=None; weakcnt=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        ms,L,mr,wk,ell,M,N=probe(info)
        if mxs is None or ms>mxs: mxs=ms; mxsg=g6
        if wr is None or mr>wr: wr=mr
        if wk: weakcnt+=1
    print(f"N={nn}: cfg={nt} | max s(v)={mxs}={float(mxs):.3f}@{mxsg} | ROWSUM-O max-resid={float(wr):+.3f} | weak bound(maxs*ell<=N) certifies {weakcnt}/{nt}")

if __name__=="__main__":
    print("=== probe ROWSUM-O proof: max incidence s(v), weak sufficient bounds ===")
    for nn in [7,8,9,10]:
        census(nn, limit=(None if nn<=9 else 1500))
    print("\n=== blowups: s(v) is constant=L/N? ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        ms,L,mr,wk,ell,M,N=probe(info)
        print(f"  C5[{t}] N={nn}: max s={float(ms):.3f} L={float(L)} L/N={float(L)/nn:.3f} ell(f)={ell[M[0]]} ell*L/N={float(ell[M[0]])*float(L)/nn:.3f} (=N?) ROWSUM-O resid={float(mr):+.3f}")
