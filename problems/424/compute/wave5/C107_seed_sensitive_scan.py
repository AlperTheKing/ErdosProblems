#!/usr/bin/env python3
"""Exact census for the seed-sensitive upper-quarter recurrence.

For a finite seed set S containing {2,3}, let G_S be the least subset of
A = {n >= 2 : n != 1 (mod 3)} containing S and closed under xy-1 for
distinct x,y in G_S.  The hard/splitless taxonomy and literal U-chain event
counts are the same as in C92, with membership in S overriding the ordinary
classification at that integer.

All acceptance arithmetic is integral.  The scan is deliberately finite:
it seeks falsifiers and identifies the smallest correction observed; it does
not certify an all-X theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def chain_root(n: int) -> int:
    """The unique even r with n = U^j(r), where U(r)=2r-1."""
    value = n - 1
    while value % 2 == 0:
        value //= 2
    return value + 1


def correction_k(seeds: tuple[int, ...]) -> int:
    return len({chain_root(seed) for seed in seeds})


def build_pairs(limit: int) -> list[list[tuple[int, int]]]:
    pairs: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]
    allowed_values = [n for n in range(2, limit + 1) if allowed(n)]
    for i, a in enumerate(allowed_values):
        for b in allowed_values[i + 1 :]:
            out = a * b - 1
            if out > limit:
                break
            if allowed(out):
                pairs[out].append((a, b))
    return pairs


def classify(n: int, state: bytearray, pairs: list[list[tuple[int, int]]]) -> int:
    admissible = pairs[n]
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in admissible):
        return GENERATED
    if not admissible:
        return SPLITLESS
    if n % 2 == 0:
        product = n + 1
        if product % 3:
            return HARD
        parent = product // 3
        if not allowed(parent) or parent == 3:
            return HARD
    return OTHER


@dataclass(frozen=True)
class ScanResult:
    seeds: tuple[int, ...]
    k: int
    required_correction: int
    required_at: int
    endpoint_ah: int
    endpoint_d: int
    first_k_failure: dict[str, int] | None
    trajectory_sha256: str


def scan_seed_set(
    seeds: tuple[int, ...],
    limit: int,
    pairs: list[list[tuple[int, int]]],
) -> ScanResult:
    if 2 not in seeds or 3 not in seeds:
        raise ValueError("the generalized gate is tested only for S containing {2,3}")
    if any(not allowed(seed) for seed in seeds):
        raise ValueError(("disallowed seed", seeds))
    if max(seeds) > limit:
        raise ValueError(("seed above limit", max(seeds), limit))

    seed_set = set(seeds)
    state = bytearray(limit + 1)
    active_hard = 0
    healed_splitless = 0
    active_prefix = [0] * (limit + 1)
    k = correction_k(seeds)
    required = -10**9
    required_at = 2
    first_failure = None
    trajectory = hashlib.sha256()

    for n in range(2, limit + 1):
        if n in seed_set:
            current = GENERATED
        elif allowed(n):
            current = classify(n, state, pairs)
        else:
            current = OTHER
        state[n] = current

        if current == HARD:
            if n % 2:
                raise AssertionError(("odd hard", n, seeds))
            active_hard += 1

        if n > 3 and n % 2 == 1 and current == GENERATED:
            parent = (n + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = chain_root(n)
                if state[root] == HARD:
                    active_hard -= 1
                elif state[root] == SPLITLESS:
                    healed_splitless += 1

        active_prefix[n] = active_hard
        quarter = active_prefix[n // 4]
        needed = active_hard - healed_splitless - quarter
        if needed > required:
            required = needed
            required_at = n
        margin = healed_splitless + quarter + k - active_hard
        if margin < 0 and first_failure is None:
            first_failure = {
                "X": n,
                "A_H": active_hard,
                "D": healed_splitless,
                "A_H_quarter": quarter,
                "k": k,
                "margin": margin,
            }

        trajectory.update(n.to_bytes(4, "little"))
        trajectory.update(active_hard.to_bytes(4, "little"))
        trajectory.update(healed_splitless.to_bytes(4, "little"))

    return ScanResult(
        seeds=seeds,
        k=k,
        required_correction=required,
        required_at=required_at,
        endpoint_ah=active_hard,
        endpoint_d=healed_splitless,
        first_k_failure=first_failure,
        trajectory_sha256=trajectory.hexdigest().upper(),
    )


def compact(result: ScanResult) -> dict[str, object]:
    return {
        "seeds": list(result.seeds),
        "chain_roots": sorted({chain_root(s) for s in result.seeds}),
        "k": result.k,
        "required_correction": result.required_correction,
        "required_at": result.required_at,
        "slack_k_minus_required": result.k - result.required_correction,
        "endpoint_A_H": result.endpoint_ah,
        "endpoint_D": result.endpoint_d,
        "first_k_failure": result.first_k_failure,
        "trajectory_sha256": result.trajectory_sha256,
    }


def candidate_seed_sets(
    limit: int,
    exhaustive_max: int,
    single_max: int,
    random_count: int,
) -> list[tuple[int, ...]]:
    base = (2, 3)
    pool = [n for n in range(5, min(exhaustive_max, limit) + 1) if allowed(n)]
    candidates: set[tuple[int, ...]] = {base, (2, 3, 66)} if limit >= 66 else {base}

    # The sharp falsifier search is k=2: add one arbitrary seed, including an
    # odd descendant whose even U-root is not itself seeded.
    for seed in range(5, min(single_max, limit) + 1):
        if allowed(seed):
            candidates.add(tuple(sorted(base + (seed,))))

    # Exhaust all extensions by up to three small allowed seeds.
    for size in range(1, 4):
        for extra in itertools.combinations(pool, size):
            candidates.add(tuple(sorted(base + extra)))

    # Target seeds on early literal U-chains and on known splitless-bank roots.
    targeted = [6, 11, 18, 20, 21, 32, 38, 41, 54, 66, 69, 77, 107, 131, 149]
    targeted = [n for n in targeted if n <= limit and allowed(n)]
    for size in range(1, min(6, len(targeted)) + 1):
        # A deterministic sparse selection of larger combinations is enough
        # for falsification; all pairs and triples are included.
        if size <= 3:
            iterable = itertools.combinations(targeted, size)
        else:
            iterable = itertools.islice(itertools.combinations(targeted, size), 250)
        for extra in iterable:
            candidates.add(tuple(sorted(set(base + extra))))

    rng = random.Random(424107)
    random_pool = [n for n in range(5, limit + 1) if allowed(n)]
    odd_pool = [n for n in random_pool if n % 2 == 1]
    for _ in range(random_count):
        size = rng.randint(1, min(12, len(random_pool)))
        extra = rng.sample(random_pool, size)
        candidates.add(tuple(sorted(set(base + tuple(extra)))))
        odd_size = rng.randint(1, min(12, len(odd_pool)))
        odd_extra = rng.sample(odd_pool, odd_size)
        candidates.add(tuple(sorted(set(base + tuple(odd_extra)))))

    return sorted(candidates, key=lambda s: (len(s), s))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5_000)
    parser.add_argument("--exhaustive-max", type=int, default=40)
    parser.add_argument("--single-max", type=int, default=5_000)
    parser.add_argument("--random-count", type=int, default=2_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 186:
        raise ValueError("limit must be at least 186")

    pairs = build_pairs(args.limit)
    candidates = candidate_seed_sets(
        args.limit, args.exhaustive_max, args.single_max, args.random_count
    )
    results = [scan_seed_set(seeds, args.limit, pairs) for seeds in candidates]
    failures = [r for r in results if r.first_k_failure is not None]
    worst = min(results, key=lambda r: (r.k - r.required_correction, len(r.seeds), r.seeds))
    by_k: dict[int, dict[str, int]] = {}
    correction_audit = {
        "chain_roots_k": {"failures": 0, "first": None},
        "chain_roots_k_minus_one": {"failures": 0, "first": None},
        "even_seed_roots": {"failures": 0, "first": None},
        "seed_values_minus_one": {"failures": 0, "first": None},
    }
    for result in results:
        row = by_k.setdefault(result.k, {
            "seed_sets": 0,
            "failures": 0,
            "max_required_correction": -10**9,
            "min_slack": 10**9,
        })
        row["seed_sets"] += 1
        row["failures"] += int(result.first_k_failure is not None)
        row["max_required_correction"] = max(
            row["max_required_correction"], result.required_correction
        )
        row["min_slack"] = min(row["min_slack"], result.k - result.required_correction)
        corrections = {
            "chain_roots_k": result.k,
            "chain_roots_k_minus_one": result.k - 1,
            "even_seed_roots": len({s for s in result.seeds if s % 2 == 0}),
            "seed_values_minus_one": len(result.seeds) - 1,
        }
        for name, value in corrections.items():
            if value >= result.required_correction:
                continue
            correction_audit[name]["failures"] += 1
            if correction_audit[name]["first"] is None:
                correction_audit[name]["first"] = {
                    "seeds": list(result.seeds),
                    "value": value,
                    "required": result.required_correction,
                    "required_at": result.required_at,
                }

    distinguished = []
    tight = []
    wanted = {(2, 3), (2, 3, 66)}
    for result in results:
        if result.seeds in wanted or result is worst or result.first_k_failure is not None:
            distinguished.append(compact(result))
        if result.k == result.required_correction:
            tight.append(compact(result))

    payload = {
        "schema": "C107-seed-sensitive-quarter-v1",
        "acceptance": "exact integer",
        "definition": {
            "U": "U(n)=2n-1",
            "chain_root": "rho(s)=1+oddpart(s-1)",
            "k": "number of distinct rho(s), s in S",
            "hypothesis": "finite allowed S containing {2,3}",
        },
        "limit": args.limit,
        "exhaustive_max": args.exhaustive_max,
        "single_max": args.single_max,
        "random_count_requested": args.random_count,
        "seed_sets_tested": len(results),
        "k_correction_failures": len(failures),
        "by_k": {str(k): row for k, row in sorted(by_k.items())},
        "correction_audit": correction_audit,
        "worst_slack": compact(worst),
        "tight_seed_sets_count": len(tight),
        "tight_seed_sets": tight[:250],
        "distinguished": distinguished[:100],
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "seed_sets_tested": len(results),
        "failures": len(failures),
        "worst_slack": worst.k - worst.required_correction,
        "worst_seeds": list(worst.seeds),
        "worst_required": worst.required_correction,
        "worst_k": worst.k,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
