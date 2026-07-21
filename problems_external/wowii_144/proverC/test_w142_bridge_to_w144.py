#!/usr/bin/env python3
"""Test whether the proved W142 bound closes the residual W144 regime.

This is only a finite falsifier for the proposed bridge

    f + ceil(2g/3) >= g - 1 + e,

where f is the eccentricity of the periphery and e is the eccentricity of
the center.  It reuses exactly the deterministic corpus of the N2 test.
"""
from __future__ import annotations

import random

import networkx as nx

from test_gpt_n2 import (all_pairs_dist, dist_to_set, ecc_of_set,
                         eccentricities, girth, graph6, nx_to_bitadj)
from bridge_tests import adversarial_graphs
from route_b_tests import (chorded_cycle, cycle_random_legs,
                           cycle_random_trees, forced_girth_random,
                           gen_theta, trap_family)
from sweep_families import build_family_graphs, random_graphs


def main() -> None:
    rng = random.Random(20260718)
    corpus = [("atlas", G) for G in nx.graph_atlas_g()]
    corpus += build_family_graphs()
    corpus += random_graphs(random.Random(20260718))
    corpus += adversarial_graphs() + trap_family()
    for _ in range(300):
        corpus.extend((cycle_random_legs(rng), cycle_random_trees(rng),
                       chorded_cycle(rng), gen_theta(rng)))
    got = tries = 0
    while got < 200 and tries < 5000:
        tries += 1
        item = forced_girth_random(rng, gmin=5)
        if item is not None:
            corpus.append(item)
            got += 1

    seen: set[str] = set()
    residual = closed = combined_closed = 0
    failures: list[tuple] = []
    combined_failures: list[tuple] = []
    for name, G in corpus:
        if G.number_of_nodes() < 5 or not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G)
        n, adj = nx_to_bitadj(G)
        g = girth(n, adj)
        if g < 5 or n - g > 15:
            continue
        code = graph6(G)
        if code in seen:
            continue
        seen.add(code)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        radius, diameter = min(ecc), max(ecc)
        center = sum(1 << v for v in range(n) if ecc[v] == radius)
        periphery = sum(1 << v for v in range(n) if ecc[v] == diameter)
        e = ecc_of_set(n, dist, center)
        f = ecc_of_set(n, dist, periphery)
        if e == 0 or e <= diameter - g // 2:
            continue
        residual += 1
        lhs = f + (2 * g + 2) // 3
        rhs = g - 1 + e
        if lhs >= rhs:
            closed += 1
        elif len(failures) < 30:
            failures.append((name, code, n, g, radius, diameter, e, f,
                             rhs - lhs))

        # Already-proved exact lower bounds from the 141--143 work and P2.
        max_degree = max(dict(G.degree()).values())
        leaves = sum(degree == 1 for _, degree in G.degree())
        known = max(diameter + (g + 1) // 2 - 1,
                    max_degree + g - 3,
                    lhs,
                    g + 1 if leaves >= 2 else 0)
        if known >= rhs:
            combined_closed += 1
        elif len(combined_failures) < 30:
            combined_failures.append((name, code, n, g, radius, diameter,
                                      e, f, max_degree, leaves, rhs - known))

    print({"residual": residual, "closed_by_w142": closed,
           "failures": residual - closed})
    for record in failures:
        print(record)
    print({"residual": residual, "closed_by_all_known": combined_closed,
           "failures": residual - combined_closed})
    for record in combined_failures:
        print(record)


if __name__ == "__main__":
    main()
