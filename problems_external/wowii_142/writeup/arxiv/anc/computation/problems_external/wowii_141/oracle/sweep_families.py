#!/usr/bin/env python3
"""Structured-family + random sweep for WOWII FC conjectures 141/142/144/145/146
beyond the n<=7 atlas (no geng/pynauty available on this machine).

Families (all connected, 2 <= n <= 14 unless noted):
  * tadpoles: cycle C_g with a pendant path of t edges          (g 3..12, n<=14)
  * cycle + pendant star: C_g with k pendant leaves at one vertex
  * cycle + two pendant paths at (near-)antipodal vertices
  * spiders (subdivided stars) S(a,b,c) attached to a cycle vertex
  * theta graphs Theta(a,b,c): two hubs joined by 3 disjoint paths
  * dumbbells: two cycles joined by a path (incl. figure-eight, length 0)
  * prisms (circular ladders) and Moebius ladders
  * named graphs: Petersen(10), Heawood(14), Moebius-Kantor(16), Pappus(18),
    Desargues(20), dodecahedron(20), hypercubes Q3/Q4, K33, K44,
    complete split / wheels / gear graphs
  * random connected G(n,p): 500 per n for n=8..12, 200 per n for n=13..14,
    p cycling over {0.15, 0.25, 0.4, 0.6}, seed 20260718 (reproducible)

All five conjectures are checked exactly on every graph.  Output:
families_results.json (violations, 141-equality graph6 list, min slacks).
"""

from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

import networkx as nx

from invariants import compute_all, check_conjectures, nx_to_bitadj

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "families_results.json"
CONJS = ("c141", "c142", "c144", "c145", "c146")
SEED = 20260718
MAX_N_EXHAUSTIVE = 20  # 2^20 masks for the induced-tree search is still fine


def graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode("ascii").strip()


# ---------------------------------------------------------------- constructors

def tadpole(g: int, t: int) -> nx.Graph:
    G = nx.cycle_graph(g)
    prev = 0
    for i in range(t):
        G.add_edge(prev, f"p{i}")
        prev = f"p{i}"
    return G


def cycle_pendant_star(g: int, k: int) -> nx.Graph:
    G = nx.cycle_graph(g)
    for i in range(k):
        G.add_edge(0, f"s{i}")
    return G


def cycle_two_tails(g: int, t1: int, t2: int) -> nx.Graph:
    G = nx.cycle_graph(g)
    prev = 0
    for i in range(t1):
        G.add_edge(prev, f"a{i}")
        prev = f"a{i}"
    prev = g // 2
    for i in range(t2):
        G.add_edge(prev, f"b{i}")
        prev = f"b{i}"
    return G


def cycle_spider(g: int, legs: tuple[int, ...]) -> nx.Graph:
    """Cycle C_g with a spider (subdivided star) rooted at cycle vertex 0."""
    G = nx.cycle_graph(g)
    for j, L in enumerate(legs):
        prev = 0
        for i in range(L):
            G.add_edge(prev, f"l{j}_{i}")
            prev = f"l{j}_{i}"
    return G


def theta(a: int, b: int, c: int) -> nx.Graph:
    """Two hubs u,v joined by three internally disjoint paths with a,b,c edges."""
    G = nx.Graph()
    u, v = "u", "v"
    for name, L in (("x", a), ("y", b), ("z", c)):
        prev = u
        for i in range(L - 1):
            G.add_edge(prev, f"{name}{i}")
            prev = f"{name}{i}"
        G.add_edge(prev, v)
    return G


def dumbbell(g1: int, g2: int, path_len: int) -> nx.Graph:
    G = nx.cycle_graph(g1)
    H = nx.relabel_nodes(nx.cycle_graph(g2), {i: f"c{i}" for i in range(g2)})
    G.update(H)
    if path_len == 0:
        G = nx.contracted_nodes(G, 0, "c0", self_loops=False)
    else:
        prev = 0
        for i in range(path_len - 1):
            G.add_edge(prev, f"q{i}")
            prev = f"q{i}"
        G.add_edge(prev, "c0")
    return G


def moebius_ladder(k: int) -> nx.Graph:
    return nx.circulant_graph(2 * k, [1, k])


def build_family_graphs() -> list[tuple[str, nx.Graph]]:
    out: list[tuple[str, nx.Graph]] = []
    for g in range(3, 13):
        for t in range(1, 15 - g):
            out.append((f"tadpole({g},{t})", tadpole(g, t)))
    for g in range(3, 12):
        for k in range(1, min(6, 15 - g)):
            out.append((f"cycle_star({g},{k})", cycle_pendant_star(g, k)))
    for g in range(4, 12):
        for t1 in range(1, 4):
            for t2 in range(t1, 4):
                if g + t1 + t2 <= 14:
                    out.append((f"cycle_two_tails({g},{t1},{t2})",
                                cycle_two_tails(g, t1, t2)))
    for g in range(3, 11):
        for legs in [(1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (2, 2, 2),
                     (3, 2, 1), (1, 1, 1), (4, 3), (2, 1, 1)]:
            if g + sum(legs) <= 14:
                out.append((f"cycle_spider({g},{legs})", cycle_spider(g, legs)))
    for a in range(1, 13):
        for b in range(max(a, 2), 13):
            for c in range(b, 13):
                if a + b + c - 1 <= 14:
                    out.append((f"theta({a},{b},{c})", theta(a, b, c)))
    for g1 in range(3, 9):
        for g2 in range(g1, 9):
            for L in range(0, 5):
                n = g1 + g2 + (L - 1 if L else -1) + (0 if L else 0)
                if g1 + g2 + max(L - 1, 0) - (1 if L == 0 else 0) <= 14:
                    out.append((f"dumbbell({g1},{g2},{L})", dumbbell(g1, g2, L)))
    for k in range(3, 8):
        out.append((f"prism({k})", nx.circular_ladder_graph(k)))
        out.append((f"moebius_ladder({k})", moebius_ladder(k)))
    named = [
        ("petersen", nx.petersen_graph()),
        ("heawood", nx.heawood_graph()),
        ("moebius_kantor", nx.moebius_kantor_graph()),
        ("pappus", nx.pappus_graph()),
        ("desargues", nx.desargues_graph()),
        ("dodecahedron", nx.dodecahedral_graph()),
        ("Q3", nx.hypercube_graph(3)),
        ("Q4", nx.hypercube_graph(4)),
        ("K33", nx.complete_bipartite_graph(3, 3)),
        ("K44", nx.complete_bipartite_graph(4, 4)),
        ("wheel(7)", nx.wheel_graph(7)),
        ("wheel(10)", nx.wheel_graph(10)),
        ("gear(6)", None),
    ]
    for name, G in named:
        if name.startswith("gear"):
            # gear graph: wheel with subdivided rim edges
            k = 6
            G = nx.Graph()
            for i in range(k):
                G.add_edge("hub", f"r{i}")
                G.add_edge(f"r{i}", f"m{i}")
                G.add_edge(f"m{i}", f"r{(i + 1) % k}")
        out.append((name, G))
    return out


def random_graphs(rng: random.Random) -> list[tuple[str, nx.Graph]]:
    out = []
    plist = [0.15, 0.25, 0.4, 0.6]
    for n in range(8, 15):
        count = 500 if n <= 12 else 200
        for i in range(count):
            p = plist[i % len(plist)]
            while True:
                G = nx.gnp_random_graph(n, p, seed=rng.randrange(2 ** 31))
                if nx.is_connected(G):
                    break
            out.append((f"rand(n={n},p={p},i={i})", G))
    return out


def main() -> None:
    rng = random.Random(SEED)
    graphs = build_family_graphs() + random_graphs(rng)

    checked = 0
    seen_g6: set[str] = set()
    hyp145_failed = 0
    violations: dict[str, list[dict]] = {c: [] for c in CONJS}
    eq141: list[dict] = []
    min_slack: dict[str, object] = {c: None for c in CONJS}
    min_slack_name: dict[str, str | None] = {c: None for c in CONJS}
    skipped_dupe = 0

    for name, G in graphs:
        n = G.number_of_nodes()
        if n < 2 or n > MAX_N_EXHAUSTIVE or not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        g6 = graph6(G)
        if g6 in seen_g6:
            skipped_dupe += 1
            continue
        seen_g6.add(g6)
        checked += 1
        nn, adj = nx_to_bitadj(G)
        inv = compute_all(nn, adj)
        res = check_conjectures(inv)
        if not res["c145"]["hypothesis"]:
            hyp145_failed += 1
        for c in CONJS:
            r = res[c]
            if r.get("hypothesis", True):
                sv = Fraction(str(r["slack"]))
                if min_slack[c] is None or sv < Fraction(str(min_slack[c])):
                    min_slack[c] = str(sv)
                    min_slack_name[c] = f"{name} [{g6}]"
            if not r["holds"]:
                violations[c].append({
                    "family": name, "graph6": g6, "n": inv["n"], "m": inv["m"],
                    "invariants": {k: v for k, v in inv.items()
                                   if k != "tree_witness_mask"},
                    "result": r,
                })
        if res["c141"]["slack"] == 0:
            eq141.append({"family": name, "graph6": g6, "n": inv["n"],
                          "girth": inv["girth"], "max_l": inv["max_l"],
                          "tree": inv["tree"]})

    payload = {
        "test": "WOWII_FC_141_142_144_145_146_families_and_random",
        "seed": SEED,
        "graphs_checked": checked,
        "duplicates_skipped": skipped_dupe,
        "c145_hypothesis_failed_count": hyp145_failed,
        "violation_counts": {c: len(violations[c]) for c in CONJS},
        "min_slack": min_slack,
        "min_slack_witness": min_slack_name,
        "c141_equality_count": len(eq141),
        "c141_equality_cases": eq141,
        "violations": violations,
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()
    summary = {k: payload[k] for k in (
        "graphs_checked", "duplicates_skipped", "c145_hypothesis_failed_count",
        "violation_counts", "min_slack", "min_slack_witness",
        "c141_equality_count")}
    summary["output_sha256"] = digest
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
