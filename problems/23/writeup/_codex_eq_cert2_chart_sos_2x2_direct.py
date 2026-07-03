#!/usr/bin/env python3
"""Direct Clarabel smoke for CERT-2 chart0 sparse 2x2 SOS atoms.

This bypasses CVXPY canonicalization. Search helper only; no exact certificate claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import clarabel
import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, vstack

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_sos as sos
import _codex_eq_cert2_chart_sos_2x2 as s2


def build_problem(chart: int, max_cols: int, max_atoms: int, atom_mode: str):
    target11, generators, meta = lp.build_chart(chart)
    target12 = sos.mul_linear(target11)
    cols = s2.repair_columns_degree12(target12, generators, max_cols)
    col_maps = [s2.column_terms_degree12(c, generators[c.gen_index]) for c in cols]
    atoms = s2.selected_atoms(target12, max_atoms, atom_mode)

    row_set = set(target12)
    for mp in col_maps:
        row_set.update(mp)
    for a, b, cross in atoms:
        row_set.add(cross)
        row_set.add(tuple(2 * x for x in a))
        row_set.add(tuple(2 * x for x in b))
    rows = sorted(row_set)
    row_index = {r: i for i, r in enumerate(rows)}

    n_x = len(cols)
    n_atoms = len(atoms)
    off_u = n_x
    off_v = off_u + n_atoms
    off_w = off_v + n_atoms
    n_var = n_x + 3 * n_atoms

    # Residual nonnegative: target - Acol*x - Au*u - Av*v - 2Aw*w >= 0.
    rr = []
    cc = []
    data = []
    for j, mp in enumerate(col_maps):
        for exp, coeff in mp.items():
            rr.append(row_index[exp])
            cc.append(j)
            data.append(float(coeff))
    for k, (a, b, cross) in enumerate(atoms):
        rr.append(row_index[tuple(2 * z for z in a)])
        cc.append(off_u + k)
        data.append(1.0)
        rr.append(row_index[tuple(2 * z for z in b)])
        cc.append(off_v + k)
        data.append(1.0)
        rr.append(row_index[cross])
        cc.append(off_w + k)
        data.append(2.0)
    A_res = coo_matrix((data, (rr, cc)), shape=(len(rows), n_var)).tocsc()
    b_res = np.array([float(target12.get(r, Fraction(0))) for r in rows], dtype=float)

    # x >= 0 for generator multipliers: x = b - A z with A=-I, b=0.
    if n_x:
        rr = list(range(n_x))
        cc = list(range(n_x))
        data = [-1.0] * n_x
        A_x = coo_matrix((data, (rr, cc)), shape=(n_x, n_var)).tocsc()
        b_x = np.zeros(n_x, dtype=float)
    else:
        A_x = csc_matrix((0, n_var))
        b_x = np.zeros(0, dtype=float)

    # SOC per atom: [u+v, 2w, u-v] in SOC, encoded as slack s=b-Az with A=-linear.
    rr = []
    cc = []
    data = []
    for k in range(n_atoms):
        base = 3 * k
        # row base: u + v
        rr.extend([base, base])
        cc.extend([off_u + k, off_v + k])
        data.extend([-1.0, -1.0])
        # row base+1: 2w
        rr.append(base + 1)
        cc.append(off_w + k)
        data.append(-2.0)
        # row base+2: u - v
        rr.extend([base + 2, base + 2])
        cc.extend([off_u + k, off_v + k])
        data.extend([-1.0, 1.0])
    A_soc = coo_matrix((data, (rr, cc)), shape=(3 * n_atoms, n_var)).tocsc()
    b_soc = np.zeros(3 * n_atoms, dtype=float)

    A = vstack([A_res, A_x, A_soc], format="csc")
    bvec = np.concatenate([b_res, b_x, b_soc])
    q = np.zeros(n_var, dtype=float)
    if n_x:
        q[:n_x] = 1.0
    if n_atoms:
        q[off_u:off_v] = 1.0
        q[off_v:off_w] = 1.0
    cones = []
    cones.append(clarabel.NonnegativeConeT(len(rows) + n_x))
    cones.extend(clarabel.SecondOrderConeT(3) for _ in range(n_atoms))
    return A, bvec, q, cones, {
        "chart": chart,
        "columns": n_x,
        "atoms": n_atoms,
        "rows": len(rows),
        "variables": n_var,
        "constraints": A.shape[0],
        "nnz": int(A.nnz),
        "max_cols": max_cols,
        "max_atoms": max_atoms,
        "atom_mode": atom_mode,
        "meta": meta,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--max-cols", type=int, default=3000)
    ap.add_argument("--max-atoms", type=int, default=500)
    ap.add_argument("--atom-mode", choices=["best", "all"], default="best")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_2x2_direct_v1.json")
    args = ap.parse_args()

    A, b, q, cones, info = build_problem(args.chart, args.max_cols, args.max_atoms, args.atom_mode)
    P = csc_matrix((len(q), len(q)))
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    settings.time_limit = float(args.time_limit)
    if args.threads > 0 and hasattr(settings, "max_threads"):
        settings.max_threads = int(args.threads)
    solver = clarabel.DefaultSolver(P, q, A, b, cones, settings)
    try:
        sol = solver.solve()
        status = str(sol.status)
        obj = None if sol.obj_val is None else float(sol.obj_val)
    except Exception as exc:
        status = f"EXCEPTION:{type(exc).__name__}:{exc}"
        obj = None
    out = {
        "schema": "eq_cert2_chart_sos_2x2_direct_v1",
        **info,
        "status": status,
        "objective": obj,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "meta"}, indent=2, sort_keys=True))
    if status not in {"Solved", "AlmostSolved"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
