#!/usr/bin/env python3
"""Independent exact verifier for the C93 common-bank census.

The verifier uses direct trial-divisor pair enumeration, not the C++ SPF
factorization.  It also compares the resulting A_H and D sets with saved C87
Horn-graph artifacts at every available regression cutoff.
"""

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
FNV_OFFSET = 14_695_981_039_346_656_037
FNV_PRIME = 1_099_511_628_211
MASK64 = (1 << 64) - 1


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> tuple[tuple[int, int], ...]:
    pairs = []
    for left in range(2, math.isqrt(n + 1) + 1):
        if (n + 1) % left:
            continue
        right = (n + 1) // left
        if left < right and allowed(left) and allowed(right):
            pairs.append((left, right))
    return tuple(pairs)


def classify(n: int, state: bytearray) -> int:
    pairs = admissible_pairs(n)
    if any(state[left] == GENERATED and state[right] == GENERATED
           for left, right in pairs):
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


def fnv_byte(digest: int, value: int) -> int:
    return ((digest ^ value) * FNV_PRIME) & MASK64


def fnv_u64(digest: int, value: int) -> int:
    for shift in range(0, 64, 8):
        digest = fnv_byte(digest, (value >> shift) & 0xFF)
    return digest


def top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def ratio_better(d: int, a_h: int, current: tuple[int, int, int] | None) -> bool:
    return current is None or d * current[1] < current[0] * a_h


def scan(limit: int) -> tuple[dict, bytearray]:
    state = bytearray(limit + 1)
    hard_roots = 0
    active_hard = 0
    hard_deaths = 0
    splitless_roots = 0
    healed_splitless = 0
    event_count = 0
    positive_events = 0
    failures_5_6 = 0
    failures_3_4 = 0
    first_5_6 = None
    first_3_4 = None
    minimum = None
    class_digest = FNV_OFFSET
    event_digest = FNV_OFFSET

    checkpoints_at = sorted({x for x in (
        2, 54, 74, 186, 362, 1_000, 2_000, 5_000, 10_000,
        16_620, 100_000, 1_000_000, 100_000_000, 1_000_000_000, limit
    ) if x <= limit})
    checkpoints = []
    next_checkpoint = 0

    for x in range(2, limit + 1):
        current = GENERATED if x in (2, 3) else (classify(x, state) if allowed(x) else OTHER)
        state[x] = current
        event = False
        if current == SPLITLESS and x % 2 == 0:
            splitless_roots += 1
        if current == HARD:
            require(x % 2 == 0, ("odd-hard", x))
            hard_roots += 1
            active_hard += 1
            event = True

        if x % 2 and current != GENERATED and allowed(x):
            parent = (x + 1) // 2
            require(allowed(parent) and state[parent] != GENERATED,
                    ("odd-hole-parent", x, parent))

        if x % 2 and current == GENERATED and x > 3:
            parent = (x + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                value = x
                while value % 4 == 1:
                    value = (value + 1) // 2
                root = (value + 1) // 2
                require(root % 2 == 0 and state[root] != GENERATED,
                        ("invalid-root", x, root))
                if state[root] == HARD:
                    require(active_hard > 0, ("hard-underflow", x, root))
                    active_hard -= 1
                    hard_deaths += 1
                    event = True
                elif state[root] == SPLITLESS:
                    healed_splitless += 1
                    event = True

        if event:
            event_count += 1
            if active_hard:
                positive_events += 1
                if ratio_better(healed_splitless, active_hard, minimum):
                    minimum = (healed_splitless, active_hard, x)
                if 6 * healed_splitless < 5 * active_hard:
                    failures_5_6 += 1
                    if first_5_6 is None:
                        first_5_6 = {"X": x, "D": healed_splitless, "A_H": active_hard}
                if 4 * healed_splitless <= 3 * active_hard:
                    failures_3_4 += 1
                    if first_3_4 is None:
                        first_3_4 = {"X": x, "D": healed_splitless, "A_H": active_hard}
            event_digest = fnv_u64(event_digest, x)
            event_digest = fnv_u64(event_digest, active_hard)
            event_digest = fnv_u64(event_digest, healed_splitless)
        class_digest = fnv_byte(class_digest, current)

        if next_checkpoint < len(checkpoints_at) and x == checkpoints_at[next_checkpoint]:
            checkpoints.append({
                "X": x,
                "A_H": active_hard,
                "D": healed_splitless,
                "hard_roots": hard_roots,
                "splitless_roots": splitless_roots,
            })
            next_checkpoint += 1

    require(hard_roots == active_hard + hard_deaths, "hard accounting")
    require(splitless_roots >= healed_splitless, "splitless accounting")
    require(minimum is not None, "missing minimum ratio")
    divisor = math.gcd(minimum[0], minimum[1])
    summary = {
        "limit": limit,
        "counts": {
            "hard_roots": hard_roots,
            "A_H": active_hard,
            "hard_chain_deaths": hard_deaths,
            "splitless_roots": splitless_roots,
            "D": healed_splitless,
            "unhealed_splitless_roots": splitless_roots - healed_splitless,
        },
        "event_audit": {
            "event_count": event_count,
            "positive_demand_events": positive_events,
            "six_D_lt_five_A_H_count": failures_5_6,
            "first_six_D_lt_five_A_H": first_5_6,
            "four_D_le_three_A_H_count": failures_3_4,
            "first_four_D_le_three_A_H": first_3_4,
            "minimum_D_over_A_H": {
                "D": minimum[0],
                "A_H": minimum[1],
                "X": minimum[2],
                "reduced_numerator": minimum[0] // divisor,
                "reduced_denominator": minimum[1] // divisor,
            },
        },
        "checkpoints": checkpoints,
        "digests": {
            "algorithm": "FNV-1a-64 little-endian",
            "classification_2_through_limit": f"{class_digest:016x}",
            "event_X_A_H_D": f"{event_digest:016x}",
        },
    }
    return summary, state


def compare_c87(state: bytearray, cutoff: int, path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    hard = sorted(
        root for root in range(2, cutoff + 1, 2)
        if state[root] == HARD and state[top(root, cutoff)] != GENERATED
    )
    common_bank = sorted(
        root for root in range(2, cutoff + 1, 2)
        if state[root] == SPLITLESS and state[top(root, cutoff)] == GENERATED
    )
    require(hard == data["hard_roots"], ("C87-hard-set", cutoff))
    require(common_bank == data["common_neighbors"], ("C87-common-set", cutoff))
    return {"X": cutoff, "A_H": len(hard), "D": len(common_bank), "matched": True}


def static_endpoint_check(state: bytearray, cutoff: int, summary: dict) -> dict:
    hard = sum(
        state[root] == HARD and state[top(root, cutoff)] != GENERATED
        for root in range(2, cutoff + 1, 2)
    )
    common_bank = sum(
        state[root] == SPLITLESS and state[top(root, cutoff)] == GENERATED
        for root in range(2, cutoff + 1, 2)
    )
    require(hard == summary["counts"]["A_H"],
            ("static-endpoint-A_H", cutoff, hard, summary["counts"]["A_H"]))
    require(common_bank == summary["counts"]["D"],
            ("static-endpoint-D", cutoff, common_bank, summary["counts"]["D"]))
    return {"X": cutoff, "A_H": hard, "D": common_bank, "matched": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--cpp-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(54 <= args.limit <= 1_000_000, ("limit", args.limit))
    cpp = json.loads(args.cpp_output.read_text(encoding="utf-8"))
    require(cpp["limit"] == args.limit, ("cpp-limit", cpp["limit"], args.limit))
    summary, state = scan(args.limit)

    for key in ("hard_roots", "A_H", "hard_chain_deaths", "splitless_roots", "D",
                "unhealed_splitless_roots"):
        require(summary["counts"][key] == cpp["counts"][key],
                ("count", key, summary["counts"][key], cpp["counts"][key]))
    require(summary["event_audit"] == cpp["event_audit"], "event audit mismatch")
    require(summary["digests"] == cpp["digests"], "digest mismatch")
    require(summary["checkpoints"] == cpp["c87_regression_checkpoints"],
            "checkpoint mismatch")

    here = Path(__file__).resolve().parent
    c87_checks = []
    for cutoff in (54, 74, 186, 362, 1_000, 2_000, 5_000, 10_000):
        if cutoff > args.limit:
            continue
        candidates = [
            here / f"C87_horn_{cutoff}.json",
            here / f"C91_detail_{cutoff}.json",
        ]
        path = next((candidate for candidate in candidates if candidate.exists()), None)
        require(path is not None, ("missing-C87-artifact", cutoff))
        c87_checks.append(compare_c87(state, cutoff, path))

    output = {
        "schema": "C93-common-bank-independent-verify-v1",
        "verdict": "exact_match",
        "summary": summary,
        "static_endpoint_check": static_endpoint_check(state, args.limit, summary),
        "c87_set_checks": c87_checks,
        "cpp_output_sha256": hashlib.sha256(args.cpp_output.read_bytes()).hexdigest().upper(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": output["verdict"],
        "limit": args.limit,
        "c87_checks": len(c87_checks),
        "minimum": summary["event_audit"]["minimum_D_over_A_H"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
