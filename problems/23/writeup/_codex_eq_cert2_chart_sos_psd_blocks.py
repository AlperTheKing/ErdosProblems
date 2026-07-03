#!/usr/bin/env python3
"""Direct Clarabel PSD-block probe for CERT-2 ChartSOS chart certificates.

Adds full PSD Gram blocks for disconnected sparse Gram components up to a size cap.
Search helper only; no exact certificate claim.
"""

from __future__ import annotations

import argparse
import json
import math
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
import _codex_eq_cert2_chart_sos_sparsity as sp


def build_psd_blocks(chart: int, seed_rows: str | None, max_block_size: int, max_blocks: int):
    target11, generators, meta = lp.build_chart(chart)
    target12 = sos.mul_linear(target11)
    rows = sp.rows_from_seed(seed_rows, target12)
    basis = sp.sparse_basis_for_rows(rows)
    adj, _by_sum, _pair_count, _represented, _diag_rows = sp.build_pair_graph(basis, rows)
    comps = sp.components(adj)
    selected = []
    for comp in comps:
        if len(comp) <= max_block_size:
            selected.append(comp)
            if max_blocks and len(selected) >= max_blocks:
                break
    return target12, generators, meta, basis, comps, selected


def repair_columns(target12, generators, max_cols: int):
    return s2.repair_columns_degree12(target12, generators, max_cols)


def build_problem(
    chart: int,
    seed_rows: str | None,
    max_block_size: int,
    max_blocks: int,
    max_cols: int,
    objective: str,
):
    target12, generators, meta, basis, comps, blocks = build_psd_blocks(
        chart, seed_rows, max_block_size, max_blocks
    )
    cols = repair_columns(target12, generators, max_cols)
    col_maps = [s2.column_terms_degree12(c, generators[c.gen_index]) for c in cols]

    n_x = len(cols)
    psd_entries = []
    row_set = set(target12)
    for mp in col_maps:
        row_set.update(mp)
    for bi, comp in enumerate(blocks):
        # Clarabel PSDTriangle order is column-wise: (0,0),(0,1),(1,1),(0,2),...
        for local_j, gj in enumerate(comp):
            for local_i in range(local_j + 1):
                gi = comp[local_i]
                a = basis[gi]
                b = basis[gj]
                exp = tuple(x + y for x, y in zip(a, b))
                row_set.add(exp)
                psd_entries.append((bi, local_i, local_j, gi, gj, exp))
    rows = sorted(row_set)
    row_index = {r: i for i, r in enumerate(rows)}

    off_psd = n_x
    n_psd = len(psd_entries)
    n_var = n_x + n_psd
    rr = []
    cc = []
    data = []
    for j, mp in enumerate(col_maps):
        for exp, coeff in mp.items():
            rr.append(row_index[exp])
            cc.append(j)
            data.append(float(coeff))
    for k, (_bi, li, lj, _gi, _gj, exp) in enumerate(psd_entries):
        rr.append(row_index[exp])
        cc.append(off_psd + k)
        data.append(1.0 if li == lj else 2.0)
    A_res = coo_matrix((data, (rr, cc)), shape=(len(rows), n_var)).tocsc()
    b_res = np.array([float(target12.get(r, Fraction(0))) for r in rows], dtype=float)

    if n_x:
        A_x = coo_matrix(([-1.0] * n_x, (list(range(n_x)), list(range(n_x)))), shape=(n_x, n_var)).tocsc()
        b_x = np.zeros(n_x, dtype=float)
    else:
        A_x = csc_matrix((0, n_var))
        b_x = np.zeros(0, dtype=float)

    cone_rows = []
    cone_cols = []
    cone_data = []
    psd_offset = 0
    block_dims = []
    entry_cursor = 0
    for bi, comp in enumerate(blocks):
        dim = len(comp)
        block_dims.append(dim)
        entries = dim * (dim + 1) // 2
        for local in range(entries):
            _bix, li, lj, _gi, _gj, _exp = psd_entries[entry_cursor + local]
            scale = 1.0 if li == lj else math.sqrt(2.0)
            cone_rows.append(psd_offset + local)
            cone_cols.append(off_psd + entry_cursor + local)
            cone_data.append(-scale)
        entry_cursor += entries
        psd_offset += entries
    A_psd = coo_matrix((cone_data, (cone_rows, cone_cols)), shape=(psd_offset, n_var)).tocsc()
    b_psd = np.zeros(psd_offset, dtype=float)

    A = vstack([A_res, A_x, A_psd], format="csc")
    bvec = np.concatenate([b_res, b_x, b_psd])
    q = np.zeros(n_var, dtype=float)
    if objective in {"sum", "cols"} and n_x:
        q[:n_x] = 1.0
    if objective in {"sum", "psd"} and n_psd:
        q[off_psd:] = 1.0
    cones = [clarabel.NonnegativeConeT(len(rows) + n_x)]
    cones.extend(clarabel.PSDTriangleConeT(dim) for dim in block_dims)
    info = {
        "chart": chart,
        "seed_rows": seed_rows,
        "max_block_size": max_block_size,
        "max_blocks": max_blocks,
        "columns": n_x,
        "psd_blocks": len(blocks),
        "psd_block_dims": block_dims,
        "psd_entries": n_psd,
        "all_component_sizes": [len(c) for c in comps],
        "rows": len(rows),
        "variables": n_var,
        "constraints": A.shape[0],
        "nnz": int(A.nnz),
        "objective_mode": objective,
        "meta": meta,
    }
    return A, bvec, q, cones, info, rows


def slack_diagnostics(A, b, x, info, rows):
    if x is None:
        return {}
    slack = np.asarray(b - A.dot(np.asarray(x, dtype=float)), dtype=float)
    n_rows = int(info["rows"])
    n_cols = int(info["columns"])
    coeff = slack[:n_rows]
    gen = slack[n_rows:n_rows + n_cols]
    neg_idx = np.where(coeff < -1e-7)[0]
    top = []
    if neg_idx.size:
        order = neg_idx[np.argsort(coeff[neg_idx])[:10]]
        for idx in order:
            top.append({"row": list(rows[int(idx)]), "slack": float(coeff[int(idx)])})
    return {
        "coeff_slack_min": float(np.min(coeff)) if coeff.size else None,
        "coeff_slack_neg_count_1e-7": int(neg_idx.size),
        "generator_slack_min": float(np.min(gen)) if gen.size else None,
        "top_negative_coeff_rows": top,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--seed-rows", default="")
    ap.add_argument("--max-block-size", type=int, default=120)
    ap.add_argument("--max-blocks", type=int, default=0)
    ap.add_argument("--max-cols", type=int, default=100000)
    ap.add_argument("--objective", choices=["zero", "sum", "cols", "psd"], default="zero")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--tol-feas", type=float, default=0.0)
    ap.add_argument("--tol-gap", type=float, default=0.0)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_psd_blocks_v1.json")
    args = ap.parse_args()

    A, b, q, cones, info, rows = build_problem(
        args.chart, args.seed_rows or None, args.max_block_size, args.max_blocks, args.max_cols, args.objective
    )
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    settings.time_limit = float(args.time_limit)
    if args.tol_feas > 0:
        settings.tol_feas = float(args.tol_feas)
    if args.tol_gap > 0:
        settings.tol_gap_abs = float(args.tol_gap)
        settings.tol_gap_rel = float(args.tol_gap)
    if args.threads > 0 and hasattr(settings, "max_threads"):
        settings.max_threads = int(args.threads)
    solver = clarabel.DefaultSolver(csc_matrix((len(q), len(q))), q, A, b, cones, settings)
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
        diagnostics.update(slack_diagnostics(A, b, getattr(sol, "x", None), info, rows))
    except Exception as exc:
        status = f"EXCEPTION:{type(exc).__name__}:{exc}"
        obj = None
        diagnostics = {}
    out = {"schema": "eq_cert2_chart_sos_psd_blocks_v1", **info, "status": status, "objective": obj, **diagnostics}
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    printable = dict(out)
    printable.pop("meta", None)
    print(json.dumps(printable, indent=2, sort_keys=True))
    if status not in {"Solved", "AlmostSolved"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
