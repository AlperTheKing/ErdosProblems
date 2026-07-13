#!/usr/bin/env python3
"""Exact support-defect profiler for Erdos Problem 864, lane P20.

All decisions and comparisons are integer or rational. Decimal strings are
emitted only as explicitly labelled display fields.
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import io
import json
import math
import random
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Iterator, Sequence


@dataclass(frozen=True)
class Sample:
    sample_id: str
    N: int
    A: tuple[int, ...]
    kind: str
    source: str
    parent_id: str | None = None


@dataclass(frozen=True)
class Admissibility:
    exceptional_sum: int | None
    exceptional_multiplicity: int
    repeated_sums: tuple[tuple[int, int], ...]


def json_line(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def rational_pair(num: int, den: int) -> tuple[int, int]:
    if den <= 0:
        raise ValueError("denominator must be positive")
    if num == 0:
        return 0, 1
    common = math.gcd(abs(num), den)
    return num // common, den // common


def rational_text(num: int, den: int) -> str:
    reduced_num, reduced_den = rational_pair(num, den)
    return f"{reduced_num}/{reduced_den}"


def decimal_text(num: int, den: int, digits: int = 12) -> str:
    with localcontext() as context:
        context.prec = digits + 12
        value = Decimal(num) / Decimal(den)
        return f"{value:.{digits}f}"


def ratio_lt(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] * right[1] < right[0] * left[1]


def ratio_le(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] * right[1] <= right[0] * left[1]


def ceil_sqrt(value: int) -> int:
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def ceil_nth_root(value: int, exponent: int) -> int:
    if value < 0 or exponent < 1:
        raise ValueError("invalid root request")
    if value <= 1:
        return value
    low, high = 0, 1
    while high**exponent < value:
        high *= 2
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**exponent >= value:
            high = middle
        else:
            low = middle
    return high


def unordered_sum_counts(values: Sequence[int]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for index, left in enumerate(values):
        for right in values[index:]:
            counts[left + right] += 1
    return counts


def positive_difference_counts(values: Sequence[int]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for index, upper in enumerate(values):
        for lower in values[:index]:
            counts[upper - lower] += 1
    return counts


def verify_sample(N: int, values: Sequence[int]) -> Admissibility:
    A = tuple(values)
    if N < 1:
        raise ValueError("N must be positive")
    if not A:
        raise ValueError("A must be nonempty")
    if A != tuple(sorted(set(A))):
        raise ValueError("A must be strictly increasing")
    if A[0] < 1 or A[-1] > N:
        raise ValueError("A lies outside [1,N]")
    repeated = tuple(
        sorted((value, count) for value, count in unordered_sum_counts(A).items() if count >= 2)
    )
    if len(repeated) > 1:
        raise ValueError(f"non-admissible sample has repeated sums {repeated}")
    differences = positive_difference_counts(A)
    if differences and max(differences.values()) > 2:
        raise ValueError("admissible sample has a difference multiplicity above two")
    if repeated:
        return Admissibility(repeated[0][0], repeated[0][1], repeated)
    return Admissibility(None, 0, repeated)


def make_id(prefix: str, N: int, values: Sequence[int]) -> str:
    payload = f"{N}:" + ",".join(str(value) for value in values)
    digest = hashlib.sha256(payload.encode("ascii")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def normalized_reflected_sample(
    points: Sequence[int], center: int, *, prefix: str, kind: str, source: str
) -> Sample:
    reflected = sorted(set(points) | {center - value for value in points})
    shift = 1 - reflected[0]
    values = tuple(value + shift for value in reflected)
    N = values[-1]
    verify_sample(N, values)
    return Sample(make_id(prefix, N, values), N, values, kind, source)


def _read_jsonl(path: Path) -> Iterator[tuple[int, dict[str, object]]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{line_number}: record is not an object")
                yield line_number, value


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def artifact_input_paths(repo_root: Path) -> list[Path]:
    compute = repo_root / "problems" / "864" / "compute"
    p12 = compute / "p12"
    return [
        compute / "census_cpsat.jsonl",
        compute / "oeis_endpoint_certificates.jsonl",
        *sorted(p12.glob("*.jsonl")),
    ]


def artifact_input_hashes(repo_root: Path) -> dict[str, str]:
    return {
        _relative(path, repo_root): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in artifact_input_paths(repo_root)
    }


def load_artifact_samples(repo_root: Path) -> list[Sample]:
    compute = repo_root / "problems" / "864" / "compute"
    samples: list[Sample] = []

    census = compute / "census_cpsat.jsonl"
    for line_number, record in _read_jsonl(census):
        N = int(record["N"])
        values = tuple(int(value) for value in record["A"])
        verify_sample(N, values)
        source = f"{_relative(census, repo_root)}:{line_number}"
        samples.append(Sample(make_id("census", N, values), N, values, "census", source))

    endpoints = compute / "oeis_endpoint_certificates.jsonl"
    for line_number, record in _read_jsonl(endpoints):
        N = int(record["n"])
        values = tuple(int(value) for value in record["set"])
        verify_sample(N, values)
        source = f"{_relative(endpoints, repo_root)}:{line_number}"
        samples.append(Sample(make_id("endpoint", N, values), N, values, "endpoint", source))

    p12 = compute / "p12"
    for path in sorted(p12.glob("*.jsonl")):
        for line_number, record in _read_jsonl(path):
            check = record.get("best_candidate_check")
            if not isinstance(check, dict) or not isinstance(check.get("reflected_set"), list):
                continue
            raw = tuple(int(value) for value in check["reflected_set"])
            shift = 1 - min(raw)
            values = tuple(sorted(value + shift for value in raw))
            N = max(values)
            verify_sample(N, values)
            family = str(record.get("family", "reflected"))
            source = f"{_relative(path, repo_root)}:{line_number}"
            samples.append(
                Sample(make_id(family, N, values), N, values, f"reflected-{family}", source)
            )

    for path in sorted(p12.glob("*natural*.jsonl")):
        for line_number, record in _read_jsonl(path):
            for field in ("best_below_3p2", "best_in_2v_to_5v_over_2"):
                candidate = record.get(field)
                if not isinstance(candidate, dict) or not isinstance(candidate.get("points"), list):
                    continue
                center = int(candidate["center"])
                family = str(record.get("family", "natural"))
                source = f"{_relative(path, repo_root)}:{line_number}:{field}"
                samples.append(
                    normalized_reflected_sample(
                        [int(value) for value in candidate["points"]],
                        center,
                        prefix=f"{family}-natural",
                        kind=f"reflected-{family}-natural",
                        source=source,
                    )
                )

    unique: dict[tuple[int, tuple[int, ...]], Sample] = {}
    for sample in samples:
        unique.setdefault((sample.N, sample.A), sample)
    return sorted(unique.values(), key=lambda item: (item.N, len(item.A), item.sample_id))


def _admissible_greedy(N: int, seed: int) -> tuple[int, ...]:
    order = list(range(1, N + 1))
    random.Random(seed).shuffle(order)
    chosen: list[int] = []
    for value in order:
        candidate = tuple(sorted((*chosen, value)))
        try:
            verify_sample(N, candidate)
        except ValueError:
            continue
        chosen = list(candidate)
    return tuple(chosen)


def generate_samples(base_samples: Sequence[Sample]) -> list[Sample]:
    generated: list[Sample] = []
    representatives: dict[str, Sample] = {}
    for sample in base_samples:
        current = representatives.get(sample.kind)
        if current is None or (sample.N, len(sample.A)) > (current.N, len(current.A)):
            representatives[sample.kind] = sample

    for base in sorted(representatives.values(), key=lambda item: item.kind):
        if len(base.A) < 6:
            continue
        analysis = verify_sample(base.N, base.A)
        if analysis.exceptional_sum is not None:
            exceptional = analysis.exceptional_sum
            removable = {
                max(left, exceptional - left)
                for index, left in enumerate(base.A)
                if left < exceptional - left and exceptional - left in set(base.A) and index % 2 == 0
            }
            partial = tuple(value for value in base.A if value not in removable)
            if len(partial) >= 3 and partial != base.A:
                verify_sample(base.N, partial)
                generated.append(
                    Sample(
                        make_id("partial-core", base.N, partial),
                        base.N,
                        partial,
                        "generated-partial-core",
                        "deterministic alternating reflection deletion",
                        base.sample_id,
                    )
                )
        alternating = tuple(value for index, value in enumerate(base.A) if index % 3 != 1)
        if len(alternating) >= 3:
            verify_sample(base.N, alternating)
            generated.append(
                Sample(
                    make_id("subset", base.N, alternating),
                    base.N,
                    alternating,
                    "generated-subset",
                    "deterministic index-modulo-three deletion",
                    base.sample_id,
                )
            )

    for N in (64, 128, 256, 512, 1024):
        for seed in (864, 20864):
            values = _admissible_greedy(N, seed + N)
            verify_sample(N, values)
            generated.append(
                Sample(
                    make_id("greedy", N, values),
                    N,
                    values,
                    "generated-greedy",
                    f"deterministic shuffled greedy seed={seed + N}",
                )
            )

    unique: dict[tuple[int, tuple[int, ...]], Sample] = {}
    for sample in generated:
        unique.setdefault((sample.N, sample.A), sample)
    return sorted(unique.values(), key=lambda item: (item.N, len(item.A), item.sample_id))


def profile_sample(sample: Sample) -> list[dict[str, int | str]]:
    analysis = verify_sample(sample.N, sample.A)
    k = len(sample.A)
    gaps = sorted(sample.A[index] - sample.A[index - 1] for index in range(1, k))
    gap_prefix = [0]
    for gap in gaps:
        gap_prefix.append(gap_prefix[-1] + gap)

    difference_counts = positive_difference_counts(sample.A)
    duplicate_count_prefix = [0] * sample.N
    duplicate_sum_prefix = [0] * sample.N
    missing_count_prefix = [0] * sample.N
    missing_sum_prefix = [0] * sample.N
    for distance in range(1, sample.N):
        multiplicity = difference_counts.get(distance, 0)
        if multiplicity not in (0, 1, 2):
            raise AssertionError("difference multiplicity escaped {0,1,2}")
        duplicate = max(multiplicity - 1, 0)
        missing = 1 if multiplicity == 0 else 0
        duplicate_count_prefix[distance] = duplicate_count_prefix[distance - 1] + duplicate
        duplicate_sum_prefix[distance] = duplicate_sum_prefix[distance - 1] + distance * duplicate
        missing_count_prefix[distance] = missing_count_prefix[distance - 1] + missing
        missing_sum_prefix[distance] = missing_sum_prefix[distance - 1] + distance * missing

    rows: list[dict[str, int | str]] = []
    total_gap = gap_prefix[-1]
    for H in range(1, sample.N + 1):
        below = bisect.bisect_left(gaps, H)
        M = H + gap_prefix[below] + H * (len(gaps) - below)
        above = bisect.bisect_right(gaps, H)
        truncated_count = len(gaps) - above
        gap_truncation = total_gap - gap_prefix[above] - H * truncated_count
        components = 1 + truncated_count
        index = H - 1
        duplicate_count = duplicate_count_prefix[index]
        missing_count = missing_count_prefix[index]
        duplicate_weight = H * duplicate_count - duplicate_sum_prefix[index]
        missing_weight = H * missing_count - missing_sum_prefix[index]
        Z = duplicate_weight - missing_weight
        base_numerator = H * H + 2 * Z
        product_num = M * base_numerator
        product_den = sample.N * H * H
        reduced_product_num, reduced_product_den = rational_pair(product_num, product_den)
        if k * k * H * H > M * (base_numerator + (k - 1) * H):
            raise AssertionError(f"P02 failed for {sample.sample_id} at H={H}")
        rows.append(
            {
                "H": H,
                "M": M,
                "Z": Z,
                "base_factor_numerator": base_numerator,
                "base_factor_denominator": H * H,
                "component_count": components,
                "gap_truncation_count": truncated_count,
                "gap_truncation_weight": gap_truncation,
                "duplicate_distance_count": duplicate_count,
                "duplicate_weight": duplicate_weight,
                "missing_distance_count": missing_count,
                "missing_weight": missing_weight,
                "frontier_product_numerator": reduced_product_num,
                "frontier_product_denominator": reduced_product_den,
            }
        )
    return rows


def product_ratio(sample: Sample, row: dict[str, int | str]) -> tuple[int, int]:
    H = int(row["H"])
    numerator = int(row["M"]) * int(row["base_factor_numerator"])
    return rational_pair(numerator, sample.N * H * H)


def choose_min_product(sample: Sample, rows: Sequence[dict[str, int | str]], low: int, high: int) -> int:
    if not 1 <= low <= high <= sample.N:
        raise ValueError("invalid minimization interval")
    best = low
    best_ratio = product_ratio(sample, rows[low - 1])
    for H in range(low + 1, high + 1):
        candidate = product_ratio(sample, rows[H - 1])
        if ratio_lt(candidate, best_ratio):
            best, best_ratio = H, candidate
    return best


def selected_rules(sample: Sample, rows: Sequence[dict[str, int | str]]) -> dict[str, int]:
    k = len(sample.A)
    h0 = min(sample.N, ceil_sqrt(sample.N * k))
    upper = min(sample.N, 2 * h0)
    lower = max(1, (h0 + 1) // 2)
    max_gap = max(
        (sample.A[index] - sample.A[index - 1] for index in range(1, k)),
        default=1,
    )
    first_nonpositive = next(
        (H for H in range(h0, sample.N + 1) if int(rows[H - 1]["Z"]) <= 0),
        sample.N,
    )
    powers = []
    power = 1
    while power < lower:
        power *= 2
    while power <= upper:
        powers.append(power)
        power *= 2
    if not powers:
        powers = [h0]
    dyadic = powers[0]
    for H in powers:
        if ratio_lt(product_ratio(sample, rows[H - 1]), product_ratio(sample, rows[dyadic - 1])):
            dyadic = H
    return {
        "H_equals_k": min(sample.N, k),
        "ceil_sqrt_N": min(sample.N, ceil_sqrt(sample.N)),
        "ceil_N_two_thirds": min(sample.N, ceil_nth_root(sample.N**2, 3)),
        "ceil_N_three_quarters": min(sample.N, ceil_nth_root(sample.N**3, 4)),
        "half_sqrt_Nk": lower,
        "ceil_sqrt_Nk": h0,
        "first_connected": min(sample.N, max_gap),
        "first_Z_nonpositive_after_h0": first_nonpositive,
        "dyadic_balanced_min": dyadic,
        "one_sided_band_min": choose_min_product(sample, rows, h0, upper),
        "balanced_band_min": choose_min_product(sample, rows, lower, upper),
        "global_min": choose_min_product(sample, rows, 1, sample.N),
    }


def _excess_over_four_thirds(ratio: tuple[int, int]) -> tuple[int, int]:
    return rational_pair(3 * ratio[0] - 4 * ratio[1], 3 * ratio[1])


def _required_coefficient(
    product: tuple[int, int], N: int, k: int, H: int
) -> tuple[int, int]:
    excess_num = 3 * product[0] - 4 * product[1]
    if excess_num <= 0:
        return 0, 1
    correction_num = H * H + N * (k - 1)
    correction_den = N * H
    return rational_pair(excess_num * correction_den, 3 * product[1] * correction_num)


def _sample_record(sample: Sample, analysis: Admissibility) -> dict[str, object]:
    return {
        "A": list(sample.A),
        "N": sample.N,
        "exceptional_multiplicity": analysis.exceptional_multiplicity,
        "exceptional_sum": analysis.exceptional_sum,
        "kind": sample.kind,
        "parent_id": sample.parent_id,
        "sample_id": sample.sample_id,
        "size": len(sample.A),
        "source": sample.source,
    }


def audit_samples(
    samples: Sequence[Sample],
    output_dir: Path,
    candidate_coefficient: Fraction,
    repo_root: Path | None = None,
    expected_artifact_hashes: dict[str, str] | None = None,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_path = output_dir / "samples.jsonl"
    profile_path = output_dir / "profiles.jsonl.gz"
    rule_worst: dict[str, dict[str, object]] = {}
    rule_falsifiers: Counter[str] = Counter()
    rule_required_worst: dict[str, dict[str, object]] = {}
    rule_c1_failures: Counter[str] = Counter()
    rule_c2_failures: Counter[str] = Counter()
    required_worst: dict[str, object] | None = None
    candidate_failures: list[dict[str, object]] = []
    total_profiles = 0

    gzip_binary = gzip.GzipFile(filename=str(profile_path), mode="wb", mtime=0)
    gzip_text = io.TextIOWrapper(gzip_binary, encoding="ascii", newline="\n")
    with sample_path.open("w", encoding="ascii", newline="\n") as sample_handle, gzip_text as profile_handle:
        for sample in samples:
            analysis = verify_sample(sample.N, sample.A)
            sample_handle.write(json_line(_sample_record(sample, analysis)) + "\n")
            rows = profile_sample(sample)
            total_profiles += len(rows)
            for row in rows:
                profile_handle.write(
                    json_line(
                        {
                            **row,
                            "N": sample.N,
                            "exceptional_multiplicity": analysis.exceptional_multiplicity,
                            "sample_id": sample.sample_id,
                            "size": len(sample.A),
                        }
                    )
                    + "\n"
                )

            rules = selected_rules(sample, rows)
            for rule, H in rules.items():
                row = rows[H - 1]
                ratio = product_ratio(sample, row)
                excess = _excess_over_four_thirds(ratio)
                if excess[0] > 0:
                    rule_falsifiers[rule] += 1
                item = {
                    "H": H,
                    "N": sample.N,
                    "frontier_product": rational_text(*ratio),
                    "frontier_product_display": decimal_text(*ratio),
                    "sample_id": sample.sample_id,
                    "size": len(sample.A),
                    "source": sample.source,
                }
                correction_num = H * H + sample.N * (len(sample.A) - 1)
                correction_den = sample.N * H
                rule_required = _required_coefficient(ratio, sample.N, len(sample.A), H)
                if not ratio_le(rule_required, (1, 1)):
                    rule_c1_failures[rule] += 1
                if not ratio_le(rule_required, (2, 1)):
                    rule_c2_failures[rule] += 1
                rule_required_item = {
                    "H": H,
                    "M": row["M"],
                    "N": sample.N,
                    "Z": row["Z"],
                    "correction_base": rational_text(correction_num, correction_den),
                    "frontier_product": rational_text(*ratio),
                    "required_coefficient": rational_text(*rule_required),
                    "required_coefficient_display": decimal_text(*rule_required),
                    "sample_id": sample.sample_id,
                    "size": len(sample.A),
                    "source": sample.source,
                }
                old_rule_required = rule_required_worst.get(rule)
                if old_rule_required is None:
                    rule_required_worst[rule] = rule_required_item
                else:
                    old_required_ratio = tuple(
                        int(value)
                        for value in str(old_rule_required["required_coefficient"]).split("/")
                    )
                    if ratio_lt(old_required_ratio, rule_required):
                        rule_required_worst[rule] = rule_required_item
                old = rule_worst.get(rule)
                if old is None:
                    rule_worst[rule] = item
                else:
                    old_num, old_den = (int(value) for value in str(old["frontier_product"]).split("/"))
                    if ratio_lt((old_num, old_den), ratio):
                        rule_worst[rule] = item

            adaptive_H = rules["ceil_N_two_thirds"]
            adaptive_row = rows[adaptive_H - 1]
            adaptive_product = product_ratio(sample, rows[adaptive_H - 1])
            correction_num = adaptive_H * adaptive_H + sample.N * (len(sample.A) - 1)
            correction_den = sample.N * adaptive_H
            required = _required_coefficient(adaptive_product, sample.N, len(sample.A), adaptive_H)
            required_item = {
                "H": adaptive_H,
                "M": adaptive_row["M"],
                "N": sample.N,
                "Z": adaptive_row["Z"],
                "component_count": adaptive_row["component_count"],
                "correction_base": rational_text(correction_num, correction_den),
                "duplicate_weight": adaptive_row["duplicate_weight"],
                "exceptional_multiplicity": analysis.exceptional_multiplicity,
                "frontier_product": rational_text(*adaptive_product),
                "gap_truncation_count": adaptive_row["gap_truncation_count"],
                "gap_truncation_weight": adaptive_row["gap_truncation_weight"],
                "missing_weight": adaptive_row["missing_weight"],
                "required_coefficient": rational_text(*required),
                "required_coefficient_display": decimal_text(*required),
                "sample_id": sample.sample_id,
                "size": len(sample.A),
                "source": sample.source,
            }
            if required_worst is None:
                required_worst = required_item
            else:
                old_required = tuple(
                    int(value) for value in str(required_worst["required_coefficient"]).split("/")
                )
                if ratio_lt(old_required, required):
                    required_worst = required_item
            coefficient_ratio = (
                candidate_coefficient.numerator,
                candidate_coefficient.denominator,
            )
            if not ratio_le(required, coefficient_ratio):
                candidate_failures.append(required_item)

    candidate_failures.sort(
        key=lambda item: -Fraction(str(item["required_coefficient"]))
    )
    input_hashes = {}
    for path in (sample_path, profile_path):
        input_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    artifact_hashes = {}
    if repo_root is not None:
        artifact_hashes = artifact_input_hashes(repo_root)
    if expected_artifact_hashes is not None and artifact_hashes != expected_artifact_hashes:
        raise RuntimeError("artifact inputs changed during the exact profile sweep")
    summary: dict[str, object] = {
        "arithmetic": "integer/rational; decimal fields are display only",
        "artifact_inputs": artifact_hashes,
        "candidate": {
            "coefficient": rational_text(candidate_coefficient.numerator, candidate_coefficient.denominator),
            "coefficient_display": decimal_text(candidate_coefficient.numerator, candidate_coefficient.denominator),
            "failures": candidate_failures,
            "failure_count": len(candidate_failures),
            "formula": "P_H <= 4/3 + C*(H/N + (k-1)/H), H=ceil_cuberoot(N^2)",
            "strongest_required_coefficient": required_worst,
        },
        "files": input_hashes,
        "profile_count": total_profiles,
        "rule_audit": {
            rule: {
                **item,
                "C1_failure_count": rule_c1_failures[rule],
                "C2_failure_count": rule_c2_failures[rule],
                "falsifier_count": rule_falsifiers[rule],
                "strongest_required_coefficient": rule_required_worst[rule],
            }
            for rule, item in sorted(rule_worst.items())
        },
        "sample_count": len(samples),
        "sample_kinds": dict(sorted(Counter(sample.kind for sample in samples).items())),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="ascii")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="repository root",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
        help="generated exact output directory",
    )
    parser.add_argument(
        "--candidate-coefficient",
        type=Fraction,
        default=Fraction(3, 2),
        help="nonnegative rational C in the finite-correction candidate",
    )
    parser.add_argument("--no-generated", action="store_true", help="use artifact samples only")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.candidate_coefficient < 0:
        raise SystemExit("--candidate-coefficient must be nonnegative")
    expected_artifact_hashes = artifact_input_hashes(args.repo_root)
    artifact_samples = load_artifact_samples(args.repo_root)
    generated = [] if args.no_generated else generate_samples(artifact_samples)
    samples = sorted(
        [*artifact_samples, *generated], key=lambda item: (item.N, len(item.A), item.sample_id)
    )
    summary = audit_samples(
        samples,
        args.output_dir,
        args.candidate_coefficient,
        args.repo_root,
        expected_artifact_hashes,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if int(summary["candidate"]["failure_count"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
