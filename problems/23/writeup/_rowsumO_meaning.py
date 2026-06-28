"""Understand & attack (ROWSUM-O): for each bad edge f,  sum_g O_fg = <p_f, s> <= N,  s(v)=sum_g p_g(v).
Combinatorial meaning:
  <p_f,s> = sum_v p_f(v) s(v) = sum_v p_f(v) (sum_g p_g(v)) = sum_g <p_f,p_g>.
Since p_f(v)<=1 and supp(p_f) = f's geodesic interval (size = sum_v[p_f(v)>0] =: |supp f|, and sum_v p_f(v)=ell(f)),
  <p_f,s> <= max_v s(v) * sum_v p_f(v) = ell(f)*max_v s(v)  -- too weak (ell can be 5, s can be big).
Better: <p_f,s> = sum_{v in supp f} p_f(v) s(v).  Want <= N = #vertices.
Candidate proof ingredients to TEST exactly:
  (P1) s(v) <= (number of bad edges through v) but more precisely s(v)=sum_g p_g(v) <= deg-like quantity.
  (P2) The map v -> contributes p_f(v)*s(v); since sum_v p_f(v)=ell(f) and we sum a 'local density' s(v).
  (P3) KEY: is  sum_v p_f(v) s(v) <= sum_v s(v)  /something? Note sum_v s(v)=sum_g ell(g)=:L (total length).
       And sum_v p_f(v) s(v) is a weighted average of s by the prob measure p_f/ell(f), times ell(f).
  Actually the cleanest: <p_f,s> <= N is NOT obviously easier than Cycle-SM. Compare numerically which is tighter:
       (Cycle-SM)  (O ell)_f <= N ell(f)    residual_CSM = (O ell)_f - N ell(f)
       (ROWSUM-O)  (O 1)_f   <= N           residual_RO  = (O 1)_f  - N
  Both verified <=0. Report which has MORE slack (easier) and whether ROWSUM-O implies CycleSM or vice versa.
  ALSO test even-weaker SUFFICIENT bounds for ROWSUM-O:
    (S1)  <p_f,s> <= sum_v [s(v)>0] * 1  = |union of supports|  <= N ? i.e. is <p_f,s> <= #(vertices on some geodesic)?
    (S2)  Crucially: is s(v) <= ??? Let me just bound <p_f,s> <= sum_{v in supp f} s(v) (since p_f<=1), and ask
          is sum_{v in supp f} s(v) <= N? (sum of incidence-density over f's own interval). Test exact.
    (S3)  the COLUMN view: s(v)=sum_g p_g(v) = (expected # geodesics through v). For triangle-free, geodesics
          are 'odd-cycle halves'; maybe sum_{v} p_f(v)s(v) telescopes."""
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

def quant(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; m=len(M)
    pf=pf_exact(info)
    s=[F(0)]*n
    s=[sum(pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    def ip(a,b):
        ss=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: ss+=av*bv
        return ss
    O=[[ip(pf[i],pf[j]) for j in range(m)] for i in range(m)]
    Oell=[sum(O[i][j]*ell[M[j]] for j in range(m)) for i in range(m)]
    O1=[sum(O[i][j] for j in range(m)) for i in range(m)]
    res_csm=[Oell[i]-N*ell[M[i]] for i in range(m)]    # <=0
    res_ro =[O1[i]-N for i in range(m)]                # <=0
    # S2: sum_{v in supp f} s(v) for each f
    s2=[]
    for j,f in enumerate(M):
        supp=[v for v in pf[j]]
        s2.append(sum(s[v] for v in supp) - N)        # want <=0 ?
    return res_csm, res_ro, s2, ell, M, N

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0
    wc=None; wr=None; ws2=None; s2viol=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        rc,rr,s2,ell,M,N=quant(info)
        mc=max(rc) if rc else F(-1); mr=max(rr) if rr else F(-1); m2=max(s2) if s2 else F(-1)
        if wc is None or mc>wc: wc=mc
        if wr is None or mr>wr: wr=mr
        if ws2 is None or m2>ws2: ws2=m2
        if m2>0: s2viol+=1
    print(f"N={nn}: cfg={nt} | max CycleSM-resid={float(wc):+.3f} | max ROWSUM-O-resid={float(wr):+.3f} | (S2) max[sum_supp s - N]={float(ws2):+.3f} (#S2-viol={s2viol})")

if __name__=="__main__":
    print("=== compare Cycle-SM vs ROWSUM-O slack, and weaker sufficient (S2) ===")
    for nn in [7,8,9,10]:
        census(nn, limit=(None if nn<=9 else 1500))
    print("\n  (S2 is the cheap bound <p_f,s> <= sum_{v in supp f} s(v); if S2 holds it PROVES ROWSUM-O trivially)")
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        rc,rr,s2,ell,M,N=quant(info)
        print(f"  C5[{t}] N={nn}: CycleSM max={float(max(rc)):+.3f} ROWSUM-O max={float(max(rr)):+.3f} S2 max={float(max(s2)):+.3f}")
