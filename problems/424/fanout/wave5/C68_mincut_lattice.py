#!/usr/bin/env python3
"""Exact tests for the C66 rank proposal and the minimum-cut lattice.

SciPy is used only to obtain an integral maximum flow.  Shore validity,
capacity, unary closure, SCC reachability, chain profiles, and toggle costs
are all recomputed with Python integers.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COMPUTE = ROOT / "problems" / "424" / "compute" / "wave5"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C56 = load_module("c68_c56", COMPUTE / "C56_image_lp_dual.py")


def build(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    pairs = {n: C56.admissible_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    hard = {n for n in values if C56.hard_shape(n, pairs[n])} & holes
    splitless = {n for n in holes if n not in (2, 3) and not pairs[n]}
    finite_bound = len(hard) + sum(2 * n - 1 <= limit for n in holes)
    infinity = finite_bound + 1
    source, sink = limit + 1, limit + 2
    capacities: dict[tuple[int, int], int] = {}
    unary: set[tuple[int, int]] = set()
    seed: set[tuple[int, int]] = set()

    def add(u: int, v: int, cap: int) -> None:
        capacities[u, v] = capacities.get((u, v), 0) + cap

    for n in hard:
        add(source, n, 1)
    for n in splitless:
        add(source, n, infinity)
    for n in holes:
        for a, b in pairs[n]:
            if (a in generated) != (b in generated):
                p = b if a in generated else a
                unary.add((n, p))
                add(n, p, infinity)
        child = 2 * n - 1
        if child <= limit:
            target = sink if child in generated else child
            seed.add((n, target))
            add(n, target, 1)

    rows = np.fromiter((u for u, _ in capacities), dtype=np.int64)
    cols = np.fromiter((v for _, v in capacities), dtype=np.int64)
    data = np.fromiter(capacities.values(), dtype=np.int64)
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(limit + 3, limit + 3), dtype=np.int64
    ).tocsr()
    result = maximum_flow(matrix, source, sink)
    return {
        "limit": limit,
        "generated": generated,
        "holes": holes,
        "hard": hard,
        "splitless": splitless,
        "unary": unary,
        "seed": seed,
        "capacities": capacities,
        "infinity": infinity,
        "source": source,
        "sink": sink,
        "matrix": matrix,
        "flow": result.flow.tocsr(),
        "value": int(result.flow_value),
    }


def residual_graph(model: dict) -> nx.DiGraph:
    residual = (model["matrix"] - model["flow"]).tocsr()
    residual.eliminate_zeros()
    active = set(model["holes"]) | {model["source"], model["sink"]}
    graph = nx.DiGraph()
    graph.add_nodes_from(active)
    for u in active:
        for index in range(residual.indptr[u], residual.indptr[u + 1]):
            if int(residual.data[index]) > 0:
                v = int(residual.indices[index])
                if v in active:
                    graph.add_edge(u, v)
    return graph


def reachable(graph: nx.DiGraph, start: int) -> set[int]:
    return {start} | nx.descendants(graph, start)


def cut_capacity(model: dict, shore: set[int]) -> int:
    full = set(shore) | {model["source"]}
    return sum(
        capacity
        for (u, v), capacity in model["capacities"].items()
        if u in full and v not in full
    )


def verify_shore(model: dict, shore: set[int], minimum: bool = True) -> dict:
    omitted_splitless = sorted(model["splitless"] - shore)
    unary_violations = sorted((n, p) for n, p in model["unary"] if n in shore and p not in shore)
    capacity = cut_capacity(model, shore)
    infinite_crossings = sum(
        1
        for (u, v), cap in model["capacities"].items()
        if cap >= model["infinity"]
        and u in shore | {model["source"]}
        and v not in shore | {model["source"]}
    )
    if omitted_splitless or unary_violations or infinite_crossings:
        raise RuntimeError(
            f"invalid shore: splitless={omitted_splitless[:3]} "
            f"unary={unary_violations[:3]} infinite={infinite_crossings}"
        )
    if minimum and capacity != model["value"]:
        raise RuntimeError(f"nonminimum shore: {capacity} != {model['value']}")
    return {"capacity": capacity, "unary_violations": len(unary_violations)}


def chain_profile(model: dict, shore: set[int]) -> dict:
    predecessor = {
        2 * parent - 1: parent
        for parent in shore
        if 2 * parent - 1 <= model["limit"] and 2 * parent - 1 in shore
    }
    roots = sorted(n for n in shore if n not in predecessor)
    hard_truncated: list[int] = []
    nonhard_exiting: list[int] = []
    chains: dict[int, list[int]] = {}
    node_to_root: dict[int, int] = {}
    covered: set[int] = set()
    for root in roots:
        nodes = []
        node = root
        while True:
            if node in covered:
                raise RuntimeError(f"seed chains merge at {node}")
            covered.add(node)
            node_to_root[node] = root
            nodes.append(node)
            child = 2 * node - 1
            if child > model["limit"]:
                terminal = "truncated"
                break
            if child in shore:
                node = child
                continue
            terminal = "exiting"
            break
        chains[root] = nodes
        hard_nodes = model["hard"] & set(nodes)
        if len(hard_nodes) > 1:
            raise RuntimeError(f"multiple hard nodes in seed chain {root}: {hard_nodes}")
        if terminal == "truncated" and hard_nodes:
            hard_truncated.append(root)
        if terminal == "exiting" and not hard_nodes:
            nonhard_exiting.append(root)
    if covered != shore:
        raise RuntimeError(f"uncovered shore nodes: {sorted(shore-covered)[:5]}")
    hard_truncated.sort()
    nonhard_exiting.sort()
    prefix_violation = None
    for index, hard_root in enumerate(hard_truncated):
        if index >= len(nonhard_exiting) or nonhard_exiting[index] > hard_root:
            prefix_violation = {
                "index": index,
                "hard_root": hard_root,
                "nonhard_root": (
                    nonhard_exiting[index] if index < len(nonhard_exiting) else None
                ),
            }
            break
    return {
        "chains": chains,
        "node_to_root": node_to_root,
        "hard_truncated": hard_truncated,
        "nonhard_exiting": nonhard_exiting,
        "rank_holds": prefix_violation is None,
        "first_rank_violation": prefix_violation,
    }


def reverse_unary_saturation(model: dict, shore: set[int], removed: set[int]) -> set[int]:
    reverse: dict[int, list[int]] = defaultdict(list)
    for n, p in model["unary"]:
        if n in shore and p in shore:
            reverse[p].append(n)
    saturated = set(removed)
    queue = deque(removed)
    while queue:
        p = queue.popleft()
        for n in reverse[p]:
            if n not in saturated:
                saturated.add(n)
                queue.append(n)
    return saturated


def prefix_toggles(model: dict, shore: set[int]) -> list[dict]:
    profile = chain_profile(model, shore)
    roots = sorted(profile["chains"])
    rows = []
    for threshold in roots:
        raw = {
            node
            for root, nodes in profile["chains"].items()
            if root <= threshold
            for node in nodes
        }
        saturated = reverse_unary_saturation(model, shore, raw)
        feasible = not (saturated & model["splitless"])
        new_shore = shore - saturated
        closure_violations = [
            (n, p) for n, p in model["unary"] if n in new_shore and p not in new_shore
        ]
        if closure_violations:
            raise RuntimeError(f"reverse unary saturation failed: {closure_violations[:3]}")
        raw_profile = {
            "hard_truncated": sum(r <= threshold for r in profile["hard_truncated"]),
            "nonhard_exiting": sum(r <= threshold for r in profile["nonhard_exiting"]),
        }
        raw_delta = raw_profile["hard_truncated"] - raw_profile["nonhard_exiting"]
        row = {
            "threshold": threshold,
            "raw_nodes": len(raw),
            "saturated_nodes": len(saturated),
            "hits_splitless": bool(saturated & model["splitless"]),
            "raw_hard_truncated_minus_nonhard_exiting": raw_delta,
            "closure_verified": not closure_violations,
        }
        if feasible:
            row["capacity_delta"] = cut_capacity(model, new_shore) - model["value"]
            row["capacity_nonincreasing"] = row["capacity_delta"] <= 0
        else:
            row["capacity_delta"] = None
            row["capacity_nonincreasing"] = False
        rows.append(row)
    return rows


def residual_scc_lattice(model: dict, enumeration_cap: int) -> dict:
    graph = residual_graph(model)
    components = list(nx.strongly_connected_components(graph))
    component_of = {v: i for i, component in enumerate(components) for v in component}
    dag = nx.DiGraph()
    dag.add_nodes_from(range(len(components)))
    for u, v in graph.edges:
        if component_of[u] != component_of[v]:
            dag.add_edge(component_of[u], component_of[v])
    source_component = component_of[model["source"]]
    sink_component = component_of[model["sink"]]
    forced = reachable(dag, source_component)
    forbidden = {sink_component} | nx.ancestors(dag, sink_component)
    eligible = sorted(set(dag) - forced - forbidden)
    canonical = set().union(*(components[i] for i in forced)) & model["holes"]
    verify_shore(model, canonical)

    shores: list[set[int]] = []
    enumeration_complete = len(eligible) <= enumeration_cap
    if enumeration_complete:
        seen: set[tuple[int, ...]] = set()
        descendant_closure = {
            i: ({i} | nx.descendants(dag, i)) - forbidden for i in eligible
        }
        for mask in range(1 << len(eligible)):
            chosen = set(forced)
            valid = True
            for bit, component in enumerate(eligible):
                if mask >> bit & 1:
                    closure = descendant_closure[component]
                    if closure & forbidden:
                        valid = False
                        break
                    chosen |= closure
            if not valid:
                continue
            shore = set().union(*(components[i] for i in chosen)) & model["holes"]
            key = tuple(sorted(shore))
            if key in seen:
                continue
            seen.add(key)
            verify_shore(model, shore)
            shores.append(shore)
    rank_failures = []
    for shore in shores:
        profile = chain_profile(model, shore)
        if not profile["rank_holds"]:
            rank_failures.append(
                {
                    "shore": sorted(shore),
                    "first_rank_violation": profile["first_rank_violation"],
                    "hard_truncated": profile["hard_truncated"],
                    "nonhard_exiting": profile["nonhard_exiting"],
                }
            )
    intersection = set.intersection(*shores) if shores else canonical
    return {
        "residual_sccs": len(components),
        "forced_sccs": len(forced),
        "forbidden_sccs": len(forbidden),
        "eligible_sccs": len(eligible),
        "enumeration_complete": enumeration_complete,
        "minimum_shores": len(shores) if enumeration_complete else None,
        "canonical_is_intersection": (not shores) or intersection == canonical,
        "alternative_rank_failures": rank_failures[:3],
    }


def inspect(limit: int, enumeration_cap: int) -> dict:
    model = build(limit)
    graph = residual_graph(model)
    shore = reachable(graph, model["source"]) & model["holes"]
    verify_shore(model, shore)
    profile = chain_profile(model, shore)
    lattice = residual_scc_lattice(model, enumeration_cap)
    toggles = prefix_toggles(model, shore)
    return {
        "limit": limit,
        "max_flow": model["value"],
        "canonical_shore": sorted(shore),
        "canonical_rank": {
            "hard_truncated": profile["hard_truncated"],
            "nonhard_exiting": profile["nonhard_exiting"],
            "holds": profile["rank_holds"],
            "first_violation": profile["first_rank_violation"],
        },
        "lattice": lattice,
        "prefix_toggles": toggles,
    }


def lattice_counterexample() -> dict:
    """Small nondegenerate counterexample to a lattice-only rank theorem.

    The labels and finite/infinite arc directions have the C60 form.  The
    mandatory source node is abstract rather than an arithmetic splitless
    value, which is intentional: this isolates exactly what cut-lattice
    theory can and cannot prove without the number-theoretic classification.
    """
    limit = 9
    source, sink = 10, 11
    holes = {4, 5, 7}
    hard = {4}
    mandatory = {5}
    unary = {(7, 4)}
    seed = {(4, 7), (5, sink)}
    infinity = 4
    capacities: dict[tuple[int, int], int] = {
        (source, 4): 1,
        (source, 5): infinity,
    }
    capacities.update({edge: infinity for edge in unary})
    capacities.update({edge: 1 for edge in seed})
    rows = np.fromiter((u for u, _ in capacities), dtype=np.int64)
    cols = np.fromiter((v for _, v in capacities), dtype=np.int64)
    data = np.fromiter(capacities.values(), dtype=np.int64)
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(12, 12), dtype=np.int64
    ).tocsr()
    result = maximum_flow(matrix, source, sink)
    model = {
        "limit": limit,
        "generated": set(),
        "holes": holes,
        "hard": hard,
        "splitless": mandatory,
        "unary": unary,
        "seed": seed,
        "capacities": capacities,
        "infinity": infinity,
        "source": source,
        "sink": sink,
        "matrix": matrix,
        "flow": result.flow.tocsr(),
        "value": int(result.flow_value),
    }
    graph = residual_graph(model)
    shore = reachable(graph, source) & holes
    verification = verify_shore(model, shore)
    profile = chain_profile(model, shore)
    raw_hard_chain = set(profile["chains"][4])
    saturated = reverse_unary_saturation(model, shore, raw_hard_chain)
    minimum_shores = []
    ordered_holes = sorted(holes)
    for mask in range(1 << len(ordered_holes)):
        candidate = {
            node for index, node in enumerate(ordered_holes) if mask >> index & 1
        }
        if cut_capacity(model, candidate) == model["value"]:
            minimum_shores.append(sorted(candidate))
    return {
        "hole_vertices": sorted(holes),
        "capacities": [
            [u, v, cap] for (u, v), cap in sorted(capacities.items())
        ],
        "max_flow": model["value"],
        "canonical_shore": sorted(shore),
        "cut_capacity": verification["capacity"],
        "all_minimum_shores": minimum_shores,
        "canonical_is_unique_minimum_shore": minimum_shores == [sorted(shore)],
        "all_mandatory_nodes_inside": mandatory <= shore,
        "all_infinite_unary_arcs_internal": all(
            not (n in shore and p not in shore) for n, p in unary
        ),
        "hard_truncated_roots": profile["hard_truncated"],
        "nonhard_exiting_roots": profile["nonhard_exiting"],
        "rank_holds": profile["rank_holds"],
        "first_rank_violation": profile["first_rank_violation"],
        "violating_prefix_raw_removal": sorted(raw_hard_chain),
        "reverse_unary_saturation": sorted(saturated),
        "saturation_hits_mandatory_node": bool(saturated & mandatory),
        "raw_removal_capacity_delta": (
            cut_capacity(model, shore - raw_hard_chain) - model["value"]
        ),
        "raw_removal_unary_violations": sorted(
            (n, p)
            for n, p in unary
            if n in shore - raw_hard_chain and p not in shore - raw_hard_chain
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, default=[54, 74, 100, 200])
    parser.add_argument("--enumeration-cap", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [inspect(limit, args.enumeration_cap) for limit in args.limits]
    payload = {
        "lattice_counterexample": lattice_counterexample(),
        "arithmetic_profiles": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            [
                {
                    "limit": row["limit"],
                    "rank": row["canonical_rank"]["holds"],
                    "lattice": row["lattice"],
                }
                for row in rows
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
