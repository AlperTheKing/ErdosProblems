#!/usr/bin/env python3
"""Stream-verifier for generated P20 exact profile artifacts."""

from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Sequence

from support_defect_profiles import artifact_input_hashes, rational_pair, verify_sample


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def load_samples(path: Path) -> dict[str, dict[str, object]]:
    samples: dict[str, dict[str, object]] = {}
    with path.open("r", encoding="ascii") as handle:
        for line_number, line in enumerate(handle, 1):
            record = json.loads(line)
            if contains_float(record):
                raise AssertionError(f"{path}:{line_number}: float field")
            sample_id = str(record["sample_id"])
            if sample_id in samples:
                raise AssertionError(f"duplicate sample id {sample_id}")
            N = int(record["N"])
            A = tuple(int(value) for value in record["A"])
            analysis = verify_sample(N, A)
            if analysis.exceptional_sum != record["exceptional_sum"]:
                raise AssertionError(f"{sample_id}: exceptional sum mismatch")
            if analysis.exceptional_multiplicity != int(record["exceptional_multiplicity"]):
                raise AssertionError(f"{sample_id}: exceptional multiplicity mismatch")
            if len(A) != int(record["size"]):
                raise AssertionError(f"{sample_id}: size mismatch")
            samples[sample_id] = record
    return samples


def make_profile_state(sample: dict[str, object]) -> dict[str, object]:
    A = tuple(int(value) for value in sample["A"])
    gaps = sorted(A[index] - A[index - 1] for index in range(1, len(A)))
    gap_prefix = [0]
    for gap in gaps:
        gap_prefix.append(gap_prefix[-1] + gap)
    differences: Counter[int] = Counter()
    for index, upper in enumerate(A):
        for lower in A[:index]:
            differences[upper - lower] += 1
    return {
        "differences": differences,
        "duplicate_count": 0,
        "duplicate_sum": 0,
        "gaps": gaps,
        "gap_prefix": gap_prefix,
        "missing_count": 0,
        "missing_sum": 0,
    }


def verify_profiles(path: Path, samples: dict[str, dict[str, object]]) -> int:
    next_h = {sample_id: 1 for sample_id in samples}
    current_id: str | None = None
    state: dict[str, object] | None = None
    finished: set[str] = set()
    count = 0
    with gzip.open(path, "rt", encoding="ascii") as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            if contains_float(row):
                raise AssertionError(f"{path}:{line_number}: float field")
            sample_id = str(row["sample_id"])
            if sample_id not in samples:
                raise AssertionError(f"unknown sample id {sample_id}")
            H = int(row["H"])
            if H != next_h[sample_id]:
                raise AssertionError(
                    f"{sample_id}: expected H={next_h[sample_id]}, found H={H}"
                )
            sample = samples[sample_id]
            N = int(sample["N"])
            k = int(sample["size"])
            if sample_id != current_id:
                if current_id is not None:
                    previous_final = int(samples[current_id]["N"]) + 1
                    if next_h[current_id] != previous_final:
                        raise AssertionError(f"{current_id}: noncontiguous profile block")
                    finished.add(current_id)
                if sample_id in finished:
                    raise AssertionError(f"{sample_id}: repeated profile block")
                current_id = sample_id
                state = make_profile_state(sample)
            if state is None:
                raise AssertionError("missing profile state")
            if int(row["N"]) != N or int(row["size"]) != k:
                raise AssertionError(f"{sample_id}: repeated metadata mismatch")
            if int(row["exceptional_multiplicity"]) != int(sample["exceptional_multiplicity"]):
                raise AssertionError(f"{sample_id}: repeated exception mismatch")
            distance = H - 1
            if distance:
                multiplicity = state["differences"].get(distance, 0)
                duplicate = max(multiplicity - 1, 0)
                missing = 1 if multiplicity == 0 else 0
                state["duplicate_count"] += duplicate
                state["duplicate_sum"] += distance * duplicate
                state["missing_count"] += missing
                state["missing_sum"] += distance * missing
            duplicate_weight = H * state["duplicate_count"] - state["duplicate_sum"]
            missing_weight = H * state["missing_count"] - state["missing_sum"]
            gaps = state["gaps"]
            gap_prefix = state["gap_prefix"]
            below = bisect.bisect_left(gaps, H)
            above = bisect.bisect_right(gaps, H)
            truncation_count = len(gaps) - above
            truncation_weight = gap_prefix[-1] - gap_prefix[above] - H * truncation_count
            M = H + gap_prefix[below] + H * (len(gaps) - below)
            expected_metrics = {
                "M": M,
                "component_count": 1 + truncation_count,
                "duplicate_distance_count": state["duplicate_count"],
                "duplicate_weight": duplicate_weight,
                "gap_truncation_count": truncation_count,
                "gap_truncation_weight": truncation_weight,
                "missing_distance_count": state["missing_count"],
                "missing_weight": missing_weight,
            }
            for field, expected in expected_metrics.items():
                if int(row[field]) != expected:
                    raise AssertionError(f"{sample_id},H={H}: {field} mismatch")
            Z = int(row["Z"])
            if Z != duplicate_weight - missing_weight:
                raise AssertionError(f"{sample_id},H={H}: Z decomposition mismatch")
            base_numerator = H * H + 2 * Z
            if int(row["base_factor_numerator"]) != base_numerator:
                raise AssertionError(f"{sample_id},H={H}: base numerator mismatch")
            if int(row["base_factor_denominator"]) != H * H:
                raise AssertionError(f"{sample_id},H={H}: base denominator mismatch")
            product = rational_pair(M * base_numerator, N * H * H)
            archived = (
                int(row["frontier_product_numerator"]),
                int(row["frontier_product_denominator"]),
            )
            if archived != product:
                raise AssertionError(f"{sample_id},H={H}: product mismatch")
            if math.gcd(abs(archived[0]), archived[1]) != 1:
                raise AssertionError(f"{sample_id},H={H}: product is not reduced")
            if k * k * H * H > M * (base_numerator + (k - 1) * H):
                raise AssertionError(f"{sample_id},H={H}: P02 inequality failed")
            next_h[sample_id] = H + 1
            count += 1
    for sample_id, expected in next_h.items():
        final = int(samples[sample_id]["N"]) + 1
        if expected != final:
            raise AssertionError(f"{sample_id}: profile ended at H={expected - 1}, expected {final - 1}")
    return count


def verify_all(repo_root: Path, results: Path) -> dict[str, object]:
    summary_path = results / "summary.json"
    samples_path = results / "samples.jsonl"
    profiles_path = results / "profiles.jsonl.gz"
    summary = json.loads(summary_path.read_text(encoding="ascii"))
    expected_files = summary["files"]
    actual_files = {
        samples_path.name: file_hash(samples_path),
        profiles_path.name: file_hash(profiles_path),
    }
    if actual_files != expected_files:
        raise AssertionError("generated file hash mismatch")
    actual_inputs = artifact_input_hashes(repo_root)
    if actual_inputs != summary["artifact_inputs"]:
        raise AssertionError("artifact input hash mismatch")
    samples = load_samples(samples_path)
    if len(samples) != int(summary["sample_count"]):
        raise AssertionError("sample count mismatch")
    profile_count = verify_profiles(profiles_path, samples)
    if profile_count != int(summary["profile_count"]):
        raise AssertionError("profile count mismatch")
    return {
        "artifact_count": len(actual_inputs),
        "profile_count": profile_count,
        "sample_count": len(samples),
        "status": "verified",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
    )
    args = parser.parse_args(argv)
    print(json.dumps(verify_all(args.repo_root, args.results), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
