#!/usr/bin/env python3
"""Exact dyadic coefficient audit for the C54 recurrence bypass.

The script treats the accepted C16 C++ census as a read-only arithmetic
engine.  It compiles that source into a temporary directory, recomputes the
least grounded set at every requested dyadic endpoint, and emits only JSON to
stdout.  All reported ratios are formed from exact integer counts.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def frac_payload(value: Fraction) -> dict[str, int | float]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def compile_engine(source: Path, output: Path) -> None:
    command = [
        "g++",
        "-O3",
        "-std=c++20",
        "-Wall",
        "-Wextra",
        "-pedantic",
        str(source),
        "-o",
        str(output),
    ]
    subprocess.run(command, check=True)


def census(engine: Path, limit: int, directory: Path) -> dict:
    output = directory / f"endpoint_{limit}.json"
    subprocess.run(
        [str(engine), str(limit), str(output)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    data = json.loads(output.read_text(encoding="ascii"))
    row = data["checkpoints"][-1]
    if row["X"] != limit:
        raise AssertionError((limit, row["X"]))
    row = dict(row)
    row["Q"] = row["Mhalf"] - row["odd_seed2"]
    return row


def shell_rows(endpoints: dict[int, dict], min_power: int, max_power: int) -> list[dict]:
    rows = []
    for power in range(min_power, max_power + 1):
        current = endpoints[power]
        previous = endpoints[power - 1]
        previous_previous = endpoints[power - 2]

        delta_m = current["M"] - previous["M"]
        delta_e = current["E"] - previous["E"]
        delta_r = current["R"] - previous["R"]
        delta_s = current["even_seed3"] - previous["even_seed3"]
        delta_h = current["hard"] - previous["hard"]
        delta_q = current["Q"] - previous["Q"]
        delta_m_parent = previous["M"] - previous_previous["M"]
        defect = delta_s + delta_h - delta_q

        if delta_m != delta_e + delta_r:
            raise AssertionError((power, "M=E+R"))
        if delta_r != delta_m_parent + defect:
            raise AssertionError(
                (power, delta_r, delta_m_parent, delta_s, delta_h, delta_q)
            )

        theta = Fraction(delta_r, delta_m_parent)
        rows.append({
            "power": power,
            "X": 1 << power,
            "delta_M": delta_m,
            "delta_E": delta_e,
            "delta_R": delta_r,
            "delta_M_parent": delta_m_parent,
            "delta_S": delta_s,
            "delta_H": delta_h,
            "delta_Q": delta_q,
            "net_shell_defect": defect,
            "theta": frac_payload(theta),
            "normalized_contraction": frac_payload(theta / 2),
            "theta_lt_2": theta < 2,
            "theta_le_1": theta <= 1,
        })
    return rows


def block_rows(shells: list[dict], width: int) -> list[dict]:
    rows = []
    for end in range(width - 1, len(shells)):
        block = shells[end - width + 1 : end + 1]
        numerator = sum(row["delta_R"] for row in block)
        denominator = sum(row["delta_M_parent"] for row in block)
        theta = Fraction(numerator, denominator)
        rows.append({
            "end_power": block[-1]["power"],
            "end_X": block[-1]["X"],
            "width": width,
            "sum_delta_R": numerator,
            "sum_delta_M_parent": denominator,
            "theta": frac_payload(theta),
            "normalized_contraction": frac_payload(theta / 2),
            "theta_lt_2": theta < 2,
            "theta_le_1": theta <= 1,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-power", type=int, default=7)
    parser.add_argument("--max-power", type=int, default=27)
    parser.add_argument(
        "--block-widths",
        type=int,
        nargs="+",
        default=[2, 4, 8],
    )
    args = parser.parse_args()
    if args.min_power < 7:
        raise ValueError("min-power must be at least 7")
    if args.max_power < args.min_power:
        raise ValueError("max-power must be at least min-power")
    if any(width < 1 for width in args.block_widths):
        raise ValueError("block widths must be positive")

    repo = Path(__file__).resolve().parents[4]
    source = (
        repo
        / "problems/424/compute/wave3/C16_hole_contraction/hole_contraction.cpp"
    )
    source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()

    with tempfile.TemporaryDirectory(prefix="C54_dyadic_") as raw_directory:
        directory = Path(raw_directory)
        engine = directory / "C54_hole_contraction.exe"
        compile_engine(source, engine)
        endpoint_rows = {
            power: census(engine, 1 << power, directory)
            for power in range(args.min_power - 2, args.max_power + 1)
        }

    shells = shell_rows(endpoint_rows, args.min_power, args.max_power)
    blocks = {
        str(width): block_rows(shells, width)
        for width in args.block_widths
        if width <= len(shells)
    }

    maximum_shell = max(shells, key=lambda row: row["theta"]["decimal"])
    tail = [row for row in shells if row["X"] >= 100_000_000]
    payload = {
        "schema_version": 1,
        "engine_source": str(source.relative_to(repo)).replace("\\", "/"),
        "engine_sha256": source_sha256,
        "arithmetic": "exact ascending divisor recursion; distinct factors only",
        "endpoint_max": 1 << args.max_power,
        "shell_identity": "DeltaR_j = DeltaM_(j-1) + DeltaS_j + DeltaH_j - DeltaQ_j",
        "candidate": "limsup DeltaR_j/DeltaM_(j-1) < 2",
        "maximum_shell_theta": maximum_shell,
        "tail_at_or_above_1e8": tail,
        "shells": shells,
        "blocks": blocks,
    }
    print(json.dumps(payload, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
