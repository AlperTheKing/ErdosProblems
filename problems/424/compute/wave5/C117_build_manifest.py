#!/usr/bin/env python3
"""Build the C117 aggregate manifest from declared exact-search artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ARTIFACTS = (
    "C117_base_powers_5k.json",
    "C117_focused.json",
    "C117_diverse_26k.json",
    "C117_slot_sweep_100k.json",
    "C117_cross_seed_fiber_30k.json",
    "C117_second_generation_fiber_30k.json",
)
RAISING_FAMILIES = {
    "base_prime_power",
    "base_multi_plus",
    "squarefree",
    "prime_power",
    "composite_q",
    "hard_shape_expansion",
    "cross_seed_fiber",
}
STATE_KEYS = ("generated", "hard", "structural_splitless", "other_hole")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build(root: Path) -> dict[str, object]:
    claims = []
    artifact_rows = []
    family_rows = []
    candidate_evaluations = 0
    classified_sources = 0
    generated_sources = 0
    hard_sources = 0
    below_min_d = 0
    target_falsifiers = 0
    maximum_source = 0
    maximum_tested_d = 0
    raising_classified = 0
    raising_generated = 0
    hard_records: dict[int, dict[str, object]] = {}

    for filename in ARTIFACTS:
        path = root / filename
        with path.open("r", encoding="ascii") as handle:
            claim = json.load(handle)
        if claim.get("schema") != "C117-structural-power-falsifier-v1":
            raise ValueError(("schema", filename, claim.get("schema")))
        claims.append(claim)
        summary = claim["summary"]
        evaluations = int(summary["evaluated_candidates"])
        candidate_evaluations += evaluations
        maximum_source = max(maximum_source, int(summary["largest_source_tested"] or 0))
        target_falsifiers += int(summary["target_3_4_falsifiers"])
        artifact_classified = 0
        for family, stats in sorted(claim["evaluation"].items()):
            state_counts = {key: int(stats.get(key, 0)) for key in STATE_KEYS}
            family_classified = sum(state_counts.values())
            artifact_classified += family_classified
            classified_sources += family_classified
            generated_sources += state_counts["generated"]
            hard_sources += state_counts["hard"]
            below = int(stats.get("below_min_d", 0))
            below_min_d += below
            maximum_tested_d = max(maximum_tested_d, int(stats.get("max_d", 0)))
            if family in RAISING_FAMILIES:
                raising_classified += family_classified
                raising_generated += state_counts["generated"]
            family_rows.append({
                "artifact": filename,
                "family": family,
                "evaluated": int(stats["evaluated"]),
                "classified_at_or_above_min_d": family_classified,
                "below_min_d": below,
                "min_d": int(stats.get("min_d", 0)),
                "max_d": int(stats.get("max_d", 0)),
                "states": state_counts,
            })
        artifact_rows.append({
            "file": filename,
            "sha256": sha256(path),
            "evaluated_candidates": evaluations,
            "classified_at_or_above_min_d": artifact_classified,
            "hard_candidates": int(summary["hard_candidates"]),
            "target_3_4_falsifiers": int(summary["target_3_4_falsifiers"]),
            "largest_source_tested": summary["largest_source_tested"],
            "evaluated_stream_sha256": claim["digests"]["evaluated_stream_sha256"],
            "parameters": claim["parameters"],
        })
        for record in claim["verification_records"]:
            product = int(record["N"])
            previous = hard_records.get(product)
            if previous is not None and previous != record:
                raise ValueError(("conflicting_hard_record", product))
            hard_records[product] = record

    if target_falsifiers:
        raise ValueError(("unexpected_target_falsifier", target_falsifiers))
    if raising_classified != raising_generated:
        raise ValueError(("nongenerated_raising_source", raising_classified, raising_generated))

    slot_claim = next(
        claim for claim in claims if claim["parameters"].get("slot_sweep_budget") == 100000
    )
    baseline = slot_claim["self_test"]["known_hard"]
    by_d: dict[int, list[dict[str, object]]] = {}
    for record in hard_records.values():
        by_d.setdefault(int(record["d"]), []).append(record)
    extremal_table = []
    for d_value, records in sorted(by_d.items()):
        best = min(records, key=lambda row: (int(row["s"]), int(row["N"])))
        extremal_table.append({
            "d": d_value,
            "hard_count": len(records),
            "minimum_s": int(best["s"]),
            "maximum_deficit": max(int(row["deficit"]) for row in records),
            "representative_h": int(best["h"]),
            "representative_N": int(best["N"]),
            "template": best["template"],
            "ratio_B8": best["ratios"]["B8"],
            "target_3_4": best["target_3_4"],
            "taxonomy": best["taxonomy"],
        })

    best_d16 = min(
        (record for record in hard_records.values() if int(record["d"]) == 16),
        key=lambda row: (int(row["s"]), int(row["N"])),
    )
    script_names = (
        "C117_structural_power_falsifier.py",
        "C117_structural_power_verify.py",
        "C117_build_manifest.py",
    )
    return {
        "schema": "C117-aggregate-manifest-v1",
        "scope": {
            "candidate_evaluations_are_globally_deduplicated": False,
            "finite_nonfalsification_is_theorem": False,
            "target_3_4_falsifier_iff": "(s+8)^4 < d^3",
            "primary_ratio": "log(s+8)/log(d)",
            "alpha_gate": 1.0 / (2.0 * __import__("math").log(2.0)),
        },
        "totals": {
            "candidate_evaluations_not_deduplicated": candidate_evaluations,
            "closure_classified_at_or_above_run_threshold": classified_sources,
            "generated": generated_sources,
            "hard": hard_sources,
            "below_run_min_d_not_closure_classified": below_min_d,
            "target_3_4_falsifiers": target_falsifiers,
            "maximum_source_tested": maximum_source,
            "maximum_d_tested": maximum_tested_d,
            "independently_replayable_distinct_hard_records": len(hard_records),
        },
        "baseline_self_test": baseline,
        "sparse_extremal_table": extremal_table,
        "observed_structural_pattern": {
            "divisor_raising_sources_classified": raising_classified,
            "divisor_raising_sources_generated": raising_generated,
            "hard_survivors_all_from_fixed_d_slot_substitution": True,
            "best_d16_source": {
                "h": best_d16["h"],
                "d": best_d16["d"],
                "s": best_d16["s"],
                "pair_types": best_d16["taxonomy"]["pair_types"],
                "missing_root_states": best_d16["taxonomy"]["missing_root_states"],
            },
            "proof_obligation_not_claim": (
                "Explain why divisor-raising creates a generated-generated pair, or why "
                "a hard survivor has only a bounded set of nonstructural blocker roots."
            ),
        },
        "artifacts": artifact_rows,
        "family_rows": family_rows,
        "implementation_sha256": {
            filename: sha256(root / filename) for filename in script_names
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = build(Path(args.root))
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
