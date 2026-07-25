"""R8: multistart continuous ascent on max_x psi, obeying OPTIMISER DISCIPLINE.

Every induced C5 at weight 1/5 is used as a start, plus the uniform vector and n_random
random starts.  Reports (a) the best value found, (b) the fraction of RANDOM starts that
reach the global value -- a direct test of "psi has no spurious local maxima".
Floats guide; the reported optimum is polished to exact rationals.
"""
import sys, os
import numpy as np
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import (C, blowup_C5, petersen, grotzsch, wagner, circle_graph, K,
                               maximize_psi, best_rational_polish, cut_matrix_stack, psi_float_all)
from R8_stability_secondorder import build_twin_graph

TESTS = [C(5), blowup_C5([2, 2, 2, 2, 2]), blowup_C5([3, 1, 2, 2, 1]), blowup_C5([2, 0, 2, 2, 2]),
         petersen(), grotzsch(), wagner(), circle_graph(11), circle_graph(14),
         C(7), K(3, 3), build_twin_graph(set()), build_twin_graph({(5, 6)})]

if __name__ == "__main__":
    NR = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    print(f"{'graph':22s} {'n':>3s} {'nC5':>4s} {'best psi (float)':>18s} {'x 25':>8s} "
          f"{'exact polish':>14s} {'rand->max':>10s}")
    for g in TESTS:
        res = maximize_psi(g, n_random=NR, seed=11)
        best = res[0][0]
        nc5 = len(g.induced_C5s())
        # how many of the last NR (random) starts reached the best value
        vals = [v for (v, _) in res]
        hits = sum(1 for v in vals if v > best - 1e-9)
        pol = best_rational_polish(g, res[0][1])
        print(f"{g.name:22s} {g.n:3d} {nc5:4d} {best:18.10f} {best*25:8.5f} "
              f"{str(pol[0]):>14s} {hits:4d}/{len(vals)}")
        if nc5 > 0 and pol[0] < F(1, 25):
            print("    *** VOID RUN: graph contains an induced C5 but exact polish < 1/25 ***")
