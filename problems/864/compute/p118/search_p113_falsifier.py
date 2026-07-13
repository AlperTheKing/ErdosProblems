#!/usr/bin/env python3
"""Exact adversarial search for a P113 Hall falsifier.

Every accepted state is an endpoint-normalized integer Sidon set.  The
resource graph is the full P113 graph: each loose triangle sees its three
supporting folds and all three pairwise differences of the fold phases.

The exhaustive and Costas lanes are purely combinatorial.  CP-SAT is used
only to discover fold-dense endpoint Sidon sets; every returned set and its
Hall score are then recomputed with Python integers.
"""

from __future__ import annotations

import argparse
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import random
from typing import Iterable, Iterator, Sequence

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p118/p113_falsifier_search.json"


def digest(values: Sequence[int]) -> str:
    return sha256(",".join(map(str, values)).encode("ascii")).hexdigest()


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in out:
                raise ValueError(("repeated sum", total, out[total], (left, right)))
            out[total] = (left, right)
    return out


def positive_differences(values: Sequence[int]) -> set[int]:
    out: set[int] = set()
    for j, right in enumerate(values):
        for left in values[:j]:
            difference = right - left
            if difference in out:
                raise ValueError(("repeated difference", difference))
            out.add(difference)
    return out


def canonical_folds(values: Sequence[int], h: int) -> list[tuple[int, int, int, int]]:
    sums = unordered_sum_map(values)
    folds = []
    for low in sorted(sums):
        high = low + h
        if high not in sums:
            continue
        a, c = sums[low]
        u, v = sums[high]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v, h))
        folds.append((a, c, u, v))
    return folds


def loose_triangles(
    folds: Sequence[tuple[int, int, int, int]],
) -> list[tuple[int, int, int]]:
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    by_a_u: dict[int, list[int]] = {}
    for a, u in au:
        by_a_u.setdefault(a, []).append(u)
    triangles = []
    for a, c in ac:
        for u in by_a_u.get(a, ()):
            third = cu.get((c, u))
            if third is None:
                continue
            ids = (ac[a, c], au[a, u], third)
            if len(set(ids)) == 1:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("nonlinear triangle", ids))
            triangles.append(ids)
    return triangles


def hopcroft_karp(neighbors: Sequence[Sequence[int]], right_count: int) -> tuple[int, list[int], list[int]]:
    left_count = len(neighbors)
    pair_left = [-1] * left_count
    pair_right = [-1] * right_count
    distance = [0] * left_count

    def bfs() -> bool:
        queue: deque[int] = deque()
        found = False
        for left in range(left_count):
            if pair_left[left] < 0:
                distance[left] = 0
                queue.append(left)
            else:
                distance[left] = -1
        while queue:
            left = queue.popleft()
            for right in neighbors[left]:
                mate = pair_right[right]
                if mate < 0:
                    found = True
                elif distance[mate] < 0:
                    distance[mate] = distance[left] + 1
                    queue.append(mate)
        return found

    def dfs(left: int) -> bool:
        for right in neighbors[left]:
            mate = pair_right[right]
            if mate < 0 or (distance[mate] == distance[left] + 1 and dfs(mate)):
                pair_left[left] = right
                pair_right[right] = left
                return True
        distance[left] = -1
        return False

    matching = 0
    while bfs():
        for left in range(left_count):
            if pair_left[left] < 0 and dfs(left):
                matching += 1
    return matching, pair_left, pair_right


def hall_witness(
    neighbors: Sequence[Sequence[int]], pair_left: Sequence[int], pair_right: Sequence[int]
) -> tuple[list[int], list[int]]:
    seen_left = {left for left, right in enumerate(pair_left) if right < 0}
    seen_right: set[int] = set()
    queue = deque(seen_left)
    while queue:
        left = queue.popleft()
        for right in neighbors[left]:
            if pair_left[left] == right or right in seen_right:
                continue
            seen_right.add(right)
            mate = pair_right[right]
            if mate >= 0 and mate not in seen_left:
                seen_left.add(mate)
                queue.append(mate)
    return sorted(seen_left), sorted(seen_right)


def peel_core(neighbors: Sequence[Sequence[int]], right_count: int) -> tuple[int, int]:
    incident = [set() for _ in range(right_count)]
    alive_left = set(range(len(neighbors)))
    alive_right = set(range(right_count))
    for left, row in enumerate(neighbors):
        for right in row:
            incident[right].add(left)
    queue = deque(right for right in alive_right if len(incident[right]) <= 1)
    while queue:
        right = queue.popleft()
        if right not in alive_right:
            continue
        alive_right.remove(right)
        live = incident[right] & alive_left
        if not live:
            continue
        left = next(iter(live))
        alive_left.remove(left)
        for other in neighbors[left]:
            if other in alive_right:
                incident[other].discard(left)
                if len(incident[other] & alive_left) <= 1:
                    queue.append(other)
    used_right = {right for left in alive_left for right in neighbors[left]}
    return len(alive_left), len(used_right)


def audit(values_input: Iterable[int], h: int, source: str) -> dict[str, object]:
    values = tuple(sorted(int(x) for x in values_input))
    if len(values) < 2 or len(values) != len(set(values)):
        raise AssertionError(("invalid values", values))
    if values[0] < 0 or values[-1] != h - 1:
        raise AssertionError(("endpoint normalization", values[:1], values[-1:], h))
    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    folds = canonical_folds(values, h)
    triangles = loose_triangles(folds)
    difference_list = sorted(differences)
    difference_id = {value: index for index, value in enumerate(difference_list)}
    full_neighbors: list[list[int]] = []
    difference_neighbors: list[list[int]] = []
    support_neighbors: list[list[int]] = []
    for triangle in triangles:
        phases = [folds[index][0] + folds[index][1] for index in triangle]
        labels = sorted({difference_id[abs(phases[i] - phases[j])] for i in range(3) for j in range(i)})
        if not labels:
            raise AssertionError(("missing phase difference", triangle))
        support = sorted(set(triangle))
        support_neighbors.append(support)
        difference_neighbors.append(labels)
        full_neighbors.append(support + [len(folds) + label for label in labels])
    full_matching, pair_left, pair_right = hopcroft_karp(
        full_neighbors, len(folds) + len(difference_list)
    )
    difference_matching = hopcroft_karp(difference_neighbors, len(difference_list))[0]
    support_matching = hopcroft_karp(support_neighbors, len(folds))[0]
    witness_left: list[int] = []
    witness_right: list[int] = []
    if full_matching < len(triangles):
        witness_left, witness_right = hall_witness(full_neighbors, pair_left, pair_right)
        actual_neighbors = {right for left in witness_left for right in full_neighbors[left]}
        if actual_neighbors != set(witness_right) or len(witness_left) <= len(witness_right):
            raise AssertionError(("invalid Hall witness", len(witness_left), len(witness_right)))
    used_resources = {right for row in full_neighbors for right in row}
    core_left, core_right = peel_core(full_neighbors, len(folds) + len(difference_list))
    result: dict[str, object] = {
        "source": source,
        "B": list(values),
        "sha256": digest(values),
        "p": len(values),
        "h": h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "difference_resources": len(difference_list),
        "used_resources": len(used_resources),
        "matching": full_matching,
        "hall_deficiency": len(triangles) - full_matching,
        "difference_matching": difference_matching,
        "difference_deficiency": len(triangles) - difference_matching,
        "support_matching": support_matching,
        "support_deficiency": len(triangles) - support_matching,
        "resource_slack": len(used_resources) - len(triangles),
        "peel_core_left": core_left,
        "peel_core_right": core_right,
        "peel_core_excess": core_left - core_right,
    }
    if witness_left:
        result["hall_witness"] = {
            "triangle_ids": witness_left,
            "resource_ids": witness_right,
            "triangles": [list(triangles[index]) for index in witness_left],
            "folds": [list(fold) for fold in folds],
            "difference_labels": difference_list,
        }
    return result


def score(row: dict[str, object]) -> tuple[int, ...]:
    return (
        int(row["hall_deficiency"]),
        int(row["peel_core_excess"]),
        int(row["difference_deficiency"]),
        -int(row["resource_slack"]),
        int(row["T_F"]),
        int(row["C_S"]),
    )


def sidon_rulers(width: int) -> Iterator[tuple[int, ...]]:
    chosen = [0]
    used: set[int] = set()

    def new_differences(value: int) -> tuple[int, ...] | None:
        differences = tuple(value - old for old in chosen)
        if len(set(differences)) < len(differences) or any(d in used for d in differences):
            return None
        return differences

    def recurse(next_value: int) -> Iterator[tuple[int, ...]]:
        endpoint = new_differences(width)
        if endpoint is not None:
            yield tuple(chosen + [width])
        for value in range(next_value, width):
            differences = new_differences(value)
            if differences is None:
                continue
            chosen.append(value)
            used.update(differences)
            yield from recurse(value + 1)
            used.difference_update(differences)
            chosen.pop()

    yield from recurse(1)


def retain(rows: list[dict[str, object]], row: dict[str, object], limit: int) -> None:
    if not int(row["T_F"]):
        return
    rows.append(row)
    rows.sort(key=score, reverse=True)
    del rows[limit:]


def exhaustive_width(width: int, keep: int) -> dict[str, object]:
    rows = triangle_rows = failures = rulers = 0
    best: list[dict[str, object]] = []
    for ruler in sidon_rulers(width):
        rulers += 1
        for gamma in range(width):
            rows += 1
            values = tuple(gamma + x for x in ruler)
            row = audit(values, width + gamma + 1, f"exhaustive W={width} gamma={gamma}")
            if row["T_F"]:
                triangle_rows += 1
                failures += int(row["hall_deficiency"] > 0)
                retain(best, row, keep)
    return {
        "width": width,
        "rulers": rulers,
        "systems": rows,
        "triangle_systems": triangle_rows,
        "failures": failures,
        "best": best,
    }


def prime_factors(value: int) -> list[int]:
    factors = []
    trial = 2
    while trial * trial <= value:
        if value % trial == 0:
            factors.append(trial)
            while value % trial == 0:
                value //= trial
        trial += 1
    if value > 1:
        factors.append(value)
    return factors


def primitive_roots(prime: int) -> list[int]:
    factors = prime_factors(prime - 1)
    return [g for g in range(2, prime) if all(pow(g, (prime - 1) // q, prime) != 1 for q in factors)]


def costas_rulers(prime: int) -> Iterator[tuple[int, ...]]:
    size = prime - 1
    radix = 2 * prime
    for root in primitive_roots(prime)[:4]:
        base = [pow(root, i, prime) - 1 for i in range(size)]
        for shift in range(min(size, 8)):
            permutation = base[shift:] + base[:shift]
            values = tuple(i * radix + permutation[i] for i in range(size))
            offset = values[0]
            normalized = tuple(x - offset for x in values)
            if min(normalized) < 0:
                continue
            normalized = tuple(sorted(normalized))
            try:
                unordered_sum_map(normalized)
            except ValueError:
                continue
            yield normalized
            yield tuple(normalized[-1] - x for x in reversed(normalized))


def event_translations(base: Sequence[int], source: str, keep: int) -> dict[str, object]:
    width = base[-1]
    sums = unordered_sum_map(base)
    sum_values = set(sums)
    best: list[dict[str, object]] = []
    events = triangle_events = failures = 0
    for h in range(width + 1, 2 * width + 1):
        fold_count = sum(low + h in sum_values for low in sum_values)
        if fold_count < 3:
            continue
        events += 1
        gamma = h - width - 1
        values = tuple(gamma + x for x in base)
        row = audit(values, h, f"{source}; gamma={gamma}")
        if row["T_F"]:
            triangle_events += 1
            failures += int(row["hall_deficiency"] > 0)
            retain(best, row, keep)
    return {
        "source": source,
        "p": len(base),
        "width": width,
        "event_systems": events,
        "triangle_systems": triangle_events,
        "failures": failures,
        "best": best,
    }


def costas_worker(prime: int, keep: int) -> dict[str, object]:
    seen: set[tuple[int, ...]] = set()
    bases = events = triangles = failures = 0
    best: list[dict[str, object]] = []
    for base in costas_rulers(prime):
        if base in seen:
            continue
        seen.add(base)
        bases += 1
        result = event_translations(base, f"Welch-Costas prime={prime}", keep)
        events += int(result["event_systems"])
        triangles += int(result["triangle_systems"])
        failures += int(result["failures"])
        for row in result["best"]:
            retain(best, row, keep)
    return {
        "prime": prime,
        "bases": bases,
        "event_systems": events,
        "triangle_systems": triangles,
        "failures": failures,
        "best": best,
    }


class IncumbentCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, selected: Sequence[cp_model.IntVar], limit: int = 24):
        super().__init__()
        self.selected = selected
        self.limit = limit
        self.rows: list[list[int]] = []

    def on_solution_callback(self) -> None:
        values = [i for i, variable in enumerate(self.selected) if self.value(variable)]
        if values not in self.rows:
            self.rows.append(values)
            if len(self.rows) > self.limit:
                self.rows.pop(0)


def cpsat_fold_dense(width: int, seconds: float, workers: int, seed: int, keep: int) -> dict[str, object]:
    model = cp_model.CpModel()
    selected = [model.NewBoolVar(f"x_{i}") for i in range(width + 1)]
    model.Add(selected[0] == 1)
    model.Add(selected[width] == 1)
    pairs: dict[tuple[int, int], cp_model.IntVar] = {}
    by_sum: list[list[cp_model.IntVar]] = [[] for _ in range(2 * width + 1)]
    for left in range(width + 1):
        for right in range(left, width + 1):
            if left == right:
                pair = selected[left]
            else:
                pair = model.NewBoolVar(f"p_{left}_{right}")
                model.Add(pair <= selected[left])
                model.Add(pair <= selected[right])
                model.Add(pair >= selected[left] + selected[right] - 1)
            pairs[left, right] = pair
            by_sum[left + right].append(pair)
    occupied = []
    for total, terms in enumerate(by_sum):
        variable = model.NewBoolVar(f"s_{total}")
        model.Add(variable == cp_model.LinearExpr.sum(terms))
        occupied.append(variable)
    folds = []
    h = width + 1
    for low in range(width):
        fold = model.NewBoolVar(f"f_{low}")
        model.Add(fold <= occupied[low])
        model.Add(fold <= occupied[low + h])
        model.Add(fold >= occupied[low] + occupied[low + h] - 1)
        folds.append(fold)
    rng = random.Random(seed)
    random_tie = sum(rng.randrange(1, 1001) * selected[i] for i in range(width + 1))
    model.Maximize(1_000_000_000 * sum(folds) + 1_000_000 * sum(selected) + random_tie)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = max(1, min(workers, 64))
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    collector = IncumbentCollector(selected)
    status = solver.Solve(model, collector)
    candidates = list(collector.rows)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        final = [i for i, variable in enumerate(selected) if solver.Value(variable)]
        if final not in candidates:
            candidates.append(final)
    best: list[dict[str, object]] = []
    failures = triangle_systems = 0
    for index, values in enumerate(candidates):
        row = audit(values, h, f"CP-SAT W={width} seed={seed} incumbent={index}")
        if row["T_F"]:
            triangle_systems += 1
            failures += int(row["hall_deficiency"] > 0)
            retain(best, row, keep)
    return {
        "width": width,
        "seed": seed,
        "status": solver.StatusName(status),
        "best_objective_bound": str(solver.BestObjectiveBound()),
        "objective_value": str(solver.ObjectiveValue()) if status in (cp_model.FEASIBLE, cp_model.OPTIMAL) else None,
        "incumbents": len(candidates),
        "triangle_systems": triangle_systems,
        "failures": failures,
        "best": best,
    }


def aggregate(sections: Sequence[dict[str, object]], keep: int) -> dict[str, object]:
    best: list[dict[str, object]] = []
    failures = 0
    for section in sections:
        failures += int(section.get("failures", 0))
        for row in section.get("best", []):
            retain(best, row, keep)
    return {"failures": failures, "best": best}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-width", type=int, default=31)
    parser.add_argument("--max-width", type=int, default=35)
    parser.add_argument("--costas-primes", default="29,31,37,43,47,53")
    parser.add_argument("--cpsat-widths", default="36,40,48,56,64")
    parser.add_argument("--cpsat-seeds", type=int, default=3)
    parser.add_argument("--cpsat-seconds", type=float, default=45.0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--keep", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    workers = max(1, min(args.workers, 64))
    keep = max(1, args.keep)

    exhaustive: list[dict[str, object]] = []
    widths = list(range(args.min_width, args.max_width + 1))
    with ProcessPoolExecutor(max_workers=min(workers, max(1, len(widths)))) as pool:
        futures = {pool.submit(exhaustive_width, width, keep): width for width in widths}
        for future in as_completed(futures):
            exhaustive.append(future.result())
    exhaustive.sort(key=lambda row: int(row["width"]))

    primes = [int(x) for x in args.costas_primes.split(",") if x.strip()]
    costas: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=min(workers, max(1, len(primes)))) as pool:
        futures = {pool.submit(costas_worker, prime, keep): prime for prime in primes}
        for future in as_completed(futures):
            costas.append(future.result())
    costas.sort(key=lambda row: int(row["prime"]))

    cp_widths = [int(x) for x in args.cpsat_widths.split(",") if x.strip()]
    cpsat = []
    cp_workers = max(1, min(workers, 32))
    for width in cp_widths:
        for seed in range(1, args.cpsat_seeds + 1):
            cpsat.append(cpsat_fold_dense(width, args.cpsat_seconds, cp_workers, seed, keep))

    all_sections = exhaustive + costas + cpsat
    global_summary = aggregate(all_sections, keep)
    payload = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; CP-SAT only proposes endpoint Sidon sets",
        "candidate": "P113 full support-fold plus three phase-difference Hall matching",
        "score_order": [
            "Hall deficiency", "peel-core excess", "difference-only deficiency",
            "negative used-resource slack", "triangle count", "fold count",
        ],
        "parameters": {
            "min_width": args.min_width,
            "max_width": args.max_width,
            "costas_primes": primes,
            "cpsat_widths": cp_widths,
            "cpsat_seeds": args.cpsat_seeds,
            "cpsat_seconds": args.cpsat_seconds,
            "workers": workers,
        },
        "exhaustive": exhaustive,
        "costas": costas,
        "cpsat": cpsat,
        "global": global_summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(args.output)
    print(json.dumps({"failures": global_summary["failures"], "best": global_summary["best"][:1]}, indent=2))


if __name__ == "__main__":
    main()
