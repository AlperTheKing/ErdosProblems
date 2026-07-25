"""Q4: degree-4 multipliers on And(4)=Gamma_11 with a reduced (still Aut-invariant) cut family.
Using fewer cuts is conservative: any feasible solution remains a valid certificate."""
import time, pickle, sys
import numpy as np
from Q4_graphs import graph_by_key, all_cuts, nondominated_cuts
import Q4_sos as Q
maxmono = int(sys.argv[1]) if len(sys.argv) > 1 else 6
n, E = graph_by_key(11)
cuts = [c for c in nondominated_cuts(all_cuts(n, E)) if len(c[1]) <= maxmono]
print(f"Gamma_11 d=2: {len(cuts)} cuts with |mono| <= {maxmono}", flush=True)
t0 = time.time(); P = Q.build(n, E, cuts, 2, mode='coef'); print(f"build {time.time()-t0:.1f}s", flush=True)
t0 = time.time()
P['prob'].solve(solver='SCS', eps_abs=1e-8, eps_rel=1e-8, max_iters=100000, verbose=True)
print(f"RESULT Gamma_11 d=2 (|mono|<={maxmono}, {len(cuts)} cuts): status={P['prob'].status} "
      f"c* = {P['c'].value}  ({time.time()-t0:.1f}s)")
