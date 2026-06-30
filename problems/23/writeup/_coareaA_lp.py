"""DECISIVE TEST of GPT-Pro's CORRECTED (A) coarea moment LP (2026-07-01).
   For a gamma-min row P=(x_0..x_{L-1}), C=P+f odd cycle.  Switch family: W(J,Y) = {x_i:i in J} union (union Y),
   J = oriented cyclic interval on P (all (s,t), 1<=|J|<=L-1), Y subset of off-row blue components of B[V\\V(P)].
   Per switch W (require flipped struct valid):
     sigma(W)=delta_B(W)-delta_M(W)>=0 ; tau_W(i)=1_{x_i in W} (i=0..L-1) ; chi_W=1_{x_0 in W and x_{L-1} in W} ;
     DGamma(W)=Gamma(flip)-Gamma.
   Coefficients: h_i=T(x_i)/N, S=sum h_i, r=argmin h_i h_{i+1}, a_i=2S-L^2(h_{r+1}1_{i=r}+h_r 1_{i=r+1}),
     mu_i=L/5 - a_i/(2N), L2delta=S^2-L^2 h_r h_{r+1}, E_0 = renormalized endpoint curvature (chi_profile),
     TARGET=(L/5)(N^2-Gamma)-E_0-L2delta.
   LP feasibility (lambda>=0): M0 sum lambda sigma=0 ; M1 sum lambda tau_i=mu_i (all i) ; M2 sum lambda chi=1 ;
     (17) sum lambda DGamma = TARGET.   Feasible => (A) holds on the row (via gamma-min).
   Float linprog verdict first.  Usage: python _coareaA_lp.py [g6] [sidestr]   default H?AFBo] gamma-min cuts.
"""
import sys, itertools
from fractions import Fraction as F
from _crux_extract import components_off_path
from _singleton_core import ell_map
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
try:
    import numpy as np
    from scipy.optimize import linprog
    HAVE_SCIPY=True
except Exception:
    HAVE_SCIPY=False

def switch_family(n,adj,side,P):
    L=len(P); Pset=set(P)
    comps=components_off_path(n,adj,side,Pset)
    out=[]
    # oriented cyclic intervals J=[s,t]_L, 1<=len<=L-1
    intervals=[]
    for s in range(L):
        cur=[]
        for ln in range(1,L):
            cur=cur+[(s+ln-1)%L]
            intervals.append(frozenset(P[idx] for idx in cur))
    # dedup interval vertex-sets but keep distinct (s,t) traces -> we keep set form (vertex membership is what matters)
    seenJ=set(); Js=[]
    for I in intervals:
        if I not in seenJ: seenJ.add(I); Js.append(I)
    for I in Js:
        for k in range(len(comps)+1):
            for Y in itertools.combinations(range(len(comps)),k):
                W=set(I)
                for ci in Y: W|=comps[ci]
                out.append(frozenset(W))
    # dedup
    seen=set(); res=[]
    for W in out:
        if W and W not in seen: seen.add(W); res.append(W)
    return res

def test_row(n,adj,side,M,ell,T,cyc,f,P):
    L=ell[f]; N=F(n); Gamma=sum(ell[g]**2 for g in M)
    h=[T[P[i]]/N for i in range(L)]; S=sum(h)
    prods=[h[i]*h[(i+1)%L] for i in range(L)]; q=min(prods); r=prods.index(q)
    a=[2*S - L*L*((h[(r+1)%L] if i==r else 0)+(h[r] if i==(r+1)%L else 0)) for i in range(L)]
    mu=[F(L,5) - a[i]/(2*N) for i in range(L)]
    L2delta=S*S - L*L*q
    chiP=[0]*n
    for end in (P[0],P[-1]):
        ch=endpt_chi(n,adj,side,end,M,n)
        for rr in range(n): chiP[rr]+=ch[rr]
    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
    TARGET=F(L,5)*(N*N-Gamma) - E0 - L2delta
    Pset=set(P)
    cols=[]  # each: dict with sigma, tau[L], chi, dG
    for W in switch_family(n,adj,side,P):
        s2=flip(side,W)
        if not Bconn(n,adj,s2): continue
        g1=gamma_of(n,adj,s2)
        if g1 is None: continue
        dB,dM=deltas(n,adj,side,W); sigma=dB-dM
        if sigma<0: continue
        tau=[1 if P[i] in W else 0 for i in range(L)]
        chi=1 if (P[0] in W and P[-1] in W) else 0
        dG=g1-Gamma
        cols.append((sigma,tau,chi,dG))
    if not cols: return ('NOCOLS',None,None)
    # Build exact A_eq lambda = b_eq, lambda>=0. Rows: M0, M1(L), M2, (17).
    # float linprog feasibility
    ncol=len(cols)
    rows=[]; b=[]
    rows.append([float(c[0]) for c in cols]); b.append(0.0)          # M0
    for i in range(L):
        rows.append([float(c[1][i]) for c in cols]); b.append(float(mu[i]))   # M1
    if E0!=0:                                                         # M2 only needed when E_0 != 0
        rows.append([float(c[2]) for c in cols]); b.append(1.0)      # M2
    rows.append([float(c[3]) for c in cols]); b.append(float(TARGET))# (17)
    feas=None
    if HAVE_SCIPY:
        A=np.array(rows); bb=np.array(b)
        res=linprog(c=np.zeros(ncol),A_eq=A,b_eq=bb,bounds=[(0,None)]*ncol,method='highs')
        feas=res.success
    return ('OK',feas,(ncol,len(cols),str(TARGET),str(E0),str(L2delta)))

def main():
    g6=sys.argv[1] if len(sys.argv)>1 else "H?AFBo]"
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    if len(sys.argv)>2:
        cuts=[[int(c) for c in sys.argv[2]]]
    else:
        _,cuts=gmins(n,E)
    print("g6=%s, %d gamma-min cuts, scipy=%s"%(g6,len(cuts),HAVE_SCIPY))
    rows=0; feas_rows=0; infeas_rows=0; nocol=0; seengeod={}
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
                tag,feas,info=test_row(n,adj,side,M,ell,T,cyc,f,list(P))
                rows+=1
                if tag=='NOCOLS': nocol+=1; continue
                # also test reverse orientation
                tagR,feasR,_=test_row(n,adj,side,M,ell,T,cyc,f,list(P)[::-1])
                eith = feas or (feasR is True)
                acc_geod=frozenset(P)
                seengeod.setdefault(acc_geod, [False])[0] |= bool(eith)
                if feas: feas_rows+=1
                else: infeas_rows+=1
                print("  P=%s feas=%s  rev_feas=%s  either=%s"%(tuple(P),feas,feasR,eith))
    print("rows=%d  FEASIBLE=%d  INFEASIBLE=%d  no-columns=%d"%(rows,feas_rows,infeas_rows,nocol))
    geod_ok=sum(1 for v in seengeod.values() if v[0]); geod_tot=len(seengeod)
    print("DISTINCT GEODESICS (by vertex set): %d ; with at-least-one-orientation FEASIBLE: %d"%(geod_tot,geod_ok))
    print("VERDICT:", "COAREA LP FEASIBLE (>=1 orientation) on ALL geodesics -- A route SURVIVES" if geod_ok==geod_tot and geod_tot>0 else ("some geodesics infeasible in BOTH orientations -- route still broken" if geod_tot>0 else "no testable rows"))

if __name__=="__main__":
    main()
