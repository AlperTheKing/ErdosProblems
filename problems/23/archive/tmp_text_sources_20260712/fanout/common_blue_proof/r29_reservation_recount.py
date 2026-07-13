"""Exact R29 old-pool deduction comparison: common-blue versus Pattern 5."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
PATTERN5 = ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(x, y):
    return (x, y) if x < y else (y, x)


def main():
    lead = load("r29_recount_lead", LEAD)
    p5 = load("r29_recount_p5", PATTERN5)
    data = lead.build()
    rows = [tuple(row) for row in data["rows"]]
    start = data["selectorStart"]
    for index in range(676):
        rows[start + index] = tuple(data["selectorMeta"][index]["anchorRow"])
    state = p5.full_state(data, tuple(rows))
    pair = state["pair"]
    old_keys = set(state["masks"])

    common_blue_pairs = [(x, 2930) for x in range(29, 43)]
    common_blue_new = [(x, y, half) for x, y in common_blue_pairs for half in (0, 1)]
    assert len(common_blue_new) == 28
    assert all(key not in old_keys for key in common_blue_new)
    assert all(pair[x, 2930] == 0 for x in range(29, 43))
    assert all(pair[2, x] == 26 for x in range(29, 43))
    assert pair[2, 2930] == 0
    reserved_edges = {norm(x, 2) for x in range(29, 43)} | {norm(2930, 2)}
    deducted_old = sorted(
        key for key in old_keys if norm(key[0], key[1]) in reserved_edges
    )
    assert deducted_old == [(2, 2930, 1)]
    common_blue_net = len(common_blue_new) - len(deducted_old)
    assert common_blue_net == 27

    pattern5_x = [56 + 2 * index for index in range(14)]
    pattern5_new = [(3, x, half) for x in pattern5_x for half in (0, 1)]
    assert len(pattern5_new) == 28
    assert all(key not in old_keys for key in pattern5_new)
    assert all(pair[3, x] == 0 for x in pattern5_x)
    pattern5_reserved_edges = set()
    pattern5_deducted_old = []
    pattern5_net = len(pattern5_new) - len(pattern5_deducted_old)
    assert pattern5_net == 28

    p5_record = p5.p5_at(data, tuple(rows), verbose=False)
    assert p5_record["K"] == 1379
    assert p5_record["boundary"] == [1, 55]
    assert p5_record["loss"] == 26
    assert p5_record["full_gap"] == 0
    assert all(p5_record["elig"].values())
    owner_components = {str(owner): state["comp"][owner] for owner in (0, 1, 2)}
    assert len(set(owner_components.values())) == 1

    result = {
        "schema": "R29_RESERVATION_DEDUCTION_COMPARISON_V1",
        "commonBluePostedFamily": {
            "basePairs": len(common_blue_pairs),
            "newHalfKeys": len(common_blue_new),
            "reservedEdgeUnion": [list(edge) for edge in sorted(reserved_edges)],
            "deductedOldKeys": [list(key) for key in deducted_old],
            "net": common_blue_net,
            "closesDefect28": False,
            "idempotenceAssumed": False,
        },
        "pattern5": {
            "basePairs": 14,
            "newHalfKeys": len(pattern5_new),
            "reservedEdgeUnion": [],
            "deductedOldKeys": pattern5_deducted_old,
            "net": pattern5_net,
            "closesDefect28": True,
            "quiescentComponentSize": p5_record["K"],
            "boundary": p5_record["boundary"],
            "switchLoss": p5_record["loss"],
            "ownerComponents": owner_components,
            "componentPreservingStatus": "fixture passes; universal adapter remains an explicit hypothesis",
        },
        "sourceSha256": {
            "lead": sha256(LEAD),
            "pattern5Gate": sha256(PATTERN5),
            "recount": sha256(Path(__file__)),
        },
    }
    output = HERE / "r29_reservation_recount_result.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commonBlueNet": common_blue_net,
        "pattern5Net": pattern5_net,
        "deductedOldKeys": deducted_old,
        "resultSha256": sha256(output),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
