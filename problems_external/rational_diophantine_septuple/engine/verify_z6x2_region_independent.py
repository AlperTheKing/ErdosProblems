#!/usr/bin/env python3
"""Independent exact replay of the fixed Z/6 x Z/2 search region.

This file deliberately does not import any other project module.  It parses
the catalogue again, reconstructs the induced cubic and all group operations
with ``fractions.Fraction``, and emits a canonical per-expression SHA-256
ledger.  The 27 deterministic shards are indexed by ``(j,n0,n1)``; within a
shard, ``n2,...,n10`` run in lexicographic order over ``(-1,0,1)^9``.

Canonical digest records are exactly

    j,n0,...,n10|O\n

for the point at infinity, or

    j,n0,...,n10|xn/xd|mask\n

for a finite point.  ``xn/xd`` is reduced with positive denominator (including
``/1``), and ``mask`` is the decimal 11-bit exact-completion mask.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
import time
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Sequence


CATALOG_SHA256 = "426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933"
BASE_TRIPLE = (
    Fraction(-6656, 61215),
    Fraction(1155, 1696),
    Fraction(795, 154),
)
R3 = (Fraction(-4081, 1560), Fraction(14739, 4160))
RECORD_IDS = tuple(range(1735, 1746))
COEFFICIENTS = (-1, 0, 1)
SHARD_COUNT = 27
EXPRESSIONS_PER_SHARD = 3**9
EXPRESSION_COUNT = 3 * 3**11
RECORD_RE = re.compile(r"^\((\d+)\)\s+\[([^\]]+)\]")

Point = tuple[Fraction, Fraction] | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def fraction_text(value: Fraction, *, force_denominator: bool = False) -> str:
    if value.denominator == 1 and not force_denominator:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(value: object) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str):
        raise TypeError(f"expected rational string, got {type(value).__name__}")
    return Fraction(value.strip())


def parse_point(value: object) -> Point:
    if value is None or value == "O" or value == "infinity":
        return None
    if isinstance(value, dict):
        return parse_fraction(value["x"]), parse_fraction(value["y"])
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return parse_fraction(value[0]), parse_fraction(value[1])
    raise TypeError(f"invalid point encoding: {value!r}")


def rational_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    if numerator_root * numerator_root != value.numerator:
        return None
    if denominator_root * denominator_root != value.denominator:
        return None
    return Fraction(numerator_root, denominator_root)


def is_compatible(left: Fraction, right: Fraction) -> bool:
    return rational_square_root(left * right + 1) is not None


class CubicCurve:
    """The rational group on y^2=A3*x^3+A2*x^2+A1*x+A0."""

    def __init__(self, base: Sequence[Fraction]) -> None:
        if len(base) != 3:
            raise ValueError("the induced curve requires three base values")
        a, b, c = base
        self.a3 = a * b * c
        self.a2 = a * b + a * c + b * c
        self.a1 = a + b + c
        self.a0 = Fraction(1)
        if self.a3 == 0:
            raise ValueError("singular degree drop")

    def rhs(self, x: Fraction) -> Fraction:
        return ((self.a3 * x + self.a2) * x + self.a1) * x + self.a0

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return y * y == self.rhs(x)

    @staticmethod
    def negate(point: Point) -> Point:
        if point is None:
            return None
        return point[0], -point[1]

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2:
            if y1 == -y2:
                return None
            slope = (3 * self.a3 * x1 * x1 + 2 * self.a2 * x1 + self.a1) / (2 * y1)
        else:
            slope = (y2 - y1) / (x2 - x1)
        x3 = (slope * slope - self.a2) / self.a3 - x1 - x2
        y3 = slope * (x1 - x3) - y1
        result = (x3, y3)
        if not self.on_curve(result):
            raise ArithmeticError("independent group law produced an off-curve point")
        return result

    def multiply(self, multiplier: int, point: Point) -> Point:
        if multiplier < 0:
            return self.multiply(-multiplier, self.negate(point))
        result: Point = None
        addend = point
        while multiplier:
            if multiplier & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            multiplier >>= 1
        return result

    def sum(self, points: Iterable[Point]) -> Point:
        result: Point = None
        for point in points:
            result = self.add(result, point)
        return result


def parse_catalog(path: Path) -> dict[int, tuple[Fraction, ...]]:
    records: dict[int, tuple[Fraction, ...]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = RECORD_RE.match(line)
        if match is None:
            continue
        index = int(match.group(1))
        values = tuple(Fraction(part.strip()) for part in match.group(2).split(","))
        if len(values) != 6:
            raise ValueError(f"catalogue record {index} has {len(values)} values")
        if index in records:
            raise ValueError(f"duplicate catalogue record {index}")
        records[index] = values
    if len(records) != 2001 or set(records) != set(range(1, 2002)):
        raise ValueError("catalogue index set is not exactly 1..2001")
    return records


def validate_tuple(values: Sequence[Fraction], expected_size: int) -> None:
    if len(values) != expected_size:
        raise ValueError(f"expected {expected_size} values, got {len(values)}")
    if any(value == 0 for value in values) or len(set(values)) != expected_size:
        raise ValueError("tuple has zero or repeated values")
    for left, right in itertools.combinations(values, 2):
        if not is_compatible(left, right):
            raise ValueError(f"nonsquare pair {left}, {right}")


def catalog_triangles(records: dict[int, tuple[Fraction, ...]]) -> tuple[tuple[Fraction, ...], ...]:
    base_set = set(BASE_TRIPLE)
    triangles: list[tuple[Fraction, ...]] = []
    for record_id in RECORD_IDS:
        values = records[record_id]
        validate_tuple(values, 6)
        if not base_set.issubset(values):
            raise ValueError(f"record {record_id} does not contain the fixed triple")
        triangle = tuple(sorted(value for value in values if value not in base_set))
        if len(triangle) != 3:
            raise ValueError(f"record {record_id} does not define a triangle")
        triangles.append(triangle)
    flattened = tuple(value for triangle in triangles for value in triangle)
    if len(set(flattened)) != 33:
        raise ValueError("the eleven catalogue triangles do not contain 33 distinct values")
    for i, left in enumerate(flattened):
        for j, right in enumerate(flattened[:i]):
            compatible = is_compatible(left, right)
            same_triangle = i // 3 == j // 3
            if compatible != same_triangle:
                raise ValueError(
                    f"catalogue extension graph mismatch at flattened vertices {j}, {i}"
                )
    return tuple(triangles)


def positive_lift(curve: CubicCurve, x: Fraction) -> Point:
    root = rational_square_root(curve.rhs(x))
    if root is None:
        raise ValueError(f"catalogue x-coordinate {x} does not lift to the induced curve")
    point = (x, abs(root))
    if not curve.on_curve(point):
        raise ArithmeticError("lift calibration failed")
    return point


def reconstruct_geometry(
    triangles: Sequence[Sequence[Fraction]],
) -> tuple[CubicCurve, tuple[Point, ...], tuple[Point, ...]]:
    curve = CubicCurve(BASE_TRIPLE)
    if not curve.on_curve(R3):
        raise ValueError("R3 is off the induced curve")
    if curve.multiply(3, R3) is not None or curve.multiply(1, R3) is None:
        raise ValueError("R3 does not have exact order three")
    lifts: list[Point] = []
    for record_id, triangle in zip(RECORD_IDS, triangles):
        least = min(triangle)
        lift = positive_lift(curve, least)
        orbit_points = (lift, curve.add(lift, R3), curve.add(lift, curve.multiply(2, R3)))
        orbit_x = {point[0] for point in orbit_points if point is not None}
        if orbit_x != set(triangle):
            raise ValueError(f"R3 orbit mismatch for catalogue record {record_id}")
        lifts.append(lift)
    t0 = lifts[0]
    directions: list[Point] = [curve.multiply(2, t0)]
    for lift in lifts[1:]:
        directions.append(curve.add(lift, curve.negate(t0)))
    if len(directions) != 11 or any(point is None for point in directions):
        raise ValueError("direction reconstruction failed")
    return curve, tuple(lifts), tuple(directions)


def _first_present(container: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in container:
            return container[name]
    raise KeyError(f"none of the required manifest keys is present: {', '.join(names)}")


def _manifest_catalog(manifest: dict[str, Any], manifest_path: Path) -> tuple[Path, str]:
    catalog = manifest.get("catalog")
    if isinstance(catalog, dict):
        path_value = _first_present(catalog, "path", "source", "file")
        expected_hash = str(_first_present(catalog, "sha256", "source_sha256")).upper()
    elif isinstance(manifest.get("source"), dict) and isinstance(
        manifest["source"].get("catalog"), dict
    ):
        source_catalog = manifest["source"]["catalog"]
        path_value = _first_present(source_catalog, "path", "source", "file")
        expected_hash = str(
            _first_present(source_catalog, "sha256", "source_sha256")
        ).upper()
    else:
        path_value = _first_present(manifest, "catalog_path", "catalog_file")
        expected_hash = str(_first_present(manifest, "catalog_sha256", "source_sha256")).upper()
    path = Path(str(path_value))
    if not path.is_absolute():
        candidates = (
            Path.cwd() / path,
            manifest_path.parent / path,
            manifest_path.parent.parent.parent / path,
            Path(__file__).resolve().parent.parent / path,
        )
        path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
    return path.resolve(), expected_hash


def validate_manifest(
    manifest_path: Path,
    manifest: dict[str, Any],
    catalog_path: Path,
    catalog_hash: str,
    triangles: Sequence[Sequence[Fraction]],
    lifts: Sequence[Point],
    directions: Sequence[Point],
) -> None:
    if manifest.get("schema_version") != 1:
        raise ValueError("manifest schema_version must be 1")
    if manifest.get("route_id") != "fixed-z6x2-maximum-extension-region":
        raise ValueError("manifest route_id differs from the registered route")
    if catalog_hash != CATALOG_SHA256:
        raise ValueError(f"catalogue hash is {catalog_hash}, expected {CATALOG_SHA256}")
    declared_triple = tuple(
        parse_fraction(item) for item in _first_present(manifest, "base_triple", "triple")
    )
    if declared_triple != BASE_TRIPLE:
        raise ValueError("manifest base triple differs from the registered ordered triple")
    declared_r3 = parse_point(_first_present(manifest, "r3", "R3", "torsion_point"))
    if declared_r3 != R3:
        raise ValueError("manifest R3 differs from the registered signed point")
    record_ids = tuple(int(item) for item in _first_present(manifest, "record_ids", "catalog_records"))
    if record_ids != RECORD_IDS:
        raise ValueError("manifest record list differs from 1735..1745")

    declared_triangles = manifest.get("triangles")
    if not isinstance(declared_triangles, list) or len(declared_triangles) != 11:
        raise ValueError("manifest must contain eleven triangles")
    parsed_triangles: list[tuple[Fraction, ...]] = []
    for index, item in enumerate(declared_triangles):
        values = item.get("values") if isinstance(item, dict) else item
        parsed_triangles.append(tuple(parse_fraction(value) for value in values))
        if isinstance(item, dict):
            if item.get("triangle_index") != index or item.get("record_id") != RECORD_IDS[index]:
                raise ValueError(f"manifest triangle metadata differs at index {index}")
            if parse_point(item.get("ti")) != lifts[index]:
                raise ValueError(f"manifest positive lift differs at index {index}")
            declared_orbit = tuple(
                parse_point(point) for point in item.get("orbit_points_ti_plus_jr3", [])
            )
            curve = CubicCurve(BASE_TRIPLE)
            expected_orbit = tuple(curve.add(lifts[index], curve.multiply(j, R3)) for j in range(3))
            if declared_orbit != expected_orbit:
                raise ValueError(f"manifest R3 orbit differs at index {index}")
    if tuple(parsed_triangles) != tuple(tuple(row) for row in triangles):
        raise ValueError("manifest triangles differ from the independent catalogue parse")

    declared_directions_raw = manifest.get("directions")
    if not isinstance(declared_directions_raw, list) or len(declared_directions_raw) != 11:
        raise ValueError("manifest must contain eleven direction points")
    declared_directions: list[Point] = []
    for index, item in enumerate(declared_directions_raw):
        if isinstance(item, dict) and "point" in item:
            if item.get("index") != index:
                raise ValueError(f"manifest direction index differs at {index}")
            declared_directions.append(parse_point(item["point"]))
        else:
            declared_directions.append(parse_point(item))
    if tuple(declared_directions) != tuple(directions):
        raise ValueError("manifest directions differ from the independent group law")

    curve = CubicCurve(BASE_TRIPLE)
    declared_curve = manifest.get("curve")
    if not isinstance(declared_curve, dict):
        raise ValueError("manifest omits the induced cubic")
    coefficients = tuple(
        parse_fraction(value)
        for value in declared_curve.get("coefficients_a3_a2_a1_a0", [])
    )
    if coefficients != (curve.a3, curve.a2, curve.a1, curve.a0):
        raise ValueError("manifest cubic coefficients differ")
    if parse_point(manifest.get("p")) != (Fraction(0), Fraction(1)):
        raise ValueError("manifest P is not (0,1)")

    region = manifest.get("region", manifest)
    expected_region = {
        "j_values": [0, 1, 2],
        "coefficient_values": [-1, 0, 1],
        "coefficient_names": [f"n{i}" for i in range(11)],
        "expression_count": EXPRESSION_COUNT,
        "shard_count": SHARD_COUNT,
        "expressions_per_shard": EXPRESSIONS_PER_SHARD,
    }
    for key, expected in expected_region.items():
        if key not in region:
            raise ValueError(f"manifest region omits {key}")
        if region[key] != expected:
            raise ValueError(f"manifest region field {key} differs: {region[key]!r}")
    if region.get("shard_id_formula") != "9*j + 3*(n0+1) + (n1+1)":
        raise ValueError("manifest shard id formula differs")

    shards = region.get("shards")
    if not isinstance(shards, list) or len(shards) != SHARD_COUNT:
        raise ValueError("manifest must explicitly contain all 27 shard declarations")
    for shard_id, shard in enumerate(shards):
        j, n0, n1 = decode_shard_id(shard_id)
        expected = {
            "shard_id": shard_id,
            "expression_count": EXPRESSIONS_PER_SHARD,
        }
        for key, value in expected.items():
            if shard.get(key) != value:
                raise ValueError(f"manifest shard {shard_id} field {key} differs")
        if shard.get("fixed") != {"j": j, "n0": n0, "n1": n1}:
            raise ValueError(f"manifest shard {shard_id} fixed prefix differs")
        if shard.get("remaining_coefficients") != [f"n{i}" for i in range(2, 11)]:
            raise ValueError(f"manifest shard {shard_id} suffix names differ")
        if shard.get("remaining_order") != "lexicographic over (-1,0,1)^9; n10 varies fastest":
            raise ValueError(f"manifest shard {shard_id} suffix order differs")

    ledger = manifest.get("ledger")
    if not isinstance(ledger, dict):
        raise ValueError("manifest omits canonical ledger rules")
    expected_ledger = {
        "infinity_line": "j,n0,...,n10|O\\n",
        "finite_line": "j,n0,...,n10|xn/xd|mask\\n",
        "mask_rule": "unsigned decimal 0..2047; bit i means exact completion of triangle 1735+i",
    }
    for key, expected in expected_ledger.items():
        if ledger.get(key) != expected:
            raise ValueError(f"manifest ledger field {key} differs")

    if not catalog_path.is_file():
        raise FileNotFoundError(catalog_path)


def decode_shard_id(shard_id: int) -> tuple[int, int, int]:
    if not 0 <= shard_id < SHARD_COUNT:
        raise ValueError(f"shard id must be in 0..{SHARD_COUNT - 1}")
    j, remainder = divmod(shard_id, 9)
    n0_digit, n1_digit = divmod(remainder, 3)
    return j, COEFFICIENTS[n0_digit], COEFFICIENTS[n1_digit]


def encode_shard_id(j: int, n0: int, n1: int) -> int:
    if j not in (0, 1, 2) or n0 not in COEFFICIENTS or n1 not in COEFFICIENTS:
        raise ValueError("invalid shard prefix")
    return 9 * j + 3 * (n0 + 1) + (n1 + 1)


def initial_shard_point(
    curve: CubicCurve,
    lifts: Sequence[Point],
    directions: Sequence[Point],
    j: int,
    n0: int,
    n1: int,
) -> Point:
    coefficients = (n0, n1) + (-1,) * 9
    terms: list[Point] = [lifts[0], curve.multiply(j, R3)]
    terms.extend(curve.multiply(coefficient, direction) for coefficient, direction in zip(coefficients, directions))
    return curve.sum(terms)


def lexicographic_deltas(curve: CubicCurve, directions: Sequence[Point]) -> dict[int, Point]:
    """Return one group increment for every suffix odometer pivot n_k."""
    deltas: dict[int, Point] = {}
    suffix_sum: Point = None
    for k in range(10, 1, -1):
        delta = curve.add(directions[k], curve.multiply(-2, suffix_sum))
        deltas[k] = delta
        suffix_sum = curve.add(directions[k], suffix_sum)
    return deltas


def completion_mask(x: Fraction, triangles: Sequence[Sequence[Fraction]]) -> int:
    if x == 0 or x in BASE_TRIPLE:
        return 0
    mask = 0
    for index, triangle in enumerate(triangles):
        if x in triangle:
            continue
        if all(is_compatible(x, value) for value in triangle):
            mask |= 1 << index
    return mask


def ledger_line(coefficients: Sequence[int], point: Point, mask: int) -> bytes:
    prefix = ",".join(str(item) for item in coefficients)
    if point is None:
        return f"{prefix}|O\n".encode("ascii")
    x = point[0]
    return f"{prefix}|{fraction_text(x, force_denominator=True)}|{mask}\n".encode("ascii")


def advance_suffix(
    curve: CubicCurve,
    point: Point,
    coefficients: list[int],
    deltas: dict[int, Point],
) -> tuple[Point, bool]:
    # ``coefficients`` is [j,n0,n1,n2,...,n10], whereas ``deltas`` is
    # indexed by direction number.  Thus n_k occupies position k+1.
    for k in range(10, 1, -1):
        position = k + 1
        if coefficients[position] < 1:
            coefficients[position] += 1
            for reset in range(k + 1, 11):
                coefficients[reset + 1] = -1
            return curve.add(point, deltas[k]), True
    return point, False


def extract_primary_digest(primary: dict[str, Any]) -> str:
    for key in ("terminal_digest_sha256", "ledger_sha256", "digest_sha256"):
        value = primary.get(key)
        if isinstance(value, str):
            return value.upper()
    terminal = primary.get("terminal_ledger")
    if isinstance(terminal, dict):
        for key in ("sha256", "digest_sha256"):
            value = terminal.get(key)
            if isinstance(value, str):
                return value.upper()
    raise KeyError("primary ledger has no recognized terminal digest field")


def run_shard(
    manifest_path: Path,
    output_path: Path,
    shard_id: int,
    limit: int | None,
    primary_ledger_path: Path | None,
) -> dict[str, Any]:
    started = time.perf_counter()
    manifest_bytes = manifest_path.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest().upper()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict):
        raise TypeError("manifest root must be an object")
    catalog_path, declared_catalog_hash = _manifest_catalog(manifest, manifest_path)
    catalog_hash = sha256_file(catalog_path)
    if declared_catalog_hash != catalog_hash:
        raise ValueError("manifest catalogue hash does not match the file")
    records = parse_catalog(catalog_path)
    triangles = catalog_triangles(records)
    curve, lifts, directions = reconstruct_geometry(triangles)
    validate_manifest(
        manifest_path,
        manifest,
        catalog_path,
        catalog_hash,
        triangles,
        lifts,
        directions,
    )

    if limit is not None and not 1 <= limit <= EXPRESSIONS_PER_SHARD:
        raise ValueError(f"limit must be in 1..{EXPRESSIONS_PER_SHARD}")
    target_count = EXPRESSIONS_PER_SHARD if limit is None else limit
    j, n0, n1 = decode_shard_id(shard_id)
    if encode_shard_id(j, n0, n1) != shard_id:
        raise ArithmeticError("shard encode/decode disagreement")
    coefficients = [j, n0, n1] + [-1] * 9
    point = initial_shard_point(curve, lifts, directions, j, n0, n1)
    deltas = lexicographic_deltas(curve, directions)
    digest = hashlib.sha256()
    finite_count = 0
    infinity_count = 0
    nonzero_count = 0
    completion_expression_count = 0
    completion_bit_count = 0
    candidate_rows: list[dict[str, Any]] = []

    for offset in range(target_count):
        if not curve.on_curve(point):
            raise ArithmeticError(f"off-curve expression at shard {shard_id}, offset {offset}")
        if point is None:
            mask = 0
            infinity_count += 1
        else:
            x = point[0]
            finite_count += 1
            if x != 0:
                nonzero_count += 1
            if not all(is_compatible(x, base) for base in BASE_TRIPLE):
                raise ArithmeticError(
                    f"expression does not extend the base triple at shard {shard_id}, offset {offset}"
                )
            mask = completion_mask(x, triangles)
            if mask:
                completion_expression_count += 1
                completion_bit_count += mask.bit_count()
                candidate_rows.append(
                    {
                        "offset": offset,
                        "coefficients": list(coefficients),
                        "x": fraction_text(x),
                        "completion_mask": mask,
                    }
                )
        digest.update(ledger_line(coefficients, point, mask))
        if offset + 1 < target_count:
            point, advanced = advance_suffix(curve, point, coefficients, deltas)
            if not advanced:
                raise ArithmeticError("suffix odometer terminated before the declared count")

    status = "CALIBRATION" if target_count != EXPRESSIONS_PER_SHARD else (
        "HIT" if completion_expression_count else "NO_HIT"
    )
    report: dict[str, Any] = {
        "schema": "z6x2-independent-shard-ledger-v1",
        "implementation": "standalone-python-fraction-cubic-group-law",
        "engine_sha256": sha256_file(Path(__file__).resolve()),
        "status": status,
        "manifest_path": str(manifest_path.resolve()),
        "manifest_sha256": manifest_hash,
        "catalog_path": str(catalog_path),
        "catalog_sha256": catalog_hash,
        "declared_region": {
            "expression_count": EXPRESSION_COUNT,
            "shard_count": SHARD_COUNT,
            "expressions_per_shard": EXPRESSIONS_PER_SHARD,
        },
        "shard": {"shard_id": shard_id, "j": j, "n0": n0, "n1": n1},
        "enumerated_expression_count": target_count,
        "finite_count": finite_count,
        "infinity_count": infinity_count,
        "nonzero_count": nonzero_count,
        "completion_expression_count": completion_expression_count,
        "completion_bit_count": completion_bit_count,
        "candidate_rows": candidate_rows,
        "terminal_digest_sha256": digest.hexdigest().upper(),
        "preflight": {
            "catalog_record_count": len(records),
            "source_sextuples_checked": len(RECORD_IDS),
            "fixed_triangle_count": len(triangles),
            "fixed_extension_count": len({value for row in triangles for value in row}),
            "fixed_graph_edge_count": sum(
                is_compatible(left, right)
                for left, right in itertools.combinations(
                    (value for row in triangles for value in row), 2
                )
            ),
            "r3_order": 3,
            "orbit_count": len(lifts),
            "direction_count": len(directions),
        },
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }

    if primary_ledger_path is not None:
        primary = json.loads(primary_ledger_path.read_text(encoding="utf-8"))
        primary_digest = extract_primary_digest(primary)
        comparisons = {
            "terminal_digest": primary_digest == report["terminal_digest_sha256"],
            "expression_count": int(
                primary.get("enumerated_expression_count", primary.get("expression_count", -1))
            )
            == target_count,
        }
        report["primary_ledger_path"] = str(primary_ledger_path.resolve())
        report["primary_terminal_digest_sha256"] = primary_digest
        report["primary_comparison"] = comparisons
        if not all(comparisons.values()):
            report["status"] = "FAILED"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def compare_ledgers(
    manifest_path: Path,
    independent_paths: Sequence[Path],
    primary_paths: Sequence[Path],
    output_path: Path,
) -> dict[str, Any]:
    if len(independent_paths) != SHARD_COUNT or len(primary_paths) != SHARD_COUNT:
        raise ValueError("comparison requires exactly 27 independent and 27 primary ledgers")
    manifest_hash = sha256_file(manifest_path)
    independent_by_shard: dict[int, dict[str, Any]] = {}
    primary_by_shard: dict[int, dict[str, Any]] = {}
    for path in independent_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        shard_id = int(data["shard"]["shard_id"])
        if shard_id in independent_by_shard:
            raise ValueError(f"duplicate independent shard {shard_id}")
        independent_by_shard[shard_id] = data
    for path in primary_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        shard_value = data.get("shard_id")
        if shard_value is None and isinstance(data.get("shard"), dict):
            shard_value = data["shard"]["shard_id"]
        shard_id = int(shard_value)
        if shard_id in primary_by_shard:
            raise ValueError(f"duplicate primary shard {shard_id}")
        primary_by_shard[shard_id] = data
    if set(independent_by_shard) != set(range(SHARD_COUNT)):
        raise ValueError("independent shard id set is incomplete")
    if set(primary_by_shard) != set(range(SHARD_COUNT)):
        raise ValueError("primary shard id set is incomplete")

    rows: list[dict[str, Any]] = []
    total_expressions = 0
    total_completions = 0
    all_match = True
    for shard_id in range(SHARD_COUNT):
        independent = independent_by_shard[shard_id]
        primary = primary_by_shard[shard_id]
        independent_digest = str(independent["terminal_digest_sha256"]).upper()
        primary_digest = extract_primary_digest(primary)
        count = int(independent["enumerated_expression_count"])
        digest_match = independent_digest == primary_digest
        count_match = count == int(
            primary.get("enumerated_expression_count", primary.get("expression_count", -1))
        )
        manifest_match = str(independent["manifest_sha256"]).upper() == manifest_hash
        row = {
            "shard_id": shard_id,
            "expression_count": count,
            "independent_digest_sha256": independent_digest,
            "primary_digest_sha256": primary_digest,
            "digest_match": digest_match,
            "count_match": count_match,
            "manifest_match": manifest_match,
        }
        rows.append(row)
        total_expressions += count
        total_completions += int(independent["completion_expression_count"])
        all_match &= digest_match and count_match and manifest_match
    all_match &= total_expressions == EXPRESSION_COUNT
    status = "HIT" if total_completions else "NO_HIT"
    if not all_match:
        status = "FAILED"
    report = {
        "schema": "z6x2-independent-ledger-comparison-v1",
        "status": status,
        "manifest_path": str(manifest_path.resolve()),
        "manifest_sha256": manifest_hash,
        "shard_count": len(rows),
        "expression_count": total_expressions,
        "completion_expression_count": total_completions,
        "all_terminal_ledgers_match": all_match,
        "shards": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="replay one deterministic shard")
    run.add_argument("manifest", type=Path)
    run.add_argument("output", type=Path)
    run.add_argument("--shard-id", type=int, required=True)
    run.add_argument(
        "--limit",
        type=int,
        help="calibration prefix length; omission consumes the complete 19683-expression shard",
    )
    run.add_argument("--primary-ledger", type=Path)

    compare = subparsers.add_parser("compare", help="compare all 27 terminal-ledger pairs")
    compare.add_argument("manifest", type=Path)
    compare.add_argument("output", type=Path)
    compare.add_argument("--independent", type=Path, nargs=SHARD_COUNT, required=True)
    compare.add_argument("--primary", type=Path, nargs=SHARD_COUNT, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run":
        report = run_shard(
            args.manifest,
            args.output,
            args.shard_id,
            args.limit,
            args.primary_ledger,
        )
    else:
        report = compare_ledgers(
            args.manifest,
            args.independent,
            args.primary,
            args.output,
        )
    print(json.dumps({key: report[key] for key in report if key in {
        "status",
        "shard",
        "enumerated_expression_count",
        "expression_count",
        "terminal_digest_sha256",
        "all_terminal_ledgers_match",
    }}, sort_keys=True))
    return 0 if report["status"] not in {"FAILED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
