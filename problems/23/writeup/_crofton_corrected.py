"""Corrected CD-Crofton certificate: handle the DIAGONAL self-overlap directly (||p_f||^2 <= ell(f) <= N),
use CD-cuts only for CROSS terms. For bad edge f:
   (Oell)_f = ell(f)*O_ff + sum_{g!=f} ell(g) O_fg,   O_ff=||p_f||^2.
Corrected LP: min sum_B d_f  s.t.  d_f(x_g,y_g) >= ell(g)O_fg  for g != f  (EXCLUDE self-edge),
   check optimum <= N*ell(f) - ell(f)*O_ff.  Then (Oell)_f <= ell(f)O_ff + opt <= N ell(f).
Part 1: characterize WHICH (graph,edge) the ORIGINAL LP fails on (is it exactly #badedges small / low overlap?).
Part 2: does the CORRECTED LP certify census-wide?  All float LP first."""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _crofton_lp import overlap_matrix, all_cuts

def lp_corrected(info,O,cuts,j,exclude_self=True):
    n=info['n']; M=info['M']; ell=info['ell']; N=n; m=len(M)
    f=M[j]; Off=O[j,j]
    rows=[g for g in range(m) if not (exclude_self and g==j)]
    b=np.array([ell[M[g]]*O[j,g] for g in rows])
    c=np.array([cu[0] for cu in cuts],dtype=float)
    Aub=np.zeros((len(rows),len(cuts)))
    for k,(dB,sep) in enumerate(cuts):
        for r,g in enumerate(rows): Aub[r,k]=-sep[g]
    res=linprog(c,A_ub=Aub,b_ub=-b,bounds=[(0,None)]*len(cuts),method='highs')
    if not res.success: return None
    opt=res.fun
    budget = N*ell[f] - (ell[f]*Off if exclude_self else 0)
    return opt, budget

def run(Nmax,Nmin=7,limit=None):
    print("--- ORIGINAL LP failure characterization + CORRECTED (diagonal-direct) LP ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        nt=0
        orig_fail=0; corr_fail=0; orig_fail_badedges=[]
        worst_corr=None; wc=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info); M=info['M']; ell=info['ell']; N=n
            for j in range(len(M)):
                # original
                from _crofton_lp import lp_f
                o0,t0=lp_f(info,O,cuts,j)
                if o0 is not None and o0>t0+1e-6:
                    orig_fail+=1; orig_fail_badedges.append(len(M))
                # corrected
                r=lp_corrected(info,O,cuts,j,exclude_self=True)
                if r:
                    opt,budget=r
                    gap=opt-budget
                    if gap>1e-6: corr_fail+=1
                    if worst_corr is None or gap>worst_corr: worst_corr=gap; wc=(g6,M[j],len(M))
        from collections import Counter
        be=Counter(orig_fail_badedges)
        print(f"  N={nn}: cfg={nt} | ORIG LP fails:{orig_fail} (on #badedges={dict(be)}) | CORRECTED LP fails:{corr_fail} (max gap={float(worst_corr) if worst_corr is not None else 0:+.4f} @ {wc})",flush=True)

if __name__=="__main__":
    run(9,7)
    run(10,10,limit=300)
