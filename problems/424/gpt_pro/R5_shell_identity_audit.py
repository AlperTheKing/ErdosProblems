#!/usr/bin/env python3
"""Independent exact replay of the R5 shell identity and T0 obstruction."""

from __future__ import annotations

import json
from pathlib import Path


I = {6, 8, 11, 15, 29, 54, 57, 74}


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_for(n: int) -> list[tuple[int, int]]:
    product = n + 1
    pairs: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if allowed(a) and allowed(b):
                pairs.append((a, b))
        a += 1
    return pairs


def hard_shape(n: int) -> bool:
    pairs = pairs_for(n)
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def in_t0(n: int) -> bool:
    return allowed(n) and n not in I


def h(n: int) -> int:
    return int(allowed(n) and not in_t0(n))


def w_x(r: int, x: int) -> int:
    y = (x + 1) // 2
    w = r
    while w <= y:
        w = 2 * w - 1
    assert y < w <= x
    return w


def audit(limit: int = 1000) -> dict:
    factor_table: dict[str, list[list[int]]] = {}
    for n in sorted(I):
        pairs = pairs_for(n)
        factor_table[str(n)] = [list(pair) for pair in pairs]
        assert all(a in I or b in I for a, b in pairs)

    checked_cutoffs = 0
    for x in range(2, limit + 1):
        y = (x + 1) // 2
        q_direct = sum(
            1
            for m in range(2, y + 1)
            if allowed(m) and not in_t0(m) and in_t0(2 * m - 1)
        )
        q_identity = sum(
            h(m) - h(2 * m - 1)
            for m in range(2, y + 1)
            if allowed(m)
        )
        assert q_direct == q_identity

        hard_count = sum(
            1
            for n in range(2, x + 1)
            if allowed(n) and hard_shape(n) and not in_t0(n)
        )
        rhs_shell = sum(
            1
            for n in range(y + 1, x + 1)
            if allowed(n) and n % 2 and not in_t0(n)
        )
        rhs_shell += sum(
            1
            for n in range(y + 1, x + 1)
            if allowed(n) and hard_shape(n) and not in_t0(n)
        )
        rhs_shell -= sum(
            1
            for n in range(2, y + 1)
            if allowed(n)
            and n % 2 == 0
            and not hard_shape(n)
            and not in_t0(n)
        )
        assert hard_count - q_direct == rhs_shell

        chain_positive = 0
        chain_negative = 0
        for r in range(2, x + 1):
            if not allowed(r) or r % 2:
                continue
            w = w_x(r, x)
            if hard_shape(r) and not in_t0(w):
                chain_positive += 1
            if (
                not hard_shape(r)
                and r <= y
                and not in_t0(r)
                and in_t0(w)
            ):
                chain_negative += 1
        assert hard_count - q_direct == chain_positive - chain_negative
        checked_cutoffs += 1

    x = 74
    y = (x + 1) // 2
    hard_holes = [
        n
        for n in range(2, x + 1)
        if allowed(n) and hard_shape(n) and not in_t0(n)
    ]
    q_parents = [
        m
        for m in range(2, y + 1)
        if allowed(m) and not in_t0(m) and in_t0(2 * m - 1)
    ]
    assert hard_holes == [54, 74]
    assert q_parents == [11]

    result = {
        "limit": limit,
        "checked_cutoffs": checked_cutoffs,
        "factor_table": factor_table,
        "x74": {
            "hard_holes": hard_holes,
            "q_parents": q_parents,
            "H_minus_Q": len(hard_holes) - len(q_parents),
        },
    }
    out = Path(__file__).with_name("R5_shell_identity_audit_1000.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
