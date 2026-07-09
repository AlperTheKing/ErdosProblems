#!/usr/bin/env python3
"""Export an O14 Rung-2 source solution as chunked PolyCert NF data.

This is a generator input, not the final Lean emitter.  It reconstructs the exact
Bernstein cone identity used by the Python/Fraction checker:

    target = residual_base + sum_i q_i * multiplier_i * slack_i

and emits ordinary monomial normal forms compatible with
Erdos23Delta0.PolyCert.NF.  Chunk pairs are grouped by monomial powers so each
pair is independently checkEq-friendly.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

# Allow imports when invoked from repo root.
THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

import _codex_eq_odl1_rung2_band_lp as band_lp
import _codex_eq_odl1_rung2_charts as charts
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_support_lp as support

NFDict = dict[tuple[tuple[int, int], ...], Fraction]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_solution(path: Path) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            col = int(rec["source_col"])
            val = Fraction(int(rec["num"]), int(rec["den"])
            )
            out[col] = out.get(col, Fraction(0)) + val
    return {k: v for k, v in out.items() if v}


def frac_json(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def pows_key(exp: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple((i, e) for i, e in enumerate(exp) if e)


def nf_add(a: NFDict, b: NFDict) -> NFDict:
    out = dict(a)
    for p, c in b.items():
        out[p] = out.get(p, Fraction(0)) + c
        if out[p] == 0:
            del out[p]
    return out


def nf_scale(a: NFDict, q: Fraction) -> NFDict:
    if q == 0:
        return {}
    return {p: c * q for p, c in a.items() if c * q}


def nf_mul(a: NFDict, b: NFDict) -> NFDict:
    out: NFDict = {}
    for pa, ca in a.items():
        da = dict(pa)
        for pb, cb in b.items():
            d = dict(da)
            for v, e in pb:
                d[v] = d.get(v, 0) + e
            key = tuple(sorted((v, e) for v, e in d.items() if e))
            out[key] = out.get(key, Fraction(0)) + ca * cb
            if out[key] == 0:
                del out[key]
    return out


def bernstein_nf(coeffs: dict[tuple[int, ...], Fraction], degree: int) -> NFDict:
    out: NFDict = {}
    for exp, beta_coeff in coeffs.items():
        if not beta_coeff:
            continue
        c = beta_coeff * charts.multinomial(degree, exp)
        if c:
            out[pows_key(exp)] = out.get(pows_key(exp), Fraction(0)) + c
    return {p: c for p, c in out.items() if c}


def sympy_expr_nf(expr, vars_) -> NFDict:
    poly = charts.sp.Poly(charts.sp.expand(expr), *vars_, domain=charts.sp.QQ)
    out: NFDict = {}
    for exp_raw, coeff_raw in poly.terms():
        coeff = Fraction(int(coeff_raw.p), int(coeff_raw.q))
        exp = tuple(int(x) for x in exp_raw)
        if coeff:
            out[pows_key(exp)] = out.get(pows_key(exp), Fraction(0)) + coeff
    return {p: c for p, c in out.items() if c}


def nf_terms(nf: NFDict) -> list[dict[str, Any]]:
    rows = []
    for pows, coeff in sorted(nf.items(), key=lambda kv: kv[0]):
        rows.append({"coeff": frac_json(coeff), "pows": [[int(v), int(e)] for v, e in pows]})
    return rows


def nf_from_terms_json(rows: list[dict[str, Any]]) -> NFDict:
    out: NFDict = {}
    for row in rows:
        pows = tuple((int(v), int(e)) for v, e in row["pows"] if int(e))
        c = Fraction(int(row["coeff"]["num"]), int(row["coeff"]["den"]))
        out[pows] = out.get(pows, Fraction(0)) + c
    return {p: c for p, c in out.items() if c}


def slack_nf_for_column(col: support.Column, prepared: support.PreparedChart, gen_polys, dominant: int) -> tuple[NFDict, int, str]:
    if col.kind == "gen":
        idx = prepared.chart.generator_names.index(col.name)
        return bernstein_nf(gen_polys[idx], support.GEN_DEGREE), support.GEN_MULT_DEGREE, col.name
    if col.kind == "delta":
        left, right = col.name.split("-", 1)
        if left != prepared.chart.generator_names[dominant]:
            raise ValueError(f"unexpected delta left {left}, dominant {prepared.chart.generator_names[dominant]}")
        ridx = prepared.chart.generator_names.index(right)
        return bernstein_nf(support.poly_diff(gen_polys[dominant], gen_polys[ridx]), support.GEN_DEGREE), support.GEN_MULT_DEGREE, col.name
    if col.kind == "band":
        num_vars = len(prepared.chart.variables)
        coeffs: dict[tuple[int, ...], Fraction] = {}
        for coord in range(num_vars):
            exp = tuple(1 if i == coord else 0 for i in range(num_vars))
            if col.name == "near_2s_minus_1":
                coeffs[exp] = Fraction(1 if coord == 0 else -1)
            elif col.name == "inf_1_minus_2s":
                coeffs[exp] = Fraction(-1 if coord == 0 else 1)
            else:
                raise ValueError(col.name)
        return bernstein_nf(coeffs, 1), support.BAND_MULT_DEGREE, col.name
    raise ValueError(col.kind)


def bucket_chunks(left: NFDict, right: NFDict, chunk_size: int) -> list[dict[str, Any]]:
    if left != right:
        diff = nf_add(left, nf_scale(right, Fraction(-1)))
        raise ValueError(f"left/right differ in {len(diff)} monomials")
    keys = sorted(left)
    chunks = []
    for i in range(0, len(keys), chunk_size):
        part_keys = keys[i:i + chunk_size]
        l = {k: left[k] for k in part_keys}
        r = {k: right[k] for k in part_keys}
        chunks.append({"left": nf_terms(l), "right": nf_terms(r)})
    return chunks


def collect_terms(rows: list[dict[str, Any]]) -> NFDict:
    return nf_from_terms_json(rows)


def raw_product_terms(mult_nf: NFDict, slack_nf: NFDict) -> list[dict[str, Any]]:
    """Return terms in the same order as Lean's NF.mul for a one-monomial multiplier."""
    mult_rows = nf_terms(mult_nf)
    if len(mult_rows) != 1:
        raise ValueError(f"expected one-term Bernstein multiplier, got {len(mult_rows)}")
    m = mult_rows[0]
    m_pows = tuple((int(v), int(e)) for v, e in m["pows"] if int(e))
    m_coeff = Fraction(int(m["coeff"]["num"]), int(m["coeff"]["den"]))
    out = []
    for s in nf_terms(slack_nf):
        d = dict(m_pows)
        for v, e in s["pows"]:
            d[int(v)] = d.get(int(v), 0) + int(e)
        s_coeff = Fraction(int(s["coeff"]["num"]), int(s["coeff"]["den"]))
        c = m_coeff * s_coeff
        if c:
            out.append({
                "coeff": frac_json(c),
                "pows": [[int(v), int(e)] for v, e in sorted(d.items()) if e],
            })
    return out


def combo_order_chunks(raw_combo_terms: list[dict[str, Any]], chunk_size: int) -> tuple[list[dict[str, Any]], NFDict]:
    chunks = []
    left_total: NFDict = {}
    for i in range(0, len(raw_combo_terms), chunk_size):
        right = raw_combo_terms[i:i + chunk_size]
        left_nf = collect_terms(right)
        left_total = nf_add(left_total, left_nf)
        chunks.append({"left": nf_terms(left_nf), "right": right})
    return chunks, left_total


def run(args: argparse.Namespace) -> dict[str, Any]:
    inventory = read_json(args.inventory)
    row = next((r for r in inventory["rows"] if int(r["slot"]) == args.slot), None)
    if row is None:
        raise ValueError(f"slot not found: {args.slot}")
    manifest = read_json(Path(row["manifest"]))
    vals = read_solution(Path(row["solution_path"]))
    prepared, columns, _mat, _b_ub = probe.build_lp(int(row["chart"]), int(row["dominant"]), row["band"], manifest["support"])
    chart, gen_polys = support.build_chart_hom2_generators(int(row["chart"]))
    if tuple(chart.generator_names) != tuple(prepared.chart.generator_names):
        raise ValueError("generator name mismatch")

    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if source_col < 0 or source_col >= len(columns):
            raise ValueError(f"source_col out of range: {source_col}")
        for beta_row, coeff in columns[source_col].terms:
            residual[beta_row] -= coeff * val
    if any(x < 0 for x in vals.values()):
        raise ValueError("negative solution coefficient")
    if any(x < 0 for x in residual):
        neg = [(i, x) for i, x in enumerate(residual) if x < 0][:5]
        raise ValueError(f"negative residual: {neg}")

    beta_residual = {beta: residual[i] for i, beta in enumerate(prepared.betas) if residual[i]}
    base_nf = bernstein_nf(beta_residual, charts.TARGET_DEGREE)
    target_nf = sympy_expr_nf(prepared.chart.target, prepared.chart.variables)

    mults = []
    slacks = []
    combo_nf = dict(base_nf)
    raw_combo_terms = nf_terms(base_nf)
    for source_col, val in sorted(vals.items()):
        col = columns[source_col]
        slack_nf, mult_degree, slack_name = slack_nf_for_column(col, prepared, gen_polys, int(row["dominant"]))
        mult_coeffs = {tuple(col.multiplier_exp): val}
        mult_nf = bernstein_nf(mult_coeffs, mult_degree)
        prod_nf = nf_mul(mult_nf, slack_nf)
        combo_nf = nf_add(combo_nf, prod_nf)
        raw_combo_terms.extend(raw_product_terms(mult_nf, slack_nf))
        mults.append({
            "source_col": int(source_col),
            "kind": col.kind,
            "name": col.name,
            "multiplier_exp": list(col.multiplier_exp),
            "degree": mult_degree,
            "nf": nf_terms(mult_nf),
        })
        slacks.append({
            "source_col": int(source_col),
            "kind": col.kind,
            "name": slack_name,
            "nf": nf_terms(slack_nf),
        })

    if combo_nf != target_nf:
        diff = nf_add(target_nf, nf_scale(combo_nf, Fraction(-1)))
        raise ValueError(f"ordinary combo identity failed; diff monomials={len(diff)}")

    chunks = bucket_chunks(target_nf, combo_nf, args.chunk_size)
    combo_chunks, combo_left_nf = combo_order_chunks(raw_combo_terms, args.chunk_size)
    if combo_left_nf != target_nf:
        diff = nf_add(target_nf, nf_scale(combo_left_nf, Fraction(-1)))
        raise ValueError(f"combo-order left chunks do not collect to target; diff monomials={len(diff)}")
    return {
        "schema": "codex_o14_chunked_cone_export_v1",
        "slot": args.slot,
        "chart": int(row["chart"]),
        "dominant": int(row["dominant"]),
        "dominant_name": row["dominant_name"],
        "band": row["band"],
        "support": manifest["support"],
        "source_solution": row["solution_path"],
        "source_solution_sha256": row["solution_sha256"],
        "manifest": row["manifest"],
        "manifest_sha256": row["manifest_sha256"],
        "variables": [str(v) for v in prepared.chart.variables],
        "var_ids": {str(v): i for i, v in enumerate(prepared.chart.variables)},
        "target_degree": charts.TARGET_DEGREE,
        "target_terms": len(target_nf),
        "base_terms": len(base_nf),
        "combo_terms": len(combo_nf),
        "raw_combo_terms": len(raw_combo_terms),
        "nonzero_solution_columns": len(vals),
        "nonzero_residual_coeffs": sum(1 for x in residual if x),
        "chunks": chunks,
        "combo_order_chunks": combo_chunks,
        "base": nf_terms(base_nf),
        "mults": mults,
        "slacks": slacks,
        "checks": {
            "solution_nonnegative": True,
            "residual_nonnegative": True,
            "ordinary_identity": True,
            "chunk_count": len(chunks),
            "combo_order_chunk_count": len(combo_chunks),
            "chunk_size": args.chunk_size,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, default=Path("tmp/codex_o14_v108_ledger_inventory.json"))
    ap.add_argument("--slot", type=int, default=0)
    ap.add_argument("--chunk-size", type=int, default=64)
    ap.add_argument("--out", type=Path, default=Path("tmp/codex_o14_chart000_chunked_cone_export.json"))
    args = ap.parse_args()
    out = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "slot": out["slot"],
        "chart": out["chart"],
        "dominant": out["dominant"],
        "target_terms": out["target_terms"],
        "base_terms": out["base_terms"],
        "mults": len(out["mults"]),
        "chunks": len(out["chunks"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
