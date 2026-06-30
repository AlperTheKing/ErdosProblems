"""DECISIVE TEST v2 of GPT-Pro's round-2 CORRECTED (A) coarea LP:
   - DELETE M2 (no both-endpoints gate; E_0 enters only as scalar shift in (S)).
   - SUBGRADIENT theta over active minimizers A={r: h_r h_{r+1}=q}: a_i(theta)=2S-L^2 sum_{r in A} theta_r(h_{r+1}1_{i=r}+h_r 1_{i=r+1}).
   Variables: lambda_W>=0 (switches W(J,Y)), theta_r>=0 (r in A).
   Constraints:
     (Theta) sum_{r in A} theta_r = 1
     (M0)    sum_W lambda_W sigma(W) = 0
     (M1')   sum_W lambda_W 1_{x_i in W}  -  (L^2/(2N)) sum_{r in A} theta_r (h_{r+1}1_{i=r}+h_r 1_{i=r+1}) = L/5 - S/N   (all i)
     (S)     sum_W lambda_W DGamma(W) = (L/5)(N^2-Gamma) - E_0 - L^2*delta
   Feasible => (A) holds via gamma-minimality.  Float linprog verdict.  Usage: python _coareaA_lp2.py [g6] [side]
"""
import sys, itertools
from fractions import Fraction as F
from _crux_extract import components_off_path
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _coareaA_lp import switch_family
try:
    import numpy as np
    from scipy.optimize import linprog
    HAVE=True
except Exception:
    HAVE=False

def test_row(n,adj,side,M,ell,T,cyc,f,P):
    L=ell[f]; N=F(n); Gamma=sum(ell[g]**2 for g in M)
    h=[T[P[i]]/N for i in range(L)]; S=sum(h)
    prods=[h[i]*h[(i+1)%L] for i in range(L)]; q=min(prods)
    A=[r for r in range(L) if prods[r]==q]            # active minimizers (ties)
    L2delta=S*S-L*L*q
    chiP=[0]*n
    for end in (P[0],P[-1]):
        ch=endpt_chi(n,adj,side,end,M,n)
        for rr in range(n): chiP[rr]+=ch[rr]
    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
    TARGET=F(L,5)*(N*N-Gamma)-E0-L2delta
    cols=[]
    for W in switch_family(n,adj,side,P):
        s2=flip(side,W)
        if not Bconn(n,adj,s2): continue
        g1=gamma_of(n,adj,s2)
        if g1 is None: continue
        dB,dM=deltas(n,adj,side,W); sigma=dB-dM
        if sigma<0: continue
        tau=[1 if P[i] in W else 0 for i in range(L)]
        cols.append((sigma,tau,g1-Gamma))
    if not cols: return ('NOCOLS',None)
    m=len(cols); na=len(A)
    nv=m+na   # [lambda_0..lambda_{m-1}, theta_{A[0]}..]
    rows=[]; b=[]
    # (Theta)
    row=[0.0]*nv
    for j in range(na): row[m+j]=1.0
    rows.append(row); b.append(1.0)
    # (M0)
    row=[float(cols[k][0]) for k in range(m)]+[0.0]*na
    rows.append(row); b.append(0.0)
    # (M1') for each i
    rhs_const=F(L,5)-S/N
    for i in range(L):
        row=[float(cols[k][1][i]) for k in range(m)]
        for j,r in enumerate(A):
            coef = -(F(L*L,2*N))*((h[(r+1)%L] if i==r else 0)+(h[r] if i==(r+1)%L else 0))
            row.append(float(coef))
        rows.append(row); b.append(float(rhs_const))
    # (S)
    row=[float(cols[k][2]) for k in range(m)]+[0.0]*na
    rows.append(row); b.append(float(TARGET))
    if not HAVE: return ('NOSCIPY',None)
    Aeq=np.array(rows); beq=np.array(b)
    res=linprog(c=np.zeros(nv),A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*nv,method='highs')
    return ('OK',res.success)

def main():
    g6=sys.argv[1] if len(sys.argv)>1 else "H?AFBo]"
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    if len(sys.argv)>2: cuts=[[int(c) for c in sys.argv[2]]]
    else: _,cuts=gmins(n,E)
    print("g6=%s %d gamma-min cuts scipy=%s  (corrected v2: no M2, theta-subgradient)"%(g6,len(cuts),HAVE))
    rows=feas=infeas=nocol=0
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                tag,fe=test_row(n,adj,side,M,ell,T,cyc,f,list(P))
                rows+=1
                if tag=='NOCOLS': nocol+=1; continue
                if fe: feas+=1
                else: infeas+=1
    print("rows=%d  FEASIBLE=%d  INFEASIBLE=%d  no-col=%d"%(rows,feas,infeas,nocol))
    print("VERDICT:", "CORRECTED COAREA LP FEASIBLE on ALL rows -- A ROUTE SURVIVES" if infeas==0 and feas>0 else ("INFEASIBLE rows remain" if infeas>0 else "no rows"))

if __name__=="__main__":
    main()
