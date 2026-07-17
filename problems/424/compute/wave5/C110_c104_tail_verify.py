#!/usr/bin/env python3
"""Independent exact verifier for the C110 tail and blocker-profile gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


GENERATED = 1
SPLITLESS = 2
HARD = 3
THRESHOLD_MAXIMUM = 64
SCALE_BITS = 32
SCALE = 1 << SCALE_BITS
FNV_OFFSET = 14_695_981_039_346_656_037
FNV_PRIME = 1_099_511_628_211
MASK64 = (1 << 64) - 1


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def full_spf(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    factors = []
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        factors.append((p, exponent))
    result = [1]
    for p, exponent in factors:
        old = tuple(result)
        power = 1
        for _ in range(exponent):
            power *= p
            result.extend(value * power for value in old)
    return result


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for left in divisors(product, spf):
        right = product // left
        if left >= 2 and left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return sorted(result)


def classify(n: int, spf: list[int], state: bytearray) -> tuple[int, list[tuple[int, int]]]:
    if n in (2, 3):
        return GENERATED, []
    if not allowed(n):
        return 0, []
    pairs = admissible_pairs(n, spf)
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
        return GENERATED, pairs
    if not pairs:
        return SPLITLESS, pairs
    if n % 2 == 0:
        product = n + 1
        easy = product % 3 == 0 and product // 3 != 3 and allowed(product // 3)
        if not easy:
            return HARD, pairs
    return 0, pairs


def seed_root(endpoint: int) -> int:
    require(endpoint > 1 and endpoint % 2 == 1, ("endpoint", endpoint))
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def failure(source: int, root: int, d: int, dyadic_bin: int, lhs: int, rhs: int) -> dict:
    return {
        "source_h": source,
        "last_root": root,
        "D": d,
        "bin": dyadic_bin,
        "lhs": lhs,
        "rhs": rhs,
    }


def reconstruct(limit: int) -> dict:
    require(limit <= 300_000, "independent verifier is capped at 300000")
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    maximum_d: dict[int, int] = {}
    bin_counts = [[0] * 32 for _ in range(THRESHOLD_MAXIMUM + 1)]
    root_counts = [0] * (THRESHOLD_MAXIMUM + 1)
    occupied_bins = [0] * (THRESHOLD_MAXIMUM + 1)
    scaled_load = [0] * (THRESHOLD_MAXIMUM + 1)
    integrated = [0] * 32
    target_events = []
    hard_sources = 0
    maximum_pair_count = 0
    digest = FNV_OFFSET
    failures = {
        "first_C104_BIN_failure": None,
        "first_integrated_load_failure": None,
        "first_occupied_bin_Carleson_failure": None,
        "first_full_Carleson_failure": None,
    }

    for n in range(2, limit + 1):
        current, pairs = classify(n, spf, state)
        state[n] = current
        digest = ((digest ^ current) * FNV_PRIME) & MASK64
        if current != HARD:
            continue
        hard_sources += 1
        pair_count = len(pairs)
        maximum_pair_count = max(maximum_pair_count, pair_count)

        witnessed: dict[int, int] = {}
        for left, right in pairs:
            blocked = False
            for endpoint in (left, right):
                if state[endpoint] == GENERATED:
                    continue
                blocked = True
                root = seed_root(endpoint)
                require(state[root] != GENERATED, ("generated-root", n, endpoint, root))
                if state[root] != SPLITLESS:
                    witnessed[root] = min(witnessed.get(root, endpoint), endpoint)
            require(blocked, ("unblocked-hard-pair", n, left, right))

        one_hole = sum(
            (state[left] != GENERATED) + (state[right] != GENERATED) == 1
            for left, right in pairs
        )
        two_hole = pair_count - one_hole
        capped = min(pair_count, THRESHOLD_MAXIMUM)

        for root, endpoint in sorted(witnessed.items()):
            old_d = maximum_d.get(root, 0)
            if capped <= old_d:
                continue
            dyadic_bin = (root - 1).bit_length() - 1
            old_q = 0 if old_d == 0 else old_d - 1
            new_q = capped - 1
            integrated[dyadic_bin] += new_q - old_q
            if (
                failures["first_integrated_load_failure"] is None
                and integrated[dyadic_bin] > 1 << dyadic_bin
            ):
                failures["first_integrated_load_failure"] = failure(
                    n, root, 0, dyadic_bin, integrated[dyadic_bin], 1 << dyadic_bin
                )

            for k in range(old_d + 1, capped + 1):
                if k < 2:
                    continue
                d = k - 1
                if bin_counts[k][dyadic_bin] == 0:
                    occupied_bins[k] += 1
                bin_counts[k][dyadic_bin] += 1
                root_counts[k] += 1
                scaled_load[k] += 1 << (SCALE_BITS - dyadic_bin)

                bin_lhs = d * bin_counts[k][dyadic_bin]
                bin_rhs = 1 << dyadic_bin
                if failures["first_C104_BIN_failure"] is None and bin_lhs > bin_rhs:
                    failures["first_C104_BIN_failure"] = failure(
                        n, root, d, dyadic_bin, bin_lhs, bin_rhs
                    )
                carleson_lhs = d * scaled_load[k]
                occupied_rhs = occupied_bins[k] * SCALE
                if (
                    failures["first_occupied_bin_Carleson_failure"] is None
                    and carleson_lhs > occupied_rhs
                ):
                    failures["first_occupied_bin_Carleson_failure"] = failure(
                        n, root, d, dyadic_bin, carleson_lhs, occupied_rhs
                    )
                full_rhs = n.bit_length() * SCALE
                if (
                    failures["first_full_Carleson_failure"] is None
                    and carleson_lhs > full_rhs
                ):
                    failures["first_full_Carleson_failure"] = failure(
                        n, root, d, dyadic_bin, carleson_lhs, full_rhs
                    )

            maximum_d[root] = capped
            if root in (54, 62):
                target_events.append(
                    {
                        "root": root,
                        "source_h": n,
                        "endpoint": endpoint,
                        "d": pair_count,
                        "one_hole_pairs": one_hole,
                        "two_hole_pairs": two_hole,
                    }
                )

    thresholds = []
    for k in range(2, THRESHOLD_MAXIMUM + 1):
        if root_counts[k]:
            thresholds.append(
                {
                    "D": k - 1,
                    "root_count": root_counts[k],
                    "occupied_bins": occupied_bins[k],
                    "scaled_dyadic_load": scaled_load[k],
                    "scale": SCALE,
                }
            )
    return {
        "limit": limit,
        "hard_sources": hard_sources,
        "maximum_pair_count": maximum_pair_count,
        "classification_fnv1a64": f"{digest:016x}",
        **failures,
        "thresholds": thresholds,
        "target_root_upgrade_events": target_events,
    }


def verify(path: Path) -> dict:
    data = path.read_bytes()
    actual = json.loads(data)
    expected = reconstruct(int(actual["limit"]))
    for key, value in expected.items():
        require(actual[key] == value, ("mismatch", key, value, actual[key]))
    return {
        "schema": "C110-c104-tail-independent-verifier-v1",
        "input": path.name,
        "input_sha256": hashlib.sha256(data).hexdigest().upper(),
        "limit": actual["limit"],
        "classification_exact_match": True,
        "threshold_loads_exact_match": True,
        "first_failures_exact_match": True,
        "target_blocker_profiles_exact_match": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.input)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
