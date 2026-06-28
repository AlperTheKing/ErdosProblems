"""GPT's CD-Crofton certificate test (LP-f) for proving (Cycle-SM) => rho(O)<=N => Gamma<=N^2.
For each bad edge f, solve:
   minimize  sum_A lambda_A * delta_B(A)
   s.t.      sum_A lambda_A * sep_A(g) >= ell(g)*<p_f,p_g>   for all bad edges g
             lambda_A >= 0
   over all cuts A (vertex subsets, A and complement identified). sep_A(g)=1 iff A separates g's endpoints.
CLAIM (GPT): optimum <= N*ell(f). If TRUE for all f, all graphs => CD proves Cycle-SM constructively:
   sum_v p_f(v)T(v) = sum_g ell(g)<p_f,p_g> <= sum_g d_f(x_g,y_g) = sum_A lam_A dM(A) <= sum_A lam_A dB(A) <= N ell(f).
The middle <= is CD (dM(A)<=dB(A)). Tests census; reports max over f of (LP_opt - N*ell(f)) (>0 = CD insufficient).
Float LP (scipy highs) first; exact rational follow-up if it certifies."""
import numpy as np
from itertools import combinations
import subprocess
from scipy.optimize import linprog
from fractions import Fraction as F
from _h import dec, GENG, loads

def overlap_matrix(info):
    n=info['n']; M=info['M']; cyc=info['cyc']; ell=info['ell']
    m=len(M)
    P=np.zeros((n,m))
    pf=[]
    for j,f in enumerate(M):
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        d={v:cnt[v]/nf for v in cnt}
        pf.append(d)
        for v,c in d.items(): P[v,j]=c
    O=P.T@P
    return O,P,pf

def all_cuts(n,info):
    """enumerate cuts A (subsets, 1..2^(n-1)-1 to dedup complement). Return list of (deltaB(A), sep-vector over M)."""
    M=info['M']; Bset=info['Bset']; m=len(M)
    cuts=[]
    for mask in range(1, 1<<(n-1)):
        A=set(v for v in range(n) if (mask>>v)&1)
        dB=sum(1 for (a,b) in Bset if (a in A)!=(b in A))
        sep=np.array([1.0 if ((g[0] in A)!=(g[1] in A)) else 0.0 for g in M])
        cuts.append((dB,sep))
    return cuts

def lp_f(info, O, cuts, j):
    """solve LP-f for bad edge index j. returns (opt, N*ell(f))."""
    n=info['n']; M=info['M']; ell=info['ell']; N=n; m=len(M)
    f=M[j]
    b=np.array([ell[M[g]]*O[j,g] for g in range(m)])     # ell(g)*<p_f,p_g>
    ncuts=len(cuts)
    c=np.array([cu[0] for cu in cuts],dtype=float)       # objective: deltaB(A)
    # constraints: sum_A lam_A sep_A(g) >= b_g  ->  -A_ub lam <= -b
    Aub=np.zeros((m,ncuts))
    for k,(dB,sep) in enumerate(cuts):
        Aub[:,k]=-sep
    bub=-b
    res=linprog(c, A_ub=Aub, b_ub=bub, bounds=[(0,None)]*ncuts, method='highs')
    if not res.success: return None, N*ell[f]
    return res.fun, N*ell[f]

def run(Nmax,Nmin=7,limit=None):
    print("--- (LP-f) CD-Crofton certificate: opt <= N*ell(f) ? ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        nt=0; worst=None; wg=None; bad=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info)
            for j in range(len(info['M'])):
                opt,target=lp_f(info,O,cuts,j)
                if opt is None: continue
                gap=opt-target
                if worst is None or gap>worst: worst=gap; wg=(g6,info['M'][j])
                if gap>1e-6: bad+=1
        print(f"  N={nn}: cfg={nt} | (f with LP_opt>N*ell) count:{bad} | max(LP_opt - N*ell(f))={worst:+.5f} @ {wg}",flush=True)

if __name__=="__main__":
    # start with tight graphs + small census to see if it certifies at all
    print("=== tight graphs (T==N, Gamma=N^2) ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info)
        worst=None
        for j in range(len(info['M'])):
            opt,target=lp_f(info,O,cuts,j)
            if opt is None: continue
            g=opt-target
            if worst is None or g>worst: worst=g
        print(f"  {g6}: max(LP_opt - N*ell)={worst:+.5f}")
    run(9,7)
    run(10,10,limit=400)
