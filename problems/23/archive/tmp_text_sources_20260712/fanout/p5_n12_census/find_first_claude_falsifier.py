"""Find the first one-copy P1/P3/P5 falsifier in deterministic census order."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
sys.path.insert(0, str(WRITEUP))
sys.path.insert(0, str(PHT))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from p5_core import analyze_rows, make_graph_context  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    graph6, generated = graph6_for_orders(10, 10)
    assert generated == {10: 9832}
    first = None
    failures = 0
    examined_tuples = 0
    for graph_ordinal, g6 in enumerate(graph6):
        n, edges = dec(g6)
        info = loads(n, edges)
        if info is None or any(length != 5 for length in info["ell"].values()):
            continue
        families = shortest_row_families(info)
        sizes = tuple(map(len, families))
        ctx = make_graph_context(n, info["Bset"], info["Mset"])
        for tuple_index, choice in enumerate(itertools.product(*(range(s) for s in sizes))):
            examined_tuples += 1
            rows = rows_for_choice(families, choice)
            analysis = analyze_rows(ctx, rows, details=first is None)
            if analysis["oneClaudeAfter"]["full"]:
                continue
            failures += 1
            if first is None:
                first = {
                    "order": n,
                    "graphOrdinal": graph_ordinal,
                    "g6": g6,
                    "familySizes": list(sizes),
                    "tupleIndex": tuple_index,
                    "choice": list(choice),
                    "rows": [list(row) for row in rows],
                    "gamma": info["G"],
                    "activeVertices": analysis["state"]["activeVertices"],
                    "collisionDemand": analysis["collisionDemand"],
                    "hitNeedSlots": analysis["hitNeedSlots"],
                    "oneDemand": analysis["oneDemand"],
                    "p5Stats": analysis["p5Stats"],
                    "p5Sources": analysis["p5Sources"],
                    "oneClaudeBefore": analysis["oneClaudeBefore"],
                    "oneClaudeAfter": analysis["oneClaudeAfter"],
                    "oneFive": analysis["oneFive"],
                }
    assert examined_tuples == 47_030
    assert failures == 192
    assert first is not None
    first["recordSha256"] = canonical_sha(first)
    result = {
        "schema": "P5_FIRST_CLAUDE_RELATION_FALSIFIER_V1",
        "relation": "one-copy P1/P3/P5; excludes P2 and P4",
        "order10ExaminedTuples": examined_tuples,
        "order10Failures": failures,
        "first": first,
        "sha256": {
            "p5Core": sha256(HERE / "p5_core.py"),
            "script": sha256(Path(__file__)),
        },
    }
    result["canonicalPayloadSha256"] = canonical_sha(result)
    output = HERE / "first_claude_relation_falsifier.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "canonicalPayloadSha256": result["canonicalPayloadSha256"],
        "first": first,
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
