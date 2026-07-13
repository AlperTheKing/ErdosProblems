#!/usr/bin/env python3
"""Audit P61 inequalities on the stored Problem 864 extremizer corpus."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from audit_completion_defect import analyze, pair_sums


ROOT = Path(__file__).resolve().parents[4]


SOURCES = (
    ("census_cpsat", ROOT / "problems/864/compute/census_cpsat.jsonl", "A"),
    (
        "endpoint_certificates",
        ROOT / "problems/864/compute/oeis_endpoint_certificates.jsonl",
        "set",
    ),
    ("p20_samples", ROOT / "problems/864/compute/p20/results/samples.jsonl", "A"),
)


def audit_source(name: str, path: Path, set_key: str) -> dict:
    counts = Counter()
    failures: dict[str, dict | None] = {
        "two_beta_le_sum_holes": None,
        "core_shift_geometry": None,
        "repair_label_packing": None,
    }
    first_two_scale_only = None
    largest_residual = None

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row = json.loads(line)
        values = row.get(set_key)
        if not values:
            continue
        counts["rows"] += 1
        a = tuple(sorted(values))
        sums = pair_sums(a)
        repeated = [label for label, count in sums.items() if count >= 2]
        if len(repeated) > 1:
            raise AssertionError(f"nonadmissible stored row {path}:{line_number}")
        counts["admissible"] += 1
        if not repeated:
            counts["no_exception"] += 1
            continue
        sigma = repeated[0]
        aset = set(a)
        residual = [x for x in a if sigma - x not in aset]
        if not residual:
            counts["fully_reflected"] += 1
            if abs(sigma - a[0] - a[-1]) != 0:
                raise AssertionError(
                    f"fully reflected row has nonzero shift {path}:{line_number}"
                )
            continue

        counts["residual_records"] += 1
        record = analyze(a)
        if record is None:
            raise AssertionError(f"failed to analyze {path}:{line_number}")
        tagged = dict(record)
        tagged["source"] = f"{path.relative_to(ROOT).as_posix()}:{line_number}"
        if largest_residual is None or (record["k"], record["u"]) > (
            largest_residual["k"],
            largest_residual["u"],
        ):
            largest_residual = tagged

        if 2 * record["beta"] > record["sum_slack"]:
            failures["two_beta_le_sum_holes"] = tagged
        if record["span"] - record["tau"] < record["core_span"]:
            failures["core_shift_geometry"] = tagged
        if record["hybrid_support"] > record["span"] + record["tau"]:
            failures["repair_label_packing"] = tagged

        b = min(record["u"], record["beta"])
        old_margin = 3 * (
            (record["k"] + record["u"] - 2 * b) ** 2 - record["k"] ** 2
        ) - 4 * record["tau"]
        two_scale_base = (
            record["u"] ** 2
            - 2 * b * (record["k"] + record["u"])
            + 2 * b**2
        )
        if old_margin < 0 <= two_scale_base:
            counts["two_scale_holds_but_p56_fails"] += 1
            if first_two_scale_only is None:
                tagged["old_credit_cleared"] = old_margin
                tagged["two_scale_credit_base"] = two_scale_base
                first_two_scale_only = tagged

    return {
        "source": path.relative_to(ROOT).as_posix(),
        "counts": dict(counts),
        "failures": failures,
        "first_two_scale_holds_but_p56_fails": first_two_scale_only,
        "largest_residual_record": largest_residual,
    }


def main() -> None:
    results = [audit_source(*source) for source in SOURCES]
    output = ROOT / "problems/864/compute/p61/stored_extremizers_audit.json"
    payload = {
        "arithmetic": "integer only",
        "sources": results,
        "all_proved_checks_pass": all(
            all(value is None for value in result["failures"].values())
            for result in results
        ),
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
