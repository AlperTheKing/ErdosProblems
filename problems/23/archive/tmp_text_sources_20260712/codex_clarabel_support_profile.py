#!/usr/bin/env python3
"""Profile Clarabel solution thresholding for the chart certificate LP."""
from __future__ import annotations

import argparse
import json
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
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--thresholds", default="1e-1,1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9,0")
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
    report = {
        "row": f"{args.chart}/{args.dom}",
        "status": str(sol.status),
        "ncol": ncol,
        "full_min_residual": float(full_res.min()),
        "full_negative_residual_count": int((full_res < -1e-7).sum()),
        "x_min": float(x.min()),
        "x_max": float(x.max()),
        "x_positive_gt_0": int((x > 0).sum()),
        "thresholds": [],
    }
    for raw in args.thresholds.split(","):
        tau = float(raw)
        xt = x.copy()
        xt[xt <= tau] = 0.0
        res = target - A.dot(xt)
        report["thresholds"].append(
            {
                "tau": tau,
                "support": int((x > tau).sum()),
                "min_residual": float(res.min()),
                "negative_residual_count": int((res < -1e-7).sum()),
                "max_violation": float(max(0.0, -res.min())),
            }
        )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
