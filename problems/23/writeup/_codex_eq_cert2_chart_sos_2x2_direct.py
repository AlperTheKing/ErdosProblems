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


def split_atoms_for_row(row):
    halves = []
    for x in row:
        halves.append((x // 2, x - x // 2))
    seen = set()
    atoms = []
    for mask in range(1 << len(row)):
        a = tuple(halves[i][(mask >> i) & 1] for i in range(len(row)))
        b = tuple(row[i] - a[i] for i in range(len(row)))
        key = (a, b) if a <= b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        atoms.append((key[0], key[1], row))
    return atoms


def load_extra_atoms(path: str | None, limit_rows: int) -> list[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    if not path:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_rows = data.get("top_negative_coeff_rows") or data.get("rows") or []
    out = []
    for item in raw_rows[:limit_rows if limit_rows > 0 else None]:
        row_data = item.get("row", item) if isinstance(item, dict) else item
        row = tuple(int(x) for x in row_data)
        out.extend(split_atoms_for_row(row))
    return out


def build_problem(
    chart: int,
    max_cols: int,
    max_atoms: int,
    atom_mode: str,
    objective: str,
    extra_atom_rows: str | None,
    extra_atom_row_limit: int,
    extra_atom_split_max: int,
):
    target11, generators, meta = lp.build_chart(chart)
    target12 = sos.mul_linear(target11)
    cols = s2.repair_columns_degree12(target12, generators, max_cols)
    col_maps = [s2.column_terms_degree12(c, generators[c.gen_index]) for c in cols]
    atoms = s2.selected_atoms(target12, max_atoms, atom_mode)
    extra_atoms = load_extra_atoms(extra_atom_rows, extra_atom_row_limit)
    if extra_atom_split_max > 0:
        for row, coeff in target12.items():
            if coeff < 0:
                row_atoms = split_atoms_for_row(row)
                if len(row_atoms) <= extra_atom_split_max:
                    extra_atoms.extend(row_atoms)
    if extra_atoms:
        seen_atoms = set(atoms)
        for atom in extra_atoms:
            if atom not in seen_atoms:
                atoms.append(atom)
                seen_atoms.add(atom)

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
    if objective in {"sum", "cols"} and n_x:
        q[:n_x] = 1.0
    if objective in {"sum", "atoms"} and n_atoms:
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
        "objective_mode": objective,
        "extra_atom_rows": extra_atom_rows,
        "extra_atom_row_limit": extra_atom_row_limit,
        "extra_atom_split_max": extra_atom_split_max,
        "meta": meta,
    }, rows


def slack_diagnostics(A, b, x, info, rows):
    if x is None:
        return {}
    x_arr = np.asarray(x, dtype=float)
    slack = np.asarray(b - A.dot(x_arr), dtype=float)
    n_rows = int(info["rows"])
    n_cols = int(info["columns"])
    n_atoms = int(info["atoms"])
    coeff = slack[:n_rows]
    gen = slack[n_rows:n_rows + n_cols]
    soc = slack[n_rows + n_cols:]
    neg_idx = np.where(coeff < -1e-7)[0]
    top = []
    if neg_idx.size:
        order = neg_idx[np.argsort(coeff[neg_idx])[:10]]
        for idx in order:
            top.append({"row": list(rows[int(idx)]), "slack": float(coeff[int(idx)])})
    soc_margin_min = None
    if n_atoms:
        blocks = soc.reshape((n_atoms, 3))
        margins = blocks[:, 0] - np.sqrt(blocks[:, 1] ** 2 + blocks[:, 2] ** 2)
        soc_margin_min = float(np.min(margins))
    return {
        "coeff_slack_min": float(np.min(coeff)) if coeff.size else None,
        "coeff_slack_neg_count_1e-7": int(neg_idx.size),
        "generator_slack_min": float(np.min(gen)) if gen.size else None,
        "soc_margin_min": soc_margin_min,
        "top_negative_coeff_rows": top,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--max-cols", type=int, default=3000)
    ap.add_argument("--max-atoms", type=int, default=500)
    ap.add_argument("--atom-mode", choices=["best", "all"], default="best")
    ap.add_argument("--objective", choices=["sum", "zero", "cols", "atoms"], default="sum")
    ap.add_argument("--extra-atom-rows", default="")
    ap.add_argument("--extra-atom-row-limit", type=int, default=0)
    ap.add_argument("--extra-atom-split-max", type=int, default=0)
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--max-iter", type=int, default=0)
    ap.add_argument("--tol-feas", type=float, default=0.0)
    ap.add_argument("--tol-gap", type=float, default=0.0)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_2x2_direct_v1.json")
    args = ap.parse_args()

    A, b, q, cones, info, row_exponents = build_problem(
        args.chart,
        args.max_cols,
        args.max_atoms,
        args.atom_mode,
        args.objective,
        args.extra_atom_rows or None,
        args.extra_atom_row_limit,
        args.extra_atom_split_max,
    )
    P = csc_matrix((len(q), len(q)))
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    settings.time_limit = float(args.time_limit)
    if args.max_iter > 0:
        settings.max_iter = int(args.max_iter)
    if args.tol_feas > 0:
        settings.tol_feas = float(args.tol_feas)
    if args.tol_gap > 0:
        settings.tol_gap_abs = float(args.tol_gap)
        settings.tol_gap_rel = float(args.tol_gap)
    if args.threads > 0 and hasattr(settings, "max_threads"):
        settings.max_threads = int(args.threads)
    solver = clarabel.DefaultSolver(P, q, A, b, cones, settings)
    try:
        sol = solver.solve()
        status = str(sol.status)
        obj = None if sol.obj_val is None else float(sol.obj_val)
        diagnostics = {
            "iterations": None if getattr(sol, "iterations", None) is None else int(sol.iterations),
            "solve_time": None if getattr(sol, "solve_time", None) is None else float(sol.solve_time),
            "r_prim": None if getattr(sol, "r_prim", None) is None else float(sol.r_prim),
            "r_dual": None if getattr(sol, "r_dual", None) is None else float(sol.r_dual),
            "obj_val_dual": None if getattr(sol, "obj_val_dual", None) is None else float(sol.obj_val_dual),
        }
        diagnostics.update(slack_diagnostics(A, b, getattr(sol, "x", None), info, row_exponents))
    except Exception as exc:
        status = f"EXCEPTION:{type(exc).__name__}:{exc}"
        obj = None
        diagnostics = {}
    out = {
        "schema": "eq_cert2_chart_sos_2x2_direct_v1",
        **info,
        "status": status,
        "objective": obj,
        **diagnostics,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "meta"}, indent=2, sort_keys=True))
    if status not in {"Solved", "AlmostSolved"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()





