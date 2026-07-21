#!/usr/bin/env python3
"""Probe direct block-location rules for eta-nondecreasing deletions.

This script audits only candidate selections inside the registered W144-MIN
frontier.  It is not evidence for a new surrogate theorem.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def cyclic_blocks(graph: nx.Graph) -> list[frozenset[int]]:
    blocks = []
    for vertices in nx.biconnected_components(graph):
        subgraph = graph.subgraph(vertices)
        if subgraph.number_of_edges() >= subgraph.number_of_nodes():
            blocks.append(frozenset(vertices))
    return blocks


def audit(max_n: int) -> None:
    counts: Counter[str] = Counter()
    for n in range(5, max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            eta, center = center_depth(graph)
            blocks = cyclic_blocks(graph)
            if len(blocks) < 2:
                counts["one_cyclic_block"] += 1
                continue
            counts["multi_cyclic_block"] += 1
            cut = set(nx.articulation_points(graph))
            noncentral_blocks = [
                block for block in blocks if (block & center).issubset(cut)
            ]
            good = []
            for block in noncentral_blocks:
                for vertex in sorted(block - cut):
                    subgraph = graph.copy()
                    subgraph.remove_node(vertex)
                    if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
                        continue
                    eta_h, _ = center_depth(subgraph)
                    if eta_h >= eta:
                        good.append((tuple(sorted(block)), vertex, eta_h))
            if not good:
                print(
                    "FAIL",
                    code.decode(),
                    "n", n,
                    "eta", eta,
                    "center", sorted(center),
                    "blocks", [sorted(block) for block in blocks],
                    "cut", sorted(cut),
                )
                raise SystemExit(1)
            counts["noncentral_block_good"] += 1
    print(dict(counts))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=12)
    args = parser.parse_args()
    audit(args.max_n)


if __name__ == "__main__":
    main()
