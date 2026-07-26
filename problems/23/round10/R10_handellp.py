"""R10 exact-route probe: coefficientwise Handelman certificate for Gamma_11 arcs.

This is a strict subcone of the registered degree-4 multiplier SOS route:
nu_S has nonnegative coefficients, sum_S nu_S = 25 L^4, and the residual
L^6-sum_S nu_S q_S is required to have nonnegative coefficients.  A feasible
point is therefore a valid certificate; infeasibility kills only this LP subcone.
"""
from __future__ import annotations

import sys
from math import factorial
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
R7 = HERE.parent / "round7"
sys.path.insert(0, str(R7))
from Q4_graphs import gamma_graph, all_cuts  # noqa: E402
from Q4_sos import monomials  # noqa: E402


def multinom(alpha):
    ans = factorial(sum(alpha))
    for a in alpha:
        ans //= factorial(a)
    return ans


def as_set(mask, n):
    return frozenset(v for v in range(n) if v and (mask >> (v - 1)) & 1)


def is_arc(S, n):
    V = frozenset(range(n))
    for T in (S, V - S):
        if not T:
            return True
        for start in range(n):
            if T == frozenset((start + j) % n for j in range(len(T))):
                return True
    return False


def main():
    n, edges = gamma_graph(11)
    cuts = [c for c in all_cuts(n, edges) if is_arc(as_set(c[0], n), n)]
    mons_d = monomials(n, 4)
    mons_t = monomials(n, 6)
    idx_t = {a: i for i, a in enumerate(mons_t)}
    nc, nd, nt = len(cuts), len(mons_d), len(mons_t)
    nv = nc * nd
    print(f"Gamma_11 arc Handelman LP: cuts={nc}, vars={nv}, eq={nd}, ub={nt}", flush=True)

    erows, ecols = [], []
    for mi in range(nd):
        for si in range(nc):
            erows.append(mi)
            ecols.append(si * nd + mi)
    aeq = sp.csr_matrix((np.ones(len(erows)), (erows, ecols)), shape=(nd, nv))
    beq = np.array([25 * multinom(m) for m in mons_d], dtype=float)

    rows, cols = [], []
    for si, (_mask, mono) in enumerate(cuts):
        for mi, m in enumerate(mons_d):
            col = si * nd + mi
            for ei in mono:
                u, v = edges[ei]
                a = list(m)
                a[u] += 1
                a[v] += 1
                rows.append(idx_t[tuple(a)])
                cols.append(col)
    aub = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(nt, nv))
    bub = np.array([multinom(a) for a in mons_t], dtype=float)
    print(f"nnz(eq)={aeq.nnz}, nnz(ub)={aub.nnz}", flush=True)

    res = linprog(np.zeros(nv), A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                  bounds=(0, None), method="highs",
                  options={"presolve": True, "time_limit": 900})
    print(f"status={res.status} success={res.success}: {res.message}", flush=True)
    if res.success:
        eqerr = float(np.max(np.abs(aeq @ res.x - beq)))
        ubmax = float(np.max(aub @ res.x - bub))
        support = int(np.count_nonzero(res.x > 1e-9))
        print(f"eqerr={eqerr:.3e} ubmax={ubmax:.3e} support={support}", flush=True)
        np.savez_compressed(HERE / "R10_handellp_solution.npz", x=res.x)


if __name__ == "__main__":
    main()
