#!/usr/bin/env python3
"""Exact large-cutoff replay of the C60 contracted max-flow certificate."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
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


C56 = load_module("c60_large_c56", COMPUTE / "C56_image_lp_dual.py")


def exact_flow(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    pairs = {n: C56.admissible_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    hard = {n for n in values if C56.hard_shape(n, pairs[n])}
    splitless = {n for n in holes if n not in (2, 3) and not pairs[n]}
    hard_holes = hard & holes
    generated_hard = hard & generated
    finite_arc_bound = len(hard_holes) + sum(2 * n - 1 <= limit for n in holes)
    infinity = finite_arc_bound + 1
    source, sink = limit + 1, limit + 2
    capacities: dict[tuple[int, int], int] = {}

    def add(u: int, v: int, capacity: int) -> None:
        capacities[u, v] = capacities.get((u, v), 0) + capacity

    for h in hard_holes:
        add(source, h, 1)
    for root in splitless:
        add(source, root, infinity)
    unary_count = 0
    seed_count = 0
    for n in holes:
        for a, b in pairs[n]:
            if (a in generated) != (b in generated):
                add(n, b if a in generated else a, infinity)
                unary_count += 1
        child = 2 * n - 1
        if child <= limit:
            add(n, sink if child in generated else child, 1)
            seed_count += 1

    rows = np.fromiter((edge[0] for edge in capacities), dtype=np.int64)
    cols = np.fromiter((edge[1] for edge in capacities), dtype=np.int64)
    data = np.fromiter(capacities.values(), dtype=np.int64)
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(limit + 3, limit + 3), dtype=np.int64
    ).tocsr()
    flow = int(maximum_flow(matrix, source, sink).flow_value)
    return {
        "limit": limit,
        "hard_count": len(hard),
        "hard_holes": len(hard_holes),
        "generated_hard": len(generated_hard),
        "splitless": len(splitless),
        "unary_arcs": unary_count,
        "seed_arcs": seed_count,
        "network_edges": len(capacities),
        "exact_max_flow": flow,
        "reserve": flow - len(hard_holes),
        "predicted_c56_objective": flow + len(generated_hard),
    }


def known_objectives() -> dict[int, int]:
    out: dict[int, int] = {}
    for name in (
        "C56_dual_cert.json",
        "C56_dual_cert_large.json",
        "C56_dual_cert_100k.json",
    ):
        for cert in json.loads((COMPUTE / name).read_text(encoding="utf-8")):
            out[int(cert["limit"])] = int(round(float(cert["floating_objective"])))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    known = known_objectives()
    rows = []
    for limit in args.limits:
        row = exact_flow(limit)
        row["saved_c56_objective"] = known.get(limit)
        row["objective_match"] = (
            row["saved_c56_objective"] is None
            or row["saved_c56_objective"] == row["predicted_c56_objective"]
        )
        if row["reserve"] < 0 or not row["objective_match"]:
            raise RuntimeError(f"failed exact large check at {limit}: {row}")
        rows.append(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
