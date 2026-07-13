#!/usr/bin/env python3
"""Independent exact row verifier for P116 BC108 search artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_score(values, h, b):
    values = tuple(values)
    sums = {}
    differences = set()
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in sums:
                raise AssertionError(("sum collision", total))
            sums[total] = (left, right)
        for right in values[i + 1:]:
            difference = right - left
            if difference in differences:
                raise AssertionError(("difference collision", difference))
            differences.add(difference)
    if values[-1] != h - 1:
        raise AssertionError(("endpoint", values[-1], h))
    folds = []
    for total, low_pair in sorted(sums.items()):
        high_pair = sums.get(total + h)
        if high_pair is not None:
            folds.append(low_pair + high_pair)
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    t_color = Counter()
    n_color = Counter(fold[2] for fold in folds)
    for (a, c), base in ac.items():
        for u in values:
            left = au.get((a, u))
            right = cu.get((c, u))
            if left is None or right is None:
                continue
            ids = (base, left, right)
            if ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("partial triangle", ids))
            triangles.append(ids)
            t_color[u] += 1
    excess = sum(max(0, t_color[u] - n_color[u]) for u in t_color)
    p = len(values)
    return {
        "p": p,
        "h": h,
        "b": b,
        "delta": (3 * p * p - p + 2) // 2 - h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "positive_color_excess": excess,
        "bc108_residual": excess - p,
        "literal_hole": all(total + b not in differences for total in sums),
    }


def verify_row(row):
    if row is None:
        return 0
    actual = independent_score(tuple(row["B"]), int(row["h"]), int(row["b"]))
    for key in (
        "p", "h", "b", "delta", "C_S", "T_F",
        "positive_color_excess", "bc108_residual",
    ):
        expected_key = "BC108_margin" if key == "bc108_residual" and "BC108_margin" in row else key
        if int(row[expected_key]) != int(actual[key]):
            raise AssertionError((key, row[expected_key], actual[key], row))
    if row.get("literal_hole") is not None and bool(row["literal_hole"]) != actual["literal_hole"]:
        raise AssertionError(("literal_hole", row, actual))
    return 1


def verify_manifest(data, artifact_path):
    checked = 0
    manifest = data.get("source_manifest", {})
    for relative, expected in manifest.items():
        if relative == "archives" or not isinstance(expected, str):
            continue
        path = artifact_path.parent / relative
        if path.exists():
            actual = sha256_file(path)
            if actual != expected:
                raise AssertionError(("source hash", path, expected, actual))
            checked += 1
    return checked


def verify_artifact(path: Path):
    data = json.loads(path.read_text())
    rows = 0
    manifest = verify_manifest(data, path)
    if "result" in data:
        result = data["result"]
        for key in ("worst", "parity_worst", "failure", "parity_failure"):
            rows += verify_row(result.get(key))
        if int(result.get("direct_bc108_failures", 0)) or int(result.get("parity_lift_bc108_failures", 0)):
            raise AssertionError(("reported failure count", path))
    if "archive_domain" in data:
        for domain_key in ("archive_domain", "mutation_domain"):
            result = data[domain_key]["result"]
            for key in ("worst", "parity_worst", "failure", "parity_failure"):
                rows += verify_row(result.get(key))
            if int(result.get("direct_bc108_failures", 0)) or int(result.get("parity_lift_bc108_failures", 0)):
                raise AssertionError(("reported failure count", path, domain_key))
    if "phases" in data:
        for phase in data["phases"]:
            if "by_deletion_count" in phase:
                if int(phase["failures"]):
                    raise AssertionError(("reported failure count", path, phase["b"]))
                for bucket in phase["by_deletion_count"]:
                    rows += verify_row(bucket.get("worst"))
                    rows += verify_row(bucket.get("failure"))
            elif "completion" in phase:
                completion = phase["completion"]
                if int(completion["bc108_failures"]):
                    raise AssertionError(("reported failure count", path, phase["b"]))
                rows += verify_row(completion.get("best_positive_row"))
                rows += verify_row(completion.get("failure"))
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "independent_rows_checked": rows,
        "source_hashes_checked": manifest,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "arithmetic": "independent exact Python integers",
        "artifacts": [verify_artifact(path.resolve()) for path in args.artifacts],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
