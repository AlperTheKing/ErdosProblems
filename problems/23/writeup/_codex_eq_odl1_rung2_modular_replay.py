#!/usr/bin/env python3
"""Modular exact replay for the first EQ-ODL1 Rung-2 square core.

This is the exact-reconstruction path for the numerically feasible reduced
support chart.  It solves the same floating LP used by the SciPy core probe,
selects an independent square core by QR on the dual-active rows, then solves
the core over several finite fields and rationally reconstructs the basic
solution.  The reconstructed multipliers are accepted only after exact Fraction
verification against the selected core and, for the full core, against every
Bernstein row of the reduced LP.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = 33
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_list(count: int) -> list[int]:
    out: list[int] = []
    p = (1 << 30) - 35
    if p % 2 == 0:
        p -= 1
    while len(out) < count:
        if is_prime(p):
            out.append(p)
        p -= 2
    return out

def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 1024 and q.denominator.bit_length() < 1024:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def frac_mod(q: Fraction, p: int) -> int:
    return (q.numerator % p) * pow(q.denominator % p, -1, p) % p


def solve_mod_prime(n: int, terms: list[tuple[int, int, Fraction]], rhs: list[Fraction], p: int) -> list[int] | None:
    aug = np.zeros((n, n + 1), dtype=np.int64)
    for i, j, coeff in terms:
        aug[i, j] = (int(aug[i, j]) + frac_mod(coeff, p)) % p
    for i, coeff in enumerate(rhs):
        aug[i, n] = frac_mod(coeff, p)

    for k in range(n):
        nz = np.flatnonzero(aug[k:, k])
        if nz.size == 0:
            return None
        piv = k + int(nz[0])
        if piv != k:
            aug[[k, piv], :] = aug[[piv, k], :]
        inv = pow(int(aug[k, k]), -1, p)
        aug[k, k:] = (aug[k, k:] * inv) % p
        if k + 1 < n:
            factors = aug[k + 1 :, k].copy()
            rows = np.flatnonzero(factors)
            if rows.size:
                sub = k + 1 + rows
                aug[sub, k:] = (aug[sub, k:] - factors[rows, None] * aug[k, k:]) % p

    x = np.zeros(n, dtype=np.int64)
    for i in range(n - 1, -1, -1):
        total = 0
        # Keep int64 dot products below overflow: 8 * (2^30)^2 < 2^63.
        for start in range(i + 1, n, 8):
            end = min(n, start + 8)
            total = (total + int(np.dot(aug[i, start:end], x[start:end]))) % p
        x[i] = (int(aug[i, n]) - total) % p
    return [int(v) for v in x]


def crt_pair(a: int, m: int, b: int, p: int) -> tuple[int, int]:
    t = ((b - a) % p) * pow(m % p, -1, p) % p
    return a + m * t, m * p


def rational_reconstruct(a: int, m: int) -> Fraction | None:
    a %= m
    bound = math.isqrt((m - 1) // 2)
    r0, r1 = m, a
    s0, s1 = 0, 1
    while abs(r1) > bound:
        if r1 == 0:
            return None
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    num, den = r1, s1
    if den < 0:
        num, den = -num, -den
    if den == 0 or den > bound or math.gcd(abs(num), den) != 1:
        return None
    try:
        if (num * pow(den, -1, m) - a) % m != 0:
            return None
    except ValueError:
        return None
    return Fraction(num, den)


def solve_float_and_select(args):
    prepared, columns, mat, b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    c = np.array([probe.stable_column_weight(col, args.objective) for col in columns], dtype=float)
    res = linprog(
        c=c,
        A_ub=mat,
        b_ub=b_ub,
        bounds=[(0, None)] * len(columns),
        method=args.method,
        options={"time_limit": args.time_limit},
    )
    if not res.success:
        return prepared, columns, mat, {"success": False, "lp_status": int(res.status), "lp_message": res.message}

    residual = b_ub - mat.dot(res.x)
    marginals = np.array(res.ineqlin.marginals, dtype=float)
    positive_cols = [i for i, x in enumerate(res.x) if x > args.x_tol]
    if args.core_limit and args.core_limit < len(positive_cols):
        positive_cols = positive_cols[: args.core_limit]
    dual_rows = [i for i, y in enumerate(marginals) if abs(y) > args.dual_tol]

    import scipy.linalg as la

    sub = mat[dual_rows, :][:, positive_cols].toarray()
    _q, rmat, piv = la.qr(sub.T, mode="economic", pivoting=True)
    diag = np.abs(np.diag(rmat))
    rank = int(np.sum(diag > args.qr_tol))
    selected_rows = [int(dual_rows[int(p)]) for p in piv[: len(positive_cols)]]
    meta = {
        "success": True,
        "lp_status": int(res.status),
        "objective": float(res.fun),
        "float_nonzero_original": int(sum(1 for x in res.x if x > args.x_tol)),
        "positive_cols": len(positive_cols),
        "candidate_dual_rows": len(dual_rows),
        "rank_estimate": rank,
        "core_limited": bool(args.core_limit and args.core_limit < int(sum(1 for x in res.x if x > args.x_tol))),
        "selected_rows_prefix": selected_rows[:20],
        "float_min_residual": float(residual.min()),
        "float_max_residual": float(residual.max()),
    }
    return prepared, columns, mat, meta | {"positive_col_indices": positive_cols, "selected_row_indices": selected_rows}


def extract_core(prepared, columns, positive_cols: list[int], selected_rows: list[int]):
    row_pos = {row: i for i, row in enumerate(selected_rows)}
    terms: list[tuple[int, int, Fraction]] = []
    nnz_by_col = [0] * len(positive_cols)
    for cpos, col_index in enumerate(positive_cols):
        for row, coeff in columns[col_index].terms:
            rpos = row_pos.get(row)
            if rpos is not None and coeff:
                terms.append((rpos, cpos, coeff))
                nnz_by_col[cpos] += 1
    rhs = [prepared.p_beta[row] for row in selected_rows]
    return terms, rhs, nnz_by_col


def verify_solution(prepared, columns, positive_cols: list[int], selected_rows: list[int], sol: list[Fraction], full: bool):
    core_res = [prepared.p_beta[row] for row in selected_rows]
    row_pos = {row: i for i, row in enumerate(selected_rows)}
    for val, col_index in zip(sol, positive_cols):
        if not val:
            continue
        for row, coeff in columns[col_index].terms:
            rpos = row_pos.get(row)
            if rpos is not None:
                core_res[rpos] -= coeff * val
    out: dict[str, object] = {
        "core_nonzero_residuals": sum(1 for x in core_res if x),
        "core_min_residual": fmt_fraction(min(core_res) if core_res else Fraction(0)),
        "solution_negative_count": sum(1 for x in sol if x < 0),
        "solution_min": fmt_fraction(min(sol) if sol else Fraction(0)),
        "solution_max": fmt_fraction(max(sol) if sol else Fraction(0)),
    }
    if not full:
        return out
    residual = prepared.p_beta[:]
    for val, col_index in zip(sol, positive_cols):
        if not val:
            continue
        for row, coeff in columns[col_index].terms:
            residual[row] -= coeff * val
    out.update(
        {
            "full_negative_residual_count": sum(1 for x in residual if x < 0),
            "full_min_residual": fmt_fraction(min(residual) if residual else Fraction(0)),
            "full_exact_ok": all(x >= 0 for x in residual) and all(x >= 0 for x in sol) and all(x == 0 for x in core_res),
        }
    )
    return out


def run(args):
    prepared, columns, _mat, meta = solve_float_and_select(args)
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_modular_replay_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "objective_mode": args.objective,
        "method": args.method,
        "lp": {k: v for k, v in meta.items() if k not in {"positive_col_indices", "selected_row_indices"}},
    }
    if not meta.get("success"):
        return out
    positive_cols = list(meta["positive_col_indices"])
    selected_rows = list(meta["selected_row_indices"])
    if meta["rank_estimate"] < len(positive_cols):
        out["abort"] = "qr_rank_below_core_dimension"
        return out

    terms, rhs, nnz_by_col = extract_core(prepared, columns, positive_cols, selected_rows)
    n = len(positive_cols)
    out["core"] = {
        "dimension": n,
        "terms": len(terms),
        "rhs_nonzero": sum(1 for x in rhs if x),
        "nnz_by_col_min": min(nnz_by_col) if nnz_by_col else 0,
        "nnz_by_col_max": max(nnz_by_col) if nnz_by_col else 0,
    }
    if args.export_core:
        args.export_core.parent.mkdir(parents=True, exist_ok=True)
        with args.export_core.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "meta", "dimension": n, "terms": len(terms)}) + "\n")
            for i, val in enumerate(rhs):
                f.write(json.dumps({"type": "rhs", "row": i, "value": fmt_fraction(val)}) + "\n")
            for i, j, coeff in terms:
                f.write(json.dumps({"type": "term", "row": i, "col": j, "value": fmt_fraction(coeff)}) + "\n")
        out["core"]["export_core"] = str(args.export_core)
    if args.export_only:
        return out

    residues: list[int] | None = None
    modulus = 1
    used_primes: list[int] = []
    skipped_primes: list[int] = []
    recon: list[Fraction] | None = None
    for p in prime_list(args.prime_count):
        sol_p = solve_mod_prime(n, terms, rhs, p)
        if sol_p is None:
            skipped_primes.append(p)
            continue
        if residues is None:
            residues = sol_p
            modulus = p
        else:
            residues = [crt_pair(a, modulus, b, p)[0] for a, b in zip(residues, sol_p)]
            modulus *= p
        used_primes.append(p)
        candidates = [rational_reconstruct(a, modulus) for a in residues]
        if all(x is not None for x in candidates):
            recon = [x for x in candidates if x is not None]
            check = verify_solution(prepared, columns, positive_cols, selected_rows, recon, full=(not args.core_limit))
            out["last_reconstruction_check"] = check
            if check.get("core_nonzero_residuals") == 0:
                break
            recon = None
    out["modular"] = {
        "used_primes": used_primes,
        "skipped_primes": skipped_primes,
        "modulus_bits": modulus.bit_length(),
        "reconstructed": recon is not None,
    }
    if recon is not None:
        out["exact_check"] = verify_solution(prepared, columns, positive_cols, selected_rows, recon, full=(not args.core_limit))
        if args.store_solution:
            out["solution"] = [fmt_fraction(x) for x in recon]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--method", default="highs")
    ap.add_argument("--objective", default="lex-small", choices=["sum", "lex-small", "lex-large", "family"])
    ap.add_argument("--time-limit", type=float, default=80.0)
    ap.add_argument("--x-tol", type=float, default=1e-9)
    ap.add_argument("--dual-tol", type=float, default=1e-9)
    ap.add_argument("--qr-tol", type=float, default=1e-9)
    ap.add_argument("--core-limit", type=int, default=0, help="0 means full positive column core")
    ap.add_argument("--prime-count", type=int, default=8)
    ap.add_argument("--export-core", type=Path)
    ap.add_argument("--export-only", action="store_true")
    ap.add_argument("--store-solution", action="store_true")
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_modular_replay_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "lp": out.get("lp"),
        "core": out.get("core"),
        "modular": out.get("modular"),
        "exact_check": out.get("exact_check"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()


