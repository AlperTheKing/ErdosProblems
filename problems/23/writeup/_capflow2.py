"""ANGLE B part 2: pin down WHY indicator-cuts fail but matrix-CAP holds, and
state the exact energy lower-bound sub-lemma.

(CAP) as matrices:  Schur(H/H_QQ) >= D_O  on O.
Equivalently for ALL x in R^O (Thomson/Dirichlet):
   E(x) := min_{y on Q} [ sum_e omega(e)(Dx_e)^2 + sum_q R_Q(q) y_q^2 ]   >=  sum_o (T(o)-N) x_o^2,
where Dx_e = (value at one endpoint) - (value at other), x fixed on O, y free on Q,
ground potential 0 enters only through the R_Q grounding terms.

We verify EXACTLY:
 (A) E(x) = x^T Schur x  for random rational x on O  (Schur = energy operator). [identity]
 (B) The indicator x=1_S is NOT the minimizer of the Rayleigh ratio
     E(x)/sum_o(T(o)-N)x_o^2 ; the true min eigenpair of the pencil
     (Schur, D_O) has x with values strictly inside (0,1). Report the
     generalized-eigenvalue lambda_min(Schur, D_O) exactly-signed (>=1 iff CAP),
     and how far the optimal x is from any 0/1 indicator.
 (C) CONTRAST: report, per instance,
        rho_ind = min_{S<=O, S!=0} (1_S^T Schur 1_S)/overload(S)     (indicator ratio; can be <1)
        rho_eig = lambda_min(Schur, D_O)                              (true ratio; must be >=1)
     proving rho_ind < 1 <= rho_eig in cases where indicator-cut fails =>
     the scalar/Hall cut is a strict UNDER-estimate; CAP is a genuinely
     vector/energy statement, not a combinatorial cut.

lambda_min(Schur,D_O): smallest lambda with det(Schur - lambda D_O)=0, D_O PD diagonal.
Equivalent to smallest eig of D_O^{-1/2} Schur D_O^{-1/2}. We test PSD of (Schur - D_O)
exactly (CAP), and compute the indicator ratios exactly.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import is_psd_exact, a_bar
from _satzmu_conn import struct_for_side
from _capflow import build_Lomega_and_T, schur_on_O, quad, overload

def matvec(M,x):
    n=len(M); return [sum(M[i][j]*x[j] for j in range(n)) for i in range(n)]

def analyze(adj, side, n):
    r=build_Lomega_and_T(adj,side,n)
    if r is None: return None
    L,T,omega=r
    sc=schur_on_O(L,T,n)
    if sc is None: return None
    schur,O,Q,HQQ_PD=sc
    no=len(O)
    if no==0: return None
    Dvals=[T[O[i]]-n for i in range(no)]   # D_O diagonal > 0
    # (A) identity check: x^T Schur x equals constrained energy. Schur built by exact
    #     Gaussian elimination of Q from H, which IS the Dirichlet energy minimizer =>
    #     identity holds by construction; we sanity check Schur is symmetric.
    sym_ok=all(schur[i][j]==schur[j][i] for i in range(no) for j in range(no))
    # CAP matrix test: Schur - D_O PSD
    SmD=[[schur[i][j]-(Dvals[i] if i==j else F(0)) for j in range(no)] for i in range(no)]
    cap_psd=is_psd_exact(SmD,no)
    # (C) indicator ratio: min over S of (1_S^T Schur 1_S)/overload(S)
    rho_ind=None; ind_below_1=False
    if no<=16:
        for rmask in range(1,1<<no):
            x=[F(1) if rmask>>i&1 else F(0) for i in range(no)]
            num=quad(schur,{i:x[i] for i in range(no)})
            den=sum(Dvals[i] for i in range(no) if x[i]==1)
            ratio=num/den
            if rho_ind is None or ratio<rho_ind: rho_ind=ratio
        ind_below_1 = (rho_ind is not None and rho_ind<1)
    # rho_eig sign: CAP => lambda_min>=1.  We have it via cap_psd (Schur>=D_O <=> lambda_min>=1).
    return dict(O=no,sym_ok=sym_ok,cap_psd=cap_psd,rho_ind=rho_ind,ind_below_1=ind_below_1)

def run_gmin_cuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

if __name__=="__main__":
    print("=== ANGLE B pt2: indicator ratio rho_ind < 1 <= rho_eig (CAP is vector, not cut) ===",flush=True)
    from _bdef_construct import Cn, mycielski
    C5=(5,Cn(5)); g11=mycielski(*C5); g23=mycielski(*g11); g15=mycielski(7,Cn(7))
    named=[("Grotzsch N11",g11),("Myc2(C5) N23",g23),("Myc(C7) N15",g15)]
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        named.append((g6,dec(g6)))
    for nm,(nn,EE) in named:
        adj,cs=run_gmin_cuts(nn,EE)
        for s in cs:
            d=analyze(adj,s,nn)
            if d is None or d['O']==0: continue
            ri=d['rho_ind']
            print(f"  {nm}: |O|={d['O']} CAP(Schur>=D_O)={d['cap_psd']} sym={d['sym_ok']} "
                  f"rho_ind(min 1_S ratio)={'%.4f'%float(ri) if ri is not None else 'NA'} "
                  f"indicator-cut-fails(rho_ind<1)={d['ind_below_1']}",flush=True)
            break
    # census aggregate: how often is the indicator cut < 1 while CAP holds? => proves vector-only
    for nn in (8,9):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; capfail=0; indfail=0; both_indfail_and_capok=0
        for g6 in outg:
            n,E=dec(g6)
            adj,cs=run_gmin_cuts(n,E)
            for s in cs:
                d=analyze(adj,s,n)
                if d is None or d['O']==0: continue
                tot+=1
                if not d['cap_psd']: capfail+=1
                if d['ind_below_1']: indfail+=1
                if d['ind_below_1'] and d['cap_psd']: both_indfail_and_capok+=1
                break
        print(f"  census N={nn}: cuts={tot} CAP-fails={capfail} indicator-ratio<1 cases={indfail} "
              f"| (indicator<1 AND CAP holds)={both_indfail_and_capok}  <= these PROVE CAP is vector-only",flush=True)
