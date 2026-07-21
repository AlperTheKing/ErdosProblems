#!/usr/bin/env python3
"""Independent slow reference for the manifest E lanes.

This implementation intentionally uses Python ``Fraction`` and ``math.isqrt``
instead of sharing arithmetic code with the C++ engine.  Its finite domain is
the same: positive squarefree kappa, integral precursor points P=(x,y), and
the closed x box supplied on the command line.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


MANIFEST_MAX_X = 1 << 20
MANIFEST_MAX_KAPPA = 1024
MAX_SECONDS = 8 * 60 * 60
ENGINE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PointRecord:
    kappa: int
    x: int
    y: int
    root_minus: Fraction
    root_center: Fraction
    root_plus: Fraction

    @property
    def doubled_x(self) -> Fraction:
        return self.root_center * self.root_center


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".tmp-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as output:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def is_squarefree(value: int) -> bool:
    if value <= 0:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % (divisor * divisor) == 0:
            return False
        divisor += 1
    return True


def make_point_record(kappa: int, x: int, y: int) -> PointRecord | None:
    denominator = 2 * y
    center_numerator = x * x + kappa * kappa
    minus_numerator = x * x - 2 * kappa * x - kappa * kappa
    plus_numerator = x * x + 2 * kappa * x - kappa * kappa
    if not center_numerator or not minus_numerator or not plus_numerator:
        return None
    record = PointRecord(
        kappa=kappa,
        x=x,
        y=y,
        root_minus=abs(Fraction(minus_numerator, denominator)),
        root_center=abs(Fraction(center_numerator, denominator)),
        root_plus=abs(Fraction(plus_numerator, denominator)),
    )
    X = record.doubled_x
    if record.root_minus**2 != X - kappa:
        raise AssertionError("reference X-kappa root identity failed")
    if record.root_plus**2 != X + kappa:
        raise AssertionError("reference X+kappa root identity failed")
    if X - kappa <= 0:
        raise AssertionError("reference accepted nonpositive X-kappa")
    return record


def fraction_json(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def inventory_record(point: PointRecord) -> dict[str, Any]:
    X = point.doubled_x
    return {
        "kappa": point.kappa,
        "precursor_x": point.x,
        "precursor_y": point.y,
        "x2_num": str(X.numerator),
        "x2_den": str(X.denominator),
        "root_minus_num": str(point.root_minus.numerator),
        "root_minus_den": str(point.root_minus.denominator),
        "root_center_num": str(point.root_center.numerator),
        "root_center_den": str(point.root_center.denominator),
        "root_plus_num": str(point.root_plus.numerator),
        "root_plus_den": str(point.root_plus.denominator),
    }


def canonical_matrix(m: int, b: int, c: int) -> list[int]:
    center = m * m
    return [
        center - b,
        center + b + c,
        center - c,
        center + b - c,
        center,
        center - b + c,
        center + c,
        center - b - c,
        center + b,
    ]


def reconstruct_candidate(
    low: PointRecord, middle: PointRecord, high: PointRecord
) -> dict[str, Any] | None:
    rational_roots = [
        low.root_center,
        high.root_plus,
        middle.root_minus,
        high.root_minus,
        middle.root_center,
        low.root_plus,
        middle.root_plus,
        low.root_minus,
        high.root_center,
    ]
    clearing = math.lcm(*(root.denominator for root in rational_roots))
    roots = [root.numerator * (clearing // root.denominator) for root in rational_roots]
    primitive = math.gcd(*roots)
    roots = [root // primitive for root in roots]
    m = roots[4]
    center = m * m
    b = center - roots[0] * roots[0]
    c = center - roots[2] * roots[2]
    if b <= 0 or c <= 0 or b == c:
        return None
    b, c = max(b, c), min(b, c)
    matrix = canonical_matrix(m, b, c)
    if any(value <= 0 for value in matrix) or len(set(matrix)) != 9:
        return None
    matrix_roots = [math.isqrt(value) for value in matrix]
    if any(root * root != value for root, value in zip(matrix_roots, matrix)):
        return None
    lines = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]
    sums = [sum(matrix[index] for index in line) for line in lines]
    if len(set(sums)) != 1:
        return None
    return {
        "kind": "E-W",
        "kappa": low.kappa,
        "msq_d": {"m": m, "b": b, "c": c},
        "clearing_denominator": str(clearing),
        "primitive_gcd": str(primitive),
        "precursors": [
            {
                "x": point.x,
                "y": point.y,
                "sqrt_x_minus_kappa": fraction_json(point.root_minus),
                "sqrt_x": fraction_json(point.root_center),
                "sqrt_x_plus_kappa": fraction_json(point.root_plus),
            }
            for point in (low, middle, high)
        ],
        "doubled_x": [fraction_json(point.doubled_x) for point in (low, middle, high)],
        "matrix_values": matrix,
        "matrix_roots": matrix_roots,
    }


def run_required_verifiers(
    candidate: dict[str, Any],
    out_dir: Path,
    python: str,
    scalar_verifier: Path,
    independent_verifier: Path,
) -> dict[str, Any]:
    candidate_path = out_dir / "candidate.json"
    matrix_path = out_dir / "candidate_matrix.txt"
    scalar_stdout = out_dir / "scalar_verify.json"
    scalar_stderr = out_dir / "scalar_verify.stderr.txt"
    independent_stdout = out_dir / "independent_verify.json"
    independent_stderr = out_dir / "independent_verify.stderr.txt"
    atomic_write_text(candidate_path, json.dumps(candidate, sort_keys=True) + "\n")
    atomic_write_text(
        matrix_path, " ".join(str(value) for value in candidate["matrix_values"]) + "\n"
    )
    with scalar_stdout.open("w", encoding="utf-8") as stdout, scalar_stderr.open(
        "w", encoding="utf-8"
    ) as stderr:
        scalar = subprocess.run(
            [python, str(scalar_verifier), "--input", str(candidate_path)],
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    with independent_stdout.open(
        "w", encoding="utf-8"
    ) as stdout, independent_stderr.open("w", encoding="utf-8") as stderr:
        independent = subprocess.run(
            [str(independent_verifier), "--file", str(matrix_path)],
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    return {
        "scalar_exit": scalar.returncode,
        "independent_exit": independent.returncode,
        "candidate_path": str(candidate_path),
        "matrix_path": str(matrix_path),
        "scalar_stdout": str(scalar_stdout),
        "independent_stdout": str(independent_stdout),
    }


def lane_bounds(lane: str) -> tuple[int, int]:
    if len(lane) != 3 or not lane.startswith("E") or not lane[1:].isdigit():
        raise ValueError("lane must be E01 through E16")
    number = int(lane[1:])
    if not 1 <= number <= 16:
        raise ValueError("lane must be E01 through E16")
    return 1 + (number - 1) * 64, number * 64


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane")
    parser.add_argument("--kappa-min", type=int)
    parser.add_argument("--kappa-max", type=int)
    parser.add_argument("--x-bound", type=int, required=True)
    parser.add_argument("--chunk-count", type=int, default=1)
    parser.add_argument("--chunk-index", type=int, default=0)
    parser.add_argument("--max-seconds", type=float, default=float(MAX_SECONDS))
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--emit-inventory", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--scalar-verifier", type=Path, default=ENGINE_DIR / "verify_scalar.py")
    parser.add_argument(
        "--independent-verifier",
        type=Path,
        default=ENGINE_DIR / "verify_independent.exe",
    )
    args = parser.parse_args(argv)
    if args.lane:
        expected = lane_bounds(args.lane)
        if args.kappa_min is not None and args.kappa_min != expected[0]:
            parser.error("kappa-min conflicts with lane")
        if args.kappa_max is not None and args.kappa_max != expected[1]:
            parser.error("kappa-max conflicts with lane")
        args.kappa_min, args.kappa_max = expected
    if args.kappa_min is None or args.kappa_max is None:
        parser.error("supply --lane or both --kappa-min and --kappa-max")
    if not 1 <= args.kappa_min <= args.kappa_max <= MANIFEST_MAX_KAPPA:
        parser.error("require 1 <= kappa-min <= kappa-max <= 1024")
    if not 0 <= args.x_bound <= MANIFEST_MAX_X:
        parser.error("require 0 <= x-bound <= 2^20")
    if not 1 <= args.chunk_count <= 64 or not 0 <= args.chunk_index < args.chunk_count:
        parser.error("invalid chunk count/index")
    if not 0 < args.max_seconds <= MAX_SECONDS:
        parser.error("require 0 < max-seconds <= 28800")
    return args


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    started_utc = utc_now()
    started = time.monotonic()
    counts = {
        "kappas_selected": 0,
        "kappas_completed": 0,
        "x_tested": 0,
        "integral_points": 0,
        "distinct_doubled_x": 0,
        "ap_endpoint_pairs": 0,
        "ap_triples": 0,
        "candidates_reconstructed": 0,
        "verifier_attempts": 0,
    }
    selected = [
        kappa
        for kappa in range(args.kappa_min, args.kappa_max + 1)
        if is_squarefree(kappa)
        and (kappa - args.kappa_min) % args.chunk_count == args.chunk_index
    ]
    counts["kappas_selected"] = len(selected)
    inventory: list[dict[str, Any]] = []
    status = "NO_HIT"
    verification: dict[str, Any] | None = None
    error: str | None = None

    try:
        for kappa in selected:
            deduplicated: dict[Fraction, PointRecord] = {}
            timed_out = False
            for x in range(-args.x_bound, args.x_bound + 1):
                counts["x_tested"] += 1
                if counts["x_tested"] & 0xFFFF == 0 and time.monotonic() - started >= args.max_seconds:
                    status = "TIMEOUT_INCOMPLETE"
                    timed_out = True
                    break
                rhs = x * (x * x - kappa * kappa)
                if rhs <= 0:
                    continue
                y = math.isqrt(rhs)
                if y == 0 or y * y != rhs:
                    continue
                counts["integral_points"] += 1
                point = make_point_record(kappa, x, y)
                if point is None:
                    continue
                previous = deduplicated.get(point.doubled_x)
                if previous is None or point.x < previous.x:
                    deduplicated[point.doubled_x] = point
            if timed_out:
                break
            points = sorted(deduplicated.values(), key=lambda point: point.doubled_x)
            counts["distinct_doubled_x"] += len(points)
            if args.emit_inventory:
                inventory.extend(inventory_record(point) for point in points)
            index_by_x = {point.doubled_x: index for index, point in enumerate(points)}
            stop = False
            for low in range(len(points)):
                for high in range(low + 1, len(points)):
                    counts["ap_endpoint_pairs"] += 1
                    midpoint = (points[low].doubled_x + points[high].doubled_x) / 2
                    middle = index_by_x.get(midpoint)
                    if middle is None or not low < middle < high:
                        continue
                    counts["ap_triples"] += 1
                    candidate = reconstruct_candidate(points[low], points[middle], points[high])
                    if candidate is None:
                        continue
                    counts["candidates_reconstructed"] += 1
                    counts["verifier_attempts"] += 1
                    verification = run_required_verifiers(
                        candidate,
                        args.out_dir,
                        args.python,
                        args.scalar_verifier,
                        args.independent_verifier,
                    )
                    if verification["scalar_exit"] == 0 and verification["independent_exit"] == 0:
                        status = "HIT_VERIFIED"
                    else:
                        status = "FAILED_VERIFICATION"
                        error = "candidate disagreed with one or both required verifiers"
                    stop = True
                    break
                if stop:
                    break
            counts["kappas_completed"] += 1
            if stop:
                break
    except Exception as exc:  # surfaced in the atomic summary
        status = "FAILED"
        error = f"{type(exc).__name__}: {exc}"

    if args.emit_inventory:
        atomic_write_text(
            args.out_dir / "inventory.jsonl",
            "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in inventory),
        )
    summary: dict[str, Any] = {
        "schema_version": 1,
        "engine": "elliptic_reference",
        "status": status,
        "lane": args.lane or "",
        "kappa_min": args.kappa_min,
        "kappa_max": args.kappa_max,
        "squarefree_only": True,
        "integral_precursors_only": True,
        "x_bound": args.x_bound,
        "chunk_count": args.chunk_count,
        "chunk_index": args.chunk_index,
        "max_seconds": args.max_seconds,
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_seconds": time.monotonic() - started,
        "counts": counts,
    }
    if verification is not None:
        summary["verification"] = verification
    if error is not None:
        summary["error"] = error
    atomic_write_text(args.out_dir / "summary.json", json.dumps(summary, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    if status in {"NO_HIT", "HIT_VERIFIED"}:
        return 0, summary
    if status == "TIMEOUT_INCOMPLETE":
        return 4, summary
    return 3, summary


def self_test() -> None:
    point_5 = make_point_record(5, -4, 6)
    assert point_5 is not None
    assert (point_5.root_minus, point_5.root_center, point_5.root_plus) == (
        Fraction(31, 12),
        Fraction(41, 12),
        Fraction(49, 12),
    )
    point_6 = make_point_record(6, 12, 36)
    assert point_6 is not None
    assert (point_6.root_minus, point_6.root_center, point_6.root_plus) == (
        Fraction(1, 2),
        Fraction(5, 2),
        Fraction(7, 2),
    )


def main(argv: list[str] | None = None) -> int:
    self_test()
    args = parse_args(argv)
    code, _ = run(args)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
