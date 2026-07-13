"""Exact census check for a sufficient joint-trade score invariant.

Acceptance arithmetic is integral.  The theorem checked here is structural:
if a new tuple uses a subset of the old selected vertices, covers a superset
of old support edges, and weakly decreases row multiplicity and raw collision
demand at every newly active owner, then its active-scoped score cannot rise.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_scoped_variation_anatomy import scoped_state


def safe_support_expansion(old, new) -> bool:
    old_selected = {v for edge in old["support"] for v in edge}
    old_selected.update(v for v, count in enumerate(old["rowCount"]) if count)
    new_selected = {v for edge in new["support"] for v in edge}
    new_selected.update(v for v, count in enumerate(new["rowCount"]) if count)
    if not new_selected <= old_selected:
        return False
    if not old["support"] <= new["support"]:
        return False
    for v in new["activeVertices"]:
        if new["rowCount"][v] > old["rowCount"][v]:
            return False
        if new["rawCollision"][v] > old["rawCollision"][v]:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=8)
    parser.add_argument("--max-combinations", type=int, default=256)
    args = parser.parse_args()

    graph6, generated = graph6_for_orders(args.n_min, args.n_max)
    result = {
        "generatedByOrder": generated,
        "acceptedAllLengthFive": 0,
        "systemsEnumerated": 0,
        "systemsSkippedCombinationCap": 0,
        "tuples": 0,
        "orderedTuplePairs": 0,
        "safeSupportExpansions": 0,
        "scoreViolations": 0,
        "fullDeactivations": 0,
        "fullDeactivationStrictViolations": 0,
        "firstSafeWitness": None,
        "firstFullDeactivationWitness": None,
        "maxCombinations": args.max_combinations,
    }

    for g6 in graph6:
        n, edges = dec(g6)
        info = loads(n, edges)
        if info is None or any(length != 5 for length in info["ell"].values()):
            continue
        result["acceptedAllLengthFive"] += 1
        families = shortest_row_families(info)
        combinations = 1
        for family in families:
            combinations *= len(family)
        if combinations > args.max_combinations:
            result["systemsSkippedCombinationCap"] += 1
            continue
        result["systemsEnumerated"] += 1

        states = []
        for rows in itertools.product(*families):
            states.append((
                rows,
                scoped_state(n, set(info["Bset"]), set(info["Mset"]), rows),
            ))
        result["tuples"] += len(states)
        result["orderedTuplePairs"] += len(states) * len(states)

        for old_rows, old in states:
            for new_rows, new in states:
                if not safe_support_expansion(old, new):
                    continue
                result["safeSupportExpansions"] += 1
                if result["firstSafeWitness"] is None:
                    result["firstSafeWitness"] = {
                        "g6": g6,
                        "oldRows": old_rows,
                        "newRows": new_rows,
                        "oldScore": old["score"],
                        "newScore": new["score"],
                    }
                if new["score"] > old["score"]:
                    result["scoreViolations"] += 1
                if old["score"] > 0 and not new["activeVertices"]:
                    result["fullDeactivations"] += 1
                    if result["firstFullDeactivationWitness"] is None:
                        result["firstFullDeactivationWitness"] = {
                            "g6": g6,
                            "oldRows": old_rows,
                            "newRows": new_rows,
                            "oldScore": old["score"],
                            "newScore": new["score"],
                        }
                    if not new["score"] < old["score"]:
                        result["fullDeactivationStrictViolations"] += 1

    assert result["scoreViolations"] == 0
    assert result["fullDeactivationStrictViolations"] == 0
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
