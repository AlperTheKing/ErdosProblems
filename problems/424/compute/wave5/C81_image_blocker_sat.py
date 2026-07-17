#!/usr/bin/env python3
"""Exact CP-SAT falsifier for image-realizable blocker cuts.

Let ``v_n`` mean that ``n`` is absent from a forward-closed source S.  For
every admissible factor pair ``a*b=n+1``, forward closure is the Horn clause

    v_n -> (v_a or v_b).

Thus the source complement is a self-blocking cut.  A nonseed ``n`` is absent
from the image F(S) exactly when every factor pair of n is hit by this cut.

The objective uses seed-2 chains instead of boundary variables.  At cutoff X,
a hard even root r contributes ``1 - f_top(r,X)`` to H-Q.  A nonhard even
root contributes ``f_r - f_top(r,X)``.  Here f is exact image membership.
Only source variables through (X+1)//2 and image gates appearing in these
root/top expressions are constructed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import ortools
from ortools.sat.python import cp_model


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def pair_iter(limit: int):
    """Yield each allowed distinct factorization n+1=a*b once."""
    for left in range(2, math.isqrt(limit + 1) + 1):
        if not allowed(left):
            continue
        for right in range(left + 1, (limit + 1) // left + 1):
            if allowed(right):
                yield left * right - 1, left, right


@dataclass(frozen=True)
class Structure:
    limit: int
    values: tuple[int, ...]
    pairs: tuple[tuple[tuple[int, int], ...], ...]
    hard: tuple[int, ...]


def build_structure(limit: int) -> Structure:
    pairs: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]
    for value, left, right in pair_iter(limit):
        pairs[value].append((left, right))
    values = tuple(value for value in range(2, limit + 1) if allowed(value))
    hard = []
    for value in values:
        if value % 2 or not pairs[value]:
            continue
        if (value + 1) % 3:
            hard.append(value)
            continue
        parent = (value + 1) // 3
        if not (allowed(parent) and parent != 3):
            hard.append(value)
    return Structure(
        limit=limit,
        values=values,
        pairs=tuple(tuple(local) for local in pairs),
        hard=tuple(hard),
    )


def chain_top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def objective_terms(
    cutoff: int, hard_set: set[int]
) -> tuple[int, dict[int, int], list[int]]:
    """Return constant, image coefficients, and even roots for H_F-Q_F."""
    constant = 0
    coefficients: dict[int, int] = {}
    roots = [
        root
        for root in range(2, cutoff + 1, 2)
        if allowed(root)
    ]

    def add(value: int, coefficient: int) -> None:
        coefficients[value] = coefficients.get(value, 0) + coefficient

    for root in roots:
        top = chain_top(root, cutoff)
        if root in hard_set:
            constant += 1
            add(top, -1)
        else:
            add(root, 1)
            add(top, -1)
    return constant, {n: c for n, c in coefficients.items() if c}, roots


def image_from_missing(
    cutoff: int,
    source_missing: set[int],
    pairs: tuple[tuple[tuple[int, int], ...], ...],
) -> set[int]:
    image = {2, 3}
    for value in range(4, cutoff + 1):
        if not allowed(value):
            continue
        if any(
            left not in source_missing and right not in source_missing
            for left, right in pairs[value]
        ):
            image.add(value)
    return image


def verify_source_closure(
    cutoff: int,
    source_missing: set[int],
    pairs: tuple[tuple[tuple[int, int], ...], ...],
) -> None:
    if 2 in source_missing or 3 in source_missing:
        raise RuntimeError("source complement contains a seed")
    for value in range(4, cutoff + 1):
        if not allowed(value) or value not in source_missing:
            continue
        for left, right in pairs[value]:
            if left not in source_missing and right not in source_missing:
                raise RuntimeError(
                    f"self-blocking failure at {left}*{right}-1={value}"
                )


def direct_statistics(
    cutoff: int,
    source_missing: set[int],
    structure: Structure,
) -> dict:
    local_missing = {value for value in source_missing if value <= cutoff}
    verify_source_closure(cutoff, local_missing, structure.pairs)
    image = image_from_missing(cutoff, local_missing, structure.pairs)
    hard_set = set(structure.hard)
    hard_holes = [
        value
        for value in structure.hard
        if value <= cutoff and value not in image
    ]
    boundaries = [
        2 * parent - 1
        for parent in range(2, (cutoff + 1) // 2 + 1)
        if allowed(parent)
        and parent not in image
        and 2 * parent - 1 in image
    ]
    unhealed_hard = []
    healed_nonhard = []
    for root in range(2, cutoff + 1, 2):
        if not allowed(root):
            continue
        top = chain_top(root, cutoff)
        if root in hard_set:
            if top not in image:
                unhealed_hard.append(root)
        elif root not in image and top in image:
            healed_nonhard.append(root)
    direct_excess = len(hard_holes) - len(boundaries)
    shell_excess = len(unhealed_hard) - len(healed_nonhard)
    if direct_excess != shell_excess:
        raise RuntimeError(
            f"shell identity failure at {cutoff}: {direct_excess}!={shell_excess}"
        )

    image_holes = [
        value
        for value in range(2, cutoff + 1)
        if allowed(value) and value not in image
    ]
    factorable_holes = [value for value in image_holes if structure.pairs[value]]
    single_hit = 0
    double_hit = 0
    for value in factorable_holes:
        for left, right in structure.pairs[value]:
            hits = int(left in local_missing) + int(right in local_missing)
            if hits == 0:
                raise RuntimeError(f"unblocked image hole at {value}")
            single_hit += hits == 1
            double_hit += hits == 2
    unsupported_source = [
        value
        for value in image_holes
        if value not in local_missing and value not in (2, 3)
    ]
    source_value_count = sum(
        allowed(value) for value in range(2, cutoff + 1)
    )
    return {
        "cutoff": cutoff,
        "objective_excess": direct_excess,
        "hard_hole_count": len(hard_holes),
        "boundary_count": len(boundaries),
        "hard_holes": hard_holes,
        "boundary_children": boundaries,
        "unhealed_hard_roots": unhealed_hard,
        "healed_nonhard_roots": healed_nonhard,
        "source_value_count": source_value_count,
        "source_missing_count": len(local_missing),
        "source_member_count": source_value_count - len(local_missing),
        "image_member_count": len(image),
        "image_hole_count": len(image_holes),
        "factorable_image_hole_count": len(factorable_holes),
        "unsupported_source_count": len(unsupported_source),
        "unsupported_source_first": unsupported_source[:20],
        "blocked_pair_count": single_hit + double_hit,
        "single_hit_pair_count": single_hit,
        "double_hit_pair_count": double_hit,
        "distinct_source_blockers_used": len(
            {
                parent
                for value in factorable_holes
                for pair in structure.pairs[value]
                for parent in pair
                if parent in local_missing
            }
        ),
    }


def add_exact_image_gate(
    model: cp_model.CpModel,
    value: int,
    local_pairs: tuple[tuple[int, int], ...],
    missing: dict[int, cp_model.IntVar],
    counters: Counter,
):
    if value in (2, 3):
        return 1
    if not local_pairs:
        return 0
    member = model.new_bool_var(f"f_{value}")
    selectors = []
    for index, (left, right) in enumerate(local_pairs):
        selector = model.new_bool_var(f"support_{value}_{index}")
        selectors.append(selector)
        model.add_implication(selector, missing[left].Not())
        model.add_implication(selector, missing[right].Not())
        model.add_bool_or([missing[left], missing[right], member])
        counters["support_pair_gates"] += 1
    model.add_bool_or([member.Not(), *selectors])
    counters["image_variables"] += 1
    counters["support_selectors"] += len(selectors)
    return member


def solve_group(task: dict) -> dict:
    cutoffs = tuple(task["cutoffs"])
    limit = max(cutoffs)
    workers = int(task["workers"])
    time_limit = float(task["time_limit"])
    random_seed = int(task["random_seed"])
    linearization_level = int(task["linearization_level"])
    started = time.perf_counter()
    structure = build_structure(limit)
    hard_set = set(structure.hard)
    if any(cutoff not in hard_set for cutoff in cutoffs):
        raise ValueError("every target cutoff must be hard-shaped")

    formulas = {
        cutoff: objective_terms(cutoff, hard_set) for cutoff in cutoffs
    }
    image_targets = sorted(
        {
            value
            for _, coefficients, _ in formulas.values()
            for value in coefficients
        }
    )
    source_limit = (limit + 1) // 2
    source_values = [
        value for value in range(2, source_limit + 1) if allowed(value)
    ]

    model = cp_model.CpModel()
    missing = {
        value: model.new_bool_var(f"v_{value}") for value in source_values
    }
    model.add(missing[2] == 0)
    model.add(missing[3] == 0)
    counters: Counter = Counter()

    for value in source_values:
        for left, right in structure.pairs[value]:
            model.add_bool_or(
                [missing[value].Not(), missing[left], missing[right]]
            )
            counters["self_blocking_clauses"] += 1

    image = {
        value: add_exact_image_gate(
            model, value, structure.pairs[value], missing, counters
        )
        for value in image_targets
    }
    for value, member in image.items():
        if isinstance(member, int):
            continue
        if value in missing:
            model.add_implication(member, missing[value].Not())
            counters["image_subset_clauses"] += 1
    for value, member in image.items():
        child = 2 * value - 1
        if child not in image:
            continue
        child_member = image[child]
        if isinstance(member, int) or isinstance(child_member, int):
            continue
        model.add_implication(member, child_member)
        counters["chain_implications"] += 1

    excess_vars = {}
    root_bound = max(len(formulas[cutoff][2]) for cutoff in cutoffs)
    for cutoff, (constant, coefficients, _) in formulas.items():
        terms = []
        adjusted_constant = constant
        for value, coefficient in coefficients.items():
            member = image[value]
            if isinstance(member, int):
                adjusted_constant += coefficient * member
            else:
                terms.append(coefficient * member)
        excess = model.new_int_var(
            -root_bound, root_bound, f"excess_{cutoff}"
        )
        model.add(excess == adjusted_constant + sum(terms))
        excess_vars[cutoff] = excess

    selected = model.new_int_var(-root_bound, root_bound, "selected_excess")
    selectors = {}
    for cutoff in cutoffs:
        selector = model.new_bool_var(f"select_{cutoff}")
        selectors[cutoff] = selector
        model.add(selected == excess_vars[cutoff]).only_enforce_if(selector)
    model.add_exactly_one(selectors.values())
    model.maximize(selected)

    proto_bytes = model.Proto().SerializeToString()
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = random_seed
    solver.parameters.linearization_level = linearization_level
    solver.parameters.cp_model_presolve = True
    status_code = solver.solve(model)
    status = solver.status_name(status_code)
    row = {
        "cutoffs": list(cutoffs),
        "cutoff_first": min(cutoffs),
        "cutoff_last": max(cutoffs),
        "cutoff_count": len(cutoffs),
        "status": status,
        "workers": workers,
        "time_limit_seconds": time_limit,
        "wall_seconds": time.perf_counter() - started,
        "solver_wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "deterministic_time": solver.response_proto.deterministic_time,
        "model_sha256": hashlib.sha256(proto_bytes).hexdigest().upper(),
        "model_proto_bytes": len(proto_bytes),
        "source_limit": source_limit,
        "source_variables": len(source_values),
        "image_target_count": len(image_targets),
        **dict(sorted(counters.items())),
    }
    if status_code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        row["best_objective_bound"] = solver.best_objective_bound
        return row

    objective = int(round(solver.objective_value))
    bound = int(round(solver.best_objective_bound))
    if status_code == cp_model.OPTIMAL and objective != bound:
        raise RuntimeError(f"optimal objective/bound mismatch: {objective}, {bound}")
    selected_cutoff = next(
        cutoff
        for cutoff, selector in selectors.items()
        if solver.boolean_value(selector)
    )
    source_missing = {
        value for value, variable in missing.items() if solver.boolean_value(variable)
    }
    witness_excess = {
        str(cutoff): solver.value(variable)
        for cutoff, variable in excess_vars.items()
    }
    if witness_excess[str(selected_cutoff)] != objective:
        raise RuntimeError("selected cutoff does not attain the objective")
    replay = direct_statistics(selected_cutoff, source_missing, structure)
    if replay["objective_excess"] != objective:
        raise RuntimeError("direct objective replay mismatch")
    row.update(
        {
            "objective_excess": objective,
            "best_objective_bound": bound,
            "selected_cutoff": selected_cutoff,
            "source_missing": sorted(source_missing),
            "witness_excess_by_cutoff": witness_excess,
            "replay": replay,
        }
    )
    return row


def chunks(values: list[int], size: int) -> list[list[int]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def run_tasks(tasks: list[dict], jobs: int) -> list[dict]:
    if jobs == 1:
        return [solve_group(task) for task in tasks]
    rows = []
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(solve_group, task): task for task in tasks}
        for future in as_completed(futures):
            rows.append(future.result())
    return sorted(rows, key=lambda row: row["cutoff_first"])


def main() -> None:
    parser = argparse.ArgumentParser()
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--scan-stop", type=int)
    targets.add_argument("--cutoffs", nargs="+", type=int)
    parser.add_argument("--scan-start", type=int, default=2)
    parser.add_argument("--group-size", type=int, default=1)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--workers-per-job", type=int, default=1)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--random-seed", type=int, default=81)
    parser.add_argument("--linearization-level", type=int, choices=(0, 1, 2), default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.scan_start < 2:
        parser.error("--scan-start must be at least 2")
    if args.group_size < 1 or args.jobs < 1 or args.workers_per_job < 1:
        parser.error("group size, jobs, and workers per job must be positive")
    if args.jobs > 61:
        parser.error("--jobs must not exceed Windows ProcessPoolExecutor's cap 61")
    if args.jobs * args.workers_per_job > 64:
        parser.error("--jobs * --workers-per-job must not exceed 64")
    if args.time_limit <= 0:
        parser.error("--time-limit must be positive")

    max_target = args.scan_stop if args.scan_stop is not None else max(args.cutoffs)
    structure = build_structure(max_target)
    hard_set = set(structure.hard)
    if args.scan_stop is not None:
        target_cutoffs = [
            value
            for value in structure.hard
            if args.scan_start <= value <= args.scan_stop
        ]
    else:
        target_cutoffs = sorted(set(args.cutoffs))
        bad = [value for value in target_cutoffs if value not in hard_set]
        if bad:
            parser.error(f"non-hard target cutoffs: {bad}")
    if not target_cutoffs:
        parser.error("no hard cutoffs selected")

    common = {
        "workers": args.workers_per_job,
        "time_limit": args.time_limit,
        "random_seed": args.random_seed,
        "linearization_level": args.linearization_level,
    }
    tasks = [
        {"cutoffs": group, **common}
        for group in chunks(target_cutoffs, args.group_size)
    ]
    started = time.perf_counter()
    rows = run_tasks(tasks, min(args.jobs, len(tasks)))
    status_counts = Counter(row["status"] for row in rows)
    all_optimal = all(row["status"] == "OPTIMAL" for row in rows)
    optimal_objectives = [
        row["objective_excess"] for row in rows if row["status"] == "OPTIMAL"
    ]
    payload = {
        "schema_version": 1,
        "model": "image_realizable_self_blocking_chain_shell",
        "exact_arithmetic": True,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "ortools": ortools.__version__,
        "logical_processors": os.cpu_count(),
        "scan_start": args.scan_start,
        "scan_stop": args.scan_stop,
        "target_cutoff_first": target_cutoffs[0],
        "target_cutoff_last": target_cutoffs[-1],
        "hard_cutoff_count": len(target_cutoffs),
        "group_size": args.group_size,
        "group_count": len(tasks),
        "jobs": args.jobs,
        "workers_per_job": args.workers_per_job,
        "total_worker_cap": args.jobs * args.workers_per_job,
        "time_limit_seconds_per_group": args.time_limit,
        "linearization_level": args.linearization_level,
        "random_seed": args.random_seed,
        "elapsed_seconds": time.perf_counter() - started,
        "status_counts": dict(sorted(status_counts.items())),
        "all_groups_optimal": all_optimal,
        "global_optimum": max(optimal_objectives) if all_optimal else None,
        "no_positive_excess_certified": (
            all_optimal and max(optimal_objectives) <= 0
        ),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="ascii"
    )
    print(
        f"cutoffs={len(target_cutoffs)} groups={len(rows)} "
        f"statuses={dict(status_counts)} global={payload['global_optimum']} "
        f"elapsed={payload['elapsed_seconds']:.3f}s"
    )


if __name__ == "__main__":
    main()
