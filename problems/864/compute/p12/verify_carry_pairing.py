"""Exact audit of the Singer carry-pairing lemma on stored P12 candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def positive_differences(values: list[int]) -> set[int]:
    return {
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    }


def unordered_sums(values: list[int]) -> set[int]:
    return {
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    }


def four_sum_contains(values: list[int], target: int) -> bool:
    pair_sums = unordered_sums(values)
    return any(target - x in pair_sums for x in pair_sums)


def audit_record(record: dict[str, object]) -> dict[str, object] | None:
    best = record.get("best_candidate")
    if not isinstance(best, dict):
        return None
    if record["family"] != "singer":
        return None

    v = int(record["modulus"])
    b = [int(x) for x in best["points"]]
    p = len(b)
    length = b[-1]
    center = int(best["candidate_center"])
    delta = positive_differences(b)
    sums = unordered_sums(b)

    assert v % 2 == 1
    assert len(delta) == (v - 1) // 2
    reflected_delta = {v - d for d in delta}
    assert delta.isdisjoint(reflected_delta)
    assert delta | reflected_delta == set(range(1, v))

    x = center - v
    assert x > 2 * length - v
    excess = {s - x for s in sums if s > x}
    literal_hole = all(center - s not in delta for s in sums)
    assert literal_hole
    assert literal_hole == excess.issubset(delta)

    tail = {s for s in sums if s > x}
    paired_tail = {s for s in tail if v + 2 * x - s in tail}
    represented = {s for s in paired_tail if center - s in delta}
    assert 2 * len(represented) == len(paired_tail)

    double_target = 2 * center - v
    assert not any(double_target - s in sums for s in sums)

    terminal_gap = v - length
    assert set(range(1, terminal_gap)).issubset(delta)
    assert all(h in delta for h in range(1, terminal_gap))

    second = b[-2]
    forced_center = v + length + second
    assert all(forced_center - s not in delta for s in sums)

    low_branch = 2 * center <= 4 * length + v
    low_missing = None
    if low_branch:
        y = 4 * length + v - 2 * center
        reflected = [length - value for value in b]
        assert 0 <= y < v
        assert not four_sum_contains(reflected, y)
        low_missing = y

    return {
        "parameter": int(record["parameter"]),
        "p": p,
        "v": v,
        "L": length,
        "M": center,
        "branch": "four-sum" if low_branch else "upper",
        "low_missing": low_missing,
        "terminal_gap": terminal_gap,
        "forced_center": forced_center,
        "paired_tail": len(paired_tail),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()

    audited: list[dict[str, object]] = []
    for path in args.inputs:
        for line in path.read_text(encoding="ascii").splitlines():
            result = audit_record(json.loads(line))
            if result is not None:
                audited.append(result)
                print(json.dumps(result, sort_keys=True))

    assert audited
    branches = {
        name: sum(row["branch"] == name for row in audited)
        for name in ("four-sum", "upper")
    }
    print(json.dumps({"audited": len(audited), "branches": branches}, sort_keys=True))


if __name__ == "__main__":
    main()
