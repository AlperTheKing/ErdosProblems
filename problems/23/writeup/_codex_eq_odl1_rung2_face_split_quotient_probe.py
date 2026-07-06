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

try:
    import highspy
except ImportError:  # pragma: no cover - optional backend
    highspy = None


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


def progress_log(enabled: bool, t0: float | None, msg: str) -> None:
    if not enabled:
        return
    seconds = time.monotonic() - t0 if t0 is not None else 0.0
    print(f"phase=build_columns {msg} seconds={seconds:.3f}", flush=True)


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 512 and q.denominator.bit_length() < 512:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def parse_fraction(value) -> Fraction:
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, list) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    if isinstance(value, dict):
        if "num" in value and "den" in value:
            return Fraction(int(value["num"]), int(value["den"]))
        if "value" in value:
            return parse_fraction(value["value"])
    raise ValueError(f"cannot parse Fraction from {value!r}")


def read_target_beta(path: Path, row_count: int) -> list[Fraction]:
    """Read an exact custom Bernstein target vector.

    This intentionally accepts the same JSON forms as
    _codex_eq_odl1_rung2_source_solution_check.py so residual/checker
    artifacts can be routed into the quotient probe without format drift.
    """

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict) and "target_beta_sparse" in data:
        raw = data["target_beta_sparse"]
    elif isinstance(data, dict) and "target_beta" in data:
        raw = data["target_beta"]
    else:
        raise ValueError("target beta JSON must be a list or contain target_beta/target_beta_sparse")

    if isinstance(raw, list) and raw and all(isinstance(x, dict) and "row" in x for x in raw):
        out = [Fraction(0) for _ in range(row_count)]
        for rec in raw:
            row = int(rec["row"])
            if row < 0 or row >= row_count:
                raise ValueError(f"target beta row out of range: {row}")
            out[row] += parse_fraction(rec)
        return out

    if not isinstance(raw, list):
        raise ValueError("target beta payload must be a list")
    if len(raw) != row_count:
        raise ValueError(f"dense target beta length {len(raw)} != row count {row_count}")
    return [parse_fraction(x) for x in raw]


def poly_terms_record(poly: Poly) -> list[dict[str, object]]:
    return [
        {"exp": list(exp), "coeff": fraction_record(coeff)}
        for exp, coeff in sorted(poly.items(), key=lambda item: grevlex_key(item[0]), reverse=True)
    ]


def poly_from_terms_record(records: list[dict[str, object]]) -> Poly:
    out: Poly = {}
    for rec in records:
        exp_raw = rec.get("exp")
        if not isinstance(exp_raw, list):
            raise ValueError(f"term record missing exp list: {rec!r}")
        coeff = parse_fraction(rec.get("coeff"))
        exp = tuple(int(x) for x in exp_raw)
        out[exp] = out.get(exp, Fraction(0)) + coeff
    return clean(out)


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


def monic_normalize(poly: Poly) -> tuple[Poly, Exp, Fraction]:
    lead_exp, lead_coeff = leading_term(poly)
    return scale_poly(poly, Fraction(1, 1) / lead_coeff), lead_exp, lead_coeff


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


def poly_from_bernstein_vector(betas: list[Exp], coeffs: list[Fraction], degree: int) -> Poly:
    if len(betas) != len(coeffs):
        raise ValueError(f"Bernstein beta/coeff length mismatch: {len(betas)} != {len(coeffs)}")
    return clean(
        {
            beta: coeff * charts.multinomial(degree, beta)
            for beta, coeff in zip(betas, coeffs)
            if coeff
        }
    )


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


def qcolumn_from_parts(
    *,
    side: str,
    kind: str,
    name: str,
    multiplier_exp: Exp,
    rem: Poly,
    quo: Poly,
) -> QColumn:
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


def tier_caps(tier: str) -> tuple[int, int, int, int]:
    if tier == "tier1":
        # Tier 1 is the pair-closed reduced-support pass from
        # FACE_SPLIT_QUOTIENT_LP_GPTPRO.md: keep columns whose quotient
        # images touch rem(P)/quo(P), but do not impose the tighter Tier-2
        # face-degree cap.  The reduced support is controlled by
        # support_mode/derived_support_limit; the legal degree caps match
        # the full quotient search space.
        return 9, 10, 7, 8
    if tier == "tier2":
        return 7, 8, 7, 8
    if tier == "tier3":
        return 9, 10, 7, 8
    raise ValueError(tier)


def base_candidate_exps(
    *,
    side: str,
    degree: int,
    divisor: Poly,
    rem_support: set[Exp],
    quo_support: set[Exp],
    support_mode: str,
    num_vars: int,
) -> list[Exp]:
    if support_mode in {"target", "derived"}:
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
        return sorted(candidate_exps, key=grevlex_key, reverse=True)
    return charts.all_exps(num_vars, degree)


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
    progress: bool = False,
    progress_t0: float | None = None,
) -> list[QColumn]:
    out: list[QColumn] = []
    exps = base_candidate_exps(
        side=side,
        degree=degree,
        divisor=divisor,
        rem_support=rem_support,
        quo_support=quo_support,
        support_mode=support_mode,
        num_vars=num_vars,
    )
    progress_log(progress, progress_t0, f"base_start side={side} degree={degree} candidates={len(exps)}")
    for idx, exp in enumerate(exps, start=1):
        col_t0 = time.monotonic() if progress else 0.0
        col = qcolumn(
            side=side,
            kind=f"{side}_base",
            name=f"B{degree}",
            multiplier_exp=exp,
            poly=bernstein_basis_poly(degree, exp),
            divisor=divisor,
        )
        if progress:
            col_seconds = time.monotonic() - col_t0
            if col_seconds >= 1.0:
                progress_log(
                    progress,
                    progress_t0,
                    "base_slow "
                    f"side={side} degree={degree} checked={idx} kept={len(out)} "
                    f"seconds={col_seconds:.3f} rem_terms={len(col.rem)} quo_terms={len(col.quo)} "
                    f"exp={','.join(str(x) for x in exp)}",
                )
        if touches(col, rem_support, quo_support, support_mode):
            out.append(col)
            if max_columns is not None and len(out) >= max_columns:
                break
        if progress and idx % 1000 == 0:
            progress_log(progress, progress_t0, f"base_progress side={side} degree={degree} checked={idx} kept={len(out)}")
    if max_columns is not None and len(out) > max_columns:
        out.sort(key=lambda c: len(c.rem) + len(c.quo), reverse=True)
        out = out[:max_columns]
    progress_log(progress, progress_t0, f"base_done side={side} degree={degree} kept={len(out)}")
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
    face_pair_family_filter: set[str] | None,
    num_vars: int,
    face_product_support: set[Exp],
    progress: bool = False,
    progress_t0: float | None = None,
) -> list[QColumn]:
    out: list[QColumn] = []
    ga = gen_polys[dominant]
    dominant_lc = leading_term(ga)[1]
    for i, gb in enumerate(gen_polys):
        if i == dominant:
            continue
        if face_pair_family_filter is not None:
            gen_name = gen_names[i]
            delta_name = f"{gen_names[dominant]}-{gen_name}"
            if gen_name not in face_pair_family_filter and delta_name not in face_pair_family_filter:
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
        progress_log(progress, progress_t0, f"face_pair_start name={gen_names[i]} degree_cap={degree_cap} candidates={len(candidate_exps)}")
        for idx, exp in enumerate(candidate_exps, start=1):
            mult = bernstein_basis_poly(sum(exp), exp)
            gen_quo, gen_rem = divide_grevlex(mul_poly(gb, mult), divisor)
            gen_col = qcolumn_from_parts(
                side="face",
                kind="face_gen",
                name=gen_names[i],
                multiplier_exp=exp,
                rem=gen_rem,
                quo=gen_quo,
            )
            # If divisor = Ga / lc, then (Ga-Gb)*mult =
            # divisor*(lc*mult - quo(Gb*mult)) - rem(Gb*mult).
            # This preserves the pair-closed cone while avoiding a second
            # polynomial division for every multiplier.
            delta_col = qcolumn_from_parts(
                side="face",
                kind="face_delta",
                name=f"{gen_names[dominant]}-{gen_names[i]}",
                multiplier_exp=exp,
                rem=scale_poly(gen_rem, Fraction(-1)),
                quo=sub_poly(scale_poly(mult, dominant_lc), gen_quo),
            )
            # Pair-closure: if either congruent partner is useful, keep both.
            if touches(gen_col, rem_support, quo_support, support_mode) or touches(delta_col, rem_support, quo_support, support_mode):
                pair_cols.extend([gen_col, delta_col])
                if max_pairs_per_family is not None and len(pair_cols) >= 2 * max_pairs_per_family:
                    break
            if progress and idx % 2000 == 0:
                progress_log(progress, progress_t0, f"face_pair_progress name={gen_names[i]} checked={idx} kept={len(pair_cols)}")
        if max_pairs_per_family is not None and len(pair_cols) > 2 * max_pairs_per_family:
            scored = []
            for j in range(0, len(pair_cols), 2):
                c1, c2 = pair_cols[j], pair_cols[j + 1]
                score = len(c1.rem) + len(c1.quo) + len(c2.rem) + len(c2.quo)
                scored.append((score, c1, c2))
            scored.sort(key=lambda item: item[0], reverse=True)
            pair_cols = [c for _score, c1, c2 in scored[:max_pairs_per_family] for c in (c1, c2)]
        out.extend(pair_cols)
        progress_log(progress, progress_t0, f"face_pair_done name={gen_names[i]} kept={len(pair_cols)} total={len(out)}")
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
    progress: bool = False,
    progress_t0: float | None = None,
) -> list[QColumn]:
    bpoly = band_poly(num_vars, band)
    out: list[QColumn] = []
    if support_mode == "derived":
        candidate_exps = candidate_multiplier_exps(bpoly, output_support, band_degree, max_columns)
    else:
        candidate_exps = charts.exps_upto(num_vars, band_degree)
    progress_log(progress, progress_t0, f"band_start side={side} degree={band_degree} candidates={len(candidate_exps)}")
    for idx, exp in enumerate(candidate_exps, start=1):
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
        if progress and idx % 2000 == 0:
            progress_log(progress, progress_t0, f"band_progress side={side} checked={idx} kept={len(out)}")
    if max_columns is not None and len(out) > max_columns:
        out.sort(key=lambda c: len(c.rem) + len(c.quo), reverse=True)
        out = out[:max_columns]
    progress_log(progress, progress_t0, f"band_done side={side} kept={len(out)}")
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
    progress: bool = False,
    progress_t0: float | None = None,
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
        progress_log(progress, progress_t0, f"lift_start kind={kind} name={name} degree_cap={degree_cap} candidates={len(candidate_exps)}")
        for idx, exp in enumerate(candidate_exps, start=1):
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
            if progress and idx % 2000 == 0:
                progress_log(progress, progress_t0, f"lift_progress kind={kind} name={name} checked={idx} kept={len(family_cols)}")
        if max_columns_per_family is not None and len(family_cols) > max_columns_per_family:
            family_cols.sort(key=lambda c: len(c.quo), reverse=True)
            family_cols = family_cols[:max_columns_per_family]
        out.extend(family_cols)
        progress_log(progress, progress_t0, f"lift_done kind={kind} name={name} kept={len(family_cols)} total={len(out)}")
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
    face_pair_family_filter: set[str] | None,
    divisor: Poly,
    rem_p: Poly,
    quo_p: Poly,
    progress: bool = False,
    progress_t0: float | None = None,
) -> list[QColumn]:
    num_vars = len(chart.variables)
    gen_polys = [homogenize_poly(expr, chart.variables, GEN_DEGREE) for expr in chart.generators]
    rem_support = set(rem_p)
    quo_support = set(quo_p)
    face_product_support = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            face_product_support.add(exp_add(qe, de))

    face_pair_cap, face_band_cap, lift_gen_cap, lift_band_cap = tier_caps(tier)

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
            progress=progress,
            progress_t0=progress_t0,
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
            face_pair_family_filter=face_pair_family_filter,
            num_vars=num_vars,
            face_product_support=face_product_support,
            progress=progress,
            progress_t0=progress_t0,
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
            progress=progress,
            progress_t0=progress_t0,
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
            progress=progress,
            progress_t0=progress_t0,
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
            progress=progress,
            progress_t0=progress_t0,
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
            progress=progress,
            progress_t0=progress_t0,
        )
    )
    return columns


def candidate_plan_summary(
    chart: charts.ChartData,
    dominant: int,
    band: str,
    tier: str,
    support_mode: str,
    max_base_columns: int | None,
    max_pairs_per_family: int | None,
    max_band_columns: int | None,
    face_pair_family_filter: set[str] | None,
    divisor: Poly,
    rem_p: Poly,
    quo_p: Poly,
) -> dict[str, object]:
    num_vars = len(chart.variables)
    gen_polys = [homogenize_poly(expr, chart.variables, GEN_DEGREE) for expr in chart.generators]
    rem_support = set(rem_p)
    quo_support = set(quo_p)
    face_product_support = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            face_product_support.add(exp_add(qe, de))
    face_pair_cap, face_band_cap, lift_gen_cap, lift_band_cap = tier_caps(tier)

    face_base_candidates = base_candidate_exps(
        side="face",
        degree=TARGET_DEGREE,
        divisor=divisor,
        rem_support=rem_support,
        quo_support=quo_support,
        support_mode=support_mode,
        num_vars=num_vars,
    )
    lift_base_candidates = base_candidate_exps(
        side="lift",
        degree=9,
        divisor=divisor,
        rem_support=set(),
        quo_support=quo_support,
        support_mode=support_mode,
        num_vars=num_vars,
    )
    if max_base_columns is not None:
        face_base_count = min(len(face_base_candidates), max_base_columns)
        lift_base_count = min(len(lift_base_candidates), max_base_columns)
    else:
        face_base_count = len(face_base_candidates)
        lift_base_count = len(lift_base_candidates)

    ga = gen_polys[dominant]
    face_pair_families = []
    face_pair_columns = 0
    for i, gb in enumerate(gen_polys):
        if i == dominant:
            continue
        if face_pair_family_filter is not None:
            gen_name = chart.generator_names[i]
            delta_name = f"{chart.generator_names[dominant]}-{gen_name}"
            if gen_name not in face_pair_family_filter and delta_name not in face_pair_family_filter:
                continue
        delta = sub_poly(ga, gb)
        if support_mode == "derived":
            gen_candidates = candidate_multiplier_exps(gb, face_product_support, face_pair_cap, max_pairs_per_family)
            delta_candidates = candidate_multiplier_exps(delta, face_product_support, face_pair_cap, max_pairs_per_family)
            candidate_exps = sorted(set(gen_candidates) | set(delta_candidates), key=grevlex_key, reverse=True)
        else:
            candidate_exps = charts.exps_upto(num_vars, face_pair_cap)
        multiplier_count = len(candidate_exps)
        if max_pairs_per_family is not None:
            multiplier_count = min(multiplier_count, max_pairs_per_family)
        columns = 2 * multiplier_count
        face_pair_columns += columns
        face_pair_families.append(
            {
                "name": chart.generator_names[i],
                "multiplier_candidates": len(candidate_exps),
                "multiplier_count_after_cap": multiplier_count,
                "pair_columns": columns,
            }
        )

    bpoly = band_poly(num_vars, band)
    if support_mode == "derived":
        face_band_candidates = candidate_multiplier_exps(bpoly, face_product_support, face_band_cap, max_band_columns)
        lift_band_candidates = candidate_multiplier_exps(bpoly, quo_support, lift_band_cap, max_band_columns)
    else:
        face_band_candidates = charts.exps_upto(num_vars, face_band_cap)
        lift_band_candidates = charts.exps_upto(num_vars, lift_band_cap)
    face_band_count = len(face_band_candidates)
    lift_band_count = len(lift_band_candidates)
    if max_band_columns is not None:
        face_band_count = min(face_band_count, max_band_columns)
        lift_band_count = min(lift_band_count, max_band_columns)

    lift_families: list[tuple[str, str, Poly]] = []
    for i, poly in enumerate(gen_polys):
        lift_families.append(("lift_gen", chart.generator_names[i], poly))
    for i, poly in enumerate(gen_polys):
        if i == dominant:
            continue
        lift_families.append(("lift_delta", f"{chart.generator_names[dominant]}-{chart.generator_names[i]}", sub_poly(ga, poly)))

    lift_family_summaries = []
    lift_family_columns = 0
    for kind, name, poly in lift_families:
        if support_mode == "derived":
            candidates = candidate_multiplier_exps(poly, quo_support, lift_gen_cap, max_pairs_per_family)
        else:
            candidates = charts.exps_upto(num_vars, lift_gen_cap)
        legal_count = sum(1 for exp in candidates if sum(exp) + total_degree(poly) <= 9)
        if max_pairs_per_family is not None:
            legal_count = min(legal_count, max_pairs_per_family)
        lift_family_columns += legal_count
        lift_family_summaries.append(
            {
                "kind": kind,
                "name": name,
                "multiplier_candidates": len(candidates),
                "legal_count_after_degree_and_cap": legal_count,
            }
        )

    total_columns = face_base_count + face_pair_columns + face_band_count + lift_base_count + lift_family_columns + lift_band_count
    return {
        "face_base_columns": face_base_count,
        "face_pair_columns": face_pair_columns,
        "face_band_columns": face_band_count,
        "lift_base_columns": lift_base_count,
        "lift_family_columns": lift_family_columns,
        "lift_band_columns": lift_band_count,
        "total_candidate_columns": total_columns,
        "face_pair_family_filter": sorted(face_pair_family_filter) if face_pair_family_filter is not None else None,
        "face_pair_families": face_pair_families,
        "lift_families": lift_family_summaries,
        "caps": {
            "face_pair_cap": face_pair_cap,
            "face_band_cap": face_band_cap,
            "lift_gen_cap": lift_gen_cap,
            "lift_band_cap": lift_band_cap,
        },
        "note": "For support=derived and no max caps, these counts match kept columns before quotient row construction.",
    }


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
    if args.method == "highspy":
        return solve_lp_highspy(rows, rhs, mat, columns, args)
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


def solve_lp_highspy(rows: list[tuple[str, Exp]], rhs: list[Fraction], mat: coo_matrix, columns: list[QColumn], args: argparse.Namespace) -> dict[str, object]:
    if highspy is None:
        return {"success": False, "lp_status": -2, "lp_message": "highspy is not installed", "method": "highspy", "objective": args.objective}
    csc = mat.tocsc()
    num_col = len(columns)
    num_row = len(rhs)
    inf = highspy.kHighsInf

    lp = highspy.HighsLp()
    lp.num_col_ = num_col
    lp.num_row_ = num_row
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = [1.0 if args.objective == "sum" else 0.0] * num_col
    lp.col_lower_ = [0.0] * num_col
    lp.col_upper_ = [inf] * num_col
    b_eq = [float(x) for x in rhs]
    lp.row_lower_ = b_eq
    lp.row_upper_ = b_eq

    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = num_col
    a.num_row_ = num_row
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", bool(args.verbose))
    if args.highspy_solver != "choose":
        highs.setOptionValue("solver", args.highspy_solver)
    if args.time_limit > 0:
        highs.setOptionValue("time_limit", float(args.time_limit))
    if args.solver_threads > 0:
        highs.setOptionValue("threads", int(args.solver_threads))
    status = highs.passModel(lp)
    if status != highspy.HighsStatus.kOk:
        return {"success": False, "lp_status": int(status), "lp_message": f"highspy passModel failed: {status}", "method": "highspy", "objective": args.objective}
    run_status = highs.run()
    model_status = highs.getModelStatus()
    model_status_text = highs.modelStatusToString(model_status)
    success = model_status == highspy.HighsModelStatus.kOptimal
    out: dict[str, object] = {
        "lp_status": int(model_status),
        "lp_message": model_status_text,
        "run_status": int(run_status),
        "success": bool(success),
        "method": "highspy",
        "objective": args.objective,
        "solver_threads": args.solver_threads,
        "highspy_solver": args.highspy_solver,
    }
    if success:
        sol = highs.getSolution()
        x = np.array(sol.col_value, dtype=float)
        b = np.array(b_eq, dtype=float)
        eq_res = mat.tocsr().dot(x) - b
        objective = float(np.dot(np.array(lp.col_cost_, dtype=float), x))
        out.update(
            {
                "float_objective": objective,
                "float_nonzero": int(sum(1 for val in x if val > args.x_tol)),
                "float_max_abs_eq_residual": float(np.max(np.abs(eq_res))) if len(eq_res) else 0.0,
                "float_bad_eq_rows_tol": int(sum(1 for val in eq_res if abs(val) > args.row_tol)),
            }
        )
        if args.exact_replay_candidate:
            out["exact_replay_candidate"] = replay_exact(
                rows,
                rhs,
                columns,
                x,
                [int(val) for val in args.max_den.split(",") if val],
            )
    return out


def pair_closure_summary(columns: list[QColumn], gen_names: tuple[str, ...], dominant: int) -> dict[str, object]:
    dominant_name = gen_names[dominant]
    face_gen: dict[str, set[Exp]] = {}
    face_delta: dict[str, set[Exp]] = {}
    for col in columns:
        if col.side != "face":
            continue
        if col.kind == "face_gen":
            face_gen.setdefault(col.name, set()).add(col.multiplier_exp)
        elif col.kind == "face_delta":
            face_delta.setdefault(col.name, set()).add(col.multiplier_exp)

    families: list[dict[str, object]] = []
    total_pairs = 0
    total_gen_only = 0
    total_delta_only = 0
    mismatch_examples: list[dict[str, object]] = []
    for i, name in enumerate(gen_names):
        if i == dominant:
            continue
        delta_name = f"{dominant_name}-{name}"
        gen_exps = face_gen.get(name, set())
        delta_exps = face_delta.get(delta_name, set())
        gen_only = sorted(gen_exps - delta_exps, key=grevlex_key, reverse=True)
        delta_only = sorted(delta_exps - gen_exps, key=grevlex_key, reverse=True)
        pair_count = len(gen_exps & delta_exps)
        total_pairs += pair_count
        total_gen_only += len(gen_only)
        total_delta_only += len(delta_only)
        families.append(
            {
                "gen_name": name,
                "delta_name": delta_name,
                "paired_multiplier_count": pair_count,
                "gen_only_count": len(gen_only),
                "delta_only_count": len(delta_only),
            }
        )
        for exp in gen_only[:3]:
            mismatch_examples.append({"family": name, "missing": "face_delta", "exp": list(exp)})
        for exp in delta_only[:3]:
            mismatch_examples.append({"family": name, "missing": "face_gen", "exp": list(exp)})

    return {
        "ok": total_gen_only == 0 and total_delta_only == 0,
        "checked_family_count": len(families),
        "paired_multiplier_count": total_pairs,
        "gen_only_count": total_gen_only,
        "delta_only_count": total_delta_only,
        "families": families,
        "mismatch_examples": mismatch_examples[:20],
    }


def column_summary(columns: list[QColumn], gen_names: tuple[str, ...] | None = None, dominant: int | None = None) -> dict[str, object]:
    counts: dict[str, int] = {}
    rem_terms = 0
    quo_terms = 0
    for col in columns:
        key = f"{col.side}:{col.kind}:{col.name}"
        counts[key] = counts.get(key, 0) + 1
        rem_terms += len(col.rem)
        quo_terms += len(col.quo)
    out = {"count": len(columns), "rem_terms": rem_terms, "quo_terms": quo_terms, "family_counts": dict(sorted(counts.items()))}
    if gen_names is not None and dominant is not None:
        closure = pair_closure_summary(columns, gen_names, dominant)
        if not closure["ok"]:
            raise RuntimeError(f"face pair closure failed: {closure['mismatch_examples'][:3]}")
        out["face_pair_closure"] = closure
    return out


def parse_family_filter(raw: str) -> set[str] | None:
    items = {item.strip() for item in raw.split(",") if item.strip()}
    return items or None


def target_metadata(args: argparse.Namespace, tier0_payload: dict[str, object] | None = None) -> dict[str, object]:
    if tier0_payload is not None:
        return {
            "target_mode": tier0_payload.get("target_mode", "chart_target"),
            "target_beta_json": tier0_payload.get("target_beta_json"),
            "tier0_json": str(args.tier0_json) if args.tier0_json else None,
        }
    return {
        "target_mode": "custom_bernstein" if args.target_beta_json else "chart_target",
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "tier0_json": None,
    }

def run(args: argparse.Namespace) -> dict[str, object]:
    global DERIVED_SUPPORT_TERM_LIMIT
    DERIVED_SUPPORT_TERM_LIMIT = None if args.derived_support_limit == 0 else args.derived_support_limit
    t0 = time.monotonic()
    if args.verbose:
        print("phase=build_chart start", flush=True)
    chart = charts.build_chart(args.chart)
    if args.verbose:
        print(f"phase=build_chart done seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=gen_hom start", flush=True)
    gen_polys = [homogenize_poly(expr, chart.variables, GEN_DEGREE) for expr in chart.generators]
    if args.verbose:
        print(f"phase=gen_hom done seconds={time.monotonic() - t0:.3f}", flush=True)
    divisor_raw = gen_polys[args.dominant]
    divisor, divisor_lead_exp, divisor_lead_coeff = monic_normalize(divisor_raw)
    tier0_payload = None
    if args.tier0_json:
        if args.target_beta_json:
            raise ValueError("--target-beta-json cannot be combined with --tier0-json; the cached tier0 JSON already fixes the target")
        if args.verbose:
            print("phase=target_divide reuse_start", flush=True)
        tier0_payload = json.loads(args.tier0_json.read_text(encoding="utf-8"))
        if int(tier0_payload.get("chart")) != args.chart or int(tier0_payload.get("dominant")) != args.dominant:
            raise ValueError("--tier0-json chart/dominant does not match requested chart/dominant")
        if not tier0_payload.get("target_division_identity_ok"):
            raise ValueError("--tier0-json does not record target_division_identity_ok=true")
        cached_divisor = poly_from_terms_record(tier0_payload["divisor_monic_terms"])  # type: ignore[index]
        if cached_divisor != divisor:
            raise ValueError("--tier0-json divisor_monic_terms do not match current chart/dominant divisor")
        rem_p = poly_from_terms_record(tier0_payload["remP_terms"])  # type: ignore[index]
        quo_p = poly_from_terms_record(tier0_payload["quoP_terms"])  # type: ignore[index]
        target_beta = None
        target_summary = tier0_payload.get("target_summary")
        target_beta_nonzero_count = tier0_payload.get("target_beta_nonzero_count")
        if args.verbose:
            print(
                f"phase=target_divide reuse_done rem_terms={len(rem_p)} quo_terms={len(quo_p)} "
                f"seconds={time.monotonic() - t0:.3f}",
                flush=True,
            )
    else:
        if args.verbose:
            print("phase=target_hom start", flush=True)
        if args.target_beta_json:
            target_betas = charts.all_exps(len(chart.variables), TARGET_DEGREE)
            target_beta = read_target_beta(args.target_beta_json, len(target_betas))
            target = poly_from_bernstein_vector(target_betas, target_beta, TARGET_DEGREE)
        else:
            target_beta = None
            target = homogenize_poly(chart.target, chart.variables, TARGET_DEGREE)
        if args.verbose:
            print(
                f"phase=target_hom done mode={target_metadata(args)['target_mode']} "
                f"terms={len(target)} seconds={time.monotonic() - t0:.3f}",
                flush=True,
            )
            print("phase=target_divide start", flush=True)
        quo_p, rem_p = divide_grevlex(target, divisor)
        recomposed = add_poly(mul_poly(quo_p, divisor), rem_p)
        identity_diff = sub_poly(target, recomposed)
        if identity_diff:
            raise RuntimeError("target division identity failed")
        target_summary = poly_summary(target)
        target_beta_nonzero_count = sum(1 for x in target_beta if x) if target_beta is not None else None
    if args.verbose:
        print(
            f"phase=target_divide done rem_terms={len(rem_p)} quo_terms={len(quo_p)} "
            f"seconds={time.monotonic() - t0:.3f}",
            flush=True,
        )
        if not args.tier0_only:
            print("phase=build_columns start", flush=True)

    if args.tier0_only:
        return {
            "schema": "eq_odl1_rung2_face_split_quotient_tier0_v1",
            **target_metadata(args, tier0_payload),
            "target_beta_nonzero_count": target_beta_nonzero_count,
            "chart": args.chart,
            "dominant": args.dominant,
            "dominant_name": chart.generator_names[args.dominant],
            "band": args.band,
            "tier": args.tier,
            "term_order": "graded_reverse_lex",
            "divisor_normalization": "leading_coeff_to_1",
            "divisor_raw_summary": poly_summary(divisor_raw),
            "divisor_raw_leading_exp": list(divisor_lead_exp),
            "divisor_raw_leading_coeff": fraction_record(divisor_lead_coeff),
            "divisor_monic_summary": poly_summary(divisor),
            "divisor_monic_terms": poly_terms_record(divisor),
            "target_summary": target_summary,
            "remP_summary": poly_summary(rem_p),
            "quoP_summary": poly_summary(quo_p),
            "target_division_identity_ok": True,
            "remP_support": [list(exp) for exp in sorted(rem_p, key=grevlex_key, reverse=True)],
            "quoP_support": [list(exp) for exp in sorted(quo_p, key=grevlex_key, reverse=True)],
            "remP_terms": poly_terms_record(rem_p),
            "quoP_terms": poly_terms_record(quo_p),
            "seconds": time.monotonic() - t0,
        }

    if args.candidate_summary_only:
        plan = candidate_plan_summary(
            chart,
            args.dominant,
            args.band,
            args.tier,
            args.support,
            None if args.max_base_columns == 0 else args.max_base_columns,
            None if args.max_pairs_per_family == 0 else args.max_pairs_per_family,
            None if args.max_band_columns == 0 else args.max_band_columns,
            parse_family_filter(args.face_pair_families),
            divisor,
            rem_p,
            quo_p,
        )
        return {
            "schema": "eq_odl1_rung2_face_split_quotient_candidate_summary_v1",
            **target_metadata(args, tier0_payload),
            "target_beta_nonzero_count": target_beta_nonzero_count,
            "chart": args.chart,
            "dominant": args.dominant,
            "dominant_name": chart.generator_names[args.dominant],
            "band": args.band,
            "tier": args.tier,
            "support": args.support,
            "derived_support_limit": DERIVED_SUPPORT_TERM_LIMIT,
            "term_order": "graded_reverse_lex",
            "divisor_normalization": "leading_coeff_to_1",
            "target_summary": target_summary,
            "divisor_summary": poly_summary(divisor),
            "remP_summary": poly_summary(rem_p),
            "quoP_summary": poly_summary(quo_p),
            "target_division_identity_ok": True,
            "candidate_plan": plan,
            "seconds": time.monotonic() - t0,
        }

    columns = build_columns(
        chart,
        args.dominant,
        args.band,
        args.tier,
        args.support,
        None if args.max_base_columns == 0 else args.max_base_columns,
        None if args.max_pairs_per_family == 0 else args.max_pairs_per_family,
        None if args.max_band_columns == 0 else args.max_band_columns,
        parse_family_filter(args.face_pair_families),
        divisor,
        rem_p,
        quo_p,
        progress=args.verbose,
        progress_t0=t0,
    )
    if args.verbose:
        print(f"phase=build_columns done columns={len(columns)} seconds={time.monotonic() - t0:.3f}", flush=True)
        if not args.columns_only:
            print("phase=build_equalities start", flush=True)
    if args.columns_only:
        return {
            "schema": "eq_odl1_rung2_face_split_quotient_columns_v1",
            **target_metadata(args, tier0_payload),
            "target_beta_nonzero_count": target_beta_nonzero_count,
            "chart": args.chart,
            "dominant": args.dominant,
            "dominant_name": chart.generator_names[args.dominant],
            "band": args.band,
            "tier": args.tier,
            "support": args.support,
            "derived_support_limit": DERIVED_SUPPORT_TERM_LIMIT,
            "term_order": "graded_reverse_lex",
            "divisor_normalization": "leading_coeff_to_1",
            "target_summary": target_summary,
            "divisor_summary": poly_summary(divisor),
            "remP_summary": poly_summary(rem_p),
            "quoP_summary": poly_summary(quo_p),
            "target_division_identity_ok": True,
            "columns": column_summary(columns, chart.generator_names, args.dominant),
            "seconds": time.monotonic() - t0,
        }
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
        **target_metadata(args, tier0_payload),
        "target_beta_nonzero_count": target_beta_nonzero_count,
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "derived_support_limit": DERIVED_SUPPORT_TERM_LIMIT,
        "term_order": "graded_reverse_lex",
        "target_summary": target_summary,
        "divisor_summary": poly_summary(divisor),
        "remP_summary": poly_summary(rem_p),
        "quoP_summary": poly_summary(quo_p),
        "columns": column_summary(columns, chart.generator_names, args.dominant),
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
    ap.add_argument(
        "--target-beta-json",
        type=Path,
        default=None,
        help="Optional exact degree-11 Bernstein target vector; default is the chart target polynomial.",
    )
    ap.add_argument(
        "--tier0-json",
        type=Path,
        default=None,
        help="Reuse exact remP/quoP/divisor terms from a previous tier0 quotient diagnostic JSON.",
    )
    ap.add_argument("--max-base-columns", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--max-pairs-per-family", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--max-band-columns", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--face-pair-families", default="", help="comma-separated non-dominant generator names/delta names to include as whole face-pair families")
    ap.add_argument("--derived-support-limit", type=int, default=0, help="0 scans all target support terms")
    ap.add_argument("--tier0-only", action="store_true", help="only emit rem(P)/quo(P) monic division diagnostic")
    ap.add_argument("--candidate-summary-only", action="store_true", help="emit exact candidate-set sizes without quotient column construction")
    ap.add_argument("--columns-only", action="store_true", help="build selected quotient columns but skip row matrix and LP")
    ap.add_argument("--no-solve", action="store_true")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm", "highspy"], default="highs")
    ap.add_argument("--solver-threads", type=int, default=0)
    ap.add_argument("--highspy-solver", choices=["choose", "simplex", "ipm"], default="choose")
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
                "columns": out.get("columns", {}).get("count"),
                "quotient_rows": out.get("quotient_rows"),
                "quotient_nnz": out.get("quotient_nnz"),
                "solve": out.get("solve"),
                "tier0_only": bool(args.tier0_only),
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
