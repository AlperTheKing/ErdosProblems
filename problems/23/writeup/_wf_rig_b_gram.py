"""Route (b) Gram/SOS exploration.

Slack S = Q1 + n*N^2/4 - sum_v (T_v - N/2)^2 - (N/5)(TVcut - TVbad),  Q1=Gamma*(N^2/25-beta).

S is CONCAVE in T (minus sum of squares) so 'S = x^T Q x, Q PSD' is impossible.
Correct Gram framing: certify the QUADRATIC inequality
   sum_v (T_v - N/2)^2 + (N/5)(TVcut - TVbad)  <=  Q1 + n N^2/4 .
The LHS quadratic part is sum_v(T_v-N/2)^2 = T^T I T - N (sum T) + nN^2/4.
With fixed edge-signs s_e = sign(T_u-T_v), (N/5)(TVcut-TVbad) = (N/5) * c^T T  (LINEAR in T),
  where c is a fixed vector. So LHS = T^T I T + b^T T + const, and we ask whether the
  MAX of LHS over the *feasible* T (here just the one realized T) stays <= budget.

This module instead measures, per config, the GRAM/eigen structure that a global certificate
would need: it builds the cut Laplacian L_cut and bad Laplacian L_bad and tests whether
   Q1 + nN^2/4 - sum_v(T_v-N/2)^2 - (N/5)(TVcut-TVbad)  (= S)  >= 0
AND reports the 'SOS residual' interpretation:
   define DIRICHLET surrogate:  pen_quad = (1/(2k)) (Dcut - Dbad) + (k/2)(|Ecut|-|Ebad|)?  -- abandoned.

Primary deliverable test (B-DIRICHLET):  for the per-config fixed signs, is there lambda>0 with
   (N/5)(TVcut - TVbad)  <=  (N/5)^2/(4 lambda) * (#cut - #bad as weighted) ... -- abandoned (constants).

Instead we test the LAPLACIAN-GAP certificate (the real route-b candidate):
   (B-LAP)   sum_v (T_v - N)^2  <=  Q1   i.e.  V2 <= Q1   FAILS already (measured).
   (B-LAP-K) V2 <= K*Q1 with K=151/16 -- the rigidity bound; combine with TV bound.
"""
from fractions import Fraction as F
import _wf_rig_b_measure as MZ

def rows():
    R=[]
    for nm,n,E in MZ.CONFIGS:
        adj,cuts=MZ.gmins(n,E)
        if not cuts: continue
        q=MZ.quants(n,adj,cuts[0])
        if q: R.append((nm,q))
    grot=MZ.mycielski(5,MZ.Cn(5)); mycg=MZ.mycielski(grot[0],grot[1])
    for nm,(nn,EE) in [('Grotzsch',grot),('Myc(Grotzsch)',mycg),('M(C7)',MZ.mycielski(7,MZ.Cn(7)))]:
        adj,cuts=MZ.gmins(nn,EE)
        for s in cuts[:1]:
            q=MZ.quants(nn,adj,s)
            if q: R.append((nm,q))
    return R

def main():
    # Test the V2<=K*Q1 bound (K=151/16) and the joint cert:
    #   S = Q1 + N(N^2-Gamma)??  -- recompute pieces
    # Decompose S = [Q1 - nx2] + [N(N^2-Gamma)] - pen, and check the
    # candidate: N(N^2-Gamma) >= pen - (Q1-nx2)?? i.e the reservoir pays.
    print('%-16s %10s %10s %10s %10s'%('name','V2/Q1','reservoir','pen','res>=pen?'))
    maxK=F(0); argK=None
    for nm,q in rows():
        N=q['N']; Q1=q['Q1']; nx2=q['nx2']
        pen=F(N,5)*(q['TVcut']-q['TVbad'])
        res=N*(N**2-q['Gamma'])   # = -N*sum(x)
        K=F(nx2,Q1) if Q1!=0 else F(0)
        if K>maxK: maxK=K; argK=nm
        print('%-16s %10s %10s %10s %5s'%(nm,float(K),str(res),str(pen),'Y' if res>=pen else 'N'))
    print('max V2/Q1 = %s = %.5f at %s   (rigidity K)'%(maxK,float(maxK),argK))

if __name__=='__main__':
    main()
