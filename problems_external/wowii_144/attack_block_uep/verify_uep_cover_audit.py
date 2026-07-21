#!/usr/bin/env python3
"""Exact audit of the load-bearing UEP-cover obstruction for W144-MIN.

For each connected multicyclic graph of girth at least five, this checks for
an admissible deletion v with nonincreasing radius and a surviving eta
realizer x that cannot be covered by a possible new center whose unique
eccentric point in G is v.  Such a pair certifies eta(G-v) >= eta(G).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def audit(min_n: int, max_n: int) -> dict:
    per_order: dict[str, dict] = {}
    corpus_hash = hashlib.sha256()
    witness_hash = hashlib.sha256()
    total = 0
    failure: dict | None = None

    for n in range(min_n, max_n + 1):
        checked = 0
        for code, graph in records(n):
            old_girth = girth(graph)
            if old_girth is None or old_girth < 5 or cycle_rank(graph) < 2:
                continue
            checked += 1
            total += 1
            corpus_hash.update(code + b"\n")

            old_eta, old_center = center_depth(graph)
            eccentricity = nx.eccentricity(graph)
            old_radius = min(eccentricity.values())
            distance = dict(nx.all_pairs_shortest_path_length(graph))
            realizers = {
                x
                for x in graph
                if min(distance[x][c] for c in old_center) == old_eta
            }

            witness: dict | None = None
            deletion_rows: list[dict] = []
            for v in sorted(graph):
                subgraph = graph.copy()
                subgraph.remove_node(v)
                if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
                    continue
                new_eccentricity = nx.eccentricity(subgraph)
                new_radius = min(new_eccentricity.values())
                new_eta, new_center = center_depth(subgraph)
                if new_radius > old_radius:
                    deletion_rows.append(
                        {
                            "v": v,
                            "new_radius": new_radius,
                            "new_eta": new_eta,
                            "status": "radius_increase",
                        }
                    )
                    continue

                q_v = []
                for u in graph:
                    if u == v or u in old_center or eccentricity[u] != old_radius + 1:
                        continue
                    farthest = [
                        y for y in graph if distance[u][y] == old_radius + 1
                    ]
                    if farthest == [v]:
                        q_v.append(u)

                uncovered = [
                    x
                    for x in sorted(realizers - {v})
                    if all(distance[x][u] >= old_eta for u in q_v)
                ]
                deletion_rows.append(
                    {
                        "v": v,
                        "new_radius": new_radius,
                        "new_eta": new_eta,
                        "q_v": q_v,
                        "uncovered": uncovered,
                    }
                )
                if uncovered:
                    assert new_eta >= old_eta
                    witness = {
                        "v": v,
                        "x": uncovered[0],
                        "q_v": q_v,
                        "new_radius": new_radius,
                        "new_eta": new_eta,
                        "new_center": sorted(new_center),
                    }
                    break

            if witness is None:
                failure = {
                    "graph6": code.decode(),
                    "n": n,
                    "m": graph.number_of_edges(),
                    "girth": old_girth,
                    "rank": cycle_rank(graph),
                    "radius": old_radius,
                    "eta": old_eta,
                    "center": sorted(old_center),
                    "realizers": sorted(realizers),
                    "edges": sorted(
                        [min(a, b), max(a, b)] for a, b in graph.edges()
                    ),
                    "deletions": deletion_rows,
                }
                break

            witness_hash.update(
                (
                    f"{code.decode()}:{witness['v']}:{witness['x']}:"
                    f"{','.join(map(str, witness['q_v']))}\n"
                ).encode()
            )

        per_order[str(n)] = {"checked": checked}
        if failure is not None:
            break

    return {
        "statement": (
            "exists admissible v with rad(G-v)<=rad(G) and a surviving "
            "eta-realizer x not covered within eta-1 by Q_v"
        ),
        "generator": "geng -ctfq",
        "min_n": min_n,
        "max_n": max_n,
        "per_order": per_order,
        "total_checked": total,
        "corpus_sha256": corpus_hash.hexdigest(),
        "canonical_witness_sha256": witness_hash.hexdigest(),
        "failure": failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "uep_cover_audit_results.json",
    )
    args = parser.parse_args()
    result = audit(args.min_n, args.max_n)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["failure"] is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
