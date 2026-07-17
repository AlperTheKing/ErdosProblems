#!/usr/bin/env python3
"""Independent exact audit of the C92 terminal-blocker descent and obstructions."""

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
    out: list[tuple[int, int]] = []
    target = n + 1
    for a in range(2, math.isqrt(target) + 1):
        if target % a:
            continue
        b = target // a
        if a < b and allowed(a) and allowed(b):
            out.append((a, b))
    return out


def classify(n: int, state: bytearray) -> int:
    pairs = factor_pairs(n)
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if n % 2 == 0:
        if (n + 1) % 3:
            return HARD
        quotient = (n + 1) // 3
        if not allowed(quotient) or quotient == 3:
            return HARD
    return OTHER


def seed_root(n: int) -> int:
    require(n >= 2, ("seed-root-input", n))
    odd_part = n - 1
    while odd_part % 2 == 0:
        odd_part //= 2
    return odd_part + 1


def build_state(limit: int) -> bytearray:
    state = bytearray(limit + 1)
    for n in range(2, limit + 1):
        if n in (2, 3):
            state[n] = GENERATED
        elif allowed(n):
            state[n] = classify(n, state)
    return state


def visible_chain(root: int, cutoff: int) -> list[int]:
    out: list[int] = []
    node = root
    while node <= cutoff:
        out.append(node)
        node = 2 * node - 1
    return out


def crossing_time(root: int, state: bytearray) -> int | None:
    node = root
    while node < len(state):
        if state[node] == GENERATED:
            return node
        node = 2 * node - 1
    return None


def terminal_descent(hole_factor: int, state: bytearray) -> list[int]:
    require(state[hole_factor] != GENERATED,
            ("generated-hole-factor", hole_factor))
    root = seed_root(hole_factor)
    path = [root]
    require(state[root] != GENERATED, ("generated-seed-root", hole_factor, root))
    while state[root] not in (SPLITLESS, HARD):
        require(state[root] == OTHER, ("bad-terminal-class", root, state[root]))
        require((root + 1) % 3 == 0, ("non-easy-root", root))
        quotient = (root + 1) // 3
        require(quotient != 3 and allowed(quotient),
                ("invalid-easy-quotient", root, quotient))
        require(state[quotient] != GENERATED,
                ("generated-easy-quotient", root, quotient))
        next_root = seed_root(quotient)
        require(next_root < root, ("nondecreasing-descent", root, next_root))
        require(state[next_root] != GENERATED,
                ("generated-next-root", root, next_root))
        root = next_root
        path.append(root)
    return path


def verify_generation_certificate(
    certificate: list[tuple[int, int, int]], state: bytearray
) -> None:
    known = {2, 3}
    for output, a, b in certificate:
        require(a != b, ("equal-inputs", output, a, b))
        require(a in known and b in known,
                ("input-not-previously-certified", output, a, b, sorted(known)))
        require(output == a * b - 1, ("bad-product", output, a, b))
        require(state[output] == GENERATED, ("not-generated", output))
        known.add(output)


def scan(limit: int) -> dict:
    require(3_859 <= limit <= 1_000_000, ("limit", limit))
    state = build_state(limit)

    hard_min = next(
        n for n in range(2, limit + 1)
        if state[n] == HARD
    )
    require(hard_min == 54, ("hard-min", hard_min))

    persistent_roots = 0
    checked_pairs = 0
    checked_hole_endpoints = 0
    max_descent_slack = None
    max_descent_witness = None
    trajectory = hashlib.sha256()

    for root in range(2, limit + 1):
        if state[root] != HARD:
            continue
        chain = visible_chain(root, limit)
        if any(state[node] == GENERATED for node in chain):
            continue
        persistent_roots += 1
        pairs = factor_pairs(root)
        require(pairs, ("hard-without-pair", root))
        for pair in pairs:
            checked_pairs += 1
            require(pair[0] >= 5, ("small-hard-factor", root, pair))
            holes = [n for n in pair if state[n] != GENERATED]
            require(holes, ("generated-hard-pair", root, pair))
            for hole in holes:
                checked_hole_endpoints += 1
                path = terminal_descent(hole, state)
                terminal = path[-1]
                require(state[terminal] in (SPLITLESS, HARD),
                        ("nonterminal", root, hole, path))
                slack = 8 * terminal - root
                require(slack <= 0,
                        ("one-eighth-failure", root, pair, hole, path, slack))
                if max_descent_slack is None or slack > max_descent_slack:
                    max_descent_slack = slack
                    max_descent_witness = {
                        "hard_root": root,
                        "factor_pair": list(pair),
                        "hole_factor": hole,
                        "descent_path": path,
                        "eight_terminal_minus_root": slack,
                    }
                trajectory.update(root.to_bytes(8, "little"))
                trajectory.update(hole.to_bytes(8, "little"))
                trajectory.update(terminal.to_bytes(8, "little"))

    expected_pairs: dict[int, list[tuple[int, int]]] = {
        8: [],
        15: [(2, 8)],
        29: [(2, 15), (5, 6)],
        57: [(2, 29)],
        113: [(2, 57), (3, 38)],
        12: [],
        23: [(2, 12), (3, 8)],
        45: [(2, 23)],
        89: [(2, 45), (3, 30), (5, 18), (6, 15)],
        74: [(5, 15)],
        114: [(5, 23)],
        227: [(2, 114), (6, 38)],
        3858: [(17, 227)],
        450: [(11, 41)],
    }
    for n, expected in expected_pairs.items():
        require(factor_pairs(n) == expected,
                ("factor-list", n, factor_pairs(n), expected))

    for n in (6, 8, 12, 18, 30, 38):
        require(state[n] == SPLITLESS, ("not-splitless", n, state[n]))
    for n in (15, 29, 57, 113, 23, 45, 89, 74, 114, 227, 3858, 450):
        require(state[n] != GENERATED, ("unexpectedly-generated", n, state[n]))

    for root in (74, 114):
        require(state[root] == HARD, ("not-hard-114-witness", root, state[root]))
        require(all(state[n] != GENERATED for n in visible_chain(root, 114)),
                ("not-persistent-114", root, visible_chain(root, 114)))
    require(seed_root(15) == 8 and seed_root(23) == 12,
            ("terminal-roots-114", seed_root(15), seed_root(23)))
    require(crossing_time(8, state) is None or crossing_time(8, state) > 114,
            ("root-8-crosses-too-early", crossing_time(8, state)))
    require(crossing_time(12, state) is None or crossing_time(12, state) > 114,
            ("root-12-crosses-too-early", crossing_time(12, state)))
    require(not any(
        state[n] == HARD and all(
            state[node] != GENERATED for node in visible_chain(n, 28)
        )
        for n in range(2, 29)
    ), "hard-root-through-28")

    certificate = [
        (5, 2, 3),
        (9, 2, 5),
        (26, 3, 9),
        (51, 2, 26),
        (101, 2, 51),
        (302, 3, 101),
        (905, 3, 302),
    ]
    verify_generation_certificate(certificate, state)
    require(state[3858] == HARD, ("3858-not-hard", state[3858]))
    require(seed_root(227) == 114, ("rho-227", seed_root(227)))
    require(crossing_time(114, state) is not None, "root-114-never-crosses")
    require(crossing_time(114, state) <= 905,
            ("root-114-crossing", crossing_time(114, state)))
    require(crossing_time(114, state) <= 3858,
            ("root-114-active-at-3858", crossing_time(114, state)))

    require(seed_root(11) == 6 and seed_root(41) == 6,
            ("contracted-loop", seed_root(11), seed_root(41)))
    require(state[11] != GENERATED and state[41] == GENERATED,
            ("loop-endpoint-states", state[11], state[41]))
    require(seed_root(5) == 2 and seed_root(15) == 8
            and seed_root(29) == 8,
            ("parallel-root-data", seed_root(5), seed_root(15), seed_root(29)))

    for n in visible_chain(8, 296):
        require(state[n] != GENERATED, ("root-8-crossed-by-296", n))
    require(crossing_time(6, state) == 41,
            ("root-6-crossing", crossing_time(6, state)))

    return {
        "schema": "C92-gpt-pro-audit-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "one_eighth_descent_census": {
            "persistent_hard_roots": persistent_roots,
            "checked_factor_pairs": checked_pairs,
            "checked_hole_endpoints": checked_hole_endpoints,
            "failures": 0,
            "closest_witness": max_descent_witness,
            "trajectory_sha256": trajectory.hexdigest().upper(),
        },
        "local_obstructions": {
            "late_splitless_at_X_114": {
                "sources": [74, 114],
                "terminal_splitless_roots": [8, 12],
                "crossing_times": [crossing_time(8, state), crossing_time(12, state)],
                "A_H_floor_X_over_4": 0,
                "conclusion": (
                    "Neither natural terminal descent lands in D(114) or A_H(28); "
                    "one dummy cannot pay both sources."
                ),
            },
            "early_hard_crossing_at_X_3858": {
                "source": 3858,
                "blocked_factor": 227,
                "terminal_hard_root": 114,
                "terminal_crossing_time": crossing_time(114, state),
                "quarter_cutoff": 964,
                "certificate_top": 905,
                "conclusion": (
                    "The unique terminal root lies in neither D(3858) nor A_H(964)."
                ),
            },
            "seed_root_loop": {
                "factor_pair": [11, 41],
                "common_seed_root": 6,
            },
            "descendant_charge_II_at_X_296": {
                "sources_at_quarter_cutoff": [54, 74],
                "terminal_roots": [6, 8],
                "terminal_roots_healed_by_296": [6],
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
