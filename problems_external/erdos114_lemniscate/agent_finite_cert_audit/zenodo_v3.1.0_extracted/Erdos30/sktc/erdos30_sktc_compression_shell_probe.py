#!/usr/bin/env python3
"""
Erdos #30 SKTC v3 compression-shell probe.

The v2 probe showed that loose random Sidon controls confound the question.
This v3 probe instead compares fixed-k Sidon rulers in shells around the
optimal diameter:

  D*, D* + 1, ..., D* + s

It reuses the v2 exact optimality receipt when supplied, then enumerates all
canonical Sidon/Golomb rulers at each shell diameter.

Claim ceiling:
  - finite compression-gradient screening only;
  - not evidence for the asymptotic Erdos #30 conjecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import erdos30_sktc_multiscale_probe as v2


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def metric_value(record: dict[str, Any], metric: str) -> float:
    if metric == "dyadic":
        return float(record["centered_dyadic_interval_discrepancy"]["value"])
    if metric == "residue":
        return float(record["centered_prime_power_residue_discrepancy"]["value"])
    if metric == "bohr":
        return float(record["centered_bohr_cell_discrepancy"]["value"])
    return float(record[metric])


def summarize_observables(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"count": 0}
    metrics = [
        "pair_load",
        "compression_delta_k2_minus_diameter",
        "centered_difference_histogram_l2",
        "centered_incidence_tensor_spectral_norm_over_sqrt_pairs",
        "dyadic",
        "residue",
        "bohr",
    ]
    out: dict[str, Any] = {"count": len(records)}
    for metric in metrics:
        values = [metric_value(record, metric) for record in records]
        out[metric] = {
            "min": min(values),
            "mean": mean(values),
            "max": max(values),
        }
    return out


def linear_slope(points: list[tuple[int, float]]) -> float | None:
    if len(points) < 2:
        return None
    xs = [float(x) for x, _ in points]
    ys = [float(y) for _, y in points]
    xbar = mean(xs)
    ybar = mean(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom == 0:
        return None
    return sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom


def load_v2_optimal_receipt(path: Path | None) -> tuple[dict[int, int], dict[int, list[list[int]]], dict[int, dict[str, Any]]]:
    diameters: dict[int, int] = {}
    marks_by_k: dict[int, list[list[int]]] = {}
    receipts: dict[int, dict[str, Any]] = {}
    if path is None or not path.exists():
        return diameters, marks_by_k, receipts
    data = json.loads(path.read_text())
    for receipt in data.get("search_receipts", []):
        k = int(receipt["k"])
        diameters[k] = int(receipt["diameter"])
        receipts[k] = receipt
    for record in data.get("records", []):
        if record.get("family") != "exact_canonical_optimal":
            continue
        k = int(record["k"])
        marks_by_k.setdefault(k, []).append(list(record["marks"]))
    return diameters, marks_by_k, receipts


def get_optimal_data(
    k: int,
    v2_diameters: dict[int, int],
    v2_marks_by_k: dict[int, list[list[int]]],
    v2_receipts: dict[int, dict[str, Any]],
) -> tuple[int, list[list[int]], dict[str, Any]]:
    if k in v2_diameters and k in v2_marks_by_k:
        receipt = dict(v2_receipts.get(k, {}))
        receipt["source"] = "v2_results_receipt"
        return v2_diameters[k], v2_marks_by_k[k], receipt
    rulers, receipt_obj = v2.all_optimal_rulers(k)
    receipt = asdict(receipt_obj)
    receipt["source"] = "computed_in_v3"
    return receipt_obj.diameter, rulers, receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=10)
    parser.add_argument("--shell-width", type=int, default=5)
    parser.add_argument("--max-q", type=int, default=64)
    parser.add_argument("--seed", type=int, default=20260502)
    parser.add_argument("--negative-control-samples", type=int, default=3)
    parser.add_argument("--negative-control-attempts", type=int, default=2000)
    parser.add_argument("--v2-results", type=Path, default=Path("results/erdos30_sktc_multiscale_v2_RESULTS.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.max_k > 10:
        raise SystemExit("Local exact compression-shell enumeration is capped at max_k <= 10 for this probe.")

    rng = random.Random(args.seed)
    v2_diameters, v2_marks_by_k, v2_receipts = load_v2_optimal_receipt(args.v2_results)

    shell_summaries: list[dict[str, Any]] = []
    shell_records: list[dict[str, Any]] = []
    negative_records: list[dict[str, Any]] = []
    optimal_receipts: list[dict[str, Any]] = []
    shell_search_receipts: list[dict[str, Any]] = []

    for k in range(2, args.max_k + 1):
        optimal_diameter, optimal_rulers, optimal_receipt = get_optimal_data(
            k, v2_diameters, v2_marks_by_k, v2_receipts
        )
        optimal_receipts.append(optimal_receipt)

        for delta in range(0, args.shell_width + 1):
            diameter = optimal_diameter + delta
            started = time.perf_counter()
            if delta == 0:
                rulers = optimal_rulers
                nodes = 0
                source = "v2_optimal_records" if optimal_receipt.get("source") == "v2_results_receipt" else "computed_optimal_records"
            else:
                rulers, nodes = v2.enumerate_fixed_diameter(k, diameter, stop_after_first=False)
                source = "fixed_diameter_exact_enumeration"
            elapsed = time.perf_counter() - started

            records = []
            for marks in rulers:
                obs = asdict(v2.observable_record("compression_shell_sidon", marks, args.max_q))
                obs.update({
                    "shell_delta": delta,
                    "optimal_diameter": optimal_diameter,
                    "shell_diameter": diameter,
                    "shell_source": source,
                })
                records.append(obs)
                shell_records.append(obs)

            negative_controls = v2.random_non_sidon_controls(
                k,
                diameter,
                sample_count=args.negative_control_samples,
                rng=rng,
                attempts=args.negative_control_attempts,
            )
            neg_records = []
            for marks in negative_controls:
                obs = asdict(v2.observable_record("same_shell_non_sidon_negative_control", marks, args.max_q))
                obs.update({
                    "shell_delta": delta,
                    "optimal_diameter": optimal_diameter,
                    "shell_diameter": diameter,
                    "shell_source": "random_same_shell_negative_control",
                })
                neg_records.append(obs)
                negative_records.append(obs)

            summary = {
                "k": k,
                "optimal_diameter": optimal_diameter,
                "shell_delta": delta,
                "shell_diameter": diameter,
                "sidon_ruler_count": len(records),
                "negative_control_count": len(neg_records),
                "negative_control_rejected_count": sum(1 for record in neg_records if not record["collision_certificate_accepts"]),
                "search_nodes": nodes,
                "seconds": elapsed,
                "source": source,
                "sidon_summary": summarize_observables(records),
                "negative_summary": summarize_observables(neg_records),
            }
            shell_summaries.append(summary)
            shell_search_receipts.append({
                "k": k,
                "optimal_diameter": optimal_diameter,
                "shell_delta": delta,
                "shell_diameter": diameter,
                "sidon_ruler_count": len(records),
                "search_nodes": nodes,
                "seconds": elapsed,
                "source": source,
            })

    metrics = [
        "pair_load",
        "centered_difference_histogram_l2",
        "centered_incidence_tensor_spectral_norm_over_sqrt_pairs",
        "dyadic",
        "residue",
        "bohr",
    ]
    slopes_by_k: dict[str, Any] = {}
    for k in range(2, args.max_k + 1):
        summaries = [summary for summary in shell_summaries if summary["k"] == k and summary["sidon_ruler_count"] > 0]
        slopes_by_k[str(k)] = {}
        for metric in metrics:
            points = [
                (summary["shell_delta"], float(summary["sidon_summary"][metric]["mean"]))
                for summary in summaries
                if metric in summary["sidon_summary"]
            ]
            slopes_by_k[str(k)][metric] = {
                "points": points,
                "slope_per_shell_delta": linear_slope(points),
                "delta0_value": points[0][1] if points else None,
                "last_shell_value": points[-1][1] if points else None,
            }

    payload = {
        "probe": "erdos30_sktc_compression_shell_v3",
        "claim_ceiling": "finite compression-gradient screening only; not asymptotic theorem evidence",
        "max_k": args.max_k,
        "shell_width": args.shell_width,
        "seed": args.seed,
        "max_q": args.max_q,
        "v2_results_source": str(args.v2_results),
        "optimal_receipts": optimal_receipts,
        "shell_search_receipts": shell_search_receipts,
        "shell_summaries": shell_summaries,
        "slopes_by_k": slopes_by_k,
        "negative_control_rejection": {
            "count": len(negative_records),
            "rejected": sum(1 for record in negative_records if not record["collision_certificate_accepts"]),
        },
        "records": shell_records,
        "negative_control_records": negative_records,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.out.write_text(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    args.out.with_suffix(args.out.suffix + ".sha256").write_text(f"{sha}  {args.out}\n")
    print(f"Wrote {args.out}")
    print(f"sha256 {sha}")


if __name__ == "__main__":
    main()
