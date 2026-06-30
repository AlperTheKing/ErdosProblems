"""Degree-capped LP certificate search for the seven-cut PMS lemma."""

from itertools import combinations_with_replacement
import argparse

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_ocpms_lp_certificate as base


def gen_monomials(num_vars, max_deg):
    out = []

    def rec(i, remaining, cur):
        if i == num_vars - 1:
            cur.append(remaining)
            out.append(tuple(cur))
            cur.pop()
            return
        for v in range(remaining + 1):
            cur.append(v)
            rec(i + 1, remaining - v, cur)
            cur.pop()

    for deg in range(max_deg + 1):
        rec(0, deg, [])
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deg", type=int, default=4)
    args = parser.parse_args()

    p, gs = base.build_target_and_constraints()
    qmons = gen_monomials(10, args.deg)
    candidates = [(gi, q) for gi in range(len(gs)) for q in qmons]
    print("deg", args.deg, "candidates", len(candidates))

    monoms = set(p)
    for gi, q in candidates:
        for gm in gs[gi]:
            monoms.add(base.add_monom(q, gm))
    monoms = sorted(monoms)
    mid = {m: i for i, m in enumerate(monoms)}
    print("rows", len(monoms))

    rows = []
    cols = []
    data = []
    for j, (gi, q) in enumerate(candidates):
        for gm, coeff in gs[gi].items():
            rows.append(mid[base.add_monom(q, gm)])
            cols.append(j)
            data.append(coeff)
    A = coo_matrix((data, (rows, cols)), shape=(len(monoms), len(candidates))).tocsr()
    b = np.array([p.get(m, 0) for m in monoms], dtype=float)

    res = linprog(
        c=np.zeros(len(candidates)),
        A_ub=A,
        b_ub=b,
        bounds=(0, None),
        method="highs",
        options={"presolve": True},
    )
    print("status", res.status, res.message)
    if res.success:
        nz = [(candidates[i], res.x[i]) for i in range(len(candidates)) if res.x[i] > 1e-8]
        print("nonzero", len(nz))
        for item in nz[:120]:
            print(item)


if __name__ == "__main__":
    main()
