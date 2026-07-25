#!/usr/bin/env python3
"""Independent small-corpus audit for the bounded skew-Kostka gate.

This file deliberately shares no counting or partition-enumeration code with
the Rust scanner.  It counts tableaux as chains of horizontal strips and
compares those counts with the pinned ehrcalc command-line binary.  It also
fingerprints the complete canonical pre-filter scope at |lambda| <= 12.
It never launches the 50,000-instance gate.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EHRCALC = (
    ROOT
    / "problems_external"
    / "ktt_lr_negativity"
    / "vendor"
    / "ehrcalc"
    / "target"
    / "release"
    / "ehrcalc.exe"
)


def normalize(parts: tuple[int, ...]) -> tuple[int, ...]:
    end = len(parts)
    while end and parts[end - 1] == 0:
        end -= 1
    return parts[:end]


@lru_cache(maxsize=None)
def partitions(n: int, max_len: int, max_part: int) -> tuple[tuple[int, ...], ...]:
    if n == 0:
        return ((),)
    if max_len == 0 or max_part == 0:
        return ()
    answer: list[tuple[int, ...]] = []
    for first in range(min(n, max_part), 0, -1):
        for tail in partitions(n - first, max_len - 1, first):
            answer.append((first,) + tail)
    return tuple(answer)


def contained(inner: tuple[int, ...], outer: tuple[int, ...]) -> bool:
    return all(
        (inner[i] if i < len(inner) else 0)
        <= (outer[i] if i < len(outer) else 0)
        for i in range(max(len(inner), len(outer)))
    )


def key(instance: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]) -> str:
    return "|".join(",".join(map(str, part)) for part in instance)


def exhaustive_scope() -> list[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    answer = []
    for outer_size in range(1, 13):
        for outer in partitions(outer_size, 6, outer_size):
            for inner_size in range(outer_size):
                for inner in partitions(inner_size, len(outer), outer[0]):
                    if not contained(inner, outer):
                        continue
                    skew_size = outer_size - inner_size
                    for weight in partitions(skew_size, 6, skew_size):
                        answer.append((outer, inner, weight))
    return answer


def horizontal_strip(outer: tuple[int, ...], inner: tuple[int, ...]) -> bool:
    rows = max(len(outer), len(inner))
    for i in range(rows):
        outer_i = outer[i] if i < len(outer) else 0
        inner_i = inner[i] if i < len(inner) else 0
        outer_next = outer[i + 1] if i + 1 < len(outer) else 0
        if not (outer_i >= inner_i >= outer_next):
            return False
    return True


def intermediate_shapes(
    inner: tuple[int, ...], outer: tuple[int, ...]
) -> tuple[tuple[int, ...], ...]:
    rows = len(outer)
    padded_inner = inner + (0,) * (rows - len(inner))
    answer: list[tuple[int, ...]] = []

    def visit(row: int, previous: int, prefix: list[int]) -> None:
        if row == rows:
            answer.append(normalize(tuple(prefix)))
            return
        upper = min(previous, outer[row])
        lower = padded_inner[row]
        for value in range(upper, lower - 1, -1):
            prefix.append(value)
            visit(row + 1, value, prefix)
            prefix.pop()

    visit(0, outer[0], [])
    return tuple(answer)


def tableau_count(
    outer: tuple[int, ...], inner: tuple[int, ...], weight: tuple[int, ...]
) -> int:
    """Count SSYT independently as nested partitions with horizontal strips."""

    if sum(outer) - sum(inner) != sum(weight) or not contained(inner, outer):
        return 0
    shapes = intermediate_shapes(inner, outer)
    by_size: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for shape in shapes:
        by_size[sum(shape)].append(shape)
    states = {inner: 1}
    current_size = sum(inner)
    for strip_size in weight:
        current_size += strip_size
        next_states: dict[tuple[int, ...], int] = defaultdict(int)
        for prior, multiplicity in states.items():
            for later in by_size[current_size]:
                if contained(prior, later) and horizontal_strip(later, prior):
                    next_states[later] += multiplicity
        states = next_states
    return states.get(outer, 0)


def dilate(parts: tuple[int, ...], n: int) -> tuple[int, ...]:
    return normalize(tuple(n * part for part in parts))


def ehrcalc_count(
    outer: tuple[int, ...], inner: tuple[int, ...], weight: tuple[int, ...]
) -> int:
    command = [
        str(EHRCALC),
        "kostka",
        "--lambda",
        ",".join(map(str, outer)),
        "--mu",
        ",".join(map(str, inner)),
        "--weight",
        ",".join(map(str, weight)),
        "--format",
        "json",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return int(json.loads(completed.stdout)["kostka"])


def main() -> None:
    scope = exhaustive_scope()
    scope_keys = sorted(key(instance) for instance in scope)
    scope_digest = hashlib.sha256(
        "".join(item + "\n" for item in scope_keys).encode("ascii")
    ).hexdigest()
    assert len(scope) == len(set(scope_keys)) == 69_218

    small = []
    for instance in scope:
        outer, inner, weight = instance
        if sum(outer) <= 7 and len(outer) <= 4 and len(weight) <= 4:
            value = tableau_count(outer, inner, weight)
            if value:
                small.append((hashlib.sha256(key(instance).encode()).digest(), instance, value))
    small.sort()
    base_sample = small[:128]
    dilation_two_sample = small[:40]

    comparisons = 0
    for _, (outer, inner, weight), independent in base_sample:
        assert independent == ehrcalc_count(outer, inner, weight)
        comparisons += 1
    for _, (outer, inner, weight), _ in dilation_two_sample:
        outer_two = dilate(outer, 2)
        inner_two = dilate(inner, 2)
        weight_two = tuple(2 * part for part in weight)
        independent = tableau_count(outer_two, inner_two, weight_two)
        assert independent == ehrcalc_count(outer_two, inner_two, weight_two)
        comparisons += 1

    print(
        json.dumps(
            {
                "status": "PASS",
                "canonical_scope_count": len(scope),
                "canonical_scope_sha256": scope_digest,
                "independent_tableau_comparisons": comparisons,
                "base_dilation_comparisons": len(base_sample),
                "dilation_two_comparisons": len(dilation_two_sample),
                "ehrcalc_binary": str(EHRCALC),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
