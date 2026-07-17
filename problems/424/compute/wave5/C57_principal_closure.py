#!/usr/bin/env python3
"""Exact perturbation gate for the splitless-closed boundary objective."""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c56_image", HERE / "C56_image_lp_dual.py")
if not SPEC or not SPEC.loader:
    raise RuntimeError("cannot load C56_image_lp_dual.py")
C56 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C56
SPEC.loader.exec_module(C56)


def least_closure(limit: int, pairs: dict[int, list[tuple[int, int]]]) -> bytearray:
    member = bytearray(limit + 1)
    member[2] = member[3] = 1
    for n in range(4, limit + 1):
        if not C56.allowed(n):
            continue
        member[n] = any(member[a] and member[b] for a, b in pairs[n])
    return member


def close_forced(
    base: bytearray,
    forced: tuple[int, ...],
    pairs: dict[int, list[tuple[int, int]]],
    limit: int,
) -> bytearray:
    member = bytearray(base)
    for n in forced:
        member[n] = 1
    start = min(forced) if forced else limit + 1
    for n in range(start + 1, limit + 1):
        if member[n] or not C56.allowed(n):
            continue
        member[n] = any(member[a] and member[b] for a, b in pairs[n])
    return member


def objective(
    member: bytearray,
    hard: list[int],
    values: list[int],
    limit: int,
) -> tuple[int, int, int]:
    hard_members = sum(member[n] for n in hard)
    boundary = sum(
        1
        for m in values
        if 2 * m - 1 <= limit and not member[m] and member[2 * m - 1]
    )
    return hard_members + boundary, hard_members, boundary


def boundary_set(member: bytearray, values: list[int], limit: int) -> set[int]:
    return {
        2 * m - 1
        for m in values
        if 2 * m - 1 <= limit and not member[m] and member[2 * m - 1]
    }


def change_details(
    base: bytearray,
    closed: bytearray,
    hard: list[int],
    values: list[int],
    limit: int,
) -> dict:
    base_boundary = boundary_set(base, values, limit)
    new_boundary = boundary_set(closed, values, limit)
    return {
        "added_members": [n for n in values if closed[n] and not base[n]],
        "added_hard_members": [n for n in hard if closed[n] and not base[n]],
        "gained_boundaries": sorted(new_boundary - base_boundary),
        "lost_boundaries": sorted(base_boundary - new_boundary),
    }


def solve(limit: int, pair_limit: int, random_trials: int) -> dict:
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    pairs = {n: C56.admissible_pairs(n) for n in values}
    hard = [n for n in values if C56.hard_shape(n, pairs[n])]
    base = least_closure(limit, pairs)
    base_objective = objective(base, hard, values, limit)
    candidates = [n for n in values if not base[n] and pairs[n]]

    principal: list[tuple[int, int, int]] = []
    for n in candidates:
        closed = close_forced(base, (n,), pairs, limit)
        value = objective(closed, hard, values, limit)[0]
        principal.append((value - base_objective[0], n, sum(closed) - sum(base)))
    principal.sort()

    pair_result = None
    if limit <= pair_limit:
        best = (10**9, 0, 0, 0)
        for i, left in enumerate(candidates):
            for right in candidates[i + 1 :]:
                closed = close_forced(base, (left, right), pairs, limit)
                value = objective(closed, hard, values, limit)[0]
                item = (value - base_objective[0], left, right, sum(closed) - sum(base))
                if item < best:
                    best = item
        pair_result = best if len(candidates) >= 2 else None

    rng = random.Random(424057 + limit)
    random_best = (10**9, [], 0)
    if candidates:
        for _ in range(random_trials):
            width = rng.randint(2, min(12, len(candidates)))
            forced = tuple(sorted(rng.sample(candidates, width)))
            closed = close_forced(base, forced, pairs, limit)
            value = objective(closed, hard, values, limit)[0]
            item = (value - base_objective[0], list(forced), sum(closed) - sum(base))
            if item[0] < random_best[0]:
                random_best = item

    best_principal_details = None
    if principal:
        _, seed, _ = principal[0]
        best_closed = close_forced(base, (seed,), pairs, limit)
        best_principal_details = change_details(base, best_closed, hard, values, limit)

    return {
        "limit": limit,
        "generated": int(sum(base)),
        "reducible_holes": len(candidates),
        "base_objective": {
            "total": base_objective[0],
            "hard_members": base_objective[1],
            "boundary": base_objective[2],
        },
        "best_principal": principal[0] if principal else None,
        "best_principal_details": best_principal_details,
        "negative_principal_count": sum(delta < 0 for delta, _, _ in principal),
        "best_pair": pair_result,
        "best_random": random_best if random_best[0] < 10**9 else None,
        "random_trials": random_trials,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, default=[100, 200, 500, 1000])
    parser.add_argument("--pair-limit", type=int, default=1000)
    parser.add_argument("--random-trials", type=int, default=2000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [solve(limit, args.pair_limit, args.random_trials) for limit in args.limits]
    text = json.dumps(rows, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
