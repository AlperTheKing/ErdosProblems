#!/usr/bin/env python3
"""Exact unlabeled enumeration for WOWII Conjecture 314, through order 9.

The generated class is hereditary: all triangle-free, induced-P5-free graphs
are obtained by adding one vertex to a smaller graph in the same class.  At
each order we quotient candidates by exact NetworkX graph isomorphism.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

import networkx as nx


GraphBits = tuple[int, ...]


def add_vertex(g: GraphBits, neighbors: int) -> GraphBits:
    n = len(g)
    out = list(g) + [neighbors]
    for v in range(n):
        if neighbors >> v & 1:
            out[v] |= 1 << n
    return tuple(out)


def independent_mask(g: GraphBits, mask: int) -> bool:
    rest = mask
    while rest:
        bit = rest & -rest
        v = bit.bit_length() - 1
        rest ^= bit
        if g[v] & rest:
            return False
    return True


def induced_connected(g: GraphBits, vertices: tuple[int, ...]) -> bool:
    allowed = sum(1 << v for v in vertices)
    seen = 1 << vertices[0]
    queue = deque([vertices[0]])
    while queue:
        v = queue.popleft()
        fresh = g[v] & allowed & ~seen
        while fresh:
            bit = fresh & -fresh
            fresh ^= bit
            seen |= bit
            queue.append(bit.bit_length() - 1)
    return seen == allowed


def has_induced_p5(g: GraphBits) -> bool:
    if len(g) < 5:
        return False
    for vertices in itertools.combinations(range(len(g)), 5):
        allowed = sum(1 << v for v in vertices)
        degrees = sorted((g[v] & allowed).bit_count() for v in vertices)
        if degrees == [1, 1, 2, 2, 2] and induced_connected(g, vertices):
            return True
    return False


def to_networkx(g: GraphBits) -> nx.Graph:
    h = nx.Graph()
    h.add_nodes_from(range(len(g)))
    h.add_edges_from(
        (u, v)
        for u in range(len(g))
        for v in range(u + 1, len(g))
        if g[u] >> v & 1
    )
    return h


def invariant_key(g: GraphBits) -> tuple:
    h = to_networkx(g)
    degrees = tuple(sorted(d for _, d in h.degree()))
    components = tuple(sorted(len(c) for c in nx.connected_components(h)))
    triangles_per_vertex = tuple(sorted(nx.triangles(h).values()))
    wl = nx.weisfeiler_lehman_graph_hash(h, iterations=max(3, len(g)))
    return len(g), h.number_of_edges(), components, degrees, triangles_per_vertex, wl


def unlabeled_extensions(parents: list[GraphBits]) -> list[GraphBits]:
    buckets: dict[tuple, list[tuple[GraphBits, nx.Graph]]] = defaultdict(list)
    for parent in parents:
        n = len(parent)
        for neighbors in range(1 << n):
            if not independent_mask(parent, neighbors):
                continue
            child = add_vertex(parent, neighbors)
            if has_induced_p5(child):
                continue
            key = invariant_key(child)
            child_nx = to_networkx(child)
            if any(nx.is_isomorphic(child_nx, old_nx) for _, old_nx in buckets[key]):
                continue
            buckets[key].append((child, child_nx))
    return [g for bucket in buckets.values() for g, _ in bucket]


def connected(g: GraphBits) -> bool:
    if not g:
        return False
    all_vertices = (1 << len(g)) - 1
    seen = 1
    queue = [0]
    while queue:
        v = queue.pop()
        fresh = g[v] & ~seen
        while fresh:
            bit = fresh & -fresh
            fresh ^= bit
            seen |= bit
            queue.append(bit.bit_length() - 1)
    return seen == all_vertices


def is_total_dominating(g: GraphBits, selected: int) -> bool:
    return all(g[v] & selected for v in range(len(g)))


def minimal_tds(g: GraphBits) -> list[int]:
    out: list[int] = []
    for selected in range(1 << len(g)):
        if not is_total_dominating(g, selected):
            continue
        if all(
            not is_total_dominating(g, selected ^ (1 << v))
            for v in range(len(g))
            if selected >> v & 1
        ):
            out.append(selected)
    return out


def chain_graph(g: GraphBits) -> bool:
    h = to_networkx(g)
    if not nx.is_bipartite(h):
        return False
    color = nx.bipartite.color(h)
    sides = [[v for v in h if color[v] == c] for c in (0, 1)]
    for side in sides:
        for u, v in itertools.combinations(side, 2):
            nu = set(h.neighbors(u))
            nv = set(h.neighbors(v))
            if not (nu <= nv or nv <= nu):
                return False
    return True


def c5_blowup(g: GraphBits) -> bool:
    classes: dict[int, list[int]] = defaultdict(list)
    for v, neighborhood in enumerate(g):
        classes[neighborhood].append(v)
    bags = list(classes.values())
    if len(bags) != 5:
        return False
    quotient = nx.Graph()
    quotient.add_nodes_from(range(5))
    for i, j in itertools.combinations(range(5), 2):
        if g[bags[i][0]] >> bags[j][0] & 1:
            quotient.add_edge(i, j)
    return nx.is_isomorphic(quotient, nx.cycle_graph(5))


def graph6(g: GraphBits) -> str:
    return nx.to_graph6_bytes(to_networkx(g), header=False).decode().strip()


def audit_order(graphs: list[GraphBits], n: int) -> dict:
    qualifying = [g for g in graphs if connected(g) and n > 1]
    chain_count = 0
    blowup_count = 0
    wtd_failures = []
    dichotomy_failures = []
    tds_profiles: Counter[tuple[int, ...]] = Counter()
    for g in qualifying:
        is_chain = chain_graph(g)
        is_blowup = c5_blowup(g)
        chain_count += int(is_chain)
        blowup_count += int(is_blowup)
        if not (is_chain or is_blowup):
            dichotomy_failures.append(graph6(g))
        sets = minimal_tds(g)
        sizes = tuple(sorted({s.bit_count() for s in sets}))
        tds_profiles[sizes] += 1
        if len(sizes) != 1:
            wtd_failures.append(
                {"graph6": graph6(g), "sizes": list(sizes), "sets": sets}
            )
    return {
        "n": n,
        "hereditary_class_unlabeled": len(graphs),
        "connected_nontrivial": len(qualifying),
        "chain_graphs": chain_count,
        "c5_blowups": blowup_count,
        "tds_size_profiles": {str(k): v for k, v in sorted(tds_profiles.items())},
        "wtd_failures": wtd_failures,
        "dichotomy_failures": dichotomy_failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=9)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.time()
    graphs: list[GraphBits] = [tuple()]
    report = {
        "method": "hereditary vertex extension + exact isomorphism quotient",
        "max_n": args.max_n,
        "orders": [],
    }
    for n in range(1, args.max_n + 1):
        order_started = time.time()
        graphs = unlabeled_extensions(graphs)
        order = audit_order(graphs, n)
        order["seconds"] = round(time.time() - order_started, 6)
        report["orders"].append(order)
        print(json.dumps(order, sort_keys=True), flush=True)
        if order["wtd_failures"] or order["dichotomy_failures"]:
            break
    report["seconds"] = round(time.time() - started, 6)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
