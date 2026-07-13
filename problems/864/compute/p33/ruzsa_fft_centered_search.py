#!/usr/bin/env python3
"""Locate exact Ruzsa reflection centers and audit centered C20.

The floating-point FFT only proposes centers. Every accepted center is
verified against the exact integer supports S(B) and Delta+(B).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import torch

P30_DIR = Path("problems/864/compute/p30")
sys.path.insert(0, str(P30_DIR))
from scan_canonical_cuts import (  # noqa: E402
    is_prime,
    primitive_root,
    ruzsa_residues,
)


def ceil_cuberoot_square(n: int) -> int:
    target = n * n
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid * mid >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def next_power_of_two(value: int) -> int:
    return 1 << (value - 1).bit_length()


def set_sha256(values: tuple[int, ...]) -> str:
    payload = json.dumps(values, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def build_supports(
    points: tuple[int, ...],
    device: torch.device,
    block_size: int,
) -> tuple[np.ndarray, np.ndarray, torch.Tensor, int]:
    span = points[-1]
    fft_length = next_power_of_two(3 * span + 1)
    point_tensor = torch.tensor(points, dtype=torch.int64, device=device)
    sum_indicator = torch.zeros(fft_length, dtype=torch.float32, device=device)
    difference_indicator = torch.zeros(
        fft_length, dtype=torch.float32, device=device
    )

    for start in range(0, len(points), block_size):
        block = point_tensor[start : start + block_size]
        sums = (block[:, None] + point_tensor[None, :]).reshape(-1)
        sum_indicator[sums] = 1.0
        differences = torch.abs(
            block[:, None] - point_tensor[None, :]
        ).reshape(-1)
        difference_indicator[differences] = 1.0
    difference_indicator[0] = 0.0

    sum_cpu = (
        sum_indicator[: 2 * span + 1].detach().cpu().numpy() > 0.5
    )
    difference_cpu = (
        difference_indicator[: span + 1].detach().cpu().numpy() > 0.5
    )

    sum_transform = torch.fft.rfft(sum_indicator)
    difference_transform = torch.fft.rfft(difference_indicator)
    convolution = torch.fft.irfft(
        sum_transform * difference_transform, n=fft_length
    )
    del sum_transform, difference_transform, sum_indicator, difference_indicator
    return sum_cpu, difference_cpu, convolution, fft_length


def exact_hole(
    center: int,
    sum_support: np.ndarray,
    differences: np.ndarray,
) -> bool:
    complements = center - differences
    in_range = (complements >= 0) & (complements < len(sum_support))
    return not bool(np.any(sum_support[complements[in_range]]))


def locate_hole(
    convolution: torch.Tensor,
    sum_support: np.ndarray,
    difference_support: np.ndarray,
    lo: int,
    hi: int,
    tolerance: float,
    candidate_limit: int,
) -> tuple[int, float, int]:
    segment = torch.abs(convolution[lo : hi + 1])
    candidate_offsets = torch.nonzero(
        segment <= tolerance, as_tuple=False
    ).flatten()
    if candidate_offsets.numel() > candidate_limit:
        values = segment[candidate_offsets]
        selected = torch.topk(
            values, k=candidate_limit, largest=False
        ).indices
        candidate_offsets = candidate_offsets[selected]
    candidates = sorted(
        int(value) + lo for value in candidate_offsets.detach().cpu().tolist()
    )
    differences = np.flatnonzero(difference_support)
    checked = 0
    for center in candidates:
        checked += 1
        if exact_hole(center, sum_support, differences):
            fft_value = float(convolution[center].detach().cpu())
            return center, fft_value, checked
    raise RuntimeError(
        f"no exact hole among {len(candidates)} FFT candidates; "
        f"increase --tolerance or --candidate-limit"
    )


def literal_admissibility(
    points: tuple[int, ...],
    center: int,
) -> dict[str, Any]:
    reflected = tuple(sorted(set(points) | {center - value for value in points}))
    counts = Counter(
        reflected[left] + reflected[right]
        for left in range(len(reflected))
        for right in range(left, len(reflected))
    )
    repeated = sorted((value, count) for value, count in counts.items() if count > 1)
    expected = [(center, len(points))]
    return {
        "checked": True,
        "admissible": repeated == expected,
        "repeated_sums": repeated,
        "expected_repeated_sums": expected,
    }


def centered_metrics(
    points: tuple[int, ...],
    center: int,
    sum_support: np.ndarray,
    difference_support: np.ndarray,
) -> dict[str, Any]:
    size = len(points)
    n = center + 1
    h = ceil_cuberoot_square(n)
    counts = np.zeros(h, dtype=np.int8)

    differences = np.flatnonzero(difference_support)
    short_differences = differences[differences < h]
    counts[short_differences] += 2

    sum_lo = max(0, center - h + 1)
    sum_hi = min(center, len(sum_support))
    short_sum_offsets = np.flatnonzero(sum_support[sum_lo:sum_hi]) + sum_lo
    cross_differences = center - short_sum_offsets
    counts[cross_differences] += 2

    point_set = set(points)
    for point in points:
        difference = center - 2 * point
        if 0 < difference < h:
            if 2 * point not in point_set and not sum_support[2 * point]:
                raise AssertionError("diagonal sum missing from sum support")
            counts[difference] -= 1

    if int(counts[1:].min(initial=0)) < 0 or int(counts[1:].max(initial=0)) > 2:
        raise AssertionError("D1 support classes overlap or have invalid multiplicity")

    weights = h - np.arange(h, dtype=np.int64)
    d_weight = int(weights[(counts == 2) & (np.arange(h) > 0)].sum())
    q_weight = int(weights[(counts == 0) & (np.arange(h) > 0)].sum())
    z = d_weight - q_weight
    weighted_pairs = int((weights[1:] * counts[1:].astype(np.int64)).sum())
    if h * h + 2 * z != h + 2 * weighted_pairs:
        raise AssertionError("centered identity failed")

    reflected = tuple(sorted(points + tuple(center - value for value in points)))
    if reflected[0] != 0 or reflected[-1] != center:
        raise AssertionError("reflection is not endpoint-normalized")
    m = h + sum(
        min(h, right - left) for left, right in zip(reflected, reflected[1:])
    )
    truncation = sum(
        max(0, right - left - h) for left, right in zip(reflected, reflected[1:])
    )
    ambient_holes = n + h - 1 - m
    if truncation != ambient_holes:
        raise AssertionError("gap identity failed")

    k = 2 * size
    c20_margin6 = (
        6 * m * (h * h + 2 * z)
        - 8 * n * h * h
        - 9 * h * h * h
        - 9 * n * (k - 1) * h
    )
    raw_over_four_thirds = 3 * m * (h * h + 2 * z) - 4 * n * h * h
    coefficient_denominator = 3 * h * (h * h + n * (k - 1))
    required = Fraction(raw_over_four_thirds, coefficient_denominator)
    lg33_margin = (
        8 * n * z
        - 12 * h * h * ambient_holes
        + 3 * h * h * h
        - 12 * h * h
        - 9 * n * (k - 1) * h
    )
    return {
        "N": n,
        "k": k,
        "H": h,
        "M": m,
        "D": d_weight,
        "Q": q_weight,
        "Z": z,
        "weighted_pair_overlap": weighted_pairs,
        "T": truncation,
        "required_coefficient": f"{required.numerator}/{required.denominator}",
        "required_coefficient_decimal": float(required),
        "required_coefficient_numerator": required.numerator,
        "required_coefficient_denominator": required.denominator,
        "c20_margin6": c20_margin6,
        "lg33_margin": lg33_margin,
        "c20_fails": c20_margin6 > 0,
    }


def search_cut(
    p: int,
    exponent: int,
    device: torch.device,
    block_size: int,
    tolerance: float,
    candidate_limit: int,
    literal_check_max: int,
) -> dict[str, Any]:
    generator = primitive_root(p)
    residues = ruzsa_residues(p, generator)
    discrete_log = {pow(generator, index, p): index for index in range(p - 1)}
    exponent %= p
    if exponent == 0:
        raise ValueError("cut exponent must be nonzero modulo p")
    base_index = discrete_log[exponent]
    base = residues[base_index]
    modulus = p * (p - 1)
    points = tuple(sorted((value - base) % modulus for value in residues))
    span = points[-1]
    size = len(points)

    sum_support, difference_support, convolution, fft_length = build_supports(
        points, device, block_size
    )
    expected_sum_support = size * (size + 1) // 2
    expected_difference_support = size * (size - 1) // 2
    actual_sum_support = int(sum_support.sum())
    actual_difference_support = int(difference_support.sum())
    if actual_sum_support != expected_sum_support:
        raise AssertionError(("Sidon sum support", actual_sum_support, expected_sum_support))
    if actual_difference_support != expected_difference_support:
        raise AssertionError(
            ("Sidon difference support", actual_difference_support, expected_difference_support)
        )

    lo = 2 * span + 1
    hi = 3 * size * size - 1
    center, fft_value, candidates_checked = locate_hole(
        convolution,
        sum_support,
        difference_support,
        lo,
        hi,
        tolerance,
        candidate_limit,
    )
    del convolution
    if not exact_hole(
        center, sum_support, np.flatnonzero(difference_support)
    ):
        raise AssertionError("reported center is not an exact hole")
    if center <= 2 * span:
        raise AssertionError("range separation failed")

    literal = (
        literal_admissibility(points, center)
        if size <= literal_check_max
        else {
            "checked": False,
            "admissible": True,
            "certificate": (
                "B is literal Sidon; center>2*span; exact center not in "
                "S(B)+Delta+(B), with diagonal sums included in S(B)"
            ),
        }
    )
    if not literal["admissible"]:
        raise AssertionError(literal)

    metrics = centered_metrics(points, center, sum_support, difference_support)
    result = {
        "p": p,
        "primitive_root": generator,
        "modulus": modulus,
        "cut_exponent": exponent,
        "base_index": base_index,
        "cut_base": base,
        "size": size,
        "span": span,
        "lower_sha256": set_sha256(points),
        "sum_support": actual_sum_support,
        "difference_support": actual_difference_support,
        "fft_length": fft_length,
        "fft_tolerance": tolerance,
        "fft_value_at_center": fft_value,
        "fft_candidates_checked": candidates_checked,
        "center": center,
        "center_over_size2": f"{center}/{size * size}",
        "exact_hole": True,
        "literal_admissibility": literal,
        "metrics": metrics,
    }
    torch.cuda.empty_cache()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--exponents", type=int, nargs="+", required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--tolerance", type=float, default=64.0)
    parser.add_argument("--candidate-limit", type=int, default=100000)
    parser.add_argument("--literal-check-max", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not is_prime(args.p):
        raise ValueError(f"{args.p} is not prime")
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")

    records = [
        search_cut(
            args.p,
            exponent,
            device,
            args.block_size,
            args.tolerance,
            args.candidate_limit,
            args.literal_check_max,
        )
        for exponent in args.exponents
    ]
    strongest = max(
        records,
        key=lambda row: Fraction(
            row["metrics"]["required_coefficient_numerator"],
            row["metrics"]["required_coefficient_denominator"],
        ),
    )
    result = {
        "arithmetic": "FFT candidate location; exact integer acceptance",
        "device": str(device),
        "record_count": len(records),
        "c20_failure_count": sum(row["metrics"]["c20_fails"] for row in records),
        "strongest": strongest,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}))


if __name__ == "__main__":
    main()
