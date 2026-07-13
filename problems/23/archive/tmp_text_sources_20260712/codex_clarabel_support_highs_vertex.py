#!/usr/bin/env python3
"""Extract an exact-replay core from a small Clarabel support via HiGHS.

The older Clarabel path used the numeric feasible point only to choose a support,
then selected an arbitrary QR square subsystem.  That subsystem can solve exactly
but land at a negative vertex.  Here we keep the good part (small Clarabel
support) and ask HiGHS to optimize the full inequality LP restricted to that
support.  The restricted problem has only hundreds of columns for the chart-8
tail, so simplex can choose a genuine nonnegative vertex quickly.

Output format is the same square-core JSONL consumed by
codex_modular_solve_cpp_threads.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import clarabel
import numpy as np
from scipy import sparse
from scipy.linalg import qr
from scipy.optimize import linprog

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def deterministic_cost(n: int, seed: int) -> np.ndarray:
    return np.array(
        [1.0 + ((j * 1103515245 + seed) % 100003) / 100003.0 for j in range(n)],
        dtype=float,
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("chart", type=int)
    ap.add_argument("dom", type=int)
    ap.add_argument("band")
    ap.add_argument("support")
    ap.add_argument("out_core")
    ap.add_argument("--clarabel-tau", type=float, default=1e-1)
    ap.add_argument("--basis-tau", type=float, default=1e-9)
    ap.add_argument("--bind-tol", type=float, default=1e-7)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--clarabel-max-iter", type=int, default=400)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    out_core = Path(args.out_core)

    prepared, columns, _m, _b = probe.build_lp(args.chart, args.dom, args.band, args.support)
    target_frac = list(prepared.p_beta)
    target = np.array([float(x) for x in target_frac], dtype=float)
    m = len(target_frac)
    ncol = len(columns)

    col_map: list[dict[int, Fraction]] = [dict() for _ in range(ncol)]
    ri: list[int] = []
    cj: list[int] = []
    vv: list[float] = []
    for j, col in enumerate(columns):
        for r, coeff in col.terms:
            col_map[j][r] = col_map[j].get(r, Fraction(0)) + coeff
        for r, coeff in col_map[j].items():
            ri.append(r)
            cj.append(j)
            vv.append(float(coeff))
    A = sparse.csc_matrix((vv, (ri, cj)), shape=(m, ncol))

    q = deterministic_cost(ncol, args.seed)
    P = sparse.csc_matrix((ncol, ncol))
    Amat = sparse.vstack([A, -sparse.identity(ncol, format="csc")], format="csc")
    b = np.concatenate([target, np.zeros(ncol)])
    cones = [clarabel.NonnegativeConeT(m), clarabel.NonnegativeConeT(ncol)]
    st = clarabel.DefaultSettings()
    st.verbose = False
    st.max_iter = args.clarabel_max_iter
    sol = clarabel.DefaultSolver(P, q, Amat, b, cones, st).solve()
    xstar = np.array(sol.x, dtype=float)
    S = [j for j in range(ncol) if xstar[j] > args.clarabel_tau]
    if not S:
        raise SystemExit("empty Clarabel support")
    print(
        f"row={args.chart}/{args.dom} clarabel_status={sol.status} "
        f"support={len(S)} tau={args.clarabel_tau}",
        flush=True,
    )

    AS = A[:, S].tocsc()
    c_restricted = deterministic_cost(len(S), args.seed + 7919)
    lp = linprog(
        c_restricted,
        A_ub=AS,
        b_ub=target,
        bounds=(0, None),
        method="highs-ds",
        options={"presolve": True, "dual_feasibility_tolerance": 1e-9, "primal_feasibility_tolerance": 1e-9},
    )
    print(
        f"restricted_highs success={lp.success} status={lp.status} message={lp.message!r} "
        f"nit={getattr(lp, 'nit', None)} fun={lp.fun if lp.success else None}",
        flush=True,
    )
    if not lp.success:
        return 2

    x = np.array(lp.x, dtype=float)
    local_pos = [i for i, val in enumerate(x) if val > args.basis_tau]
    Sb = [S[i] for i in local_pos]
    if not Sb:
        raise SystemExit("empty HiGHS vertex support")

    residual = target - AS.dot(x)
    ASb = A[:, Sb].tocsc()
    rownorm = np.asarray(np.abs(ASb).sum(axis=1)).ravel()
    tight = np.where((rownorm > 1e-12) & (np.abs(residual) < args.bind_tol))[0]
    if len(tight) < len(Sb):
        order = np.where(rownorm > 1e-12)[0]
        order = order[np.argsort(np.abs(residual[order]))]
        tight = order[: max(len(Sb), min(len(order), 6 * len(Sb) + 100))]

    A_tight = np.asarray(ASb[tight].todense())
    _, Rr, pivr = qr(A_tight.T, mode="economic", pivoting=True)
    diag = np.abs(np.diag(Rr))
    tol = max(diag.max() * 1e-9, 1e-12) if diag.size else 1e-12
    rank = int((diag > tol).sum())
    if rank < len(Sb):
        print(
            json.dumps(
                {
                    "row": f"{args.chart}/{args.dom}",
                    "status": "rank_deficient_vertex_support",
                    "support": len(S),
                    "vertex_support": len(Sb),
                    "tight_rows": len(tight),
                    "rank": rank,
                }
            ),
            flush=True,
        )
        return 3
    T = [int(tight[i]) for i in pivr[: len(Sb)]]

    recs: list[dict[str, object]] = [{"type": "meta", "dimension": len(Sb)}]
    for k, j in enumerate(Sb):
        recs.append({"type": "col", "col": k, "source_col": j})
    for ti, row in enumerate(T):
        tv = target_frac[row]
        recs.append({"type": "rhs", "row": ti, "value": f"{tv.numerator}/{tv.denominator}"})
        for k, j in enumerate(Sb):
            coeff = col_map[j].get(row)
            if coeff:
                recs.append(
                    {
                        "type": "term",
                        "row": ti,
                        "col": k,
                        "value": f"{coeff.numerator}/{coeff.denominator}",
                    }
                )

    out_core.parent.mkdir(parents=True, exist_ok=True)
    with out_core.open("w", encoding="utf-8") as f:
        for rec in recs:
            f.write(json.dumps(rec) + "\n")

    print(
        json.dumps(
            {
                "row": f"{args.chart}/{args.dom}",
                "clarabel_status": str(sol.status),
                "clarabel_support": len(S),
                "vertex_support": len(Sb),
                "tight_rows": len(tight),
                "rank": rank,
                "core": str(out_core),
                "min_residual_float": float(residual.min()),
                "max_x_float": float(x.max()),
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
