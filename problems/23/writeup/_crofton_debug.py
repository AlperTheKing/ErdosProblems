"""Debug the LP-failing graphs: confirm (Cycle-SM) HOLDS there (else bug), dump structure, and the
binding LP constraint. Distinguishes 'CD-cuts genuinely insufficient' from 'LP/formulation bug'."""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
from _h import dec, loads
from _crofton_lp import overlap_matrix, all_cuts

def debug(g6):
    n,E=dec(g6); info=loads(n,E); N=n
    O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info)
    M=info['M']; ell=info['ell']; T=info['T']
    print(f"\n=== {g6} N={n} Gamma={info['G']} (N^2={n*n}) #badedges={len(M)} ===")
    print(f"  T = {[float(t) for t in T]}")
    print(f"  bad edges M = {M}, ell = {[ell[f] for f in M]}")
    for j,f in enumerate(M):
        # exact Cycle-SM check
        s=sum(sum(T[v] for v in P2) for P2 in info['cyc'][f]); nf=len(info['cyc'][f])
        lhs=F(s,nf)                      # sum_v p_f(v)T(v) exact
        rhs=N*ell[f]
        # LP
        m=len(M)
        b=np.array([ell[M[g]]*O[j,g] for g in range(m)])
        c=np.array([cu[0] for cu in cuts],dtype=float)
        Aub=np.zeros((m,len(cuts)))
        for k,(dB,sep) in enumerate(cuts): Aub[:,k]=-sep
        res=linprog(c,A_ub=Aub,b_ub=-b,bounds=[(0,None)]*len(cuts),method='highs')
        opt=res.fun if res.success else None
        tag=""
        if opt is not None and opt>rhs+1e-6: tag="  <<< LP FAILS (CD-cut insufficient)"
        flag_cs = "CycleSM HOLDS" if lhs<=rhs else "CYCLE-SM FAILS(!!)"
        print(f"  f={f} ell={ell[f]} | Cycle-SM: sum p_f T = {float(lhs):.3f} <= N*ell={rhs} ? {flag_cs} | LP opt={opt:.3f} vs N*ell={rhs}{tag}")
        # show c_g(f) vector (lower bounds)
        cg=[float(ell[M[g]]*O[j,g]) for g in range(m)]
        print(f"      c_g(f)=ell(g)<p_f,p_g> = {[round(x,2) for x in cg]}  (sum={sum(cg):.3f} = sum_v p_f T)")

if __name__=="__main__":
    for g6 in ["F?o~_","H??F?~{","I???F?\\~_"]:
        debug(g6)
