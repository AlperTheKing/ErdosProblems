#!/usr/bin/env python3
"""Emit compact Chart000 sparse rows checked by kernel reduction."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def qlean(q: Fraction) -> str:
    if q.denominator == 1:
        return f"({q.numerator} : Rat)"
    return f"(({q.numerator} : Rat) / ({q.denominator} : Rat))"


def read_solution(path: Path) -> list[tuple[int, Fraction]]:
    rows: list[tuple[int, Fraction]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rec = json.loads(line)
            rows.append((
                int(rec["source_col"]),
                Fraction(int(rec["num"]), int(rec["den"])),
            ))
    rows.sort()
    return rows


def emit_weights(path: Path, count: int) -> dict[str, int | str]:
    weight_refs = ",\n  ".join(f"weight{i:04d}" for i in range(count))
    text = "\n".join([
        "import Erdos23Delta0.O14.SparseConePacked",
        "import Erdos23Delta0.O14.CompactPilot.Chart000Weights",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        "namespace Chart000PackedWeights",
        "",
        "open Chart000Weights",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
        "def weights : Array Rat := #[",
        f"  {weight_refs}",
        "]",
        "",
        "theorem weights_size : weights.size = Chart000Weights.count := by rfl",
        "",
        "end Chart000PackedWeights",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"out": str(path), "weights": count, "bytes": path.stat().st_size}


def term_lean(weight_id: int, coeff: Fraction) -> str:
    return (
        "{ weightId := " + str(weight_id)
        + ", coeff := " + qlean(coeff) + " }"
    )


def row_lean(target: Fraction, terms: list[tuple[int, Fraction]]) -> str:
    term_text = ", ".join(term_lean(weight_id, coeff) for weight_id, coeff in terms)
    return (
        "{ target := " + qlean(target)
        + ", terms := [" + term_text + "] }"
    )


def emit_shard(
    path: Path,
    namespace: str,
    selected: list[tuple[int, int]],
    prepared,
    terms_by_row: dict[int, list[tuple[int, Fraction]]],
) -> dict[str, int | str]:
    rows = ",\n  ".join(
        row_lean(prepared.p_beta[beta_row], terms_by_row[beta_row])
        for _global_index, beta_row in selected
    )
    text = "\n".join([
        "import Erdos23Delta0.O14.CompactPilot.Chart000PackedWeights",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        f"namespace {namespace}",
        "",
        "open SparseConePacked",
        "open Chart000PackedWeights",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
        "def rows : List Row := [",
        f"  {rows}",
        "]",
        "",
        "theorem rows_checked : checkRows weights rows = true := by decide",
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
        "max_terms": max((len(terms_by_row[r]) for _, r in selected), default=0),
        "term_occurrences": sum(len(terms_by_row[r]) for _, r in selected),
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
    records.append(emit_weights(args.out_dir / "Chart000PackedWeights.lean", len(solution)))
    for shard, start in enumerate(range(0, len(indexed), args.chunk_size)):
        selected = indexed[start : start + args.chunk_size]
        records.append(emit_shard(
            args.out_dir / f"Chart000PackedRows{shard:03d}.lean",
            f"Chart000PackedRows{shard:03d}",
            selected,
            prepared,
            terms_by_row,
        ))

    print(json.dumps({
        "out_dir": str(args.out_dir),
        "files": len(records),
        "rows": len(indexed),
        "term_occurrences": sum(int(rec.get("term_occurrences", 0)) for rec in records),
        "bytes": sum(int(rec["bytes"]) for rec in records),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
