#!/usr/bin/env python3
"""Exact replay checker for saved EQ-ODL1 Farkas certificates.

A saved certificate proves infeasibility of the selected finite LP support when
it contains y >= 0 such that A^T y >= 0 and b^T y < 0 for the model
A x <= b, x >= 0.  All arithmetic here is Fraction arithmetic.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_shifted_lp as eq
import _codex_eq_odl1_clarabel_lp as clp


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def check(path: Path) -> dict[str, object]:
    cert = json.loads(path.read_text(encoding="utf-8"))
    target_expr, _ = eq.build_target()
    generators = eq.build_generators()
    cols = clp.select_columns(
        target_expr,
        generators,
        cert.get("mode", "negative"),
        cert.get("diagnostic", "tmp/eq_odl1_support_diagnose_v2.json"),
        cert.get("selected_generators", ""),
    )
    target, col_maps, monoms, row_index = clp.exact_maps(target_expr, generators, cols)
    y_raw = cert.get("farkas_exact_check", {}).get("certificate_y")
    if y_raw is None:
        raise ValueError("missing farkas_exact_check.certificate_y")
    y = [parse_fraction(s) for s in y_raw]
    if len(y) != len(monoms):
        raise ValueError(f"certificate length {len(y)} != monomial constraints {len(monoms)}")

    min_y = min(y) if y else Fraction(0)
    bty = sum(target.get(exp, Fraction(0)) * y[i] for i, exp in enumerate(monoms))
    min_aty = None
    negative = []
    zero_cols = 0
    for j, cmap in enumerate(col_maps):
        acc = sum(coeff * y[row_index[exp]] for exp, coeff in cmap.items())
        if min_aty is None or acc < min_aty:
            min_aty = acc
        if acc < 0 and len(negative) < 20:
            negative.append({"column": j, "value": str(acc)})
        if acc == 0:
            zero_cols += 1
    ok = min_y >= 0 and not negative and bty < 0
    return {
        "schema": "eq_odl1_farkas_cert_check_v1",
        "certificate": str(path),
        "ok": ok,
        "mode": cert.get("mode"),
        "selected_generators": cert.get("selected_generators"),
        "variables": len(cols),
        "constraints": len(monoms),
        "min_y": str(min_y),
        "bty": str(bty),
        "min_ATy": str(min_aty if min_aty is not None else Fraction(0)),
        "negative_ATy_count_at_least": len(negative),
        "negative_ATy_first": negative,
        "zero_ATy_count": zero_cols,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate", type=Path)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_farkas_cert_check_v1.json"))
    args = ap.parse_args()
    result = check(args.certificate)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["ok", "variables", "constraints", "bty", "min_ATy"]}, sort_keys=True))


if __name__ == "__main__":
    main()
