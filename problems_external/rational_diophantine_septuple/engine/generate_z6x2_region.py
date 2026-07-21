#!/usr/bin/env python3
"""Freeze and validate the fixed Z/6 x Z/2 maximum-extension region.

This generator is deliberately narrower than the general catalogue tools.  It
accepts only records 1735--1745 for the one registered base triple, proves all
of the manifest calibration claims with exact rational arithmetic, and writes
a self-contained search manifest.  It performs no finite-region search.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

from catalog_scan import parse_catalog
from elliptic_core import CubicCurve, Point, extension_point, rational_sqrt


PROBLEM_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = PROBLEM_DIR / "engine"
CATALOG_PATH = PROBLEM_DIR / "sources" / "2001.sextuples.txt"
SCAN_SUMMARY_PATH = PROBLEM_DIR / "runs" / "catalog_scan_20260720T0643" / "summary.json"
EXCLUSION_MANIFEST_PATH = (
    PROBLEM_DIR / "runs" / "catalog_multiseed_box1_20260720T0655" / "manifest.json"
)

EXPECTED_HASHES = {
    "catalog": "426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933",
    "scan_summary": "A281BF2AC54433E7D80F013BB4BF63D1B8843C9763213BF8A27E58B12F8DF656",
    "exclusion_manifest": "593063D5FCD0BAC94EE3D3F15FA9E18B4ACC65B90C95C992C34DF13CD0C56860",
}

BASE_TRIPLE = (
    Fraction(-6656, 61215),
    Fraction(1155, 1696),
    Fraction(795, 154),
)
P = (Fraction(0), Fraction(1))
R3 = (Fraction(-4081, 1560), Fraction(14739, 4160))
RECORD_IDS = tuple(range(1735, 1746))
COEFFICIENT_VALUES = (-1, 0, 1)
MODULAR_PRIMES = (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def qtext(value: Fraction) -> str:
    return str(value)


def point_json(point: Point) -> list[str] | None:
    if point is None:
        return None
    return [qtext(point[0]), qtext(point[1])]


def compatible(left: Fraction, right: Fraction) -> bool:
    return rational_sqrt(left * right + 1) is not None


def pair_roots(values: Iterable[Fraction]) -> list[dict[str, Any]]:
    sequence = tuple(values)
    result: list[dict[str, Any]] = []
    for left_index, right_index in itertools.combinations(range(len(sequence)), 2):
        value = sequence[left_index] * sequence[right_index] + 1
        root = rational_sqrt(value)
        if root is None:
            raise ValueError(
                f"nonsquare pair at positions {left_index},{right_index}: {value}"
            )
        result.append(
            {
                "indices": [left_index, right_index],
                "product_plus_one": qtext(value),
                "root": qtext(root),
            }
        )
    return result


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def assert_source_hashes() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for label, path in (
        ("catalog", CATALOG_PATH),
        ("scan_summary", SCAN_SUMMARY_PATH),
        ("exclusion_manifest", EXCLUSION_MANIFEST_PATH),
    ):
        observed = sha256_file(path)
        expected = EXPECTED_HASHES[label]
        if observed != expected:
            raise ValueError(f"{label} SHA-256 mismatch: {observed} != {expected}")
        rows[label] = {
            "path": path.relative_to(PROBLEM_DIR).as_posix(),
            "sha256": observed,
        }
    return rows


def connected_components(
    vertices: tuple[Fraction, ...], edges: set[tuple[Fraction, Fraction]]
) -> list[tuple[Fraction, ...]]:
    neighbors = {vertex: set() for vertex in vertices}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    unseen = set(vertices)
    components: list[tuple[Fraction, ...]] = []
    while unseen:
        start = min(unseen)
        stack = [start]
        component: set[Fraction] = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(neighbors[vertex] - component)
        unseen -= component
        components.append(tuple(sorted(component)))
    return sorted(components)


def build_manifest(output_dir: Path) -> dict[str, Any]:
    source_rows = assert_source_hashes()
    records = {int(row["index"]): row for row in parse_catalog(CATALOG_PATH)}
    curve = CubicCurve.from_diophantine_triple(*BASE_TRIPLE)

    if not curve.is_on_curve(P):
        raise ArithmeticError("P=(0,1) is not on the induced curve")
    if not curve.is_on_curve(R3):
        raise ArithmeticError("declared R3 is not on the induced curve")
    if curve.scalar_mul(3, R3) is not None or curve.scalar_mul(1, R3) is None:
        raise ArithmeticError("declared R3 does not have exact order three")

    triangles: list[dict[str, Any]] = []
    triangle_sets: list[tuple[Fraction, ...]] = []
    lifts: list[tuple[Fraction, Fraction]] = []
    all_extensions: list[Fraction] = []
    sextuple_pair_count = 0
    orbit_identity_count = 0

    for triangle_index, record_id in enumerate(RECORD_IDS):
        record = records.get(record_id)
        if record is None:
            raise ValueError(f"catalogue record {record_id} is absent")
        values = tuple(record["values"])  # type: ignore[arg-type]
        if len(values) != 6 or len(set(values)) != 6 or any(value == 0 for value in values):
            raise ValueError(f"catalogue record {record_id} is not a distinct nonzero sextuple")
        if not set(BASE_TRIPLE).issubset(values):
            raise ValueError(f"catalogue record {record_id} does not contain the base triple")

        roots = pair_roots(values)
        sextuple_pair_count += len(roots)
        triangle = tuple(sorted(value for value in values if value not in set(BASE_TRIPLE)))
        if len(triangle) != 3:
            raise ValueError(f"record {record_id} does not leave a three-value triangle")
        lift = extension_point(*BASE_TRIPLE, triangle[0])
        orbit_points = tuple(
            curve.add(lift, curve.scalar_mul(j, R3)) for j in range(3)
        )
        if any(point is None for point in orbit_points):
            raise ArithmeticError(f"record {record_id} orbit contains infinity")
        orbit_x = tuple(point[0] for point in orbit_points if point is not None)
        if set(orbit_x) != set(triangle) or len(set(orbit_x)) != 3:
            raise ArithmeticError(f"record {record_id} is not the exact R3 x-orbit")
        orbit_identity_count += 3

        triangle_sets.append(triangle)
        lifts.append(lift)
        all_extensions.extend(triangle)
        triangles.append(
            {
                "triangle_index": triangle_index,
                "record_id": record_id,
                "values": [qtext(value) for value in triangle],
                "source_sextuple": [qtext(value) for value in values],
                "source_pair_roots": roots,
                "lift_convention": "positive product of the three nonnegative base roots at the least x",
                "least_x": qtext(triangle[0]),
                "ti": point_json(lift),
                "orbit_points_ti_plus_jr3": [point_json(point) for point in orbit_points],
                "orbit_x_ti_plus_jr3": [qtext(value) for value in orbit_x],
            }
        )

    extension_tuple = tuple(sorted(all_extensions))
    if len(extension_tuple) != 33 or len(set(extension_tuple)) != 33:
        raise ArithmeticError("the eleven records do not supply 33 distinct extensions")
    graph_edges = {
        (left, right)
        for left, right in itertools.combinations(extension_tuple, 2)
        if compatible(left, right)
    }
    expected_edges = {
        tuple(sorted((left, right)))
        for triangle in triangle_sets
        for left, right in itertools.combinations(triangle, 2)
    }
    if graph_edges != expected_edges or len(graph_edges) != 33:
        raise ArithmeticError("the exact compatibility graph is not eleven isolated triangles")
    components = connected_components(extension_tuple, graph_edges)
    if components != sorted(triangle_sets):
        raise ArithmeticError("compatibility graph components do not match catalogue records")

    t0 = lifts[0]
    directions: list[Point] = [curve.scalar_mul(2, t0)]
    minus_t0 = curve.neg(t0)
    directions.extend(curve.add(lift, minus_t0) for lift in lifts[1:])
    if len(directions) != 11 or any(direction is None for direction in directions):
        raise ArithmeticError("one of the eleven finite directions is the identity")
    if any(not curve.is_on_curve(direction) for direction in directions):
        raise ArithmeticError("one of the eleven directions is off the induced curve")

    shard_rows = []
    for j in range(3):
        for n0 in COEFFICIENT_VALUES:
            for n1 in COEFFICIENT_VALUES:
                shard_id = 9 * j + 3 * (n0 + 1) + (n1 + 1)
                shard_rows.append(
                    {
                        "shard_id": shard_id,
                        "fixed": {"j": j, "n0": n0, "n1": n1},
                        "remaining_coefficients": [f"n{i}" for i in range(2, 11)],
                        "remaining_order": "lexicographic over (-1,0,1)^9; n10 varies fastest",
                        "expression_count": 3**9,
                    }
                )
    shard_rows.sort(key=lambda row: int(row["shard_id"]))
    if [row["shard_id"] for row in shard_rows] != list(range(27)):
        raise ArithmeticError("shard ids are not exactly 0..26")

    generator_path = Path(__file__).resolve()
    search_path = ENGINE_DIR / "z6x2_region_search.py"
    primary_verifier = ENGINE_DIR / "verify_tuple.py"
    independent_verifier = ENGINE_DIR / "verify_septuple_independent.py"
    for required in (search_path, primary_verifier, independent_verifier):
        if not required.is_file():
            raise FileNotFoundError(required)

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "route_id": "fixed-z6x2-maximum-extension-region",
        "run_id": output_dir.name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FROZEN_INPUT",
        "source": source_rows,
        "engine": {
            "generator": {
                "path": generator_path.relative_to(PROBLEM_DIR).as_posix(),
                "sha256": sha256_file(generator_path),
            },
            "primary_search": {
                "path": search_path.relative_to(PROBLEM_DIR).as_posix(),
                "sha256": sha256_file(search_path),
            },
        },
        "final_verifiers": [
            {
                "path": primary_verifier.relative_to(PROBLEM_DIR).as_posix(),
                "sha256": sha256_file(primary_verifier),
                "entrypoint": "verify_tuple(values, expect_size=7)",
            },
            {
                "path": independent_verifier.relative_to(PROBLEM_DIR).as_posix(),
                "sha256": sha256_file(independent_verifier),
                "entrypoint": "verify_septuple(values)",
            },
        ],
        "base_triple": [qtext(value) for value in BASE_TRIPLE],
        "base_pair_roots": pair_roots(BASE_TRIPLE),
        "curve": {
            "model": "y^2=a3*x^3+a2*x^2+a1*x+a0=(1+a*x)(1+b*x)(1+c*x)",
            "coefficients_a3_a2_a1_a0": [
                qtext(curve.a3),
                qtext(curve.a2),
                qtext(curve.a1),
                qtext(curve.a0),
            ],
            "discriminant": qtext(curve.discriminant),
        },
        "p": point_json(P),
        "r3": point_json(R3),
        "r3_order": 3,
        "record_ids": list(RECORD_IDS),
        "triangles": triangles,
        "compatibility_graph": {
            "vertex_count": len(extension_tuple),
            "edge_count": len(graph_edges),
            "component_count": len(components),
            "component_sizes": [len(component) for component in components],
            "edges": [
                [qtext(left), qtext(right)] for left, right in sorted(graph_edges)
            ],
            "cross_triangle_edge_count": len(graph_edges - expected_edges),
        },
        "directions": [
            {
                "index": index,
                "name": f"D{index}",
                "definition": "2*T0" if index == 0 else f"T{index}-T0",
                "point": point_json(direction),
            }
            for index, direction in enumerate(directions)
        ],
        "region": {
            "formula": "Q(j,n)=T0+j*R3+sum(i=0..10,n_i*D_i)",
            "j_values": [0, 1, 2],
            "coefficient_names": [f"n{i}" for i in range(11)],
            "coefficient_values": list(COEFFICIENT_VALUES),
            "expression_count": 3 * 3**11,
            "shard_count": 27,
            "expressions_per_shard": 3**9,
            "shard_id_formula": "9*j + 3*(n0+1) + (n1+1)",
            "shards": shard_rows,
        },
        "ledger": {
            "encoding": "ASCII UTF-8",
            "infinity_line": "j,n0,...,n10|O\\n",
            "finite_line": "j,n0,...,n10|xn/xd|mask\\n",
            "fraction_rule": "reduced signed numerator and positive denominator; slash retained for denominator 1",
            "mask_rule": "unsigned decimal 0..2047; bit i means exact completion of triangle 1735+i",
            "per_shard_digest": "SHA-256 of the 19683 lines in declared lexicographic order",
        },
        "modular_filter": {
            "primes": list(MODULAR_PRIMES),
            "soundness_rule": "reject q only when denominator is a unit mod p and q is a quadratic nonresidue mod p",
            "survivor_rule": "every modular survivor is tested by exact integer square roots of reduced numerator and denominator",
        },
        "validation": {
            "source_sextuple_count": len(triangles),
            "source_pair_condition_count": sextuple_pair_count,
            "r3_order_identity": "3*R3=O",
            "orbit_identity_count": orbit_identity_count,
            "extension_vertex_count": len(extension_tuple),
            "compatibility_edge_count": len(graph_edges),
            "cross_triangle_edge_count": 0,
            "direction_count": len(directions),
            "expression_count_arithmetic": 3 * 3**11,
        },
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        raise SystemExit(f"refusing to overwrite frozen manifest: {manifest_path}")
    manifest = build_manifest(output_dir)
    atomic_write_json(manifest_path, manifest)
    manifest_hash = sha256_file(manifest_path)
    report = {
        "status": "PASS",
        "manifest": manifest_path.name,
        "manifest_sha256": manifest_hash,
        "records": len(manifest["record_ids"]),
        "triangles": len(manifest["triangles"]),
        "edges": manifest["compatibility_graph"]["edge_count"],
        "directions": len(manifest["directions"]),
        "shards": manifest["region"]["shard_count"],
        "expressions": manifest["region"]["expression_count"],
    }
    atomic_write_json(output_dir / "generation_report.json", report)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
