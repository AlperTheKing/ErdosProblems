#!/usr/bin/env python3
"""Search exact phase twins for indexed signed-ruler residue statistics."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path


def is_sidon(z: tuple[int, ...]) -> bool:
    sums = [z[i] + z[j] for i in range(len(z)) for j in range(i, len(z))]
    return len(sums) == len(set(sums))


def labels(z: tuple[int, ...], gap: int) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    p = len(z)
    differences = tuple(z[j] - z[i] for i in range(p) for j in range(i + 1, p))
    sum_stars = tuple(
        tuple(gap + z[i] + z[j] for j in range(i, p))
        for i in range(p)
    )
    return differences, sum_stars


def residue_signatures(
    z: tuple[int, ...], gap: int
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Return global, indexed-off-diagonal, and indexed-full cross counts."""
    p = len(z)
    differences, sum_stars = labels(z, gap)
    global_profile: list[int] = []
    indexed_off: list[int] = []
    indexed_full: list[int] = []
    for modulus in range(p, p * p + 1):
        dcounts = Counter(value % modulus for value in differences)
        modulus_full: list[int] = []
        modulus_off: list[int] = []
        for star in sum_stars:
            full_count = sum(dcounts[value % modulus] for value in star)
            off_count = sum(dcounts[value % modulus] for value in star[1:])
            modulus_full.append(full_count)
            modulus_off.append(off_count)
        global_profile.append(sum(modulus_full))
        indexed_off.extend(modulus_off)
        indexed_full.extend(modulus_full)
    return tuple(global_profile), tuple(indexed_off), tuple(indexed_full)


def quotient_moments(
    z: tuple[int, ...], gap: int, degree: int, include_diagonal: bool
) -> tuple[int, ...]:
    p = len(z)
    differences, sum_stars = labels(z, gap)
    profile: list[int] = []
    for modulus in range(p, p * p + 1):
        for star in sum_stars:
            chosen = star if include_diagonal else star[1:]
            moments = [0] * (degree + 1)
            for d in differences:
                for c in chosen:
                    delta = d - c
                    if delta % modulus == 0:
                        quotient = delta // modulus
                        power = 1
                        for order in range(degree + 1):
                            moments[order] += power
                            power *= quotient
            profile.extend(moments)
    return tuple(profile)


def make_record(z: tuple[int, ...], gap: int) -> dict[str, object]:
    differences, sum_stars = labels(z, gap)
    sums = tuple(value for star in sum_stars for value in star)
    overlap = sorted(set(differences).intersection(sums))
    return {
        "z": z,
        "gap": gap,
        "width": z[-1],
        "span": gap + 2 * z[-1],
        "valid": not overlap,
        "overlap": overlap,
    }


def update_twin_table(
    table: dict[tuple[object, ...], dict[bool, dict[str, object]]],
    key: tuple[object, ...],
    record: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]] | None:
    valid = bool(record["valid"])
    bucket = table.setdefault(key, {})
    bucket.setdefault(valid, record)
    if True in bucket and False in bucket:
        return bucket[True], bucket[False]
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p-min", type=int, default=4)
    parser.add_argument("--p-max", type=int, default=5)
    parser.add_argument("--max-width", type=int, default=35)
    parser.add_argument("--max-gap", type=int, default=35)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    tables: dict[str, dict[tuple[object, ...], dict[bool, dict[str, object]]]] = {
        "global": {},
        "indexed_off": {},
        "indexed_full": {},
    }
    twins: dict[str, dict[str, object]] = {}
    sidon_rulers = 0
    candidates = 0

    for p in range(args.p_min, args.p_max + 1):
        for width in range(p - 1, args.max_width + 1):
            max_subcritical_gap = min(args.max_gap, 3 * p * p - 1 - 2 * width)
            if max_subcritical_gap < 1:
                continue
            for interior in itertools.combinations(range(1, width), p - 2):
                z = (0, *interior, width)
                if not is_sidon(z):
                    continue
                sidon_rulers += 1
                for gap in range(1, max_subcritical_gap + 1):
                    candidates += 1
                    record = make_record(z, gap)
                    global_profile, indexed_off, indexed_full = residue_signatures(z, gap)
                    profiles = {
                        "global": global_profile,
                        "indexed_off": indexed_off,
                        "indexed_full": indexed_full,
                    }
                    for name, profile in profiles.items():
                        if name in twins:
                            continue
                        # Equal p and span make the pair live under the same target bound.
                        key = (p, record["span"], profile)
                        twin = update_twin_table(tables[name], key, record)
                        if twin is not None:
                            valid_record, invalid_record = twin
                            twins[name] = {
                                "valid": valid_record,
                                "invalid": invalid_record,
                                "profile": profile,
                            }
                    if len(twins) == len(tables):
                        break
                if len(twins) == len(tables):
                    break
            if len(twins) == len(tables):
                break
        if len(twins) == len(tables):
            break

    for name, twin in twins.items():
        valid_record = twin["valid"]
        invalid_record = twin["invalid"]
        if name.startswith("indexed"):
            include_diagonal = name == "indexed_full"
            for degree in range(1, 4):
                valid_moments = quotient_moments(
                    tuple(valid_record["z"]),
                    int(valid_record["gap"]),
                    degree,
                    include_diagonal,
                )
                invalid_moments = quotient_moments(
                    tuple(invalid_record["z"]),
                    int(invalid_record["gap"]),
                    degree,
                    include_diagonal,
                )
                twin[f"quotient_moments_through_{degree}_equal"] = (
                    valid_moments == invalid_moments
                )

    result = {
        "parameters": {
            "p_min": args.p_min,
            "p_max": args.p_max,
            "max_width": args.max_width,
            "max_gap": args.max_gap,
            "strict_subcritical": "gap + 2*width < 3*p^2",
            "moduli": "p..p^2",
        },
        "sidon_rulers": sidon_rulers,
        "candidates": candidates,
        "twins": twins,
        "missing": sorted(set(tables).difference(twins)),
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
