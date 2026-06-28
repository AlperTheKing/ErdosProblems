"""ANGLE B pt3 (CORRECTED): pure effective-conductance matrix Y_eff vs overload D_O.

Two equivalent Schur forms (Q-block pivot uses H_QQ=L_{omega,QQ}+R_Q in BOTH):
  schurH   = Schur(H / H_QQ)         (O-diagonal carries -D_O)   CAP <=> schurH >= 0
  Y_eff    = Schur(L_omega / H_QQ)   pure conductance from O      CAP <=> Y_eff >= D_O
  Relation:  Y_eff = schurH + D_O.

Y_eff is the effective-conductance (Dirichlet-to-Neumann) matrix of the omega
network grounded by R_Q on Q, restricted to the overloaded boundary O. It is a
bona fide Laplacian-type (weighted, with leakage to ground) operator: PSD, and
1^T(Y_eff over all of O)... we test its electrical properties exactly.

Tests:
 (A) Y_eff = schurH + D_O exactly, and Y_eff is PSD (effective conductance is PSD).  [identity/structure]
 (B) Y_eff is a valid grounded-Laplacian response: x^T Y_eff x >= 0 for all x, and
     equals the Dirichlet energy min over y on Q (= electrical interpretation).  [PSD check]
 (C) CAP matrix:  Y_eff - D_O = schurH  >= 0.   (the real lemma)
 (D) Indicator/Hall ratio on the CONDUCTANCE object:
        rho_ind = min_{S<=O} (1_S^T Y_eff 1_S)/overload(S).
     CAP-matrix needs lambda_min(Y_eff,D_O)>=1; the indicator gives an UPPER bound on...
     actually 1_S^T Y_eff 1_S is the energy to hold S at 1, rest of O at 0 -> this is
     an effective conductance between S and (O\S +ground). Compare to overload(S).
     Report whether indicator ratio >= 1 (Hall holds) or < 1 (indicator insufficient),
     AND whether CAP-matrix holds, to see if scalar-cut is necessary/sufficient.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import is_psd_exact, a_bar
from _capflow import build_Lomega_and_T, schur_on_O, quad, overload

def schur_Lomega_on_O(L,T,n):
    """Y_eff = Schur(L_omega / (L_omega,QQ+R_Q)) restricted to O.
       Pivot Q-block of the matrix  Lpls = L_omega + diag(R on Q, 0 on O), R=N-T on Q.
       (On O we keep pure L_omega diagonal; the -D_O is NOT added here.)"""
    N=n
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    perm=O+Q; no=len(O)
    A=[[L[perm[i]][perm[j]] for j in range(n)] for i in range(n)]
    # add R_Q on Q diagonal only
    for k in range(no,n):
        A[k][k]+=F(N)-T[perm[k]]
    Mm=[row[:] for row in A]
    for q in range(no,n):
        d=Mm[q][q]
        if d<=0: return None
        for i in range(n):
            if i==q or Mm[i][q]==0: continue
            fac=Mm[i][q]/d
            for j in range(n): Mm[i][j]-=fac*Mm[q][j]
    Yeff=[[Mm[i][j] for j in range(no)] for i in range(no)]
    return Yeff,O,Q

def analyze(adj, side, n):
    r=build_Lomega_and_T(adj,side,n)
    if r is None: return None
    L,T,omega=r
    scH=schur_on_O(L,T,n)
    scY=schur_Lomega_on_O(L,T,n)
    if scH is None or scY is None: return None
    schurH,O,Q,_=scH
    Yeff,O2,Q2=scY
    no=len(O)
    Dvals=[T[O[i]]-n for i in range(no)]
    # (A) Y_eff = schurH + D_O exactly
    idA=all(Yeff[i][j]==schurH[i][j]+(Dvals[i] if i==j else F(0)) for i in range(no) for j in range(no))
    # (B) Y_eff PSD
    Ypsd=is_psd_exact([row[:] for row in Yeff],no)
    # (C) CAP: Y_eff - D_O = schurH PSD
    cap=is_psd_exact([row[:] for row in schurH],no)
    # (D) indicator ratio on Y_eff
    rho_ind=None
    if no<=16:
        for rmask in range(1,1<<no):
            x={i:(F(1) if rmask>>i&1 else F(0)) for i in range(no)}
            num=quad(Yeff,x)
            den=sum(Dvals[i] for i in range(no) if x[i]==1)
            ratio=num/den
            if rho_ind is None or ratio<rho_ind: rho_ind=ratio
    return dict(O=no,idA=idA,Ypsd=Ypsd,cap=cap,rho_ind=rho_ind,
                ind_ge1=(rho_ind is not None and rho_ind>=1))

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
    print("=== ANGLE B pt3: Y_eff (effective conductance) vs D_O; indicator-cut necessity/sufficiency ===",flush=True)
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
            print(f"  {nm}: |O|={d['O']} Yeff=schurH+D_O={d['idA']} Yeff-PSD={d['Ypsd']} "
                  f"CAP(Yeff>=D_O)={d['cap']} rho_ind={'%.4f'%float(ri) if ri is not None else 'NA'} "
                  f"indicatorHall(rho_ind>=1)={d['ind_ge1']}",flush=True)
            break
    for nn in (8,9,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; capfail=0; idfail=0; hall_holds_all=0; hall_fail=0; hall_fail_but_cap_ok=0
        for g6 in outg:
            n,E=dec(g6)
            adj,cs=run_gmin_cuts(n,E)
            for s in cs:
                d=analyze(adj,s,n)
                if d is None or d['O']==0: continue
                tot+=1
                if not d['cap']: capfail+=1
                if not d['idA']: idfail+=1
                if d['ind_ge1']: hall_holds_all+=1
                else:
                    hall_fail+=1
                    if d['cap']: hall_fail_but_cap_ok+=1
                break
        print(f"  census N={nn}: cuts={tot} CAP-fails={capfail} idA-fails={idfail} "
              f"| indicatorHall holds={hall_holds_all} fails={hall_fail} "
              f"(Hall FAILS but CAP HOLDS)={hall_fail_but_cap_ok} <= proves indicator-cut INSUFFICIENT",flush=True)
