#!/usr/bin/env python3
"""Emit a stress-test shard of exact O14 sparse residual inequalities."""

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


def emit_shard(
    path: Path,
    namespace: str,
    selected: list[tuple[int, int]],
    prepared,
    terms_by_row: dict[int, list[tuple[int, Fraction]]],
) -> dict[str, int | str]:
    lines = [
        "import Erdos23Delta0.O14.CompactPilot.Chart000Weights",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        f"namespace {namespace}",
        "",
        "open Chart000Weights",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
    ]
    for global_index, beta_row in selected:
        target = prepared.p_beta[beta_row]
        terms = terms_by_row[beta_row]
        weighted = " + ".join(
            f"weight{weight_id:04d} * {qlean(coeff)}"
            for weight_id, coeff in terms
        ) or "(0 : Rat)"
        unfolds = ", ".join(f"weight{weight_id:04d}" for weight_id, _ in terms)
        lines.append(f"theorem residual{global_index:04d}_nonneg :")
        lines.append(f"    0 <= {qlean(target)} - ({weighted}) := by")
        if unfolds:
            lines.append(f"  norm_num [{unfolds}]")
        else:
            lines.append("  norm_num")
        lines.append("")
    lines.extend([
        f"end {namespace}",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
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
    parser.add_argument("--count", type=int, default=64)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--all-dir", type=Path)
    parser.add_argument("--chunk-size", type=int, default=64)
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    row = next(rec for rec in inventory["rows"] if int(rec["slot"]) == args.slot)
    manifest = json.loads(Path(row["manifest"]).read_text(encoding="utf-8"))
    prepared, columns, _matrix, _rhs = probe.build_lp(
        int(row["chart"]), int(row["dominant"]), row["band"], manifest["support"]
    )
    solution = read_solution(Path(row["solution_path"]))
    weight_index = {source_col: index for index, (source_col, _q) in enumerate(solution)}

    terms_by_row: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    active = {index for index, q in enumerate(prepared.p_beta) if q}
    for source_col, _weight in solution:
        for beta_row, coeff in columns[source_col].terms:
            terms_by_row[beta_row].append((weight_index[source_col], coeff))
            active.add(beta_row)

    ranked = sorted(active, key=lambda r: (-len(terms_by_row[r]), r))
    indexed = list(enumerate(ranked))
    if args.all_dir is not None:
        records = []
        for shard, start in enumerate(range(0, len(indexed), args.chunk_size)):
            selected = indexed[start : start + args.chunk_size]
            records.append(emit_shard(
                args.all_dir / f"Chart000Residual{shard:03d}.lean",
                f"Chart000Residual{shard:03d}",
                selected,
                prepared,
                terms_by_row,
            ))
        print(json.dumps({
            "out_dir": str(args.all_dir),
            "shards": len(records),
            "rows": sum(int(rec["rows"]) for rec in records),
            "term_occurrences": sum(int(rec["term_occurrences"]) for rec in records),
            "bytes": sum(int(rec["bytes"]) for rec in records),
        }, sort_keys=True))
    else:
        if args.out is None:
            raise SystemExit("--out or --all-dir is required")
        selected = indexed[args.offset : args.offset + args.count]
        print(json.dumps(emit_shard(
            args.out,
            "Chart000ResidualPilot",
            selected,
            prepared,
            terms_by_row,
        ), sort_keys=True))


if __name__ == "__main__":
    main()
