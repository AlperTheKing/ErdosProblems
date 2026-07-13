"""Exact replay of the corrected global-Hall descent on the real N=24 cage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GLOBAL = ROOT / "tmp/fanout/r53_global_softcap_gate"
R35 = ROOT / "tmp/fanout/r35_24_trade"
for path in (GLOBAL, R35):
    sys.path.insert(0, str(path))

import evaluate_trade as fixture
from global_softcap import analyze_global, make_graph_context


PATH = (
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 31, 44),
    (0, 0, 0, 0, 0, 0, 0, 0, 3, 15, 31, 44),
    (0, 0, 0, 0, 0, 0, 0, 5, 3, 15, 31, 44),
)


def evaluate(state):
    rows = [
        fixture.ROW_FAMILIES[index][choice]
        for index, choice in enumerate(state)
    ]
    ctx = make_graph_context(fixture.N, fixture.BLUE, fixture.BAD)
    summary, _certificate = analyze_global(
        ctx, rows, enumerate_after_zero=True
    )
    return {
        "state": list(state),
        "globalCollisionHalfDemand": summary["state"][
            "globalCollisionHalfDemand"
        ],
        "defect": summary["minimumDefect"],
        "shore": summary["minCutSourceOwners"],
        "stages": [
            [stage["afterAdding"], stage["defect"]]
            for stage in summary["stages"]
        ],
    }


def main():
    records = [evaluate(state) for state in PATH]
    assert [record["globalCollisionHalfDemand"] for record in records] == [
        312,
        284,
        256,
    ]
    assert [record["defect"] for record in records] == [24, 8, 0]
    assert sum(left != right for left, right in zip(PATH[0], PATH[1])) == 1
    assert sum(left != right for left, right in zip(PATH[1], PATH[2])) == 1
    payload = {
        "schema": "R53_N24_GLOBAL_MIN_COLLISION_DESCENT_V1",
        "arithmetic": "Python integers; integral grouped max flow",
        "relations": ["P1", "P2", "P3", "commonBlue", "P4", "P5"],
        "records": records,
        "verdict": "PASS_TWO_ONE_ROW_DESCENTS_TO_ZERO_DEFECT",
    }
    encoded = (
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    output = HERE / "n24_min_collision_descent.json"
    output.write_bytes(encoded)
    print(encoded.decode("ascii"), end="")
    print("sha256=" + hashlib.sha256(encoded).hexdigest())


if __name__ == "__main__":
    main()
