#!/usr/bin/env python3
"""Independent exact referee for the fixed rank-12 Boolean-cube route.

This module intentionally uses only the Python standard library.  It does not
import either search engine and it does not enumerate the full 4096-point cube.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path
from typing import Optional


ARCHIVE_SHA256 = "3C0F200A895B4460E5A206112321AE05CBD7EA58263B369753FC68B1A7B8218E"

A = 1444491707528591356856089186460491195711268950880
B = 559921583779625421248683584939561762456224290170437461555851482041439747
U = 7138564997564
M = 955655055996458012197251

TRIPLE = (
    F(6125241375, 11907531272),
    F(5535371271425, 14277129995128),
    F(-273138178560, 153430695649),
)
PAIR_ROOTS = (
    F(13040990647, 11907531272),
    F(1955029, 6735029),
    F(4494674021, 8075299771),
)

TORSION = (
    (F(910954389920845836020349), F(-455477194960422918010175)),
    (F(-5448727291190824028230629, 4), F(5448727291190824028230625, 8)),
    (F(451227432876860171037309), F(-225613716438430085518655)),
)

POINTS = (
    (F(158850932500649609134809), F(578334775816714524616276221704042845)),
    (F(351104017200784386392209), F(309897966944945116194624198332593845)),
    (F(-427722660290928813983135), F(-1048576645526111528109185629948786727)),
    (F(954500781939375762742909), F(225326008863345220543071618783370945)),
    (F(423679598259676591990909), F(154829810959547852593332987635966145)),
    (F(1535808449095818094207905), F(1401421444080498380369785533616999513)),
    (F(444801887422056021535383), F(73569216148613399817347986859758945)),
    (F(-1206006015871044278678751), F(-740210245609217615143269452335454375)),
    (F(-192562292438693523617091), F(-911556889640548767064630159456313855)),
    (F(10508879668527356682921249), F(33851800053181168926568362825476385625)),
    (F(951514410733369555670349), F(216676520921276805299703311439049825)),
    (F(-7355680099955426717481581, 81), F(-605705671933225602690651446390633849125, 729)),
)

P0 = (
    F(-M),
    F(-1033237630189640270243631944200109375),
)

CALIBRATION_SUBSETS = {
    "basis": [0] + [1 << i for i in range(12)],
    "adjacent_pairs": [3 << i for i in range(11)] + [2049],
    "mixed_dense": [
        7,
        15,
        31,
        63,
        127,
        255,
        511,
        1023,
        2047,
        4095,
        1365,
        2730,
        585,
        1170,
        2340,
    ],
}

Point = Optional[tuple[F, F]]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def qstr(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def on_minimal(point: Point) -> bool:
    if point is None:
        return True
    x, y = point
    return y * y + x * y + y == x**3 - x**2 - A * x + B


def negate(point: Point) -> Point:
    if point is None:
        return None
    x, y = point
    return (x, -y - x - 1)


def add(p: Point, q: Point) -> Point:
    """General-Weierstrass addition for [a1,a2,a3,a4,a6]=[1,-1,1,-A,B]."""
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and y2 == -y1 - x1 - 1:
        return None
    if x1 != x2:
        lam = (y2 - y1) / (x2 - x1)
        nu = (y1 * x2 - y2 * x1) / (x2 - x1)
    else:
        den = 2 * y1 + x1 + 1
        if den == 0:
            return None
        lam = (3 * x1**2 - 2 * x1 - A - y1) / den
        nu = (-x1**3 - A * x1 + 2 * B - y1) / den
    x3 = lam * lam + lam + 1 - x1 - x2
    y3 = -(lam + 1) * x3 - nu - 1
    result = (x3, y3)
    assert on_minimal(result)
    return result


def double(point: Point) -> Point:
    return add(point, point)


def psi(point: Point) -> Point:
    if point is None:
        return None
    x, y = point
    X = F(25, U**2) * (x + M)
    Y = F(125, 2 * U**3) * (2 * y + x + 1)
    return (X, Y)


def psi_inverse(point: Point) -> Point:
    if point is None:
        return None
    X, Y = point
    x = F(U**2, 25) * X - M
    y = (F(2 * U**3, 125) * Y - x - 1) / 2
    return (x, y)


def on_scaled(point: Point) -> bool:
    if point is None:
        return True
    X, Y = point
    a, b, c = TRIPLE
    return Y * Y == (X + a * b) * (X + a * c) * (X + b * c)


def add_scaled(p: Point, q: Point) -> Point:
    """Independent addition on Y^2=X^3+s2*X^2+s1*X+s0."""
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and y2 == -y1:
        return None
    a, b, c = TRIPLE
    r1, r2, r3 = a * b, a * c, b * c
    s2 = r1 + r2 + r3
    s1 = r1 * r2 + r1 * r3 + r2 * r3
    if x1 != x2:
        lam = (y2 - y1) / (x2 - x1)
    else:
        if y1 == 0:
            return None
        lam = (3 * x1**2 + 2 * s2 * x1 + s1) / (2 * y1)
    x3 = lam * lam - s2 - x1 - x2
    y3 = -y1 + lam * (x1 - x3)
    result = (x3, y3)
    assert on_scaled(result)
    return result


def poly_mul(p: list[F], q: list[F]) -> list[F]:
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


def exact_square_root(value: F) -> Optional[F]:
    if value < 0:
        return None
    rn = math.isqrt(value.numerator)
    rd = math.isqrt(value.denominator)
    if rn * rn != value.numerator or rd * rd != value.denominator:
        return None
    return F(rn, rd)


def source_audit(source_path: Path) -> dict:
    archive = source_path.read_bytes()
    assert sha256_bytes(archive) == ARCHIVE_SHA256
    raw = gzip.decompress(archive)
    text = raw.decode("utf-8")
    lines = text.splitlines()
    assert len(lines) == 840
    assert "6125241375" in lines[396] and "273138178560" in lines[396]
    assert str(A) in lines[399]
    assert str(B) in lines[400]
    for i, (x, y) in enumerate(TORSION):
        line = lines[404 + i]
        assert qstr(x) in line and qstr(y) in line
    for i, (x, y) in enumerate(POINTS):
        line = lines[410 + i]
        assert qstr(x) in line and qstr(y) in line
    span_curve = ("\n".join(lines[184:192]) + "\n").encode("utf-8")
    span_data = ("\n".join(lines[395:422]) + "\n").encode("utf-8")
    return {
        "archive_path": source_path.as_posix(),
        "archive_sha256": sha256_bytes(archive),
        "decompressed_name": "highranktriples.tex",
        "decompressed_bytes": len(raw),
        "decompressed_sha256": sha256_bytes(raw),
        "line_count": len(lines),
        "coordinate_transform_lines": [185, 192],
        "coordinate_transform_span_sha256": sha256_bytes(span_curve),
        "rank12_data_lines": [396, 422],
        "rank12_data_span_sha256": sha256_bytes(span_data),
        "source_constants_match": True,
    }


def polynomial_map_audit() -> dict:
    a, b, c = TRIPLE
    alpha = F(25, U**2)
    beta = F(125, 2 * U**3)
    # (2y+x+1)^2 after eliminating y from the minimal equation.
    completed_square = [F(1 + 4 * B), F(2 - 4 * A), F(-3), F(4)]
    lhs = [beta * beta * coefficient for coefficient in completed_square]
    rhs = [F(1)]
    for root_constant in (a * b, a * c, b * c):
        rhs = poly_mul(rhs, [alpha * M + root_constant, alpha])
    assert lhs == rhs
    return {
        "alpha": qstr(alpha),
        "beta": qstr(beta),
        "completed_square_coefficients_ascending": [qstr(x) for x in completed_square],
        "target_coefficients_ascending": [qstr(x) for x in rhs],
        "polynomial_identity": True,
        "inverse_formula": "x=U^2*X/25-m; y=(2*U^3*Y/125-x-1)/2",
        "nonzero_scalars": alpha != 0 and beta != 0,
    }


def point_audit() -> dict:
    a, b, c = TRIPLE
    assert len(set(TRIPLE)) == 3 and all(x != 0 for x in TRIPLE)
    pair_products = (a * b, a * c, b * c)
    for product, root in zip(pair_products, PAIR_ROOTS):
        assert product + 1 == root * root

    torsion_rows = []
    expected_roots = {-a * b: "-ab", -a * c: "-ac", -b * c: "-bc"}
    seen_roots = set()
    for source_point in TORSION:
        assert on_minimal(source_point)
        assert 2 * source_point[1] + source_point[0] + 1 == 0
        image = psi(source_point)
        assert image is not None and image[1] == 0 and on_scaled(image)
        assert image[0] in expected_roots
        assert psi_inverse(image) == source_point
        seen_roots.add(image[0])
        torsion_rows.append(
            {
                "source": [qstr(source_point[0]), qstr(source_point[1])],
                "image": [qstr(image[0]), qstr(image[1])],
                "image_label": expected_roots[image[0]],
            }
        )
    assert seen_roots == set(expected_roots)

    assert on_minimal(P0)
    p0_image = psi(P0)
    assert p0_image == (F(0), a * b * c)
    assert psi_inverse(p0_image) == P0

    point_rows = []
    for i, point in enumerate(POINTS, 1):
        assert on_minimal(point)
        image = psi(point)
        assert on_scaled(image)
        assert psi_inverse(image) == point
        point_rows.append(
            {
                "label": f"P{i}",
                "minimal": [qstr(point[0]), qstr(point[1])],
                "on_minimal": True,
                "image_on_scaled": True,
                "roundtrip": True,
            }
        )

    coefficient_from_map = F(25, U**2) / (a * b * c)
    declared_coefficient = F(-6735029, 4874148659847186464642623440000)
    assert coefficient_from_map == declared_coefficient

    return {
        "triple": [qstr(x) for x in TRIPLE],
        "triple_distinct_nonzero": True,
        "pair_roots": [qstr(x) for x in PAIR_ROOTS],
        "pair_root_checks": [True, True, True],
        "minimal_model": {"a1": 1, "a2": -1, "a3": 1, "a4": str(-A), "a6": str(B)},
        "torsion_images": torsion_rows,
        "torsion_images_are_all_scaled_roots": True,
        "p0": [qstr(P0[0]), qstr(P0[1])],
        "p0_image": [qstr(p0_image[0]), qstr(p0_image[1])],
        "p0_image_is_0_abc": True,
        "published_points": point_rows,
        "published_points_checked": len(point_rows),
        "published_independence_reproved": False,
        "independence_needed_for_fixed_cube_exhaustion": False,
        "direct_d_coefficient": qstr(declared_coefficient),
        "direct_d_identity": "d=X/(abc)=direct_d_coefficient*(x+m)",
        "direct_d_formula_verified": True,
    }


def expression(index: int) -> Point:
    assert 0 <= index < 4096
    q = P0
    for i, point in enumerate(POINTS):
        if index & (1 << i):
            q = add(q, double(point))
    return q


def calibration_audit() -> dict:
    a, b, c = TRIPLE
    coefficient = F(-6735029, 4874148659847186464642623440000)
    used: set[int] = set()
    sections = {}
    for name, indices in CALIBRATION_SUBSETS.items():
        assert len(indices) == len(set(indices))
        assert not (used & set(indices))
        used.update(indices)
        rows = []
        for index in indices:
            q = expression(index)
            assert q is not None and on_minimal(q)
            image = psi(q)
            assert image is not None and on_scaled(image)
            scaled_q = psi(P0)
            for i, point in enumerate(POINTS):
                if index & (1 << i):
                    scaled_point = psi(point)
                    scaled_q = add_scaled(scaled_q, add_scaled(scaled_point, scaled_point))
            assert scaled_q == image
            d_from_image = image[0] / (a * b * c)
            d_direct = coefficient * (q[0] + M)
            assert d_from_image == d_direct
            roots = [exact_square_root(1 + t * d_direct) for t in TRIPLE]
            assert all(root is not None for root in roots)
            rows.append(
                {
                    "index": index,
                    "weight": index.bit_count(),
                    "minimal_x": qstr(q[0]),
                    "minimal_y": qstr(q[1]),
                    "d": qstr(d_direct),
                    "extension_roots": [qstr(root) for root in roots if root is not None],
                    "dual_group_law_match": True,
                }
            )
        sections[name] = {
            "indices": indices,
            "row_count": len(rows),
            "rows_sha256": sha256_bytes(canonical_json_bytes(rows)),
            "rows": rows,
        }
    assert len(used) == 40
    return {
        "bit_convention": "P1 is bit 0 and P12 is bit 11; index=sum(eps_i*2^(i-1))",
        "expression": "Q_index=P0+2*sum(eps_i*Pi), additions in increasing i",
        "subsets_are_pairwise_disjoint": True,
        "calibration_expression_count": len(used),
        "full_cube_enumerated": False,
        "sections": sections,
    }


def manifest_recommendation(calibration: dict) -> dict:
    return {
        "format": "rank12_boolean_cube_manifest_v1",
        "canonical_serialization": "UTF-8 canonical JSON, sorted keys, compact separators, final LF",
        "required_source_fields": [
            "archive relative path and SHA-256",
            "decompressed source SHA-256 and cited line spans",
            "prior-art query record and date",
        ],
        "required_math_fields": [
            "triple and three pair roots as reduced rational strings",
            "general Weierstrass coefficients [1,-1,1,-A,B]",
            "U, m, psi and inverse psi formulas",
            "P0, three torsion points with expected images, and P1 through P12",
            "direct d formula and induced-curve bridge citation",
        ],
        "required_enumeration_fields": {
            "bit_order": "P1 least-significant through P12 most-significant",
            "index_range": [0, 4095],
            "expression_count": 4096,
            "addition_order": "increasing point index",
            "infinity_sentinel": "INF",
            "rational_encoding": "reduced num/den with positive denominator",
            "exclusions": ["infinity", "d=0", "d=a", "d=b", "d=c"],
            "deduplication": "group equal d values and retain sorted provenance indices",
        },
        "required_ledger_fields": {
            "expression_tsv": "index, status, minimal_x_num, minimal_x_den, d_num, d_den",
            "value_tsv": "vertex_index, d_num, d_den, comma-separated provenance indices",
            "vertex_order": "strict increasing rational value",
            "edge_tsv": "i,j in lexicographic order with i<j",
            "graph_scope": "every unordered pair of retained deduplicated vertices",
            "terminal_fields": [
                "4096 expressions accounted for",
                "infinity/exclusion/duplicate counts",
                "deduplicated vertex count",
                "tested pair count n(n-1)/2",
                "edge count and K4 list",
                "SHA-256 for each ledger",
            ],
        },
        "required_engine_fields": [
            "primary and independent engine paths and SHA-256 values",
            "runtime version and command line",
            "start/end timestamps, exit codes, and owned process IDs",
        ],
        "required_acceptance_fields": [
            "all source/map/point referee assertions pass",
            "the three disjoint calibration ledgers match the referee hashes",
            "primary and independent expression and value ledgers match exactly",
            "primary and independent complete edge ledgers and K4 results match exactly",
            "every K4 passes both full seven-value verifiers",
            "NO_HIT is permitted only after all 4096 expressions and all retained pairs are accounted for",
        ],
        "calibration_subsets": {
            name: {
                "indices": section["indices"],
                "expected_rows_sha256": section["rows_sha256"],
            }
            for name, section in calibration["sections"].items()
        },
    }


def route_spec_audit(route_spec_path: Path) -> dict:
    spec = json.loads(route_spec_path.read_text(encoding="utf-8"))
    a, b, c = TRIPLE
    assert spec["schema"] == "rank12_boolean_cube_route/v1"
    assert spec["source"]["sha256"] == ARCHIVE_SHA256
    assert spec["source"]["local_path"].endswith("sources/highranktriples_2020_source.tar")
    assert spec["source"]["relevant_line_spans"] == [[185, 192], [396, 422]]
    assert spec["triple"]["values"] == [qstr(x) for x in TRIPLE]
    assert spec["triple"]["pair_roots"] == [qstr(x) for x in PAIR_ROOTS]
    assert spec["triple"]["pair_root_labels"] == ["ab", "ac", "bc"]
    assert spec["triple"]["abc"] == qstr(a * b * c)
    assert spec["minimal_model"]["a1"] == "1"
    assert spec["minimal_model"]["a2"] == "-1"
    assert spec["minimal_model"]["a3"] == "1"
    assert spec["minimal_model"]["a4"] == str(-A)
    assert spec["minimal_model"]["a6"] == str(B)
    assert spec["isomorphism"]["U"] == str(U)
    assert spec["isomorphism"]["m"] == str(M)
    assert spec["isomorphism"]["X_formula"] == "25*(x+m)/U^2"
    assert spec["isomorphism"]["Y_formula"] == "125*(2*y+x+1)/(2*U^3)"
    assert spec["isomorphism"]["inverse_x_formula"] == "U^2*X/25-m"
    assert spec["isomorphism"]["inverse_y_formula"] == "U^3*Y/125-(x+1)/2"
    assert spec["isomorphism"]["P0"] == [qstr(P0[0]), qstr(P0[1])]
    assert spec["isomorphism"]["P0_image"] == ["0", qstr(a * b * c)]
    assert spec["isomorphism"]["d_from_minimal_x"]["coefficient"] == qstr(
        F(-6735029, 4874148659847186464642623440000)
    )
    assert spec["points"] == [[qstr(x), qstr(y)] for x, y in POINTS]
    assert spec["cube"]["dimension"] == 12
    assert spec["cube"]["mask_min"] == 0
    assert spec["cube"]["mask_max"] == 4095
    assert spec["cube"]["declared_expressions"] == 4096
    assert spec["search_contract"]["target_clique_size"] == 4
    assert spec["search_contract"]["candidate_tuple_size"] == 7
    assert spec["search_contract"]["candidate_pair_count"] == 21

    actual_images = []
    labels = {-a * b: "-ab", -a * c: "-ac", -b * c: "-bc"}
    for point in TORSION:
        image = psi(point)
        assert image is not None
        actual_images.append(
            {
                "minimal_point": [qstr(point[0]), qstr(point[1])],
                "scaled_image": [qstr(image[0]), qstr(image[1])],
                "scaled_image_label": labels[image[0]],
            }
        )
    listed_map = {
        (
            row["label"],
            tuple(row["minimal_point"]),
            tuple(row["scaled_induced_point"]),
        )
        for row in spec["isomorphism"]["torsion_map"]
    }
    expected_map = {
        (
            row["scaled_image_label"],
            tuple(row["minimal_point"]),
            tuple(row["scaled_image"]),
        )
        for row in actual_images
    }
    assert listed_map == expected_map
    return {
        "path": route_spec_path.as_posix(),
        "sha256": sha256_bytes(route_spec_path.read_bytes()),
        "arithmetic_constants_match": True,
        "source_points_match": True,
        "cube_contract_match": True,
        "status": "PASS",
        "actual_torsion_images": actual_images,
        "issues": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--route-spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = source_audit(args.source)
    polynomial_map = polynomial_map_audit()
    points = point_audit()
    calibration = calibration_audit()
    route_spec = route_spec_audit(args.route_spec)
    report = {
        "status": "PASS",
        "scope": "source, triple, map, torsion, P0, 12 point memberships, direct d formula, 40 calibration expressions",
        "source": source,
        "polynomial_map": polynomial_map,
        "point_audit": points,
        "route_spec_audit": route_spec,
        "calibration": calibration,
        "recommended_manifest_schema": manifest_recommendation(calibration),
        "logical_findings": {
            "fixed_cube_is_finite": True,
            "declared_expression_count": 4096,
            "point_independence_is_not_required_for_declared_expression_exhaustion": True,
            "source_independence_claim_was_not_reproved": True,
            "negative_result_scope": "only the frozen 4096 group expressions and their complete retained compatibility graph",
            "arithmetic_issue_found": False,
            "logical_issue_found": False,
            "route_spec_semantic_issue_found": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True).encode("ascii") + b"\n")
    print(json.dumps({"status": report["status"], "output": str(args.output), "sha256": sha256_bytes(args.output.read_bytes())}, sort_keys=True))


if __name__ == "__main__":
    main()
