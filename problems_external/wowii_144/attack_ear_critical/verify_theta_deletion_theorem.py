#!/usr/bin/env python3
"""Verify the proved theta-graph eta-preserving deletion theorem.

For all integer path lengths 1 <= a <= b <= c with a+b >= 5, construct
Theta(a,b,c), delete the first internal vertex of the b-path, and recompute
all distances and full centers.  The script also checks the structural
formulas used in the proof.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import networkx as nx

from theta_probe import inv, theta

HERE = Path(__file__).resolve().parent


def tadpole_eta(cycle_length: int, tail_length: int) -> int:
    half_cycle = cycle_length // 2
    if tail_length <= half_cycle:
        return tail_length
    return (half_cycle + tail_length) // 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-length", type=int, default=30)
    parser.add_argument("--output", type=Path, default=HERE / "theta_deletion_verification.json")
    args = parser.parse_args()
    checked = 0
    minimum_delta = None
    minimum_bound_slack = None
    tight = 0
    first_failure = None
    for a in range(1, args.max_length + 1):
        for b in range(a, args.max_length + 1):
            for c in range(b, args.max_length + 1):
                if a == b == 1 or a + b < 5:
                    continue
                graph, paths = theta((a, b, c))
                if graph.number_of_edges() != a + b + c:
                    continue
                checked += 1
                old = inv(graph)
                half_long_cycle = (a + c) // 2
                general_bound = (b + 1) // 2
                bound = 1 if b == 3 else general_bound
                long_path = paths[2]
                anchor = (c - b) // 2
                anchor_vertices = {long_path[anchor], long_path[c - anchor], 0, 1}
                anchors_central = anchor_vertices <= old["center"]
                special_midpoint_central = True
                if b == 3 and c % 2 == 0:
                    special_midpoint_central = long_path[c // 2] in old["center"]
                subgraph = graph.copy()
                subgraph.remove_node(paths[1][1])
                new = inv(subgraph)
                predicted_new_eta = tadpole_eta(a + c, b - 2)
                delta = new["eta"] - old["eta"]
                bound_slack = bound - old["eta"]
                minimum_delta = delta if minimum_delta is None else min(minimum_delta, delta)
                minimum_bound_slack = (
                    bound_slack
                    if minimum_bound_slack is None
                    else min(minimum_bound_slack, bound_slack)
                )
                if delta == 0:
                    tight += 1
                valid = (
                    old["radius"] == half_long_cycle
                    and anchors_central
                    and special_midpoint_central
                    and old["eta"] <= bound
                    and new["eta"] == predicted_new_eta
                    and new["eta"] >= bound
                    and delta >= 0
                )
                if not valid:
                    first_failure = {
                        "lengths": [a, b, c],
                        "old": {
                            "radius": old["radius"],
                            "eta": old["eta"],
                            "center": sorted(old["center"]),
                        },
                        "half_long_cycle": half_long_cycle,
                        "bound": bound,
                        "anchors": sorted(anchor_vertices),
                        "anchors_central": anchors_central,
                        "special_midpoint_central": special_midpoint_central,
                        "new_eta": new["eta"],
                        "predicted_new_eta": predicted_new_eta,
                        "delta": delta,
                    }
                    break
            if first_failure is not None:
                break
        if first_failure is not None:
            break
    result = {
        "statement": "Theta(a,b,c), a<=b<=c, a+b>=5: delete first internal b-path vertex without decreasing eta",
        "max_length": args.max_length,
        "checked": checked,
        "minimum_delta_eta": minimum_delta,
        "minimum_theta_bound_slack": minimum_bound_slack,
        "tight": tight,
        "first_failure": first_failure,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if first_failure is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
