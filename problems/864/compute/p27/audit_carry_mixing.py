"""Exact and spectral audit for the P27 Singer carry-mixing lane.

The script reads stored P12 Singer scan records without importing their code.
For each stored reflected candidate it verifies the E_d criterion and its
equivalent ordered four-point count.  It also reports the Fourier spectrum of
the cut-oriented positive-difference selector.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import numpy as np


def positive_differences(values: list[int]) -> set[int]:
    return {
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    }


def unordered_pairs(values: list[int]) -> Iterable[tuple[int, int]]:
    for i, alpha in enumerate(values):
        for beta in values[i:]:
            yield alpha, beta


def singer_records(paths: list[Path]) -> Iterable[tuple[Path, dict[str, object]]]:
    for path in paths:
        with path.open("r", encoding="ascii") as handle:
            for line in handle:
                record = json.loads(line)
                if record.get("family") == "singer":
                    yield path, record


def candidate_from(record: dict[str, object]) -> dict[str, object] | None:
    for key in ("best_candidate", "best_below_3p2"):
        candidate = record.get(key)
        if isinstance(candidate, dict) and "points" in candidate:
            return candidate
    return None


def oriented_spectrum(delta: set[int], modulus: int) -> dict[str, object]:
    indicator = np.zeros(modulus, dtype=np.float64)
    indicator[list(delta)] = 1.0
    transform = np.fft.fft(indicator)

    # Averaging a fixed cyclic difference over all cut origins gives this ramp.
    ramp = np.zeros(modulus, dtype=np.float64)
    ramp[1:] = 1.0 - np.arange(1, modulus, dtype=np.float64) / modulus
    ramp_transform = np.fft.fft(ramp)
    residual = transform - ramp_transform

    nonzero = transform[1:]
    residual_nonzero = residual[1:]
    max_index = int(np.argmax(np.abs(nonzero))) + 1
    residual_index = int(np.argmax(np.abs(residual_nonzero))) + 1
    real_error = float(np.max(np.abs(nonzero.real + 0.5)))
    return {
        "delta_fourier_max": float(abs(transform[max_index])),
        "delta_fourier_max_frequency": max_index,
        "delta_fourier_frequency_1": float(abs(transform[1])),
        "ramp_fourier_frequency_1": float(abs(ramp_transform[1])),
        "ramp_residual_max": float(abs(residual[residual_index])),
        "ramp_residual_max_frequency": residual_index,
        "nonzero_real_part_error_from_minus_half": real_error,
    }


def audit_candidate(
    path: Path,
    record: dict[str, object],
    candidate: dict[str, object],
    spectrum: bool,
) -> dict[str, object]:
    q = int(record["parameter"])
    modulus = int(record["modulus"])
    points = sorted(int(x) for x in candidate["points"])
    center = int(candidate.get("candidate_center", candidate.get("center")))
    span = points[-1]
    reflected = sorted(span - x for x in points)
    delta = positive_differences(points)
    d = modulus + 2 * span - center
    g = modulus - d

    if modulus != q * q + q + 1 or len(points) != q + 1:
        raise AssertionError("record is not a Singer (v,q+1,1) candidate")
    if not 0 < d < modulus or not center > 2 * span:
        raise AssertionError("candidate is outside the P27 range")
    if len(delta) != (modulus - 1) // 2:
        raise AssertionError("positive differences do not have Singer size")
    if delta & {modulus - x for x in delta}:
        raise AssertionError("positive difference orientations overlap")
    if delta | {modulus - x for x in delta} != set(range(1, modulus)):
        raise AssertionError("positive difference orientations do not partition")

    e_values: set[int] = set()
    witnesses: list[tuple[int, int, int]] = []
    ordered_count = 0
    diagonal_count = 0
    reflected_set = set(reflected)
    for alpha, beta in unordered_pairs(reflected):
        if alpha + beta >= d:
            continue
        e = d - alpha - beta
        e_values.add(e)
        if e not in delta:
            witnesses.append((alpha, beta, e))

    for w in reflected:
        for alpha in reflected:
            for beta in reflected:
                z = g + w + alpha + beta
                if z in reflected_set:
                    ordered_count += 1
                    if alpha == beta:
                        diagonal_count += 1

    unordered_four_count = (ordered_count + diagonal_count) // 2
    if 2 * unordered_four_count != ordered_count + diagonal_count:
        raise AssertionError("unordered correction is not integral")
    if len(witnesses) != unordered_four_count:
        raise AssertionError("E_d and four-point counts disagree")
    if witnesses:
        raise AssertionError("stored reflected center is not an E_d failure")

    density = Fraction(len(points), modulus)
    ambient_ordered = math.comb(d + 2, 3)
    ordered_uniform_main = density**4 * ambient_ordered
    unordered_uniform_main = ordered_uniform_main / 2
    output: dict[str, object] = {
        "source": path.name,
        "q": q,
        "v": modulus,
        "p": len(points),
        "L": span,
        "M": center,
        "d": d,
        "d_over_v": str(Fraction(d, modulus)),
        "g": g,
        "E_d_size": len(e_values),
        "witness_count": len(witnesses),
        "ordered_four_count": ordered_count,
        "diagonal_four_count": diagonal_count,
        "unordered_four_count": unordered_four_count,
        "ordered_uniform_main": str(ordered_uniform_main),
        "unordered_uniform_main": str(unordered_uniform_main),
        "unordered_uniform_main_float": float(unordered_uniform_main),
    }
    if spectrum:
        output.update(oriented_spectrum(delta, modulus))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--spectrum",
        action="store_true",
        help="compute numpy FFT diagnostics for each distinct candidate",
    )
    args = parser.parse_args()

    audited: list[dict[str, object]] = []
    seen: set[tuple[int, int, tuple[int, ...]]] = set()
    for path, record in singer_records(args.inputs):
        candidate = candidate_from(record)
        if candidate is None:
            continue
        points = tuple(int(x) for x in candidate["points"])
        center = int(candidate.get("candidate_center", candidate.get("center")))
        key = (int(record["modulus"]), center, points)
        if key in seen:
            continue
        seen.add(key)
        result = audit_candidate(path, record, candidate, args.spectrum)
        audited.append(result)
        print(json.dumps(result, sort_keys=True))

    if not audited:
        raise AssertionError("no Singer candidates found")
    summary = {
        "audited": len(audited),
        "all_exact_identities_pass": all(
            row["witness_count"] == row["unordered_four_count"] == 0
            for row in audited
        ),
        "largest_q": max(int(row["q"]) for row in audited),
        "largest_d_over_v": str(
            max(Fraction(str(row["d_over_v"])) for row in audited)
        ),
        "smallest_d_over_v": str(
            min(Fraction(str(row["d_over_v"])) for row in audited)
        ),
        "largest_missing_uniform_main": max(
            float(row["unordered_uniform_main_float"]) for row in audited
        ),
    }
    print(json.dumps({"summary": summary}, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({"records": audited, "summary": summary}, indent=2, sort_keys=True)
            + "\n",
            encoding="ascii",
        )


if __name__ == "__main__":
    main()
