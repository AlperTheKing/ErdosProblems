#!/usr/bin/env python3
"""Independent verifier for the C100 fixed-orbit overlap census."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DIVISORS = (2, 3, 5)
PAIR_BITS = {"23": 0b011, "25": 0b101, "35": 0b110}


def orbit(limit: int) -> bytearray:
    member = bytearray(limit + 1)
    for seed in (2, 3, 5):
        member[seed] = 1
    for n in range(6, limit + 1):
        shifted = n + 1
        member[n] = any(
            shifted % divisor == 0
            and shifted // divisor != divisor
            and member[shifted // divisor]
            for divisor in DIVISORS
        )
    return member


def mask_at(n: int, member: bytearray) -> int:
    shifted = n + 1
    mask = 0
    for bit, divisor in enumerate(DIVISORS):
        if (
            shifted % divisor == 0
            and shifted // divisor != divisor
            and member[shifted // divisor]
        ):
            mask |= 1 << bit
    return mask


def payload(limit: int) -> dict[str, object]:
    member = orbit(limit)
    prefix = [0] * (limit + 1)
    count = 0
    for n, flag in enumerate(member):
        count += flag
        prefix[n] = count

    image_sizes = {
        str(divisor): prefix[(limit + 1) // divisor] - 1
        for divisor in DIVISORS
    }
    intersections = {name: 0 for name in PAIR_BITS}
    triple = 0
    pair_audits = {
        name: {
            "intersection": 0,
            "failures": 0,
            "first_failure": 0,
            "last_failure": 0,
            "worst_x": 0,
            "worst_excess": "0",
            "worst_intersection": 0,
            "worst_left_size": 0,
            "worst_right_size": 0,
            "min_margin_after_5000_x": 0,
            "min_margin_after_5000": None,
        }
        for name in PAIR_BITS
    }
    quadratic = {
        "inequality": "X*Delta(X) <= 3*C(X)^2",
        "failures": 0,
        "first_failure": 0,
        "last_failure": 0,
        "worst_x": 0,
        "worst_excess": "0",
    }
    residue_capacity = [0] * 30
    residue_image = {str(divisor): [0] * 30 for divisor in DIVISORS}
    residue_pair = {name: [0] * 30 for name in PAIR_BITS}

    for n in range(limit + 1):
        residue_capacity[n % 30] += 1
        if member[n]:
            mask = mask_at(n, member)
            for bit, divisor in enumerate(DIVISORS):
                if mask & (1 << bit):
                    residue_image[str(divisor)][n % 30] += 1
            for name, bits in PAIR_BITS.items():
                if mask & bits == bits:
                    intersections[name] += 1
                    residue_pair[name][n % 30] += 1
            triple += mask == 0b111
        if n < 24:
            continue
        for name, (left, right) in zip(PAIR_BITS, ((2, 3), (2, 5), (3, 5))):
            left_size = prefix[(n + 1) // left] - 1
            right_size = prefix[(n + 1) // right] - 1
            lhs = intersections[name] * n
            rhs = left_size * right_size
            audit = pair_audits[name]
            if lhs > rhs:
                excess = lhs - rhs
                audit["failures"] += 1
                if audit["first_failure"] == 0:
                    audit["first_failure"] = n
                audit["last_failure"] = n
                if excess > int(audit["worst_excess"]):
                    audit["worst_x"] = n
                    audit["worst_excess"] = str(excess)
                    audit["worst_intersection"] = intersections[name]
                    audit["worst_left_size"] = left_size
                    audit["worst_right_size"] = right_size
            elif n >= 5000:
                margin = rhs - lhs
                old_margin = audit["min_margin_after_5000"]
                if old_margin is None or margin < int(old_margin):
                    audit["min_margin_after_5000"] = str(margin)
                    audit["min_margin_after_5000_x"] = n
        collision_tax = sum(intersections.values()) - triple
        lhs = collision_tax * n
        rhs = 3 * prefix[n] ** 2
        if lhs > rhs:
            excess = lhs - rhs
            quadratic["failures"] += 1
            if quadratic["first_failure"] == 0:
                quadratic["first_failure"] = n
            quadratic["last_failure"] = n
            if excess > int(quadratic["worst_excess"]):
                quadratic["worst_x"] = n
                quadratic["worst_excess"] = str(excess)

    for name in PAIR_BITS:
        pair_audits[name]["intersection"] = intersections[name]
        if pair_audits[name]["min_margin_after_5000"] is None:
            pair_audits[name]["min_margin_after_5000"] = "0"

    residue_audits: dict[str, dict[str, int | str]] = {}
    for name, (left, right) in zip(PAIR_BITS, ((2, 3), (2, 5), (3, 5))):
        failures = []
        for residue in range(30):
            intersection = residue_pair[name][residue]
            left_size = residue_image[str(left)][residue]
            right_size = residue_image[str(right)][residue]
            capacity = residue_capacity[residue]
            excess = intersection * capacity - left_size * right_size
            if excess > 0:
                failures.append(
                    (
                        excess,
                        residue,
                        intersection,
                        left_size,
                        right_size,
                        capacity,
                    )
                )
        worst = max(failures, default=(0, 0, 0, 0, 0, 0))
        residue_audits[name] = {
            "failures": len(failures),
            "worst_residue": worst[1],
            "worst_intersection": worst[2],
            "worst_left_size": worst[3],
            "worst_right_size": worst[4],
            "worst_capacity": worst[5],
            "worst_excess": str(worst[0]),
        }

    return {
        "limit": limit,
        "orbit_count": count,
        "image_sizes": image_sizes,
        "triple_intersection": triple,
        "collision_tax": sum(intersections.values()) - triple,
        "intersections": intersections,
        "pair_audits": pair_audits,
        "residue_30_pair_audits": residue_audits,
        "quadratic_tax_audit": quadratic,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    stored = json.loads(args.result.read_text(encoding="ascii"))
    limit = int(stored["limit"])
    if limit > 2_000_000:
        raise SystemExit("independent verifier is limited to 2,000,000")
    replay = payload(limit)

    assert stored["orbit_count"] == replay["orbit_count"]
    assert stored["image_sizes"] == replay["image_sizes"]
    assert stored["triple_intersection"] == replay["triple_intersection"]
    assert stored["collision_tax"] == replay["collision_tax"]
    for name in PAIR_BITS:
        assert (
            stored["pair_audits"][name]["intersection"]
            == replay["intersections"][name]
        )
        assert stored["pair_audits"][name] == replay["pair_audits"][name]
        assert (
            stored["residue_30_pair_audits"][name]
            == replay["residue_30_pair_audits"][name]
        )
    assert stored["quadratic_tax_audit"] == replay["quadratic_tax_audit"]
    print(json.dumps({"verified": True, **replay}, indent=2))


if __name__ == "__main__":
    main()
