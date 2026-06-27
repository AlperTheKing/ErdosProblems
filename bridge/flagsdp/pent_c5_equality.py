"""
On C5[q]: GPI LHS = sum_e h_e m_phi(e), h_e=5, m_phi separable.
sum_e m_phi(e) = sum_{u in V4} sum_{v in V0} [phi[u]+phi[v]+ M1+M2+M3]
 where Mc = min_{V_c} phi.  beta = q^2 bad edges.
 = q*(sum_{V4} phi) + q*(sum_{V0} phi) + q^2*(M1+M2+M3).
RHS with Gamma=N^2: (N + N^2 - Gamma) sum phi = N * sum phi  (deficit 0).
GPI: 5 * LHS <= N * sum_v phi = 5q * sum_v phi.
Check the gap and find the pentagonal facet that makes it tight (phi = class-uniform).
"""
import numpy as np, random
random.seed(1)
def test(q, phi=None):
    n=5*q
    cls=[[i*q+j for j in range(q)] for i in range(5)]
    if phi is None: phi=np.array([random.random() for _ in range(n)])
    Mc=[min(phi[w] for w in cls[i]) for i in range(5)]
    Sc=[sum(phi[w] for w in cls[i]) for i in range(5)]
    lhs_sum_m = q*Sc[4]+q*Sc[0]+ (q*q)*(Mc[1]+Mc[2]+Mc[3])
    LHS=5*lhs_sum_m
    RHS=(5*q)*sum(phi)
    return LHS,RHS,phi,Sc,Mc

for q in (2,3,5):
    # random
    L,R,_,_,_=test(q); print(f"q={q} random: LHS={L:.3f} RHS={R:.3f} gap={R-L:.3f} OK={L<=R+1e-9}")
    # class-uniform phi=1
    L,R,_,Sc,Mc=test(q, np.ones(5*q)); print(f"q={q} phi=1 : LHS={L:.3f} RHS={R:.3f} gap={R-L:.3f} (expect 0 = tight)")
    # phi = indicator of V0 only
    phi=np.zeros(5*q)
    for w in range(q): phi[w]=1.0  # V0
    L,R,_,_,_=test(q, phi); print(f"q={q} phi=1_V0: LHS={L:.3f} RHS={R:.3f} gap={R-L:.3f}")
