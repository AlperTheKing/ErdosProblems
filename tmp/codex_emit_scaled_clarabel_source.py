#!/usr/bin/env python3
"""Emit a rational source solution by scaling and flooring a Clarabel point.

This is a certificate *candidate* generator.  It makes no proof claim; the
official exact source_solution_check is the gate.  It is useful when basis
extraction is the only failing step and the numeric full-source point is very
close to feasible.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import clarabel
import numpy as np
from scipy import sparse

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("chart", type=int)
    ap.add_argument("dom", type=int)
    ap.add_argument("band")
    ap.add_argument("support")
    ap.add_argument("out_solution")
    ap.add_argument("--scale", type=float, default=0.999)
    ap.add_argument("--den", type=int, default=10**12)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--min-emit", type=float, default=0.0)
    args = ap.parse_args()

    prepared, columns, _m, _b = probe.build_lp(args.chart, args.dom, args.band, args.support)
    target = np.array([float(x) for x in prepared.p_beta], dtype=float)
    m = len(target)
    ncol = len(columns)

    ri = []
    cj = []
    vv = []
    for j, col in enumerate(columns):
        acc = {}
        for r, coeff in col.terms:
            acc[r] = acc.get(r, 0.0) + float(coeff)
        for r, val in acc.items():
            ri.append(r)
            cj.append(j)
            vv.append(val)
    A = sparse.csc_matrix((vv, (ri, cj)), shape=(m, ncol))

    q = np.array([1.0 + ((j * 1103515245 + args.seed) % 100003) / 100003.0 for j in range(ncol)])
    P = sparse.csc_matrix((ncol, ncol))
    Amat = sparse.vstack([A, -sparse.identity(ncol, format="csc")], format="csc")
    b = np.concatenate([target, np.zeros(ncol)])
    cones = [clarabel.NonnegativeConeT(m), clarabel.NonnegativeConeT(ncol)]
    st = clarabel.DefaultSettings()
    st.verbose = False
    st.max_iter = 400
    sol = clarabel.DefaultSolver(P, q, Amat, b, cones, st).solve()
    x = np.array(sol.x, dtype=float)

    full_res = target - A.dot(x)
    out = Path(args.out_solution)
    out.parent.mkdir(parents=True, exist_ok=True)
    records = 0
    den = int(args.den)
    with out.open("w", encoding="utf-8") as f:
        for j, val in enumerate(x):
            y = max(0.0, args.scale * float(val))
            if y <= args.min_emit:
                continue
            num = math.floor(y * den)
            if num <= 0:
                continue
            f.write(json.dumps({"source_col": j, "num": int(num), "den": den}) + "\n")
            records += 1

    print(
        json.dumps(
            {
                "row": f"{args.chart}/{args.dom}",
                "status": str(sol.status),
                "scale": args.scale,
                "den": den,
                "records": records,
                "numeric_full_min_residual": float(full_res.min()),
                "numeric_x_min": float(x.min()),
                "numeric_x_max": float(x.max()),
                "solution": str(out),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
