"""Inspect equality cases for the W144-IND2 multicyclic deletion lemma."""

from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def girth(graph: nx.Graph) -> int | None:
    best: int | None = None
    for source in graph:
        dist = {source: 0}
        parent = {source: None}
        queue = [source]
        for u in queue:
            for w in graph[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    parent[w] = u
                    queue.append(w)
                elif parent[u] != w:
                    length = dist[u] + dist[w] + 1
                    if best is None or length < best:
                        best = length
    return best


def center_depth(graph: nx.Graph) -> tuple[int, frozenset[int]]:
    ecc = nx.eccentricity(graph)
    radius = min(ecc.values())
    center = frozenset(v for v, value in ecc.items() if value == radius)
    distances = nx.multi_source_dijkstra_path_length(graph, center)
    return max(distances.values()), center


def cycle_rank(graph: nx.Graph) -> int:
    return graph.number_of_edges() - graph.number_of_nodes() + 1


def records(order: int):
    process = subprocess.Popen(
        [str(GENG), "-ctfq", str(order)],
        stdout=subprocess.PIPE,
        text=False,
    )
    assert process.stdout is not None
    for line in process.stdout:
        code = line.strip()
        if code:
            yield code, nx.from_graph6_bytes(code)
    if process.wait() != 0:
        raise RuntimeError("geng failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("order", type=int)
    parser.add_argument("--show", type=int, default=40)
    args = parser.parse_args()

    counted = Counter()
    shown = 0
    for code, graph in records(args.order):
        g = girth(graph)
        if g is None or g < 5 or cycle_rank(graph) < 2:
            continue
        e, center = center_depth(graph)
        phi = g + e
        candidates = []
        for v in graph:
            h = graph.copy()
            h.remove_node(v)
            if not nx.is_connected(h) or cycle_rank(h) < 1:
                continue
            gh = girth(h)
            assert gh is not None
            eh, center_h = center_depth(h)
            candidates.append(
                {
                    "v": v,
                    "deg": graph.degree[v],
                    "dg": gh - g,
                    "de": eh - e,
                    "slack": gh + eh - phi,
                    "center_hit": v in center,
                    "g_h": gh,
                    "e_h": eh,
                    "center_h": sorted(center_h),
                }
            )
        best = max(item["slack"] for item in candidates)
        counted[(best, g, e, cycle_rank(graph))] += 1
        if best == 0 and shown < args.show:
            winners = [item for item in candidates if item["slack"] == best]
            print(
                code.decode(),
                f"n={args.order} m={graph.number_of_edges()} rank={cycle_rank(graph)}",
                f"g={g} e={e} C={sorted(center)}",
                f"deg={sorted(dict(graph.degree()).values())}",
                f"winners={winners}",
            )
            shown += 1
    print("SUMMARY")
    for key, count in sorted(counted.items()):
        print(key, count)


if __name__ == "__main__":
    main()
