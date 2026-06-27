"""
THE CRUX TEST for the cut-metric angle.

The cut-metric/pentagonal program wants to PROVE GPI by:
  (1) a per-cut facet F(S) >= sum_e h_e mS(e), tight on C5[q],
  (2) a way to combine facets over a layer-cake of phi giving the (N+N^2-Gamma) sum phi RHS.

The fatal obstruction (per prompt): m_phi(e) >= integral min_P|P cap S_t| dt is the WRONG direction.
Equivalently: sum_e h_e m_phi(e)  vs  integral_0^inf [sum_e h_e mS_t(e)] dt.
If LHS <= that integral ALWAYS, then 0/1 cut-Hall (each level) would imply GPI by integration.
The DEAD claim says the inequality goes the wrong way (LHS can EXCEED the integral). VERIFY the sign:

  Define  Int(phi) := integral_0^inf [ sum_e h_e * min_P |P cap S_t| ] dt    (sum of level-set cut-Halls)
  and     Lhs(phi) := sum_e h_e * min_P sum_{v in P} phi(v).
  Layer-cake gives sum_{v in P} phi(v) = integral |P cap S_t| dt, so for a FIXED P,
     sum_v phi = integral |P cap S_t| dt.  Taking min over P:
     Lhs = min_P integral |P cap S_t| dt  >=  integral min_P |P cap S_t| dt = Int(phi).
  So Lhs >= Int -- the level-set bound UNDERSHOOTS, cannot certify GPI. CONFIRM numerically the gap
  Lhs - Int > 0 strictly on some triangle-free graph (this is the recorded 'DEAD' fact, re-verified),
  and measure HOW BIG the layer-cake defect is vs the GPI slack (N+N^2-Gamma)sum phi - Lhs.
"""
import sys, numpy as np, random
sys.path.insert(0,'.')
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs

def Int_phi(phi, M, geos, he):
    # layer-cake over distinct thresholds of phi
    vals=sorted(set(phi.tolist())|{0.0})
    # thresholds t: between consecutive sorted values, S_t={v: phi[v]>=t}
    pts=sorted(set(phi.tolist()))
    total=0.0; prev=0.0
    for t in pts:
        # on (prev, t], S_t = {v: phi>=t}? integrate measure of dt with the level just above prev
        pass
    # cleaner: Int = sum over e he * integral_0^inf minP|P cap S_t| dt.
    # For fixed e, define g(t)=min_P |P cap {phi>=t}|, piecewise const, integrate.
    thr=sorted(set(phi.tolist()))
    res=0.0
    for e in M:
        # integrate g over t in [0, max phi]; breakpoints at distinct phi values
        last=0.0
        allv=sorted(set([0.0]+[phi[v] for v in range(len(phi))]))
        # sample midpoints between breakpoints up to max
        prevt=0.0
        for k in range(1,len(allv)):
            tlo=allv[k-1]; thi=allv[k]; tmid=(tlo+thi)/2
            S=set(v for v in range(len(phi)) if phi[v]>=tmid)
            g=min(sum(1 for v in P if v in S) for P in geos[e])
            res+=he[e]*g*(thi-tlo)
    return res

def Lhs(phi, M, geos, he):
    return sum(he[e]*min(sum(phi[v] for v in P) for P in geos[e]) for e in M)

N=int(sys.argv[1]) if len(sys.argv)>1 else 8
random.seed(7)
worst_defect=0.0; wrec=None; checked=0
for nn,A in enumerate_graphs(N, triangle_free=True):
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: continue
    side,Gam,M=res
    if not M: continue
    K=N+N*N-Gam
    geos={e:all_shortest_geos(N,adj,side,*e) for e in M}
    he={e:len(geos[e][0]) for e in M}
    for trial in range(40):
        phi=np.array([random.random() for _ in range(N)])
        L=Lhs(phi,M,geos,he); I=Int_phi(phi,M,geos,he)
        checked+=1
        defect=L-I  # >=0 always (layer-cake undershoot)
        gpislack=K*phi.sum()-L
        if defect>worst_defect:
            worst_defect=defect; wrec=(L,I,defect,gpislack,Gam,sorted(E))
print(f"N={N}: checked {checked} (graph,toll) samples")
print(f"  max layer-cake defect (Lhs - Int) = {worst_defect:.5f}  (>0 confirms WRONG direction, DEAD route)")
if wrec:
    L,I,d,gs,Gam,E=wrec
    print(f"  at worst: Lhs={L:.4f} Int={I:.4f} defect={d:.4f} | GPI-slack={gs:.4f} Gamma={Gam}")
    print(f"  -> level-set bound Int <= Lhs <= K*sumphi: Int leaves slack {gs+d:.4f}; defect alone {d:.4f}")
