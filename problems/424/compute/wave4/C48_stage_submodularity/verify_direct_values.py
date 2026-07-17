#!/usr/bin/env python3
"""Direct integer evaluation of the two C48 hole-domain lattice witnesses."""

from __future__ import annotations

import json
from pathlib import Path

from verify_stage_obstructions import allowed, is_hard_shape, least_g, pairs_of


LIMIT = 1000


def main() -> None:
    pairs = [pairs_of(n) if n >= 2 else [] for n in range(LIMIT + 1)]
    G = least_g(LIMIT, pairs)
    events = []
    for n in range(4, LIMIT + 1):
        if is_hard_shape(n, pairs[n]):
            events.append((n, n, 1))
    for q in range(4, (LIMIT + 1) // 2 + 1):
        if allowed(q) and G[2 * q - 1]:
            events.append((2 * q - 1, q, -1))

    def unsupported(node: int, deleted: set[int]) -> int:
        return int(all(a in deleted or b in deleted for a, b in pairs[node]))

    def value(deleted: set[int], cutoff: int) -> int:
        return sum(
            coefficient * unsupported(node, deleted)
            for event, node, coefficient in events
            if event <= cutoff
        )

    result = {}
    for name, cutoff, x, y, expected in (
        ("submodularity", 594, 35, 119, [-9, -10, -8, -10, -1]),
        ("supermodularity", 69, 12, 18, [0, 0, -1, 0, 1]),
    ):
        values = [
            value({x}, cutoff),
            value({y}, cutoff),
            value({x, y}, cutoff),
            value(set(), cutoff),
        ]
        mixed = values[0] + values[1] - values[2] - values[3]
        observed = values + [mixed]
        if observed != expected:
            raise AssertionError((name, observed, expected))
        result[name] = {
            "X": cutoff,
            "D1": [x],
            "D2": [y],
            "D1_is_actual_hole": not G[x],
            "D2_is_actual_hole": not G[y],
            "f_D1": values[0],
            "f_D2": values[1],
            "f_union": values[2],
            "f_intersection": values[3],
            "mixed_difference": mixed,
        }
    out = Path(__file__).with_name("direct_values.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
