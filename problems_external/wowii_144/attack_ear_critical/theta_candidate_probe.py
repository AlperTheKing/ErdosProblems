#!/usr/bin/env python3
"""Test explicit deletion positions on the middle/longest theta paths."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from theta_probe import inv, theta

HERE = Path(__file__).resolve().parent


def delta_delete(graph, old_eta: int, vertex: int) -> int:
    subgraph = graph.copy()
    subgraph.remove_node(vertex)
    return inv(subgraph)["eta"] - old_eta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-length", type=int, default=30)
    parser.add_argument("--output", type=Path, default=HERE / "theta_candidate_probe.json")
    args = parser.parse_args()
    labels = [
        "middle_first",
        "middle_mid_left",
        "middle_mid_right",
        "longest_first",
        "longest_mid_left",
        "longest_mid_right",
        "some_middle_mid",
        "some_longest_mid",
    ]
    totals = {label: 0 for label in labels}
    totals.update({"theta": 0, "some_of_six": 0})
    failures = {label: [] for label in labels + ["some_of_six"]}
    for a in range(1, args.max_length + 1):
        for b in range(a, args.max_length + 1):
            for c in range(b, args.max_length + 1):
                if a == b == 1 or a + b < 5:
                    continue
                graph, paths = theta((a, b, c))
                if graph.number_of_edges() != a + b + c:
                    continue
                totals["theta"] += 1
                old_eta = inv(graph)["eta"]
                selected = {}
                for path_index, name in ((1, "middle"), (2, "longest")):
                    path = paths[path_index]
                    length = len(path) - 1
                    positions = {
                        "first": 1,
                        "mid_left": length // 2,
                        "mid_right": (length + 1) // 2,
                    }
                    for suffix, position in positions.items():
                        selected[f"{name}_{suffix}"] = delta_delete(
                            graph, old_eta, path[position]
                        )
                selected["some_middle_mid"] = max(
                    selected["middle_mid_left"], selected["middle_mid_right"]
                )
                selected["some_longest_mid"] = max(
                    selected["longest_mid_left"], selected["longest_mid_right"]
                )
                for label in labels:
                    if selected[label] >= 0:
                        totals[label] += 1
                    elif len(failures[label]) < 12:
                        failures[label].append(
                            {"lengths": [a, b, c], "eta": old_eta, "deltas": selected}
                        )
                if max(selected[label] for label in labels[:6]) >= 0:
                    totals["some_of_six"] += 1
                elif len(failures["some_of_six"]) < 12:
                    failures["some_of_six"].append(
                        {"lengths": [a, b, c], "eta": old_eta, "deltas": selected}
                    )
    result = {"max_length": args.max_length, "totals": totals, "failures": failures}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
