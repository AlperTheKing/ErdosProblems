#!/usr/bin/env python3
"""Generate and exactly verify finite LP dual certificates for SCB.

The optimizer is used only to discover integer dual multipliers.  Verification
reconstructs the integer matrix and checks dual feasibility and objective with
Python integers; it does not trust the floating-point optimum.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c56_image", HERE / "C56_image_lp_dual.py")
if not SPEC or not SPEC.loader:
    raise RuntimeError("cannot load C56_image_lp_dual.py")
C56 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C56
SPEC.loader.exec_module(C56)


def build(limit: int):
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    pairs = {n: C56.admissible_pairs(n) for n in values}
    hard = [n for n in values if C56.hard_shape(n, pairs[n])]
    splitless = [n for n in values if n not in (2, 3) and not pairs[n]]

    lp = C56.LPBuilder()
    t: dict[int, int] = {}
    for n in values:
        if n in (2, 3):
            t[n] = lp.var(f"t_{n}", 1.0, 1.0)
        elif n in splitless:
            t[n] = lp.var(f"t_{n}", 0.0, 0.0)
        else:
            t[n] = lp.var(f"t_{n}")

    for n in values:
        for a, b in pairs[n]:
            lp.le(
                {t[a]: 1.0, t[b]: 1.0, t[n]: -1.0},
                1.0,
                f"closure_{n}_{a}_{b}",
            )

    q: dict[int, int] = {}
    for m in values:
        child = 2 * m - 1
        if child > limit:
            continue
        z = lp.var(f"q_{child}")
        q[child] = z
        lp.le({z: 1.0, t[m]: 1.0}, 1.0, f"q_le_notparent_{child}")
        lp.le({z: 1.0, t[child]: -1.0}, 0.0, f"q_le_child_{child}")
        lp.le(
            {t[child]: 1.0, t[m]: -1.0, z: -1.0},
            0.0,
            f"q_ge_difference_{child}",
        )

    c = [0] * len(lp.names)
    for n in hard:
        c[t[n]] += 1
    for z in q.values():
        c[z] += 1
    return lp, c, hard, splitless


def rounded_ints(values, tolerance: float, label: str) -> tuple[list[int], float]:
    out: list[int] = []
    worst = 0.0
    for value in values:
        integer = int(round(float(value)))
        error = abs(float(value) - integer)
        worst = max(worst, error)
        if error > tolerance:
            raise RuntimeError(f"nonintegral {label} marginal {value} (error {error})")
        out.append(integer)
    return out, worst


def generate(limit: int, tolerance: float) -> dict:
    lp, c, hard, splitless = build(limit)
    result = linprog(
        np.asarray(c, dtype=float),
        A_ub=lp.matrix(),
        b_ub=np.asarray(lp.rhs),
        bounds=lp.bounds,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    row, e_row = rounded_ints(result.ineqlin.marginals, tolerance, "row")
    lower, e_lower = rounded_ints(result.lower.marginals, tolerance, "lower")
    upper, e_upper = rounded_ints(result.upper.marginals, tolerance, "upper")
    cert = {
        "limit": limit,
        "hard_count": len(hard),
        "splitless_count": len(splitless),
        "variable_count": len(lp.names),
        "row_count": len(lp.rhs),
        "floating_objective": float(result.fun),
        "max_rounding_error": max(e_row, e_lower, e_upper),
        "row": [[lp.row_names[i], y] for i, y in enumerate(row) if y],
        "lower": [[lp.names[i], y] for i, y in enumerate(lower) if y],
        "upper": [[lp.names[i], y] for i, y in enumerate(upper) if y],
    }
    verify_one(cert)
    return cert


def verify_one(cert: dict) -> dict:
    limit = int(cert["limit"])
    lp, c, hard, splitless = build(limit)
    row_index = {name: i for i, name in enumerate(lp.row_names)}
    var_index = {name: i for i, name in enumerate(lp.names)}

    row = [0] * len(lp.rhs)
    lower = [0] * len(lp.names)
    upper = [0] * len(lp.names)
    for name, value in cert["row"]:
        row[row_index[name]] = int(value)
    for name, value in cert["lower"]:
        lower[var_index[name]] = int(value)
    for name, value in cert["upper"]:
        upper[var_index[name]] = int(value)

    if not all(value <= 0 for value in row):
        raise RuntimeError("positive <=-row dual multiplier")
    if not all(value >= 0 for value in lower):
        raise RuntimeError("negative lower-bound dual multiplier")
    if not all(value <= 0 for value in upper):
        raise RuntimeError("positive upper-bound dual multiplier")

    stationarity = [lower[j] + upper[j] for j in range(len(lp.names))]
    for i, j, value in zip(lp.rows, lp.cols, lp.data):
        integer = int(round(value))
        if value != integer:
            raise RuntimeError("nonintegral model coefficient")
        stationarity[j] += row[i] * integer
    if stationarity != c:
        raise RuntimeError("exact stationarity check failed")

    objective = 0
    for rhs, value in zip(lp.rhs, row):
        integer = int(round(rhs))
        if rhs != integer:
            raise RuntimeError("nonintegral right-hand side")
        objective += integer * value
    for (lo, hi), lo_value, hi_value in zip(lp.bounds, lower, upper):
        ilo = int(round(lo))
        ihi = int(round(hi))
        if lo != ilo or hi != ihi:
            raise RuntimeError("nonintegral variable bound")
        objective += ilo * lo_value + ihi * hi_value

    if len(hard) != int(cert["hard_count"]):
        raise RuntimeError("hard-count mismatch")
    if len(splitless) != int(cert["splitless_count"]):
        raise RuntimeError("splitless-count mismatch")
    if objective < len(hard):
        raise RuntimeError("dual objective does not prove SCB")
    return {
        "limit": limit,
        "hard_count": len(hard),
        "exact_dual_objective": objective,
        "exact_margin": objective - len(hard),
        "nonzero_row": len(cert["row"]),
        "nonzero_lower": len(cert["lower"]),
        "nonzero_upper": len(cert["upper"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int)
    parser.add_argument("--generate", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--tolerance", type=float, default=1e-7)
    args = parser.parse_args()

    if bool(args.generate) == bool(args.verify):
        parser.error("choose exactly one of --generate or --verify")

    if args.generate:
        if not args.limits:
            parser.error("--generate requires --limits")
        certificates = [generate(limit, args.tolerance) for limit in args.limits]
        args.generate.parent.mkdir(parents=True, exist_ok=True)
        args.generate.write_text(json.dumps(certificates, indent=2) + "\n", encoding="utf-8")
        summary = [verify_one(cert) for cert in certificates]
    else:
        certificates = json.loads(args.verify.read_text(encoding="utf-8"))
        summary = [verify_one(cert) for cert in certificates]

    text = json.dumps(summary, indent=2)
    print(text)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
