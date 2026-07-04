#!/usr/bin/env python3
"""EQ-ODL1 Rung-2 chart builder and Bernstein triviality sweep.

Implements the first Rung-2 gate from EQ_HEIGHT_LEMMA_GPTPRO.md:
  * ten height charts w_k = 1, w_i = 1 + x_i >= 1;
  * compactification S = 1 + sum x_i, s = 1/S, z_i = x_i/S;
  * chart target P_k = s^11 P_EQ1^(k)(z/s);
  * dominance chart labels (k, generator, band), 10 x 15 x 2 = 300;
  * triviality test: Bernstein coefficients of P_k alone on the simplex.

The chart polynomial P_k alone does not depend on the dominance generator or band;
this script still emits per-chart rows so later passes can attach band-only and full
LP certificates to the same 300 labels.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

import sympy as sp

import _codex_eq_odl1_shifted_lp as eq

TARGET_DEGREE = 11


@dataclass(frozen=True)
class ChartData:
    k: int
    variables: tuple[sp.Symbol, ...]
    target: sp.Expr
    generators: tuple[sp.Expr, ...]
    generator_names: tuple[str, ...]
    s: sp.Symbol
    z: tuple[sp.Symbol, ...]


def all_exps(num_vars: int, total_degree: int) -> list[tuple[int, ...]]:
    out = []
    for combo in combinations_with_replacement(range(num_vars), total_degree):
        exp = [0] * num_vars
        for i in combo:
            exp[i] += 1
        out.append(tuple(exp))
    return out


def exps_upto(num_vars: int, max_degree: int) -> list[tuple[int, ...]]:
    out = []
    for degree in range(max_degree + 1):
        out.extend(all_exps(num_vars, degree))
    return out


def monomial(vars_: tuple[sp.Symbol, ...], exp: tuple[int, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for var, power in zip(vars_, exp):
        if power:
            out *= var ** power
    return out


def coeff_fraction(poly: sp.Poly, exp: tuple[int, ...]) -> Fraction:
    coeff = poly.coeff_monomial(monomial(tuple(poly.gens), exp))
    return Fraction(int(coeff.p), int(coeff.q))


def fmt_fraction(q: Fraction) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def cert1_raw_generators() -> list[tuple[str, sp.Expr]]:
    return eq.cert1_generators()


def all_raw_generators() -> list[tuple[str, sp.Expr]]:
    out = [(f"F{i}", f) for i, f in enumerate(eq.old_lp.F, start=1)]
    out.extend(cert1_raw_generators())
    if len(out) != 15:
        raise RuntimeError(f"expected 15 generators, got {len(out)}")
    return out


def homogenize_expr(expr: sp.Expr, degree: int, sub_x: dict[sp.Symbol, sp.Expr], s: sp.Symbol) -> sp.Expr:
    return sp.Poly(sp.together((s ** degree) * expr.subs(sub_x)).as_numer_denom()[0], *sorted(set([s]) | {v for v in []}, key=str)).as_expr()


def build_chart(k: int) -> ChartData:
    target, _meta = eq.build_target()
    raw_generators = all_raw_generators()
    s = sp.symbols("s")
    z = sp.symbols("z0:10")
    active_z = tuple(z[i] for i in range(10) if i != k)
    chart_vars = (s,) + active_z

    sub_x: dict[sp.Symbol, sp.Expr] = {}
    for i, x in enumerate(eq.xs):
        if i == k:
            sub_x[x] = sp.Integer(0)
        else:
            sub_x[x] = z[i] / s

    target_expr = sp.together((s ** TARGET_DEGREE) * target.subs(sub_x)).as_numer_denom()[0]
    target_poly = sp.Poly(sp.expand(target_expr), *chart_vars, domain=sp.QQ).as_expr()

    gen_exprs = []
    names = []
    for name, expr in raw_generators:
        deg = eq.total_degree_from_map(eq.coeff_map(expr))
        g_expr = sp.together((s ** deg) * expr.subs(sub_x)).as_numer_denom()[0]
        gen_exprs.append(sp.Poly(sp.expand(g_expr), *chart_vars, domain=sp.QQ).as_expr())
        names.append(name)
    return ChartData(k=k, variables=chart_vars, target=target_poly, generators=tuple(gen_exprs), generator_names=tuple(names), s=s, z=active_z)


def ordinary_coeff_stats(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> dict[str, object]:
    poly = sp.Poly(sp.expand(expr), *vars_, domain=sp.QQ)
    coeffs = [Fraction(int(c.p), int(c.q)) for c in poly.coeffs()]
    neg = sum(1 for c in coeffs if c < 0)
    return {
        "terms": len(coeffs),
        "ordinary_min_coeff": fmt_fraction(min(coeffs) if coeffs else Fraction(0)),
        "ordinary_negative_coeffs": neg,
        "total_degree": poly.total_degree(),
    }


def multinomial(total: int, exp: tuple[int, ...]) -> int:
    out = math.factorial(total)
    for e in exp:
        out //= math.factorial(e)
    return out


def bernstein_degree_coefficients(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], degree: int) -> dict[tuple[int, ...], Fraction]:
    """Return degree-d Bernstein coefficients on the simplex sum(vars)=1.

    Sparse forward expansion:
      x^alpha = x^alpha (sum x)^(d-|alpha|)
              = sum_gamma multinomial(d-|alpha|, gamma) x^(alpha+gamma),
    then divide by the Bernstein basis multinomial(d, beta) x^beta.
    """
    poly = sp.Poly(sp.expand(expr), *vars_, domain=sp.QQ)
    num_vars = len(vars_)
    exps_by_degree = {r: all_exps(num_vars, r) for r in range(degree + 1)}
    multinomial_degree = {
        r: {exp: multinomial(r, exp) for exp in exps_by_degree[r]}
        for r in range(degree + 1)
    }
    out = {beta: Fraction(0) for beta in exps_by_degree[degree]}
    for alpha_raw, coeff_raw in poly.terms():
        alpha = tuple(int(a) for a in alpha_raw)
        alpha_degree = sum(alpha)
        if alpha_degree > degree:
            raise ValueError(f"monomial degree {alpha_degree} exceeds Bernstein degree {degree}: {alpha}")
        coeff = Fraction(int(coeff_raw.p), int(coeff_raw.q))
        rem = degree - alpha_degree
        for gamma in exps_by_degree[rem]:
            beta = tuple(a + g for a, g in zip(alpha, gamma))
            out[beta] += coeff * Fraction(multinomial_degree[rem][gamma], multinomial_degree[degree][beta])
    return out


def chart_row(chart: ChartData, gen_index: int, band: str, bernstein_cache: dict[int, dict[str, object]]) -> dict[str, object]:
    if chart.k not in bernstein_cache:
        stats = ordinary_coeff_stats(chart.target, chart.variables)
        bcoeff = bernstein_degree_coefficients(chart.target, chart.variables, TARGET_DEGREE)
        vals = list(bcoeff.values())
        stats.update({
            "bernstein_degree": TARGET_DEGREE,
            "bernstein_coeffs": len(vals),
            "bernstein_min_coeff": fmt_fraction(min(vals) if vals else Fraction(0)),
            "bernstein_negative_coeffs": sum(1 for v in vals if v < 0),
            "trivial_closed": all(v >= 0 for v in vals),
        })
        bernstein_cache[chart.k] = stats
    stats = bernstein_cache[chart.k]
    return {
        "k": chart.k,
        "dominant_generator": chart.generator_names[gen_index],
        "dominant_generator_index": gen_index,
        "band": band,
        **stats,
    }


def run() -> dict[str, object]:
    rows = []
    per_chart = {}
    for k in range(10):
        print(f"height chart {k}: build", flush=True)
        chart = build_chart(k)
        print(f"height chart {k}: bernstein", flush=True)
        cache: dict[int, dict[str, object]] = {}
        for gen_index in range(len(chart.generator_names)):
            for band in ("near_2s_minus_1", "inf_1_minus_2s"):
                rows.append(chart_row(chart, gen_index, band, cache))
        per_chart[str(k)] = cache[k]
    trivial = sum(1 for row in rows if row["trivial_closed"])
    return {
        "schema": "eq_odl1_rung2_chart_triviality_v1",
        "target": "P_EQ1 = D_EQ*(eta25 - 25*(I_EQ - N))",
        "charts": 10,
        "generators": 15,
        "bands": ["near_2s_minus_1", "inf_1_minus_2s"],
        "chart_rows": len(rows),
        "trivial_closed_rows": trivial,
        "nontrivial_rows": len(rows) - trivial,
        "trivial_closed_height_charts": [int(k) for k, stats in per_chart.items() if stats["trivial_closed"]],
        "per_height_chart": per_chart,
        "rows": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_chart_triviality_v1.json"))
    args = ap.parse_args()
    out = run()
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "chart_rows": out["chart_rows"],
        "trivial_closed_rows": out["trivial_closed_rows"],
        "trivial_closed_height_charts": out["trivial_closed_height_charts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

