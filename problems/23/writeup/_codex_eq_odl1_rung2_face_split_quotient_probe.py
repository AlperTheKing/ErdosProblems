#!/usr/bin/env python3
"""Quotient-coupled face-split LP probe for EQ-ODL1 Rung-2.

This implements the search-side formulation from
FACE_SPLIT_QUOTIENT_LP_GPTPRO.md.  It is deliberately a probe: a float LP
solution is only a candidate until exact replay succeeds and the expanded
ordinary ConeCert is emitted by a later materializer.

For a dominant generator g = G_a#, divide every face column F_j exactly:

    F_j = rem(F_j) + g * quo(F_j)

and solve the coupled nonnegative system

    sum_j alpha_j rem(F_j) = rem(P)
    sum_j alpha_j quo(F_j) + sum_k beta_k M_k = quo(P).

The row space is ordinary monomial coefficients in the quotient/remainder
coordinates, not the full degree-11 Bernstein row set.
"""

from __future__ import annotations

import argparse
import heapq
import json
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_band_lp as band_lp
import _codex_eq_odl1_rung2_charts as charts


TARGET_DEGREE = charts.TARGET_DEGREE
GEN_DEGREE = 2

Exp = tuple[int, ...]
Poly = dict[Exp, Fraction]
DERIVED_SUPPORT_TERM_LIMIT: int | None = None


@dataclass(frozen=True)
class QColumn:
    side: str
    kind: str
    name: str
    multiplier_exp: Exp
    rem: tuple[tuple[Exp, Fraction], ...]
    quo: tuple[tuple[Exp, Fraction], ...]


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 512 and q.denominator.bit_length() < 512:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def clean(poly: Poly) -> Poly:
    return {exp: coeff for exp, coeff in poly.items() if coeff}


def exp_add(a: Exp, b: Exp) -> Exp:
    return tuple(x + y for x, y in zip(a, b))


def exp_sub(a: Exp, b: Exp) -> Exp:
    return tuple(x - y for x, y in zip(a, b))


def exp_divides(a: Exp, b: Exp) -> bool:
    return all(x >= y for x, y in zip(a, b))


def grevlex_key(exp: Exp) -> tuple[int, tuple[int, ...]]:
    # Graded reverse lexicographic order, variables in chart order.
    return (sum(exp), tuple(-x for x in reversed(exp)))


def leading_term(poly: Poly) -> tuple[Exp, Fraction]:
    exp = max(poly, key=grevlex_key)
    return exp, poly[exp]


def heap_key(exp: Exp) -> tuple[int, tuple[int, ...]]:
    # Min-heap key whose first item is the grevlex-leading monomial.
    return (-sum(exp), tuple(reversed(exp)))


def add_poly(a: Poly, b: Poly) -> Poly:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) + coeff
        if not out[exp]:
            del out[exp]
    return out


def sub_poly(a: Poly, b: Poly) -> Poly:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) - coeff
        if not out[exp]:
            del out[exp]
    return out


def mul_poly(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            exp = exp_add(ea, eb)
            out[exp] = out.get(exp, Fraction(0)) + ca * cb
    return clean(out)


def scale_poly(poly: Poly, scale: Fraction) -> Poly:
    if not scale:
        return {}
    return clean({exp: coeff * scale for exp, coeff in poly.items()})


def monomial_poly(exp: Exp, coeff: Fraction = Fraction(1)) -> Poly:
    return {} if coeff == 0 else {exp: coeff}


def subtract_shifted(work: Poly, heap: list[tuple[tuple[int, tuple[int, ...]], Exp]], divisor: Poly, shift: Exp, scale: Fraction) -> None:
    for exp, coeff in divisor.items():
        out_exp = exp_add(exp, shift)
        existed = out_exp in work
        new_coeff = work.get(out_exp, Fraction(0)) - scale * coeff
        if new_coeff:
            work[out_exp] = new_coeff
            if not existed:
                heapq.heappush(heap, (heap_key(out_exp), out_exp))
        elif out_exp in work:
            del work[out_exp]


def divide_grevlex(target: Poly, divisor: Poly) -> tuple[Poly, Poly]:
    if not divisor:
        raise ValueError("empty divisor")
    lead_exp, lead_coeff = leading_term(divisor)
    work = dict(target)
    heap = [(heap_key(exp), exp) for exp in work]
    heapq.heapify(heap)
    quotient: Poly = {}
    remainder: Poly = {}
    while heap:
        _key, exp = heapq.heappop(heap)
        coeff = work.get(exp)
        if coeff is None:
            continue
        if exp_divides(exp, lead_exp):
            shift = exp_sub(exp, lead_exp)
            scale = coeff / lead_coeff
            quotient[shift] = quotient.get(shift, Fraction(0)) + scale
            subtract_shifted(work, heap, divisor, shift, scale)
        else:
            del work[exp]
            remainder[exp] = remainder.get(exp, Fraction(0)) + coeff
    return clean(quotient), clean(remainder)


def poly_from_expr(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> Poly:
    poly = sp.Poly(sp.expand(expr), *vars_, domain=sp.QQ)
    out: Poly = {}
    for exp_raw, coeff_raw in poly.terms():
        q = sp.Rational(coeff_raw)
        coeff = Fraction(int(q.p), int(q.q))
        if coeff:
            out[tuple(int(x) for x in exp_raw)] = coeff
    return out


def total_degree(poly: Poly) -> int:
    return max((sum(exp) for exp in poly), default=0)


def homogenize_poly(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], degree: int) -> Poly:
    poly = sp.Poly(sp.expand(expr), *vars_, domain=sp.QQ)
    deg = poly.total_degree()
    if deg > degree:
        raise ValueError(f"polynomial degree {deg} exceeds requested homogeneous degree {degree}")
    sigma = sum(vars_)
    return poly_from_expr(sp.expand(poly.as_expr() * sigma ** (degree - deg)), vars_)


def bernstein_basis_poly(degree: int, exp: Exp) -> Poly:
    return {exp: Fraction(charts.multinomial(degree, exp))}


def band_poly(num_vars: int, band: str) -> Poly:
    out: Poly = {}
    zero = tuple(0 for _ in range(num_vars))
    for coord in range(num_vars):
        exp = tuple(1 if i == coord else 0 for i in range(num_vars))
        out[exp] = band_lp.band_coeff(zero, coord, 0, band)
    return clean(out)


def poly_summary(poly: Poly) -> dict[str, object]:
    vals = list(poly.values())
    neg = [x for x in vals if x < 0]
    pos = [x for x in vals if x > 0]
    return {
        "terms": len(vals),
        "positive_terms": len(pos),
        "negative_terms": len(neg),
        "total_degree": total_degree(poly),
        "min_coeff": fmt_fraction(min(vals) if vals else Fraction(0)),
        "max_coeff": fmt_fraction(max(vals) if vals else Fraction(0)),
    }


def qcolumn(
    *,
    side: str,
    kind: str,
    name: str,
    multiplier_exp: Exp,
    poly: Poly,
    divisor: Poly,
) -> QColumn:
    if side == "face":
        quo, rem = divide_grevlex(poly, divisor)
    elif side == "lift":
        rem = {}
        quo = poly
    else:
        raise ValueError(side)
    return QColumn(
        side=side,
        kind=kind,
        name=name,
        multiplier_exp=multiplier_exp,
        rem=tuple(sorted(rem.items(), key=lambda item: grevlex_key(item[0]), reverse=True)),
        quo=tuple(sorted(quo.items(), key=lambda item: grevlex_key(item[0]), reverse=True)),
    )


def touches(col: QColumn, rem_support: set[Exp], quo_support: set[Exp], mode: str) -> bool:
    if mode in {"all", "derived"}:
        return True
    if mode != "target":
        raise ValueError(mode)
    return any(exp in rem_support for exp, _ in col.rem) or any(exp in quo_support for exp, _ in col.quo)


def candidate_multiplier_exps(
    poly: Poly,
    output_support: set[Exp],
    degree_cap: int,
    max_count: int | None,
) -> list[Exp]:
    seen: set[Exp] = set()
    poly_exps = sorted(poly, key=grevlex_key, reverse=True)
    support_exps = sorted(output_support, key=grevlex_key, reverse=True)
    if DERIVED_SUPPORT_TERM_LIMIT is not None:
        support_exps = support_exps[:DERIVED_SUPPORT_TERM_LIMIT]
    for out_exp in support_exps:
        for poly_exp in poly_exps:
            if not exp_divides(out_exp, poly_exp):
                continue
            m = exp_sub(out_exp, poly_exp)
            if sum(m) <= degree_cap:
                seen.add(m)
                if max_count is not None and len(seen) >= max_count:
                    return sorted(seen, key=grevlex_key, reverse=True)
    return sorted(seen, key=grevlex_key, reverse=True)


def make_base_columns(
    *,
    side: str,
    degree: int,
    divisor: Poly,
    rem_support: set[Exp],
    quo_support: set[Exp],
    support_mode: str,
    max_columns: int | None,
    num_vars: int,
) -> list[QColumn]:
    out: list[QColumn] = []
    if support_mode == "target":
        if side == "face":
            lead_exp, _lead_coeff = leading_term(divisor)
            candidate_exps = {
                exp for exp in rem_support
                if sum(exp) == degree
            }
            for exp in quo_support:
                shifted = exp_add(exp, lead_exp)
                if sum(shifted) == degree:
                    candidate_exps.add(shifted)
        else:
            candidate_exps = {
                exp for exp in quo_support
                if sum(exp) == degree
            }
        exps = sorted(candidate_exps, key=grevlex_key, reverse=True)
    elif support_mode == "derived":
        if side == "face":
            lead_exp, _lead_coeff = leading_term(divisor)
            candidate_exps = {
                exp for exp in rem_support
                if sum(exp) == degree
            }
            for exp in quo_support:
                shifted = exp_add(exp, lead_exp)
                if sum(shifted) == degree:
                    candidate_exps.add(shifted)
        else:
            candidate_exps = {
                exp for exp in quo_support
                if sum(exp) == degree
            }
        exps = sorted(candidate_exps, key=grevlex_key, reverse=True)
    else:
        exps = charts.all_exps(num_vars, degree)
    for exp in exps:
        col = qcolumn(
            side=side,
            kind=f"{side}_base",
            name=f"B{degree}",
            multiplier_exp=exp,
            poly=bernstein_basis_poly(degree, exp),
            divisor=divisor,
        )
        if touches(col, rem_support, quo_support, support_mode):
            out.append(col)
            if max_columns is not None and len(out) >= max_columns:
                break
    if max_columns is not None and len(out) > max_columns:
        out.sort(key=lambda c: len(c.rem) + len(c.quo), reverse=True)
        out = out[:max_columns]
    return out


def make_face_pair_columns(
    *,
    gen_polys: list[Poly],
    gen_names: tuple[str, ...],
    dominant: int,
    degree_cap: int,
    divisor: Poly,
    rem_support: set[Exp],
    quo_support: set[Exp],
    support_mode: str,
    max_pairs_per_family: int | None,
    num_vars: int,
    face_product_support: set[Exp],
) -> list[QColumn]:
    out: list[QColumn] = []
    ga = gen_polys[dominant]
    for i, gb in enumerate(gen_polys):
        if i == dominant:
            continue
        pair_cols: list[QColumn] = []
        delta = sub_poly(ga, gb)
        if support_mode == "derived":
            max_candidates = max_pairs_per_family
            gen_candidates = candidate_multiplier_exps(gb, face_product_support, degree_cap, max_candidates)
            delta_candidates = candidate_multiplier_exps(delta, face_product_support, degree_cap, max_candidates)
            candidate_exps = sorted(set(gen_candidates) | set(delta_candidates), key=grevlex_key, reverse=True)
        else:
            candidate_exps = charts.exps_upto(num_vars, degree_cap)
        for exp in candidate_exps:
            mult = bernstein_basis_poly(sum(exp), exp)
            gen_col = qcolumn(
                side="face",
                kind="face_gen",
                name=gen_names[i],
                multiplier_exp=exp,
                poly=mul_poly(gb, mult),
                divisor=divisor,
            )
            delta_col = qcolumn(
                side="face",
                kind="face_delta",
                name=f"{gen_names[dominant]}-{gen_names[i]}",
                multiplier_exp=exp,
                poly=mul_poly(delta, mult),
                divisor=divisor,
            )
            # Pair-closure: if either congruent partner is useful, keep both.
            if touches(gen_col, rem_support, quo_support, support_mode) or touches(delta_col, rem_support, quo_support, support_mode):
                pair_cols.extend([gen_col, delta_col])
                if max_pairs_per_family is not None and len(pair_cols) >= 2 * max_pairs_per_family:
                    break
        if max_pairs_per_family is not None and len(pair_cols) > 2 * max_pairs_per_family:
            scored = []
            for j in range(0, len(pair_cols), 2):
                c1, c2 = pair_cols[j], pair_cols[j + 1]
                score = len(c1.rem) + len(c1.quo) + len(c2.rem) + len(c2.quo)
                scored.append((score, c1, c2))
            scored.sort(key=lambda item: item[0], reverse=True)
            pair_cols = [c for _score, c1, c2 in scored[:max_pairs_per_family] for c in (c1, c2)]
        out.extend(pair_cols)
    return out


def make_band_columns(
    *,
    side: str,
    band: str,
    band_degree: int,
    divisor: Poly,
    rem_support: set[Exp],
    quo_support: set[Exp],
    support_mode: str,
    max_columns: int | None,
    num_vars: int,
    output_support: set[Exp],
) -> list[QColumn]:
    bpoly = band_poly(num_vars, band)
    out: list[QColumn] = []
    if support_mode == "derived":
        candidate_exps = candidate_multiplier_exps(bpoly, output_support, band_degree, max_columns)
    else:
        candidate_exps = charts.exps_upto(num_vars, band_degree)
    for exp in candidate_exps:
        mult = bernstein_basis_poly(sum(exp), exp)
        col = qcolumn(
            side=side,
            kind=f"{side}_band",
            name=band,
            multiplier_exp=exp,
            poly=mul_poly(bpoly, mult),
            divisor=divisor,
        )
        if touches(col, rem_support, quo_support, support_mode):
            out.append(col)
            if max_columns is not None and len(out) >= max_columns:
                break
    if max_columns is not None and len(out) > max_columns:
        out.sort(key=lambda c: len(c.rem) + len(c.quo), reverse=True)
        out = out[:max_columns]
    return out


def make_lift_gen_columns(
    *,
    gen_polys: list[Poly],
    gen_names: tuple[str, ...],
    dominant: int,
    degree_cap: int,
    divisor: Poly,
    quo_support: set[Exp],
    support_mode: str,
    max_columns_per_family: int | None,
    num_vars: int,
) -> list[QColumn]:
    out: list[QColumn] = []
    ga = gen_polys[dominant]
    families: list[tuple[str, str, Poly]] = []
    for i, poly in enumerate(gen_polys):
        families.append(("lift_gen", gen_names[i], poly))
    for i, poly in enumerate(gen_polys):
        if i == dominant:
            continue
        families.append(("lift_delta", f"{gen_names[dominant]}-{gen_names[i]}", sub_poly(ga, poly)))

    for kind, name, poly in families:
        family_cols: list[QColumn] = []
        if support_mode == "derived":
            candidate_exps = candidate_multiplier_exps(poly, quo_support, degree_cap, max_columns_per_family)
        else:
            candidate_exps = charts.exps_upto(num_vars, degree_cap)
        for exp in candidate_exps:
            if sum(exp) + total_degree(poly) > 9:
                continue
            mult = bernstein_basis_poly(sum(exp), exp)
            col = qcolumn(
                side="lift",
                kind=kind,
                name=name,
                multiplier_exp=exp,
                poly=mul_poly(poly, mult),
                divisor=divisor,
            )
            if touches(col, set(), quo_support, support_mode):
                family_cols.append(col)
                if max_columns_per_family is not None and len(family_cols) >= max_columns_per_family:
                    break
        if max_columns_per_family is not None and len(family_cols) > max_columns_per_family:
            family_cols.sort(key=lambda c: len(c.quo), reverse=True)
            family_cols = family_cols[:max_columns_per_family]
        out.extend(family_cols)
    return out


def build_columns(
    chart: charts.ChartData,
    dominant: int,
    band: str,
    tier: str,
    support_mode: str,
    max_base_columns: int | None,
    max_pairs_per_family: int | None,
    max_band_columns: int | None,
    divisor: Poly,
    rem_p: Poly,
    quo_p: Poly,
) -> list[QColumn]:
    num_vars = len(chart.variables)
    gen_polys = [homogenize_poly(expr, chart.variables, GEN_DEGREE) for expr in chart.generators]
    rem_support = set(rem_p)
    quo_support = set(quo_p)
    face_product_support = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            face_product_support.add(exp_add(qe, de))

    if tier == "tier1":
        face_pair_cap = 5
        face_band_cap = 6
        lift_gen_cap = 5
        lift_band_cap = 6
    elif tier == "tier2":
        face_pair_cap = 7
        face_band_cap = 8
        lift_gen_cap = 7
        lift_band_cap = 8
    elif tier == "tier3":
        face_pair_cap = 9
        face_band_cap = 10
        lift_gen_cap = 7
        lift_band_cap = 8
    else:
        raise ValueError(tier)

    columns: list[QColumn] = []
    columns.extend(
        make_base_columns(
            side="face",
            degree=TARGET_DEGREE,
            divisor=divisor,
            rem_support=rem_support,
            quo_support=quo_support,
            support_mode=support_mode,
            max_columns=max_base_columns,
            num_vars=num_vars,
        )
    )
    columns.extend(
        make_face_pair_columns(
            gen_polys=gen_polys,
            gen_names=chart.generator_names,
            dominant=dominant,
            degree_cap=face_pair_cap,
            divisor=divisor,
            rem_support=rem_support,
            quo_support=quo_support,
            support_mode=support_mode,
            max_pairs_per_family=max_pairs_per_family,
            num_vars=num_vars,
            face_product_support=face_product_support,
        )
    )
    columns.extend(
        make_band_columns(
            side="face",
            band=band,
            band_degree=face_band_cap,
            divisor=divisor,
            rem_support=rem_support,
            quo_support=quo_support,
            support_mode=support_mode,
            max_columns=max_band_columns,
            num_vars=num_vars,
            output_support=face_product_support,
        )
    )
    columns.extend(
        make_base_columns(
            side="lift",
            degree=9,
            divisor=divisor,
            rem_support=set(),
            quo_support=quo_support,
            support_mode=support_mode,
            max_columns=max_base_columns,
            num_vars=num_vars,
        )
    )
    columns.extend(
        make_lift_gen_columns(
            gen_polys=gen_polys,
            gen_names=chart.generator_names,
            dominant=dominant,
            degree_cap=lift_gen_cap,
            divisor=divisor,
            quo_support=quo_support,
            support_mode=support_mode,
            max_columns_per_family=max_pairs_per_family,
            num_vars=num_vars,
        )
    )
    columns.extend(
        make_band_columns(
            side="lift",
            band=band,
            band_degree=lift_band_cap,
            divisor=divisor,
            rem_support=set(),
            quo_support=quo_support,
            support_mode=support_mode,
            max_columns=max_band_columns,
            num_vars=num_vars,
            output_support=quo_support,
        )
    )
    return columns


def row_key(kind: str, exp: Exp) -> tuple[str, Exp]:
    return kind, exp


def build_equalities(rem_p: Poly, quo_p: Poly, columns: list[QColumn]) -> tuple[list[tuple[str, Exp]], list[Fraction], coo_matrix]:
    row_keys: set[tuple[str, Exp]] = {row_key("rem", exp) for exp in rem_p}
    row_keys.update(row_key("quo", exp) for exp in quo_p)
    for col in columns:
        row_keys.update(row_key("rem", exp) for exp, _ in col.rem)
        row_keys.update(row_key("quo", exp) for exp, _ in col.quo)
    rows_sorted = sorted(row_keys, key=lambda item: (item[0], grevlex_key(item[1])), reverse=True)
    row_index = {key: i for i, key in enumerate(rows_sorted)}
    rhs = [Fraction(0) for _ in rows_sorted]
    for exp, coeff in rem_p.items():
        rhs[row_index[row_key("rem", exp)]] = coeff
    for exp, coeff in quo_p.items():
        rhs[row_index[row_key("quo", exp)]] = coeff
    mat_rows: list[int] = []
    mat_cols: list[int] = []
    mat_vals: list[float] = []
    for j, col in enumerate(columns):
        for exp, coeff in col.rem:
            mat_rows.append(row_index[row_key("rem", exp)])
            mat_cols.append(j)
            mat_vals.append(float(coeff))
        for exp, coeff in col.quo:
            mat_rows.append(row_index[row_key("quo", exp)])
            mat_cols.append(j)
            mat_vals.append(float(coeff))
    mat = coo_matrix((mat_vals, (mat_rows, mat_cols)), shape=(len(rows_sorted), len(columns)))
    return rows_sorted, rhs, mat


def replay_exact(rows: list[tuple[str, Exp]], rhs: list[Fraction], columns: list[QColumn], raw: np.ndarray, max_denominators: list[int]) -> dict[str, object]:
    row_index = {key: i for i, key in enumerate(rows)}
    attempts: list[dict[str, object]] = []
    best_q: list[Fraction] | None = None
    for max_den in max_denominators:
        q = [Fraction(str(max(0.0, float(x)))).limit_denominator(max_den) for x in raw]
        best_q = q
        residual = rhs[:]
        nonzero = 0
        for val, col in zip(q, columns):
            if not val:
                continue
            nonzero += 1
            for exp, coeff in col.rem:
                residual[row_index[row_key("rem", exp)]] -= coeff * val
            for exp, coeff in col.quo:
                residual[row_index[row_key("quo", exp)]] -= coeff * val
        bad = [(i, x) for i, x in enumerate(residual) if x]
        attempts.append(
            {
                "max_denominator": max_den,
                "nonzero_multiplier_count": nonzero,
                "nonzero_residual_count": len(bad),
                "residual_prefix": [
                    {"row": i, "kind": rows[i][0], "exp": list(rows[i][1]), "value": fmt_fraction(x)}
                    for i, x in bad[:10]
                ],
            }
        )
        if not bad:
            return {"exact_ok": True, "max_denominator": max_den, "nonzero_multiplier_count": nonzero, "attempts": attempts}
    return {
        "exact_ok": False,
        "attempts": attempts,
        "candidate_nonzero_prefix": [
            {"col": i, "value": fmt_fraction(v), "side": columns[i].side, "kind": columns[i].kind, "name": columns[i].name, "multiplier_exp": list(columns[i].multiplier_exp)}
            for i, v in enumerate(best_q or [])
            if v
        ][:30],
    }


def solve_lp(rows: list[tuple[str, Exp]], rhs: list[Fraction], mat: coo_matrix, columns: list[QColumn], args: argparse.Namespace) -> dict[str, object]:
    if not columns:
        return {"success": False, "lp_status": -1, "lp_message": "no columns"}
    c = np.ones(len(columns), dtype=float) if args.objective == "sum" else np.zeros(len(columns), dtype=float)
    b_eq = np.array([float(x) for x in rhs], dtype=float)
    options = {} if args.time_limit <= 0 else {"time_limit": args.time_limit}
    res = linprog(c=c, A_eq=mat.tocsr(), b_eq=b_eq, bounds=[(0, None)] * len(columns), method=args.method, options=options)
    out: dict[str, object] = {
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
        "method": args.method,
        "objective": args.objective,
    }
    if res.success:
        eq_res = mat.tocsr().dot(res.x) - b_eq
        out.update(
            {
                "float_objective": float(res.fun),
                "float_nonzero": int(sum(1 for x in res.x if x > args.x_tol)),
                "float_max_abs_eq_residual": float(np.max(np.abs(eq_res))) if len(eq_res) else 0.0,
                "float_bad_eq_rows_tol": int(sum(1 for x in eq_res if abs(x) > args.row_tol)),
            }
        )
        if args.exact_replay_candidate:
            out["exact_replay_candidate"] = replay_exact(
                rows,
                rhs,
                columns,
                res.x,
                [int(x) for x in args.max_den.split(",") if x],
            )
    return out


def column_summary(columns: list[QColumn]) -> dict[str, object]:
    counts: dict[str, int] = {}
    rem_terms = 0
    quo_terms = 0
    for col in columns:
        key = f"{col.side}:{col.kind}:{col.name}"
        counts[key] = counts.get(key, 0) + 1
        rem_terms += len(col.rem)
        quo_terms += len(col.quo)
    return {"count": len(columns), "rem_terms": rem_terms, "quo_terms": quo_terms, "family_counts": dict(sorted(counts.items()))}


def run(args: argparse.Namespace) -> dict[str, object]:
    global DERIVED_SUPPORT_TERM_LIMIT
    DERIVED_SUPPORT_TERM_LIMIT = None if args.derived_support_limit == 0 else args.derived_support_limit
    t0 = time.monotonic()
    if args.verbose:
        print("phase=build_chart start", flush=True)
    chart = charts.build_chart(args.chart)
    if args.verbose:
        print(f"phase=build_chart done seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=target_hom start", flush=True)
    target = homogenize_poly(chart.target, chart.variables, TARGET_DEGREE)
    if args.verbose:
        print(f"phase=target_hom done terms={len(target)} seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=gen_hom start", flush=True)
    gen_polys = [homogenize_poly(expr, chart.variables, GEN_DEGREE) for expr in chart.generators]
    if args.verbose:
        print(f"phase=gen_hom done seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=target_divide start", flush=True)
    divisor = gen_polys[args.dominant]
    quo_p, rem_p = divide_grevlex(target, divisor)
    recomposed = add_poly(mul_poly(quo_p, divisor), rem_p)
    identity_diff = sub_poly(target, recomposed)
    if identity_diff:
        raise RuntimeError("target division identity failed")
    if args.verbose:
        print(
            f"phase=target_divide done rem_terms={len(rem_p)} quo_terms={len(quo_p)} "
            f"seconds={time.monotonic() - t0:.3f}",
            flush=True,
        )
        print("phase=build_columns start", flush=True)

    columns = build_columns(
        chart,
        args.dominant,
        args.band,
        args.tier,
        args.support,
        None if args.max_base_columns == 0 else args.max_base_columns,
        None if args.max_pairs_per_family == 0 else args.max_pairs_per_family,
        None if args.max_band_columns == 0 else args.max_band_columns,
        divisor,
        rem_p,
        quo_p,
    )
    if args.verbose:
        print(f"phase=build_columns done columns={len(columns)} seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=build_equalities start", flush=True)
    rows, rhs, mat = build_equalities(rem_p, quo_p, columns)
    if args.verbose:
        print(
            f"phase=build_equalities done rows={len(rows)} nnz={mat.nnz} "
            f"seconds={time.monotonic() - t0:.3f}",
            flush=True,
        )
        if not args.no_solve:
            print("phase=solve start", flush=True)
    solve = {"skipped": True} if args.no_solve else solve_lp(rows, rhs, mat, columns, args)
    if args.verbose and not args.no_solve:
        print(f"phase=solve done seconds={time.monotonic() - t0:.3f}", flush=True)
    return {
        "schema": "eq_odl1_rung2_face_split_quotient_probe_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "derived_support_limit": DERIVED_SUPPORT_TERM_LIMIT,
        "term_order": "graded_reverse_lex",
        "target_summary": poly_summary(target),
        "divisor_summary": poly_summary(divisor),
        "remP_summary": poly_summary(rem_p),
        "quoP_summary": poly_summary(quo_p),
        "columns": column_summary(columns),
        "quotient_rows": len(rows),
        "quotient_nnz": int(mat.nnz),
        "rhs_nonzero": sum(1 for x in rhs if x),
        "solve": solve,
        "seconds": time.monotonic() - t0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--tier", choices=["tier1", "tier2", "tier3"], default="tier2")
    ap.add_argument("--support", choices=["target", "derived", "all"], default="target")
    ap.add_argument("--max-base-columns", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--max-pairs-per-family", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--max-band-columns", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--derived-support-limit", type=int, default=0, help="0 scans all target support terms")
    ap.add_argument("--no-solve", action="store_true")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--objective", choices=["sum", "zero"], default="sum")
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--x-tol", type=float, default=1e-9)
    ap.add_argument("--row-tol", type=float, default=1e-8)
    ap.add_argument("--exact-replay-candidate", action="store_true")
    ap.add_argument("--max-den", default="1000,10000,1000000")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "chart": out["chart"],
                "dominant": out["dominant"],
                "dominant_name": out["dominant_name"],
                "tier": out["tier"],
                "columns": out["columns"]["count"],
                "quotient_rows": out["quotient_rows"],
                "quotient_nnz": out["quotient_nnz"],
                "solve": out["solve"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
