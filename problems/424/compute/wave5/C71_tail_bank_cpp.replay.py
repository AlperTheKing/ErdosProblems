#!/usr/bin/env python3
"""Independent small replay for the C71 exact incremental scanner.

The replay discovers admissible pairs by direct trial division.  It does not
import C67 code and does not use the C++ kernel's smallest-prime-factor table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path
from typing import Any


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
FNV_OFFSET = 14_695_981_039_346_656_037
FNV_PRIME = 1_099_511_628_211
MASK64 = (1 << 64) - 1


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def fnv_byte(digest: int, value: int) -> int:
    return ((digest ^ value) * FNV_PRIME) & MASK64


def fnv_u64(digest: int, value: int) -> int:
    for shift in range(0, 64, 8):
        digest = fnv_byte(digest, (value >> shift) & 0xFF)
    return digest


def classify_direct(n: int, state: bytearray) -> int:
    product = n + 1
    has_admissible_pair = False
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left >= right:
            continue
        if not allowed(left) or not allowed(right):
            continue
        has_admissible_pair = True
        if state[left] == GENERATED and state[right] == GENERATED:
            return GENERATED
    if not has_admissible_pair:
        return SPLITLESS
    if n % 2 == 0:
        if product % 3:
            return HARD
        parent = product // 3
        if not allowed(parent) or parent == 3:
            return HARD
    return OTHER


def checkpoint_cutoffs(limit: int) -> list[int]:
    values = {2, 6, 54, 74, 16_620, 175_956, 1_000_000, limit}
    x = 10
    while x <= limit:
        values.add(x)
        x *= 10
    return sorted(x for x in values if x <= limit)


class Audit:
    def __init__(self) -> None:
        self.checked_cutoffs = 0
        self.failure_count = 0
        self.first_failure: dict[str, int] | None = None
        self.ratio_numerator = 0
        self.ratio_denominator = 1
        self.ratio_x = 0
        self.maximum_excess: int | None = None
        self.maximum_excess_x = 0
        self.maximum_excess_left = 0
        self.maximum_excess_right = 0
        self.endpoint_left = 0
        self.endpoint_right = 0

    def observe(self, x: int, left: int, right: int) -> None:
        self.checked_cutoffs += 1
        if left > right:
            self.failure_count += 1
            if self.first_failure is None:
                self.first_failure = {
                    "X": x,
                    "left": left,
                    "right": right,
                    "excess": left - right,
                }
        if right and left * self.ratio_denominator > self.ratio_numerator * right:
            self.ratio_numerator = left
            self.ratio_denominator = right
            self.ratio_x = x
        excess = left - right
        if self.maximum_excess is None or excess > self.maximum_excess:
            self.maximum_excess = excess
            self.maximum_excess_x = x
            self.maximum_excess_left = left
            self.maximum_excess_right = right
        self.endpoint_left = left
        self.endpoint_right = right

    def as_dict(self, limit: int, left_name: str) -> dict[str, Any]:
        divisor = math.gcd(self.ratio_numerator, self.ratio_denominator)
        return {
            "checked_cutoffs": self.checked_cutoffs,
            "failure_count": self.failure_count,
            "first_failure": self.first_failure,
            "max_ratio": {
                "numerator": self.ratio_numerator,
                "denominator": self.ratio_denominator,
                "X": self.ratio_x,
                "reduced_numerator": self.ratio_numerator // divisor,
                "reduced_denominator": self.ratio_denominator // divisor,
            },
            "maximum_excess": {
                "value": self.maximum_excess,
                "X": self.maximum_excess_x,
                "left": self.maximum_excess_left,
                "right": self.maximum_excess_right,
            },
            "endpoint": {
                "X": limit,
                left_name: self.endpoint_left,
                "e_plus": self.endpoint_right,
            },
            "verdict": (
                "fails" if self.first_failure else "no_failure_through_limit"
            ),
        }


def replay(limit: int) -> dict[str, Any]:
    state = bytearray(limit + 1)
    wanted = checkpoint_cutoffs(limit)
    next_checkpoint = 0
    checkpoints: list[dict[str, int]] = []
    generated_count = 0
    allowed_count = 0
    splitless_count = 0
    splitless_half = 0
    hard_count = 0
    active_hard = 0
    deaths = 0
    classification_digest = FNV_OFFSET
    trajectory_digest = FNV_OFFSET
    terminal_audit = Audit()
    all_hard_audit = Audit()

    for x in range(2, limit + 1):
        current = OTHER
        if x in (2, 3):
            current = GENERATED
        elif allowed(x):
            current = classify_direct(x, state)
        state[x] = current

        if allowed(x):
            allowed_count += 1
        if current == GENERATED:
            generated_count += 1
        elif current == SPLITLESS:
            splitless_count += 1
        elif current == HARD:
            assert x % 2 == 0
            hard_count += 1
            active_hard += 1

        if x % 2 and current != GENERATED and allowed(x):
            parent = (x + 1) // 2
            assert allowed(parent) and state[parent] != GENERATED

        if x % 2 and current == GENERATED and x > 3:
            parent = (x + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                low_bit = (x - 1) & -(x - 1)
                root = (x - 1) // low_bit + 1
                assert root % 2 == 0 and state[root] != GENERATED
                if state[root] == HARD:
                    active_hard -= 1
                    deaths += 1

        if x % 2 == 0 and state[x // 2] == SPLITLESS:
            splitless_half += 1
        e_plus = splitless_count - splitless_half
        terminal_audit.observe(x, active_hard, e_plus)
        all_hard_audit.observe(x, hard_count, e_plus)

        classification_digest = fnv_byte(classification_digest, current)
        trajectory_digest = fnv_u64(trajectory_digest, x)
        trajectory_digest = fnv_u64(trajectory_digest, active_hard)
        trajectory_digest = fnv_u64(trajectory_digest, e_plus)
        trajectory_digest = fnv_u64(trajectory_digest, hard_count)

        if next_checkpoint < len(wanted) and x == wanted[next_checkpoint]:
            checkpoints.append(
                {
                    "X": x,
                    "generated": generated_count,
                    "E": splitless_count,
                    "K": hard_count,
                    "A_H": active_hard,
                    "e_plus": e_plus,
                    "hard_chain_deaths": deaths,
                }
            )
            next_checkpoint += 1

    assert hard_count == active_hard + deaths
    terminal = terminal_audit.as_dict(limit, "A_H")
    all_hard = all_hard_audit.as_dict(limit, "K")
    if limit >= 175_956:
        assert terminal["failure_count"] == 0
        assert all_hard["failure_count"] == 0
        assert terminal["max_ratio"] == {
            "numerator": 656,
            "denominator": 1033,
            "X": 16_620,
            "reduced_numerator": 656,
            "reduced_denominator": 1033,
        }
        assert all_hard["max_ratio"] == {
            "numerator": 8846,
            "denominator": 9907,
            "X": 175_956,
            "reduced_numerator": 8846,
            "reduced_denominator": 9907,
        }

    return {
        "limit": limit,
        "counts": {
            "allowed": allowed_count,
            "generated": generated_count,
            "holes": allowed_count - generated_count,
            "E": splitless_count,
            "K": hard_count,
            "A_H": active_hard,
            "e_plus": terminal_audit.endpoint_right,
            "hard_chain_deaths": deaths,
        },
        "inequalities": {
            "A_H_le_e_plus": terminal,
            "K_le_e_plus": all_hard,
        },
        "checkpoints": checkpoints,
        "digests": {
            "algorithm": "FNV-1a-64 little-endian",
            "classification_2_through_limit": f"{classification_digest:016x}",
            "trajectory_X_A_H_e_plus_K": f"{trajectory_digest:016x}",
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest().upper()


def first_difference(left: Any, right: Any, path: str = "$" ) -> str | None:
    if type(left) is not type(right):
        return f"{path}: types {type(left).__name__} != {type(right).__name__}"
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return f"{path}: keys {sorted(left)} != {sorted(right)}"
        for key in left:
            difference = first_difference(left[key], right[key], f"{path}.{key}")
            if difference:
                return difference
        return None
    if isinstance(left, list):
        if len(left) != len(right):
            return f"{path}: lengths {len(left)} != {len(right)}"
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            difference = first_difference(
                left_item, right_item, f"{path}[{index}]"
            )
            if difference:
                return difference
        return None
    if left != right:
        return f"{path}: {left!r} != {right!r}"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=200_000)
    parser.add_argument("--cpp-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 2 <= args.limit <= 1_000_000:
        raise SystemExit("replay LIMIT must lie in [2,1000000]")

    command = [str(args.exe.resolve()), str(args.limit), str(args.cpp_output)]
    cpp_started = time.perf_counter()
    completed = subprocess.run(command, text=True, capture_output=True, check=True)
    cpp_seconds = time.perf_counter() - cpp_started
    with args.cpp_output.open(encoding="utf-8") as handle:
        cpp_full = json.load(handle)
    cpp_summary = {
        key: cpp_full[key]
        for key in ("limit", "counts", "inequalities", "checkpoints", "digests")
    }

    python_started = time.perf_counter()
    python_summary = replay(args.limit)
    python_seconds = time.perf_counter() - python_started
    difference = first_difference(python_summary, cpp_summary)
    if difference:
        raise AssertionError(f"independent replay mismatch: {difference}")

    certificate = {
        "schema_version": 1,
        "status": "exact_match",
        "limit": args.limit,
        "independent_method": (
            "Python direct trial division for every candidate factor; no C67 import "
            "and no smallest-prime-factor table"
        ),
        "cpp_command": command,
        "cpp_stdout": completed.stdout.strip(),
        "verified_fields": [
            "counts",
            "both per-cutoff inequality audits",
            "checkpoints",
            "classification digest",
            "A_H/e_plus/K trajectory digest",
        ],
        "summary_sha256": canonical_sha256(python_summary),
        "cpp_executable_sha256": sha256(args.exe),
        "cpp_output_sha256": sha256(args.cpp_output),
        "replay_source_sha256": sha256(Path(__file__)),
        "timing_seconds": {
            "cpp_wall": round(cpp_seconds, 6),
            "python_replay": round(python_seconds, 6),
        },
        "summary": python_summary,
    }
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(certificate, handle, indent=2)
        handle.write("\n")
    print(
        f"exact_match limit={args.limit} cpp_seconds={cpp_seconds:.3f} "
        f"python_seconds={python_seconds:.3f}"
    )


if __name__ == "__main__":
    main()
