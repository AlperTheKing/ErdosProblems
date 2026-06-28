"""Analyze the overlap-LP DUAL certificate (lam_A cuts + mu_g caps) to find a UNIFORM construction
=> a proof of ROWSUM-O via weak duality. For each bad edge f, extract from the LP:
  lam_A (marginals of cut constraints), mu_g (marginals of x_g<=1 caps).
Dual feasibility: sum_A lam_A sep_A(g) + mu_g >= O_fg for all g; value sum_A lam_A deltaB(A) + sum_g mu_g = (O1)_f.
Look for structure: is mu_g ~ O_fg for the 'diagonal-like' g (g=f and tightly-overlapping)? Are binding cuts the
geodesic-interval gate cuts {d_B(a,.)<=i}? Does mu_f = O_ff (diagonal handled by cap)?"""
import numpy as np
from scipy.optimize import linprog
from collections import deque
from _h import dec, loads
from _crofton_lp import overlap_matrix, all_cuts

def gate_cuts(info,f):
    """geodesic-interval gate cuts G_i={v: d_B(a,v)<=i} of bad edge f=(a,b); return list of frozenset(A)."""
    a,b=f; n=info['n']; adj=info['adj']; side=info['side']
    da={a:0}; q=deque([a])
    while q:
        x=q.popleft()
        for y in adj[x]:
            if side[x]!=side[y] and y not in da: da[y]=da[x]+1; q.append(y)
    h=info['ell'][f]-1
    gates=[]
    for i in range(h):
        A=frozenset(v for v in da if da[v]<=i)
        gates.append(A)
    return gates

def analyze(g6):
    n,E=dec(g6); info=loads(n,E); N=n
    O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info); M=info['M']; m=len(M)
    cutsets=[frozenset(v for v in range(n) if (mask:=k+1) and ((k+1)>>v)&1) for k in range(len(cuts))]
    # rebuild cut subsets properly
    cutsets=[]
    for kk in range(1,1<<(n-1)):
        cutsets.append(frozenset(v for v in range(n) if (kk>>v)&1))
    print(f"\n=== {g6} N={n} Gamma={info['G']} ===")
    for j,f in enumerate(M):
        c=-O[j,:]; Aub=np.array([cu[1] for cu in cuts]); bub=np.array([cu[0] for cu in cuts],dtype=float)
        res=linprog(c,A_ub=Aub,b_ub=bub,bounds=[(0,1)]*m,method='highs')
        if not res.success: continue
        opt=-res.fun
        lam=-res.ineqlin.marginals          # dual of cut constraints (>=0)
        mu=-res.upper.marginals             # dual of x_g<=1 (>=0)
        val=sum(lam[k]*bub[k] for k in range(len(cuts)))+mu.sum()
        gates=set(gate_cuts(info,f))
        used=[(k,lam[k]) for k in range(len(cuts)) if lam[k]>1e-7]
        used_are_gates=all((cutsets[k] in gates or (frozenset(range(n))-cutsets[k]) in gates) for k,_ in used)
        print(f"  f={f} ell={info['ell'][f]}: opt={opt:.3f} (O1={O[j,:].sum():.3f}) dualval={val:.3f} | #cuts_used={len(used)} all_gates={used_are_gates} | mu_f={mu[j]:.3f} O_ff={O[j,j]:.3f} | sum mu={mu.sum():.3f} sum lam*dB={sum(lam[k]*bub[k] for k in range(len(cuts))):.3f}")
        # per-g: is mu_g + (cut contribution) >= O_fg, and how is O_fg split?
        cutcontrib=Aub.T@lam   # sum_A lam_A sep_A(g) for each g
        # show the split for a few g
        splits=[(M[g],float(O[j,g]),float(mu[g]),float(cutcontrib[g])) for g in range(m)]
        print(f"      O_fg vs (mu_g, cutcontrib_g): {[(str(gg),round(o,2),round(mm,2),round(cc,2)) for gg,o,mm,cc in splits]}")

if __name__=="__main__":
    for g6 in ["F?o~_","FCp`_","H?bB@_W","I?ABCc]}?"]:
        analyze(g6)
