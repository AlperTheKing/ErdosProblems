#!/usr/bin/env python3
"""Rung-1 shifted-cone LP search for EQ-ODL1.

Target:
    P_EQ1 = D_EQ * (eta25 - 25 * (I_EQ - N)) >= 0.

Search cone:
    P_EQ1 = P0 + sum F_j P_j + sum G_l P_l,
where P0 and all multipliers have nonnegative shifted coefficients in
w_i = 1 + x_i.  SciPy/HiGHS is only a search oracle.  A result is accepted
only if rationalized coefficients pass an exact SymPy residual check.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_cert2_odl_lp as old_lp

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import EQ, b_edges, edges_of, m_edges, shortest_paths


xs = old_lp.xs
ws = old_lp.ws
TARGET_DEGREE = 11


@dataclass(frozen=True)
class Generator:
    name: str
    expr: sp.Expr
    degree: int
    cap: int


@dataclass(frozen=True)
class Column:
    gen_index: int
    exp: tuple[int, ...]


def coeff_map(expr: sp.Expr) -> dict[tuple[int, ...], Fraction]:
    poly = sp.Poly(sp.expand(expr), *xs, domain=sp.QQ)
    return {tuple(int(a) for a in monom): Fraction(int(coeff.p), int(coeff.q)) for monom, coeff in poly.terms()}


def total_degree_from_map(cmap: dict[tuple[int, ...], Fraction]) -> int:
    return max((sum(exp) for exp, coeff in cmap.items() if coeff), default=0)


def monomial_from_exp(exp: tuple[int, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for x, power in zip(xs, exp):
        if power:
            out *= x ** power
    return out


def all_monomial_exps(max_degree: int) -> list[tuple[int, ...]]:
    out = [(0,) * len(xs)]
    for degree in range(1, max_degree + 1):
        for combo in combinations_with_replacement(range(len(xs)), degree):
            exp = [0] * len(xs)
            for i in combo:
                exp[i] += 1
            out.append(tuple(exp))
    return out


def add_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def sub_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...] | None:
    out = tuple(x - y for x, y in zip(a, b))
    return None if min(out) < 0 else out


def path_weight(path: tuple[int, ...], weights: tuple[sp.Expr, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for v in path[1:-1]:
        out *= weights[v]
    return out


def row_overlap_expr(row: tuple[int, ...], weights: tuple[sp.Expr, ...], paths_by_bad) -> sp.Expr:
    row_set = set(row)
    total = sp.Integer(0)
    for a, b in sorted(paths_by_bad):
        paths = paths_by_bad[(a, b)]
        denom = sp.Integer(0)
        inner = sp.Integer(0)
        for path in paths:
            wp = path_weight(path, weights)
            denom += wp
            for v in path[1:-1]:
                if v in row_set:
                    inner += wp / weights[v]
        endpoint = sp.Integer(0)
        if a in row_set:
            endpoint += weights[b]
        if b in row_set:
            endpoint += weights[a]
        total += endpoint + weights[a] * weights[b] * inner / denom
    return sp.factor(total)


def build_target() -> tuple[sp.Expr, dict[str, object]]:
    n, edges = edges_of(EQ)
    side = tuple(int(c) for c in old_lp.SIDE)
    bset = b_edges(edges, side)
    bad = sorted(m_edges(edges, side))
    if n != 10 or bad != [(1, 9), (2, 7), (7, 9)]:
        raise RuntimeError(f"unexpected EQ data: n={n} bad={bad}")
    paths_by_bad = {edge: shortest_paths(n, bset, edge[0], edge[1]) for edge in bad}
    i_eq = row_overlap_expr(old_lp.ACTIVE_ROW, ws, paths_by_bad)
    d_eq = old_lp.eq_denominator(ws)
    expr = sp.together(d_eq * (old_lp.eta25 - 25 * (i_eq - old_lp.N)))
    num, den = expr.as_numer_denom()
    if sp.factor(den) != 1:
        raise RuntimeError(f"D_EQ did not clear denominator: {sp.factor(den)}")
    return sp.expand(num), {
        "graph": EQ,
        "side": old_lp.SIDE,
        "active_row": list(old_lp.ACTIVE_ROW),
        "bad_edges": [list(e) for e in bad],
        "D_EQ": str(d_eq),
        "I_EQ": str(i_eq),
        "target": "D_EQ*(eta25 - 25*(I_EQ - N))",
    }


def cert1_generators() -> list[tuple[str, sp.Expr]]:
    w = ws
    m = old_lp.m
    eta25 = old_lp.eta25
    u = w[0] + w[8]
    v = w[4] + w[6]
    x = w[1] + w[7]
    y = w[2] + w[9]
    z = w[3] + w[5]
    t = m + 1
    a = u + v + z
    b = x + y
    return [
        ("B0_eta25_25", eta25 - 25),
        ("G1_UV_T", u * v - t),
        ("G2_UZ_T", u * z - t),
        ("G3_XY_T", x * y - t),
        ("G4_VZ_XY", v * z - x * y),
        ("G5_VZ_T", v * z - t),
        ("G6_A2_9T", a * a - 9 * t),
        ("G7_B2_4T", b * b - 4 * t),
    ]


def build_generators() -> list[Generator]:
    raw: list[tuple[str, sp.Expr, int]] = []
    for i, f in enumerate(old_lp.F, start=1):
        deg = 1 if i <= 4 else 2
        cap = 10 if deg == 1 else 9
        raw.append((f"F{i}", f, cap))
    for name, expr in cert1_generators():
        raw.append((name, expr, 9))
    out = []
    for name, expr, cap in raw:
        cmap = coeff_map(expr)
        out.append(Generator(name=name, expr=sp.expand(expr), degree=total_degree_from_map(cmap), cap=cap))
    return out


def candidate_columns(target: dict[tuple[int, ...], Fraction], generators: list[Generator], support: str) -> list[Column]:
    if support == "all":
        return [Column(gi, exp) for gi, gen in enumerate(generators) for exp in all_monomial_exps(gen.cap)]
    if support != "negative":
        raise ValueError(f"unknown support {support!r}")
    neg_target = [exp for exp, coeff in target.items() if coeff < 0]
    cols = []
    seen = set()
    for gi, gen in enumerate(generators):
        gmap = coeff_map(gen.expr)
        neg_gen = [exp for exp, coeff in gmap.items() if coeff < 0]
        for beta in neg_target:
            for alpha in neg_gen:
                gamma = sub_exp(beta, alpha)
                if gamma is None or sum(gamma) > gen.cap:
                    continue
                key = (gi, gamma)
                if key not in seen:
                    seen.add(key)
                    cols.append(Column(gi, gamma))
    return cols


def column_map(col: Column, generators: list[Generator]) -> dict[tuple[int, ...], Fraction]:
    gen = generators[col.gen_index]
    mon = monomial_from_exp(col.exp)
    return coeff_map(gen.expr * mon)


def solve_lp(target_expr: sp.Expr, support: str, max_denominators: list[int], objective: str, time_limit: float | None) -> dict[str, object]:
    target = coeff_map(target_expr)
    generators = build_generators()
    cols = candidate_columns(target, generators, support)
    col_maps = [column_map(col, generators) for col in cols]
    monoms = sorted(set(target) | set().union(*(set(m) for m in col_maps))) if col_maps else sorted(target)
    row_index = {m: i for i, m in enumerate(monoms)}
    data = []
    rows = []
    col_ids = []
    for j, cmap in enumerate(col_maps):
        for exp, coeff in cmap.items():
            rows.append(row_index[exp])
            col_ids.append(j)
            data.append(float(coeff))
    mat = coo_matrix((data, (rows, col_ids)), shape=(len(monoms), len(cols))).tocsr()
    b_ub = [float(target.get(exp, Fraction(0))) for exp in monoms]
    c = [0.0 if objective == "zero" else 1.0] * len(cols)
    print("support", support, "vars", len(cols), "constraints", len(monoms), flush=True)
    options = {} if time_limit is None else {"time_limit": float(time_limit)}
    res = linprog(c=c, A_ub=mat, b_ub=b_ub, bounds=[(0, None)] * len(cols), method="highs", options=options)
    out = {
        "schema": "eq_odl1_shifted_lp_v1",
        "support": support,
        "variables": len(cols),
        "constraints": len(monoms),
        "generators": [{"name": g.name, "degree": g.degree, "cap": g.cap} for g in generators],
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
    }
    print("LP", res.status, res.message, flush=True)
    if not res.success:
        return out
    raw = res.x
    out["float_nonzero"] = int(sum(1 for x in raw if x > 1e-9))
    for max_den in max_denominators:
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in raw]
        ok, check = exact_check(target_expr, generators, cols, coeffs)
        print("try", max_den, "ok", ok, "min", check["residual_min_coeff"], "neg", check["negative_terms"][:1], flush=True)
        if ok:
            out.update({"exact_ok": True, "max_denominator": max_den, "exact_check": check})
            return out
    ok, check = exact_check(target_expr, generators, cols, [Fraction(str(x)) for x in raw])
    out.update({"exact_ok": ok, "exact_check": check})
    return out


def exact_check(target_expr: sp.Expr, generators: list[Generator], cols: list[Column], coeffs: list[Fraction]) -> tuple[bool, dict[str, object]]:
    expr = target_expr
    nz = []
    for col, coeff in zip(cols, coeffs):
        if not coeff:
            continue
        gen = generators[col.gen_index]
        nz.append({"generator": gen.name, "monomial": str(monomial_from_exp(col.exp)), "coeff": str(coeff)})
        expr -= sp.Rational(coeff.numerator, coeff.denominator) * gen.expr * monomial_from_exp(col.exp)
    poly = sp.Poly(sp.expand(expr), *xs, domain=sp.QQ)
    neg = []
    vals = []
    for exp, coeff in poly.terms():
        q = Fraction(int(coeff.p), int(coeff.q))
        vals.append(q)
        if q < 0 and len(neg) < 20:
            neg.append({"monomial": exp, "coeff": str(q)})
    return not neg, {
        "residual_terms": len(vals),
        "residual_min_coeff": str(min(vals) if vals else Fraction(0)),
        "negative_terms": neg,
        "nonzero_multipliers": nz[:5000],
        "nonzero_multiplier_count": len(nz),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--objective", choices=["zero", "sum"], default="sum")
    ap.add_argument("--max-den", default="1000,1000000")
    ap.add_argument("--time-limit", type=float, default=0.0, help="HiGHS time limit in seconds; 0 means no limit")
    ap.add_argument("--summary", default="tmp/eq_odl1_shifted_lp_v1.json")
    args = ap.parse_args()
    target, meta = build_target()
    max_denominators = [int(x) for x in args.max_den.split(",") if x]
    time_limit = None if args.time_limit <= 0 else args.time_limit
    result = solve_lp(target, args.support, max_denominators, args.objective, time_limit)
    result["target_meta"] = meta
    result["target_terms"] = len(coeff_map(target))
    result["target_negative_terms"] = sum(1 for c in coeff_map(target).values() if c < 0)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in ["success", "exact_ok", "lp_status", "variables", "constraints", "target_terms", "target_negative_terms"]}, sort_keys=True))


if __name__ == "__main__":
    main()

