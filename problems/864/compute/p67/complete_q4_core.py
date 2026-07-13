"""Complete the q=4 excess core to a valid P37 pair and verify its fibers."""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path


HERE = Path(__file__).resolve().parent
CORE = HERE / "q4_excess_core_result.json"
OUT = HERE / "q4_excess_valid_pair.json"


def pair_sums(values: tuple[int, ...]) -> set[int]:
    return {a + b for i, a in enumerate(values) for b in values[i:]}


def differences(values: tuple[int, ...]) -> set[int]:
    return {b - a for i, a in enumerate(values) for b in values[i + 1 :]}


def is_sidon(values: tuple[int, ...]) -> bool:
    return len(pair_sums(values)) == len(values) * (len(values) + 1) // 2


def valid_gap(values: tuple[int, ...], gap: int) -> bool:
    return differences(values).isdisjoint({gap + s for s in pair_sums(values)})


def blocks(values: tuple[int, ...], target: int, cutoff: int) -> tuple[tuple[int, ...], ...]:
    low = tuple(value for value in values if value <= cutoff)
    return tuple(
        triple
        for triple in combinations_with_replacement(low, 3)
        if sum(triple) == target and len(set(triple)) in (1, 3)
    )


def search(max_endpoint: int) -> dict[str, object] | None:
    core = json.loads(CORE.read_text(encoding="ascii"))["result"]
    labels = tuple(int(value) for value in core["labels"])
    x, y = int(core["x"]), int(core["y"])
    for endpoint in range(max(labels) + 1, max_endpoint + 1):
        values = tuple(sorted((*labels, endpoint)))
        if not is_sidon(values):
            continue
        for gap in range(1, endpoint - max(x, y) + 1):
            if not valid_gap(values, gap):
                continue
            cutoff = endpoint - gap
            left, right = blocks(values, x, cutoff), blocks(values, y, cutoff)
            left_support = set().union(*(set(block) for block in left))
            right_support = set().union(*(set(block) for block in right))
            assert len(left) == len(right) == 4
            assert len(left_support) == len(right_support) == 12
            assert len(left_support & right_support) == 11
            return {
                "Z": list(values),
                "p": len(values),
                "W": endpoint,
                "G": gap,
                "K": cutoff,
                "x": x,
                "y": y,
                "left_blocks": [list(block) for block in left],
                "right_blocks": [list(block) for block in right],
                "left_support": sorted(left_support),
                "right_support": sorted(right_support),
                "intersection": sorted(left_support & right_support),
                "intersection_size": 11,
                "block_count_sum": 8,
                "excess": 3,
                "pair_sum_count": len(pair_sums(values)),
                "positive_difference_count": len(differences(values)),
                "cross_intersection": sorted(
                    differences(values).intersection(
                        {gap + s for s in pair_sums(values)}
                    )
                ),
            }
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-endpoint", type=int, default=30000)
    args = parser.parse_args()
    result = search(args.max_endpoint)
    payload = {"exact_arithmetic": "integers", "result": result}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
