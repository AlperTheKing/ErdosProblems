#!/usr/bin/env python3
"""Independent recomputation layer (networkx-based, separate code paths from
invariants.py) for double-checking oracle results:

  * girth via nx.girth (Boitmanis et al. implementation in networkx)
  * largest induced tree via descending itertools.combinations + nx.is_tree
  * independence numbers via complement + exact maximal-clique enumeration
  * eccentricities / center / periphery via nx.eccentricity
  * G^2 via nx.power, radius via nx.radius

cross_check(G) recomputes every invariant both ways and asserts equality;
returns the invariant dict.  Used on all violations, all 141-equality cases,
and a deterministic sample of sweep graphs.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx

from invariants import compute_all, check_conjectures, nx_to_bitadj
from fractions import Fraction


def girth_nx(G: nx.Graph) -> int:
    g = nx.girth(G)
    return 0 if g == math.inf else int(g)


def largest_induced_tree_nx(G: nx.Graph) -> int:
    vertices = tuple(sorted(G.nodes()))
    for size in range(len(vertices), 0, -1):
        for subset in itertools.combinations(vertices, size):
            if nx.is_tree(G.subgraph(subset)):
                return size
    raise AssertionError("singleton induces a tree")


def alpha_nx(G: nx.Graph) -> int:
    """Exact independence number: max clique of the complement."""
    if G.number_of_nodes() == 0:
        return 0
    comp = nx.complement(G)
    return max(len(c) for c in nx.find_cliques(comp)) if comp.number_of_nodes() else 0


def indep_neighbors_card_nx(G: nx.Graph, v) -> int:
    return alpha_nx(G.subgraph(list(G.neighbors(v))))


def dist_to_set_nx(dist_from: dict, S: set) -> int:
    return min(dist_from[s] for s in S) if S else 0


def cross_check(G: nx.Graph) -> dict:
    """Recompute all invariants independently; raise AssertionError on mismatch."""
    n, adj = nx_to_bitadj(G)
    inv = compute_all(n, adj)
    nodes = sorted(G.nodes())
    node_of = {i: u for i, u in enumerate(nodes)}

    # girth
    assert girth_nx(G) == inv["girth"], f"girth mismatch: {girth_nx(G)} vs {inv['girth']}"

    # largest induced tree
    t_nx = largest_induced_tree_nx(G)
    assert t_nx == inv["tree"], f"tree mismatch: {t_nx} vs {inv['tree']}"
    # also verify the oracle witness really induces a tree of that size
    wit = [node_of[i] for i in range(n) if inv["tree_witness_mask"] >> i & 1]
    assert len(wit) == inv["tree"] and nx.is_tree(G.subgraph(wit)), "witness not a tree"

    # local independence numbers (on G)
    l_nx = [indep_neighbors_card_nx(G, node_of[i]) for i in range(n)]
    assert l_nx == inv["l_values"], f"l-values mismatch: {l_nx} vs {inv['l_values']}"

    # local independence minimum of the complement
    Gc = nx.complement(G)
    lmin_nx = min(indep_neighbors_card_nx(Gc, v) for v in Gc.nodes())
    assert lmin_nx == inv["lmin_complement"], \
        f"lmin(comp) mismatch: {lmin_nx} vs {inv['lmin_complement']}"

    # eccentricities, center, periphery
    ecc = nx.eccentricity(G)
    radius, diam = min(ecc.values()), max(ecc.values())
    assert radius == inv["radius"] and diam == inv["ediam"]
    center = {u for u in nodes if ecc[u] == radius}
    periph = {u for u in nodes if ecc[u] == diam}
    center_mask = sum(1 << i for i in range(n) if node_of[i] in center)
    periph_mask = sum(1 << i for i in range(n) if node_of[i] in periph)
    assert center_mask == inv["center_mask"] and periph_mask == inv["periphery_mask"]

    # ecc(G, center)  (FC `ecc`: max over v NOT in S, 0 if S = univ)
    sp = dict(nx.all_pairs_shortest_path_length(G))
    outside = [u for u in nodes if u not in center]
    ecc_center_nx = max((dist_to_set_nx(sp[u], center) for u in outside), default=0)
    assert ecc_center_nx == inv["ecc_center"], \
        f"ecc(center) mismatch: {ecc_center_nx} vs {inv['ecc_center']}"

    # eccSet(G, periphery)  (max over ALL v)
    ecc_set_nx = max(dist_to_set_nx(sp[u], periph) for u in nodes)
    assert ecc_set_nx == inv["eccSet_periphery"], \
        f"eccSet(periphery) mismatch: {ecc_set_nx} vs {inv['eccSet_periphery']}"

    # graph square radius
    G2 = nx.power(G, 2)
    rad2_nx = nx.radius(G2)
    assert rad2_nx == inv["graphSquareRadius"], \
        f"rad(G^2) mismatch: {rad2_nx} vs {inv['graphSquareRadius']}"

    # re-evaluate conjectures from the independently computed pieces
    res = check_conjectures(inv)
    lhs141 = girth_nx(G) // 2 - 1 + max(l_nx)
    assert (lhs141 <= t_nx) == res["c141"]["holds"]
    lhs142 = Fraction(2, 3) * girth_nx(G) + ecc_set_nx
    assert (lhs142 <= t_nx) == res["c142"]["holds"]
    lhs144 = girth_nx(G) - 1 + ecc_center_nx
    assert (lhs144 <= t_nx) == res["c144"]["holds"]
    if lmin_nx > 0:
        assert (2 * ecc_set_nx <= t_nx * lmin_nx) == res["c145"]["holds"]
    if rad2_nx > 0:
        assert (2 * ecc_set_nx <= t_nx * rad2_nx) == res["c146"]["holds"]
    return inv


def main() -> None:
    import json
    import random
    from pathlib import Path

    root = Path(__file__).resolve().parent
    report = {"checked": [], "violations_reverified": 0, "eq141_reverified": 0,
              "sample_reverified": 0, "mismatches": []}

    def check_g6(g6: str, label: str) -> None:
        G = nx.from_graph6_bytes(g6.encode())
        try:
            cross_check(G)
            report["checked"].append({"graph6": g6, "label": label, "ok": True})
        except AssertionError as e:  # pragma: no cover
            report["mismatches"].append({"graph6": g6, "label": label,
                                         "error": str(e)})

    for fname in ("atlas_results.json", "families_results.json"):
        path = root / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for conj, viols in data.get("violations", {}).items():
            for v in viols:
                check_g6(v["graph6"], f"{fname}:{conj}:violation")
                report["violations_reverified"] += 1
        for e in data.get("c141_equality_cases", []):
            check_g6(e["graph6"], f"{fname}:c141:equality")
            report["eq141_reverified"] += 1

    # deterministic sample of atlas graphs for oracle self-validation
    rng = random.Random(12345)
    atlas = nx.graph_atlas_g()
    eligible = [g for g in atlas
                if g.number_of_nodes() >= 2 and nx.is_connected(g)]
    for G in rng.sample(eligible, 80):
        cross_check(G)
        report["sample_reverified"] += 1
    # plus fixed sanity graphs
    for G in (nx.petersen_graph(), nx.heawood_graph(),
              nx.cycle_graph(9), nx.complete_graph(6),
              nx.path_graph(8), nx.circular_ladder_graph(5)):
        cross_check(G)
        report["sample_reverified"] += 1

    out = root / "verify_report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: (v if not isinstance(v, list) else len(v))
                      for k, v in report.items()}, indent=2, sort_keys=True))
    if report["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
