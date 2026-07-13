#!/usr/bin/env python3
"""Independent exact verifier for P66 completion-charge search artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def pair_sums(values: tuple[int, ...]) -> Counter[int]:
    return Counter(
        values[i] + values[j]
        for j in range(len(values))
        for i in range(j + 1)
    )


def analyze(values: list[int]) -> dict[str, int | list[int]]:
    a = tuple(sorted(values))
    if len(a) != len(set(a)) or not a or a[0] != 0:
        raise AssertionError("witness must be a normalized set")
    sums = pair_sums(a)
    repeated = [s for s, count in sums.items() if count >= 2]
    if len(repeated) != 1:
        raise AssertionError("witness does not have exactly one repeated sum")
    sigma = repeated[0]
    aset = set(a)
    core = tuple(x for x in a if sigma - x in aset)
    residual = tuple(x for x in a if sigma - x not in aset)
    if not residual:
        raise AssertionError("witness has empty residual")

    delta = int(sigma % 2 == 0 and sigma // 2 in aset)
    p = (len(core) - delta) // 2
    c = len(core)
    u = len(residual)
    span = a[-1]
    differences = {
        a[j] - a[i]
        for j in range(len(a))
        for i in range(j)
    }
    q = Counter(
        abs(residual[i] + residual[j] - sigma)
        for j in range(u)
        for i in range(j + 1)
    )
    if 0 in q or max(q.values(), default=0) > 2:
        raise AssertionError("invalid virtual-label multiplicity")
    beta = sum(max(0, int(d in differences) + count - 1) for d, count in q.items())
    expected_sum_support = 2 * p * (p + delta) + 1 + c * u + u * (u + 1) // 2
    if len(sums) != expected_sum_support:
        raise AssertionError("sum-support identity failed")
    expected_difference_support = p * (p + delta) + c * u + u * (u - 1) // 2
    if len(differences) != expected_difference_support:
        raise AssertionError("difference-support identity failed")
    h_s = 2 * span + 1 - len(sums)
    return {
        "A": list(a),
        "span": span,
        "sigma": sigma,
        "p": p,
        "delta": delta,
        "c": c,
        "u": u,
        "beta": beta,
        "hS": h_s,
        "margin": h_s - 2 * beta,
        "tau": abs(sigma - span),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--expect-n36", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.artifact.read_text(encoding="utf-8"))
    if data.get("arithmetic") != "integer only":
        raise AssertionError("artifact does not declare integer arithmetic")
    if not (1 <= int(data["threads"]) <= 64):
        raise AssertionError("worker cap violated")
    if args.expect_n36:
        expected = {"admissible": 510_030, "repeated_residual": 412_860}
        for key, value in expected.items():
            if data["counts"][key] != value:
                raise AssertionError((key, data["counts"][key], value))

    checked = 0
    for field in ("min_margin", "min_unproved_margin", "max_ratio", "first_failure"):
        record = data.get(field)
        if record is None:
            continue
        rebuilt = analyze(record["A"])
        for key, value in rebuilt.items():
            if record[key] != value:
                raise AssertionError((field, key, record[key], value))
        checked += 1

    failure = data.get("first_failure")
    if data["counts"]["failures"] == 0:
        if failure is not None:
            raise AssertionError("zero failures but a failure witness is present")
    elif failure is None or failure["margin"] >= 0:
        raise AssertionError("failure count lacks a negative-margin witness")

    print(json.dumps({
        "artifact": str(args.artifact),
        "counts": data["counts"],
        "checked_witnesses": checked,
        "status": "PASS",
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
