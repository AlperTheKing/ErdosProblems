#!/usr/bin/env python3
"""Primary exact enumerator for the frozen fixed Z/6 x Z/2 region.

The ``shard`` command evaluates one of the 27 manifest shards.  Full shards
are intentionally guarded by ``--allow-full-search``; calibration mode can
evaluate a strict prefix without claiming exhaustion.  The ``aggregate``
command accepts only 27 complete full-shard ledgers.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Iterator

from elliptic_core import CubicCurve, Point
from verify_septuple_independent import verify_septuple
from verify_tuple import verify_tuple


PROBLEM_DIR = Path(__file__).resolve().parents[1]
COEFFICIENT_VALUES = (-1, 0, 1)
TAIL_EXPRESSION_COUNT = 3**9


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def fraction_ledger(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def parse_point(value: Any) -> Point:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"invalid manifest point: {value!r}")
    return Fraction(value[0]), Fraction(value[1])


def validate_manifest(path: Path) -> tuple[dict[str, Any], str]:
    manifest_hash = sha256_file(path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported manifest schema")
    if manifest.get("route_id") != "fixed-z6x2-maximum-extension-region":
        raise ValueError("manifest is for a different route")
    region = manifest.get("region", {})
    if (
        region.get("expression_count") != 531441
        or region.get("shard_count") != 27
        or region.get("expressions_per_shard") != TAIL_EXPRESSION_COUNT
        or region.get("shard_id_formula") != "9*j + 3*(n0+1) + (n1+1)"
    ):
        raise ValueError("manifest region does not match the frozen 27-shard map")
    if len(manifest.get("triangles", [])) != 11 or len(manifest.get("directions", [])) != 11:
        raise ValueError("manifest must contain eleven triangles and eleven directions")

    search_contract = manifest.get("engine", {}).get("primary_search", {})
    observed_engine_hash = sha256_file(Path(__file__).resolve())
    if search_contract.get("sha256") != observed_engine_hash:
        raise ValueError(
            f"search engine SHA-256 mismatch: {observed_engine_hash} != "
            f"{search_contract.get('sha256')}"
        )
    for source in manifest.get("source", {}).values():
        source_path = PROBLEM_DIR / source["path"]
        observed = sha256_file(source_path)
        if observed != source["sha256"]:
            raise ValueError(f"frozen source SHA-256 mismatch for {source_path}")
    return manifest, manifest_hash


def shard_fixed_coefficients(manifest: dict[str, Any], shard_id: int) -> tuple[int, int, int]:
    if not 0 <= shard_id < 27:
        raise ValueError("shard id must be in 0..26")
    rows = manifest["region"]["shards"]
    row = next((item for item in rows if int(item["shard_id"]) == shard_id), None)
    if row is None:
        raise ValueError(f"manifest omits shard {shard_id}")
    fixed = row["fixed"]
    j, n0, n1 = int(fixed["j"]), int(fixed["n0"]), int(fixed["n1"])
    if shard_id != 9 * j + 3 * (n0 + 1) + (n1 + 1):
        raise ValueError(f"manifest shard {shard_id} violates the declared formula")
    return j, n0, n1


def tail_coefficients(limit: int) -> Iterator[tuple[int, ...]]:
    return itertools.islice(
        itertools.product(COEFFICIENT_VALUES, repeat=9),
        limit,
    )


def exact_rational_square(value: Fraction) -> bool:
    if value < 0:
        return False
    nr = isqrt(value.numerator)
    dr = isqrt(value.denominator)
    return nr * nr == value.numerator and dr * dr == value.denominator


def modularly_rejected(value: Fraction, primes: tuple[int, ...]) -> int | None:
    """Return a sound rejecting prime, skipping nonunit denominators."""

    for prime in primes:
        denominator = value.denominator % prime
        if denominator == 0:
            continue
        residue = (value.numerator % prime) * pow(denominator, -1, prime) % prime
        if residue and pow(residue, (prime - 1) // 2, prime) == prime - 1:
            return prime
    return None


def square_test(value: Fraction, primes: tuple[int, ...], statistics: dict[str, Any]) -> bool:
    statistics["square_tests"] += 1
    rejecting_prime = modularly_rejected(value, primes)
    if rejecting_prime is not None:
        statistics["modular_rejections"] += 1
        key = str(rejecting_prime)
        statistics["modular_rejections_by_prime"][key] = (
            statistics["modular_rejections_by_prime"].get(key, 0) + 1
        )
        return False
    statistics["exact_square_tests"] += 1
    result = exact_rational_square(value)
    if result:
        statistics["exact_squares"] += 1
    else:
        statistics["exact_nonsquares"] += 1
    return result


def add_multiple(curve: CubicCurve, point: Point, multiplier: int, direction: Point) -> Point:
    if multiplier == 0:
        return point
    return curve.add(point, curve.scalar_mul(multiplier, direction))


def initial_point(
    curve: CubicCurve,
    t0: Point,
    r3: Point,
    directions: tuple[Point, ...],
    coefficients: tuple[int, ...],
    j: int,
) -> Point:
    point = curve.add(t0, curve.scalar_mul(j, r3))
    for coefficient, direction in zip(coefficients, directions, strict=True):
        point = add_multiple(curve, point, coefficient, direction)
    return point


def mask_for_x(
    x: Fraction,
    base: tuple[Fraction, ...],
    triangles: tuple[tuple[Fraction, ...], ...],
    primes: tuple[int, ...],
    statistics: dict[str, Any],
    hits: list[dict[str, Any]],
    emitted_hits: set[tuple[Fraction, int]],
) -> int:
    if x == 0 or x in base:
        statistics["base_forbidden_x"] += 1
        return 0

    base_tests = tuple(square_test(value * x + 1, primes, statistics) for value in base)
    if not all(base_tests):
        # Every finite non-forbidden expression is in P+2E(Q).  A failed
        # direct extension test invalidates the finite-region construction.
        raise ArithmeticError(f"finite expression x={x} failed a base square condition")
    statistics["base_extension_x"] += 1

    mask = 0
    for triangle_index, triangle in enumerate(triangles):
        if x in triangle:
            statistics["triangle_duplicate_skips"] += 1
            continue
        passes = True
        for value in triangle:
            if not square_test(value * x + 1, primes, statistics):
                passes = False
                break
        if not passes:
            continue

        candidate = base + triangle + (x,)
        primary = verify_tuple(
            candidate,
            name=f"z6x2-shard-hit-triangle-{triangle_index}",
            expect_size=7,
        )
        independent = verify_septuple(
            [str(value) for value in candidate],
            name=f"z6x2-shard-hit-triangle-{triangle_index}",
        )
        if not primary["valid"] or not independent["valid"]:
            raise ArithmeticError("completion bit failed one of the two final verifiers")
        mask |= 1 << triangle_index
        key = (x, triangle_index)
        if key not in emitted_hits:
            emitted_hits.add(key)
            hits.append(
                {
                    "triangle_index": triangle_index,
                    "record_id": 1735 + triangle_index,
                    "x": str(x),
                    "values": [str(value) for value in candidate],
                    "primary_verifier": primary,
                    "independent_verifier": independent,
                }
            )
    return mask


def write_unique_x_sidecar(output: Path, values: set[Fraction]) -> tuple[Path, str]:
    sidecar = output.with_name(output.stem + ".unique_x.txt.gz")
    temporary = sidecar.with_name(sidecar.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            for value in sorted(values):
                compressed.write((fraction_ledger(value) + "\n").encode("ascii"))
        raw.flush()
        os.fsync(raw.fileno())
    os.replace(temporary, sidecar)
    return sidecar, sha256_file(sidecar)


def run_shard(args: argparse.Namespace) -> int:
    manifest_path = args.manifest.resolve()
    manifest, manifest_hash = validate_manifest(manifest_path)
    if args.mode == "full" and not args.allow_full_search:
        raise ValueError("full enumeration requires the explicit --allow-full-search gate")
    if args.mode == "calibration":
        if args.limit is None or not 1 <= args.limit < TAIL_EXPRESSION_COUNT:
            raise ValueError("calibration requires --limit in 1..19682")
        limit = args.limit
    else:
        if args.limit is not None:
            raise ValueError("--limit is forbidden in full mode")
        limit = TAIL_EXPRESSION_COUNT

    j, n0, n1 = shard_fixed_coefficients(manifest, args.shard_id)
    base = tuple(Fraction(value) for value in manifest["base_triple"])
    curve = CubicCurve.from_diophantine_triple(*base)
    r3 = parse_point(manifest["r3"])
    t0 = parse_point(manifest["triangles"][0]["ti"])
    directions = tuple(parse_point(row["point"]) for row in manifest["directions"])
    triangles = tuple(
        tuple(Fraction(value) for value in row["values"])
        for row in manifest["triangles"]
    )
    primes = tuple(int(prime) for prime in manifest["modular_filter"]["primes"])
    if r3 is None or t0 is None or any(direction is None for direction in directions):
        raise ValueError("manifest search points must all be finite")
    if curve.scalar_mul(3, r3) is not None:
        raise ArithmeticError("manifest R3 no longer has order three")

    statistics: dict[str, Any] = {
        "square_tests": 0,
        "modular_rejections": 0,
        "modular_rejections_by_prime": {},
        "exact_square_tests": 0,
        "exact_squares": 0,
        "exact_nonsquares": 0,
        "base_forbidden_x": 0,
        "base_extension_x": 0,
        "triangle_duplicate_skips": 0,
    }
    ledger = hashlib.sha256()
    cache: dict[Fraction, int] = {}
    unique_finite_x: set[Fraction] = set()
    emitted_hits: set[tuple[Fraction, int]] = set()
    hits: list[dict[str, Any]] = []
    infinity_count = 0
    finite_expression_count = 0
    cache_hit_count = 0
    completion_bit_count = 0
    first_coefficients: list[int] | None = None
    last_coefficients: list[int] | None = None

    previous: tuple[int, ...] | None = None
    point: Point = None
    processed = 0
    for tail in tail_coefficients(limit):
        coefficients = (n0, n1) + tail
        if previous is None:
            point = initial_point(curve, t0, r3, directions, coefficients, j)
        else:
            for direction_index, (old, new) in enumerate(zip(previous, coefficients, strict=True)):
                delta = new - old
                if delta:
                    if delta not in (-2, 1):
                        raise ArithmeticError(f"unexpected lexicographic delta {delta}")
                    point = add_multiple(curve, point, delta, directions[direction_index])
        previous = coefficients
        if not curve.is_on_curve(point):
            raise ArithmeticError("odometer update produced a point off the curve")

        processed += 1
        coefficient_text = ",".join(str(value) for value in (j,) + coefficients)
        if first_coefficients is None:
            first_coefficients = [j, *coefficients]
        last_coefficients = [j, *coefficients]
        if point is None:
            infinity_count += 1
            ledger.update(f"{coefficient_text}|O\n".encode("ascii"))
            continue

        finite_expression_count += 1
        x = point[0]
        unique_finite_x.add(x)
        if x in cache:
            cache_hit_count += 1
            mask = cache[x]
        else:
            mask = mask_for_x(
                x,
                base,
                triangles,
                primes,
                statistics,
                hits,
                emitted_hits,
            )
            cache[x] = mask
        completion_bit_count += mask.bit_count()
        ledger.update(
            f"{coefficient_text}|{fraction_ledger(x)}|{mask}\n".encode("ascii")
        )

    if processed != limit:
        raise ArithmeticError(f"processed {processed} expressions, expected {limit}")
    output = args.output.resolve()
    sidecar, sidecar_hash = write_unique_x_sidecar(output, unique_finite_x)
    complete = args.mode == "full" and processed == TAIL_EXPRESSION_COUNT
    status = (
        "SHARD_COMPLETE_HIT"
        if complete and hits
        else "SHARD_COMPLETE_NO_HIT"
        if complete
        else "CALIBRATION_HIT"
        if hits
        else "CALIBRATION_COMPLETE"
    )
    result: dict[str, Any] = {
        "schema_version": 1,
        "route_id": manifest["route_id"],
        "status": status,
        "mode": args.mode,
        "complete": complete,
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest_hash,
        "engine_sha256": sha256_file(Path(__file__).resolve()),
        "shard_id": args.shard_id,
        "fixed": {"j": j, "n0": n0, "n1": n1},
        "expression_count": processed,
        "expected_expression_count": TAIL_EXPRESSION_COUNT if args.mode == "full" else limit,
        "first_coefficients": first_coefficients,
        "last_coefficients": last_coefficients,
        "ledger_sha256": ledger.hexdigest().upper(),
        "infinity_expression_count": infinity_count,
        "finite_expression_count": finite_expression_count,
        "unique_finite_x_count": len(unique_finite_x),
        "duplicate_finite_x_expression_count": finite_expression_count - len(unique_finite_x),
        "cache_hit_count": cache_hit_count,
        "completion_bit_count": completion_bit_count,
        "hit_count": len(hits),
        "hits": hits,
        "statistics": statistics,
        "unique_x_file": sidecar.name,
        "unique_x_sha256": sidecar_hash,
    }
    atomic_write_json(output, result)
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "shard_id",
                    "expression_count",
                    "unique_finite_x_count",
                    "completion_bit_count",
                    "hit_count",
                    "ledger_sha256",
                )
            },
            sort_keys=True,
        )
    )
    return 0


def read_unique_x(result_path: Path, result: dict[str, Any]) -> set[Fraction]:
    sidecar = result_path.parent / result["unique_x_file"]
    if sha256_file(sidecar) != result["unique_x_sha256"]:
        raise ValueError(f"unique-x sidecar SHA mismatch for {sidecar}")
    values: set[Fraction] = set()
    with gzip.open(sidecar, "rt", encoding="ascii") as handle:
        for line in handle:
            token = line.strip()
            if token:
                values.add(Fraction(token))
    if len(values) != int(result["unique_finite_x_count"]):
        raise ValueError(f"unique-x count mismatch for {sidecar}")
    return values


def run_aggregate(args: argparse.Namespace) -> int:
    manifest_path = args.manifest.resolve()
    manifest, manifest_hash = validate_manifest(manifest_path)
    results_dir = args.results_dir.resolve()
    shard_results: list[dict[str, Any]] = []
    all_unique_x: set[Fraction] = set()
    all_hits: list[dict[str, Any]] = []
    digest_of_digests = hashlib.sha256()
    total_expressions = 0
    total_completion_bits = 0

    for shard_id in range(27):
        path = results_dir / f"shard_{shard_id:02d}.json"
        result = json.loads(path.read_text(encoding="utf-8"))
        if (
            result.get("manifest_sha256") != manifest_hash
            or result.get("shard_id") != shard_id
            or result.get("mode") != "full"
            or result.get("complete") is not True
            or result.get("expression_count") != TAIL_EXPRESSION_COUNT
            or result.get("status") not in {"SHARD_COMPLETE_NO_HIT", "SHARD_COMPLETE_HIT"}
        ):
            raise ValueError(f"incomplete or inconsistent shard result: {path}")
        digest = result["ledger_sha256"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"invalid ledger digest in {path}")
        digest_of_digests.update(f"{shard_id}|{digest}\n".encode("ascii"))
        total_expressions += int(result["expression_count"])
        total_completion_bits += int(result["completion_bit_count"])
        all_hits.extend(result["hits"])
        all_unique_x.update(read_unique_x(path, result))
        shard_results.append(
            {
                "shard_id": shard_id,
                "result_file": path.name,
                "result_sha256": sha256_file(path),
                "ledger_sha256": digest,
                "unique_finite_x_count": result["unique_finite_x_count"],
                "hit_count": result["hit_count"],
            }
        )

    if total_expressions != int(manifest["region"]["expression_count"]):
        raise ArithmeticError(
            f"aggregate expression count {total_expressions} != manifest 531441"
        )
    summary = {
        "schema_version": 1,
        "route_id": manifest["route_id"],
        "status": "HIT" if all_hits else "NO_HIT",
        "scope": "only the frozen 531441-expression fixed Z/6 x Z/2 region",
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest_hash,
        "shard_count": len(shard_results),
        "expression_count": total_expressions,
        "unique_finite_x_count": len(all_unique_x),
        "completion_bit_count": total_completion_bits,
        "hit_count": len(all_hits),
        "hits": all_hits,
        "shard_ledger_digest_sha256": digest_of_digests.hexdigest().upper(),
        "shard_digest_combination_rule": "SHA-256 of ASCII lines shard_id|ledger_sha256\\n in shard order",
        "shards": shard_results,
    }
    atomic_write_json(args.output.resolve(), summary)
    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "status",
                    "shard_count",
                    "expression_count",
                    "unique_finite_x_count",
                    "completion_bit_count",
                    "hit_count",
                    "shard_ledger_digest_sha256",
                )
            },
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    shard = subparsers.add_parser("shard", help="run one deterministic shard")
    shard.add_argument("--manifest", type=Path, required=True)
    shard.add_argument("--output", type=Path, required=True)
    shard.add_argument("--shard-id", type=int, required=True)
    shard.add_argument("--mode", choices=("calibration", "full"), required=True)
    shard.add_argument("--limit", type=int)
    shard.add_argument("--allow-full-search", action="store_true")
    shard.set_defaults(handler=run_shard)

    aggregate = subparsers.add_parser("aggregate", help="combine 27 complete shards")
    aggregate.add_argument("--manifest", type=Path, required=True)
    aggregate.add_argument("--results-dir", type=Path, required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    aggregate.set_defaults(handler=run_aggregate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.handler(args)
    except (ArithmeticError, FileNotFoundError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
