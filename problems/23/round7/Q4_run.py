"""Q4 driver: run the multiplier-Positivstellensatz SDP on a pattern, report c*, save primal+dual.
Usage: python Q4_run.py <m> <d> [mode] [cuts:nd|all] [solver]
  m    : Gamma_m (5 -> C5, 8 -> And(3)=Wagner, 11 -> And(4));  d : multiplier degree = 2d
"""
import sys, time, pickle
import numpy as np
from Q4_graphs import gamma_graph, all_cuts, nondominated_cuts
import Q4_sos as Q

m = int(sys.argv[1]) if len(sys.argv) > 1 else 5
d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
mode = sys.argv[3] if len(sys.argv) > 3 else 'coef'
cutsel = sys.argv[4] if len(sys.argv) > 4 else 'nd'
solver = sys.argv[5] if len(sys.argv) > 5 else 'CLARABEL'

n, E = gamma_graph(m)
cuts = all_cuts(n, E)
if cutsel == 'nd':
    cuts = nondominated_cuts(cuts)
print(f"Gamma_{m}: n={n} |E|={len(E)} cuts={len(cuts)} ({cutsel})  multiplier degree {2*d}", flush=True)
t0 = time.time()
P = Q.build(n, E, cuts, d, mode=mode)
print(f"   build {time.time()-t0:.1f}s", flush=True)
t0 = time.time()
kw = {}
if solver == 'SCS':
    kw = dict(eps_abs=1e-10, eps_rel=1e-10, max_iters=500000)
P['prob'].solve(solver=solver, verbose=True, **kw)
tsolve = time.time() - t0
cv = P['c'].value if hasattr(P['c'], 'value') else P['c']
print(f"   solve {tsolve:.1f}s  status={P['prob'].status}")
print(f"RESULT Gamma_{m} d={d} mode={mode} cuts={cutsel}: c* = {cv}"
      f"   ==> max psi <= {1.0/cv if cv else float('nan'):.10f}")

out = dict(m=m, d=d, mode=mode, cutsel=cutsel, n=n, E=E, cuts=cuts, c=cv,
           status=P['prob'].status, time=tsolve,
           nu=np.asarray(P['nu'].value), Q=[(B, np.asarray(V.value)) for V, B in P['Q']],
           dual=[c.dual_value for c in P['prob'].constraints])
with open(f"Q4_sol_g{m}_d{d}_{mode}_{cutsel}.pkl", "wb") as f:
    pickle.dump(out, f)
print(f"   saved Q4_sol_g{m}_d{d}_{mode}_{cutsel}.pkl")
