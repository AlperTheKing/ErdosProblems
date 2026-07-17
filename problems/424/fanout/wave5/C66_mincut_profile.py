#!/usr/bin/env python3
"""Exact profiler for the canonical minimum source shore of the C60 network.

SciPy supplies an integral maximum flow.  Everything reported about the cut
is then recomputed with Python integers from the original capacity dictionary:
the residual source shore, cut capacity, C60 cut formula, unary closure, and
the seed-chain decomposition of the reserve.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

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


C56 = load_module("c66_c56", COMPUTE / "C56_image_lp_dual.py")


def ratio(num: int, den: int) -> dict[str, int | str] | None:
    if den == 0:
        return None
    return {"numerator": num, "denominator": den, "text": f"{num}/{den}"}


def counter_dict(values) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items())}


def residue_profile(nodes: set[int]) -> dict:
    return {
        "count": len(nodes),
        "parity": counter_dict(n % 2 for n in nodes),
        "mod3": counter_dict(n % 3 for n in nodes),
        "mod6": counter_dict(n % 6 for n in nodes),
        "mod9": counter_dict(n % 9 for n in nodes),
        "mod12": counter_dict(n % 12 for n in nodes),
    }


class DisjointSet:
    def __init__(self, vertices: set[int]) -> None:
        self.parent = {v: v for v in vertices}
        self.size = {v: 1 for v in vertices}

    def find(self, v: int) -> int:
        parent = self.parent[v]
        while parent != self.parent[parent]:
            parent = self.parent[parent]
        while v != parent:
            nxt = self.parent[v]
            self.parent[v] = parent
            v = nxt
        return parent

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def component_profile(
    shore: set[int],
    internal_edges: list[tuple[int, int]],
    hard_in: set[int],
    splitless: set[int],
    outgoing_origins: set[int],
    unary_out: dict[int, list[int]],
    label: str,
) -> dict:
    dsu = DisjointSet(shore)
    for u, v in internal_edges:
        dsu.union(u, v)
    groups: defaultdict[int, list[int]] = defaultdict(list)
    for node in shore:
        groups[dsu.find(node)].append(node)
    internal_count: Counter[int] = Counter()
    for u, _ in internal_edges:
        internal_count[dsu.find(u)] += 1
    rows = []
    for root, nodes in groups.items():
        node_set = set(nodes)
        hard_count = len(node_set & hard_in)
        outgoing_count = len(node_set & outgoing_origins)
        rows.append(
            {
                "minimum": min(nodes),
                "maximum": max(nodes),
                "vertices": len(nodes),
                "node_list": sorted(nodes) if len(nodes) <= 25 else None,
                "hard": hard_count,
                "splitless": len(node_set & splitless),
                "outgoing_seed_arcs": outgoing_count,
                "internal_edges": internal_count[root],
                "unary_terminals": sum(not unary_out.get(node) for node in nodes),
                "hard_to_outgoing": ratio(hard_count, outgoing_count),
            }
        )
    by_size = sorted(rows, key=lambda row: (-row["vertices"], row["minimum"]))
    finite = [row for row in rows if row["outgoing_seed_arcs"]]
    by_ratio = sorted(
        finite,
        key=lambda row: (
            -Fraction(row["hard"], row["outgoing_seed_arcs"]),
            row["minimum"],
        ),
    )
    no_out_hard = [
        row for row in rows if row["hard"] and not row["outgoing_seed_arcs"]
    ]
    return {
        "label": label,
        "components": len(rows),
        "singletons": sum(row["vertices"] == 1 for row in rows),
        "components_with_hard_but_no_outgoing_seed": len(no_out_hard),
        "hard_in_no_outgoing_components": sum(row["hard"] for row in no_out_hard),
        "hard_but_no_outgoing_samples": sorted(
            no_out_hard, key=lambda row: row["minimum"]
        )[:25],
        "largest": by_size[:25],
        "largest_hard_to_outgoing_ratio": by_ratio[:25],
    }


def residual_reachable(capacity_matrix, flow_matrix, source: int) -> set[int]:
    residual = (capacity_matrix - flow_matrix).tocsr()
    residual.eliminate_zeros()
    seen = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for index in range(residual.indptr[u], residual.indptr[u + 1]):
            if residual.data[index] <= 0:
                continue
            v = int(residual.indices[index])
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return seen


def seed_chain_profile(
    limit: int,
    shore: set[int],
    holes: set[int],
    generated: set[int],
    hard_in: set[int],
    outgoing_pairs: set[tuple[int, int]],
) -> dict:
    predecessor = {
        child: parent
        for parent in shore
        for child in [2 * parent - 1]
        if child <= limit and child in shore
    }
    roots = sorted(node for node in shore if node not in predecessor)
    chains = []
    covered: set[int] = set()
    for root in roots:
        nodes = []
        node = root
        while True:
            if node in covered:
                raise RuntimeError(f"seed chains merge at {node}")
            covered.add(node)
            nodes.append(node)
            child = 2 * node - 1
            if child > limit:
                terminal = "truncated"
                outgoing = None
                break
            if child in shore:
                node = child
                continue
            terminal = "generated_exit" if child in generated else "hole_exit"
            outgoing = (node, child)
            if child not in generated and child not in holes:
                raise RuntimeError(f"unclassified seed child {child}")
            if outgoing not in outgoing_pairs:
                raise RuntimeError(f"missing outgoing seed arc {outgoing}")
            break
        hard_nodes = sorted(set(nodes) & hard_in)
        if len(hard_nodes) > 1:
            raise RuntimeError(f"seed chain has multiple even hard nodes: {hard_nodes}")
        chains.append(
            {
                "root": root,
                "length": len(nodes),
                "terminal": terminal,
                "hard_root": hard_nodes[0] if hard_nodes else None,
                "outgoing": list(outgoing) if outgoing else None,
            }
        )
    if covered != shore:
        raise RuntimeError(f"seed chain partition missed {len(shore - covered)} nodes")
    exiting = [chain for chain in chains if chain["outgoing"] is not None]
    truncated = [chain for chain in chains if chain["outgoing"] is None]
    hard_exit = [chain for chain in exiting if chain["hard_root"] is not None]
    hard_truncated = [chain for chain in truncated if chain["hard_root"] is not None]
    nonhard_exit = [chain for chain in exiting if chain["hard_root"] is None]
    nonhard_truncated = [chain for chain in truncated if chain["hard_root"] is None]
    if len(exiting) != len(outgoing_pairs):
        raise RuntimeError("seed-chain exits do not biject with outgoing seed arcs")
    if len(hard_exit) + len(hard_truncated) != len(hard_in):
        raise RuntimeError("hard nodes do not biject with hard-root seed chains")
    reserve_identity = len(nonhard_exit) - len(hard_truncated)
    hard_truncated_roots = sorted(chain["root"] for chain in hard_truncated)
    nonhard_exit_roots = sorted(chain["root"] for chain in nonhard_exit)
    rank_pairs = list(zip(hard_truncated_roots, nonhard_exit_roots))
    rank_violations = [
        [index, hard_root, nonhard_root]
        for index, (hard_root, nonhard_root) in enumerate(rank_pairs)
        if nonhard_root > hard_root
    ]
    return {
        "chains": len(chains),
        "exiting_chains": len(exiting),
        "truncated_chains": len(truncated),
        "hard_exiting_chains": len(hard_exit),
        "hard_truncated_chains": len(hard_truncated),
        "nonhard_exiting_chains": len(nonhard_exit),
        "reserve_identity": reserve_identity,
        "hard_truncated_to_nonhard_exiting": ratio(
            len(hard_truncated), len(nonhard_exit)
        ),
        "length_histogram": counter_dict(chain["length"] for chain in chains),
        "hard_exiting_length_histogram": counter_dict(
            chain["length"] for chain in hard_exit
        ),
        "hard_truncated_length_histogram": counter_dict(
            chain["length"] for chain in hard_truncated
        ),
        "nonhard_exiting_length_histogram": counter_dict(
            chain["length"] for chain in nonhard_exit
        ),
        "nonhard_truncated_length_histogram": counter_dict(
            chain["length"] for chain in nonhard_truncated
        ),
        "hard_exiting_roots": sorted(chain["root"] for chain in hard_exit),
        "hard_truncated_roots": hard_truncated_roots,
        "nonhard_exiting_roots": nonhard_exit_roots,
        "nonhard_truncated_roots": sorted(chain["root"] for chain in nonhard_truncated),
        "rank_pairing_nonhard_exit_to_hard_truncated": {
            "pairs": len(rank_pairs),
            "nonhard_root_at_most_hard_root": not rank_violations,
            "violations": rank_violations[:25],
        },
        "longest_chains": sorted(
            chains, key=lambda chain: (-chain["length"], chain["root"])
        )[:25],
    }


def profile(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    pairs = {n: C56.admissible_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    hard = {n for n in values if C56.hard_shape(n, pairs[n])}
    hard_holes = hard & holes
    splitless = {n for n in holes if n not in (2, 3) and not pairs[n]}

    finite_arc_bound = len(hard_holes) + sum(2 * n - 1 <= limit for n in holes)
    infinity = finite_arc_bound + 1
    source, sink = limit + 1, limit + 2
    capacities: dict[tuple[int, int], int] = {}
    unary_selectors: list[tuple[int, int, int]] = []
    seed_arcs: list[tuple[int, int]] = []

    def add(u: int, v: int, capacity: int) -> None:
        capacities[u, v] = capacities.get((u, v), 0) + capacity

    for node in hard_holes:
        add(source, node, 1)
    for node in splitless:
        add(source, node, infinity)
    for n in holes:
        for a, b in pairs[n]:
            if (a in generated) != (b in generated):
                generated_factor, hole_factor = (a, b) if a in generated else (b, a)
                add(n, hole_factor, infinity)
                unary_selectors.append((n, generated_factor, hole_factor))
        child = 2 * n - 1
        if child <= limit:
            target = sink if child in generated else child
            add(n, target, 1)
            seed_arcs.append((n, child))

    rows = np.fromiter((edge[0] for edge in capacities), dtype=np.int64)
    cols = np.fromiter((edge[1] for edge in capacities), dtype=np.int64)
    data = np.fromiter(capacities.values(), dtype=np.int64)
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(limit + 3, limit + 3), dtype=np.int64
    ).tocsr()
    result = maximum_flow(matrix, source, sink)
    flow_value = int(result.flow_value)
    reachable = residual_reachable(matrix, result.flow, source)
    if sink in reachable:
        raise RuntimeError(f"{limit}: sink remains residual-reachable")
    shore = holes & reachable

    hard_in = hard_holes & shore
    hard_out = hard_holes - shore
    outgoing = [
        (parent, child)
        for parent, child in seed_arcs
        if parent in shore and (child in generated or child not in shore)
    ]
    outgoing_set = set(outgoing)
    outgoing_origins = {parent for parent, _ in outgoing}
    if len(outgoing_origins) != len(outgoing):
        raise RuntimeError(f"{limit}: two outgoing seed arcs share an origin")

    cut_edges = []
    cut_capacity = 0
    for (u, v), capacity in capacities.items():
        if u in reachable and v not in reachable:
            cut_edges.append((u, v, capacity))
            cut_capacity += capacity
    infinite_cut_edges = [edge for edge in cut_edges if edge[2] >= infinity]

    selectors_from_shore = [
        selector for selector in unary_selectors if selector[0] in shore
    ]
    selector_violations = [
        selector for selector in selectors_from_shore if selector[2] not in shore
    ]
    if not splitless <= shore:
        raise RuntimeError(f"{limit}: source shore omits splitless roots")
    if selector_violations or infinite_cut_edges:
        raise RuntimeError(f"{limit}: infinite-capacity closure violation")

    formula_capacity = len(hard_out) + len(outgoing)
    reserve = flow_value - len(hard_holes)
    if cut_capacity != flow_value or formula_capacity != flow_value:
        raise RuntimeError(
            f"{limit}: cut mismatch cut={cut_capacity}, formula={formula_capacity}, flow={flow_value}"
        )
    if reserve != len(outgoing) - len(hard_in):
        raise RuntimeError(f"{limit}: reserve identity failed")
    if reserve < 0:
        raise RuntimeError(f"{limit}: C60 inequality fails by {-reserve}")

    unary_out: defaultdict[int, list[int]] = defaultdict(list)
    for n, _, p in selectors_from_shore:
        unary_out[n].append(p)
    max_depth: dict[int, int] = {}
    min_splitless_depth: dict[int, int | None] = {}
    for node in sorted(shore):
        children = unary_out.get(node, [])
        max_depth[node] = 0 if not children else 1 + max(max_depth[p] for p in children)
        split_depths = [
            min_splitless_depth[p]
            for p in children
            if min_splitless_depth[p] is not None
        ]
        if node in splitless:
            min_splitless_depth[node] = 0
        elif split_depths:
            min_splitless_depth[node] = 1 + min(int(depth) for depth in split_depths)
        else:
            min_splitless_depth[node] = None

    unary_internal_edges = [(n, p) for n, _, p in selectors_from_shore]
    seed_internal_edges = [
        (parent, child)
        for parent, child in seed_arcs
        if parent in shore and child in shore
    ]
    selector_factor_counts = Counter(g for _, g, _ in selectors_from_shore)
    terminal_nodes = {node for node in shore if not unary_out.get(node)}

    seed_chains = seed_chain_profile(
        limit, shore, holes, generated, hard_in, outgoing_set
    )
    if seed_chains["reserve_identity"] != reserve:
        raise RuntimeError(f"{limit}: seed-chain reserve decomposition failed")

    return {
        "limit": limit,
        "network": {
            "allowed": len(values),
            "generated": len(generated),
            "holes": len(holes),
            "hard_holes": len(hard_holes),
            "splitless": len(splitless),
            "unary_selectors": len(unary_selectors),
            "seed_arcs": len(seed_arcs),
            "capacity_edges": len(capacities),
            "infinity": infinity,
        },
        "certificate": {
            "max_flow": flow_value,
            "direct_cut_capacity": cut_capacity,
            "formula_cut_capacity": formula_capacity,
            "hard_outside_shore": len(hard_out),
            "hard_inside_shore": len(hard_in),
            "outgoing_seed_arcs": len(outgoing),
            "reserve": reserve,
            "hard_to_outgoing": ratio(len(hard_in), len(outgoing)),
            "inequality_hard_le_outgoing": len(hard_in) <= len(outgoing),
            "splitless_roots_all_in_shore": splitless <= shore,
            "unary_closure_violations": len(selector_violations),
            "infinite_cut_edges": len(infinite_cut_edges),
        },
        "source_side_holes": sorted(shore),
        "hard_holes_in_source_side": sorted(hard_in),
        "outgoing_seed_arc_list": [list(edge) for edge in sorted(outgoing)],
        "closure": {
            "selectors_from_source_side": len(selectors_from_shore),
            "selector_list_n_generated_hole": [
                list(selector) for selector in sorted(selectors_from_shore)
            ],
            "outputs_with_multiple_selectors": {
                str(n): len(children)
                for n, children in sorted(unary_out.items())
                if len(children) > 1
            },
            "generated_factor_counts": {
                str(g): count for g, count in sorted(selector_factor_counts.items())
            },
        },
        "unary_depth": {
            "maximum": max(max_depth.values(), default=0),
            "histogram": counter_dict(max_depth.values()),
            "vertices_reaching_splitless": sum(
                depth is not None for depth in min_splitless_depth.values()
            ),
            "minimum_splitless_depth_histogram": counter_dict(
                depth for depth in min_splitless_depth.values() if depth is not None
            ),
            "terminal_nodes": len(terminal_nodes),
            "terminal_splitless": len(terminal_nodes & splitless),
            "terminal_with_only_two_hole_selectors": len(terminal_nodes - splitless),
        },
        "unary_components": component_profile(
            shore,
            unary_internal_edges,
            hard_in,
            splitless,
            outgoing_origins,
            unary_out,
            "undirected unary-selector components",
        ),
        "closure_seed_components": component_profile(
            shore,
            unary_internal_edges + seed_internal_edges,
            hard_in,
            splitless,
            outgoing_origins,
            unary_out,
            "undirected internal unary-plus-seed components",
        ),
        "seed_chains": seed_chains,
        "residues": {
            "source_side": residue_profile(shore),
            "hard_inside": residue_profile(hard_in),
            "outgoing_seed_origins": residue_profile(outgoing_origins),
            "hard_truncated_roots": residue_profile(
                set(seed_chains["hard_truncated_roots"])
            ),
        },
    }


def largest_ratio(rows: list[dict], numerator_path: tuple[str, ...], denominator_path: tuple[str, ...]):
    best = None
    for row in rows:
        numerator = row
        denominator = row
        for key in numerator_path:
            numerator = numerator[key]
        for key in denominator_path:
            denominator = denominator[key]
        if denominator == 0:
            continue
        if best is None or numerator * best[1] > best[0] * denominator:
            best = (numerator, denominator, row["limit"])
    if best is None:
        return None
    return {
        "numerator": best[0],
        "denominator": best[1],
        "text": f"{best[0]}/{best[1]}",
        "limit": best[2],
    }


def dense_rank_scan(max_limit: int) -> dict:
    rank_failures = []
    inequality_failures = []
    minimum_reserve: tuple[int, int] | None = None
    maximum_ratio: tuple[int, int, int] | None = None
    for limit in range(2, max_limit + 1):
        row = profile(limit)
        reserve = row["certificate"]["reserve"]
        if minimum_reserve is None or reserve < minimum_reserve[0]:
            minimum_reserve = (reserve, limit)
        hard_inside = row["certificate"]["hard_inside_shore"]
        outgoing = row["certificate"]["outgoing_seed_arcs"]
        if outgoing and (
            maximum_ratio is None
            or hard_inside * maximum_ratio[1] > maximum_ratio[0] * outgoing
        ):
            maximum_ratio = (hard_inside, outgoing, limit)
        if not row["certificate"]["inequality_hard_le_outgoing"]:
            inequality_failures.append(limit)
        if not row["seed_chains"]["rank_pairing_nonhard_exit_to_hard_truncated"][
            "nonhard_root_at_most_hard_root"
        ]:
            rank_failures.append(limit)
    return {
        "range": [2, max_limit],
        "cutoffs": max_limit - 1,
        "minimum_reserve": {
            "value": minimum_reserve[0],
            "first_limit": minimum_reserve[1],
        }
        if minimum_reserve
        else None,
        "maximum_hard_to_outgoing_ratio": {
            "numerator": maximum_ratio[0],
            "denominator": maximum_ratio[1],
            "text": f"{maximum_ratio[0]}/{maximum_ratio[1]}",
            "limit": maximum_ratio[2],
        }
        if maximum_ratio
        else None,
        "c60_inequality_failures": inequality_failures,
        "rank_pairing_failures": rank_failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limits",
        nargs="+",
        type=int,
        default=[54, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000],
    )
    parser.add_argument("--output", type=Path, default=HERE / "C66_mincut_profile.json")
    parser.add_argument("--dense-scan-max", type=int, default=2000)
    args = parser.parse_args()
    if not args.limits or min(args.limits) < 2:
        raise ValueError("all limits must be at least 2")
    rows = [profile(limit) for limit in args.limits]
    dense_scan = dense_rank_scan(args.dense_scan_max) if args.dense_scan_max >= 2 else None
    payload = {
        "method": "SciPy integral max-flow plus independent integer cut reconstruction",
        "limits": args.limits,
        "all_exact_checks_pass": True,
        "dense_rank_scan": dense_scan,
        "maximum_hard_to_outgoing_ratio": largest_ratio(
            rows,
            ("certificate", "hard_inside_shore"),
            ("certificate", "outgoing_seed_arcs"),
        ),
        "maximum_truncated_hard_to_nonhard_exit_ratio": largest_ratio(
            rows,
            ("seed_chains", "hard_truncated_chains"),
            ("seed_chains", "nonhard_exiting_chains"),
        ),
        "profiles": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    compact = [
        {
            "limit": row["limit"],
            "shore": len(row["source_side_holes"]),
            "hard_in": row["certificate"]["hard_inside_shore"],
            "seed_out": row["certificate"]["outgoing_seed_arcs"],
            "reserve": row["certificate"]["reserve"],
            "hard_truncated": row["seed_chains"]["hard_truncated_chains"],
            "nonhard_exit": row["seed_chains"]["nonhard_exiting_chains"],
        }
        for row in rows
    ]
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
