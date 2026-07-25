import sys, numpy as np
from scipy.optimize import minimize
Q = [((0,7),(3,4)), ((1,2),(5,6)), ((0,1),(4,5)), ((2,3),(6,7)),
     ((0,4),(1,5),(2,6),(3,7))]
def qs(x): return [sum(x[u]*x[v] for (u,v) in p) for p in Q]
def minq(x): return min(qs(x))
def prodq(x):
    p=1.0
    for v in qs(x): p*=v
    return p
def maximise(fun, ntrial, seed):
    rng = np.random.default_rng(seed); best=(-1.0,None)
    cons=[{'type':'eq','fun':lambda z: float(np.sum(z)-1.0)}]
    for t in range(ntrial):
        x0=rng.dirichlet(np.ones(8)*rng.uniform(0.1,3.0))
        r=minimize(lambda z:-fun(np.clip(z,0,None)),x0,constraints=cons,
                   bounds=[(0,1)]*8,method='SLSQP',options={'maxiter':300,'ftol':1e-16})
        x=np.clip(r.x,0,None); s=x.sum()
        if s<=0: continue
        x=x/s; v=fun(x)
        if v>best[0]: best=(v,x.copy())
    return best
v,x = maximise(minq, 400, 5)
print(f"max_simplex min_j q_j  = {v:.12f}  (1/25 = 0.04)  at {np.round(x,6)}")
v2,x2 = maximise(prodq, 400, 5)
print(f"max_simplex prod_j q_j = {v2:.6e}  (25^-5 = {25.0**-5:.6e})  ratio={v2/(25.0**-5):.6f}")
print("   at", np.round(x2,6))
