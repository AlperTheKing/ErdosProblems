#!/usr/bin/env python3
"""
Erdos #30 SKTC v5 finite shell-graph certificate.

For one fixed shell (k, D), read the exact shell vertices from the v3
compression-shell result, enumerate local one-mark moves, and emit a complete
certificate:

  - vertices;
  - every oriented candidate one-mark move;
  - accepted edge targets;
  - rejected move witnesses: order violation or repeated-difference collision;
  - graph consequences: components >= V - E, and for E=0, zero modes = V.

Claim ceiling:
  - finite shell-geometry certificate only;
  - not progress on the asymptotic Erdos #30 conjecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Any


def canonical_ruler(marks: list[int]) -> tuple[int, ...]:
    diameter = marks[-1]
    reflected = tuple(diameter - x for x in reversed(marks))
    return min(tuple(marks), reflected)


def orientations(marks: tuple[int, ...]) -> list[dict[str, Any]]:
    diameter = marks[-1]
    reflected = tuple(diameter - x for x in reversed(marks))
    out = [{"name": "canonical", "marks": list(marks)}]
    if reflected != marks:
        out.append({"name": "reflected", "marks": list(reflected)})
    return out


def repeated_difference_witness(marks: list[int]) -> dict[str, Any] | None:
    seen: dict[int, tuple[int, int]] = {}
    for i, a in enumerate(marks):
        for b in marks[:i]:
            diff = a - b
            if diff <= 0:
                return {
                    "type": "nonpositive_difference",
                    "difference": diff,
                    "pair": [a, b],
                }
            if diff in seen:
                c, d = seen[diff]
                return {
                    "type": "repeated_difference_collision",
                    "difference": diff,
                    "pair_1": [c, d],
                    "pair_2": [a, b],
                    "equation": f"{c}-{d} = {a}-{b} = {diff}",
                }
            seen[diff] = (a, b)
    return None


def is_sidon(marks: list[int]) -> bool:
    return repeated_difference_witness(marks) is None


def connected_components(vertex_count: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    adj: list[set[int]] = [set() for _ in range(vertex_count)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen = [False] * vertex_count
    components: list[list[int]] = []
    for start in range(vertex_count):
        if seen[start]:
            continue
        queue: deque[int] = deque([start])
        seen[start] = True
        component: list[int] = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for nxt in adj[node]:
                if not seen[nxt]:
                    seen[nxt] = True
                    queue.append(nxt)
        components.append(component)
    return components


def load_shell_vertices(v3_results: Path, k: int, diameter: int) -> list[tuple[int, ...]]:
    data = json.loads(v3_results.read_text())
    vertices = {
        tuple(record["marks"])
        for record in data.get("records", [])
        if int(record["k"]) == k and int(record["shell_diameter"]) == diameter
    }
    return sorted(vertices)


def certify_shell(vertices: list[tuple[int, ...]], k: int, diameter: int) -> dict[str, Any]:
    vertex_index = {vertex: idx for idx, vertex in enumerate(vertices)}
    vertex_set = set(vertices)
    candidate_moves: list[dict[str, Any]] = []
    accepted_edges: set[tuple[int, int]] = set()
    rejected_counts = {
        "order_violation": 0,
        "repeated_difference_collision": 0,
        "valid_candidate_missing_from_shell": 0,
    }

    for source_idx, source in enumerate(vertices):
        for orientation in orientations(source):
            oriented = orientation["marks"]
            for mark_index in range(1, k - 1):
                for step in (-1, 1):
                    moved = oriented[:]
                    old_value = moved[mark_index]
                    moved[mark_index] += step
                    candidate_id = len(candidate_moves)
                    base = {
                        "candidate_id": candidate_id,
                        "source_vertex_index": source_idx,
                        "source_canonical_marks": list(source),
                        "orientation": orientation["name"],
                        "oriented_source_marks": oriented,
                        "moved_mark_index": mark_index,
                        "old_value": old_value,
                        "new_value": moved[mark_index],
                        "step": step,
                        "candidate_oriented_marks": moved,
                    }

                    if not (moved[mark_index - 1] < moved[mark_index] < moved[mark_index + 1]):
                        rejected_counts["order_violation"] += 1
                        candidate_moves.append({
                            **base,
                            "status": "rejected",
                            "reason": "order_violation",
                            "witness": {
                                "left_neighbor": moved[mark_index - 1],
                                "new_value": moved[mark_index],
                                "right_neighbor": moved[mark_index + 1],
                                "required": "left_neighbor < new_value < right_neighbor",
                            },
                        })
                        continue

                    candidate_canonical = canonical_ruler(moved)
                    collision = repeated_difference_witness(sorted(moved))
                    if collision is not None:
                        rejected_counts["repeated_difference_collision"] += 1
                        candidate_moves.append({
                            **base,
                            "status": "rejected",
                            "reason": "repeated_difference_collision",
                            "candidate_canonical_marks": list(candidate_canonical),
                            "witness": collision,
                        })
                        continue

                    if candidate_canonical not in vertex_set:
                        rejected_counts["valid_candidate_missing_from_shell"] += 1
                        candidate_moves.append({
                            **base,
                            "status": "rejected",
                            "reason": "valid_candidate_missing_from_shell",
                            "candidate_canonical_marks": list(candidate_canonical),
                            "witness": {
                                "note": "The candidate is Sidon but absent from the shell vertex list; this indicates an incomplete input shell.",
                            },
                        })
                        continue

                    target_idx = vertex_index[candidate_canonical]
                    edge = tuple(sorted((source_idx, target_idx)))
                    if source_idx != target_idx:
                        accepted_edges.add(edge)
                    candidate_moves.append({
                        **base,
                        "status": "accepted",
                        "reason": "valid_one_mark_edge",
                        "candidate_canonical_marks": list(candidate_canonical),
                        "target_vertex_index": target_idx,
                        "edge": list(edge),
                    })

    components = connected_components(len(vertices), accepted_edges)
    edge_list = [list(edge) for edge in sorted(accepted_edges)]
    v_count = len(vertices)
    e_count = len(accepted_edges)
    component_lower_bound = v_count - e_count
    consequence = {
        "vertex_count": v_count,
        "edge_count": e_count,
        "component_count": len(components),
        "component_sizes": sorted((len(c) for c in components), reverse=True),
        "component_lower_bound_v_minus_e": component_lower_bound,
        "component_bound_tight": len(components) == component_lower_bound,
        "laplacian_zero_modes": len(components),
        "zero_modes_equal_components": True,
        "if_edge_count_zero_then_zero_modes_equal_vertices": e_count == 0 and len(components) == v_count,
    }
    return {
        "k": k,
        "diameter": diameter,
        "vertices": [list(vertex) for vertex in vertices],
        "vertex_count": v_count,
        "candidate_move_count": len(candidate_moves),
        "accepted_edges": edge_list,
        "accepted_edge_count": e_count,
        "rejected_counts": rejected_counts,
        "all_candidates_accounted_for": len(candidate_moves)
        == sum(rejected_counts.values()) + len([m for m in candidate_moves if m["status"] == "accepted"]),
        "all_vertices_are_sidon": all(is_sidon(list(vertex)) for vertex in vertices),
        "candidate_moves": candidate_moves,
        "graph_consequence": consequence,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v3-results", type=Path, default=Path("results/erdos30_sktc_compression_shell_v3_RESULTS.json"))
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--diameter", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    vertices = load_shell_vertices(args.v3_results, args.k, args.diameter)
    if not vertices:
        raise SystemExit(f"No shell vertices found for k={args.k}, diameter={args.diameter}")

    certificate = certify_shell(vertices, args.k, args.diameter)
    payload = {
        "probe": "erdos30_sktc_finite_shell_graph_certificate_v5",
        "claim_ceiling": "finite shell-geometry certificate only; not asymptotic theorem evidence",
        "v3_results_source": str(args.v3_results),
        "certificate": certificate,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.out.write_text(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    args.out.with_suffix(args.out.suffix + ".sha256").write_text(f"{sha}  {args.out}\n")
    print(f"Wrote {args.out}")
    print(f"sha256 {sha}")


if __name__ == "__main__":
    main()
