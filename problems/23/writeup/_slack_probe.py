"""Empirical structure probe for the endpoint-curvature slack
      SLACK(P) = B_L(P) - DG(x_0) - DG(x_{L-1})   (>= 0, validated)
   Goal: recognize SLACK as a manifestly nonnegative form.
   Compare per-row against candidate nonneg quantities:
     C_L            = S^2 - L^2*q                       (path-load AM-GM deficit)
     Qmin           = min_phi Q_mix(phi)                (mixed five-shadow AM-GM deficit)
     SSQ            = sum_i (T[x_i]-N)^2                 (path-load variance-ish)
     DEF            = sum_i (N - T[x_i])  = L*N - sum T[x_i]   (path underload)
   Print the pieces for the smallest-slack nonzero rows and look for slack == combo.
   ALL exact Fraction.
"""
import itertools, subprocess
from collections import deque
from fractions import Fraction as F
from _wf_deficit_farkas import gamma_of, deltas, flip, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint

def endpoint_dg(n, adj, side, v, Gamma):
    s2 = flip(side, [v])
    if not Bconn(n, adj, s2): return F(0)
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return F(0)
    g1 = gamma_of(n, adj, s2)
    return F(0) if g1 is None else g1 - Gamma

def qmix_min(n, T, Gamma, P, L):
    N = F(n); fixed = {P[i]: i for i in range(L)}
    free = [v for v in range(n) if v not in fixed]
    if len(free) > 8: return None   # skip if too many extensions
    best = None
    for assign in itertools.product(range(L), repeat=len(free)):
        ncnt=[0]*L; wsum=[F(0)]*L
        for i in range(L): ncnt[i]+=1; wsum[i]+=T[P[i]]
        for v,c in zip(free,assign): ncnt[c]+=1; wsum[c]+=T[v]
        w=[wsum[i]/N for i in range(L)]
        mn=min(F(ncnt[i])*w[(i+1)%L] for i in range(L))
        Q=Gamma-(L*L)*mn   # general-L mixed slack: Gamma - L^2*min(n_i w_{i+1})
        if best is None or Q<best: best=Q
    return best

def rows_for(name,n,E):
    adj,cuts=gmins(n,E); out=[]
    for side in cuts:
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st; N=F(n); Gamma=sum(T)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                x=P
                h=[T[x[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                C_L=S*S-(L*L)*q
                B_L=L*(N*N-Gamma)-25*sum(T[x[i]]-N for i in range(L))-C_L
                DG0=endpoint_dg(n,adj,side,x[0],Gamma); DGL=endpoint_dg(n,adj,side,x[-1],Gamma)
                slack=B_L-DG0-DGL
                SSQ=sum((T[x[i]]-N)**2 for i in range(L))
                DEF=L*N-sum(T[x[i]] for i in range(L))
                Qm=qmix_min(n,T,Gamma,x,L)
                out.append(dict(name=name,L=L,P=tuple(x),Gamma=Gamma,slack=slack,B_L=B_L,
                                DG0=DG0,DGL=DGL,C_L=C_L,SSQ=SSQ,DEF=DEF,Qm=Qm))
    return out

def main():
    fams=[]
    for nn in range(5,9):
        for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fams.append(("cen%d-%s"%(nn,g6),n,E))
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2)]:
        n,E=odd_blowup(5,list(sizes)); fams.append(("C5%s"%(sizes,),n,E))
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n,E=union_disjoint((n5,E5),(n7,E7)); E=E+[(0,n5)]
    fams.append(("glue_C5|C7",n,E))
    allrows=[]
    for (name,n,E) in fams: allrows+=rows_for(name,n,E)
    # test simple identities
    eq_CL=sum(1 for r in allrows if r['slack']==r['C_L'])
    eq_Qm=sum(1 for r in allrows if r['Qm'] is not None and r['slack']==r['Qm'])
    print("total rows:",len(allrows))
    print("slack==C_L on", eq_CL, "rows; slack==Qmin on", eq_Qm, "rows")
    # smallest nonzero slack rows
    nz=[r for r in allrows if r['slack']>0]
    nz.sort(key=lambda r:r['slack'])
    print("\nsmallest nonzero slack rows (slack | B_L DG0 DGL | C_L SSQ DEF Qmin):")
    for r in nz[:12]:
        print("  %-14s L=%d slack=%s | B_L=%s DG0=%s DGL=%s | C_L=%s SSQ=%s DEF=%s Qm=%s"
              % (r['name'],r['L'],str(r['slack']),str(r['B_L']),str(r['DG0']),str(r['DGL']),
                 str(r['C_L']),str(r['SSQ']),str(r['DEF']),str(r['Qm'])))
    # ratio slack / C_L where C_L>0
    rats=set()
    for r in allrows:
        if r['C_L']>0: rats.add(r['slack']/r['C_L'])
    print("\ndistinct slack/C_L ratios (first 8):", sorted(rats)[:8], "... count", len(rats))

if __name__=="__main__":
    main()
