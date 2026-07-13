#!/usr/bin/env python3
"""Exact finite smooth/rough membership census for Erdos 424, gates (31)-(32).

This is a discovery and falsification tool.  It constructs the exact membership
bitmap of G by the well-founded recursion

    n in G iff n in {2, 3}, or n + 1 = a*b with a,b in G and 2 <= a < b,

then reads T(n) as G(3*n).  The optimized bitmap builder is embedded C++ and
uses process-unique temporary files in an existing writable directory; all
reported census arithmetic is integer or Fraction arithmetic.  Floating-point
values are used only to instantiate the real-valued parameter recipe and to
display exact rational diagnostics.
"""

from __future__ import annotations

import argparse
import bisect
from contextlib import contextmanager
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[4]
DEFAULT_TEMP_ROOT = SCRIPT_PATH.parent
TEMP_PREFIX = f".C03_{os.getpid()}_"

CPP_SOURCE = r"""
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: exact_g_bitmap LIMIT OUTPUT_BITMAP\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit > 1000000000ULL) {
        throw std::runtime_error("LIMIT exceeds the audited uint32 range");
    }
    const std::uint32_t limit = static_cast<std::uint32_t>(parsed_limit);
    const auto started = std::chrono::steady_clock::now();

    // spf[m] is the smallest prime factor of m, for every m <= limit + 1.
    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t p = 2;
         static_cast<std::uint64_t>(p) * p <= static_cast<std::uint64_t>(limit) + 1;
         ++p) {
        if (spf[p] != p) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += p) {
            if (spf[multiple] == multiple) spf[multiple] = p;
        }
    }

    // Byte i is exactly 1 when i is in G, and 0 otherwise.
    std::vector<std::uint8_t> reached(static_cast<std::size_t>(limit) + 1, 0);
    std::uint64_t count = 0;
    if (limit >= 2) {
        reached[2] = 1;
        ++count;
    }
    if (limit >= 3) {
        reached[3] = 1;
        ++count;
    }

    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);
    for (std::uint32_t n = 4; n <= limit; ++n) {
        const std::uint32_t product = n + 1;
        std::uint32_t remaining = product;
        divisors.clear();
        divisors.push_back(1);

        while (remaining > 1) {
            const std::uint32_t prime = spf[remaining];
            const std::size_t old_size = divisors.size();
            std::uint32_t power = 1;
            do {
                remaining /= prime;
                power *= prime;
                for (std::size_t i = 0; i < old_size; ++i) {
                    divisors.push_back(divisors[i] * power);
                }
            } while (remaining > 1 && spf[remaining] == prime);
        }

        for (const std::uint32_t left : divisors) {
            if (left < 2) continue;
            const std::uint32_t right = product / left;
            if (left >= right) continue;  // Enforces distinct values.
            if (reached[left] && reached[right]) {
                reached[n] = 1;
                ++count;
                break;
            }
        }
    }

    std::ofstream output(argv[2], std::ios::binary);
    if (!output) throw std::runtime_error("could not open output bitmap");
    output.write(
        reinterpret_cast<const char*>(reached.data()),
        static_cast<std::streamsize>(reached.size())
    );
    if (!output) throw std::runtime_error("could not write output bitmap");

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::cout << "{\"limit\":" << limit
              << ",\"count\":" << count
              << ",\"elapsed_seconds\":" << elapsed.count()
              << "}\n";
    return 0;
}
"""


@dataclass(frozen=True)
class FormulaSpec:
    x: int
    u_real: float
    y_real: float
    z_real: float
    l_real: float
    l_int: int
    y_int: int
    z_int: int


@dataclass
class RoughPrefixData:
    z: int
    max_r: int
    rough: np.ndarray
    missing: np.ndarray
    rough_prefix: np.ndarray
    missing_prefix: np.ndarray
    rough_sha256: str
    missing_sha256: str


def sha256_path(path: Path, byte_count: int | None = None) -> str:
    digest = hashlib.sha256()
    remaining = byte_count
    with path.open("rb") as stream:
        while True:
            size = 8 * 1024 * 1024 if remaining is None else min(8 * 1024 * 1024, remaining)
            if size == 0:
                break
            block = stream.read(size)
            if not block:
                break
            digest.update(block)
            if remaining is not None:
                remaining -= len(block)
    if remaining not in (None, 0):
        raise ValueError(f"{path} has fewer than {byte_count} bytes")
    return digest.hexdigest()


def sha256_array(array: np.ndarray) -> str:
    if not array.flags.c_contiguous:
        array = np.ascontiguousarray(array)
    return hashlib.sha256(memoryview(array)).hexdigest()


def fraction_record(value: Fraction) -> dict[str, int | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal_approx": format(float(value), ".15g"),
    }


def count_rate(misses: int, population: int) -> dict[str, int | str]:
    if population <= 0:
        raise ValueError("rate population must be positive")
    return fraction_record(Fraction(misses, population))


def primes_up_to(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [p for p in range(2, limit + 1) if sieve[p]]


def is_z_smooth(value: int, z: int) -> bool:
    """Return P+(value) <= z, with 1 declared z-smooth."""
    if value < 1:
        return False
    remaining = value
    for prime in primes_up_to(z):
        while remaining % prime == 0:
            remaining //= prime
    return remaining == 1


def formula_spec(x: int) -> FormulaSpec:
    """Instantiate the natural-log parameter recipe and directed rounding."""
    if x <= math.e:
        raise ValueError("X must exceed e")
    log_x = math.log(x)
    u_real = math.sqrt(math.log(log_x))
    y_real = math.exp(math.sqrt(log_x))
    z_real = math.exp(math.log(y_real) / u_real)
    l_real = math.exp(math.sqrt(math.log(z_real)))
    return FormulaSpec(
        x=x,
        u_real=u_real,
        y_real=y_real,
        z_real=z_real,
        l_real=l_real,
        l_int=math.ceil(l_real),
        y_int=math.floor(y_real),
        z_int=math.floor(z_real),
    )


@contextmanager
def flat_temporary_root(root: Path | None) -> Iterable[Path]:
    """Yield an existing writable root and remove this process's flat artifacts."""
    resolved = (root or SCRIPT_PATH.parent).resolve()
    if not resolved.is_dir():
        raise ValueError(f"temporary root is not an existing directory: {resolved}")
    try:
        yield resolved
    finally:
        for artifact in resolved.glob(f"{TEMP_PREFIX}*"):
            try:
                artifact.unlink()
            except FileNotFoundError:
                pass


def compile_helper(temp_dir: Path, compiler_name: str) -> tuple[Path, dict[str, object]]:
    compiler = shutil.which(compiler_name)
    if compiler is None:
        raise RuntimeError(f"compiler not found: {compiler_name}")
    source_path = temp_dir / f"{TEMP_PREFIX}exact_g_bitmap.cpp"
    executable = temp_dir / (
        f"{TEMP_PREFIX}exact_g_bitmap.exe"
        if os.name == "nt"
        else f"{TEMP_PREFIX}exact_g_bitmap"
    )
    source_path.write_text(CPP_SOURCE, encoding="ascii", newline="\n")
    command = [
        compiler,
        "-O3",
        "-DNDEBUG",
        "-std=c++20",
        str(source_path),
        "-o",
        str(executable),
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    elapsed = time.perf_counter() - started
    version = subprocess.run(
        [compiler, "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    return executable, {
        "compiler": compiler,
        "compiler_version": version,
        "compile_command": subprocess.list2cmdline(command),
        "compile_stdout": completed.stdout.strip(),
        "compile_stderr": completed.stderr.strip(),
        "compile_elapsed_seconds": format(elapsed, ".6f"),
        "helper_source_sha256": hashlib.sha256(CPP_SOURCE.encode("ascii")).hexdigest(),
        "helper_executable_sha256": sha256_path(executable),
    }


def run_helper(
    executable: Path, limit: int, bitmap_path: Path, timeout_seconds: int
) -> tuple[dict[str, object], dict[str, object]]:
    command = [str(executable), str(limit), str(bitmap_path)]
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=None if timeout_seconds == 0 else timeout_seconds,
    )
    wall_elapsed = time.perf_counter() - started
    helper_output = json.loads(completed.stdout)
    expected_size = limit + 1
    actual_size = bitmap_path.stat().st_size
    if actual_size != expected_size:
        raise AssertionError(f"bitmap has {actual_size} bytes, expected {expected_size}")
    return helper_output, {
        "run_command": subprocess.list2cmdline(command),
        "run_stderr": completed.stderr.strip(),
        "run_wall_seconds": format(wall_elapsed, ".6f"),
    }


def independent_worklist_closure(limit: int) -> bytearray:
    """Independent truncated closure, used only by the small self-test."""
    reached = bytearray(limit + 1)
    pool = [value for value in (2, 3) if value <= limit]
    inset = set(pool)
    work = list(pool)
    for value in pool:
        reached[value] = 1
    while work:
        left = work.pop()
        max_right = (limit + 1) // left
        stop = bisect.bisect_right(pool, max_right)
        for right in pool[:stop]:
            if left == right:
                continue
            child = left * right - 1
            if child <= limit and child not in inset:
                inset.add(child)
                bisect.insort(pool, child)
                work.append(child)
                reached[child] = 1
    return reached


def hash_t_bitmap(membership: np.memmap, t_limit: int) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    chunk = 1_000_000
    for start in range(0, t_limit + 1, chunk):
        stop = min(t_limit + 1, start + chunk)
        values = np.ascontiguousarray(membership[3 * start : 3 * stop : 3])
        count += int(np.count_nonzero(values))
        digest.update(memoryview(values))
    return count, digest.hexdigest()


def validate_reference(
    membership: np.memmap, limit: int
) -> dict[str, object] | None:
    reference_path = SCRIPT_PATH.parents[1] / f"census_{limit}.json"
    if not reference_path.exists():
        return None
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    if int(reference["limit"]) != limit:
        raise AssertionError("reference limit mismatch")
    actual_count = int(np.count_nonzero(membership))
    checkpoint_rows = []
    for checkpoint, expected in reference.get("checkpoints", []):
        actual = int(np.count_nonzero(membership[: int(checkpoint) + 1]))
        checkpoint_rows.append(
            {
                "bound": int(checkpoint),
                "expected": int(expected),
                "actual": actual,
                "match": actual == int(expected),
            }
        )
    count_match = actual_count == int(reference["count"])
    checkpoints_match = all(row["match"] for row in checkpoint_rows)
    if not count_match or not checkpoints_match:
        raise AssertionError("membership bitmap disagrees with reference census")
    return {
        "path": str(reference_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": sha256_path(reference_path),
        "count_expected": int(reference["count"]),
        "count_actual": actual_count,
        "count_match": count_match,
        "checkpoint_rows": checkpoint_rows,
        "all_checkpoints_match": checkpoints_match,
    }


def build_rough_prefix_data(
    membership: np.memmap, z: int, max_r: int
) -> RoughPrefixData:
    if 3 * max_r >= membership.size:
        raise ValueError("rough census exceeds the exact T membership window")
    rough = np.ones(max_r + 1, dtype=np.bool_)
    rough[: min(z + 1, max_r + 1)] = False
    for prime in primes_up_to(z):
        rough[prime::prime] = False
    t_values = membership[: 3 * max_r + 1 : 3]
    missing = np.logical_and(rough, t_values == 0)
    rough_prefix = np.cumsum(rough, dtype=np.int64)
    missing_prefix = np.cumsum(missing, dtype=np.int64)
    return RoughPrefixData(
        z=z,
        max_r=max_r,
        rough=rough,
        missing=missing,
        rough_prefix=rough_prefix,
        missing_prefix=missing_prefix,
        rough_sha256=sha256_array(rough),
        missing_sha256=sha256_array(missing),
    )


def prefix_counts(data: RoughPrefixData, cutoff: int) -> dict[str, object]:
    rough_count = int(data.rough_prefix[cutoff])
    missing_count = int(data.missing_prefix[cutoff])
    return {
        "cutoff": cutoff,
        "rough_count": rough_count,
        "T_member_count": rough_count - missing_count,
        "T_miss_count": missing_count,
        "ambient_miss_rate": count_rate(missing_count, cutoff),
        "conditional_rough_miss_rate": count_rate(missing_count, rough_count),
    }


def slab_counts(data: RoughPrefixData, left: int, right: int) -> dict[str, object]:
    before_rough = int(data.rough_prefix[left - 1]) if left else 0
    before_missing = int(data.missing_prefix[left - 1]) if left else 0
    rough_count = int(data.rough_prefix[right]) - before_rough
    missing_count = int(data.missing_prefix[right]) - before_missing
    return {
        "left": left,
        "right": right,
        "integer_count": right - left + 1,
        "rough_count": rough_count,
        "T_member_count": rough_count - missing_count,
        "T_miss_count": missing_count,
        "ambient_slab_miss_rate": count_rate(missing_count, right - left + 1),
        "conditional_rough_miss_rate": count_rate(missing_count, rough_count),
    }


def _is_better(
    numerator: int, denominator: int, best_numerator: int, best_denominator: int
) -> bool:
    return numerator * best_denominator > best_numerator * denominator


def prefix_rate_suprema(
    data: RoughPrefixData, left: int, right: int
) -> dict[str, object]:
    """Exact suprema over every integer cutoff in [left,right].

    Both rates can only increase at a missing rough integer.  Checking left
    and all such events is therefore an exhaustive exact comparison.
    """
    ambient_arg = left
    ambient_num = int(data.missing_prefix[left])
    ambient_den = left
    conditional_arg = left
    conditional_num = ambient_num
    conditional_den = int(data.rough_prefix[left])
    candidate_events = np.flatnonzero(data.missing[left + 1 : right + 1])
    for offset in candidate_events:
        cutoff = left + 1 + int(offset)
        misses = int(data.missing_prefix[cutoff])
        rough = int(data.rough_prefix[cutoff])
        if _is_better(misses, cutoff, ambient_num, ambient_den):
            ambient_arg, ambient_num, ambient_den = cutoff, misses, cutoff
        if _is_better(misses, rough, conditional_num, conditional_den):
            conditional_arg, conditional_num, conditional_den = cutoff, misses, rough
    return {
        "cutoffs_exhausted": right - left + 1,
        "increase_events_checked": int(candidate_events.size),
        "ambient": {
            "definition": "# {z-rough r <= R with r not in T} / R",
            "argmax_R": ambient_arg,
            "rate": fraction_record(Fraction(ambient_num, ambient_den)),
            "counts_at_argmax": prefix_counts(data, ambient_arg),
        },
        "conditional": {
            "definition": "# {z-rough r <= R with r not in T} / # {z-rough r <= R}",
            "argmax_R": conditional_arg,
            "rate": fraction_record(Fraction(conditional_num, conditional_den)),
            "counts_at_argmax": prefix_counts(data, conditional_arg),
        },
    }


def factor_cutoff_supremum(
    data: RoughPrefixData, x: int, smooth_t_values: Sequence[int]
) -> dict[str, object]:
    cutoffs_to_s: dict[int, list[int]] = {}
    for smooth in smooth_t_values:
        cutoffs_to_s.setdefault(x // smooth, []).append(smooth)
    best_cutoff = -1
    best_num = 0
    best_den = 1
    for cutoff in sorted(cutoffs_to_s):
        misses = int(data.missing_prefix[cutoff])
        if best_cutoff < 0 or _is_better(misses, cutoff, best_num, best_den):
            best_cutoff, best_num, best_den = cutoff, misses, cutoff
    if best_cutoff < 0:
        raise ValueError("no eligible smooth T-members")
    return {
        "distinct_factor_cutoffs": len(cutoffs_to_s),
        "argmax_R": best_cutoff,
        "smooth_s_at_argmax": cutoffs_to_s[best_cutoff],
        "ambient_rate": fraction_record(Fraction(best_num, best_den)),
        "counts_at_argmax": prefix_counts(data, best_cutoff),
    }


def analyze_spec(
    membership: np.memmap, spec: FormulaSpec, rough_data: RoughPrefixData
) -> dict[str, object]:
    smooth_values = [
        value for value in range(1, spec.y_int + 1) if is_z_smooth(value, spec.z_int)
    ]
    smooth_members = [value for value in smooth_values if membership[3 * value]]
    smooth_misses = [value for value in smooth_values if not membership[3 * value]]
    eligible = [value for value in smooth_values if value >= spec.l_int]
    eligible_members = [value for value in eligible if membership[3 * value]]
    eligible_misses = [value for value in eligible if not membership[3 * value]]

    harmonic = sum((Fraction(1, value) for value in smooth_values), Fraction())
    member_weight = sum((Fraction(1, value) for value in smooth_members), Fraction())
    missing_weight = sum((Fraction(1, value) for value in smooth_misses), Fraction())
    eligible_missing_weight = sum(
        (Fraction(1, value) for value in eligible_misses), Fraction()
    )

    rough_left = spec.x // spec.y_int
    rough_right = spec.x // spec.l_int
    if rough_left <= spec.z_int or rough_right > rough_data.max_r:
        raise AssertionError("invalid rough cutoff interval")
    suprema = prefix_rate_suprema(rough_data, rough_left, rough_right)
    ambient_sup = Fraction(
        int(suprema["ambient"]["rate"]["numerator"]),
        int(suprema["ambient"]["rate"]["denominator"]),
    )
    conditional_sup = Fraction(
        int(suprema["conditional"]["rate"]["numerator"]),
        int(suprema["conditional"]["rate"]["denominator"]),
    )

    return {
        "X": spec.x,
        "real_recipe": {
            "u=sqrt(log(log(X)))": format(spec.u_real, ".17g"),
            "y=exp(sqrt(log(X)))": format(spec.y_real, ".17g"),
            "z=y^(1/u)": format(spec.z_real, ".17g"),
            "L=exp(sqrt(log(z)))": format(spec.l_real, ".17g"),
        },
        "integer_triple_(L,y,z)": [spec.l_int, spec.y_int, spec.z_int],
        "rounding": "L=ceil(L_real), y=floor(y_real), z=floor(z_real)",
        "smooth_s_le_y": {
            "definition": "1 <= s <= y and every prime divisor of s is <= z; 1 is smooth",
            "values": smooth_values,
            "count": len(smooth_values),
            "T_member_count": len(smooth_members),
            "T_miss_count": len(smooth_misses),
            "T_miss_values": smooth_misses,
            "count_miss_rate": count_rate(len(smooth_misses), len(smooth_values)),
            "H_z(y)_exact": fraction_record(harmonic),
            "T_member_reciprocal_sum_exact": fraction_record(member_weight),
            "gate31_T_miss_reciprocal_sum_exact": fraction_record(missing_weight),
            "gate31_mass_over_log(z)_decimal_only": format(
                float(missing_weight) / math.log(spec.z_int), ".15g"
            ),
        },
        "eligible_s_in_[L,y]": {
            "values": eligible,
            "count": len(eligible),
            "T_member_count": len(eligible_members),
            "T_miss_count": len(eligible_misses),
            "T_miss_values": eligible_misses,
            "T_miss_reciprocal_sum_exact": fraction_record(eligible_missing_weight),
        },
        "rough_r": {
            "definition": "r > z and no prime <= z divides r",
            "prefix_cutoff_interval": [rough_left, rough_right],
            "interval_derivation": "[floor(X/y), floor(X/L)] for integer L,y",
            "classification_arrays_built_through": rough_data.max_r,
            "rough_mask_sha256": rough_data.rough_sha256,
            "rough_T_miss_mask_sha256": rough_data.missing_sha256,
            "left_endpoint_prefix": prefix_counts(rough_data, rough_left),
            "right_endpoint_prefix": prefix_counts(rough_data, rough_right),
            "cutoff_interval_slab": slab_counts(rough_data, rough_left, rough_right),
            "suprema_over_every_integer_cutoff": suprema,
            "supremum_over_actual_eligible_T_s_cutoffs": factor_cutoff_supremum(
                rough_data, spec.x, eligible_members
            ),
        },
        "gate32_diagnostics": {
            "definition": "H_z(y) times the displayed exact prefix-rate supremum",
            "H_times_ambient_sup_exact": fraction_record(harmonic * ambient_sup),
            "H_times_conditional_sup_exact": fraction_record(harmonic * conditional_sup),
        },
    }


def git_head() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def default_x_values(t_limit: int) -> list[int]:
    values = [value for value in (1_000_000, 10_000_000) if value <= t_limit]
    values.append(t_limit)
    return sorted(set(values))


def run_self_test(compiler: str, temp_root: Path | None) -> None:
    limit = 10_000
    with flat_temporary_root(temp_root) as temp_dir:
        executable, compile_metadata = compile_helper(temp_dir, compiler)
        bitmap_path = temp_dir / f"{TEMP_PREFIX}selftest_g.bin"
        helper_output, _ = run_helper(executable, limit, bitmap_path, 0)
        actual = bitmap_path.read_bytes()
        expected = independent_worklist_closure(limit)
        if actual != expected:
            differences = [
                index
                for index, (left, right) in enumerate(zip(actual, expected))
                if left != right
            ][:10]
            raise AssertionError(f"independent closure mismatch at {differences}")
        if sum(actual) != 3207 or int(helper_output["count"]) != 3207:
            raise AssertionError("unexpected exact count at 10000")
        assert is_z_smooth(1, 7)
        assert is_z_smooth(72, 7)
        assert not is_z_smooth(77, 7)

        mapped = np.memmap(bitmap_path, dtype=np.uint8, mode="r")
        rough_data = build_rough_prefix_data(mapped, z=5, max_r=1000)
        left, right = 100, 1000
        optimized = prefix_rate_suprema(rough_data, left, right)
        for label, conditional in (("ambient", False), ("conditional", True)):
            best_r = left
            best = Fraction(
                int(rough_data.missing_prefix[left]),
                int(rough_data.rough_prefix[left]) if conditional else left,
            )
            for cutoff in range(left + 1, right + 1):
                candidate = Fraction(
                    int(rough_data.missing_prefix[cutoff]),
                    int(rough_data.rough_prefix[cutoff]) if conditional else cutoff,
                )
                if candidate > best:
                    best_r, best = cutoff, candidate
            recorded = optimized[label]
            assert int(recorded["argmax_R"]) == best_r
            assert Fraction(
                int(recorded["rate"]["numerator"]),
                int(recorded["rate"]["denominator"]),
            ) == best
        mapped._mmap.close()
        del mapped
        print(
            json.dumps(
                {
                    "self_test": "PASS",
                    "limit": limit,
                    "exact_G_count": sum(actual),
                    "bitmap_sha256": hashlib.sha256(actual).hexdigest(),
                    "independent_algorithm": "truncated sorted-worklist closure",
                    "rough_supremum_crosscheck_cutoffs": right - left + 1,
                    "helper_source_sha256": compile_metadata["helper_source_sha256"],
                    "script_sha256": sha256_path(SCRIPT_PATH),
                },
                indent=2,
                sort_keys=True,
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100_000_000)
    parser.add_argument(
        "--x-values",
        type=int,
        nargs="+",
        help="finite X values; default is 1e6, 1e7, and floor(limit/3) when available",
    )
    parser.add_argument("--compiler", default="g++")
    parser.add_argument(
        "--temp-root",
        type=Path,
        default=DEFAULT_TEMP_ROOT,
        help="optional writable parent for temporary compiler and bitmap files",
    )
    parser.add_argument(
        "--helper-timeout",
        type=int,
        default=0,
        help="seconds; zero means no timeout",
    )
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test(args.compiler, args.temp_root)
        return
    if args.limit < 100:
        raise ValueError("--limit must be at least 100")
    t_limit = args.limit // 3
    x_values = sorted(set(args.x_values or default_x_values(t_limit)))
    if not x_values or x_values[-1] > t_limit:
        raise ValueError(f"every X must be at most floor(limit/3)={t_limit}")
    specs = [formula_spec(value) for value in x_values]
    for spec in specs:
        if spec.l_int > spec.y_int:
            raise ValueError(f"empty [L,y] at X={spec.x}")

    started = time.perf_counter()
    with flat_temporary_root(args.temp_root) as temp_dir:
        executable, compile_metadata = compile_helper(temp_dir, args.compiler)
        bitmap_path = temp_dir / f"{TEMP_PREFIX}g_membership.bin"
        helper_output, run_metadata = run_helper(
            executable, args.limit, bitmap_path, args.helper_timeout
        )
        membership = np.memmap(bitmap_path, dtype=np.uint8, mode="r")
        g_count = int(np.count_nonzero(membership))
        if g_count != int(helper_output["count"]):
            raise AssertionError("helper count disagrees with bitmap")

        reference = validate_reference(membership, args.limit)
        t_count, t_sha256 = hash_t_bitmap(membership, t_limit)
        prefix_sha256 = {
            str(bound): sha256_path(bitmap_path, bound + 1)
            for bound in (1_000_000, 10_000_000)
            if bound <= args.limit
        }

        requirements: dict[int, int] = {}
        for spec in specs:
            requirements[spec.z_int] = max(
                requirements.get(spec.z_int, 0), spec.x // spec.l_int
            )
        analyses_by_x: dict[int, dict[str, object]] = {}
        rough_builds: list[dict[str, object]] = []
        for z, max_r in sorted(requirements.items()):
            rough_started = time.perf_counter()
            rough_data = build_rough_prefix_data(membership, z, max_r)
            rough_builds.append(
                {
                    "z": z,
                    "max_r": max_r,
                    "rough_mask_sha256": rough_data.rough_sha256,
                    "rough_T_miss_mask_sha256": rough_data.missing_sha256,
                    "elapsed_seconds": format(time.perf_counter() - rough_started, ".6f"),
                }
            )
            for spec in specs:
                if spec.z_int == z:
                    analyses_by_x[spec.x] = analyze_spec(membership, spec, rough_data)

        first_members = np.flatnonzero(
            membership[: min(args.limit + 1, 1000)]
        ).tolist()[:30]
        output = {
            "schema_version": 1,
            "scope": "finite discovery/falsification census only; no asymptotic inference",
            "generated_at": datetime.now().astimezone().isoformat(),
            "invocation": subprocess.list2cmdline([sys.executable, *sys.argv]),
            "git_HEAD": git_head(),
            "environment": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "platform": platform.platform(),
            },
            "definitions": {
                "G": "least set containing 2,3 and closed under a*b-1 for distinct values a,b",
                "membership_recursion": (
                    "G[n]=1 iff n in {2,3}, or some divisor pair "
                    "2<=a<b of n+1 has G[a]=G[b]=1"
                ),
                "T": "T={n>=1: 3*n is in G}; exact only through floor(B/3)",
                "z_smooth": "s>=1 with every prime divisor <=z; 1 is z-smooth",
                "z_rough": "r>z with no prime divisor <=z",
                "ambient_rough_miss_rate": (
                    "D_z(R)=#{r<=R: r is z-rough and r not in T}/R"
                ),
                "conditional_rough_miss_rate": (
                    "same numerator divided by #{r<=R: r is z-rough}"
                ),
            },
            "membership_bitmap": {
                "B": args.limit,
                "byte_layout": "B+1 bytes indexed 0..B; byte n is 1 iff n in G",
                "size_bytes": int(membership.size),
                "G_count": g_count,
                "sha256": sha256_path(bitmap_path),
                "prefix_bitmap_sha256_through_bound_inclusive": prefix_sha256,
                "first_30_members": first_members,
                "T_limit": t_limit,
                "T_count_through_limit": t_count,
                "T_bitmap_sha256_indices_0_through_limit": t_sha256,
                "reference_census_crosscheck": reference,
            },
            "builder": compile_metadata | run_metadata | {"helper_output": helper_output},
            "rough_array_builds": rough_builds,
            "parameter_censuses": [analyses_by_x[value] for value in x_values],
            "total_wall_seconds": format(time.perf_counter() - started, ".6f"),
            "interpretation_guard": (
                "All values are finite exact censuses except labeled decimal recipe/display "
                "fields. They neither prove nor suggest a limiting rate without a separate theorem."
            ),
            "script_sha256": sha256_path(SCRIPT_PATH),
        }
        membership._mmap.close()
        del membership
        print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
