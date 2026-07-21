#!/usr/bin/env python3
"""Targeted audit of the one-leaf extension step for W144-GCOMB."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx

from audit_gcomb_exact_order import exact_girth


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def metric_data(graph: nx.Graph, girth: int, kappa: int) -> dict[str, object]:
    n = graph.number_of_nodes()
    beta = graph.number_of_edges() - n + 1
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    distances = nx.multi_source_dijkstra_path_length(graph, center)
    eta = max(distances.values())
    diameter = max(eccentricity.values())
    maximum_degree = max(dict(graph.degree()).values())
    terms = {
        "degree": maximum_degree - 2 + kappa,
        "diameter": diameter - math.floor(girth / 2),
        "order_rank": n - girth - beta + 1,
    }
    return {
        "n": n,
        "beta": beta,
        "radius": radius,
        "center": sorted(center),
        "eta": eta,
        "diameter": diameter,
        "maximum_degree": maximum_degree,
        "terms": terms,
        "rhs": max(terms.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument(
        "--output", type=Path, default=HERE / "leaf_extension_audit_results.json"
    )
    args = parser.parse_args()

    summary: dict[str, object] = {
        "orders": {},
        "cores": 0,
        "rooted_extensions": 0,
        "max_eta_increase": None,
        "eta_increase_counts": Counter(),
        "radius_transition_counts": Counter(),
        "center_hausdorff_H_to_G_max": None,
        "leaf_cover_failures": [],
        "eta_plus_one_failures": [],
        "order_term_compensation_failures": [],
        "rhs_compensation_failures": [],
        "first_eta_rise": None,
        "first_order_term_compensation_failure": None,
        "first_rhs_compensation_failure": None,
    }

    for order in range(args.min_n, args.max_n + 1):
        process = subprocess.Popen(
            [str(GENG), "-Ctfq", str(order)], stdout=subprocess.PIPE, text=False
        )
        assert process.stdout is not None
        generated = retained = extensions = 0
        for line in process.stdout:
            code = line.strip()
            if not code:
                continue
            generated += 1
            core = nx.from_graph6_bytes(code)
            girth = exact_girth(core)
            if girth is None or girth < 5:
                continue
            if all(degree == 2 for _, degree in core.degree()):
                continue
            retained += 1
            summary["cores"] += 1
            core_data = metric_data(core, girth, kappa=1)
            for root in core:
                graph = core.copy()
                leaf = order
                graph.add_edge(root, leaf)
                data = metric_data(graph, girth, kappa=0)
                extensions += 1
                summary["rooted_extensions"] += 1

                eta_increase = int(data["eta"]) - int(core_data["eta"])
                summary["eta_increase_counts"][str(eta_increase)] += 1
                old_max = summary["max_eta_increase"]
                summary["max_eta_increase"] = (
                    eta_increase if old_max is None else max(old_max, eta_increase)
                )
                transition = f'{core_data["radius"]}->{data["radius"]}'
                summary["radius_transition_counts"][transition] += 1

                center_G = set(data["center"])
                max_to_new = max(
                    min(nx.shortest_path_length(graph, c, z) for z in center_G)
                    for c in core_data["center"]
                )
                old_h = summary["center_hausdorff_H_to_G_max"]
                summary["center_hausdorff_H_to_G_max"] = (
                    max_to_new if old_h is None else max(old_h, max_to_new)
                )

                witness = {
                    "core_graph6": code.decode("ascii"),
                    "root": root,
                    "core": core_data,
                    "extension": data,
                    "eta_increase": eta_increase,
                    "old_center_to_new_center_max": max_to_new,
                }
                if eta_increase > 1:
                    summary["eta_plus_one_failures"].append(witness)
                if int(data["eta"]) > int(data["rhs"]):
                    summary["leaf_cover_failures"].append(witness)
                if eta_increase > 0 and summary["first_eta_rise"] is None:
                    summary["first_eta_rise"] = witness
                if (
                    eta_increase > 0
                    and int(data["terms"]["order_rank"]) < int(data["eta"])
                ):
                    if summary["first_order_term_compensation_failure"] is None:
                        summary["first_order_term_compensation_failure"] = witness
                    summary["order_term_compensation_failures"].append(witness)
                if (
                    eta_increase > 0
                    and int(data["rhs"]) < int(core_data["rhs"]) + eta_increase
                ):
                    if summary["first_rhs_compensation_failure"] is None:
                        summary["first_rhs_compensation_failure"] = witness
                    summary["rhs_compensation_failures"].append(witness)
        if process.wait() != 0:
            raise RuntimeError(f"geng failed at order {order}")
        summary["orders"][str(order)] = {
            "generated": generated,
            "retained_noncycle_cores": retained,
            "rooted_extensions": extensions,
        }

    for key in ("eta_increase_counts", "radius_transition_counts"):
        summary[key] = dict(sorted(summary[key].items()))
    for key in (
        "leaf_cover_failures",
        "eta_plus_one_failures",
        "order_term_compensation_failures",
        "rhs_compensation_failures",
    ):
        summary[key] = {
            "count": len(summary[key]),
            "first_20": summary[key][:20],
        }
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "cores",
                    "rooted_extensions",
                    "max_eta_increase",
                    "eta_increase_counts",
                    "center_hausdorff_H_to_G_max",
                    "leaf_cover_failures",
                    "eta_plus_one_failures",
                    "order_term_compensation_failures",
                    "rhs_compensation_failures",
                )
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
