#!/usr/bin/env python3
"""Exact event-form replay and a local-descent obstruction for C92."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for a in range(2, math.isqrt(n + 1) + 1):
        if (n + 1) % a:
            continue
        b = (n + 1) // a
        if a < b and allowed(a) and allowed(b):
            pairs.append((a, b))
    return pairs


def classify(n: int, state: bytearray) -> int:
    pairs = factor_pairs(n)
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if n % 2 == 0:
        if (n + 1) % 3:
            return HARD
        parent = (n + 1) // 3
        if not allowed(parent) or parent == 3:
            return HARD
    return OTHER


def seed_root(n: int) -> int:
    value = n - 1
    while value % 2 == 0:
        value //= 2
    return value + 1


def scan(limit: int) -> dict:
    require(450 <= limit <= 200_000, ("limit", limit))
    state = bytearray(limit + 1)
    hard_birth_prefix = [0] * (limit + 1)
    hard_death_prefix = [0] * (limit + 1)
    active_hard_prefix = [0] * (limit + 1)
    splitless_death_prefix = [0] * (limit + 1)
    hard_death_time: dict[int, int] = {}
    splitless_death_time: dict[int, int] = {}
    active_hard = 0
    hard_births = 0
    hard_deaths = 0
    splitless_deaths = 0
    event_equivalence_failures = 0
    scale_upper_failures = 0
    scale_lower_failures = 0
    trajectory = hashlib.sha256()

    for x in range(2, limit + 1):
        if x in (2, 3):
            current = GENERATED
        elif allowed(x):
            current = classify(x, state)
        else:
            current = OTHER
        state[x] = current

        if current == HARD:
            require(x % 2 == 0, ("odd-hard", x))
            active_hard += 1
            hard_births += 1

        if x > 3 and x % 2 == 1 and current == GENERATED:
            parent = (x + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = seed_root(x)
                if state[root] == HARD:
                    active_hard -= 1
                    hard_deaths += 1
                    hard_death_time[root] = x
                elif state[root] == SPLITLESS:
                    splitless_deaths += 1
                    splitless_death_time[root] = x

        hard_birth_prefix[x] = hard_births
        hard_death_prefix[x] = hard_deaths
        active_hard_prefix[x] = active_hard
        splitless_death_prefix[x] = splitless_deaths

        quarter = x // 4
        interval_margin = (
            splitless_deaths
            + hard_deaths
            - hard_death_prefix[quarter]
            + 1
            - (hard_births - hard_birth_prefix[quarter])
        )
        scale_margin = (
            splitless_deaths + active_hard_prefix[quarter] + 1 - active_hard
        )
        if interval_margin != scale_margin:
            event_equivalence_failures += 1
        if scale_margin < 0:
            scale_upper_failures += 1
        if 2 * splitless_deaths - 7 * active_hard_prefix[quarter] < 0:
            scale_lower_failures += 1

        trajectory.update(x.to_bytes(4, "little"))
        trajectory.update(interval_margin.to_bytes(8, "little", signed=True))

    require(event_equivalence_failures == 0, "event equivalence failed")

    # Three persistent hard roots have a forced descent through the same
    # missing endpoint 11 and hence the same splitless seed root 6.
    forced = {54: (5, 11), 186: (11, 17), 450: (11, 41)}
    visible_chains: dict[str, list[int]] = {}
    for root, unique_pair in forced.items():
        require(state[root] == HARD, ("not-hard", root, state[root]))
        require(factor_pairs(root) == [unique_pair],
                ("nonunique-pair", root, factor_pairs(root)))
        missing = [u for u in unique_pair if state[u] != GENERATED]
        require(missing == [11], ("forced-endpoint", root, missing))
        node = root
        visible: list[int] = []
        while node <= 450:
            visible.append(node)
            require(state[node] != GENERATED,
                    ("not-persistent-at-450", root, node))
            node = 2 * node - 1
        visible_chains[str(root)] = visible

    require(state[6] == SPLITLESS, ("root-6", state[6]))
    require(splitless_death_time.get(6) == 41,
            ("root-6-death", splitless_death_time.get(6)))
    require(seed_root(11) == 6, ("root-of-11", seed_root(11)))

    return {
        "schema": "C92-event-obstruction-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "event_form": {
            "statement": (
                "H_birth(X)-H_birth(floor(X/4)) <= D(X)+"
                "H_death(X)-H_death(floor(X/4))+1"
            ),
            "algebraic_equivalence_failures": event_equivalence_failures,
            "inequality_failures": scale_upper_failures,
        },
        "scale_quarter_lower_failures": scale_lower_failures,
        "local_capacity_one_obstruction": {
            "cutoff": 450,
            "persistent_hard_roots": sorted(forced),
            "unique_admissible_pairs": {
                str(root): list(pair) for root, pair in forced.items()
            },
            "forced_missing_endpoint": 11,
            "common_seed_root": 6,
            "common_seed_root_first_generated_descendant": 41,
            "visible_hole_chains": visible_chains,
            "conclusion": (
                "Any capacity-one charge using only a hard root's missing "
                "factor seed root sends all three sources to the same target."
            ),
        },
        "endpoint": {
            "A_H": active_hard,
            "D": splitless_deaths,
            "hard_births": hard_births,
            "hard_deaths": hard_deaths,
        },
        "event_trajectory_sha256": trajectory.hexdigest().upper(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "limit": result["limit"],
        "event_equivalence_failures": result["event_form"][
            "algebraic_equivalence_failures"
        ],
        "event_inequality_failures": result["event_form"][
            "inequality_failures"
        ],
        "scale_lower_failures": result["scale_quarter_lower_failures"],
        "obstruction": result["local_capacity_one_obstruction"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
