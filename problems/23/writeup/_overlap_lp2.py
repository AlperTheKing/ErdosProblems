"""Full-census + dual-structure + blow-up stress for GPT's overlap-packing LP.
LP-f: max sum_g O_fg x_g s.t. 0<=x_g<=1, sum_g sep_A(g) x_g <= deltaB(A) for all cuts A.  Claim opt<=N.
Dual: min sum_A lam_A deltaB(A) + sum_g mu_g  s.t.  sum_A lam_A sep_A(g) + mu_g >= O_fg,  lam,mu>=0.
(cut metric + per-pair cap rebate mu_g). Dump which cuts+caps bind (does it generalize?).
Stress: small blow-ups (N<=15 feasible via full cut enum)."""
import numpy as np
from scipy.optimize import linprog
import subprocess
from _h import dec, GENG, loads
from _crofton_lp import overlap_matrix, all_cuts

def overlap_lp(O, cuts, j, N, m, want_dual=False):
    c=-O[j,:]
    Aub=np.array([cu[1] for cu in cuts]); bub=np.array([cu[0] for cu in cuts],dtype=float)
    res=linprog(c,A_ub=Aub,b_ub=bub,bounds=[(0,1)]*m,method='highs')
    if not res.success: return None,None
    opt=-res.fun
    dual=None
    if want_dual:
        # x at optimum; which constraints bind
        x=res.x
        dual={'x':x,'binding_cuts':[k for k in range(len(cuts)) if abs(Aub[k]@x-bub[k])<1e-7 and bub[k]>0],
              'capped_g':[g for g in range(m) if x[g]>1-1e-7]}
    return opt,dual

def blowup(n,E,t):
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE

def run_census(Nmax,Nmin=10,stride=1):
    print(f"--- overlap-LP opt<=N over census (stride {stride}) ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        out=out[::stride]
        nt=0; bad=0; worst=None; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info); m=len(info['M'])
            for j in range(m):
                opt,_=overlap_lp(O,cuts,j,n,m)
                if opt is None: continue
                gap=opt-n
                if gap>1e-6: bad+=1
                if worst is None or gap>worst: worst=gap; wg=(g6,info['M'][j])
        print(f"  N={nn}: cfg={nt} | opt>N count:{bad} | max(opt-N)={worst:+.5f}@{wg}",flush=True)

def stress_blowups():
    print("--- overlap-LP on small blow-ups (stress) ---")
    cases=[("DUW",2),("DUW",3),("F?o~_",2),("H??F?~{",2),("I?BD@g]Qo",1)]
    # C5/C7 small blowups
    def Cblow(k,q):
        L=2*k+1; m=L*q; E=[]
        for i in range(L):
            for a in range(q):
                for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
        return m,E
    items=[]
    for g6,t in cases:
        n,E=dec(g6); nn,EE=blowup(n,E,t); items.append((f"{g6}[{t}]",nn,EE))
    for (k,q) in [(2,2),(2,3),(3,2)]:
        m,E=Cblow(k,q); items.append((f"C{2*k+1}[{q}]",m,E))
    for label,nn,EE in items:
        if nn>15: print(f"  {label} N={nn}: skip (cut enum too big)"); continue
        info=loads(nn,EE)
        if info is None: print(f"  {label}: skip"); continue
        O,P,pf=overlap_matrix(info); cuts=all_cuts(nn,info); m=len(info['M'])
        worst=None
        for j in range(m):
            opt,_=overlap_lp(O,cuts,j,nn,m)
            if opt is None: continue
            if worst is None or opt-nn>worst: worst=opt-nn
        print(f"  {label} N={nn} Gamma={info['G']} | max(opt-N)={worst:+.5f} ({'OK' if worst<=1e-6 else 'FAIL'})")

def dump_dual():
    print("--- dual structure (binding cuts + capped edges) on representative graphs ---")
    for g6 in ["FCp`_","H?bB@_W","I?ABCc]}?","F?o~_"]:
        n,E=dec(g6); info=loads(n,E)
        O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info); m=len(info['M'])
        for j in range(min(m,2)):
            opt,dual=overlap_lp(O,cuts,j,n,m,want_dual=True)
            ncap=len(dual['capped_g']); ncut=len(dual['binding_cuts'])
            print(f"  {g6} f={info['M'][j]} N={n}: opt={opt:.3f} (O1={O[j,:].sum():.3f}) | #capped(x_g=1)={ncap}/{m} | #binding cuts={ncut}")

if __name__=="__main__":
    dump_dual()
    stress_blowups()
    run_census(10,10,stride=1)
    run_census(11,11,stride=25)
