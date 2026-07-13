"""Independent literal verifier and compact table for P12 JSONL scans."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def unordered_sum_counts(values: list[int]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for i, a in enumerate(values):
        for j in range(i, len(values)):
            counts[a + values[j]] += 1
    return counts


def verify_record(record: dict[str, object]) -> dict[str, object]:
    modulus = int(record["modulus"])
    residues = [int(x) for x in record["residues"]]
    p = len(residues)

    modular_sums = Counter(
        (residues[i] + residues[j]) % modulus
        for i in range(p)
        for j in range(i, p)
    )
    if max(modular_sums.values()) != 1:
        raise AssertionError("residue set is not strongly modular Sidon")

    pair_sums = {(a + b) % modulus for a in residues for b in residues}
    differences = {(a - b) % modulus for a in residues for b in residues}
    cover = {(s + d) % modulus for s in pair_sums for d in differences}
    if len(cover) != modulus:
        raise AssertionError("stored modular 3B-B saturation is false")
    if int(record["modular_3b_minus_b_coverage"]) != modulus:
        raise AssertionError("stored modular coverage count disagrees")

    best = record.get("best_candidate")
    if not isinstance(best, dict):
        return {
            "family": record["family"],
            "parameter": record["parameter"],
            "p": p,
            "modulus": modulus,
            "candidate": None,
        }

    b = [int(x) for x in best["points"]]
    center = int(best["candidate_center"])
    if b != sorted(set(b)) or b[0] != 0:
        raise AssertionError("candidate ruler is not normalized")
    if not center > 2 * b[-1]:
        raise AssertionError("center does not separate reflected copies")
    if center >= 3 * p * p:
        raise AssertionError("candidate does not beat coefficient 3")

    b_counts = unordered_sum_counts(b)
    if max(b_counts.values()) != 1:
        raise AssertionError("candidate B is not literally Sidon")
    sums = set(b_counts)
    positive_differences = {
        b[j] - b[i] for i in range(p) for j in range(i + 1, p)
    }
    if center in {s + d for s in sums for d in positive_differences}:
        raise AssertionError("candidate center lies in S(B)+Delta+(B)")

    reflected = sorted(set(b) | {center - x for x in b})
    if len(reflected) != 2 * p:
        raise AssertionError("reflected copies overlap")
    repeats = sorted(
        (s, multiplicity)
        for s, multiplicity in unordered_sum_counts(reflected).items()
        if multiplicity >= 2
    )
    if repeats != [(center, p)]:
        raise AssertionError(("literal admissibility failed", repeats))

    return {
        "family": record["family"],
        "parameter": int(record["parameter"]),
        "p": p,
        "modulus": modulus,
        "affine_multiplier": int(best["affine_multiplier"]),
        "cut_base": int(best["cut_base"]),
        "cut_gap": int(best["cut_gap"]),
        "span": b[-1],
        "center": center,
        "center_over_p2": str(Fraction(center, p * p)),
        "hole_offset_above_2span": center - 2 * b[-1],
        "scan_exhaustive": bool(record["scan_exhaustive"]),
        "candidate": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    manifest = []
    for path in args.inputs:
        raw = path.read_bytes()
        manifest.append(
            {
                "path": path.as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        )
        for line_number, line in enumerate(raw.decode("ascii").splitlines(), 1):
            try:
                row = verify_record(json.loads(line))
            except Exception as exc:
                raise AssertionError(f"{path}:{line_number}: {exc}") from exc
            if row["candidate"]:
                rows.append(row)

    rows.sort(key=lambda x: (str(x["family"]), int(x["p"])))
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="ascii") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    args.manifest.write_text(
        json.dumps(
            {
                "inputs": manifest,
                "verified_records": len(rows),
                "csv": args.csv.as_posix(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="ascii",
    )
    print(json.dumps({"verified_records": len(rows), "manifest": manifest}, sort_keys=True))


if __name__ == "__main__":
    main()
