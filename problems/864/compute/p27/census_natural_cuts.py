"""Census every cut and every d in the stored P12 natural Singer scans."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import numpy as np


def records(paths: list[Path]) -> Iterable[tuple[Path, dict[str, object]]]:
    for path in paths:
        with path.open("r", encoding="ascii") as handle:
            for line in handle:
                record = json.loads(line)
                if record.get("family") == "singer":
                    yield path, record


def cyclic_cuts(values: list[int], modulus: int) -> Iterable[tuple[int, list[int]]]:
    for base in values:
        yield base, sorted((value - base) % modulus for value in values)


def profiles(points: list[int], modulus: int) -> tuple[np.ndarray, np.ndarray]:
    span = points[-1]
    reflected = [span - value for value in reversed(points)]
    delta = {
        points[j] - points[i]
        for i in range(len(points))
        for j in range(i + 1, len(points))
    }
    if len(delta) != (modulus - 1) // 2:
        raise AssertionError("cut does not have the Singer orientation size")
    if delta | {modulus - value for value in delta} != set(range(1, modulus)):
        raise AssertionError("Singer orientation partition failed")

    sums = np.zeros(modulus, dtype=np.float64)
    for i, alpha in enumerate(reflected):
        for beta in reflected[i:]:
            total = alpha + beta
            if total < modulus:
                sums[total] = 1.0
    complement = np.zeros(modulus, dtype=np.float64)
    complement[1:] = 1.0
    complement[list(delta)] = 0.0
    return sums, complement


def exact_convolution(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    length = len(left) + len(right) - 1
    fft_length = 1 << (length - 1).bit_length()
    values = np.fft.irfft(
        np.fft.rfft(left, fft_length) * np.fft.rfft(right, fft_length),
        fft_length,
    )[:length]
    rounded = np.rint(values).astype(np.int64)
    if float(np.max(np.abs(values - rounded))) > 1e-5:
        raise AssertionError("FFT convolution did not round to integers")
    if int(np.min(rounded)) < 0:
        raise AssertionError("rounded convolution has a negative coefficient")
    return rounded


def audit_record(path: Path, record: dict[str, object]) -> dict[str, object]:
    q = int(record["parameter"])
    modulus = int(record["modulus"])
    residues = sorted(int(value) for value in record["residues"])
    if modulus != q * q + q + 1 or len(residues) != q + 1:
        raise AssertionError("record parameters are not Singer parameters")

    cut_rows: list[dict[str, object]] = []
    for base, points in cyclic_cuts(residues, modulus):
        sums, complement = profiles(points, modulus)
        counts = exact_convolution(sums, complement)
        failures = np.flatnonzero(counts[1:modulus] == 0) + 1
        if len(failures) == 0:
            raise AssertionError("every cut must have the endpoint failure")
        maximum = int(failures[-1])
        cut_rows.append(
            {
                "base": base,
                "span": points[-1],
                "max_failure_d": maximum,
                "max_failure_d_over_v": str(Fraction(maximum, modulus)),
                "failure_count": int(len(failures)),
            }
        )

    maximum = max(int(row["max_failure_d"]) for row in cut_rows)
    best = [row for row in cut_rows if int(row["max_failure_d"]) == maximum]
    thresholds = {
        name: sum(int(row["max_failure_d"]) * denominator >= numerator * modulus for row in cut_rows)
        for name, numerator, denominator in (
            ("one_quarter", 1, 4),
            ("three_tenths", 3, 10),
            ("one_third", 1, 3),
            ("two_fifths", 2, 5),
        )
    }
    return {
        "source": path.name,
        "q": q,
        "v": modulus,
        "cuts": len(cut_rows),
        "max_failure_d": maximum,
        "max_failure_d_over_v": str(Fraction(maximum, modulus)),
        "max_failure_cut_bases": [int(row["base"]) for row in best],
        "cuts_with_failure_at_or_above": thresholds,
        "min_cut_max_failure_d": min(int(row["max_failure_d"]) for row in cut_rows),
        "min_cut_max_failure_d_over_v": str(
            Fraction(min(int(row["max_failure_d"]) for row in cut_rows), modulus)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    audited = [audit_record(path, record) for path, record in records(args.inputs)]
    if not audited:
        raise AssertionError("no Singer records found")
    for row in audited:
        print(json.dumps(row, sort_keys=True))
    summary = {
        "records": len(audited),
        "cuts": sum(int(row["cuts"]) for row in audited),
        "largest_q": max(int(row["q"]) for row in audited),
        "largest_max_failure_ratio": str(
            max(Fraction(str(row["max_failure_d_over_v"])) for row in audited)
        ),
        "largest_q_max_failure_ratio": next(
            str(row["max_failure_d_over_v"])
            for row in audited
            if int(row["q"]) == max(int(item["q"]) for item in audited)
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
