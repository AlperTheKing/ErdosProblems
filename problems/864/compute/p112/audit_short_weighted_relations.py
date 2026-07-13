#!/usr/bin/env python3
"""Exact broad audit of short weighted loose-triangle relation matrices."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p46 = load("p46_p112", ROOT / "problems/864/compute/p46/carry_statistics.py")
p103 = load("p103_p112", ROOT / "problems/864/compute/p103/audit_relation_matroid.py")
w103 = load("w103_p112", ROOT / "problems/864/compute/p103/audit_weighted_relations.py")


def audit_row(B: tuple[int, ...], h: int, b: int) -> dict[str, int]:
    folds, triangles, full_rows = w103.relation_rows(B, h, b)
    C = len(folds)
    p = len(B)
    short_rows = [
        {
            column: value
            for column, value in row.items()
            if column < C + p or C + 2 * p <= column < C + 3 * p
        }
        for row in full_rows
    ]
    role_x_rows = []
    for f0, fz, fx in triangles:
        phase = folds[f0][0] + folds[f0][1] + b
        role_x_rows.append({
            f0: 1,
            C + fz: 1,
            2 * C + fx: 1,
            3 * C + fx: phase,
        })
    return {
        "C_S": C,
        "T_F": len(triangles),
        "short_rank": w103.sparse_rank(short_rows),
        "role_x_rank": w103.sparse_rank(role_x_rows),
    }


def empty_summary() -> dict[str, object]:
    return {
        "rows": 0,
        "triangle_rows": 0,
        "short_failures": 0,
        "role_x_failures": 0,
        "first_short_failure": None,
        "first_role_x_failure": None,
    }


def consume(summary: dict[str, object], B: tuple[int, ...], h: int, b: int, witness: dict[str, object]) -> None:
    summary["rows"] += 1
    row = audit_row(B, h, b)
    if not row["T_F"]:
        return
    summary["triangle_rows"] += 1
    if row["short_rank"] < row["T_F"]:
        summary["short_failures"] += 1
        if summary["first_short_failure"] is None:
            summary["first_short_failure"] = {**witness, **row, "B": B, "h": h, "b": b}
    if row["role_x_rank"] < row["T_F"]:
        summary["role_x_failures"] += 1
        if summary["first_role_x_failure"] is None:
            summary["first_role_x_failure"] = {**witness, **row, "B": B, "h": h, "b": b}


def scan_width(max_width: int) -> dict[str, object]:
    summary = empty_summary()
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            reflected = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                B = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    consume(summary, B, h, b, {"width": width, "gamma": gamma})
    return summary


def scan_p88() -> dict[str, object]:
    summary = empty_summary()
    for gamma in range(2085):
        B = tuple(x + gamma for x in p103.P88)
        h = 3286 + gamma
        consume(summary, B, h, 1, {"gamma": gamma, "source": "P88"})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "field": f"GF({w103.PRIME})",
        "short_matrix": "S,L1,dL1 in C_S+2p columns",
        "role_x_matrix": "role-separated incidence plus d times X-role incidence in 4C_S columns",
        "width_scan": scan_width(args.max_width),
        "P88_scan": scan_p88(),
    }
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
