#!/usr/bin/env python3
"""Independent exact replay of the R8 three-seed quarter countermodel."""

from __future__ import annotations

import hashlib
import json

GENERATED, SPLITLESS, HARD, OTHER = 1, 2, 3, 4
LIMIT = 186
EXPECTED_PREFIX = {
    2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65,
    66, 69, 77, 80, 81, 84, 87, 98, 99, 101, 105, 122, 125,
    129, 131, 134, 137, 149, 152, 153, 158, 159, 161, 164, 167,
    173,
}


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    result = []
    a = 2
    while a * a <= n + 1:
        if (n + 1) % a == 0:
            b = (n + 1) // a
            if a < b and allowed(a) and allowed(b):
                result.append((a, b))
        a += 1
    return result


def root_of(n: int) -> int:
    while n % 2:
        n = (n + 1) // 2
    return n


def classify(n: int, state: bytearray) -> int:
    pairs = factor_pairs(n)
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if n % 2 == 0:
        successor = n + 1
        if successor % 3:
            return HARD
        cofactor = successor // 3
        if not allowed(cofactor) or cofactor == 3:
            return HARD
    return OTHER


def main() -> None:
    state = bytearray(LIMIT + 1)
    for seed in (2, 3, 66):
        state[seed] = GENERATED

    hard_births: list[int] = []
    hard_deaths: dict[int, int] = {}
    splitless_heals: dict[int, int] = {}

    for n in range(4, LIMIT + 1):
        if n == 66:
            current = GENERATED
        else:
            current = classify(n, state) if allowed(n) else 0
        state[n] = current
        if current == HARD:
            hard_births.append(n)

        if n % 2 and current == GENERATED:
            parent = (n + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of(n)
                if state[root] == HARD:
                    hard_deaths.setdefault(root, n)
                elif state[root] == SPLITLESS:
                    splitless_heals.setdefault(root, n)

    prefix = {n for n in range(2, LIMIT + 1) if state[n] == GENERATED}
    persistent = [r for r in hard_births if hard_deaths.get(r, LIMIT + 1) > LIMIT]
    quarter_persistent = [
        r for r in hard_births
        if r <= LIMIT // 4 and hard_deaths.get(r, LIMIT + 1) > LIMIT // 4
    ]
    healed = sorted(r for r, time in splitless_heals.items() if time <= LIMIT)

    expected_persistent = [54, 74, 114, 144, 174, 186]
    expected_healed = [6, 18, 20, 38]
    checks = {
        "prefix": prefix == EXPECTED_PREFIX,
        "persistent_hard": persistent == expected_persistent,
        "quarter_persistent_hard": quarter_persistent == [],
        "healed_splitless": healed == expected_healed,
        "quarter_failure": len(persistent) > len(healed) + len(quarter_persistent) + 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"R8 replay failed: {failed}")

    result = {
        "schema": "R8-quarter-countermodel-v1",
        "acceptance": "exact integers",
        "seeds": [2, 3, 66],
        "cutoff": LIMIT,
        "quarter": LIMIT // 4,
        "generated_prefix": sorted(prefix),
        "persistent_hard": persistent,
        "healed_splitless": healed,
        "quarter_persistent_hard": quarter_persistent,
        "margin_D_plus_quarter_plus_1_minus_AH": (
            len(healed) + len(quarter_persistent) + 1 - len(persistent)
        ),
        "classification_sha256": hashlib.sha256(bytes(state[2:])).hexdigest().upper(),
        "checks": checks,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
