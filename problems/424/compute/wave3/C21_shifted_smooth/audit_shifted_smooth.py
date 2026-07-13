#!/usr/bin/env python3
"""Exact finite audit for the C21 shifted-smooth SR-S lane.

The accepted C03 helper constructs G. The C21 C++ analyzer then factors every
3s+1 at the requested range and emits integer counts plus directed rational
intervals. This wrapper checks partitions, derives certified Fraction bounds,
and removes timing data so repeated outputs are byte-for-byte deterministic.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
CPP_PATH = HERE / "shifted_smooth.cpp"
C03_PATH = HERE.parent / "C03_smooth_rough.py"
KNOWN_PREFIXES = {
    10: (4, None),
    100: (23, None),
    1_000: (250, None),
    10_000: (3_207, None),
    100_000: (39_843, None),
    1_000_000: (
        457_599,
        "569056ee7b16336bbf9eaa0b0fcfc77376048f12d7157da440333207b8a2e365",
    ),
    10_000_000: (
        4_952_270,
        "7f5f29e1d5733d623c514c98c183796c3ab15a99d9ad9e5f0c9ff6ea627d85a0",
    ),
}


def load_c03():
    spec = importlib.util.spec_from_file_location("c21_c03", C03_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {C03_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


C03 = load_c03()


@contextmanager
def retrying_flat_temporary_root():
    try:
        yield HERE
    finally:
        for artifact in HERE.glob(f"{C03.TEMP_PREFIX}*"):
            for attempt in range(50):
                try:
                    artifact.unlink()
                    break
                except FileNotFoundError:
                    break
                except PermissionError:
                    if attempt == 49:
                        raise
                    time.sleep(0.1)


def sha256_path(path: Path, byte_count: int | None = None) -> str:
    digest = hashlib.sha256()
    remaining = byte_count
    with path.open("rb") as stream:
        while True:
            size = 8 * 1024 * 1024
            if remaining is not None:
                size = min(size, remaining)
            if size == 0:
                break
            block = stream.read(size)
            if not block:
                break
            digest.update(block)
            if remaining is not None:
                remaining -= len(block)
    if remaining not in (None, 0):
        raise AssertionError("hash byte range exceeds file length")
    return digest.hexdigest()


def compile_analyzer(compiler_name: str, executable: Path) -> dict[str, str]:
    compiler = shutil.which(compiler_name)
    if compiler is None:
        raise RuntimeError(f"compiler not found: {compiler_name}")
    command = [
        compiler,
        "-O3",
        "-DNDEBUG",
        "-std=c++20",
        str(CPP_PATH),
        "-o",
        str(executable),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    version = subprocess.run(
        [compiler, "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    return {
        "compiler_version": version,
        "source_sha256": sha256_path(CPP_PATH),
        "compile_stdout": completed.stdout.strip(),
        "compile_stderr": completed.stderr.strip(),
    }


def parse_bounds(record: dict[str, str]) -> tuple[Fraction, Fraction]:
    denominator = int(record["denominator"])
    lower = Fraction(int(record["lower_numerator"]), denominator)
    upper = Fraction(int(record["upper_numerator"]), denominator)
    if lower > upper:
        raise AssertionError("directed interval is reversed")
    return lower, upper


def decimal_text(value: Fraction, places: int = 15) -> str:
    with localcontext() as context:
        context.prec = places + 12
        number = Decimal(value.numerator) / Decimal(value.denominator)
        return format(number, f".{places}f")


def fraction_record(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": decimal_text(value),
    }


def interval_record(lower: Fraction, upper: Fraction) -> dict[str, object]:
    return {
        "lower": fraction_record(lower),
        "upper": fraction_record(upper),
    }


def enrich_row(row: dict[str, object]) -> None:
    counts = row["counts"]
    harmonic = row["harmonic_bounds"]
    assert isinstance(counts, dict)
    assert isinstance(harmonic, dict)

    if counts["smooth"] != counts["T_present"] + counts["T_missing"]:
        raise AssertionError("smooth membership partition failed")
    if counts["T_missing"] != counts["splitless"] + counts["blocked"]:
        raise AssertionError("missing partition failed")
    if counts["blocked"] != (
        counts["unique_pair_blocked"] + counts["multi_pair_blocked"]
    ):
        raise AssertionError("blocked multiplicity partition failed")
    if counts["splitless"] != (
        counts["no_2mod3_prime"] + counts["exceptional_p2_square"]
    ):
        raise AssertionError("splitless characterization count failed")

    h_lower, h_upper = parse_bounds(harmonic["H"])
    present_lower, present_upper = parse_bounds(harmonic["present"])
    missing_lower, missing_upper = parse_bounds(harmonic["missing"])
    splitless_lower, splitless_upper = parse_bounds(harmonic["splitless"])
    blocked_lower, blocked_upper = parse_bounds(harmonic["blocked"])
    unique_lower, unique_upper = parse_bounds(harmonic["unique_pair_blocked"])
    multi_lower, multi_upper = parse_bounds(harmonic["multi_pair_blocked"])

    if (h_lower, h_upper) != (
        present_lower + missing_lower,
        present_upper + missing_upper,
    ):
        raise AssertionError("harmonic membership partition failed")
    if (missing_lower, missing_upper) != (
        splitless_lower + blocked_lower,
        splitless_upper + blocked_upper,
    ):
        raise AssertionError("harmonic missing partition failed")
    if (blocked_lower, blocked_upper) != (
        unique_lower + multi_lower,
        unique_upper + multi_upper,
    ):
        raise AssertionError("harmonic blocked partition failed")

    k_lower, k_upper = parse_bounds(harmonic["missing_arithmetic_pair_mass"])
    holes_lower, holes_upper = parse_bounds(
        harmonic["missing_hole_endpoint_mass"]
    )
    if k_lower > holes_lower or k_upper > holes_upper:
        raise AssertionError("aggregated blocker inequality failed")

    all_holes_lower, all_holes_upper = parse_bounds(
        harmonic["hole_endpoint_mass"]
    )

    first_lower, _ = parse_bounds(harmonic["witness_first_moment"])
    _, second_upper = parse_bounds(harmonic["witness_second_moment"])
    if second_upper == 0:
        moment_coverage_lower = Fraction(0)
    else:
        moment_coverage_lower = (
            first_lower * first_lower / (second_upper * h_upper)
        )
    actual_missing_interval = (
        missing_lower / h_upper,
        missing_upper / h_lower,
    )
    actual_coverage_interval = (
        present_lower / h_upper,
        present_upper / h_lower,
    )
    moment_missing_upper = 1 - moment_coverage_lower
    if first_lower * first_lower > second_upper * present_upper:
        raise AssertionError("weighted Cauchy interval check failed")

    row["certified_ratios"] = {
        "actual_missing_over_H": interval_record(*actual_missing_interval),
        "actual_covered_over_H": interval_record(*actual_coverage_interval),
        "splitless_over_H": interval_record(
            splitless_lower / h_upper,
            splitless_upper / h_lower,
        ),
        "blocked_over_H": interval_record(
            blocked_lower / h_upper,
            blocked_upper / h_lower,
        ),
        "all_hole_endpoint_mass_over_H": interval_record(
            all_holes_lower / h_upper,
            all_holes_upper / h_lower,
        ),
        "Cauchy_covered_over_H_lower": fraction_record(moment_coverage_lower),
        "Cauchy_missing_over_H_upper": fraction_record(moment_missing_upper),
    }


def validate_prefixes(bitmap_path: Path, helper_limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    largest = min(helper_limit, max(KNOWN_PREFIXES))
    with bitmap_path.open("rb") as stream:
        prefix = stream.read(largest + 1)
    if len(prefix) != largest + 1:
        raise AssertionError("G bitmap ended inside the accepted prefix range")
    for bound, (expected_count, expected_hash) in KNOWN_PREFIXES.items():
        if bound > helper_limit:
            continue
        actual_count = prefix[: bound + 1].count(b"\x01")
        if actual_count != expected_count:
            raise AssertionError(f"G prefix count mismatch at {bound}")
        actual_hash = None
        if expected_hash is not None:
            actual_hash = sha256_path(bitmap_path, bound + 1)
            if actual_hash != expected_hash:
                raise AssertionError(f"G prefix hash mismatch at {bound}")
        rows.append(
            {
                "bound": bound,
                "count": actual_count,
                "sha256": actual_hash,
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10_000_000)
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--output", type=Path, default=HERE / "result.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 100 <= args.limit <= 100_000_000:
        raise ValueError("--limit must lie in [100, 100000000]")
    output = args.output.resolve()
    if output.parent != HERE:
        raise ValueError("--output must be directly inside the C21 directory")
    helper_limit = 3 * args.limit + 1

    with retrying_flat_temporary_root() as temp_dir:
        c03_executable, c03_compile = C03.compile_helper(temp_dir, args.compiler)
        bitmap_path = temp_dir / f"{C03.TEMP_PREFIX}c21_G.bin"
        helper_output, _ = C03.run_helper(
            c03_executable, helper_limit, bitmap_path, 0
        )
        prefix_checks = validate_prefixes(bitmap_path, helper_limit)

        analyzer = temp_dir / f"{C03.TEMP_PREFIX}c21_shifted_smooth.exe"
        analyzer_compile = compile_analyzer(args.compiler, analyzer)
        raw_path = temp_dir / f"{C03.TEMP_PREFIX}c21_raw.json"
        completed = subprocess.run(
            [str(analyzer), str(args.limit), str(bitmap_path), str(raw_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "C21 analyzer failed with code "
                f"{completed.returncode}: {completed.stderr.strip()}"
            )
        raw = json.loads(raw_path.read_text(encoding="ascii"))
        raw.pop("elapsed_seconds", None)
        for row in raw["rows"]:
            enrich_row(row)

        result = {
            "method": (
                "exact C03 well-founded G bitmap; exact SPF factorization of "
                "every 3s+1; integer counts and directed denominator-1e18 bounds"
            ),
            "parameters": {
                "smooth_limit": args.limit,
                "G_limit": helper_limit,
            },
            "G_builder": {
                "count_through_G_limit": int(helper_output["count"]),
                "bitmap_sha256": sha256_path(bitmap_path),
                "source_sha256": c03_compile["helper_source_sha256"],
                "compiler_version": c03_compile["compiler_version"],
                "accepted_prefix_checks": prefix_checks,
            },
            "C21_analyzer": {
                "source_sha256": analyzer_compile["source_sha256"],
                "script_sha256": sha256_path(Path(__file__).resolve()),
                "compiler_version": analyzer_compile["compiler_version"],
                "row_count": len(raw["rows"]),
                "stderr": completed.stderr.strip(),
            },
            "audit": raw,
        }

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    output.write_text(rendered, encoding="ascii", newline="\n")
    print(
        f"limit={args.limit} rows={len(raw['rows'])} "
        f"output_sha256={hashlib.sha256(rendered.encode('ascii')).hexdigest()}"
    )


if __name__ == "__main__":
    main()
