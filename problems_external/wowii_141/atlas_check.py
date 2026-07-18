#!/usr/bin/env python3
"""Independent exhaustive atlas check for WOWII / Graffiti.pc 141.

For every connected graph in ``networkx.graph_atlas_g()`` this program
computes, by direct exhaustive algorithms:

* girth (zero for a forest),
* the maximum independence number of an open neighbourhood,
* the largest order of an induced tree, and
* the R1 star/geodesic witness from ``APPROACH_REGISTRY.md``.

The detailed result is written as JSON Lines, with a JSON summary and a
separate failure certificate.  Graphs are examined in increasing order of
``(number of vertices, number of edges, atlas index)``.  On the first failed
theorem or cyclic-witness check, the program stops after writing that smallest
failure certificate.

NetworkX supplies only the graph atlas and the graph data structure.  The
mathematical quantities below are computed here rather than delegated to
NetworkX optimisation routines.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import networkx as nx


SCHEMA_VERSION = 1


def pairs(vertices: Sequence[int]) -> Iterator[tuple[int, int]]:
    """Yield all unordered pairs from a sequence."""

    return itertools.combinations(vertices, 2)


def canonical_graph(graph: nx.Graph) -> nx.Graph:
    """Return a simple graph with deterministic integer vertex labels."""

    if graph.is_directed() or graph.is_multigraph():
        raise ValueError("the graph atlas entry must be a simple undirected graph")
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def graph6(graph: nx.Graph) -> str:
    """Return the canonical graph6 representation used in certificates."""

    return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def is_connected_on(graph: nx.Graph, vertices: Iterable[int]) -> bool:
    """Check connectedness of the subgraph induced by ``vertices``."""

    vertex_set = set(vertices)
    if not vertex_set:
        return False
    start = min(vertex_set)
    seen = {start}
    queue: deque[int] = deque([start])
    while queue:
        current = queue.popleft()
        for neighbour in graph.neighbors(current):
            if neighbour in vertex_set and neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return seen == vertex_set


def induced_edge_count(graph: nx.Graph, vertices: Iterable[int]) -> int:
    """Count edges with both endpoints in ``vertices``."""

    vertex_set = set(vertices)
    return sum(
        1 for u, v in graph.edges() if u in vertex_set and v in vertex_set
    )


def is_induced_tree(graph: nx.Graph, vertices: Iterable[int]) -> bool:
    """Check whether the indicated nonempty induced subgraph is a tree."""

    vertex_set = set(vertices)
    return bool(vertex_set) and induced_edge_count(
        graph, vertex_set
    ) == len(vertex_set) - 1 and is_connected_on(graph, vertex_set)


def shortest_distance_avoiding_edge(
    graph: nx.Graph,
    source: int,
    target: int,
    blocked_edge: tuple[int, int],
) -> int | None:
    """Find a shortest path length while ignoring one undirected edge."""

    blocked = {blocked_edge, (blocked_edge[1], blocked_edge[0])}
    distance = {source: 0}
    queue: deque[int] = deque([source])
    while queue:
        current = queue.popleft()
        for neighbour in sorted(graph.neighbors(current)):
            if (current, neighbour) in blocked:
                continue
            if neighbour in distance:
                continue
            distance[neighbour] = distance[current] + 1
            if neighbour == target:
                return distance[neighbour]
            queue.append(neighbour)
    return None


def exact_girth(graph: nx.Graph) -> int:
    """Compute girth exactly; use zero for an acyclic graph.

    For every edge ``uv``, remove only that edge and find a shortest remaining
    ``u``--``v`` path.  The minimum such path length plus one is exactly the
    length of a shortest cycle.
    """

    best: int | None = None
    for u, v in graph.edges():
        distance = shortest_distance_avoiding_edge(graph, u, v, (u, v))
        if distance is None:
            continue
        candidate = distance + 1
        if best is None or candidate < best:
            best = candidate
    return 0 if best is None else best


def is_independent(graph: nx.Graph, vertices: Sequence[int]) -> bool:
    """Check whether ``vertices`` form an independent set."""

    return all(not graph.has_edge(u, v) for u, v in pairs(vertices))


def maximum_independent_subset(
    graph: nx.Graph, vertices: Iterable[int]
) -> tuple[int, list[int]]:
    """Compute an exact maximum independent subset by enumeration."""

    ordered = sorted(vertices)
    for size in range(len(ordered), -1, -1):
        for candidate in itertools.combinations(ordered, size):
            if is_independent(graph, candidate):
                return size, list(candidate)
    raise AssertionError("the empty set must be independent")


def maximum_local_independence(
    graph: nx.Graph,
) -> tuple[int, int, list[int], list[int]]:
    """Return max local independence, a maximiser, its set, and all values."""

    values: list[int] = []
    witnesses: list[list[int]] = []
    nodes = sorted(graph.nodes())
    for vertex in nodes:
        value, witness = maximum_independent_subset(
            graph, graph.neighbors(vertex)
        )
        values.append(value)
        witnesses.append(witness)
    maximum = max(values)
    first_index = values.index(maximum)
    return maximum, nodes[first_index], witnesses[first_index], values


def maximum_induced_tree(graph: nx.Graph) -> tuple[int, list[int]]:
    """Compute the exact largest induced-tree order by subset enumeration."""

    nodes = sorted(graph.nodes())
    for size in range(len(nodes), 0, -1):
        for candidate in itertools.combinations(nodes, size):
            if is_induced_tree(graph, candidate):
                return size, list(candidate)
    raise AssertionError("every nonempty graph has a one-vertex induced tree")


def bfs_from(
    graph: nx.Graph, root: int
) -> tuple[dict[int, int], dict[int, int | None]]:
    """Run deterministic BFS and return distances and parents."""

    distance = {root: 0}
    parent: dict[int, int | None] = {root: None}
    queue: deque[int] = deque([root])
    while queue:
        current = queue.popleft()
        for neighbour in sorted(graph.neighbors(current)):
            if neighbour in distance:
                continue
            distance[neighbour] = distance[current] + 1
            parent[neighbour] = current
            queue.append(neighbour)
    return distance, parent


def recover_path(parent: dict[int, int | None], endpoint: int) -> list[int]:
    """Recover a root-to-endpoint path from BFS parents."""

    reverse_path = [endpoint]
    while parent[reverse_path[-1]] is not None:
        reverse_path.append(parent[reverse_path[-1]])  # type: ignore[arg-type]
    return list(reversed(reverse_path))


def build_r1_witness(
    graph: nx.Graph,
    girth: int,
    local_alpha: int,
    centre: int,
    independent_neighbours: Sequence[int],
) -> dict[str, object]:
    """Construct and validate the R1 star/geodesic witness."""

    independent_set = set(independent_neighbours)
    target = local_alpha + math.floor(girth / 2) - 1

    if girth == 0:
        kind = "forest_star"
        r = None
        path = [centre]
        geodesic_exists = True
        witness_vertices = sorted(independent_set | {centre})
    elif girth == 3:
        kind = "triangle_star"
        r = 0
        path = [centre]
        geodesic_exists = True
        witness_vertices = sorted(independent_set | {centre})
    else:
        kind = "star_plus_geodesic"
        r = math.floor(girth / 2) - 1
        distance, parent = bfs_from(graph, centre)
        endpoints = sorted(v for v, d in distance.items() if d == r)
        geodesic_exists = bool(endpoints)
        path = recover_path(parent, endpoints[0]) if endpoints else []
        witness_vertices = sorted(independent_set | set(path) | {centre})

    witness_is_tree = is_induced_tree(graph, witness_vertices)
    witness_size = len(witness_vertices)
    size_bound_holds = witness_size >= target
    path_edges_exist = all(
        graph.has_edge(path[index], path[index + 1])
        for index in range(max(0, len(path) - 1))
    )

    if path:
        distance_from_centre, _ = bfs_from(graph, centre)
        path_is_geodesic = (
            path[0] == centre
            and path_edges_exist
            and distance_from_centre[path[-1]] == len(path) - 1
        )
    else:
        path_is_geodesic = False

    construction_holds = bool(
        geodesic_exists
        and path_is_geodesic
        and witness_is_tree
        and size_bound_holds
    )
    return {
        "kind": kind,
        "centre": centre,
        "independent_neighbours": sorted(independent_neighbours),
        "r": r,
        "path": path,
        "path_is_geodesic": path_is_geodesic,
        "geodesic_exists": geodesic_exists,
        "witness_vertices": witness_vertices,
        "witness_size": witness_size,
        "required_theorem_lhs": target,
        "witness_is_induced_tree": witness_is_tree,
        "size_bound_holds": size_bound_holds,
        "construction_holds": construction_holds,
    }


def analyse_graph(atlas_index: int, atlas_graph: nx.Graph) -> dict[str, object]:
    """Compute all exact quantities and certificates for one atlas graph."""

    graph = canonical_graph(atlas_graph)
    order = graph.number_of_nodes()
    size = graph.number_of_edges()
    girth = exact_girth(graph)
    local_alpha, centre, independent_neighbours, local_values = (
        maximum_local_independence(graph)
    )
    induced_tree_size, induced_tree_vertices = maximum_induced_tree(graph)
    theorem_lhs = math.floor(girth / 2) - 1 + local_alpha
    theorem_holds = theorem_lhs <= induced_tree_size
    witness = build_r1_witness(
        graph, girth, local_alpha, centre, independent_neighbours
    )

    failure_reasons: list[str] = []
    theorem_domain = order >= 2
    if theorem_domain and not theorem_holds:
        failure_reasons.append("conjectured_inequality_failed")
    if theorem_domain and girth > 0 and not witness["construction_holds"]:
        failure_reasons.append("cyclic_r1_construction_failed")

    return {
        "atlas_index": atlas_index,
        "atlas_name": atlas_graph.name,
        "graph6": graph6(graph),
        "order": order,
        "size": size,
        "edges": [list(edge) for edge in sorted(graph.edges())],
        "theorem_domain": theorem_domain,
        "is_cyclic": girth > 0,
        "girth": girth,
        "max_local_independence": local_alpha,
        "local_independence_by_vertex": local_values,
        "maximising_vertex": centre,
        "max_independent_neighbour_set": independent_neighbours,
        "largest_induced_tree_size": induced_tree_size,
        "largest_induced_tree_vertices": induced_tree_vertices,
        "theorem_lhs": theorem_lhs,
        "theorem_slack": induced_tree_size - theorem_lhs,
        "theorem_holds": theorem_holds,
        "r1_witness": witness,
        "failure_reasons": failure_reasons,
    }


def run_internal_self_checks() -> None:
    """Check the independent primitives on small named graphs."""

    expected_girths = [
        (nx.path_graph(5), 0),
        (nx.cycle_graph(3), 3),
        (nx.cycle_graph(4), 4),
        (nx.complete_graph(4), 3),
    ]
    for graph, expected in expected_girths:
        actual = exact_girth(graph)
        if actual != expected:
            raise AssertionError(
                f"girth self-check failed: expected {expected}, got {actual}"
            )

    alpha, centre, independent_neighbours, _ = maximum_local_independence(
        nx.cycle_graph(5)
    )
    if alpha != 2 or len(independent_neighbours) != 2:
        raise AssertionError("local-independence self-check failed on C5")
    if centre not in nx.cycle_graph(5):
        raise AssertionError("invalid local-independence centre")

    tree_size, _ = maximum_induced_tree(nx.cycle_graph(5))
    if tree_size != 4:
        raise AssertionError("maximum-induced-tree self-check failed on C5")


def sha256_file(path: Path) -> str:
    """Return a file's SHA-256 digest."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    """Write deterministic, human-readable JSON."""

    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="directory for JSON/JSONL artifacts (default: script directory)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    output_dir: Path = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    run_internal_self_checks()

    atlas = nx.graph_atlas_g()
    connected_entries: list[tuple[int, nx.Graph]] = []
    for atlas_index, graph in enumerate(atlas):
        if graph.number_of_nodes() == 0:
            continue
        if nx.is_connected(graph):
            connected_entries.append((atlas_index, graph))
    connected_entries.sort(
        key=lambda item: (
            item[1].number_of_nodes(),
            item[1].number_of_edges(),
            item[0],
        )
    )

    records: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    by_order: dict[str, dict[str, int]] = {}

    for atlas_index, graph in connected_entries:
        record = analyse_graph(atlas_index, graph)
        records.append(record)

        order_key = str(record["order"])
        order_counts = by_order.setdefault(
            order_key,
            {
                "connected": 0,
                "theorem_domain": 0,
                "cyclic": 0,
                "inequality_failures": 0,
                "cyclic_construction_failures": 0,
            },
        )
        order_counts["connected"] += 1
        if record["theorem_domain"]:
            order_counts["theorem_domain"] += 1
        if record["is_cyclic"]:
            order_counts["cyclic"] += 1
        if record["theorem_domain"] and not record["theorem_holds"]:
            order_counts["inequality_failures"] += 1
        if (
            record["theorem_domain"]
            and record["is_cyclic"]
            and not record["r1_witness"]["construction_holds"]  # type: ignore[index]
        ):
            order_counts["cyclic_construction_failures"] += 1

        if record["failure_reasons"]:
            failures.append(record)
            break

    results_path = output_dir / "atlas_check_results.jsonl"
    results_path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )

    domain_records = [record for record in records if record["theorem_domain"]]
    cyclic_domain_records = [
        record for record in domain_records if record["is_cyclic"]
    ]
    inequality_failures = [
        record for record in domain_records if not record["theorem_holds"]
    ]
    construction_failures = [
        record
        for record in cyclic_domain_records
        if not record["r1_witness"]["construction_holds"]  # type: ignore[index]
    ]

    fully_enumerated = len(records) == len(connected_entries)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if fully_enumerated and not failures else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "networkx_version": nx.__version__,
        "method": {
            "girth": "minimum edge-deleted endpoint distance plus one",
            "local_independence": "enumerate every neighbourhood subset",
            "largest_induced_tree": "enumerate vertex subsets in decreasing order",
            "r1": "maximum local independent star plus deterministic BFS geodesic",
            "failure_order": "(order, size, atlas_index)",
            "fail_fast": True,
        },
        "scope": {
            "atlas_entries": len(atlas),
            "connected_entries_including_singleton": len(connected_entries),
            "fully_enumerated": fully_enumerated,
            "processed_connected_entries": len(records),
            "processed_theorem_domain_entries": len(domain_records),
            "processed_cyclic_theorem_domain_entries": len(cyclic_domain_records),
            "processed_forest_theorem_domain_entries": len(domain_records)
            - len(cyclic_domain_records),
            "maximum_order": max(record["order"] for record in records),
        },
        "checks": {
            "inequality_failures": len(inequality_failures),
            "cyclic_r1_construction_failures": len(construction_failures),
            "total_failure_certificates": len(failures),
        },
        "extrema": {
            "minimum_theorem_slack": min(
                record["theorem_slack"] for record in domain_records
            ),
            "maximum_theorem_slack": max(
                record["theorem_slack"] for record in domain_records
            ),
            "maximum_girth": max(record["girth"] for record in domain_records),
            "maximum_local_independence": max(
                record["max_local_independence"] for record in domain_records
            ),
            "maximum_largest_induced_tree_size": max(
                record["largest_induced_tree_size"] for record in domain_records
            ),
        },
        "by_order": by_order,
        "smallest_failure": failures[0] if failures else None,
        "artifacts": {
            "detailed_results": results_path.name,
            "detailed_results_sha256": sha256_file(results_path),
            "failures": "atlas_check_failures.json",
            "summary": "atlas_check_summary.json",
        },
    }

    failures_path = output_dir / "atlas_check_failures.json"
    write_json(
        failures_path,
        {
            "schema_version": SCHEMA_VERSION,
            "failure_count": len(failures),
            "smallest_failure": failures[0] if failures else None,
            "failures": failures,
        },
    )
    summary["artifacts"]["failures_sha256"] = sha256_file(failures_path)  # type: ignore[index]

    summary_path = output_dir / "atlas_check_summary.json"
    write_json(summary_path, summary)

    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
