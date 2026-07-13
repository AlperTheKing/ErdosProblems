"""Independent literal verifier for parallel Singer affine-scan outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def unordered_sum_counts(values: list[int]) -> Counter[int]:
    return Counter(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def verify(path: Path) -> dict[str, object]:
    record = json.loads(path.read_text(encoding="ascii"))
    best = record["best_candidate"]
    if not isinstance(best, dict):
        raise AssertionError("scan has no candidate")
    b = [int(x) for x in best["points"]]
    center = int(best["candidate_center"])
    if b != sorted(set(b)) or not b or b[0] != 0:
        raise AssertionError("invalid normalized lower block")
    if center <= 2 * b[-1]:
        raise AssertionError("reflected blocks overlap")
    if max(unordered_sum_counts(b).values()) != 1:
        raise AssertionError("lower block is not Sidon")

    reflected = sorted(b + [center - x for x in b])
    if len(reflected) != 2 * len(b) or len(set(reflected)) != len(reflected):
        raise AssertionError("reflected set has collisions")
    repeats = sorted(
        (value, count)
        for value, count in unordered_sum_counts(reflected).items()
        if count >= 2
    )
    if repeats != [(center, len(b))]:
        raise AssertionError(("not admissible", repeats))

    p = len(b)
    return {
        "file": path.as_posix(),
        "p": p,
        "center": center,
        "center_over_p2": str(Fraction(center, p * p)),
        "reflected_size": 2 * p,
        "repeats": repeats,
        "status": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()
    for path in args.inputs:
        print(json.dumps(verify(path), sort_keys=True))


if __name__ == "__main__":
    main()
