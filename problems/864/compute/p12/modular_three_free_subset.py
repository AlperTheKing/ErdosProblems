"""Exact maximum 3-sum-free subsets of translated modular Sidon sets.

For D subset Z/v and a translation t, the odd lift

    E = {1 + 2(c+t mod v) : c selected from D}

is 3-sum-free whenever no selected indices satisfy

    d - a - b - c = 1 + 2t (mod v),

where repeated summands a,b,c are allowed.  For each target r=2t this is a
finite hypergraph independent-set problem.  We solve every residue exactly by
CP-SAT and then verify the best literal odd lift E={2c+1} independently.
"""

from __future__ import annotations

import argparse
import itertools
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from ortools.sat.python import cp_model

from algebraic_scan import bose_chowla, ruzsa, singer


def relation_hypergraphs(values: tuple[int, ...], modulus: int) -> list[set[tuple[int, ...]]]:
    p = len(values)
    out: list[set[tuple[int, ...]]] = [set() for _ in range(modulus)]
    for a in range(p):
        for b in range(a, p):
            for c in range(b, p):
                triple = values[a] + values[b] + values[c]
                for d in range(p):
                    residue = (values[d] - triple) % modulus
                    out[residue].add(tuple(sorted({a, b, c, d})))
    return out


def solve_one(task: tuple[int, int, tuple[tuple[int, ...], ...], float]) -> dict[str, object]:
    target, p, edges, seconds = task
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x_{i}") for i in range(p)]
    for edge in edges:
        model.add(sum(x[i] for i in edge) <= len(edge) - 1)
    model.maximize(sum(x))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.random_seed = 864 + target
    status = solver.solve(model)
    return {
        "target": target,
        "status": solver.status_name(status),
        "optimal": status == cp_model.OPTIMAL,
        "size": int(round(solver.objective_value)) if status in (cp_model.FEASIBLE, cp_model.OPTIMAL) else None,
        "selected": [i for i, var in enumerate(x) if status in (cp_model.FEASIBLE, cp_model.OPTIMAL) and solver.value(var)],
        "hyperedges": len(edges),
        "wall_seconds": solver.wall_time,
    }


def modular_sidon(values: list[int], modulus: int) -> bool:
    sums = [(values[i] + values[j]) % modulus for i in range(len(values)) for j in range(i, len(values))]
    return len(sums) == len(set(sums))


def modular_three_free(values: list[int], modulus: int, offset: int = 0) -> bool:
    triples = {
        (a + b + c + offset) % modulus
        for a in values
        for b in values
        for c in values
    }
    return not (set(values) & triples)


def literal_sidon(values: list[int]) -> bool:
    sums = [values[i] + values[j] for i in range(len(values)) for j in range(i, len(values))]
    return len(sums) == len(set(sums))


def literal_three_free(values: list[int]) -> bool:
    triples = {a + b + c for a in values for b in values for c in values}
    return not (set(values) & triples)


def run(
    family: str,
    parameter: int,
    workers: int,
    seconds_per_residue: float,
) -> dict[str, object]:
    generators = {"bose": bose_chowla, "singer": singer, "ruzsa": ruzsa}
    modulus, residues, metadata = generators[family](parameter)
    graphs = relation_hypergraphs(residues, modulus)
    tasks = [
        (target, len(residues), tuple(sorted(graphs[target])), seconds_per_residue)
        for target in range(modulus)
    ]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        solved = list(pool.map(solve_one, tasks, chunksize=1))
    if not all(x["optimal"] for x in solved):
        failed = [x["target"] for x in solved if not x["optimal"]]
        raise RuntimeError(f"non-optimal residues: {failed[:20]}")
    def best_geometry(solution: dict[str, object]):
        selected = [residues[i] for i in solution["selected"]]
        candidates = []
        for translation in range(modulus):
            offset = (int(solution["target"]) - 2 * translation) % modulus
            if offset == 0:
                offset = modulus
            translated = sorted((x + translation) % modulus for x in selected)
            lift = [offset + 2 * x for x in translated]
            candidates.append((max(lift), offset, translation, translated, lift))
        return min(candidates)

    geometries = [(best_geometry(solution), solution) for solution in solved]
    geometry, best = min(
        geometries,
        key=lambda item: (-int(item[1]["size"]), item[0][0], int(item[1]["target"])),
    )
    _, offset, translation, selected_residues, odd_lift = geometry
    if not modular_sidon(selected_residues, modulus):
        raise AssertionError("selected translate lost modular Sidonicity")
    if not modular_three_free(selected_residues, modulus, offset=offset):
        raise AssertionError("selected translate is not modular offset-3-sum-free")
    if not literal_sidon(odd_lift) or not literal_three_free(odd_lift):
        raise AssertionError("same-parity integer lift failed literal verification")
    k = len(odd_lift)
    return {
        "family": family,
        "parameter": parameter,
        "modulus": modulus,
        "source_size": len(residues),
        "metadata": metadata,
        "workers": workers,
        "seconds_per_residue": seconds_per_residue,
        "all_residues_optimal": True,
        "best_target_relation": best["target"],
        "offset_G": offset,
        "translation": translation,
        "best_size": k,
        "selected_indices": best["selected"],
        "translated_residues": selected_residues,
        "odd_lift": odd_lift,
        "odd_lift_max": max(odd_lift),
        "odd_lift_max_over_k2": str(Fraction(max(odd_lift), k * k)),
        "beats_three": max(odd_lift) < 3 * k * k,
        "residue_size_distribution": {
            str(size): sum(1 for x in solved if x["size"] == size)
            for size in sorted({int(x["size"]) for x in solved})
        },
        "max_hyperedges": max(int(x["hyperedges"]) for x in solved),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=("bose", "singer", "ruzsa"), required=True)
    parser.add_argument("--parameters", nargs="+", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seconds-per-residue", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error("--workers must be in [1,16] for the P12 lane")
    records = [
        run(args.family, parameter, args.workers, args.seconds_per_residue)
        for parameter in args.parameters
    ]
    args.output.write_text(
        "\n".join(json.dumps(x, sort_keys=True) for x in records) + "\n",
        encoding="ascii",
    )
    for record in records:
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
