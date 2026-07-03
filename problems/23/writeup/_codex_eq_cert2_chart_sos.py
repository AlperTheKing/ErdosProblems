#!/usr/bin/env python3
"""CERT-2 charted SOS prototype/size estimator.

This is a search/prototyping helper, not a certificate emitter.  It builds the
formal degree-12 chart target P_hat*(s+sum z) and reports dense vs sparse SOS
basis sizes for chart 0.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp

DIM = lp.SX_DIM
DEG11 = lp.TARGET_DEGREE
DEG12 = 12
SOS_DEG = 6


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


def mul_linear(poly: dict[tuple[int, ...], Fraction]) -> dict[tuple[int, ...], Fraction]:
    out: dict[tuple[int, ...], Fraction] = {}
    units = []
    for i in range(DIM):
        e = [0] * DIM
        e[i] = 1
        units.append(tuple(e))
    for exp, coeff in poly.items():
        for unit in units:
            key = add_exp(exp, unit)
            out[key] = out.get(key, Fraction(0)) + coeff
    return {k: v for k, v in out.items() if v}


def dense_sos_basis() -> list[tuple[int, ...]]:
    seed = (SOS_DEG,) + (0,) * (DIM - 1)
    return [e for e in weak_compositions(SOS_DEG, DIM) if e != seed]


def rows12_from_seed(seed_path: str | None, target12: dict[tuple[int, ...], Fraction]) -> set[tuple[int, ...]]:
    if not seed_path:
        return {exp for exp, coeff in target12.items() if coeff < 0}
    data = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    rows11 = data.get("rows") or data.get("active_rows")
    if rows11 is None:
        raise ValueError("seed row file must contain rows or active_rows")
    out: set[tuple[int, ...]] = set()
    units = []
    for i in range(DIM):
        e = [0] * DIM
        e[i] = 1
        units.append(tuple(e))
    for row in rows11:
        row_t = tuple(int(v) for v in row)
        for unit in units:
            out.add(add_exp(row_t, unit))
    return out


def sparse_basis_for_rows(rows: set[tuple[int, ...]]) -> tuple[list[tuple[int, ...]], int]:
    basis: set[tuple[int, ...]] = set()
    pair_count = 0
    all_deg6 = list(weak_compositions(SOS_DEG, DIM))
    seed = (SOS_DEG,) + (0,) * (DIM - 1)
    for row in rows:
        for beta in all_deg6:
            gamma = sub_exp(row, beta)
            if gamma is None or sum(gamma) != SOS_DEG:
                continue
            if beta == seed or gamma == seed:
                continue
            basis.add(beta)
            basis.add(gamma)
            if beta <= gamma:
                pair_count += 1
    return sorted(basis), pair_count


def estimate_pair_rows(basis: list[tuple[int, ...]]) -> tuple[int, int]:
    rows = set()
    pairs = 0
    for i, a in enumerate(basis):
        for b in basis[i:]:
            rows.add(add_exp(a, b))
            pairs += 1
    return pairs, len(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--seed-rows", default="")
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_size_v1.json")
    args = ap.parse_args()

    target11, generators, meta = lp.build_chart(args.chart)
    target12 = mul_linear(target11)
    dense_basis = dense_sos_basis()
    rows = rows12_from_seed(args.seed_rows or None, target12)
    sparse_basis, active_pairs = sparse_basis_for_rows(rows)
    dense_n = len(dense_basis)
    sparse_pair_total, sparse_rows_total = estimate_pair_rows(sparse_basis)
    out = {
        "schema": "eq_cert2_chart_sos_size_v1",
        "chart": args.chart,
        "target11_terms": len(target11),
        "target12_terms": len(target12),
        "target12_negative_terms": sum(1 for c in target12.values() if c < 0),
        "generator_count": len(generators),
        "dense_homogeneous_degree6_basis_no_seed": dense_n,
        "dense_psd_triangle_entries": dense_n * (dense_n + 1) // 2,
        "rows12_from_seed": len(rows),
        "sparse_basis_from_rows": len(sparse_basis),
        "sparse_active_pairs_on_rows": active_pairs,
        "sparse_full_pair_entries": sparse_pair_total,
        "sparse_full_pair_rows": sparse_rows_total,
        "seed_rows": args.seed_rows,
        "meta": meta,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in out if k != "meta"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
