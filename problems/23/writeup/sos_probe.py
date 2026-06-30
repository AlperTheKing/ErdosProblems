"""SOS-angle probe for crux (A): E_0 + delta*L^2 <= (L/5)(N^2 - Gamma).

Per row we have (all exact Fraction):
  h_0..h_{L-1} >=0 (loads/N), L odd>=5, S=sum h_i, q=min_i h_i h_{i+1},
  delta=(S/L)^2 - q,  E_0 (endpoint curvature, can be <0), Gamma, N.

Two ALGEBRAIC facts already exact-verified by the team:
 (LIN)  L^2*delta = (1/2) sum_i a_i h_i,  a_i=2S - L^2(h_{r+1}1_{i=r}+h_r 1_{i=r+1}), r=argmin.

CANDIDATE SOS DECOMPOSITION (the thing to falsify):
 Claim that the row slack
     R := (L/5)(N^2-Gamma) - E_0 - delta*L^2
 admits, on EVERY gamma-min row, the lower bound
     R >= (L/5)*(N^2-Gamma) - E_0 - L^2*delta
 trivially; but we want a CERTIFICATE that R>=0 from a sum of squares in the
 DEVIATIONS of the load from its cyclic mean, MINUS an endpoint term that
 gamma-minimality forces nonpositive.

 Write m = S/L (cyclic mean of h on the path). Decompose
     L^2*delta = L^2*((S/L)^2 - q) = S^2 - L^2 q.
 Use the elementary identity (cyclic, indices mod L):
     S^2 - L^2 q = (1/2) sum_{i<j} (h_i - h_j)^2 ... NO -- q is a single min product, not symmetric.
 Instead the SHARP decomposition we test:
     delta*L^2 = S^2 - L^2 q.
 Define for the argmin edge (r,r+1):  P_min = h_r h_{r+1} = q.
 The candidate (call it SOS-MEAN):
     delta*L^2 = sum_i (h_i - m)^2  + [ L*m^2 - L^2 q ]          (m=S/L)
 because sum_i(h_i-m)^2 = sum h_i^2 - L m^2, and S^2 = L^2 m^2.
 So  S^2 - L^2 q = L^2 m^2 - L^2 q, and sum_i(h_i-m)^2 = sum h_i^2 - L m^2.
 => delta*L^2 = L^2 m^2 - L^2 q  and  this is NOT sum of squares directly.

We TEST several concrete certificate inequalities exactly and report worst ratios.
"""
import subprocess
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def rows_iter(fams):
    for (n,E) in fams:
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        try: _,cuts=gmins(n,E)
        except Exception: continue
        for side in cuts:
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            N=F(n); Gamma=sum(T)
            for f in M:
                L=ell[f]
                if L%2==0: continue
                for P in cyc[f]:
                    if len(P)!=L: continue
                    h=[T[P[i]]/N for i in range(L)]
                    S=sum(h)
                    prods=[h[i]*h[(i+1)%L] for i in range(L)]
                    q=min(prods); r=prods.index(q)
                    delta=(S/L)**2 - q
                    chiP=[0]*n
                    ok=True
                    for end in (P[0],P[-1]):
                        ch=endpt_chi(n,adj,side,end,M,n)
                        for rr in range(n): chiP[rr]+=ch[rr]
                    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
                    yield dict(n=n,N=N,L=L,Gamma=Gamma,h=h,S=S,q=q,r=r,delta=delta,E0=E0)

def build_fams():
    fams=[]
    n,E=dec("H?AFBo]"); fams.append((n,E))
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            fams.append(dec(g6))
    for sizes in [(2,2,2,2,2),(3,3,3,3,3),(2,1,2,1,2),(3,2,3,2,3),(2,1,2,1,3),(4,1,4,1,4)]:
        fams.append(odd_blowup(5,list(sizes)))
    return fams

def main():
    fams=build_fams()
    # Certificate C1: the per-row "mean-deviation absorbs dispersion, endpoint pays the rest"
    #   R = (L/5)(N^2-Gamma) - E_0 - delta*L^2
    # We test the SOS-FACTORED LOWER BOUND:
    #   (L/5)(N^2-Gamma) - delta*L^2 >= E_0 + SOSpart, with SOSpart = sum_i (h_i - m)^2 >=0.
    # i.e. test whether  (L/5)(N^2-Gamma) - E_0  >=  delta*L^2 + sum_i(h_i-m)^2   (STRONGER than A).
    # If TRUE on battery, that is a clean SOS certificate (the dispersion appears DOUBLED).
    worst_A=None; worst_C1=None; worst_C2=None
    nA=fc1=fc2=0; tot=0
    for row in rows_iter(fams):
        tot+=1
        L=row['L']; N=row['N']; Gamma=row['Gamma']; E0=row['E0']; delta=row['delta']
        h=row['h']; S=row['S']; m=S/L
        rhs=F(L,5)*(N*N-Gamma)
        lhsA=E0+delta*L*L
        # (A) ratio
        if rhs>0:
            ratA=lhsA/rhs
            if worst_A is None or ratA>worst_A[0]: worst_A=(ratA,row['n'],L,str(lhsA),str(rhs))
        if lhsA>rhs: nA+=1
        # C1: stronger SOS form
        sosdev=sum((hi-m)**2 for hi in h)
        lhsC1=E0+delta*L*L+sosdev
        if lhsC1>rhs: fc1+=1
        if rhs>0:
            r1=lhsC1/rhs
            if worst_C1 is None or r1>worst_C1[0]: worst_C1=(r1,row['n'],L,str(lhsC1),str(rhs))
        # C2: dispersion-as-pure-SOS reform. delta*L^2 = S^2 - L^2 q.
        #   S^2 = (sum h)^2.  Use min-edge anchor: q=h_r h_{r+1}.
        #   Identity: S^2 - L^2 h_r h_{r+1}. Test a Schur-like lower-cert:
        #   delta*L^2 <= (1/2)*sum_i a_i h_i (this is EQ by LIN). So check the
        #   "a_i nonneg-weighted" interpretation: a_i = 2S - L^2(...). Test:
        #   does (L/5)(N^2-Gamma) - E_0 - (1/2) sum a_i h_i >= 0 with the a_i clipped?
        a=[2*S - L*L*((h[(row['r']+1)%L] if i==row['r'] else 0)+(h[row['r']] if i==(row['r']+1)%L else 0)) for i in range(L)]
        lin=F(1,2)*sum(a[i]*h[i] for i in range(L))
        # sanity: lin == delta*L^2
        assert lin==delta*L*L, (lin, delta*L*L)
    print("rows=%d"%tot)
    print("(A) violations=%d  worst ratio=%s ~%.5f  @n=%s L=%s"%(nA,worst_A[0],float(worst_A[0]),worst_A[1],worst_A[2]))
    print("(C1 stronger: +sum(h_i-m)^2) violations=%d  worst ratio=%s ~%.5f @n=%s L=%s"%(fc1,worst_C1[0],float(worst_C1[0]),worst_C1[1],worst_C1[2]))

if __name__=="__main__":
    main()
