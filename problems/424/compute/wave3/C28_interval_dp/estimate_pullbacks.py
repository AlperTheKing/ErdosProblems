"""Estimate exact tiled-DP work without allocating membership bit vectors.

For an interval I=[lo, hi) requested from D[a,b,c], channel (p,r) needs
exactly ceil((I-r)/p), clipped to the predecessor universe.  This script
propagates and coalesces those integer intervals through the full state DAG.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


CHANNELS = ((0, 2, 0), (1, 3, 1), (2, 5, 3))


def modulus(a: int, b: int, c: int) -> int:
    return (2**a) * (3**b) * (5**c)


def ceil_div(n: int, d: int) -> int:
    return -((-n) // d)


def merge(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    intervals.sort()
    out = [intervals[0]]
    for lo, hi in intervals[1:]:
        old_lo, old_hi = out[-1]
        if lo <= old_hi:
            out[-1] = (old_lo, max(old_hi, hi))
        else:
            out.append((lo, hi))
    return out


def estimate(a: int, b: int, c: int, lo: int, hi: int) -> dict[str, object]:
    requested: dict[tuple[int, int, int], list[tuple[int, int]]] = {
        (a, b, c): [(lo, hi)]
    }
    by_level: dict[int, dict[str, int]] = {}

    for level in range(a + b + c, 0, -1):
        additions: dict[tuple[int, int, int], list[tuple[int, int]]] = defaultdict(list)
        level_bits = 0
        level_intervals = 0
        level_states = 0
        for state, intervals in tuple(requested.items()):
            if sum(state) != level:
                continue
            level_states += 1
            level_intervals += len(intervals)
            level_bits += sum(end - start for start, end in intervals)
            for axis, p, r in CHANNELS:
                if state[axis] == 0:
                    continue
                child = list(state)
                child[axis] -= 1
                child_key = tuple(child)
                child_m = modulus(*child_key)
                for start, end in intervals:
                    child_lo = max(0, ceil_div(start - r, p))
                    child_hi = min(child_m, ceil_div(end - r, p))
                    if child_lo < child_hi:
                        additions[child_key].append((child_lo, child_hi))
        by_level[level] = {
            "states": level_states,
            "intervals": level_intervals,
            "bits": level_bits,
        }
        for state, intervals in additions.items():
            requested[state] = merge(intervals)

    base = requested.get((0, 0, 0), [])
    by_level[0] = {
        "states": int(bool(base)),
        "intervals": len(base),
        "bits": sum(end - start for start, end in base),
    }
    total_bits = sum(row["bits"] for row in by_level.values())
    total_intervals = sum(row["intervals"] for row in by_level.values())
    output_bits = hi - lo
    return {
        "state": [a, b, c],
        "modulus": modulus(a, b, c),
        "tile": [lo, hi],
        "output_bits": output_bits,
        "total_state_bits": total_bits,
        "work_ratio": total_bits / output_bits,
        "total_intervals": total_intervals,
        "max_level_bits": max(row["bits"] for row in by_level.values()),
        "levels": by_level,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=int)
    parser.add_argument("b", type=int)
    parser.add_argument("c", type=int)
    parser.add_argument("--tile-bits", type=int, required=True)
    parser.add_argument(
        "--positions",
        choices=("edges", "quartiles"),
        default="quartiles",
        help="sample first/middle/last or all quartile-aligned tiles",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    m = modulus(args.a, args.b, args.c)
    width = min(args.tile_bits, m)
    fractions = (0, 2, 4) if args.positions == "edges" else (0, 1, 2, 3, 4)
    starts = sorted({min(m - width, ((m - width) * q) // 4) for q in fractions})
    rows = [estimate(args.a, args.b, args.c, lo, lo + width) for lo in starts]
    summary = {
        "state": [args.a, args.b, args.c],
        "modulus": m,
        "tile_bits": width,
        "samples": rows,
        "min_work_ratio": min(row["work_ratio"] for row in rows),
        "max_work_ratio": max(row["work_ratio"] for row in rows),
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
