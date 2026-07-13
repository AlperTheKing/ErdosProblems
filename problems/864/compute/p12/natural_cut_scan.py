"""Exact scan of cyclic cuts for the natural (multiplier one) family lift."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from algebraic_scan import (
    analyze_lift,
    bose_chowla,
    cyclic_lifts,
    positive_differences,
    reflected_admissibility,
    ruzsa,
    singer,
    unordered_sums,
)


def first_hole_in_window(points: tuple[int, ...], lo: int, hi: int) -> int | None:
    sums_bits = 0
    for value in unordered_sums(points):
        sums_bits |= 1 << value
    forbidden = 0
    for difference in positive_differences(points):
        forbidden |= sums_bits << difference
    for value in range(lo, hi + 1):
        if not ((forbidden >> value) & 1):
            return value
    return None


def scan(family: str, parameter: int) -> dict[str, object]:
    generators = {"bose": bose_chowla, "singer": singer, "ruzsa": ruzsa}
    modulus, residues, metadata = generators[family](parameter)
    best_any = None
    best_two_v = None
    successful_cuts = 0
    successful_two_v_cuts = 0
    for points, base, gap in cyclic_lifts(residues, modulus):
        rec = analyze_lift(points)
        center = rec["candidate_center"]
        if center is not None:
            successful_cuts += 1
            item = (int(center), int(rec["span"]), base, gap, points)
            if best_any is None or item < best_any:
                best_any = item
        center_two_v = first_hole_in_window(points, 2 * modulus, 5 * modulus // 2)
        if center_two_v is not None:
            successful_two_v_cuts += 1
            item = (center_two_v, points[-1], base, gap, points)
            if best_two_v is None or item < best_two_v:
                best_two_v = item

    def encode(item: tuple[int, int, int, int, tuple[int, ...]] | None):
        if item is None:
            return None
        center, span, base, gap, points = item
        check = reflected_admissibility(points, center)
        if not check["admissible"]:
            raise AssertionError("literal reflected verification failed")
        return {
            "center": center,
            "span": span,
            "cut_base": base,
            "cut_gap": gap,
            "points": points,
            "center_over_p2": str(Fraction(center, len(points) ** 2)),
            "hole_offset_above_2span": center - 2 * span,
        }

    return {
        "family": family,
        "parameter": parameter,
        "modulus": modulus,
        "size": len(residues),
        "metadata": metadata,
        "cuts": len(residues),
        "successful_cuts_below_3p2": successful_cuts,
        "successful_cuts_in_2v_to_5v_over_2": successful_two_v_cuts,
        "best_below_3p2": encode(best_any),
        "best_in_2v_to_5v_over_2": encode(best_two_v),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=("bose", "singer", "ruzsa"), required=True)
    parser.add_argument("--parameters", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [scan(args.family, x) for x in args.parameters]
    args.output.write_text(
        "\n".join(json.dumps(x, sort_keys=True) for x in records) + "\n",
        encoding="ascii",
    )
    for record in records:
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
