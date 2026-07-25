#!/usr/bin/env python3
"""
Erdos #30 SKTC v4 shell-graph spectral probe.

Input: v3 compression-shell result JSON.

For each fixed (k, D) shell, build a local transition graph:
  - nodes are canonical Sidon/Golomb rulers in that shell;
  - edges connect rulers that differ by moving one interior mark by +/- 1,
    modulo reflection.

Then compute graph/Laplacian observables:
  - connected components and isolated nodes;
  - graph Laplacian eigenvalues;
  - zero modes, algebraic connectivity, first positive spectral gap;
  - adjacent spacing and adjacent gap-ratio summaries for positive eigenvalues.

Claim ceiling:
  - finite shell-geometry / eigenvalue-spacing screening only;
  - not evidence for the asymptotic Erdos #30 conjecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np


TOL = 1e-9


def canonical_ruler(marks: list[int]) -> tuple[int, ...]:
    diameter = marks[-1]
    reflected = tuple(diameter - x for x in reversed(marks))
    return min(tuple(marks), reflected)


def orientations(marks: tuple[int, ...]) -> list[tuple[int, ...]]:
    diameter = marks[-1]
    reflected = tuple(diameter - x for x in reversed(marks))
    if reflected == marks:
        return [marks]
    return [marks, reflected]


def one_mark_neighbors(marks: tuple[int, ...], shell_set: set[tuple[int, ...]]) -> set[tuple[int, ...]]:
    out: set[tuple[int, ...]] = set()
    k = len(marks)
    for oriented in orientations(marks):
        values = list(oriented)
        for idx in range(1, k - 1):
            for step in (-1, 1):
                moved = values[:]
                moved[idx] += step
                if not (moved[idx - 1] < moved[idx] < moved[idx + 1]):
                    continue
                candidate = canonical_ruler(moved)
                if candidate != marks and candidate in shell_set:
                    out.add(candidate)
    return out


def connected_components(adj: list[set[int]]) -> list[list[int]]:
    seen = [False] * len(adj)
    components: list[list[int]] = []
    for start in range(len(adj)):
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


def spacing_summary(values: list[float]) -> dict[str, Any]:
    if len(values) < 2:
        return {
            "count": 0,
            "min": None,
            "mean": None,
            "max": None,
            "adjacent_gap_ratio_mean": None,
        }
    spacings = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    ratios = []
    for i in range(len(spacings) - 1):
        a = spacings[i]
        b = spacings[i + 1]
        if max(a, b) > TOL:
            ratios.append(min(a, b) / max(a, b))
    return {
        "count": len(spacings),
        "min": min(spacings),
        "mean": sum(spacings) / len(spacings),
        "max": max(spacings),
        "adjacent_gap_ratio_mean": (sum(ratios) / len(ratios)) if ratios else None,
    }


def spectrum_for_shell(records: list[dict[str, Any]]) -> dict[str, Any]:
    rulers = sorted({tuple(record["marks"]) for record in records})
    n = len(rulers)
    if n == 0:
        return {
            "node_count": 0,
            "edge_count": 0,
            "component_count": 0,
            "component_sizes": [],
            "isolated_node_count": 0,
            "average_degree": 0.0,
            "laplacian_eigenvalues": [],
            "zero_mode_count": 0,
            "algebraic_connectivity_lambda_1": None,
            "first_positive_laplacian_eigenvalue": None,
            "positive_laplacian_spacing": spacing_summary([]),
            "adjacency_eigenvalues": [],
            "adjacency_spacing": spacing_summary([]),
        }

    index = {ruler: i for i, ruler in enumerate(rulers)}
    shell_set = set(rulers)
    adj: list[set[int]] = [set() for _ in rulers]
    for i, ruler in enumerate(rulers):
        for neighbor in one_mark_neighbors(ruler, shell_set):
            j = index[neighbor]
            adj[i].add(j)
            adj[j].add(i)

    edge_count = sum(len(neighbors) for neighbors in adj) // 2
    degrees = [len(neighbors) for neighbors in adj]
    components = connected_components(adj)

    adjacency = np.zeros((n, n), dtype=float)
    for i, neighbors in enumerate(adj):
        for j in neighbors:
            adjacency[i, j] = 1.0
    laplacian = np.diag(degrees) - adjacency

    lap_eigs = [float(x) for x in np.linalg.eigvalsh(laplacian)]
    adj_eigs = [float(x) for x in np.linalg.eigvalsh(adjacency)]
    zero_mode_count = sum(1 for x in lap_eigs if abs(x) <= TOL)
    positive_lap = [x for x in lap_eigs if x > TOL]

    return {
        "node_count": n,
        "edge_count": edge_count,
        "component_count": len(components),
        "component_sizes": sorted((len(c) for c in components), reverse=True),
        "isolated_node_count": sum(1 for d in degrees if d == 0),
        "average_degree": (sum(degrees) / n) if n else 0.0,
        "max_degree": max(degrees) if degrees else 0,
        "laplacian_eigenvalues": lap_eigs,
        "zero_mode_count": zero_mode_count,
        "algebraic_connectivity_lambda_1": lap_eigs[1] if n > 1 else None,
        "first_positive_laplacian_eigenvalue": positive_lap[0] if positive_lap else None,
        "positive_laplacian_spacing": spacing_summary(positive_lap),
        "adjacency_eigenvalues": adj_eigs,
        "adjacency_spacing": spacing_summary(adj_eigs),
    }


def shell_key(record: dict[str, Any]) -> tuple[int, int, int, int]:
    return (
        int(record["k"]),
        int(record["optimal_diameter"]),
        int(record["shell_delta"]),
        int(record["shell_diameter"]),
    )


def trend(points: list[tuple[int, float | None]]) -> dict[str, Any]:
    filtered = [(x, y) for x, y in points if y is not None and math.isfinite(float(y))]
    if len(filtered) < 2:
        return {"points": points, "slope_per_delta": None}
    xs = [float(x) for x, _ in filtered]
    ys = [float(y) for _, y in filtered]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    slope = None if denom == 0 else sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom
    return {"points": points, "slope_per_delta": slope}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v3-results", type=Path, default=Path("results/erdos30_sktc_compression_shell_v3_RESULTS.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.v3_results.read_text())
    by_shell: dict[tuple[int, int, int, int], list[dict[str, Any]]] = {}
    for record in data.get("records", []):
        by_shell.setdefault(shell_key(record), []).append(record)

    shell_spectra: list[dict[str, Any]] = []
    for key, records in sorted(by_shell.items()):
        k, optimal_diameter, shell_delta, shell_diameter = key
        spectrum = spectrum_for_shell(records)
        shell_spectra.append({
            "k": k,
            "optimal_diameter": optimal_diameter,
            "shell_delta": shell_delta,
            "shell_diameter": shell_diameter,
            **spectrum,
        })

    trends_by_k: dict[str, Any] = {}
    for k in sorted({item["k"] for item in shell_spectra}):
        items = [item for item in shell_spectra if item["k"] == k]
        trends_by_k[str(k)] = {
            "node_count": trend([(item["shell_delta"], float(item["node_count"])) for item in items]),
            "component_count": trend([(item["shell_delta"], float(item["component_count"])) for item in items]),
            "isolated_node_count": trend([(item["shell_delta"], float(item["isolated_node_count"])) for item in items]),
            "average_degree": trend([(item["shell_delta"], float(item["average_degree"])) for item in items]),
            "first_positive_laplacian_eigenvalue": trend([
                (item["shell_delta"], item["first_positive_laplacian_eigenvalue"]) for item in items
            ]),
            "adjacent_gap_ratio_mean": trend([
                (item["shell_delta"], item["positive_laplacian_spacing"]["adjacent_gap_ratio_mean"]) for item in items
            ]),
        }

    nontrivial = [item for item in shell_spectra if item["node_count"] >= 3]
    disconnected = [item for item in shell_spectra if item["component_count"] > 1]
    payload = {
        "probe": "erdos30_sktc_shell_graph_spectrum_v4",
        "claim_ceiling": "finite shell-geometry and eigenvalue-spacing screening only; not asymptotic theorem evidence",
        "v3_results_source": str(args.v3_results),
        "shell_count": len(shell_spectra),
        "nontrivial_shell_count_node_ge_3": len(nontrivial),
        "disconnected_shell_count": len(disconnected),
        "shell_spectra": shell_spectra,
        "trends_by_k": trends_by_k,
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
