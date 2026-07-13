#!/usr/bin/env python3
"""Exact greedy deletion search inside certified admissible witnesses.

Every searched set is a subset of a literally admissible parent, so it is
admissible without relocating the exceptional sum.  Candidate deletions are
ranked by the exact change in the cleared centered-C20 margin.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from search_interval_lemmas import ceil_cuberoot, difference_counts, is_admissible


def metrics(points: tuple[int, ...], n: int) -> dict[str, Any]:
    if not points:
        raise ValueError("the empty subset is not searched")
    h = ceil_cuberoot(n * n)
    k = len(points)
    gaps = [right - left for left, right in zip(points, points[1:])]
    m_h = h + sum(min(h, gap) for gap in gaps)
    counts = difference_counts(points)
    if max(counts.values(), default=0) > 2:
        raise AssertionError("a certified admissible subset has nu(d) > 2")
    w_h = sum(
        (h - difference) * multiplicity
        for difference, multiplicity in counts.items()
        if difference < h
    )
    z_h = w_h - h * (h - 1) // 2
    d_h = sum(
        h - difference
        for difference, multiplicity in counts.items()
        if difference < h and multiplicity == 2
    )
    q_h = sum(h - difference for difference in range(1, h) if counts[difference] == 0)
    if z_h != d_h - q_h:
        raise AssertionError("centered convention mismatch")
    c20_margin = (
        6 * m_h * (h + 2 * w_h)
        - 8 * n * h * h
        - 9 * h**3
        - 9 * n * (k - 1) * h
    )
    g_h = n + h - 1 - m_h
    lg33_margin = (
        8 * n * z_h
        - 12 * h * h * g_h
        + 3 * h**3
        - 12 * h * h
        - 9 * n * (k - 1) * h
    )
    return {
        "A": list(points),
        "N": n,
        "H": h,
        "k": k,
        "M_H": m_h,
        "W_H": w_h,
        "D_H": d_h,
        "Q_H": q_h,
        "Z_H": z_h,
        "ambient_holes": g_h,
        "c20_cleared_margin": c20_margin,
        "lg33_cleared_margin": lg33_margin,
    }


def deletion_losses(points: tuple[int, ...], h: int) -> tuple[list[int], list[int]]:
    size = len(points)
    w_losses = [0] * size
    for right_index, right in enumerate(points):
        for left_index, left in enumerate(points[:right_index]):
            difference = right - left
            if difference < h:
                weight = h - difference
                w_losses[left_index] += weight
                w_losses[right_index] += weight

    m_losses = [0] * size
    if size == 1:
        m_losses[0] = h
        return w_losses, m_losses
    m_losses[0] = min(h, points[1] - points[0])
    m_losses[-1] = min(h, points[-1] - points[-2])
    for index in range(1, size - 1):
        left_gap = points[index] - points[index - 1]
        right_gap = points[index + 1] - points[index]
        m_losses[index] = (
            min(h, left_gap)
            + min(h, right_gap)
            - min(h, left_gap + right_gap)
        )
    return w_losses, m_losses


def greedy_delete(parent: tuple[int, ...], n: int) -> dict[str, Any]:
    current = metrics(parent, n)
    best = current
    steps: list[dict[str, int]] = []

    while len(current["A"]) > 1:
        points = tuple(current["A"])
        h = current["H"]
        w_losses, m_losses = deletion_losses(points, h)
        best_delta: int | None = None
        best_index: int | None = None
        best_margin: int | None = None
        for index, (w_loss, m_loss) in enumerate(zip(w_losses, m_losses)):
            new_product = (current["M_H"] - m_loss) * (
                h + 2 * (current["W_H"] - w_loss)
            )
            old_product = current["M_H"] * (h + 2 * current["W_H"])
            delta = 6 * (new_product - old_product) + 9 * n * h
            candidate_margin = current["c20_cleared_margin"] + delta
            if best_delta is None or delta > best_delta:
                best_delta = delta
                best_index = index
                best_margin = candidate_margin

        assert best_delta is not None and best_index is not None and best_margin is not None
        if best_delta <= 0:
            break
        removed = points[best_index]
        next_points = points[:best_index] + points[best_index + 1 :]
        next_metrics = metrics(next_points, n)
        if next_metrics["c20_cleared_margin"] != best_margin:
            raise AssertionError("incremental deletion margin mismatch")
        steps.append({"removed": removed, "delta": best_delta, "margin": best_margin})
        current = next_metrics
        if current["c20_cleared_margin"] > best["c20_cleared_margin"]:
            best = current

    if not is_admissible(tuple(best["A"])):
        raise AssertionError("subset of certified parent is not admissible")
    return {
        "parent_size": len(parent),
        "steps": steps,
        "local_optimum": current,
        "best": best,
    }


def load_parents(path: Path, minimum_size: int) -> list[tuple[str, int, tuple[int, ...]]]:
    parents: list[tuple[str, int, tuple[int, ...]]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            record = json.loads(line)
            if "A" not in record:
                continue
            points = tuple(record["A"])
            if len(points) < minimum_size:
                continue
            n = int(record.get("N", record.get("verification", {}).get("ambient_n")))
            identifier = str(record.get("sample_id", record.get("name", f"line-{line_number}")))
            parents.append((identifier, n, points))
    return parents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument("--minimum-size", type=int, default=12)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/certified_subset_search.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parents = load_parents(args.input, args.minimum_size)
    if args.limit:
        parents = parents[: args.limit]
    results = []
    for identifier, n, points in parents:
        search = greedy_delete(points, n)
        results.append({"id": identifier, "N": n, **search})
    results.sort(key=lambda item: item["best"]["c20_cleared_margin"], reverse=True)
    output = {
        "arithmetic": "integer",
        "input": str(args.input),
        "parent_count": len(results),
        "c20_failure_count": sum(item["best"]["c20_cleared_margin"] > 0 for item in results),
        "lg33_failure_count": sum(item["best"]["lg33_cleared_margin"] > 0 for item in results),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "parent_count": output["parent_count"],
                "c20_failure_count": output["c20_failure_count"],
                "lg33_failure_count": output["lg33_failure_count"],
                "best_id": results[0]["id"] if results else None,
                "best_margin": results[0]["best"]["c20_cleared_margin"] if results else None,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
