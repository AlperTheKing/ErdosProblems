#!/usr/bin/env python3
"""Approximate chordal width for CERT-2 ChartSOS Gram sparsity graphs.

Search helper only. It reports graph-core and NetworkX min-degree treewidth
estimates for the disconnected Gram compatibility graph.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import networkx as nx
from networkx.algorithms import approximation as nx_approx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_sos as sos
import _codex_eq_cert2_chart_sos_sparsity as sp


def graph_from_adj(adj: list[set[int]], nodes: list[int] | None = None) -> nx.Graph:
    if nodes is None:
        nodes = list(range(len(adj)))
    node_set = set(nodes)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for u in nodes:
        for v in adj[u]:
            if v in node_set and u <= v:
                if u != v:
                    G.add_edge(u, v)
    return G


def bag_stats(decomp: nx.Graph) -> dict[str, int]:
    sizes = [len(bag) for bag in decomp.nodes]
    return {
        "bags": len(sizes),
        "max_bag": max(sizes) if sizes else 0,
        "min_bag": min(sizes) if sizes else 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--basis", choices=["dense-leq", "dense-exact", "sparse"], default="sparse")
    ap.add_argument("--seed-rows", default="")
    ap.add_argument("--components", type=int, default=4, help="Number of largest components for treewidth estimates")
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_width_v1.json")
    args = ap.parse_args()

    target11, generators, meta = lp.build_chart(args.chart)
    target12 = sos.mul_linear(target11)
    rows = sp.rows_from_seed(args.seed_rows or None, target12)
    num_vars = len(next(iter(target12)))
    if args.basis == "dense-leq":
        basis = sp.monomials_leq_degree(num_vars, 6)
        seed = (6,) + (0,) * (num_vars - 1)
        basis = [b for b in basis if b != seed]
    elif args.basis == "dense-exact":
        basis = sp.monomials_exact_degree(num_vars, 6)
        seed = (6,) + (0,) * (num_vars - 1)
        basis = [b for b in basis if b != seed]
    else:
        basis = sp.sparse_basis_for_rows(rows)

    adj, by_sum, pair_count, represented, diag_rows = sp.build_pair_graph(basis, rows)
    comps = sp.components(adj)
    full_G = graph_from_adj(adj)
    core = nx.core_number(full_G) if full_G.number_of_nodes() else {}
    comp_out = []
    for idx, comp in enumerate(comps[: args.components]):
        G = graph_from_adj(adj, comp)
        core_vals = [core[v] for v in comp]
        item = {
            "component": idx,
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "density_num": 2 * G.number_of_edges(),
            "density_den": G.number_of_nodes() * (G.number_of_nodes() - 1),
            "max_core": max(core_vals) if core_vals else 0,
        }
        try:
            tw, decomp = nx_approx.treewidth_min_degree(G)
            item.update({"treewidth_min_degree": int(tw), **bag_stats(decomp)})
        except Exception as exc:  # keep this diagnostic script robust
            item["treewidth_error"] = f"{type(exc).__name__}:{exc}"
        comp_out.append(item)

    out = {
        "schema": "eq_cert2_chart_sos_width_v1",
        "chart": args.chart,
        "basis_mode": args.basis,
        "seed_rows": args.seed_rows or None,
        "basis_size": len(basis),
        "row_count": len(rows),
        "active_pair_count": pair_count,
        "represented_row_count": len(represented),
        "component_count": len(comps),
        "component_sizes": [len(c) for c in comps],
        "global_max_core": max(core.values()) if core else 0,
        "components_estimated": comp_out,
        "meta": meta,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    printable = dict(out)
    printable.pop("meta", None)
    print(json.dumps(printable, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
