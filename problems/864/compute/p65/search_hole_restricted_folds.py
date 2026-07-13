#!/usr/bin/env python3
"""Exact search for the P65 hole-restricted shifted-sum fold bound.

All pair sums are unordered with diagonals.  The hole check allows every
repetition in x+y+z-w and is evaluated by an exact precomputed gap set.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[4]
P53_SCRIPT = ROOT / "problems/864/compute/p53/shifted_sum_overlap.py"


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for i, x in enumerate(values):
        for y in values[i:]:
            s = x + y
            if s in out:
                raise AssertionError(("repeated unordered sum", s, out[s], (x, y)))
            out[s] = (x, y)
    return out


def positive_difference_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for j, y in enumerate(values):
        for x in values[:j]:
            d = y - x
            if d in out:
                raise AssertionError(("repeated positive difference", d, out[d], (x, y)))
            out[d] = (x, y)
    return out


def sidon_rulers(width: int) -> Iterator[tuple[int, ...]]:
    """Every endpoint-normalized Sidon ruler in [0,width]."""
    chosen = [0]
    used: set[int] = set()

    def additions(value: int) -> tuple[int, ...] | None:
        ds = tuple(value - old for old in chosen)
        if len(ds) != len(set(ds)) or any(d in used for d in ds):
            return None
        return ds

    def rec(start: int) -> Iterator[tuple[int, ...]]:
        endpoint = additions(width)
        if endpoint is not None:
            yield tuple(chosen + [width])
        for value in range(start, width):
            ds = additions(value)
            if ds is None:
                continue
            chosen.append(value)
            used.update(ds)
            yield from rec(value + 1)
            used.difference_update(ds)
            chosen.pop()

    yield from rec(1)


def forbidden_gap_set(z: Sequence[int]) -> set[int]:
    """Positive g for which -g lies in 3Z-Z, repetitions included."""
    pair_sums = {x + y for i, x in enumerate(z) for y in z[i:]}
    triple_sums = {s + x for s in pair_sums for x in z}
    return {w - t for w in z for t in triple_sums if w > t}


def hole_holds(values: Sequence[int], b: int) -> bool:
    """Literal -b notin 3B-B, with all four variables allowed to repeat."""
    sums = set(unordered_sum_map(values))
    differences = {x - y for x in values for y in values}
    return all(-b - s not in differences for s in sums)


def fold_rows(z: Sequence[int], gamma: int, b: int) -> dict[str, object]:
    z = tuple(z)
    width = z[-1]
    values = tuple(gamma + x for x in z)
    h = gamma + width + 1
    p = len(z)
    sums_z = unordered_sum_map(z)
    collisions = []
    diagonal_types: Counter[str] = Counter()
    for low in sorted(sums_z):
        high = low + h
        if high not in sums_z:
            continue
        a0, a1 = sums_z[low]
        c0, c1 = sums_z[high]
        low_pair = (gamma + a0, gamma + a1)
        high_pair = (gamma + c0, gamma + c1)
        if not (low_pair[0] <= low_pair[1] < high_pair[0] <= high_pair[1]):
            raise AssertionError(("separation", values, h, low_pair, high_pair))
        if low_pair[0] == low_pair[1]:
            kind = "low_diagonal"
        elif high_pair[0] == high_pair[1]:
            kind = "high_diagonal"
        else:
            kind = "off_diagonal"
        diagonal_types[kind] += 1
        collisions.append({
            "low_sum": 2 * gamma + low,
            "high_sum": 2 * gamma + high,
            "low_pair": list(low_pair),
            "high_pair": list(high_pair),
            "type": kind,
        })
    delta = (3 * p * p - p + 2) // 2 - h
    return {
        "B": list(values), "Z": list(z), "p": p, "width": width,
        "gamma": gamma, "h": h, "b": b, "delta": delta,
        "hole": hole_holds(values, b),
        "C_S": len(collisions), "bound": 2 * p - 3,
        "excess": len(collisions) - (2 * p - 3),
        "collision_types": dict(sorted(diagonal_types.items())),
        "collisions": collisions,
    }


def scan_ruler(z: Sequence[int], source: str) -> dict[str, object]:
    z = tuple(z)
    if z[0] != 0 or len(set(z)) != len(z):
        raise AssertionError((source, z))
    unordered_sum_map(z)
    positive_difference_map(z)
    p, width = len(z), z[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = min(width - 1, baseline - width - 2)
    gaps = forbidden_gap_set(z)
    tested = holes = 0
    best: dict[str, object] | None = None
    failures: list[dict[str, object]] = []
    if max_gamma >= 0:
        sums = set(unordered_sum_map(z))
        for gamma in range(max_gamma + 1):
            h = width + gamma + 1
            c_s = sum(s + h in sums for s in sums)
            for b in (1, 2):
                tested += 1
                # 3(gamma+Z)-(gamma+Z)=2gamma+(3Z-Z).
                hole = b + 2 * gamma not in gaps
                if not hole:
                    continue
                holes += 1
                delta = baseline - h
                if delta <= 0:
                    raise AssertionError((source, gamma, b, delta))
                summary = {
                    "source": source, "p": p, "width": width,
                    "gamma": gamma, "h": h, "b": b, "delta": delta,
                    "C_S": c_s, "bound": 2 * p - 3,
                    "excess": c_s - (2 * p - 3), "Z": list(z),
                }
                rank = (summary["excess"], c_s, -p, -h, -b)
                if best is None or rank > (
                    best["excess"], best["C_S"], -best["p"],
                    -best["h"], -best["b"],
                ):
                    best = summary
                if c_s > 2 * p - 3:
                    exact = fold_rows(z, gamma, b)
                    if not exact["hole"]:
                        raise AssertionError(("gap-set hole mismatch", summary))
                    failures.append({"source": source, **exact})
    return {
        "source": source, "p": p, "width": width,
        "candidate_translations": tested,
        "hole_translations": holes,
        "best": best,
        "failures": failures,
    }


def load_dense_rulers() -> tuple[tuple[int, ...], ...]:
    spec = importlib.util.spec_from_file_location("p53_shifted", P53_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(P53_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(tuple(int(x) for x in row) for row in module.DENSE_RULERS)


def exhaustive(max_width: int) -> dict[str, object]:
    started = time.perf_counter()
    ruler_count = candidates = holes = 0
    failures: list[dict[str, object]] = []
    best: dict[str, object] | None = None
    by_width = []
    digest = hashlib.sha256()
    for width in range(1, max_width + 1):
        wr = wc = wh = 0
        for index, z in enumerate(sidon_rulers(width)):
            ruler_count += 1
            wr += 1
            digest.update(json.dumps(z, separators=(",", ":")).encode("ascii"))
            row = scan_ruler(z, f"W{width}-R{index}")
            candidates += int(row["candidate_translations"])
            holes += int(row["hole_translations"])
            wc += int(row["candidate_translations"])
            wh += int(row["hole_translations"])
            failures.extend(row["failures"])
            candidate = row["best"]
            if candidate is not None and (
                best is None or
                (candidate["excess"], candidate["C_S"], -candidate["p"], -candidate["h"])
                > (best["excess"], best["C_S"], -best["p"], -best["h"])
            ):
                best = candidate
        by_width.append({
            "width": width, "rulers": wr,
            "candidate_translations": wc, "hole_translations": wh,
        })
    return {
        "domain": f"all endpoint-normalized Sidon rulers of width <= {max_width}",
        "max_width": max_width, "rulers": ruler_count,
        "candidate_translations": candidates, "hole_translations": holes,
        "ruler_stream_sha256": digest.hexdigest(),
        "failure_count": len(failures), "failures": failures,
        "best": best, "by_width": by_width,
        "elapsed_seconds": time.perf_counter() - started,
    }


def dense() -> dict[str, object]:
    started = time.perf_counter()
    reports = []
    failures = []
    for index, base in enumerate(load_dense_rulers()):
        for orientation, z in (
            ("listed", base),
            ("reflected", tuple(base[-1] - x for x in reversed(base))),
        ):
            row = scan_ruler(z, f"dense-{index}-{orientation}")
            reports.append(row)
            failures.extend(row["failures"])
    return {
        "domain": "listed optimal rulers of orders 20..28, both orientations",
        "reports": reports, "failure_count": len(failures),
        "failures": failures, "elapsed_seconds": time.perf_counter() - started,
    }


def parent_subsets(max_delete: int) -> dict[str, object]:
    """Exact local deletion search around the P53 26-mark parent."""
    parent = (
        0, 1, 33, 83, 104, 110, 124, 163, 185, 200, 203, 249, 251,
        258, 314, 318, 343, 356, 386, 430, 440, 456, 464, 475, 487, 492,
    )
    internal = parent[1:-1]
    reports = []
    failures = []
    subset_count = 0
    started = time.perf_counter()
    for deleted_count in range(max_delete + 1):
        level_best = None
        level_holes = 0
        for deleted in combinations(internal, deleted_count):
            removed = set(deleted)
            z = tuple(x for x in parent if x not in removed)
            subset_count += 1
            row = scan_ruler(z, f"p53-parent-delete-{','.join(map(str, deleted))}")
            level_holes += int(row["hole_translations"])
            failures.extend(row["failures"])
            candidate = row["best"]
            if candidate is not None and (
                level_best is None or
                (candidate["excess"], candidate["C_S"], -candidate["h"])
                > (level_best["excess"], level_best["C_S"], -level_best["h"])
            ):
                level_best = candidate
        reports.append({
            "deleted_count": deleted_count,
            "subsets": sum(1 for _ in combinations(internal, deleted_count)),
            "hole_translations": level_holes, "best": level_best,
        })
    return {
        "domain": f"P53 26-mark parent, endpoints retained, <= {max_delete} deletions",
        "subsets": subset_count, "reports": reports,
        "failure_count": len(failures), "failures": failures,
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--parent-delete", type=int, default=5)
    parser.add_argument("--skip-exhaustive", action="store_true")
    parser.add_argument("--skip-parent", action="store_true")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "problems/864/compute/p65/hole_restricted_folds.json",
    )
    args = parser.parse_args()
    output: dict[str, object] = {
        "schema_version": 1, "arithmetic": "exact integers",
        "statement": "delta>0 and (-b notin 3B-B) imply C_S<=2p-3",
        "diagonals_included": True, "three_minus_one_repetitions_included": True,
        "dense": dense(),
    }
    if not args.skip_exhaustive:
        output["exhaustive"] = exhaustive(args.max_width)
    if not args.skip_parent:
        output["parent_subsets"] = parent_subsets(args.parent_delete)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        key: {
            "failure_count": value["failure_count"],
            "elapsed_seconds": value["elapsed_seconds"],
            **({"rulers": value["rulers"], "hole_translations": value["hole_translations"]}
               if key == "exhaustive" else {}),
            **({"subsets": value["subsets"]} if key == "parent_subsets" else {}),
        }
        for key, value in output.items()
        if key in {"dense", "exhaustive", "parent_subsets"}
    }, indent=2))


if __name__ == "__main__":
    main()
