#!/usr/bin/env python3
"""Emit Chart000 residual rows as one-denominator integer arithmetic."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def read_solution(path: Path) -> list[tuple[int, Fraction]]:
    records: list[tuple[int, Fraction]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append((
                int(rec["source_col"]),
                Fraction(int(rec["num"]), int(rec["den"])),
            ))
    records.sort()
    return records


def intlean(value: int) -> str:
    return f"({value} : Int)"


def natlean(value: int) -> str:
    if value < 0:
        raise ValueError("negative Nat literal")
    return f"({value} : Nat)"


def emit_weights(
    path: Path,
    denom: int,
    scaled_weights: list[int],
) -> dict[str, int | str]:
    values = ",\n  ".join(natlean(value) for value in scaled_weights)
    text = "\n".join([
        "import Erdos23Delta0.O14.SparseConeScaledNat",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        "namespace Chart000ScaledWeights",
        "",
        "open SparseConeScaledNat",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
        f"def weightDenom : Nat := {denom}",
        "",
        "def weights : Array Nat := #[",
        f"  {values}",
        "]",
        "",
        "theorem weightDenom_pos : 0 < weightDenom := by norm_num [weightDenom]",
        "",
        "end Chart000ScaledWeights",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {
        "out": str(path),
        "weights": len(scaled_weights),
        "denom_bits": denom.bit_length(),
        "max_weight_bits": max((abs(value).bit_length() for value in scaled_weights), default=0),
        "bytes": path.stat().st_size,
    }


def scale_row(
    target: Fraction,
    terms: list[tuple[int, Fraction]],
    weight_denom: int,
    scaled_weights: list[int],
) -> tuple[int, int, list[tuple[int, int]], int]:
    scale = target.denominator
    for _weight_id, coeff in terms:
        scale = math.lcm(scale, coeff.denominator)

    target_scaled_q = target * weight_denom * scale
    if target_scaled_q.denominator != 1:
        raise AssertionError("target did not integer-scale")
    target_scaled = target_scaled_q.numerator

    scaled_terms: list[tuple[int, int]] = []
    weighted_total = 0
    for weight_id, coeff in terms:
        coeff_scaled_q = coeff * scale
        if coeff_scaled_q.denominator != 1:
            raise AssertionError("coefficient did not integer-scale")
        coeff_scaled = coeff_scaled_q.numerator
        scaled_terms.append((weight_id, coeff_scaled))
        weighted_total += scaled_weights[weight_id] * coeff_scaled

    residual = target_scaled - weighted_total
    if residual < 0:
        raise AssertionError(f"negative scaled residual: {residual}")
    return scale, target_scaled, scaled_terms, residual


def term_lean(weight_id: int, coeff: int) -> str:
    return f"{{ weightId := {weight_id}, coeff := {intlean(coeff)} }}"


def row_lean(scale: int, target: int, terms: list[tuple[int, int]]) -> str:
    term_text = ", ".join(term_lean(weight_id, coeff) for weight_id, coeff in terms)
    return (
        f"{{ scalePred := {scale - 1}, target := {intlean(target)}, "
        f"terms := [{term_text}] }}"
    )


def emit_shard(
    path: Path,
    namespace: str,
    selected: list[tuple[int, int]],
    prepared,
    terms_by_row: dict[int, list[tuple[int, Fraction]]],
    weight_denom: int,
    scaled_weights: list[int],
) -> dict[str, int | str]:
    scaled_rows = [
        scale_row(
            prepared.p_beta[beta_row],
            terms_by_row[beta_row],
            weight_denom,
            scaled_weights,
        )
        for _global_index, beta_row in selected
    ]
    rows = ",\n  ".join(
        row_lean(scale, target, terms)
        for scale, target, terms, _residual in scaled_rows
    )
    text = "\n".join([
        "import Erdos23Delta0.O14.CompactPilot.Chart000ScaledWeights",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        f"namespace {namespace}",
        "",
        "open SparseConeScaledNat",
        "open Chart000ScaledWeights",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
        "def rows : List Row := [",
        f"  {rows}",
        "]",
        "",
        "theorem rows_checked : checkRows weights rows = true := by rfl",
        "",
        f"end {namespace}",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {
        "out": str(path),
        "rows": len(selected),
        "max_terms": max((len(terms) for _scale, _target, terms, _residual in scaled_rows), default=0),
        "term_occurrences": sum(len(terms) for _scale, _target, terms, _residual in scaled_rows),
        "max_residual_bits": max((residual.bit_length() for _scale, _target, _terms, residual in scaled_rows), default=0),
        "bytes": path.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=Path("tmp/codex_o14_v108_ledger_inventory.json"))
    parser.add_argument("--slot", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=64)
    parser.add_argument("--count", type=int)
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    chart = next(rec for rec in inventory["rows"] if int(rec["slot"]) == args.slot)
    manifest = json.loads(Path(chart["manifest"]).read_text(encoding="utf-8"))
    prepared, columns, _matrix, _rhs = probe.build_lp(
        int(chart["chart"]), int(chart["dominant"]), chart["band"], manifest["support"]
    )
    solution = read_solution(Path(chart["solution_path"]))
    weight_index = {source_col: index for index, (source_col, _q) in enumerate(solution)}

    weight_denom = 1
    for _source_col, weight in solution:
        weight_denom = math.lcm(weight_denom, weight.denominator)
    scaled_weights = []
    for _source_col, weight in solution:
        scaled = weight * weight_denom
        if scaled.denominator != 1:
            raise AssertionError("weight did not integer-scale")
        if scaled.numerator < 0:
            raise AssertionError("negative solution weight")
        scaled_weights.append(scaled.numerator)

    terms_by_row: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    active = {index for index, q in enumerate(prepared.p_beta) if q}
    for source_col, _weight in solution:
        for beta_row, coeff in columns[source_col].terms:
            terms_by_row[beta_row].append((weight_index[source_col], coeff))
            active.add(beta_row)

    ranked = sorted(active, key=lambda row: (-len(terms_by_row[row]), row))
    indexed = list(enumerate(ranked))
    if args.count is not None:
        indexed = indexed[:args.count]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, int | str]] = []
    records.append(emit_weights(
        args.out_dir / "Chart000ScaledWeights.lean",
        weight_denom,
        scaled_weights,
    ))
    for shard, start in enumerate(range(0, len(indexed), args.chunk_size)):
        selected = indexed[start : start + args.chunk_size]
        records.append(emit_shard(
            args.out_dir / f"Chart000ScaledRows{shard:03d}.lean",
            f"Chart000ScaledRows{shard:03d}",
            selected,
            prepared,
            terms_by_row,
            weight_denom,
            scaled_weights,
        ))

    print(json.dumps({
        "out_dir": str(args.out_dir),
        "files": len(records),
        "rows": len(indexed),
        "term_occurrences": sum(int(rec.get("term_occurrences", 0)) for rec in records),
        "bytes": sum(int(rec["bytes"]) for rec in records),
        "weight_denom_bits": weight_denom.bit_length(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
