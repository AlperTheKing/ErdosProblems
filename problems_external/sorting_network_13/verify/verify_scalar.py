#!/usr/bin/env python3
"""Exhaustive scalar verifier for binary sorting-network fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load_fixture(path: Path) -> tuple[dict[str, Any], list[tuple[int, int]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "sorting-network-fixture-v1":
        raise ValueError(f"{path}: unsupported schema")

    channels = data["channels"]
    expected_comparators = data["expected_comparators"]
    expected_depth = data["expected_depth"]
    layers = data["layers"]
    if not isinstance(channels, int) or channels < 2:
        raise ValueError(f"{path}: invalid channel count")
    if len(layers) != expected_depth:
        raise ValueError(
            f"{path}: depth is {len(layers)}, expected {expected_depth}"
        )

    flat: list[tuple[int, int]] = []
    for layer_index, layer in enumerate(layers):
        used: set[int] = set()
        for pair in layer:
            if (
                not isinstance(pair, list)
                or len(pair) != 2
                or not all(isinstance(x, int) for x in pair)
            ):
                raise ValueError(f"{path}: malformed comparator {pair!r}")
            low, high = pair
            if not 0 <= low < high < channels:
                raise ValueError(f"{path}: out-of-range comparator {pair!r}")
            if low in used or high in used:
                raise ValueError(
                    f"{path}: channel reused in layer {layer_index}: {pair!r}"
                )
            used.update(pair)
            flat.append((low, high))
    if len(flat) != expected_comparators:
        raise ValueError(
            f"{path}: {len(flat)} comparators, expected {expected_comparators}"
        )
    return data, flat


def network_sha256(comparators: list[tuple[int, int]]) -> str:
    canonical = ";".join(f"{low},{high}" for low, high in comparators)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def verify(path: Path) -> dict[str, Any]:
    data, comparators = load_fixture(path)
    channels = data["channels"]
    tested = 1 << channels
    failures = 0
    first_failure: int | None = None

    for word in range(tested):
        wires = [(word >> channel) & 1 for channel in range(channels)]
        for low, high in comparators:
            if wires[low] > wires[high]:
                wires[low], wires[high] = wires[high], wires[low]

        ones = word.bit_count()
        expected = [0] * (channels - ones) + [1] * ones
        if wires != expected:
            failures += 1
            if first_failure is None:
                first_failure = word

    return {
        "fixture": data["id"],
        "channels": channels,
        "comparators": len(comparators),
        "depth": len(data["layers"]),
        "binary_inputs_tested": tested,
        "failures": failures,
        "first_failure": first_failure,
        "network_sha256": network_sha256(comparators),
        "accepted": failures == 0,
    }


def main() -> int:
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fixtures",
        nargs="*",
        type=Path,
        default=[
            fixtures_dir / "sn12_40_depth8.json",
            fixtures_dir / "sn13_46_depth9.json",
        ],
    )
    args = parser.parse_args()

    results = [verify(path.resolve()) for path in args.fixtures]
    report = {
        "schema": "sorting-network-verification-v1",
        "verifier": "python-scalar-v1",
        "representation": "one binary input as a mutable list of channel bits",
        "results": results,
        "accepted": all(item["accepted"] for item in results),
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
