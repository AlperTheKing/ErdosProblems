"""Replay the first tuple/minimizer record from a collision census output."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
P5_DIR = HERE.parent / "p5_n12_census"
for path in (WRITEUP, PHT, P5_DIR, HERE):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from collision_only_core import analyze_collision_only, canonical_sha  # noqa: E402
from p5_core import make_graph_context  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("census", type=Path)
    parser.add_argument(
        "--key",
        choices=(
            "firstTupleFalsifier",
            "firstDefectMinimizerFalsifier",
            "firstAllTupleFalsifier",
        ),
        default="firstTupleFalsifier",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    census = json.loads(args.census.read_text(encoding="ascii"))
    record = census["total"]["first"][args.key]
    if record is None:
        payload = {
            "schema": "R32_NO_COMMON_COLLISION_REPLAY_V1",
            "verdict": "NO_RECORD_TO_REPLAY",
            "key": args.key,
            "censusSha256": sha256(args.census),
        }
        payload["canonicalPayloadSha256"] = canonical_sha(payload)
        args.output.write_text(
            json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
        )
        print(json.dumps(payload, sort_keys=True))
        return 0

    g6 = record["g6"]
    choice = tuple(record["choice"])
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        raise AssertionError("recorded graph lost its canonical cut")
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    if math.prod(sizes) != record["tupleCount"]:
        raise AssertionError("tuple count changed")
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    rows = rows_for_choice(families, choice)
    analysis = analyze_collision_only(ctx, rows, details=True)
    for key in (
        "collisionDemand",
        "collisionMatched",
        "collisionDefect",
        "hitNeedSlotsSeparate",
    ):
        if analysis[key] != record[key]:
            raise AssertionError((key, analysis[key], record[key]))

    best = None
    for tuple_index, candidate_choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        candidate_rows = rows_for_choice(families, candidate_choice)
        candidate = analyze_collision_only(ctx, candidate_rows)
        rank = (candidate["collisionDefect"], tuple_index)
        if best is None or rank < best[0]:
            best = (rank, candidate_choice, candidate)
    if best is None:
        raise AssertionError("no tuple")

    payload = {
        "schema": "R32_NO_COMMON_COLLISION_REPLAY_V1",
        "verdict": (
            "EXACT_TUPLE_FALSIFIER_BUT_GRAPH_MINIMUM_ZERO"
            if analysis["collisionDefect"] > 0 and best[0][0] == 0
            else "EXACT_REPLAY"
        ),
        "relation": ["P1_sameFirst", "P3_rowCompanion", "strictP4", "P5"],
        "commonBlue": False,
        "hallDemandIncludesHitNeed": False,
        "g6": g6,
        "order": n,
        "graphEdges": [list(edge) for edge in sorted(edges)],
        "blue": [list(edge) for edge in sorted(info["Bset"])],
        "bad": [list(edge) for edge in sorted(info["Mset"])],
        "gamma": info["G"],
        "familySizes": list(sizes),
        "failingTuple": {
            "tupleIndex": record["tupleIndex"],
            "choice": list(choice),
            "analysis": analysis,
        },
        "defectMinimum": {
            "defect": best[0][0],
            "tupleIndex": best[0][1],
            "choice": list(best[1]),
            "collisionDemand": best[2]["collisionDemand"],
            "collisionMatched": best[2]["collisionMatched"],
            "hitNeedSlotsSeparate": best[2]["hitNeedSlotsSeparate"],
        },
        "sha256": {
            "census": sha256(args.census),
            "collisionCore": sha256(HERE / "collision_only_core.py"),
            "fullbankCore": sha256(HERE / "fullbank_core.py"),
            "p5Core": sha256(P5_DIR / "p5_core.py"),
            "replay": sha256(Path(__file__)),
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "verdict": payload["verdict"],
                "g6": g6,
                "failingChoice": list(choice),
                "failingDefect": analysis["collisionDefect"],
                "witness": analysis["hallWitness"],
                "minimumDefect": best[0][0],
                "minimumChoice": list(best[1]),
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

