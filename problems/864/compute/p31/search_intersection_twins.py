#!/usr/bin/env python3
"""Search twins preserving indexed relative support intersections."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from search_indexed_twins import is_sidon, labels, make_record, update_twin_table


def intersection_signatures(
    z: tuple[int, ...], gap: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    p = len(z)
    differences, stars = labels(z, gap)
    off_profile: list[int] = []
    full_profile: list[int] = []
    for modulus in range(p, p * p + 1):
        d_support = {value % modulus for value in differences}
        for star in stars:
            off_support = {value % modulus for value in star[1:]}
            full_support = off_support | {star[0] % modulus}
            off_profile.append(len(d_support & off_support))
            full_profile.append(len(d_support & full_support))
    return tuple(off_profile), tuple(full_profile)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p-min", type=int, default=4)
    parser.add_argument("--p-max", type=int, default=5)
    parser.add_argument("--max-width", type=int, default=35)
    parser.add_argument("--max-gap", type=int, default=35)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    tables: dict[str, dict] = {"intersection_off": {}, "intersection_full": {}}
    twins: dict[str, dict] = {}
    sidon_rulers = 0
    candidates = 0

    for p in range(args.p_min, args.p_max + 1):
        for width in range(p - 1, args.max_width + 1):
            max_gap = min(args.max_gap, 3 * p * p - 1 - 2 * width)
            if max_gap < 1:
                continue
            for interior in itertools.combinations(range(1, width), p - 2):
                z = (0, *interior, width)
                if not is_sidon(z):
                    continue
                sidon_rulers += 1
                for gap in range(1, max_gap + 1):
                    candidates += 1
                    record = make_record(z, gap)
                    off_profile, full_profile = intersection_signatures(z, gap)
                    for name, profile in (
                        ("intersection_off", off_profile),
                        ("intersection_full", full_profile),
                    ):
                        if name in twins:
                            continue
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
