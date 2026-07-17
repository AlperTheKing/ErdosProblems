#!/usr/bin/env python3
"""Exact backbone scan for zero-slack C23 image optimizers."""

from __future__ import annotations

import argparse
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
C78_PATH = ROOT / "problems/424/compute/wave5/C78_minimal_image_audit.py"
SPEC = importlib.util.spec_from_file_location("c78", C78_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load C78")
C78 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C78)


def build(cutoff: int):
    values = [n for n in range(2, cutoff + 1) if C78.allowed(n)]
    pairs = {n: C78.admissible_pairs(n) for n in values}
    model = cp_model.CpModel()
    source = {n: model.new_bool_var(f"s_{n}") for n in values}
    image = {n: model.new_bool_var(f"f_{n}") for n in values}
    model.add(source[2] == 1)
    model.add(source[3] == 1)
    model.add(image[2] == 1)
    model.add(image[3] == 1)

    for n in values:
        if n in (2, 3):
            continue
        witnesses = []
        for index, (left, right) in enumerate(pairs[n]):
            model.add(source[left] + source[right] - 1 <= source[n])
            witnesses.append(
                C78.bool_and(model, source[left], source[right], f"w_{n}_{index}")
            )
        if witnesses:
            for witness in witnesses:
                model.add(image[n] >= witness)
            model.add(image[n] <= sum(witnesses))
        else:
            model.add(image[n] == 0)

    boundaries = {}
    for parent in values:
        child = 2 * parent - 1
        if child <= cutoff:
            boundaries[parent] = C78.boundary_var(
                model, image[parent], image[child], f"b_{parent}_{child}"
            )

    hard = [n for n in values if C78.hard_shape(n, pairs[n])]
    excess = sum(1 - image[n] for n in hard) - sum(boundaries.values())

    shell = {}
    for root in range(2, cutoff + 1, 2):
        if not C78.allowed(root):
            continue
        top = C78.chain_top(root, cutoff)
        if C78.hard_shape(root, pairs[root]):
            # Upward closure makes top-absence equivalent to an unhealed root.
            event = model.new_bool_var(f"unhealed_hard_{root}")
            model.add(event + image[top] == 1)
            shell[f"unhealed_hard_{root}"] = event
        else:
            event = model.new_bool_var(f"healed_nonhard_{root}")
            model.add(event <= 1 - image[root])
            model.add(event <= image[top])
            model.add(event >= image[top] - image[root])
            shell[f"healed_nonhard_{root}"] = event

    model.maximize(excess)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        raise RuntimeError((cutoff, solver.status_name(status)))
    optimum = round(solver.objective_value)
    if optimum != 0:
        raise RuntimeError((cutoff, "not tight", optimum))

    model.add(excess == optimum)
    model.clear_objective()
    variables = {
        **{f"source_{n}": var for n, var in source.items()},
        **{f"image_{n}": var for n, var in image.items()},
        **{f"boundary_{parent}": var for parent, var in boundaries.items()},
        **shell,
    }
    return model, variables, len(values), len(hard)


def feasible(base: cp_model.CpModel, index: int, value: int, seconds: float) -> bool:
    model = base.clone()
    variable = model.get_bool_var_from_proto_index(index)
    model.add(variable == value)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    status = solver.solve(model)
    if status == cp_model.UNKNOWN:
        raise RuntimeError((variable.name, value, "UNKNOWN"))
    return status in (cp_model.FEASIBLE, cp_model.OPTIMAL)


def scan(cutoff: int, workers: int, seconds: float) -> dict:
    base, variables, value_count, hard_count = build(cutoff)
    queries = [
        (name, variable.index, value)
        for name, variable in variables.items()
        for value in (0, 1)
    ]

    def run(query):
        name, index, value = query
        return name, value, feasible(base, index, value, seconds)

    possible = {name: [False, False] for name in variables}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for name, value, result in pool.map(run, queries):
            possible[name][value] = result

    classes = {"forced_zero": [], "forced_one": [], "free": []}
    for name, (can_zero, can_one) in sorted(possible.items()):
        if can_zero and can_one:
            classes["free"].append(name)
        elif can_zero:
            classes["forced_zero"].append(name)
        elif can_one:
            classes["forced_one"].append(name)
        else:
            raise RuntimeError((cutoff, name, "no optimal assignment"))

    summary = {}
    for prefix in ("source_", "image_", "boundary_", "unhealed_", "healed_"):
        summary[prefix.rstrip("_")] = {
            key: sum(name.startswith(prefix) for name in names)
            for key, names in classes.items()
        }
    return {
        "cutoff": cutoff,
        "allowed_values": value_count,
        "hard_shapes": hard_count,
        "zero_slack_optimum": 0,
        "class_counts": {key: len(names) for key, names in classes.items()},
        "category_counts": summary,
        "classes": classes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoffs", nargs="+", type=int, default=[54, 74, 186, 362])
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--seconds-per-query", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    rows = [scan(cutoff, args.workers, args.seconds_per_query) for cutoff in args.cutoffs]
    payload = {"schema_version": 1, "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    for row in rows:
        print(row["cutoff"], row["class_counts"], row["category_counts"])


if __name__ == "__main__":
    main()
