"""Test the user's GEODESIC-MEASURE MAJORIZATION / Collatz-Wielandt price-cap route for (A).
   nu_g(v) = p_g(v)/L_g  (prob measure; p_g(v)=through-fraction = avg over Q in cyc[g] of 1_{v in Q}; sum_v p_g=L_g).
   T(v)/Gamma = sum_g (L_g^2/Gamma) nu_g(v)  =>  T/Gamma in conv{nu_g}.
   Active face A(P)={r: h_r h_{r+1}=q}.  theta in Delta(A).  a_i(theta)=2S - L^2(theta_i h_{i+1}+theta_{i-1} h_{i-1}).
   Row price pi(x_i)=L/5 + a_i(theta)/(2N), pi(v)=L/5 off-path.  Cap R_P = (L/5)(N^2/Gamma) - E_0/Gamma.
   (GPM):  exists theta s.t.  <pi, nu_g> <= R_P  for every bad edge g.   <=>  for each g:
        sum_i a_i(theta) p_g(x_i)  <=  (2 N L_g / Gamma)[ (L/5)(N^2-Gamma) - E_0 ].
   Feasible (theta>=0, sum theta=1, all |M| constraints) => (A) holds on the row (via convexity of T/Gamma).
   Also test stronger PATHWISE form (PGPM): per geodesic Q of g, sum_{x_i in Q} a_i(theta) <= same-RHS-with L_g=ell_g.
   Usage: python _gpm_lp.py [g6] [side]   default: H?AFBo] gamma-min + a census sweep flag.
"""
import sys, subprocess, random
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
import numpy as np
from scipy.optimize import linprog

def pg_through(cyc_g):
    """p_g(v) = (1/|cyc_g|) #{Q: v in Q}; returns dict."""
    k=len(cyc_g); cnt={}
    for Q in cyc_g:
        for v in set(Q): cnt[v]=cnt.get(v,0)+1
    return {v:F(cnt[v],k) for v in cnt}

def a_of_theta(theta_vec, A, L, S, h):
    """a_i(theta) for i=0..L-1 given theta on active face A (list), theta_vec aligned to A."""
    th=[F(0)]*L
    for j,r in enumerate(A): th[r]=theta_vec[j]
    a=[2*S - L*L*(th[i]*h[(i+1)%L] + th[(i-1)%L]*h[(i-1)%L]) for i in range(L)]
    return a

def test_row(n,adj,side,M,ell,T,cyc,f,P, pathwise=False):
    L=ell[f]; N=F(n); Gamma=sum(ell[g]**2 for g in M)
    h=[T[P[i]]/N for i in range(L)]; S=sum(h)
    prods=[h[i]*h[(i+1)%L] for i in range(L)]; q=min(prods)
    A=[r for r in range(L) if prods[r]==q]
    chiP=[0]*n
    for end in (P[0],P[-1]):
        ch=endpt_chi(n,adj,side,end,M,n)
        for rr in range(n): chiP[rr]+=ch[rr]
    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
    capbracket=F(L,5)*(N*N-Gamma) - E0
    na=len(A)
    # constant a_i(0)=2S; linear coef of theta_r: a_i(e_r)-2S
    base=[2*S]*L
    coefs=[]  # coefs[j][i] = a_i(e_{A[j]}) - 2S
    for j in range(na):
        ev=[F(0)]*na; ev[j]=F(1)
        a_ev=a_of_theta(ev,A,L,S,h)
        coefs.append([a_ev[i]-2*S for i in range(L)])
    # constraints
    A_ub=[]; b_ub=[]
    if not pathwise:
        for g in M:
            pgv=pg_through(cyc[g])
            pp=[pgv.get(P[i],F(0)) for i in range(L)]
            const_g=sum(base[i]*pp[i] for i in range(L))   # = 2S * sum pp
            row=[sum(coefs[j][i]*pp[i] for i in range(L)) for j in range(na)]
            rhs=F(2*N*ell[g],Gamma)*capbracket
            A_ub.append([float(c) for c in row]); b_ub.append(float(rhs-const_g))
    else:
        for g in M:
            for Q in cyc[g]:
                Qset=set(Q)
                pp=[F(1) if P[i] in Qset else F(0) for i in range(L)]
                const_g=sum(base[i]*pp[i] for i in range(L))
                row=[sum(coefs[j][i]*pp[i] for i in range(L)) for j in range(na)]
                rhs=F(2*N*ell[g],Gamma)*capbracket
                A_ub.append([float(c) for c in row]); b_ub.append(float(rhs-const_g))
    A_eq=[[1.0]*na]; b_eq=[1.0]
    res=linprog(c=np.zeros(na),A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),
                bounds=[(0,None)]*na,method='highs')
    return res.success

def run_graph(name,n,E,acc,cuts=None,pathwise=False):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    if cuts is None:
        try: _,cuts=gmins(n,E)
        except Exception: return
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
                ok=test_row(n,adj,side,M,ell,T,cyc,f,list(P),pathwise=pathwise)
                acc['rows']+=1
                if ok: acc['feas']+=1
                else:
                    acc['infeas']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,''.join(map(str,side)),f,tuple(P))

def main():
    mode='gpm'
    pathwise='--pathwise' in sys.argv
    print("MODE:", "PATHWISE (PGPM)" if pathwise else "averaged (GPM)")
    # focused: cen6 ECxo where coarea died, then H?AFBo], then census N<=8
    acc=dict(rows=0,feas=0,infeas=0,ex=None)
    # cen6 ECxo
    for g6 in ["ECxo","H?AFBo]"]:
        n,E=dec(g6); run_graph(g6,n,E,acc,pathwise=pathwise)
        print("after %s: rows=%d feas=%d infeas=%d %s"%(g6,acc['rows'],acc['feas'],acc['infeas'],acc['ex'] or ''),flush=True)
    for nn in range(5,9):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); run_graph("cen%d"%nn,n,E,acc,pathwise=pathwise)
        print("census N=%d: rows=%d feas=%d infeas=%d %s"%(nn,acc['rows'],acc['feas'],acc['infeas'],acc['ex'] or ''),flush=True)
    print("="*55)
    print("rows=%d FEASIBLE=%d INFEASIBLE=%d"%(acc['rows'],acc['feas'],acc['infeas']))
    print("VERDICT:", "GPM FEASIBLE on all rows -- convex route proves (A) on this battery" if acc['infeas']==0 and acc['feas']>0 else "INFEASIBLE: %s"%(acc['ex'],))

if __name__=="__main__":
    main()
