"""GPT's edge-capacitated OVERLAP-PACKING LP (primal, with x_g<=1 caps) — different from the dead cut-metric LP.
For each bad edge f:
   max sum_g O_fg * x_g   s.t.  0<=x_g<=1,  sum_g sep_A(g) x_g <= deltaB(A)  for all cuts A.
x_g=1 is feasible (sum_g sep_A(g) = deltaM(A) <= deltaB(A) by CD), with objective (O1)_f. So opt >= (O1)_f.
CLAIM (GPT): opt <= N. Then ROWSUM-O ((O1)_f<=N) follows. The x_g<=1 cap repairs the single-edge case
(where the cut-metric LP failed). Test census: is opt <= N? If yes, the LP dual = a proof of ROWSUM-O."""
import numpy as np
from scipy.optimize import linprog
import subprocess
from _h import dec, GENG, loads
from _crofton_lp import overlap_matrix, all_cuts

def overlap_lp(info, O, cuts, j):
    M=info['M']; m=len(M); N=info['n']
    c = -O[j,:]                          # maximize sum O_fg x_g  => minimize -()
    # constraints: sum_g sep_A(g) x_g <= deltaB(A)
    Aub=np.array([cu[1] for cu in cuts])        # rows = cuts, cols = g ; entries sep_A(g)
    bub=np.array([cu[0] for cu in cuts],dtype=float)
    res=linprog(c, A_ub=Aub, b_ub=bub, bounds=[(0,1)]*m, method='highs')
    if not res.success: return None
    return -res.fun                       # the max objective

def run(Nmax,Nmin=7,limit=None):
    print("--- GPT overlap-packing LP: opt <= N ? (=> ROWSUM-O) ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        nt=0; bad=0; worst=None; wg=None; rowsum_bad=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info); N=n
            for j in range(len(info['M'])):
                opt=overlap_lp(info,O,cuts,j)
                if opt is None: continue
                gap=opt-N
                if gap>1e-6: bad+=1
                if worst is None or gap>worst: worst=gap; wg=(g6,info['M'][j])
                # also confirm (O1)_f = row sum <= opt (sanity)
                rs=O[j,:].sum()
                if rs>N+1e-6: rowsum_bad+=1
        print(f"  N={nn}: cfg={nt} | overlap-LP opt>N count:{bad} | max(opt-N)={worst:+.5f}@{wg} | (O1)_f>N:{rowsum_bad}",flush=True)

if __name__=="__main__":
    # single-edge graphs first (where cut-metric LP failed): F?o~_, H??F?~{
    print("=== single-bad-edge graphs (cut-metric LP failed here) ===")
    for g6 in ["F?o~_","H??F?~{","I???F?\\~_"]:
        n,E=dec(g6); info=loads(n,E)
        O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info)
        for j in range(len(info['M'])):
            opt=overlap_lp(info,O,cuts,j)
            print(f"  {g6}: bad edge {info['M'][j]} | overlap-LP opt={opt:.4f} <= N={n}? {opt<=n+1e-6} | (O1)_f={O[j,:].sum():.4f}")
    run(9,7)
    run(10,10,limit=400)
