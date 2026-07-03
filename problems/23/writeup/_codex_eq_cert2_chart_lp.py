#!/usr/bin/env python3
"""Prototype CERT-2 charted Bernstein-Handelman LP.

This follows EQ_HEIGHT_LEMMA_GPTPRO.md ADDENDUM 3b.  The script is an
oracle/prototype, not a final certificate emitter:

* exact SymPy/Fraction dictionaries build the chart polynomial data;
* SciPy/HiGHS is used only to find a candidate LP solution;
* any accepted candidate must pass an exact rational residual check.

The chart compactification is

    x_chart = 0,  x_i = z_i / s,  s + sum z_i = 1,

and the target is P_hat = s^11 P_EQ(z/s).  Generators are homogenized to
their own degree, then multiplied by a total-degree Bernstein monomial of
degree 11 - deg(generator).  The free B0 term is represented implicitly by
requiring the residual degree-11 Bernstein/monomial coefficients to be
nonnegative.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_cert2_odl_lp as old_lp
from _codex_seed_qmax_constraints import constraint as qmax_constraint, value as qmax_value

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import EQ


TARGET_DEGREE = 11
SX_DIM = 10  # barycentric variables: s plus the nine non-chart z variables


@dataclass(frozen=True)
class Generator:
    name: str
    degree: int
    terms: dict[tuple[int, ...], Fraction]  # chart-homogeneous exponents in SX_DIM vars


@dataclass(frozen=True)
class Column:
    gen_index: int
    beta: tuple[int, ...]
    scale: int


def coeff_map(expr: sp.Expr) -> dict[tuple[int, ...], Fraction]:
    poly = sp.Poly(sp.expand(expr), *old_lp.xs, domain=sp.QQ)
    out: dict[tuple[int, ...], Fraction] = {}
    for exp, coeff in poly.terms():
        out[tuple(int(a) for a in exp)] = Fraction(int(coeff.p), int(coeff.q))
    return out


def total_degree(poly: dict[tuple[int, ...], Fraction]) -> int:
    return max((sum(exp) for exp, c in poly.items() if c), default=0)


def chart_homogenize(
    poly: dict[tuple[int, ...], Fraction],
    chart: int,
    formal_degree: int,
) -> dict[tuple[int, ...], Fraction]:
    """Substitute x_chart=0, x_i=z_i/s, multiply by s^formal_degree."""
    others = [i for i in range(10) if i != chart]
    out: dict[tuple[int, ...], Fraction] = {}
    for exp, coeff in poly.items():
        if not coeff or exp[chart] != 0:
            continue
        degree = sum(exp)
        s_pow = formal_degree - degree
        if s_pow < 0:
            raise ValueError((chart, formal_degree, exp))
        new_exp = [0] * SX_DIM
        new_exp[0] = s_pow
        for j, old_i in enumerate(others, start=1):
            new_exp[j] = exp[old_i]
        key = tuple(new_exp)
        out[key] = out.get(key, Fraction(0)) + coeff
    return {k: v for k, v in out.items() if v}


def multinomial(degree: int, exp: tuple[int, ...]) -> int:
    out = math.factorial(degree)
    for a in exp:
        out //= math.factorial(a)
    return out


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, parts - 1):
            yield (first, *rest)


def add_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def sub_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...] | None:
    out = tuple(x - y for x, y in zip(a, b))
    if min(out) < 0:
        return None
    return out


def g_exprs() -> list[tuple[str, sp.Expr]]:
    w = old_lp.ws
    m = old_lp.m
    n = old_lp.N
    eta25 = n * n - 25 * m
    u = w[0] + w[8]
    v = w[4] + w[6]
    x = w[1] + w[7]
    y = w[2] + w[9]
    z = w[3] + w[5]
    t = m + 1
    a = u + v + z
    b = x + y
    return [
        ("G1_UV_T", u * v - t),
        ("G2_UZ_T", u * z - t),
        ("G3_VZ_T", v * z - t),
        ("G4_XY_T", x * y - t),
        ("G5_VZ_XY", v * z - x * y),
        ("G6_A2_9T", a * a - 9 * t),
        ("G7_B2_4T", b * b - 4 * t),
        ("G8_eta25_25", eta25 - 25),
    ]



def maxcut_facet_exprs(mode: str, selected_masks=()) -> list[tuple[str, sp.Expr]]:
    if mode == "none":
        return []
    if mode not in {"tight", "all", "selected"}:
        raise ValueError(f"unknown maxcut facet mode {mode!r}")
    selected_masks = {int(m) for m in selected_masks}
    side = tuple(int(c) for c in old_lp.SIDE)
    ones = (1,) * 10
    out: list[tuple[str, sp.Expr]] = []
    seen = set()
    for mask in range(1, (1 << 10) - 1):
        if not (mask & 1):
            continue
        c = qmax_constraint(EQ, side, mask)
        if c is None:
            continue
        if mode == "tight" and qmax_value(c, ones) != 0:
            continue
        if mode == "selected" and mask not in selected_masks:
            continue
        key = tuple(sorted(c.items()))
        if key in seen:
            continue
        seen.add(key)
        expr = sp.Integer(0)
        for (a, b), sign in c.items():
            expr += sign * old_lp.ws[a] * old_lp.ws[b]
        out.append((f"QMAX_{mask}", sp.expand(expr)))
    return out

def build_chart(chart: int, extra_maxcut: str = "none", maxcut_masks=()) -> tuple[dict[tuple[int, ...], Fraction], list[Generator], dict[str, object]]:
    target, target_meta = old_lp.build_target()
    target_map = coeff_map(target)
    target_hat = chart_homogenize(target_map, chart, TARGET_DEGREE)

    raw_generators: list[tuple[str, sp.Expr]] = []
    raw_generators.extend((f"F{i}", f) for i, f in enumerate(old_lp.F, start=1))
    raw_generators.extend(g_exprs())
    raw_generators.extend(maxcut_facet_exprs(extra_maxcut, maxcut_masks))

    generators: list[Generator] = []
    for name, expr in raw_generators:
        cmap = coeff_map(expr)
        deg = total_degree(cmap)
        if deg > TARGET_DEGREE:
            raise ValueError((name, deg))
        terms = chart_homogenize(cmap, chart, deg)
        generators.append(Generator(name=name, degree=deg, terms=terms))

    meta = {
        "graph": target_meta.get("graph", EQ),
        "side": target_meta.get("side", old_lp.SIDE),
        "active_row": target_meta.get("active_row", list(old_lp.ACTIVE_ROW)),
        "bad_edges": target_meta.get("bad_edges", []),
        "chart": chart,
        "extra_maxcut": extra_maxcut,
        "maxcut_masks": [int(m) for m in maxcut_masks],
        "target_terms_chart": len(target_hat),
        "target_degree": TARGET_DEGREE,
        "generators": [
            {"name": g.name, "degree": g.degree, "terms": len(g.terms)}
            for g in generators
        ],
    }
    return target_hat, generators, meta


def repair_columns(
    target_hat: dict[tuple[int, ...], Fraction],
    generators: list[Generator],
    mode: str,
    max_columns_per_generator: int | None,
) -> list[Column]:
    if mode == "all":
        columns = [
            Column(gi, beta, multinomial(TARGET_DEGREE - gen.degree, beta))
            for gi, gen in enumerate(generators)
            for beta in weak_compositions(TARGET_DEGREE - gen.degree, SX_DIM)
        ]
    elif mode == "repair":
        negative_target = [exp for exp, coeff in target_hat.items() if coeff < 0]
        seen: set[tuple[int, tuple[int, ...]]] = set()
        columns = []
        for gi, gen in enumerate(generators):
            beta_degree = TARGET_DEGREE - gen.degree
            gen_negative = [exp for exp, coeff in gen.terms.items() if coeff < 0]
            for target_exp in negative_target:
                for gen_exp in gen_negative:
                    beta = sub_exp(target_exp, gen_exp)
                    if beta is None or sum(beta) != beta_degree:
                        continue
                    key = (gi, beta)
                    if key in seen:
                        continue
                    seen.add(key)
                    columns.append(Column(gi, beta, multinomial(beta_degree, beta)))
                    if max_columns_per_generator is not None:
                        count_g = sum(1 for c in columns if c.gen_index == gi)
                        if count_g >= max_columns_per_generator:
                            break
                if max_columns_per_generator is not None:
                    count_g = sum(1 for c in columns if c.gen_index == gi)
                    if count_g >= max_columns_per_generator:
                        break
    else:
        raise ValueError(f"unknown support mode {mode!r}")
    return columns


def column_terms(col: Column, gen: Generator) -> dict[tuple[int, ...], Fraction]:
    out: dict[tuple[int, ...], Fraction] = {}
    scale = Fraction(col.scale)
    for exp, coeff in gen.terms.items():
        key = add_exp(exp, col.beta)
        out[key] = out.get(key, Fraction(0)) + scale * coeff
    return {k: v for k, v in out.items() if v}


def solve_chart(
    chart: int,
    support: str,
    extra_maxcut: str,
    maxcut_masks: list[int],
    max_columns_per_generator: int | None,
    max_denominators: list[int],
    objective: str,
    time_limit: float | None,
    method: str,
) -> dict[str, object]:
    target_hat, generators, meta = build_chart(chart, extra_maxcut=extra_maxcut, maxcut_masks=maxcut_masks)
    columns = repair_columns(target_hat, generators, support, max_columns_per_generator)
    term_maps = [column_terms(col, generators[col.gen_index]) for col in columns]
    monomials = sorted(set(target_hat) | set().union(*(set(mp) for mp in term_maps)))
    row_index = {mon: i for i, mon in enumerate(monomials)}

    row_scale = [max(1.0, abs(float(target_hat.get(mon, Fraction(0))))) for mon in monomials]
    entries: list[tuple[int, int, float]] = []
    for j, mp in enumerate(term_maps):
        for mon, coeff in mp.items():
            i = row_index[mon]
            value = float(coeff)
            row_scale[i] = max(row_scale[i], abs(value))
            entries.append((i, j, value))
    rows = [i for i, _j, _v in entries]
    cols = [j for _i, j, _v in entries]
    data = [v / row_scale[i] for i, _j, v in entries]
    matrix = coo_matrix((data, (rows, cols)), shape=(len(monomials), len(columns))).tocsr()
    b_ub = [float(target_hat.get(mon, Fraction(0))) / row_scale[i] for i, mon in enumerate(monomials)]
    c = [0.0 if objective == "zero" else 1.0] * len(columns)

    result: dict[str, object] = {
        "schema": "eq_cert2_chart_bernstein_lp_v1",
        "mode": "P_hat_minus_sum_G_B_has_nonnegative_B0_coefficients",
        "support": support,
        "method": method,
        "chart": chart,
        "columns": len(columns),
        "constraints": len(monomials),
        "nonzeros": len(data),
        "meta": meta,
    }
    print(
        "chart",
        chart,
        "support",
        support,
        "columns",
        len(columns),
        "constraints",
        len(monomials),
        "nonzeros",
        len(data),
        flush=True,
    )
    if not columns:
        result["success"] = False
        result["lp_message"] = "no columns"
        return result

    options = {}
    if time_limit is not None and time_limit > 0:
        options["time_limit"] = time_limit
    res = linprog(
        c=c,
        A_ub=matrix,
        b_ub=b_ub,
        bounds=[(0, None)] * len(columns),
        method=method,
        options=options,
    )
    result.update(
        {
            "lp_status": int(res.status),
            "lp_message": res.message,
            "success": bool(res.success),
        }
    )
    print("LP", res.status, res.message, flush=True)
    if not res.success:
        return result

    result["float_nonzero"] = int(sum(1 for x in res.x if x > 1e-9))
    result["float_objective"] = str(res.fun)
    for max_den in max_denominators:
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in res.x]
        ok, check = exact_residual_check(target_hat, generators, columns, coeffs)
        print(
            "try",
            max_den,
            "ok",
            ok,
            "min",
            check["residual_min_coeff"],
            "neg",
            len(check["negative_terms"]),
            "seed",
            check["seed_residual"],
            flush=True,
        )
        if ok:
            nz = [
                {
                    "generator": generators[col.gen_index].name,
                    "beta": list(col.beta),
                    "bernstein_scale": col.scale,
                    "coeff": str(coeff),
                }
                for col, coeff in zip(columns, coeffs)
                if coeff
            ]
            result.update(
                {
                    "exact_ok": True,
                    "max_denominator": max_den,
                    **check,
                    "nonzero_terms": nz,
                }
            )
            return result
    result["exact_ok"] = False
    result["last_exact_check"] = check
    return result


def exact_residual_check(
    target_hat: dict[tuple[int, ...], Fraction],
    generators: list[Generator],
    columns: list[Column],
    coeffs: list[Fraction],
) -> tuple[bool, dict[str, object]]:
    residual = dict(target_hat)
    for col, coeff in zip(columns, coeffs):
        if not coeff:
            continue
        gen = generators[col.gen_index]
        for exp, term_coeff in column_terms(col, gen).items():
            residual[exp] = residual.get(exp, Fraction(0)) - coeff * term_coeff
            if residual[exp] == 0:
                del residual[exp]
    all_coeffs = list(residual.values())
    neg = []
    for mon, coeff in sorted(residual.items()):
        if coeff < 0:
            neg.append({"monomial": list(mon), "coeff": str(coeff)})
            if len(neg) >= 20:
                break
    seed = (TARGET_DEGREE,) + (0,) * (SX_DIM - 1)
    seed_residual = residual.get(seed, Fraction(0))
    ok = not neg and seed_residual == 0
    return ok, {
        "residual_terms": len(residual),
        "residual_min_coeff": str(min(all_coeffs) if all_coeffs else Fraction(0)),
        "negative_terms": neg,
        "seed_residual": str(seed_residual),
    }


def parse_ints(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--support", choices=["repair", "all"], default="repair")
    ap.add_argument("--extra-maxcut", choices=["none", "tight", "all", "selected"], default="none")
    ap.add_argument("--maxcut-masks", default="")
    ap.add_argument("--max-columns-per-generator", type=int, default=0)
    ap.add_argument("--max-den", default="10,25,50,100,250,1000,5000,20000")
    ap.add_argument("--objective", choices=["zero", "sum"], default="sum")
    ap.add_argument("--time-limit", type=float, default=0.0, help="HiGHS time limit in seconds; 0 means unlimited")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--summary", default="tmp/eq_cert2_chart_lp_v1.json")
    args = ap.parse_args()

    limit = args.max_columns_per_generator or None
    out = solve_chart(
        chart=args.chart,
        support=args.support,
        extra_maxcut=args.extra_maxcut,
        maxcut_masks=parse_ints(args.maxcut_masks) if args.maxcut_masks else [],
        max_columns_per_generator=limit,
        max_denominators=parse_ints(args.max_den),
        objective=args.objective,
        time_limit=args.time_limit or None,
        method=args.method,
    )
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    if out.get("exact_ok"):
        print("PASS exact ChartCert LP", args.summary)
    elif out.get("success"):
        print("LP_FEASIBLE_BUT_NOT_EXACT", args.summary)
    else:
        print("NO_CERT", args.summary)
        raise SystemExit(1)


if __name__ == "__main__":
    main()




