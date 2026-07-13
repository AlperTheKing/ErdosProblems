#!/usr/bin/env python3
"""Exact archived-ruler search for dense loose fold triangles (P86).

All combinatorial decisions use Python integers.  Floating point is not used
for candidate acceptance or ranking.  The two search lanes are:

* every positive-defect endpoint translation of each archived Sidon ruler;
* every eligible q=2 parity lift followed by one same-parity insertion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p86/dense_loose_scan.json"
ARCHIVE_PATHS = (
    "problems/864/compute/p46/carry_statistics.json",
    "problems/864/compute/p53/counterexample_p25_h494.json",
    "problems/864/compute/p53/counterexample_p26_h494.json",
    "problems/864/compute/p53/dense_optimal_rulers_scan.json",
    "problems/864/compute/p54/audit_delta_positive_part.json",
    "problems/864/compute/p57/fold_repair_translation_scan.json",
    "problems/864/compute/p58/singer_q13_scan.json",
    "problems/864/compute/p60/audit_results.json",
    "problems/864/compute/p65/dense_subset_optimization.json",
    "problems/864/compute/p65/parent_subset_optimization.json",
    "problems/864/compute/p65/hole_restricted_folds.json",
    "problems/864/compute/p69/audit_results.json",
    "problems/864/compute/p79/global_shift_bound_audit.json",
    "problems/864/compute/p79/named_witness_audit.json",
    "problems/864/compute/p79/outer_codegree_audit.json",
)
LOCAL_KEEP = 32


@dataclass(frozen=True)
class BaseRuler:
    values: tuple[int, ...]
    sources: tuple[str, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ratio_text(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}"


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in out:
                raise ValueError(("repeated sum", total, out[total], (left, right)))
            out[total] = (left, right)
    return out


def positive_differences(values: Sequence[int]) -> set[int]:
    out: set[int] = set()
    for j, right in enumerate(values):
        for left in values[:j]:
            difference = right - left
            if difference in out:
                raise ValueError(("repeated difference", difference))
            out.add(difference)
    return out


def normalized_sidon(values: Iterable[int]) -> tuple[int, ...] | None:
    row = tuple(sorted(set(int(x) for x in values)))
    if len(row) < 3:
        return None
    row = tuple(x - row[0] for x in row)
    try:
        unordered_sum_map(row)
        positive_differences(row)
    except ValueError:
        return None
    return row


def iter_mark_arrays(obj: object, trail: str) -> Iterator[tuple[str, list[int]]]:
    if isinstance(obj, dict):
        tag_parts = []
        for key in ("kind", "source", "source_id"):
            value = obj.get(key)
            if isinstance(value, (str, int)):
                tag_parts.append(f"{key}={value}")
        tag = f"[{','.join(tag_parts)}]" if tag_parts else ""
        for key, value in obj.items():
            child = f"{trail}/{key}{tag}"
            if (
                key in {"B", "Z", "ruler", "marks"}
                and isinstance(value, list)
                and len(value) >= 3
                and all(isinstance(x, int) and not isinstance(x, bool) for x in value)
            ):
                yield child, value
            yield from iter_mark_arrays(value, child)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from iter_mark_arrays(value, f"{trail}/{index}")


def load_archives() -> tuple[list[BaseRuler], list[dict[str, str | int]]]:
    by_values: dict[tuple[int, ...], set[str]] = {}
    manifests: list[dict[str, str | int]] = []
    for relative in ARCHIVE_PATHS:
        path = ROOT / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        arrays = 0
        accepted = 0
        for source, raw in iter_mark_arrays(payload, relative):
            arrays += 1
            ruler = normalized_sidon(raw)
            if ruler is None:
                continue
            accepted += 1
            by_values.setdefault(ruler, set()).add(source)
            reflected = tuple(ruler[-1] - x for x in reversed(ruler))
            by_values.setdefault(reflected, set()).add(source + "/reflected")
        manifests.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "mark_arrays": arrays,
                "sidon_orientations_accepted": accepted,
            }
        )
    bases = [
        BaseRuler(values, tuple(sorted(sources)))
        for values, sources in sorted(by_values.items(), key=lambda item: item[0])
    ]
    return bases, manifests


def fold_edges(
    values: Sequence[int], h: int
) -> tuple[list[tuple[int, int, int, int]], dict[int, tuple[int, int]]]:
    sums = unordered_sum_map(values)
    edges: list[tuple[int, int, int, int]] = []
    for low in sorted(sums):
        if low + h not in sums:
            continue
        a, c = sums[low]
        u, v = sums[low + h]
        if not (a <= c < u <= v):
            raise AssertionError(("fold order", a, c, u, v, h))
        edges.append((a, c, u, v))
    return edges, sums


def loose_triangle_data(
    edges: Sequence[tuple[int, int, int, int]], witness_limit: int = 3
) -> tuple[int, list[list[list[int]]]]:
    by_a_c: dict[int, list[tuple[int, int]]] = {}
    by_a_u: dict[int, list[tuple[int, int]]] = {}
    cu: dict[tuple[int, int], int] = {}
    for edge_id, (a, c, u, _v) in enumerate(edges):
        by_a_c.setdefault(a, []).append((c, edge_id))
        by_a_u.setdefault(a, []).append((u, edge_id))
        if (c, u) in cu:
            raise AssertionError(("nonlinear CU projection", c, u))
        cu[c, u] = edge_id

    count = 0
    witnesses: list[list[list[int]]] = []
    for a in sorted(set(by_a_c) & set(by_a_u)):
        for c, edge_ac in by_a_c[a]:
            for u, edge_au in by_a_u[a]:
                edge_cu = cu.get((c, u))
                if edge_cu is None:
                    continue
                ids = (edge_ac, edge_au, edge_cu)
                if ids[0] == ids[1] == ids[2]:
                    continue
                if len(set(ids)) != 3:
                    raise AssertionError(("linearity violation", ids))
                count += 1
                if len(witnesses) < witness_limit:
                    witnesses.append([list(edges[index]) for index in ids])
    return count, witnesses


def literal_hole(values: Sequence[int], b: int) -> bool:
    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    return differences.isdisjoint(total + b for total in sums)


def audit_candidate(
    values_input: Iterable[int], h: int, b: int, source: str,
    transform: str, witness_limit: int = 3,
) -> dict[str, object]:
    values = tuple(sorted(int(x) for x in values_input))
    if not values or len(set(values)) != len(values):
        raise AssertionError("invalid values")
    if values[-1] != h - 1 or values[0] < 0 or b not in (1, 2):
        raise AssertionError(("endpoint", values[:1], values[-1:], h, b))
    p = len(values)
    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    edges, _ = fold_edges(values, h)
    triangles, witnesses = loose_triangle_data(edges, witness_limit)
    delta_numerator = 3 * p * p - p + 2 - 2 * h
    if delta_numerator <= 0 or delta_numerator % 2:
        raise AssertionError(("defect", delta_numerator))
    if not differences.isdisjoint(total + b for total in sums):
        raise AssertionError("literal hole fails")
    return {
        "source": source,
        "transform": transform,
        "B": list(values),
        "p": p,
        "h": h,
        "b": b,
        "delta": delta_numerator // 2,
        "C_S": len(edges),
        "T_F": triangles,
        "C_S_over_p2": ratio_text(len(edges), p * p),
        "T_F_over_p3": ratio_text(triangles, p * p * p),
        "loose_triangle_witnesses_ac_au_cu": witnesses,
    }


def masks_for_ruler(values: Sequence[int]) -> tuple[int, int]:
    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    sum_mask = sum(1 << total for total in sums)
    difference_mask = sum(1 << difference for difference in differences)
    return sum_mask, difference_mask


def translation_worker(base: BaseRuler) -> dict[str, object]:
    z = base.values
    p, width = len(z), z[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = min(width - 1, baseline - width - 2)
    if max_gamma < 0:
        return {"tested": 0, "folded": 0, "admissible": 0, "records": []}
    sum_mask, difference_mask = masks_for_ruler(z)
    records = []
    tested = folded = admissible = 0
    source = " | ".join(base.sources[:4])
    if len(base.sources) > 4:
        source += f" | +{len(base.sources) - 4} sources"
    for gamma in range(max_gamma + 1):
        tested += 2
        h = width + gamma + 1
        c_s = (sum_mask & (sum_mask >> h)).bit_count()
        if c_s == 0:
            continue
        folded += 2
        for b in (1, 2):
            shift = 2 * gamma + b
            if ((sum_mask << shift) & difference_mask) != 0:
                continue
            admissible += 1
            values = tuple(x + gamma for x in z)
            records.append(
                audit_candidate(values, h, b, source, f"translate gamma={gamma}")
            )
    return {
        "tested": tested,
        "folded": folded,
        "admissible": admissible,
        "records": sort_records(records)[:LOCAL_KEEP],
    }


def insertion_is_sidon(values: Sequence[int], existing_sums: set[int], x: int) -> bool:
    new_sums = [x + value for value in values]
    new_sums.append(2 * x)
    return len(new_sums) == len(set(new_sums)) and existing_sums.isdisjoint(new_sums)


def insertion_worker(base: BaseRuler) -> dict[str, object]:
    z = base.values
    p, width = len(z), z[-1]
    new_p = p + 1
    baseline = (3 * new_p * new_p - new_p + 2) // 2
    max_g = min(width, (baseline - 1) // 2 - width)
    if max_g < 1:
        return {"tested": 0, "sidon": 0, "records": []}
    records = []
    tested = sidon = 0
    source = " | ".join(base.sources[:4])
    if len(base.sources) > 4:
        source += f" | +{len(base.sources) - 4} sources"
    for g in range(1, max_g + 1):
        c_base = tuple(value + g for value in z)
        h0 = width + g
        existing = set(unordered_sum_map(c_base))
        occupied = set(c_base)
        for x in range(1, h0):
            if x in occupied:
                continue
            tested += 1
            if not insertion_is_sidon(c_base, existing, x):
                continue
            sidon += 1
            c = tuple(sorted(c_base + (x,)))
            # q=2, B=2C-1.  All marks are odd, so the b=1 hole is automatic.
            values = tuple(2 * value - 1 for value in c)
            h = 2 * h0
            records.append(
                audit_candidate(
                    values, h, 1, source,
                    f"q=2 parity lift; g={g}; inserted_C={x}",
                )
            )
    return {
        "tested": tested,
        "sidon": sidon,
        "records": sort_records(records)[:LOCAL_KEEP],
    }


def sort_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    from functools import cmp_to_key

    def compare(left: dict[str, object], right: dict[str, object]) -> int:
        lp, rp = int(left["p"]), int(right["p"])
        lhs = int(left["T_F"]) * rp**3
        rhs = int(right["T_F"]) * lp**3
        if lhs != rhs:
            return -1 if lhs > rhs else 1
        lhs = int(left["C_S"]) * rp**2
        rhs = int(right["C_S"]) * lp**2
        if lhs != rhs:
            return -1 if lhs > rhs else 1
        left_tail = (int(left["delta"]), str(left["source"]), str(left["transform"]))
        right_tail = (int(right["delta"]), str(right["source"]), str(right["transform"]))
        return -1 if left_tail > right_tail else (1 if left_tail < right_tail else 0)

    return sorted(records, key=cmp_to_key(compare))


def summarize_records(
    records: list[dict[str, object]], limit: int, total_count: int
) -> dict[str, object]:
    ordered = sort_records(records)
    by_p: dict[int, dict[str, object]] = {}
    for row in ordered:
        p = int(row["p"])
        if p not in by_p:
            by_p[p] = row
    return {
        "record_count": total_count,
        "extremal_records_retained_before_global_ranking": len(records),
        "top_by_T_F_over_p3": ordered[:limit],
        "best_by_p": [by_p[p] for p in sorted(by_p)],
    }


def run_parallel(
    worker, bases: Sequence[BaseRuler], workers: int
) -> list[dict[str, object]]:
    if workers == 1:
        return [worker(base) for base in bases]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, bases, chunksize=1))


def run_search(workers: int, top: int) -> dict[str, object]:
    bases, manifests = load_archives()
    translation_rows = run_parallel(translation_worker, bases, workers)
    insertion_bases = [
        base for base in bases
        if len(base.values) <= 40
        and any("/p46/" in source or "/p53/" in source for source in base.sources)
    ]
    insertion_rows = run_parallel(insertion_worker, insertion_bases, workers)

    translation_records = [record for row in translation_rows for record in row["records"]]
    insertion_records = [record for row in insertion_rows for record in row["records"]]
    result: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact Python integers for all combinatorial decisions and rankings",
        "command": (
            "python problems/864/compute/p86/dense_loose_search.py search "
            f"--workers {workers} --top {top} --output "
            "problems/864/compute/p86/dense_loose_scan.json"
        ),
        "worker_cap": workers,
        "definitions": {
            "C_S": "number of unordered sum-support pairs s,s+h",
            "T_F": "noncanonical triangles in the labelled A-C-U shadow graph",
            "delta": "(3p^2-p+2)/2-h",
            "literal_hole": "positive differences disjoint from B+B+b",
        },
        "archive_manifest": manifests,
        "unique_oriented_sidon_bases": len(bases),
        "translation_scan": {
            "domain": "all positive-defect gamma with nonzero folds, both b=1,2",
            "base_count": len(bases),
            "tested_b_candidates": sum(int(row["tested"]) for row in translation_rows),
            "folded_b_candidates": sum(int(row["folded"]) for row in translation_rows),
            "admissible_candidates": sum(int(row["admissible"]) for row in translation_rows),
            **summarize_records(
                translation_records, top,
                sum(int(row["admissible"]) for row in translation_rows),
            ),
        },
        "one_insertion_scan": {
            "domain": (
                "all archived bases with p<=40; every q=2 positive-defect g and "
                "every same-parity interior insertion; b=1"
            ),
            "base_count": len(insertion_bases),
            "tested_insertions": sum(int(row["tested"]) for row in insertion_rows),
            "sidon_insertions": sum(int(row["sidon"]) for row in insertion_rows),
            **summarize_records(
                insertion_records, top,
                sum(int(row["sidon"]) for row in insertion_rows),
            ),
        },
    }
    # This fixed regression witness validates the triangle convention against P82.
    # Load the canonical 26-mark pre-lift certificate used by P75.
    certificate = json.loads(
        (ROOT / "problems/864/compute/p53/counterexample_p26_h494.json").read_text()
    )
    raw = certificate.get("hypotheses", {}).get("B", certificate.get("B"))
    if not isinstance(raw, list):
        raise AssertionError("missing p53 p26 certificate B")
    # P75 applies q=2 and offset 1 to the h=494 certificate.
    lifted = [2 * int(x) + 1 for x in raw]
    result["regression_P75"] = audit_candidate(
        lifted, 988, 1, "p53/counterexample_p26_h494.json", "P75 q=2 lift"
    )
    if result["regression_P75"]["C_S"] != 51 or result["regression_P75"]["T_F"] != 25:
        raise AssertionError(result["regression_P75"])
    return result


def verify_report(path: Path) -> dict[str, object]:
    path = path.resolve()
    payload = json.loads(path.read_text(encoding="ascii"))
    checked = 0
    for section in ("translation_scan", "one_insertion_scan"):
        rows = payload[section]["top_by_T_F_over_p3"] + payload[section]["best_by_p"]
        for row in rows:
            fresh = audit_candidate(
                row["B"], int(row["h"]), int(row["b"]),
                str(row["source"]), str(row["transform"]),
            )
            for key in ("p", "delta", "C_S", "T_F", "C_S_over_p2", "T_F_over_p3"):
                if fresh[key] != row[key]:
                    raise AssertionError((section, key, fresh[key], row[key]))
            checked += 1
    row = payload["regression_P75"]
    fresh = audit_candidate(row["B"], int(row["h"]), int(row["b"]), "verify", "verify")
    if fresh["C_S"] != 51 or fresh["T_F"] != 25:
        raise AssertionError(fresh)
    checked += 1
    return {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "input": str(path.relative_to(ROOT)),
        "input_sha256": sha256_file(path),
        "records_checked": checked,
        "status": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    search = subparsers.add_parser("search")
    search.add_argument("--workers", type=int, default=16)
    search.add_argument("--top", type=int, default=25)
    search.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--input", type=Path, default=DEFAULT_OUTPUT)
    verify.add_argument(
        "--output", type=Path,
        default=ROOT / "problems/864/compute/p86/verification.json",
    )
    args = parser.parse_args()
    if args.command == "search":
        workers = max(1, min(int(args.workers), 16))
        payload = run_search(workers, max(1, int(args.top)))
        output = args.output
    else:
        payload = verify_report(args.input)
        output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
