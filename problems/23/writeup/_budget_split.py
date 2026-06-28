"""Attempt a FULLY per-edge PSD certificate for N I - K (not just B).
We have N I - K = (N I - diag(T)) + sum_f B_f,  B_f = ell(f)diag(p_f) - p_f p_f^T (PSD, C-S).
diag(T) = sum_f ell(f) diag(p_f). So N I - K = N I - sum_f ell(f)diag(p_f) + sum_f(ell(f)diag(p_f)-p_f p_f^T)
                                          = N I - sum_f p_f p_f^T   (trivially, =def).
To get a per-edge PSD cert we must split N I among edges: N I = sum_f D_f with D_f>=0 diagonal, sum_f D_f = N I,
and show each  C_f := D_f - p_f p_f^T  is PSD.  C_f = D_f - p_f p_f^T PSD <=> p_f^T D_f^{-1} p_f <= 1 (Schur,
on supp where D_f>0; need D_f(v)>0 wherever p_f(v)>0). i.e. sum_{v in supp f} p_f(v)^2 / D_f(v) <= 1.
Total budget constraint: sum_f D_f(v) = N for every vertex v.
So the certificate EXISTS iff there are nonneg D_f(v) with:
   (1) for each vertex v: sum_f D_f(v) = N
   (2) for each bad edge f: sum_v p_f(v)^2 / D_f(v) <= 1   (only v in supp f, need D_f(v)>0 there)
This is a FEASIBILITY problem (convex: constraint (2) is convex in D_f). If feasible for ALL census graphs +
blowups, it's a clean structured PSD certificate: 'distribute the N-budget across the bad edges so each
edge's geodesic-incidence rank-1 is dominated.'

Natural candidate split (water-filling): D_f(v) proportional to the demand p_f(v) at v among edges through v:
   D_f(v) = N * p_f(v) / sum_{g: v in supp g} p_g(v) = N * p_f(v)/ (sum_g p_g(v)).
Let s(v)=sum_g p_g(v) (geodesic-incidence total at v, NOTE: s(v) != T(v); T uses ell-weights). Then
   sum_f D_f(v) = N * s(v)/s(v) = N  ✓ (1) holds.  Check (2): sum_v p_f(v)^2/D_f(v) = sum_v p_f(v)^2 * s(v)/(N p_f(v))
   = (1/N) sum_{v in supp f} p_f(v) s(v).  So (2) becomes:  sum_v p_f(v) s(v) <= N  for every bad edge f.
   i.e.  <p_f, s> <= N  where s(v)=sum_g p_g(v).  THIS is a clean per-edge inequality! Test it EXACTLY.
   (<p_f,s> = sum_g <p_f,p_g> = sum_g O_fg = (O 1)_f = row sum of O.)
So the candidate certificate REDUCES to:  (ROWSUM-O)  for every bad edge f:  sum_g O_fg <= N.
Test (ROWSUM-O) EXACTLY census-wide + blowups. If it holds, we get a per-edge water-filling PSD certificate."""
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

def rowsumO(info):
    n=info['n']; N=n; M=info['M']; m=len(M)
    pf=pf_exact(info)
    def ip(a,b):
        s=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: s+=av*bv
        return s
    O=[[ip(pf[i],pf[j]) for j in range(m)] for i in range(m)]
    rows=[sum(O[i][j] for j in range(m)) for i in range(m)]   # (O 1)_f = <p_f, s>
    res=[rows[i]-N for i in range(m)]   # <=0 desired
    # also the water-filling feasibility directly: does D_f(v)=N p_f(v)/s(v) satisfy (2)?
    # (2) <=> rows[i] <= N, same thing. So return max residual.
    return max(res) if res else F(-1), rows, M, N

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; worst=None; wg=None; viol=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        mr,rows,M,N=rowsumO(info)
        if worst is None or mr>worst: worst=mr; wg=g6
        if mr>0: viol+=1
    print(f"N={nn}: cfg={nt} | EXACT max (rowsum O - N) = {worst} = {float(worst):+.4f} @ {wg} | #violations(>0)={viol}")
    return worst, wg

if __name__=="__main__":
    print("=== (ROWSUM-O) test: sum_g O_fg <= N for all bad edges f? (=> water-filling per-edge PSD cert) ===")
    for nn in [7,8,9,10,11]:
        census(nn, limit=(None if nn<=10 else 1200))
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        mr,rows,M,N=rowsumO(info)
        print(f"  C5[{t}] N={nn}: max(rowsumO - N)={mr}={float(mr):+.4f}  (rows={[float(r) for r in rows[:6]]}...)")
    print("\n=== tight ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        mr,rows,M,N=rowsumO(info)
        print(f"  {g6} N={n}: max(rowsumO - N)={mr}={float(mr):+.4f}")
