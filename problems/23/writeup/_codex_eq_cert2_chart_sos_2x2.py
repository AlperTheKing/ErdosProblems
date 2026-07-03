#!/usr/bin/env python3
"""Small CVXPY/Clarabel smoke for CERT-2 chart0 sparse 2x2 SOS atoms.

Search only; no exact certificate claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import cvxpy as cp
import numpy as np
from scipy.sparse import coo_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_sos as sos


def degree12_generators(chart: int):
    _target, gens, meta = lp.build_chart(chart)
    return gens, meta


def repair_columns_degree12(target12, generators, max_cols: int):
    negative_target = [exp for exp, coeff in target12.items() if coeff < 0]
    seen = set()
    cols = []
    for gi, gen in enumerate(generators):
        beta_degree = 12 - gen.degree
        gen_negative = [exp for exp, coeff in gen.terms.items() if coeff < 0]
        for target_exp in negative_target:
            for gen_exp in gen_negative:
                beta = lp.sub_exp(target_exp, gen_exp)
                if beta is None or sum(beta) != beta_degree:
                    continue
                key = (gi, beta)
                if key in seen:
                    continue
                seen.add(key)
                cols.append(lp.Column(gi, beta, lp.multinomial(beta_degree, beta)))
                if max_cols and len(cols) >= max_cols:
                    return cols
    return cols


def column_terms_degree12(col, gen):
    return lp.column_terms(col, gen)


def selected_atoms(target12, max_atoms: int, mode: str):
    all_deg6 = list(sos.weak_compositions(6, lp.SX_DIM))
    seed = (6,) + (0,) * (lp.SX_DIM - 1)
    atoms = []
    neg_rows = sorted((exp, coeff) for exp, coeff in target12.items() if coeff < 0)
    for row, coeff in neg_rows:
        best = None
        all_for_row = []
        for a in all_deg6:
            b = sos.sub_exp(row, a)
            if b is None or sum(b) != 6 or a > b or a == seed or b == seed:
                continue
            da = tuple(2 * x for x in a)
            db = tuple(2 * x for x in b)
            ca = target12.get(da, Fraction(0))
            cb = target12.get(db, Fraction(0))
            if ca > 0 and cb > 0:
                score = min(ca, cb)
                cand = (score, a, b, row)
                all_for_row.append((a, b, row))
                if best is None or cand > best:
                    best = cand
        if mode == "best":
            if best is not None:
                _score, a, b, row = best
                atoms.append((a, b, row))
        elif mode == "all":
            atoms.extend(all_for_row)
        else:
            raise ValueError(f"unknown atom mode {mode!r}")
        if max_atoms and len(atoms) >= max_atoms:
            return atoms[:max_atoms]
    return atoms


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--max-cols", type=int, default=3000)
    ap.add_argument("--max-atoms", type=int, default=500)
    ap.add_argument("--atom-mode", choices=["best", "all"], default="best")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_2x2_smoke_v1.json")
    args = ap.parse_args()

    target11, generators, meta = lp.build_chart(args.chart)
    target12 = sos.mul_linear(target11)
    cols = repair_columns_degree12(target12, generators, args.max_cols)
    col_maps = [column_terms_degree12(c, generators[c.gen_index]) for c in cols]
    atoms = selected_atoms(target12, args.max_atoms, args.atom_mode)

    row_set = set(target12)
    for mp in col_maps:
        row_set.update(mp)
    for a, b, cross in atoms:
        row_set.add(cross)
        row_set.add(tuple(2 * x for x in a))
        row_set.add(tuple(2 * x for x in b))
    rows = sorted(row_set)
    row_index = {r: i for i, r in enumerate(rows)}

    data = []
    rr = []
    cc = []
    for j, mp in enumerate(col_maps):
        for exp, coeff in mp.items():
            rr.append(row_index[exp])
            cc.append(j)
            data.append(float(coeff))
    Acol = coo_matrix((data, (rr, cc)), shape=(len(rows), len(cols))).tocsr()

    au_r = []
    au_c = []
    av_r = []
    av_c = []
    aw_r = []
    aw_c = []
    for k, (a, b, cross) in enumerate(atoms):
        au_r.append(row_index[tuple(2 * z for z in a)])
        au_c.append(k)
        av_r.append(row_index[tuple(2 * z for z in b)])
        av_c.append(k)
        aw_r.append(row_index[cross])
        aw_c.append(k)
    ones = [1.0] * len(atoms)
    Au = coo_matrix((ones, (au_r, au_c)), shape=(len(rows), len(atoms))).tocsr()
    Av = coo_matrix((ones, (av_r, av_c)), shape=(len(rows), len(atoms))).tocsr()
    Aw = coo_matrix((ones, (aw_r, aw_c)), shape=(len(rows), len(atoms))).tocsr()
    target_vec = np.array([float(target12.get(r, Fraction(0))) for r in rows])

    x = cp.Variable(len(cols), nonneg=True) if cols else None
    u = cp.Variable(len(atoms), nonneg=True)
    v = cp.Variable(len(atoms), nonneg=True)
    w = cp.Variable(len(atoms))
    expr = target_vec
    if cols:
        expr = expr - Acol @ x
    expr = expr - Au @ u - Av @ v - 2 * (Aw @ w)
    constraints = [expr >= 0]
    for k in range(len(atoms)):
        constraints.append(cp.SOC(u[k] + v[k], cp.hstack([2 * w[k], u[k] - v[k]])))
    obj_terms = []
    if cols:
        obj_terms.append(cp.sum(x))
    obj_terms.append(cp.sum(u + v))
    prob = cp.Problem(cp.Minimize(sum(obj_terms)), constraints)
    try:
        value = prob.solve(solver=cp.CLARABEL, verbose=False, time_limit=args.time_limit)
        status = prob.status
    except Exception as exc:
        status = f"EXCEPTION:{type(exc).__name__}:{exc}"
        value = None
    out = {
        "schema": "eq_cert2_chart_sos_2x2_smoke_v1",
        "chart": args.chart,
        "max_cols": args.max_cols,
        "max_atoms": args.max_atoms,
        "columns": len(cols),
        "atoms": len(atoms),
        "rows": len(rows),
        "status": status,
        "objective": None if value is None else float(value),
        "meta": meta,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "meta"}, indent=2, sort_keys=True))
    if status not in {"optimal", "optimal_inaccurate"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


