#!/usr/bin/env python3
"""Independent scalar verifier for the simple .net fixture format."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path


def load_network(path: Path) -> tuple[int, list[tuple[int, int]]]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    key, n_text = lines[0].split()
    if key != "n":
        raise ValueError("first data line must be 'n <channels>'")
    n = int(n_text)
    pairs = [tuple(map(int, line.split())) for line in lines[1:]]
    for lo, hi in pairs:
        if not 0 <= lo < hi < n:
            raise ValueError(f"invalid comparator {(lo, hi)} for n={n}")
    return n, pairs


def verify(n: int, pairs: list[tuple[int, int]]) -> tuple[int, int | None]:
    failures = 0
    first_failure = None
    for mask in range(1 << n):
        values = [(mask >> i) & 1 for i in range(n)]
        for lo, hi in pairs:
            if values[lo] > values[hi]:
                values[lo], values[hi] = values[hi], values[lo]
        if any(values[i] > values[i + 1] for i in range(n - 1)):
            failures += 1
            if first_failure is None:
                first_failure = mask
    return failures, first_failure


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("network", type=Path)
    parser.add_argument("--expect", type=int)
    args = parser.parse_args()
    n, pairs = load_network(args.network)
    if args.expect is not None and len(pairs) != args.expect:
        raise SystemExit(f"expected {args.expect} comparators, found {len(pairs)}")
    started = time.perf_counter()
    failures, first_failure = verify(n, pairs)
    elapsed = time.perf_counter() - started
    print(json.dumps({
        "verifier": "python-scalar",
        "file": str(args.network),
        "sha256": hashlib.sha256(args.network.read_bytes()).hexdigest(),
        "channels": n,
        "comparators": len(pairs),
        "inputs": 1 << n,
        "failures": failures,
        "first_failure": first_failure,
        "elapsed_s": round(elapsed, 6),
    }, sort_keys=True))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
