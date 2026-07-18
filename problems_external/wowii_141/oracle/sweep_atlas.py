#!/usr/bin/env python3
"""Exhaustive sweep of ALL connected graphs on 2..7 vertices (networkx atlas)
against WOWII conjectures 141/142/144/145/146 as formalized in
formal-conjectures (see invariants.py header for the exact Lean statements).

Outputs atlas_results.json with: violations (if any), 141-equality cases
(graph6 + values, for the sharpness section), min slack per conjecture,
and summary counts.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import networkx as nx

from invariants import compute_all, check_conjectures, nx_to_bitadj

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "atlas_results.json"

CONJS = ("c141", "c142", "c144", "c145", "c146")


def graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode("ascii").strip()


def main() -> None:
    atlas = nx.graph_atlas_g()
    checked = 0
    skipped_small_or_disconnected = 0
    hyp145_failed = 0
    violations: dict[str, list[dict]] = {c: [] for c in CONJS}
    eq141: list[dict] = []
    min_slack: dict[str, object] = {c: None for c in CONJS}
    min_slack_g6: dict[str, str | None] = {c: None for c in CONJS}

    def slack_val(c: str, res: dict):
        s = res["slack"]
        return Fraction(s) if isinstance(s, str) else Fraction(s)

    for graph in atlas:
        n = graph.number_of_nodes()
        if n < 2 or not nx.is_connected(graph):
            skipped_small_or_disconnected += 1
            continue
        checked += 1
        nn, adj = nx_to_bitadj(graph)
        inv = compute_all(nn, adj)
        res = check_conjectures(inv)
        g6 = graph6(graph)

        if not res["c145"]["hypothesis"]:
            hyp145_failed += 1

        for c in CONJS:
            r = res[c]
            if r.get("hypothesis", True):
                sv = slack_val(c, r)
                if min_slack[c] is None or sv < Fraction(str(min_slack[c])):
                    min_slack[c] = str(sv)
                    min_slack_g6[c] = g6
            if not r["holds"]:
                violations[c].append({
                    "graph6": g6, "n": inv["n"], "m": inv["m"],
                    "invariants": {k: v for k, v in inv.items()
                                   if k != "tree_witness_mask"},
                    "result": r,
                })

        if res["c141"]["slack"] == 0:
            eq141.append({
                "graph6": g6, "n": inv["n"], "m": inv["m"],
                "girth": inv["girth"], "max_l": inv["max_l"],
                "tree": inv["tree"],
                "lhs": res["c141"]["lhs"], "rhs": res["c141"]["rhs"],
            })

    payload = {
        "test": "WOWII_FC_conjectures_141_142_144_145_146_atlas_n2_7",
        "atlas_total": len(atlas),
        "connected_n_ge_2_checked": checked,
        "skipped": skipped_small_or_disconnected,
        "c145_hypothesis_failed_count": hyp145_failed,
        "violation_counts": {c: len(violations[c]) for c in CONJS},
        "min_slack": min_slack,
        "min_slack_graph6": min_slack_g6,
        "c141_equality_count": len(eq141),
        "c141_equality_cases": eq141,
        "violations": violations,
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()

    summary = {k: payload[k] for k in (
        "atlas_total", "connected_n_ge_2_checked", "c145_hypothesis_failed_count",
        "violation_counts", "min_slack", "min_slack_graph6", "c141_equality_count")}
    summary["output_sha256"] = digest
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
