#!/usr/bin/env python3
"""Exact search for periodic composition covers in the Erdos #424 affine system.

The conjugated generators are g_d(u) = d*u + d - 2.  A word (d1,...,dk)
means g_dk o ... o g_d1, matching the order in which the generators are
applied to an orbit point.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from math import gcd, lcm
from pathlib import Path
from typing import Iterable


D = (2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69, 77, 80, 81, 84)


@dataclass(frozen=True)
class Affine:
    slope: int
    intercept: int
    word: tuple[int, ...]


@dataclass(frozen=True)
class Candidate:
    mask: int
    affine: Affine


@dataclass
class SolverStats:
    nodes: int = 0
    memo_hits: int = 0
    exhausted: bool = True
    status: str = "ALGORITHM_X"


def append_generator(affine: Affine, d: int) -> Affine:
    """Append d to the application-order word, i.e. compose g_d on the left."""
    return Affine(
        d * affine.slope,
        d * affine.intercept + d - 2,
        affine.word + (d,),
    )


def generate_affines(master: int, max_depth: int) -> list[Affine]:
    """Generate every distinct affine map of depth <= max_depth with slope | master."""
    identity = Affine(1, 0, ())
    seen: dict[tuple[int, int], Affine] = {(1, 0): identity}
    frontier = [identity]
    for _ in range(max_depth):
        following: list[Affine] = []
        for affine in frontier:
            for d in D:
                slope = d * affine.slope
                if master % slope:
                    continue
                child = append_generator(affine, d)
                key = (child.slope, child.intercept)
                if key not in seen:
                    seen[key] = child
                    following.append(child)
        frontier = following
        if not frontier:
            break
    return sorted(
        (affine for key, affine in seen.items() if key != (1, 0)),
        key=lambda affine: (affine.slope, affine.intercept, affine.word),
    )


def class_mask(residue: int, modulus: int, period: int) -> int:
    if period % modulus:
        raise ValueError("class modulus must divide the checking period")
    mask = 0
    for value in range(residue % modulus, period, modulus):
        mask |= 1 << value
    return mask


def iter_bits(mask: int) -> Iterable[int]:
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def deduplicate_candidates(candidates: Iterable[Candidate]) -> list[Candidate]:
    by_mask: dict[int, Candidate] = {}
    for candidate in candidates:
        incumbent = by_mask.get(candidate.mask)
        if incumbent is None or candidate.affine.word < incumbent.affine.word:
            by_mask[candidate.mask] = candidate
    return sorted(
        by_mask.values(),
        key=lambda candidate: (
            -candidate.mask.bit_count(),
            candidate.affine.slope,
            candidate.affine.word,
        ),
    )


def exact_cover(
    target: int, candidates: list[Candidate], max_nodes: int
) -> tuple[list[Candidate] | None, SolverStats]:
    """Algorithm X on integer bitsets; exhaustion is certified unless max_nodes is hit."""
    stats = SolverStats()
    incidence: dict[int, list[int]] = {point: [] for point in iter_bits(target)}
    for index, candidate in enumerate(candidates):
        if candidate.mask == 0 or candidate.mask & ~target:
            continue
        for point in iter_bits(candidate.mask):
            incidence[point].append(index)

    if any(not choices for choices in incidence.values()):
        return None, stats

    memo: set[int] = set()

    def visit(covered: int, chosen: list[int]) -> list[int] | None:
        stats.nodes += 1
        if stats.nodes > max_nodes:
            stats.exhausted = False
            return None
        if covered == target:
            return chosen.copy()
        if covered in memo:
            stats.memo_hits += 1
            return None

        uncovered = target ^ covered
        point = min(
            iter_bits(uncovered),
            key=lambda p: sum(
                candidates[index].mask & covered == 0 for index in incidence[p]
            ),
        )
        choices = [
            index
            for index in incidence[point]
            if candidates[index].mask & covered == 0
        ]
        choices.sort(key=lambda index: -candidates[index].mask.bit_count())
        for index in choices:
            result = visit(covered | candidates[index].mask, chosen + [index])
            if result is not None:
                return result
            if not stats.exhausted:
                return None
        memo.add(covered)
        return None

    selected = visit(0, [])
    return (
        None if selected is None else [candidates[index] for index in selected],
        stats,
    )


def exact_cover_cp_sat(
    target: int, candidates: list[Candidate], workers: int
) -> tuple[list[Candidate] | None, SolverStats]:
    """Solve the same finite exact-cover instance with OR-Tools CP-SAT."""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    variables = [model.new_bool_var(f"use_{index}") for index in range(len(candidates))]
    incidence: dict[int, list[int]] = {point: [] for point in iter_bits(target)}
    for index, candidate in enumerate(candidates):
        if candidate.mask == 0 or candidate.mask & ~target:
            continue
        for point in iter_bits(candidate.mask):
            incidence[point].append(index)
    if any(not choices for choices in incidence.values()):
        return None, SolverStats(status="INFEASIBLE_EMPTY_COLUMN")
    for choices in incidence.values():
        model.add_exactly_one(variables[index] for index in choices)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.cp_model_presolve = True
    status_code = solver.solve(model)
    status = solver.status_name(status_code)
    stats = SolverStats(
        nodes=solver.num_branches,
        memo_hits=solver.num_conflicts,
        exhausted=status in ("OPTIMAL", "INFEASIBLE"),
        status=status,
    )
    if status not in ("OPTIMAL", "FEASIBLE"):
        return None, stats
    return [
        candidate
        for variable, candidate in zip(variables, candidates)
        if solver.value(variable)
    ], stats


def solve_instance(
    args: argparse.Namespace, target: int, candidates: list[Candidate]
) -> tuple[list[Candidate] | None, SolverStats]:
    if args.solver == "cp-sat":
        return exact_cover_cp_sat(target, candidates, args.workers)
    return exact_cover(target, candidates, args.max_nodes)


def direct_safe_seeds() -> list[tuple[int, int, int]]:
    seeds: list[tuple[int, int, int]] = []
    for index, x in enumerate(D):
        for y in D[index + 1 :]:
            seed = x * y - 1
            if seed > max(D):
                seeds.append((seed, x, y))
    return sorted(set(seeds))


def progression_candidates(
    affines: list[Affine], q: int, residue: int, period: int
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for affine in affines:
        displacement = (affine.slope - 1) * residue + affine.intercept
        if displacement % q:
            continue
        induced_residue = displacement // q
        mask = class_mask(induced_residue, affine.slope, period)
        candidates.append(Candidate(mask, affine))
    return deduplicate_candidates(candidates)


def union_candidates(
    affines: list[Affine], q: int, residues: tuple[int, ...], master: int
) -> tuple[int, list[Candidate]]:
    period = q * master
    target = 0
    residue_set = set(residues)
    for residue in residues:
        target |= class_mask(residue, q, period)

    candidates: list[Candidate] = []
    for affine in affines:
        if any(
            (affine.slope * residue + affine.intercept) % q not in residue_set
            for residue in residues
        ):
            continue
        mask = 0
        modulus = q * affine.slope
        for residue in residues:
            image_residue = affine.slope * residue + affine.intercept
            mask |= class_mask(image_residue, modulus, period)
        if mask & ~target == 0:
            candidates.append(Candidate(mask, affine))
    return target, deduplicate_candidates(candidates)


def seed_for_domain(q: int, residues: set[int]) -> tuple[int, int, int] | None:
    for seed, x, y in direct_safe_seeds():
        if (seed - 1) % q in residues:
            return seed, x, y
    return None


def passes_outer_image_obstruction(q: int, residues: Iterable[int]) -> bool:
    """Necessary condition for a periodic domain covered by nonempty D-words.

    Every word image lies in g_d(Z) for its last letter d.  Dirichlet's
    theorem shows that qZ+r is contained in the finite union of these images
    only if one d in D divides both q and r+2.
    """
    return all(any(q % d == 0 and (residue + 2) % d == 0 for d in D) for residue in residues)


def certificate(
    q: int,
    residues: tuple[int, ...],
    selected: list[Candidate],
    seed: tuple[int, int, int],
) -> dict[str, object]:
    return {
        "D": list(D),
        "coordinate": "u=x-1",
        "domain": {"modulus": q, "residues": list(residues)},
        "maps": [
            {
                "word_application_order": list(item.affine.word),
                "slope": item.affine.slope,
                "intercept": item.affine.intercept,
            }
            for item in selected
        ],
        "safe_seed": {
            "x0": seed[0],
            "u0": seed[0] - 1,
            "witness": [seed[1], seed[2]],
        },
    }


def search_progressions(args: argparse.Namespace, affines: list[Affine]) -> dict | None:
    total_nodes = 0
    cases = 0
    truncated = 0
    obstructed = 0
    for q in range(1, args.q_max + 1):
        for residue in range(q):
            seed = seed_for_domain(q, {residue})
            if seed is None:
                continue
            if not passes_outer_image_obstruction(q, (residue,)):
                obstructed += 1
                continue
            cases += 1
            candidates = progression_candidates(affines, q, residue, args.master)
            target = (1 << args.master) - 1
            result, stats = solve_instance(args, target, candidates)
            total_nodes += stats.nodes
            truncated += not stats.exhausted
            if result is not None:
                print(
                    f"FOUND mode=progression q={q} residue={residue} "
                    f"maps={len(result)} nodes={stats.nodes} status={stats.status}"
                )
                return certificate(q, (residue,), result, seed)
    print(
        f"NO_CERT mode=progression cases={cases} nodes={total_nodes} "
        f"truncated={truncated} outer_obstructed={obstructed}"
    )
    return None


def search_unions(args: argparse.Namespace, affines: list[Affine]) -> dict | None:
    total_nodes = 0
    cases = 0
    truncated = 0
    obstructed = 0
    for q in range(2, args.union_q_max + 1):
        for residue_mask in range(1, 1 << q):
            residues = tuple(i for i in range(q) if residue_mask >> i & 1)
            seed = seed_for_domain(q, set(residues))
            if seed is None:
                continue
            if not passes_outer_image_obstruction(q, residues):
                obstructed += 1
                continue
            cases += 1
            target, candidates = union_candidates(affines, q, residues, args.master)
            result, stats = solve_instance(args, target, candidates)
            total_nodes += stats.nodes
            truncated += not stats.exhausted
            if result is not None:
                print(
                    f"FOUND mode=union q={q} residues={residues} "
                    f"maps={len(result)} nodes={stats.nodes} status={stats.status}"
                )
                return certificate(q, residues, result, seed)
    print(
        f"NO_CERT mode=union cases={cases} nodes={total_nodes} "
        f"truncated={truncated} outer_obstructed={obstructed}"
    )
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=int, default=2160)
    parser.add_argument("--depth", type=int, default=7)
    parser.add_argument("--q-max", type=int, default=48)
    parser.add_argument("--union-q-max", type=int, default=10)
    parser.add_argument("--max-nodes", type=int, default=2_000_000)
    parser.add_argument("--solver", choices=("cp-sat", "algorithm-x"), default="cp-sat")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument(
        "--mode", choices=("progression", "union", "both"), default="both"
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.master < 2 or args.depth < 1 or args.q_max < 1 or not 1 <= args.workers <= 64:
        raise SystemExit(
            "master >= 2, depth >= 1, q-max >= 1, and 1 <= workers <= 64 are required"
        )
    affines = generate_affines(args.master, args.depth)
    print(
        f"D={len(D)} master={args.master} depth={args.depth} "
        f"distinct_affines={len(affines)}"
    )
    result = None
    if args.mode in ("progression", "both"):
        result = search_progressions(args, affines)
    if result is None and args.mode in ("union", "both"):
        result = search_unions(args, affines)
    if result is not None and args.output is not None:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
        print(f"certificate={args.output}")
    return 0 if result is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
