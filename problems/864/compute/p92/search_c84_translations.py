#!/usr/bin/env python3
"""Scan every P86 archived-ruler translation for P84 C84 and P92 SDRs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
P86_PATH = ROOT / "problems/864/compute/p86/dense_loose_search.py"
P92_PATH = ROOT / "problems/864/compute/p92/audit_constituent_matching.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def certificate(base, gamma: int, b: int, row: dict[str, object]) -> dict[str, object]:
    B = tuple(value + gamma for value in base.values)
    p = len(B)
    h = B[-1] + 1
    sums = {
        x + y
        for i, x in enumerate(B)
        for y in B[i:]
    }
    differences = {
        y - x
        for i, x in enumerate(B)
        for y in B[i + 1 :]
    }
    assert len(sums) == p * (p + 1) // 2
    assert len(differences) == p * (p - 1) // 2
    assert differences.isdisjoint(total + b for total in sums)
    delta_numerator = 3 * p * p - p + 2 - 2 * h
    assert delta_numerator > 0 and delta_numerator % 2 == 0
    return {
        "source": list(base.sources),
        "gamma": gamma,
        "b": b,
        "delta": delta_numerator // 2,
        "B": B,
        **row,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    p86 = load_module("p86_for_p92", P86_PATH)
    p92 = load_module("p92_matching", P92_PATH)
    bases, _manifests = p86.load_archives()

    tested = folded = admissible = nonzero = 0
    c84_failures = 0
    constituent_failures = 0
    hexagon_failures = 0
    first_c84 = first_constituent = first_hexagon = None
    max_difference = None
    max_ratio = None

    for base in bases:
        z = base.values
        p, width = len(z), z[-1]
        baseline = (3 * p * p - p + 2) // 2
        max_gamma = min(width - 1, baseline - width - 2)
        if max_gamma < 0:
            continue
        sum_mask, difference_mask = p86.masks_for_ruler(z)
        sum_pairs = p86.unordered_sum_map(z)
        for gamma in range(max_gamma + 1):
            tested += 2
            h = width + gamma + 1
            c_s = (sum_mask & (sum_mask >> h)).bit_count()
            if not c_s:
                continue
            folded += 2
            admissible_bs = [
                b
                for b in (1, 2)
                if ((sum_mask << (2 * gamma + b)) & difference_mask) == 0
            ]
            if not admissible_bs:
                continue

            B = tuple(value + gamma for value in z)
            fold_list = [
                (
                    sum_pairs[low][0] + gamma,
                    sum_pairs[low][1] + gamma,
                    sum_pairs[low + h][0] + gamma,
                    sum_pairs[low + h][1] + gamma,
                )
                for low in sum_pairs
                if low + h in sum_pairs
            ]
            assert len(fold_list) == c_s
            triangle_ids = p92.loose_triangle_ids(fold_list)
            triangles = len(triangle_ids)
            folds = len(fold_list)
            constituent_adjacency = [tuple(ids) for ids in triangle_ids]
            constituent_matching, constituent_assignment = (
                p92.maximum_constituent_matching(
                    constituent_adjacency, folds
                )
            )
            hexagon_adjacency = p92.hexagon_adjacency(
                fold_list, triangle_ids
            )
            hexagon_matching, hexagon_assignment = (
                p92.maximum_constituent_matching(
                    hexagon_adjacency, folds
                )
            )
            row: dict[str, object] = {
                "p": p,
                "h": h,
                "C_S": folds,
                "T_F": triangles,
                "constituent_matching": constituent_matching,
                "hexagon_matching": hexagon_matching,
            }
            if constituent_matching != triangles:
                left, right = p92.hall_witness(
                    constituent_adjacency, constituent_assignment
                )
                assert len(right) < len(left)
                row["constituent_hall_triangles"] = left
                row["constituent_hall_folds"] = right
            if hexagon_matching != triangles:
                left, right = p92.hall_witness(
                    hexagon_adjacency, hexagon_assignment
                )
                assert len(right) < len(left)
                row["hexagon_hall_triangles"] = left
                row["hexagon_hall_folds"] = right
            admissible += len(admissible_bs)
            nonzero += len(admissible_bs) * (triangles > 0)
            difference = triangles - folds
            if max_difference is None or difference > max_difference[0]:
                max_difference = (difference, B, h, admissible_bs[0], row)
            if (
                max_ratio is None
                or triangles * max_ratio[1] > max_ratio[0] * folds
            ):
                max_ratio = (
                    triangles, folds, B, h, admissible_bs[0], row
                )

            if triangles > folds:
                c84_failures += len(admissible_bs)
                if first_c84 is None:
                    first_c84 = certificate(
                        base, gamma, admissible_bs[0], row
                    )
            if int(row["constituent_matching"]) != triangles:
                constituent_failures += len(admissible_bs)
                if first_constituent is None:
                    first_constituent = certificate(
                        base, gamma, admissible_bs[0], row
                    )
            if int(row["hexagon_matching"]) != triangles:
                hexagon_failures += len(admissible_bs)
                if first_hexagon is None:
                    first_hexagon = certificate(
                        base, gamma, admissible_bs[0], row
                    )

    def compact(record):
        if record is None:
            return None
        value, B, h, b, row = record
        return {
            "value": value,
            "p": len(B),
            "h": h,
            "b": b,
            "C_S": row["C_S"],
            "T_F": row["T_F"],
            "B": B,
        }

    def compact_ratio(record):
        if record is None:
            return None
        numerator, denominator, B, h, b, row = record
        return {
            "numerator": numerator,
            "denominator": denominator,
            "p": len(B),
            "h": h,
            "b": b,
            "C_S": row["C_S"],
            "T_F": row["T_F"],
            "B": B,
        }

    result = {
        "domain": "all P86 archived-ruler positive-defect translations",
        "base_count": len(bases),
        "tested_b_candidates": tested,
        "folded_b_candidates": folded,
        "admissible_candidates": admissible,
        "nonzero_triangle_rows": nonzero,
        "T_F_gt_C_S_failures": c84_failures,
        "first_T_F_gt_C_S_failure": first_c84,
        "constituent_matching_failures": constituent_failures,
        "first_constituent_matching_failure": first_constituent,
        "hexagon_matching_failures": hexagon_failures,
        "first_hexagon_matching_failure": first_hexagon,
        "max_T_F_minus_C_S": compact(max_difference),
        "max_T_F_over_C_S": compact_ratio(max_ratio),
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
