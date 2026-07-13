#!/usr/bin/env python3
"""Exact dependency audit for the R56 two-prefix state-erasure question.

This gate has deliberately narrow coverage.  It verifies that the existing
15-pair selected-detour cut witnesses are computed from the fixed graph and
candidate branch windows only, and replays every reported negative mask.  It
does not assert that an arbitrary R55 protection branch exports one of these
fixed payloads.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXCHANGE = ROOT / "tmp" / "fanout" / "cdc_wave1" / "exchange"
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (EXCHANGE, SOFTCAP):
    sys.path.insert(0, str(path))

import global_softcap as soft  # noqa: E402
from unit_detour_core_gate import build_graph, edge  # noqa: E402


CLOSURE = EXCHANGE / "selected_detour_closure_gate.py"
REPAIR = EXCHANGE / "selected_detour_repair_gate.py"

EXPECTED = {
    (0, 1): (65, (0, 6)),
    (0, 2): (193, (0, 6, 7)),
    (0, 3): (1, (0,)),
    (0, 4): (2049, (0, 11)),
    (0, 5): (1592, (3, 4, 5, 9, 10)),
    (1, 2): (193, (0, 6, 7)),
    (1, 3): (65, (0, 6)),
    (1, 4): (2113, (0, 6, 11)),
    (1, 5): (1080, (3, 4, 5, 10)),
    (2, 3): (193, (0, 6, 7)),
    (2, 4): (2241, (0, 6, 7, 11)),
    (2, 5): (56, (3, 4, 5)),
    (3, 4): (2049, (0, 11)),
    (3, 5): (6145, (0, 11, 12)),
    (4, 5): (6145, (0, 11, 12)),
}

BANNED_STATE_NAMES = {
    "RowChoice",
    "selectedSupport",
    "selected_support",
    "pairCount",
    "pair_count",
    "omega",
    "rows",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def function_ast(path: Path, name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError((path, name))


def names_in(node: ast.AST) -> set[str]:
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def attributes_in(node: ast.AST) -> set[str]:
    return {
        item.attr for item in ast.walk(node) if isinstance(item, ast.Attribute)
    }


def selected_vertices(mask: int, n: int) -> tuple[int, ...]:
    return tuple(v for v in range(n) if mask & (1 << v))


def replay_catalogue() -> list[dict]:
    n, blue, base_bad, protection = build_graph(6)
    windows = tuple(
        edge(path[i], path[i + 4])
        for path in protection
        for i in range(len(path) - 4)
    )
    if len(windows) != 6 or len(set(windows)) != 6:
        raise AssertionError(windows)
    records = []
    for pair in combinations(range(len(windows)), 2):
        bad = frozenset(set(base_bad) | {windows[pair[0]], windows[pair[1]]})
        ctx = soft.make_graph_context(n, blue, bad)
        values = tuple(ctx.sigma(mask) for mask in range(1 << (n - 1)))
        minimum = min(values)
        first_mask = values.index(minimum)
        expected_mask, expected_vertices = EXPECTED[pair]
        if minimum != -1:
            raise AssertionError((pair, minimum))
        if first_mask != expected_mask:
            raise AssertionError((pair, first_mask, expected_mask))
        actual_vertices = selected_vertices(first_mask, n)
        if actual_vertices != expected_vertices:
            raise AssertionError((pair, actual_vertices, expected_vertices))
        records.append(
            {
                "pair": pair,
                "minimumSigma": minimum,
                "firstMinimumMask": first_mask,
                "selectedVertices": actual_vertices,
                "numberOfMinimumMasks": sum(value == minimum for value in values),
            }
        )
    return records


def main() -> int:
    minimum_sigma_ast = function_ast(CLOSURE, "minimum_sigma")
    cut_names = names_in(minimum_sigma_ast) | attributes_in(minimum_sigma_ast)
    forbidden = sorted(cut_names & BANNED_STATE_NAMES)
    if forbidden:
        raise AssertionError(forbidden)

    repair_main = function_ast(REPAIR, "main")
    repair_source = ast.get_source_segment(
        REPAIR.read_text(encoding="utf-8"), repair_main
    )
    if repair_source is None:
        raise AssertionError("repair main source unavailable")
    graph_only_formula = (
        "ctx.sigma(mask) < 0" in repair_source
        and "all(crosses(mask, item) for mask in negative_masks)"
        in repair_source
    )
    if not graph_only_formula:
        raise AssertionError("repair cut formula changed")

    records = replay_catalogue()
    payload = {
        "schema": "R56_SELECTED_DETOUR_STATE_ERASURE_AUDIT_V1",
        "scope": "fixed six-window unit-detour catalogue only",
        "outcome": "GRAPH_ONLY_FOR_EXISTING_CATALOGUE",
        "universalExtractionProved": False,
        "minimumSigmaAstNames": sorted(cut_names),
        "forbiddenStateNames": forbidden,
        "repairFormulaGraphOnly": graph_only_formula,
        "cataloguePairs": len(records),
        "allPairsMinimumSigmaMinusOne": all(
            record["minimumSigma"] == -1 for record in records
        ),
        "records": records,
        "sources": {
            str(CLOSURE.relative_to(ROOT)): sha256(CLOSURE),
            str(REPAIR.relative_to(ROOT)): sha256(REPAIR),
        },
    }
    output = HERE / "result.json"
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
