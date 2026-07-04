#!/usr/bin/env python3
"""Clarabel LP runner for EQ-ODL1 shifted-cone searches.

Clarabel is used only as a numerical search oracle.  A successful primal solve
is accepted only if returned coefficients rationalize and pass exact residual
checking.  A primal-infeasible solve can optionally be replayed as an exact
Farkas certificate for the selected finite LP support: z >= 0, A^T z = 0,
b^T z < 0 for A x + s = b, s in the nonnegative cone.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import clarabel
import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, eye, vstack

import _codex_eq_odl1_shifted_lp as eq
import _codex_eq_odl1_reduced_lp as red


def select_columns(target_expr, generators: list[eq.Generator], mode: str, diagnostic: str, names_csv: str) -> list[eq.Column]:
    if mode == "negative":
        return eq.candidate_columns(eq.coeff_map(target_expr), generators, "negative")
    if mode == "greedy":
        return red.load_greedy_columns(Path(diagnostic), generators)
    if mode == "generators":
        names = {x.strip() for x in names_csv.split(",") if x.strip()}
        return red.load_generator_columns(target_expr, generators, names)
    raise ValueError(mode)


def exact_maps(target_expr, generators: list[eq.Generator], cols: list[eq.Column]):
    target = eq.coeff_map(target_expr)
    col_maps = [eq.column_map(col, generators) for col in cols]
    monoms = sorted(set(target) | set().union(*(set(m) for m in col_maps))) if col_maps else sorted(target)
    row_index = {m: i for i, m in enumerate(monoms)}
    return target, col_maps, monoms, row_index


def build_lp_matrix(target_expr, generators: list[eq.Generator], cols: list[eq.Column]):
    target, col_maps, monoms, row_index = exact_maps(target_expr, generators, cols)
    data = []
    rows = []
    col_ids = []
    for j, cmap in enumerate(col_maps):
        for exp, coeff in cmap.items():
            rows.append(row_index[exp])
            col_ids.append(j)
            data.append(float(coeff))
    mat = coo_matrix((data, (rows, col_ids)), shape=(len(monoms), len(cols))).tocsc()
    b_ub = np.array([float(target.get(exp, Fraction(0))) for exp in monoms], dtype=float)
    return mat, b_ub, len(monoms)


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    num = q.numerator
    den = q.denominator
    if abs(num).bit_length() < 1024 and den.bit_length() < 1024:
        return str(q)
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(num).bit_length()}/den_bits={den.bit_length()}"

def dual_float_stats(a, b, z_raw) -> dict[str, object]:
    z = np.array(z_raw, dtype=float)
    atz = a.T @ z
    return {
        "dual_min_z": float(np.min(z)) if z.size else 0.0,
        "dual_max_abs_ATz": float(np.max(np.abs(atz))) if atz.size else 0.0,
        "dual_btz": float(b @ z),
    }


def exact_dual_check(target_expr, generators: list[eq.Generator], cols: list[eq.Column], z_raw, max_denominators: list[int], clamp_negative: bool = True) -> dict[str, object]:
    target, col_maps, monoms, row_index = exact_maps(target_expr, generators, cols)
    n_constraints = len(monoms)
    n_cols = len(cols)
    if len(z_raw) != n_constraints + n_cols:
        return {
            "exact_dual_ok": False,
            "error": f"dual length {len(z_raw)} != {n_constraints}+{n_cols}",
        }
    attempts = []
    for max_den in max_denominators:
        zq = []
        for val in z_raw:
            x = float(val)
            if clamp_negative and x < 0 and x > -1e-8:
                x = 0.0
            if clamp_negative:
                x = max(0.0, x)
            zq.append(Fraction(str(x)).limit_denominator(max_den))
        min_z = min(zq) if zq else Fraction(0)
        nonzero = []
        max_abs = Fraction(0)
        for j, cmap in enumerate(col_maps):
            acc = -zq[n_constraints + j]
            for exp, coeff in cmap.items():
                acc += coeff * zq[row_index[exp]]
            if acc:
                if len(nonzero) < 20:
                    nonzero.append({"column": j, "value": fmt_fraction(acc)})
                if abs(acc) > max_abs:
                    max_abs = abs(acc)
        btz = sum(target.get(exp, Fraction(0)) * zq[i] for i, exp in enumerate(monoms))
        attempt = {
            "max_denominator": max_den,
            "min_z": fmt_fraction(min_z),
            "btz": fmt_fraction(btz),
            "max_abs_ATz": fmt_fraction(max_abs),
            "nonzero_ATz_count": sum(1 for j, cmap in enumerate(col_maps) if (-zq[n_constraints + j] + sum(coeff * zq[row_index[exp]] for exp, coeff in cmap.items())) != 0),
            "nonzero_ATz_first": nonzero,
        }
        attempts.append(attempt)
        if min_z >= 0 and not nonzero and btz < 0:
            return {
                "exact_dual_ok": True,
                "max_denominator": max_den,
                "btz": fmt_fraction(btz),
                "min_z": fmt_fraction(min_z),
                "attempts": attempts,
            }
    return {"exact_dual_ok": False, "attempts": attempts}

def exact_farkas_check(target_expr, generators: list[eq.Generator], cols: list[eq.Column], z_raw, max_denominators: list[int], clamp_negative: bool = True) -> dict[str, object]:
    """Replay the LP Farkas certificate y >= 0, A^T y >= 0, b^T y < 0.

    The Clarabel model represents x >= 0 by adding a second nonnegative cone.
    For a proof of infeasibility of A x <= b, x >= 0, we only need the first
    block of the dual ray: y for A x <= b. The second block is numerically
    close to A^T y, but independently rounding it makes exact stationarity much
    harder than the actual Farkas certificate.
    """
    target, col_maps, monoms, row_index = exact_maps(target_expr, generators, cols)
    n_constraints = len(monoms)
    if len(z_raw) < n_constraints:
        return {
            "exact_farkas_ok": False,
            "error": f"dual length {len(z_raw)} < {n_constraints}",
        }
    attempts = []
    for max_den in max_denominators:
        yq = []
        for val in z_raw[:n_constraints]:
            x = float(val)
            if clamp_negative and x < 0 and x > -1e-8:
                x = 0.0
            if clamp_negative:
                x = max(0.0, x)
            yq.append(Fraction(str(x)).limit_denominator(max_den))
        min_y = min(yq) if yq else Fraction(0)
        min_aty = None
        negative = []
        negative_count = 0
        zero_cols = 0
        for j, cmap in enumerate(col_maps):
            acc = sum(coeff * yq[row_index[exp]] for exp, coeff in cmap.items())
            if min_aty is None or acc < min_aty:
                min_aty = acc
            if acc < 0:
                negative_count += 1
                if len(negative) < 20:
                    negative.append({"column": j, "value": fmt_fraction(acc)})
            if acc == 0:
                zero_cols += 1
        bty = sum(target.get(exp, Fraction(0)) * yq[i] for i, exp in enumerate(monoms))
        attempt = {
            "max_denominator": max_den,
            "min_y": fmt_fraction(min_y),
            "bty": fmt_fraction(bty),
            "min_ATy": fmt_fraction(min_aty if min_aty is not None else Fraction(0)),
            "negative_ATy_count": negative_count,
            "zero_ATy_count": zero_cols,
            "negative_ATy_first": negative,
        }
        attempts.append(attempt)
        if min_y >= 0 and negative_count == 0 and bty < 0:
            return {
                "exact_farkas_ok": True,
                "max_denominator": max_den,
                "bty": fmt_fraction(bty),
                "min_y": fmt_fraction(min_y),
                "min_ATy": attempt["min_ATy"],
                "zero_ATy_count": zero_cols,
                "certificate_y": [fmt_fraction(q) for q in yq],
                "attempts": attempts,
            }
    return {"exact_farkas_ok": False, "attempts": attempts}


def solve_clarabel(
    target_expr,
    cols: list[eq.Column],
    objective: str,
    time_limit: float,
    max_iter: int,
    threads: int,
    max_denominators: list[int],
    store_dual: bool,
):
    generators = eq.build_generators()
    a_ub, b_ub, constraints = build_lp_matrix(target_expr, generators, cols)
    n = len(cols)
    p = csc_matrix((n, n), dtype=float)
    q = np.zeros(n, dtype=float) if objective == "zero" else np.ones(n, dtype=float)
    # A_ub x <= b  => A_ub x + s = b, s >= 0.
    # x >= 0       => -I x + s = 0, s >= 0.
    a = vstack([a_ub, -eye(n, format="csc")], format="csc")
    b = np.concatenate([b_ub, np.zeros(n, dtype=float)])
    cones = [clarabel.NonnegativeConeT(constraints), clarabel.NonnegativeConeT(n)]
    settings = clarabel.DefaultSettings()
    settings.verbose = True
    settings.time_limit = float(time_limit)
    settings.max_iter = int(max_iter)
    settings.max_threads = int(threads)
    print("clarabel vars", n, "constraints", constraints, "rows", a.shape[0], flush=True)
    solver = clarabel.DefaultSolver(p, q, a, b, cones, settings)
    solution = solver.solve()
    status = str(solution.status)
    out = {
        "schema": "eq_odl1_clarabel_lp_v2",
        "variables": n,
        "constraints": constraints,
        "rows_with_nonnegativity": int(a.shape[0]),
        "objective": objective,
        "status": status,
        "solve_time": getattr(solution, "solve_time", None),
        "iterations": getattr(solution, "iterations", None),
        "exact_ok": None,
    }
    print("Clarabel", status, flush=True)
    if hasattr(solution, "z") and solution.z is not None:
        out["dual_float_stats"] = dual_float_stats(a, b, solution.z)
        if "PrimalInfeasible" in status:
            out["dual_exact_check"] = exact_dual_check(target_expr, generators, cols, solution.z, max_denominators)
            out["farkas_exact_check"] = exact_farkas_check(target_expr, generators, cols, solution.z, max_denominators)
        if store_dual:
            out["dual_ray"] = [float(x) for x in solution.z]
    if "Solved" not in status:
        return out
    raw = list(solution.x)
    out["float_nonzero"] = int(sum(1 for x in raw if x > 1e-9))
    for max_den in max_denominators:
        coeffs = [Fraction(str(max(0.0, x))).limit_denominator(max_den) for x in raw]
        ok, check = eq.exact_check(target_expr, generators, cols, coeffs)
        print("try", max_den, "ok", ok, "min", check["residual_min_coeff"], "neg", check["negative_terms"][:1], flush=True)
        if ok:
            out.update({"exact_ok": True, "max_denominator": max_den, "exact_check": check})
            return out
    ok, check = eq.exact_check(target_expr, generators, cols, [Fraction(str(max(0.0, x))) for x in raw])
    out.update({"exact_ok": ok, "exact_check": check})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["negative", "greedy", "generators"], default="negative")
    ap.add_argument("--diagnostic", default="tmp/eq_odl1_support_diagnose_v2.json")
    ap.add_argument("--generators", default="F1,F2,F3,F4,B0_eta25_25")
    ap.add_argument("--objective", choices=["zero", "sum"], default="sum")
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--max-iter", type=int, default=1000)
    ap.add_argument("--threads", type=int, default=64)
    ap.add_argument("--max-den", default="1000,1000000")
    ap.add_argument("--store-dual", action="store_true")
    ap.add_argument("--summary", default="tmp/eq_odl1_clarabel_lp_v1.json")
    args = ap.parse_args()

    target_expr, meta = eq.build_target()
    generators = eq.build_generators()
    cols = select_columns(target_expr, generators, args.mode, args.diagnostic, args.generators)
    max_denominators = [int(x) for x in args.max_den.split(",") if x]
    result = solve_clarabel(target_expr, cols, args.objective, args.time_limit, args.max_iter, args.threads, max_denominators, args.store_dual)
    result["mode"] = args.mode
    result["selected_generators"] = args.generators
    result["diagnostic"] = args.diagnostic
    result["target_meta"] = {k: v for k, v in meta.items() if k != "I_EQ"}
    result["target_terms"] = len(eq.coeff_map(target_expr))
    result["target_negative_terms"] = sum(1 for c in eq.coeff_map(target_expr).values() if c < 0)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in ["status", "exact_ok", "variables", "constraints", "iterations", "dual_float_stats"]}, sort_keys=True))


if __name__ == "__main__":
    main()




