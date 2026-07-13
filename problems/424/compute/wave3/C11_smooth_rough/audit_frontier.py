#!/usr/bin/env python3
"""Exact finite audits for the Erdos 424 C11 smooth/rough frontier.

The script reuses the audited C03 bitmap builder, but all temporary artifacts
live under this C11 directory.  Reported mathematical quantities are integers
or reduced Fractions.  Floating point is used only by C03 to instantiate the
prescribed (L,y,z) parameter recipe.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
C03_PATH = HERE.parent / "C03_smooth_rough.py"
sys.dont_write_bytecode = True
EXACT_PARAMETER_TRIPLES = {
    1_000_000: (5, 41, 9),
    10_000_000: (5, 55, 11),
    33_333_333: (5, 64, 11),
}


def load_c03():
    spec = importlib.util.spec_from_file_location("c11_c03", C03_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {C03_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


C03 = load_c03()


def fraction_record(value: Fraction) -> dict[str, int | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "text": str(value),
    }


def smooth_values(limit: int, z: int) -> list[int]:
    values = [1]
    for prime in C03.primes_up_to(z):
        old_values = tuple(values)
        additions: list[int] = []
        power = prime
        while power <= limit:
            for base in old_values:
                value = base * power
                if value <= limit:
                    additions.append(value)
            if power > limit // prime:
                break
            power *= prime
        values.extend(additions)
    values.sort()
    if len(values) != len(set(values)):
        raise AssertionError("smooth-number generator produced duplicates")
    return values


def sifted_prefixes(
    membership: np.memmap, limit: int, z: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    coprime = np.ones(limit + 1, dtype=np.bool_)
    coprime[0] = False
    for prime in C03.primes_up_to(z):
        coprime[prime::prime] = False
    t_values = membership[: 3 * limit + 1 : 3].astype(np.bool_)
    if t_values.size != limit + 1:
        raise AssertionError("T slice has the wrong length")
    sifted_t = np.logical_and(coprime, t_values)
    sifted_miss = np.logical_and(coprime, np.logical_not(t_values))
    return (
        coprime,
        np.cumsum(coprime, dtype=np.int64),
        np.cumsum(sifted_t, dtype=np.int64),
        np.cumsum(sifted_miss, dtype=np.int64),
    )


def arithmetic_factor_pairs(value: int) -> list[tuple[int, int]]:
    return [
        (divisor, value // divisor)
        for divisor in range(2, math.isqrt(value) + 1)
        if value % divisor == 0 and divisor < value // divisor
    ]


def low_falsifiers(membership: np.memmap) -> dict[str, object]:
    # 23 is in T through the non-seed pair 5*14, although its seed-2
    # pullback 35 is absent from G.
    r_reverse = 23
    h_reverse = (3 * r_reverse + 1) // 2
    reverse_pairs = arithmetic_factor_pairs(3 * r_reverse + 1)
    reverse_witnesses = [
        pair for pair in reverse_pairs if membership[pair[0]] and membership[pair[1]]
    ]
    if not membership[3 * r_reverse] or membership[h_reverse]:
        raise AssertionError("seed-2 reverse falsifier changed")
    if reverse_witnesses != [(5, 14)]:
        raise AssertionError("unexpected witness list for r=23")

    # 19 is a rough T-miss whose shifted value has only one arithmetic
    # factor pair, so no pointwise many-witness lower bound is available.
    r_one_pair = 19
    one_pairs = arithmetic_factor_pairs(3 * r_one_pair + 1)
    if membership[3 * r_one_pair] or one_pairs != [(2, 29)]:
        raise AssertionError("one-pair rough-miss falsifier changed")
    if not membership[2] or membership[29]:
        raise AssertionError("unexpected G membership in 58=2*29")

    # 17 is in T but has exactly one admissible G_2 witness pair.
    r_one_witness = 17
    witness_pairs = [
        pair
        for pair in arithmetic_factor_pairs(3 * r_one_witness + 1)
        if membership[pair[0]] and membership[pair[1]]
    ]
    if witness_pairs != [(2, 26)]:
        raise AssertionError("single closure-witness falsifier changed")

    return {
        "seed2_reverse_falsifier": {
            "r": r_reverse,
            "T(r)": bool(membership[3 * r_reverse]),
            "h=(3r+1)/2": h_reverse,
            "G(h)": bool(membership[h_reverse]),
            "all_factor_pairs_of_3r+1": reverse_pairs,
            "G2_witness_pairs": reverse_witnesses,
        },
        "one_arithmetic_pair_rough_miss": {
            "r": r_one_pair,
            "T(r)": bool(membership[3 * r_one_pair]),
            "3r+1": 3 * r_one_pair + 1,
            "factor_pairs": one_pairs,
            "G(2)": bool(membership[2]),
            "G(29)": bool(membership[29]),
        },
        "one_G2_witness_T_member": {
            "r": r_one_witness,
            "T(r)": bool(membership[3 * r_one_witness]),
            "3r+1": 3 * r_one_witness + 1,
            "G2_witness_pairs": witness_pairs,
        },
    }


def analyze_x(membership: np.memmap, x: int) -> dict[str, object]:
    if x not in EXACT_PARAMETER_TRIPLES:
        raise ValueError(f"no audited exact (L,y,z) triple recorded for X={x}")
    ell, y, z = EXACT_PARAMETER_TRIPLES[x]
    smooth = smooth_values(x, z)
    smooth_to_y = [value for value in smooth if value <= y]
    smooth_window = [value for value in smooth_to_y if value >= ell]

    coprime, coprime_prefix, sifted_t_prefix, sifted_miss_prefix = sifted_prefixes(
        membership, x, z
    )

    def phi(bound: int) -> int:
        return int(coprime_prefix[bound])

    def sifted_t(bound: int) -> int:
        return int(sifted_t_prefix[bound])

    def sifted_miss(bound: int) -> int:
        return int(sifted_miss_prefix[bound])

    partition_total = sum(phi(x // value) for value in smooth)
    if partition_total != x:
        raise AssertionError("canonical smooth/rough partition does not sum to X")

    high = sum(phi(x // value) for value in smooth if value > y)
    smooth_miss = sum(
        phi(x // value) for value in smooth_to_y if not membership[3 * value]
    )
    rough_miss = sum(
        sifted_miss(x // value)
        for value in smooth_to_y
        if membership[3 * value]
    )
    full_good = x - high - smooth_miss - rough_miss - 1
    full_good_direct = (
        sum(
            sifted_t(x // value)
            for value in smooth_to_y
            if membership[3 * value]
        )
        - 1
    )
    if full_good != full_good_direct:
        raise AssertionError("full certificate partition mismatch")

    # Window version: both canonical factors are required to be unbounded,
    # so r=1 is part of the ambient exception.
    window_supply = sum(phi(x // value) - 1 for value in smooth_window)
    ambient_window_exception = x - window_supply
    window_smooth_miss = sum(
        phi(x // value) - 1
        for value in smooth_window
        if not membership[3 * value]
    )
    window_rough_miss = sum(
        sifted_miss(x // value)
        for value in smooth_window
        if membership[3 * value]
    )
    window_good = (
        x - ambient_window_exception - window_smooth_miss - window_rough_miss
    )
    window_good_direct = sum(
        sifted_t(x // value) - 1
        for value in smooth_window
        if membership[3 * value]
    )
    if window_good != window_good_direct:
        raise AssertionError("window certificate partition mismatch")

    smooth_miss_values = [
        value for value in smooth_to_y if not membership[3 * value]
    ]
    harmonic = sum((Fraction(1, value) for value in smooth_to_y), Fraction())
    missing_weight = sum(
        (Fraction(1, value) for value in smooth_miss_values), Fraction()
    )

    # Closure gives t in T => 4t-1 in T.  The following child mass is the
    # part on which its contrapositive can recurse without leaving z-smooths.
    affine_children = [
        value
        for value in smooth_miss_values
        if value % 4 == 3
        and C03.is_z_smooth((value + 1) // 4, z)
        and not membership[3 * ((value + 1) // 4)]
    ]
    affine_child_weight = sum(
        (Fraction(1, value) for value in affine_children), Fraction()
    )

    rough = coprime.copy()
    rough[: z + 1] = False
    t_values = membership[: 3 * x + 1 : 3].astype(np.bool_)
    rough_miss_mask = np.logical_and(rough, np.logical_not(t_values))

    indices = np.arange(x + 1, dtype=np.int64)
    pullbacks = (3 * indices + 1) // 2
    pullback_in_g = membership[pullbacks].astype(np.bool_)
    seed2_unresolved = np.logical_and(rough, np.logical_not(pullback_in_g))

    def rough_candidate_record(bound: int) -> dict[str, int]:
        prefix = slice(0, bound + 1)
        rough_count = int(np.count_nonzero(rough[prefix]))
        rough_miss_count = int(np.count_nonzero(rough_miss_mask[prefix]))
        implication_violations = int(
            np.count_nonzero(
                np.logical_and(rough_miss_mask[prefix], pullback_in_g[prefix])
            )
        )
        seed2_unresolved_count = int(np.count_nonzero(seed2_unresolved[prefix]))
        seed2_reverse_failures = int(
            np.count_nonzero(
                np.logical_and(
                    np.logical_and(rough[prefix], t_values[prefix]),
                    seed2_unresolved[prefix],
                )
            )
        )
        if implication_violations != 0:
            raise AssertionError("true seed-2 closure implication failed")
        if seed2_unresolved_count != rough_miss_count + seed2_reverse_failures:
            raise AssertionError("seed-2 partition mismatch")

        # A rough child 4t-1 that is missing has a missing parent t.
        # Restricting to rough parents gives a genuine self-recursion test.
        child_indices = np.flatnonzero(
            np.logical_and(
                rough_miss_mask[prefix], indices[prefix] % 4 == 3
            )
        )
        parents = (child_indices + 1) // 4
        rough_parents = rough[parents]
        rough_parent_children = child_indices[rough_parents]
        if np.any(t_values[parents[rough_parents]]):
            raise AssertionError("4t-1 contrapositive failed on rough parents")
        rough_parent_child_count = int(rough_parent_children.size)
        return {
            "R": bound,
            "rough_count": rough_count,
            "T_miss_count": rough_miss_count,
            "seed2_unresolved_count": seed2_unresolved_count,
            "seed2_reverse_failure_count": seed2_reverse_failures,
            "true_seed2_implication_violations": implication_violations,
            "rough_missing_4t_minus_1_children_with_rough_parent": (
                rough_parent_child_count
            ),
            "M_minus_3_recursive_children": (
                rough_miss_count - 3 * rough_parent_child_count
            ),
            "M_minus_4_recursive_children": (
                rough_miss_count - 4 * rough_parent_child_count
            ),
        }

    rough_candidate_prefixes = {
        "C03_window_right_floor_X_over_L": rough_candidate_record(x // ell),
        "full_X": rough_candidate_record(x),
    }

    del indices, pullbacks, pullback_in_g, t_values, coprime, rough

    return {
        "X": x,
        "integer_parameters": {"L": ell, "y": y, "z": z},
        "certificate_21_full": {
            "E_high_smooth_part": high,
            "E_smooth_membership": smooth_miss,
            "E_rough_membership": rough_miss,
            "singleton_n=1": 1,
            "certified_T2_count": full_good,
            "partition_check": high + smooth_miss + rough_miss + 1 + full_good,
        },
        "window_certificate_for_C03_cutoffs": {
            "E_ambient_s_outside_[L,y]_or_r=1": ambient_window_exception,
            "E_smooth_membership": window_smooth_miss,
            "E_rough_membership": window_rough_miss,
            "certified_T2_count": window_good,
            "partition_check": (
                ambient_window_exception
                + window_smooth_miss
                + window_rough_miss
                + window_good
            ),
        },
        "gate31": {
            "H_z(y)": fraction_record(harmonic),
            "W_missing": fraction_record(missing_weight),
            "affine_4t_minus_1_recursive_children": affine_children,
            "affine_child_weight": fraction_record(affine_child_weight),
            "W_minus_3_child_weight": fraction_record(
                missing_weight - 3 * affine_child_weight
            ),
            "W_minus_4_child_weight": fraction_record(
                missing_weight - 4 * affine_child_weight
            ),
        },
        "rough_candidate_prefixes": rough_candidate_prefixes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100_000_000)
    parser.add_argument(
        "--x-values",
        type=int,
        nargs="+",
        default=[1_000_000, 10_000_000, 33_333_333],
    )
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    x_values = sorted(set(args.x_values))
    unknown = [x for x in x_values if x not in EXACT_PARAMETER_TRIPLES]
    if unknown:
        raise ValueError(f"no exact parameter triples for X values: {unknown}")
    required_limit = 3 * max(x_values)
    if args.limit < required_limit:
        raise ValueError(f"--limit must be at least {required_limit}")

    with C03.flat_temporary_root(HERE) as temp_dir:
        executable, compile_record = C03.compile_helper(temp_dir, args.compiler)
        bitmap_path = temp_dir / f"{C03.TEMP_PREFIX}c11_g_membership.bin"
        helper_record, _ = C03.run_helper(
            executable, args.limit, bitmap_path, 0
        )
        membership = np.memmap(bitmap_path, dtype=np.uint8, mode="r")
        try:
            result = {
                "method": (
                    "exact C03 well-founded G bitmap; audited integer triples; "
                    "integer/Fraction C11 audits"
                ),
                "limit": args.limit,
                "helper": {
                    "limit": int(helper_record["limit"]),
                    "count": int(helper_record["count"]),
                },
                "compile": {
                    "compiler_version": compile_record["compiler_version"],
                    "helper_source_sha256": compile_record[
                        "helper_source_sha256"
                    ],
                },
                "low_falsifiers": low_falsifiers(membership),
                "rows": [analyze_x(membership, x) for x in x_values],
            }
        finally:
            mmap = getattr(membership, "_mmap", None)
            if mmap is not None:
                mmap.close()
            del membership

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        output = args.output.resolve()
        if output.parent != HERE:
            raise ValueError("--output must be directly inside the C11 directory")
        output.write_text(rendered, encoding="ascii", newline="\n")


if __name__ == "__main__":
    main()
