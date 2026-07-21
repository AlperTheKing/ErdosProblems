#!/usr/bin/env python3
"""Primary exact engine for the frozen rank-12 Boolean cube.

The full ``search`` command is guarded by ``--allow-full-search``.  The
``preflight`` command checks the published model, the exact isomorphism, all
twelve published points, the rational Diophantine base triple, and a fixed
set of separated Boolean masks without consuming the full 4096-point cube.

Points are represented on the general Weierstrass model

    y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6.

No elliptic-curve package is imported.  All curve arithmetic uses
``fractions.Fraction`` and the chord-and-tangent formulas for this model.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from verify_septuple_independent import verify_septuple
from verify_tuple import verify_tuple


PROBLEM_DIR = Path(__file__).resolve().parents[1]
ROUTE_ID = "fixed-rank12-boolean-cube"
EXPRESSION_COUNT = 1 << 12
PRIMARY_FULL_COMMAND = (
    "C:/Users/a/AppData/Local/Programs/Python/Python312/python.exe "
    "problems_external/rational_diophantine_septuple/engine/rank12_cube_primary.py search "
    "--manifest problems_external/rational_diophantine_septuple/runs/"
    "rank12_boolean_cube_20260720T144330/manifest.json --output "
    "problems_external/rational_diophantine_septuple/runs/"
    "rank12_boolean_cube_20260720T144330/primary_full/summary.json --allow-full-search"
)

A = 1444491707528591356856089186460491195711268950880
B = 559921583779625421248683584939561762456224290170437461555851482041439747
U = 7138564997564
M_TRANSLATION = 955655055996458012197251

BASE_TRIPLE = (
    Fraction(6125241375, 11907531272),
    Fraction(5535371271425, 14277129995128),
    Fraction(-273138178560, 153430695649),
)
BASE_PAIR_ROOTS = (
    Fraction(13040990647, 11907531272),
    Fraction(1955029, 6735029),
    Fraction(4494674021, 8075299771),
)

P0 = (
    Fraction(-M_TRANSLATION),
    Fraction(-1033237630189640270243631944200109375),
)

PUBLISHED_POINTS = (
    (Fraction(158850932500649609134809), Fraction(578334775816714524616276221704042845)),
    (Fraction(351104017200784386392209), Fraction(309897966944945116194624198332593845)),
    (Fraction(-427722660290928813983135), Fraction(-1048576645526111528109185629948786727)),
    (Fraction(954500781939375762742909), Fraction(225326008863345220543071618783370945)),
    (Fraction(423679598259676591990909), Fraction(154829810959547852593332987635966145)),
    (Fraction(1535808449095818094207905), Fraction(1401421444080498380369785533616999513)),
    (Fraction(444801887422056021535383), Fraction(73569216148613399817347986859758945)),
    (Fraction(-1206006015871044278678751), Fraction(-740210245609217615143269452335454375)),
    (Fraction(-192562292438693523617091), Fraction(-911556889640548767064630159456313855)),
    (Fraction(10508879668527356682921249), Fraction(33851800053181168926568362825476385625)),
    (Fraction(951514410733369555670349), Fraction(216676520921276805299703311439049825)),
    (
        Fraction(-7355680099955426717481581, 81),
        Fraction(-605705671933225602690651446390633849125, 729),
    ),
)

PUBLISHED_TORSION = (
    (
        Fraction(910954389920845836020349),
        Fraction(-455477194960422918010175),
    ),
    (
        Fraction(-5448727291190824028230629, 4),
        Fraction(5448727291190824028230625, 8),
    ),
    (
        Fraction(451227432876860171037309),
        Fraction(-225613716438430085518655),
    ),
)

CALIBRATION_GROUPS = {
    "basis_and_complements": (
        0,
        4095,
        *(1 << bit for bit in range(12)),
        *(4095 ^ (1 << bit) for bit in range(12)),
    ),
    "lower_block": tuple(range(64)),
    "lcg64": tuple((1103515245 * index + 12345) & 4095 for index in range(64)),
    "upper_block": tuple(range(4032, 4096)),
}

REFEREE_SUBSETS = {
    "basis": {
        "indices": (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048),
        "rows_sha256": "C38DA452175F4227DE69A0B1FFB905CC9D1F5146989BFC4FD77CA4C3C0D5F4D2",
    },
    "adjacent_pairs": {
        "indices": (3, 6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 2049),
        "rows_sha256": "C635BEE90AE9095C03A299B44FCC5AD511CBE21E531A7EDFC6626029EE9A8E85",
    },
    "mixed_dense": {
        "indices": (7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 1365, 2730, 585, 1170, 2340),
        "rows_sha256": "5AC00DACA027C7A7575B34249C6987B02B45EC3C9973214F575D40AEF6A1BB94",
    },
}

EXPECTED_CROSS_PREFLIGHT_HASHES = {
    "expression": "7B9A7A490979E305331677F63C6D29BFA459E494A04A18AE12CE6C9EEC7ABF80",
    "value": "A6FFA20652720086A3148F322AC7687FED7918C951A78291B06FBC1DF51B9873",
    "edge": "6B4C557677870240694CDBF16673082F48FBEBC96D4C1FF129FAD935137B5FB8",
}

MODULAR_FILTER_PRIMES = (
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
)


Point = tuple[Fraction, Fraction] | None


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def point_json(point: Point) -> list[str] | None:
    if point is None:
        return None
    return [fraction_text(point[0]), fraction_text(point[1])]


def parse_point(value: Any) -> Point:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"invalid point: {value!r}")
    return Fraction(value[0]), Fraction(value[1])


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


def write_gzip_bytes(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(payload)
        raw.flush()
        os.fsync(raw.fileno())
    os.replace(temporary, path)
    return sha256_file(path)


def write_gzip_lines(path: Path, lines: Iterable[str]) -> tuple[str, str, int]:
    """Write canonical ASCII lines and return file hash, content hash, count."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    content_digest = hashlib.sha256()
    count = 0
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            for line in lines:
                encoded = line.encode("ascii")
                content_digest.update(encoded)
                zipped.write(encoded)
                count += 1
        raw.flush()
        os.fsync(raw.fileno())
    os.replace(temporary, path)
    return sha256_file(path), content_digest.hexdigest().upper(), count


@dataclass(frozen=True)
class GeneralWeierstrassCurve:
    a1: Fraction
    a2: Fraction
    a3: Fraction
    a4: Fraction
    a6: Fraction

    def is_on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (
            y * y + self.a1 * x * y + self.a3 * y
            == x * x * x + self.a2 * x * x + self.a4 * x + self.a6
        )

    def negate(self, point: Point) -> Point:
        if point is None:
            return None
        x, y = point
        return x, -y - self.a1 * x - self.a3

    def double(self, point: Point) -> Point:
        if point is None:
            return None
        x, y = point
        denominator = 2 * y + self.a1 * x + self.a3
        if denominator == 0:
            return None
        slope = (
            3 * x * x + 2 * self.a2 * x + self.a4 - self.a1 * y
        ) / denominator
        intercept = (
            -x * x * x + self.a4 * x + 2 * self.a6 - self.a3 * y
        ) / denominator
        x3 = slope * slope + self.a1 * slope - self.a2 - 2 * x
        y3 = -(slope + self.a1) * x3 - intercept - self.a3
        result = x3, y3
        if not self.is_on_curve(result):
            raise ArithmeticError("doubling formula produced a point off the curve")
        return result

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2:
            if y1 == y2:
                return self.double(left)
            if right == self.negate(left):
                return None
            raise ArithmeticError("same x-coordinate has neither equal nor opposite y")
        slope = (y2 - y1) / (x2 - x1)
        intercept = (y1 * x2 - y2 * x1) / (x2 - x1)
        x3 = slope * slope + self.a1 * slope - self.a2 - x1 - x2
        y3 = -(slope + self.a1) * x3 - intercept - self.a3
        result = x3, y3
        if not self.is_on_curve(result):
            raise ArithmeticError("addition formula produced a point off the curve")
        return result

    def scalar_mul(self, multiplier: int, point: Point) -> Point:
        if multiplier < 0:
            return self.scalar_mul(-multiplier, self.negate(point))
        result: Point = None
        addend = point
        value = multiplier
        while value:
            if value & 1:
                result = self.add(result, addend)
            addend = self.double(addend)
            value >>= 1
        return result


CURVE = GeneralWeierstrassCurve(
    Fraction(1), Fraction(-1), Fraction(1), Fraction(-A), Fraction(B)
)


def psi_to_scaled_curve(point: Point) -> Point:
    """Apply the frozen origin-preserving map Emin -> E'."""

    if point is None:
        return None
    x, y = point
    scaled_x = Fraction(25) * (x + M_TRANSLATION) / (U * U)
    scaled_y = Fraction(125) * (2 * y + x + 1) / (2 * U**3)
    return scaled_x, scaled_y


def is_on_scaled_curve(point: Point) -> bool:
    if point is None:
        return True
    x, y = point
    a, b, c = BASE_TRIPLE
    return y * y == (x + a * b) * (x + a * c) * (x + b * c)


def extension_value_from_minimal_x(x: Fraction) -> Fraction:
    return Fraction(-6735029) * (x + M_TRANSLATION) / Fraction(
        4874148659847186464642623440000
    )


def rational_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    if (
        numerator_root * numerator_root != value.numerator
        or denominator_root * denominator_root != value.denominator
    ):
        return None
    return Fraction(numerator_root, denominator_root)


def compatible(left: Fraction, right: Fraction) -> bool:
    """Test left*right+1 by the equivalent integer product criterion."""

    numerator = left.numerator * right.numerator + left.denominator * right.denominator
    denominator = left.denominator * right.denominator
    if numerator < 0:
        return False
    witness = numerator * denominator
    root = isqrt(witness)
    return root * root == witness


def direct_base_compatibility(value: Fraction) -> tuple[bool, bool, bool]:
    return tuple(compatible(value, base) for base in BASE_TRIPLE)  # type: ignore[return-value]


def point_for_mask(mask: int, doubled_points: Sequence[Point]) -> Point:
    if not 0 <= mask < EXPRESSION_COUNT:
        raise ValueError("Boolean mask must be in 0..4095")
    point: Point = P0
    for bit, direction in enumerate(doubled_points):
        if mask & (1 << bit):
            point = CURVE.add(point, direction)
    return point


def enumerate_gray_cube(doubled_points: Sequence[Point]) -> list[Point]:
    if len(doubled_points) != 12:
        raise ValueError("the frozen cube requires twelve doubled points")
    by_mask: list[Point] = [None] * EXPRESSION_COUNT
    point: Point = P0
    previous_gray = 0
    for step in range(EXPRESSION_COUNT):
        gray = step ^ (step >> 1)
        if step:
            changed = gray ^ previous_gray
            if changed == 0 or changed & (changed - 1):
                raise ArithmeticError("Gray step did not flip exactly one bit")
            bit = changed.bit_length() - 1
            direction = doubled_points[bit]
            if gray & changed:
                point = CURVE.add(point, direction)
            else:
                point = CURVE.add(point, CURVE.negate(direction))
        if not CURVE.is_on_curve(point):
            raise ArithmeticError(f"mask {gray} is off the minimal model")
        by_mask[gray] = point
        previous_gray = gray
    if len({step ^ (step >> 1) for step in range(EXPRESSION_COUNT)}) != EXPRESSION_COUNT:
        raise ArithmeticError("Gray enumeration did not visit all Boolean masks")
    return by_mask


def _compact_fraction(value: Fraction) -> str:
    return str(value)


def _compact_point(point: Point) -> list[str] | None:
    if point is None:
        return None
    return [_compact_fraction(point[0]), _compact_fraction(point[1])]


def _require_exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    observed = set(value)
    if observed != keys:
        missing = sorted(keys - observed)
        unknown = sorted(observed - keys)
        raise ValueError(f"{label} keys mismatch; missing={missing}, unknown={unknown}")
    return value


def _expected_route_spec() -> dict[str, Any]:
    a, b, c = BASE_TRIPLE
    torsion_order = (PUBLISHED_TORSION[2], PUBLISHED_TORSION[0], PUBLISHED_TORSION[1])
    torsion_labels = ("-bc", "-ac", "-ab")
    torsion_scaled = tuple(psi_to_scaled_curve(point) for point in torsion_order)
    return {
        "schema": "rank12_boolean_cube_route/v1",
        "route": "fixed rank-12 Boolean cube",
        "source": {
            "citation": "A. Dujella and J. C. Peral, High rank elliptic curves induced by rational Diophantine triples, arXiv:2005.10706",
            "url": "https://arxiv.org/abs/2005.10706",
            "local_path": "problems_external/rational_diophantine_septuple/sources/highranktriples_2020_source.tar",
            "container": "gzip-compressed single TeX member highranktriples.tex",
            "sha256": "3C0F200A895B4460E5A206112321AE05CBD7EA58263B369753FC68B1A7B8218E",
            "relevant_line_spans": [[185, 192], [396, 422]],
        },
        "triple": {
            "values": [_compact_fraction(value) for value in BASE_TRIPLE],
            "pair_roots": [_compact_fraction(value) for value in BASE_PAIR_ROOTS],
            "pair_root_labels": ["ab", "ac", "bc"],
            "abc": _compact_fraction(a * b * c),
        },
        "minimal_model": {
            "equation": "y^2 + x*y + y = x^3 - x^2 + a4*x + a6",
            "a1": "1",
            "a2": "-1",
            "a3": "1",
            "a4": str(-A),
            "a6": str(B),
        },
        "isomorphism": {
            "direction": "minimal model to scaled induced curve",
            "scaled_induced_equation": "Y^2 = (X+a*b)*(X+a*c)*(X+b*c)",
            "U": str(U),
            "m": str(M_TRANSLATION),
            "X_formula": "25*(x+m)/U^2",
            "Y_formula": "125*(2*y+x+1)/(2*U^3)",
            "inverse_x_formula": "U^2*X/25-m",
            "inverse_y_formula": "U^3*Y/125-(x+1)/2",
            "P0": _compact_point(P0),
            "P0_image": ["0", _compact_fraction(a * b * c)],
            "d_from_minimal_x": {
                "coefficient": "-6735029/4874148659847186464642623440000",
                "formula": "coefficient*(x+m)",
            },
            "torsion_map": [
                {
                    "label": label,
                    "minimal_point": _compact_point(point),
                    "scaled_induced_point": _compact_point(image),
                }
                for label, point, image in zip(
                    torsion_labels, torsion_order, torsion_scaled, strict=True
                )
            ],
        },
        "points": [_compact_point(point) for point in PUBLISHED_POINTS],
        "cube": {
            "dimension": 12,
            "mask_min": 0,
            "mask_max": 4095,
            "declared_expressions": 4096,
            "formula": "Q_mask = P0 + 2*sum(bit_i(mask)*P_(i+1), i=0..11)",
            "bit_order": "least significant bit selects the first listed point",
        },
        "search_contract": {
            "extension_value": "d = x(psi(Q))/(a*b*c)",
            "required_base_square_tests_per_finite_value": 3,
            "excluded_values": "infinity, zero, the three fixed triple values, and duplicate extension values",
            "graph_edge": "d_i*d_j+1 is a rational square",
            "target_clique_size": 4,
            "candidate_tuple_size": 7,
            "candidate_pair_count": 21,
            "primary_verifier": "engine/verify_tuple.py --expect-size 7",
            "independent_verifier": "engine/verify_septuple_independent.py",
        },
        "exit_contract": {
            "success": "a K4 candidate accepted by both full verifiers",
            "negative": "matching exhaustive ledgers and graph results with no K4; scoped NO_HIT only",
            "failure": "any point, map, expression-count, ledger, graph, or verifier disagreement",
            "forbidden_extensions": "cube translation, coefficient enlargement, other rank-12 examples, or rank-family scans",
        },
    }


def validate_route_spec(path: Path) -> tuple[dict[str, Any], str]:
    route_hash = sha256_file(path)
    route_spec = json.loads(path.read_text(encoding="utf-8"))
    _require_exact_keys(
        route_spec,
        {"schema", "route", "source", "triple", "minimal_model", "isomorphism", "points", "cube", "search_contract", "exit_contract"},
        "route_spec",
    )
    _require_exact_keys(
        route_spec["source"],
        {"citation", "url", "local_path", "container", "sha256", "relevant_line_spans"},
        "route_spec.source",
    )
    _require_exact_keys(
        route_spec["triple"],
        {"values", "pair_roots", "pair_root_labels", "abc"},
        "route_spec.triple",
    )
    _require_exact_keys(
        route_spec["minimal_model"],
        {"equation", "a1", "a2", "a3", "a4", "a6"},
        "route_spec.minimal_model",
    )
    iso = _require_exact_keys(
        route_spec["isomorphism"],
        {
            "direction", "scaled_induced_equation", "U", "m", "X_formula", "Y_formula",
            "inverse_x_formula", "inverse_y_formula", "P0", "P0_image",
            "d_from_minimal_x", "torsion_map",
        },
        "route_spec.isomorphism",
    )
    _require_exact_keys(
        iso["d_from_minimal_x"], {"coefficient", "formula"},
        "route_spec.isomorphism.d_from_minimal_x",
    )
    if not isinstance(iso["torsion_map"], list) or len(iso["torsion_map"]) != 3:
        raise ValueError("route_spec.isomorphism.torsion_map must have three rows")
    for index, row in enumerate(iso["torsion_map"]):
        _require_exact_keys(row, {"label", "minimal_point", "scaled_induced_point"}, f"torsion_map[{index}]")
    _require_exact_keys(
        route_spec["cube"],
        {"dimension", "mask_min", "mask_max", "declared_expressions", "formula", "bit_order"},
        "route_spec.cube",
    )
    _require_exact_keys(
        route_spec["search_contract"],
        {
            "extension_value", "required_base_square_tests_per_finite_value", "excluded_values",
            "graph_edge", "target_clique_size", "candidate_tuple_size", "candidate_pair_count",
            "primary_verifier", "independent_verifier",
        },
        "route_spec.search_contract",
    )
    _require_exact_keys(
        route_spec["exit_contract"],
        {"success", "negative", "failure", "forbidden_extensions"},
        "route_spec.exit_contract",
    )
    expected = _expected_route_spec()
    if route_spec != expected:
        raise ValueError("route_spec values differ from the compiled frozen constants")
    source_path = PROBLEM_DIR.parents[1] / route_spec["source"]["local_path"]
    if not source_path.is_file():
        raise ValueError(f"frozen primary source is missing: {source_path}")
    if sha256_file(source_path) != route_spec["source"]["sha256"]:
        raise ValueError("frozen primary-source SHA-256 mismatch")
    return route_spec, route_hash


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789ABCDEF" for character in value)
    )


def _repo_path(relative: str) -> Path:
    return PROBLEM_DIR.parents[1] / relative


def validate_manifest(
    path: Path, *, allow_pending: bool = False
) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    manifest_hash = sha256_file(path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    _require_exact_keys(
        manifest,
        {"schema", "route_spec", "engines", "verifiers", "runtime", "calibration", "modular_filter", "search", "outputs"},
        "manifest",
    )
    if manifest["schema"] != "rank12_boolean_cube_manifest/v1":
        raise ValueError("manifest schema mismatch")
    route_contract = _require_exact_keys(
        manifest["route_spec"], {"path", "sha256"}, "manifest.route_spec"
    )
    engines = _require_exact_keys(
        manifest["engines"], {"primary", "independent", "referee"}, "manifest.engines"
    )
    _require_exact_keys(engines["primary"], {"path", "sha256"}, "manifest.engines.primary")
    _require_exact_keys(engines["independent"], {"path", "sha256"}, "manifest.engines.independent")
    _require_exact_keys(
        engines["referee"], {"path", "sha256", "report_path", "report_sha256"},
        "manifest.engines.referee",
    )
    verifiers = _require_exact_keys(
        manifest["verifiers"], {"primary", "independent"}, "manifest.verifiers"
    )
    for name in ("primary", "independent"):
        _require_exact_keys(verifiers[name], {"path", "sha256"}, f"manifest.verifiers.{name}")
    runtime = _require_exact_keys(
        manifest["runtime"],
        {"implementation", "version", "executable", "primary_command", "independent_command"},
        "manifest.runtime",
    )
    calibration = _require_exact_keys(
        manifest["calibration"],
        {"referee_subsets", "cross_engine_subsets", "canonical_row", "canonical_serialization"},
        "manifest.calibration",
    )
    referee_subsets = _require_exact_keys(
        calibration["referee_subsets"], set(REFEREE_SUBSETS),
        "manifest.calibration.referee_subsets",
    )
    for name in REFEREE_SUBSETS:
        _require_exact_keys(
            referee_subsets[name], {"indices", "expected_rows_sha256"},
            f"manifest.calibration.referee_subsets.{name}",
        )
    cross = _require_exact_keys(
        calibration["cross_engine_subsets"],
        {"basis_and_complements", "lower_block", "lcg64", "upper_block", "union_count"},
        "manifest.calibration.cross_engine_subsets",
    )
    _require_exact_keys(cross["basis_and_complements"], {"definition", "count"}, "cross.basis_and_complements")
    _require_exact_keys(cross["lower_block"], {"range_inclusive", "count"}, "cross.lower_block")
    _require_exact_keys(cross["lcg64"], {"formula", "i_range_inclusive", "count"}, "cross.lcg64")
    _require_exact_keys(cross["upper_block"], {"range_inclusive", "count"}, "cross.upper_block")
    modular = _require_exact_keys(
        manifest["modular_filter"],
        {"primes", "rule", "exact_confirmation_of_every_retained_pair"},
        "manifest.modular_filter",
    )
    search = _require_exact_keys(
        manifest["search"],
        {
            "mask_min", "mask_max", "declared_expressions", "addition_order", "bit_order",
            "infinity_sentinel", "rational_encoding", "deduplication", "excluded_values",
            "base_square_tests_per_finite_value", "graph_scope", "target_clique_size",
            "candidate_tuple_size", "candidate_pair_count", "no_hit_scope",
        },
        "manifest.search",
    )
    _require_exact_keys(
        manifest["outputs"],
        {"primary_dir", "independent_dir", "comparison_path", "terminal_referee_path"},
        "manifest.outputs",
    )

    expected_route_path = "problems_external/rational_diophantine_septuple/runs/rank12_boolean_cube_20260720T144330/route_spec.json"
    if route_contract["path"] != expected_route_path:
        raise ValueError("manifest route_spec path mismatch")
    route_path = _repo_path(route_contract["path"])
    route_spec, route_hash = validate_route_spec(route_path)
    if route_contract["sha256"] != route_hash:
        raise ValueError("manifest route_spec SHA-256 mismatch")

    expected_engine_paths = {
        "primary": "problems_external/rational_diophantine_septuple/engine/rank12_cube_primary.py",
        "independent": "problems_external/rational_diophantine_septuple/engine/rank12_cube_independent.py",
    }
    for name, expected_path in expected_engine_paths.items():
        contract = engines[name]
        if contract["path"] != expected_path:
            raise ValueError(f"manifest {name} engine path mismatch")
        actual_path = _repo_path(contract["path"])
        if not actual_path.is_file():
            if allow_pending and contract["sha256"] == "PENDING":
                continue
            raise ValueError(f"manifest {name} engine is missing")
        observed = sha256_file(actual_path)
        if contract["sha256"] == "PENDING" and allow_pending:
            continue
        if not _is_sha256(contract["sha256"]) or contract["sha256"] != observed:
            raise ValueError(f"manifest {name} engine SHA-256 mismatch")

    observed_engine_hash = sha256_file(Path(__file__).resolve())
    if engines["primary"]["sha256"] not in {"PENDING", observed_engine_hash}:
        raise ValueError("manifest primary engine does not identify this file")

    expected_referee = {
        "path": "problems_external/rational_diophantine_septuple/engine/referee_rank12_cube.py",
        "sha256": "F076E26699F3BD856511B0072B6CE73BB85B006FA06BA24B6BED36659F68671F",
        "report_path": "problems_external/rational_diophantine_septuple/runs/rank12_boolean_cube_20260720T144330/referee_report.json",
        "report_sha256": "B242E3107ADD2D6D681420B91BC86A172CB25CAA9276F0A09F348AE9F92C39CC",
    }
    if engines["referee"] != expected_referee:
        raise ValueError("manifest referee contract mismatch")
    for key in ("path", "report_path"):
        target = _repo_path(engines["referee"][key])
        hash_key = "sha256" if key == "path" else "report_sha256"
        if not target.is_file() or sha256_file(target) != engines["referee"][hash_key]:
            raise ValueError(f"manifest referee {key} hash mismatch")

    expected_verifiers = {
        "primary": {
            "path": "problems_external/rational_diophantine_septuple/engine/verify_tuple.py",
            "sha256": "E0B86F53FFA3769EBF2D37F5571DC20414272DC0024944E75E61F217DAD36D33",
        },
        "independent": {
            "path": "problems_external/rational_diophantine_septuple/engine/verify_septuple_independent.py",
            "sha256": "0750D1B36B8ADCCC191072BE4C2011AA7126986F3E16EAD64BE2CB17FB934679",
        },
    }
    if verifiers != expected_verifiers:
        raise ValueError("manifest verifier contract mismatch")
    for contract in verifiers.values():
        if sha256_file(_repo_path(contract["path"])) != contract["sha256"]:
            raise ValueError("manifest verifier file hash mismatch")

    if (
        runtime["implementation"] != "CPython"
        or runtime["version"] != ".".join(str(part) for part in sys.version_info[:3])
        or Path(runtime["executable"]).resolve() != Path(sys.executable).resolve()
    ):
        raise ValueError("manifest runtime does not match the active interpreter")
    if not allow_pending and (
        runtime["primary_command"] == "PENDING"
        or runtime["independent_command"] == "PENDING"
    ):
        raise ValueError("full search is forbidden while runtime commands are PENDING")
    if runtime["primary_command"] not in {"PENDING", PRIMARY_FULL_COMMAND}:
        raise ValueError("manifest primary command mismatch")
    if not allow_pending and runtime["primary_command"] != PRIMARY_FULL_COMMAND:
        raise ValueError("full search requires the frozen primary command")

    for name, expected in REFEREE_SUBSETS.items():
        observed = referee_subsets[name]
        if observed["indices"] != list(expected["indices"]) or observed["expected_rows_sha256"] != expected["rows_sha256"]:
            raise ValueError(f"manifest referee subset mismatch: {name}")
    expected_cross = {
        "basis_and_complements": {
            "definition": "[0,4095] + [1<<i for i=0..11] + [4095^(1<<i) for i=0..11]",
            "count": 26,
        },
        "lower_block": {"range_inclusive": [0, 63], "count": 64},
        "lcg64": {"formula": "(1103515245*i+12345)&4095", "i_range_inclusive": [0, 63], "count": 64},
        "upper_block": {"range_inclusive": [4032, 4095], "count": 64},
        "union_count": 201,
    }
    if cross != expected_cross:
        raise ValueError("manifest cross-engine calibration subsets mismatch")
    if (
        calibration["canonical_row"] != "mask,status,minimal_x_num,minimal_x_den,d_num,d_den"
        or calibration["canonical_serialization"] != "UTF-8 canonical JSON, sorted keys, compact separators, final LF"
    ):
        raise ValueError("manifest calibration serialization mismatch")
    expected_modular = {
        "primes": list(MODULAR_FILTER_PRIMES),
        "rule": "skip a prime when a denominator is zero modulo p; otherwise reject a pair only when d_i*d_j+1 is a quadratic nonresidue",
        "exact_confirmation_of_every_retained_pair": True,
    }
    if modular != expected_modular:
        raise ValueError("manifest modular filter mismatch")
    expected_search = {
        "mask_min": 0,
        "mask_max": 4095,
        "declared_expressions": 4096,
        "addition_order": "increasing point index",
        "bit_order": "P1 is least significant and P12 is most significant",
        "infinity_sentinel": "INF",
        "rational_encoding": "reduced num/den with positive denominator",
        "deduplication": "sort by rational d and retain all provenance masks",
        "excluded_values": ["infinity", "d=0", "d=a", "d=b", "d=c"],
        "base_square_tests_per_finite_value": 3,
        "graph_scope": "every unordered pair of retained deduplicated values",
        "target_clique_size": 4,
        "candidate_tuple_size": 7,
        "candidate_pair_count": 21,
        "no_hit_scope": "only the frozen 4096 expressions and their complete retained compatibility graph",
    }
    if search != expected_search:
        raise ValueError("manifest search contract mismatch")
    expected_outputs = {
        "primary_dir": "problems_external/rational_diophantine_septuple/runs/rank12_boolean_cube_20260720T144330/primary_full",
        "independent_dir": "problems_external/rational_diophantine_septuple/runs/rank12_boolean_cube_20260720T144330/independent_full",
        "comparison_path": "problems_external/rational_diophantine_septuple/runs/rank12_boolean_cube_20260720T144330/comparison.json",
        "terminal_referee_path": "problems_external/rational_diophantine_septuple/runs/rank12_boolean_cube_20260720T144330/terminal_referee.json",
    }
    if manifest["outputs"] != expected_outputs:
        raise ValueError("manifest output contract mismatch")
    return manifest, manifest_hash, route_spec, route_hash


def model_preflight() -> dict[str, Any]:
    if not CURVE.is_on_curve(P0):
        raise ArithmeticError("P0 is not on the published minimal model")
    for index, point in enumerate(PUBLISHED_POINTS, start=1):
        if not CURVE.is_on_curve(point):
            raise ArithmeticError(f"published P{index} is off the minimal model")
        image = psi_to_scaled_curve(point)
        if not is_on_scaled_curve(image):
            raise ArithmeticError(f"image of published P{index} is off E'")

    a, b, c = BASE_TRIPLE
    observed_pair_roots = (
        rational_square_root(a * b + 1),
        rational_square_root(a * c + 1),
        rational_square_root(b * c + 1),
    )
    if observed_pair_roots != BASE_PAIR_ROOTS:
        raise ArithmeticError("base-triple pair roots disagree with the frozen roots")

    p0_image = psi_to_scaled_curve(P0)
    if p0_image != (Fraction(0), a * b * c):
        raise ArithmeticError("P0 does not map to (0,abc)")
    if extension_value_from_minimal_x(P0[0]) != 0:
        raise ArithmeticError("the extension map does not send P0 to d=0")

    torsion_images: list[Point] = []
    for index, point in enumerate(PUBLISHED_TORSION, start=1):
        if not CURVE.is_on_curve(point):
            raise ArithmeticError(f"published torsion point {index} is off Emin")
        if CURVE.double(point) is not None:
            raise ArithmeticError(f"published torsion point {index} is not 2-torsion")
        image = psi_to_scaled_curve(point)
        if image is None or image[1] != 0 or not is_on_scaled_curve(image):
            raise ArithmeticError(f"torsion image {index} is not a 2-torsion point on E'")
        torsion_images.append(image)
    expected_torsion_x = {-a * b, -a * c, -b * c}
    if {point[0] for point in torsion_images if point is not None} != expected_torsion_x:
        raise ArithmeticError("the three torsion images do not match -ab,-ac,-bc")

    map_scale = Fraction(25, U * U) / (a * b * c)
    declared_scale = Fraction(-6735029, 4874148659847186464642623440000)
    if map_scale != declared_scale:
        raise ArithmeticError("d-from-x formula disagrees with X/(abc)")

    return {
        "base_pair_roots": [fraction_text(root) for root in observed_pair_roots if root is not None],
        "p0_image": point_json(p0_image),
        "torsion_images": [point_json(point) for point in torsion_images],
        "published_point_count": len(PUBLISHED_POINTS),
        "published_points_on_both_models": True,
        "map_scale": fraction_text(map_scale),
    }


@dataclass(frozen=True)
class ExpressionRecord:
    mask: int
    status: str
    point: Point
    d: Fraction | None


def classify_expression(mask: int, point: Point) -> ExpressionRecord:
    if point is None:
        return ExpressionRecord(mask, "INF", None, None)
    d_value = extension_value_from_minimal_x(point[0])
    if not all(direct_base_compatibility(d_value)):
        raise ArithmeticError(f"mask {mask} failed a direct base-square condition")
    if d_value == 0:
        status = "ZERO"
    elif d_value in BASE_TRIPLE:
        status = "BASE"
    else:
        status = "RETAINED"
    return ExpressionRecord(mask, status, point, d_value)


def expression_tsv_line(record: ExpressionRecord) -> str:
    if record.point is None:
        return f"{record.mask}\tINF\t\t\t\t\n"
    if record.d is None:
        raise ArithmeticError("finite expression record has no extension value")
    x = record.point[0]
    return (
        f"{record.mask}\t{record.status}\t{x.numerator}\t{x.denominator}\t"
        f"{record.d.numerator}\t{record.d.denominator}\n"
    )


def build_value_catalog(
    records: Sequence[ExpressionRecord],
) -> tuple[list[Fraction], dict[Fraction, list[int]]]:
    provenance: dict[Fraction, list[int]] = {}
    for record in records:
        if record.status == "RETAINED" and record.d is not None:
            provenance.setdefault(record.d, []).append(record.mask)
    values = sorted(provenance)
    for masks in provenance.values():
        masks.sort()
    return values, provenance


def value_tsv_lines(
    values: Sequence[Fraction], provenance: dict[Fraction, list[int]]
) -> Iterator[str]:
    for index, value in enumerate(values):
        masks = ",".join(str(mask) for mask in provenance[value])
        yield f"{index}\t{value.numerator}\t{value.denominator}\t{masks}\n"


def edge_tsv_lines(adjacency: Sequence[int]) -> Iterator[str]:
    for left, neighbors in enumerate(adjacency):
        candidates = neighbors & ~((1 << (left + 1)) - 1)
        while candidates:
            bit = candidates & -candidates
            right = bit.bit_length() - 1
            yield f"{left}\t{right}\n"
            candidates ^= bit


def canonical_json_sha256(value: Any) -> str:
    payload = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def referee_row(mask: int, point: Point) -> dict[str, Any]:
    if point is None:
        raise ArithmeticError(f"referee mask {mask} unexpectedly maps to infinity")
    d_value = extension_value_from_minimal_x(point[0])
    roots = [rational_square_root(1 + base * d_value) for base in BASE_TRIPLE]
    if any(root is None for root in roots):
        raise ArithmeticError(f"referee mask {mask} failed a base-square condition")
    return {
        "index": mask,
        "weight": mask.bit_count(),
        "minimal_x": _compact_fraction(point[0]),
        "minimal_y": _compact_fraction(point[1]),
        "d": _compact_fraction(d_value),
        "extension_roots": [_compact_fraction(root) for root in roots if root is not None],
        "dual_group_law_match": True,
    }


def _cross_engine_masks() -> list[int]:
    union: set[int] = set()
    for masks in CALIBRATION_GROUPS.values():
        union.update(masks)
    return sorted(union)


def run_preflight(args: argparse.Namespace) -> int:
    manifest, manifest_hash, _route_spec, route_hash = validate_manifest(
        args.manifest.resolve(), allow_pending=True
    )
    model_report = model_preflight()
    doubled = tuple(CURVE.double(point) for point in PUBLISHED_POINTS)
    if any(point is None for point in doubled):
        raise ArithmeticError("a published infinite-order point doubled to infinity")

    referee_results: dict[str, Any] = {}
    for name, expected in REFEREE_SUBSETS.items():
        rows = [referee_row(mask, point_for_mask(mask, doubled)) for mask in expected["indices"]]
        observed_hash = canonical_json_sha256(rows)
        if observed_hash != expected["rows_sha256"]:
            raise ArithmeticError(
                f"referee subset {name} hash mismatch: {observed_hash} != {expected['rows_sha256']}"
            )
        referee_results[name] = {
            "indices": list(expected["indices"]),
            "row_count": len(rows),
            "rows_sha256": observed_hash,
        }

    cross_masks = _cross_engine_masks()
    if len(cross_masks) != 201:
        raise ArithmeticError(f"cross-engine mask union has {len(cross_masks)} entries, expected 201")
    records = [
        classify_expression(mask, point_for_mask(mask, doubled)) for mask in cross_masks
    ]
    values, provenance = build_value_catalog(records)
    adjacency, graph_bits, graph_statistics = build_exact_graph(
        values, manifest["modular_filter"]["primes"]
    )
    clique = first_k4(adjacency)

    output = args.output.resolve()
    expression_path = output.with_name(output.stem + ".expressions.tsv.gz")
    values_path = output.with_name(output.stem + ".values.tsv.gz")
    edges_path = output.with_name(output.stem + ".edges.tsv.gz")
    expression_file_hash, expression_hash, expression_count = write_gzip_lines(
        expression_path, (expression_tsv_line(record) for record in records)
    )
    value_file_hash, value_hash, value_count = write_gzip_lines(
        values_path, value_tsv_lines(values, provenance)
    )
    edge_file_hash, edge_hash, edge_count = write_gzip_lines(
        edges_path, edge_tsv_lines(adjacency)
    )
    observed_cross_hashes = {
        "expression": expression_hash,
        "value": value_hash,
        "edge": edge_hash,
    }
    if observed_cross_hashes != EXPECTED_CROSS_PREFLIGHT_HASHES:
        raise ArithmeticError(
            "cross-engine preflight ledger mismatch: "
            f"{observed_cross_hashes} != {EXPECTED_CROSS_PREFLIGHT_HASHES}"
        )

    status_counts = {
        status: sum(record.status == status for record in records)
        for status in ("INF", "ZERO", "BASE", "RETAINED")
    }
    report = {
        "schema": "rank12_boolean_cube_primary_preflight/v1",
        "route_id": ROUTE_ID,
        "status": "PREFLIGHT_PASS",
        "scope": "three referee subsets and the 201-mask cross-engine union; not the full cube",
        "manifest_path": str(args.manifest.resolve()),
        "manifest_sha256": manifest_hash,
        "route_spec_sha256": route_hash,
        "engine_sha256": sha256_file(Path(__file__).resolve()),
        "model": model_report,
        "referee_subsets": referee_results,
        "cross_engine": {
            "named_subset_counts": {name: len(masks) for name, masks in CALIBRATION_GROUPS.items()},
            "union_count": len(cross_masks),
            "status_counts": status_counts,
            "retained_expression_count": status_counts["RETAINED"],
            "deduplicated_vertex_count": len(values),
            "graph_statistics": graph_statistics,
            "graph_bits_sha256": hashlib.sha256(graph_bits).hexdigest().upper(),
            "independent_ledger_hashes": EXPECTED_CROSS_PREFLIGHT_HASHES,
            "independent_ledger_match": True,
            "k4_vertex_indices": list(clique) if clique is not None else None,
            "expression_ledger": {
                "path": expression_path.name,
                "file_sha256": expression_file_hash,
                "content_sha256": expression_hash,
                "row_count": expression_count,
            },
            "value_ledger": {
                "path": values_path.name,
                "file_sha256": value_file_hash,
                "content_sha256": value_hash,
                "row_count": value_count,
            },
            "edge_ledger": {
                "path": edges_path.name,
                "file_sha256": edge_file_hash,
                "content_sha256": edge_hash,
                "row_count": edge_count,
            },
        },
    }
    atomic_write_json(output, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "referee_hashes": {name: row["rows_sha256"] for name, row in referee_results.items()},
                "cross_engine_union_count": len(cross_masks),
                "deduplicated_vertex_count": len(values),
                "pair_count": graph_statistics["pair_count"],
                "edge_count": edge_count,
                "k4_vertex_indices": report["cross_engine"]["k4_vertex_indices"],
                "ledger_hashes": observed_cross_hashes,
            },
            sort_keys=True,
        )
    )
    return 0


def _quadratic_residue_sets(primes: Sequence[int]) -> tuple[frozenset[int], ...]:
    return tuple(frozenset((value * value) % prime for value in range(prime)) for prime in primes)


def _residue_rows(
    values: Sequence[Fraction], primes: Sequence[int]
) -> tuple[tuple[tuple[int, int], ...], ...]:
    return tuple(
        tuple((value.numerator % prime, value.denominator % prime) for value in values)
        for prime in primes
    )


def build_exact_graph(values: Sequence[Fraction], primes: Sequence[int]) -> tuple[list[int], bytes, dict[str, int]]:
    """Evaluate every unordered pair and return adjacency plus bit ledger."""

    count = len(values)
    pair_count = count * (count - 1) // 2
    graph_bits = bytearray((pair_count + 7) // 8)
    adjacency = [0] * count
    residue_sets = _quadratic_residue_sets(primes)
    residues = _residue_rows(values, primes)
    statistics = {
        "pair_count": 0,
        "negative_rejections": 0,
        "modular_rejections": 0,
        "exact_tests": 0,
        "exact_squares": 0,
        "exact_nonsquares": 0,
    }

    pair_index = 0
    for left_index in range(count):
        left = values[left_index]
        for right_index in range(left_index + 1, count):
            right = values[right_index]
            statistics["pair_count"] += 1
            numerator = (
                left.numerator * right.numerator
                + left.denominator * right.denominator
            )
            if numerator < 0:
                statistics["negative_rejections"] += 1
                pair_index += 1
                continue

            rejected = False
            for prime_index, prime in enumerate(primes):
                left_num, left_den = residues[prime_index][left_index]
                right_num, right_den = residues[prime_index][right_index]
                residue = (
                    (left_num * right_num + left_den * right_den)
                    * left_den
                    * right_den
                ) % prime
                if residue not in residue_sets[prime_index]:
                    rejected = True
                    break
            if rejected:
                statistics["modular_rejections"] += 1
                pair_index += 1
                continue

            statistics["exact_tests"] += 1
            denominator = left.denominator * right.denominator
            witness = numerator * denominator
            root = isqrt(witness)
            if root * root == witness:
                statistics["exact_squares"] += 1
                adjacency[left_index] |= 1 << right_index
                adjacency[right_index] |= 1 << left_index
                graph_bits[pair_index >> 3] |= 1 << (pair_index & 7)
            else:
                statistics["exact_nonsquares"] += 1
            pair_index += 1

    if pair_index != pair_count or statistics["pair_count"] != pair_count:
        raise ArithmeticError("complete graph pair count mismatch")
    return adjacency, bytes(graph_bits), statistics


def first_k4(adjacency: Sequence[int]) -> tuple[int, int, int, int] | None:
    count = len(adjacency)
    all_bits = (1 << count) - 1
    for left in range(count):
        above_left = all_bits ^ ((1 << (left + 1)) - 1)
        second_candidates = adjacency[left] & above_left
        while second_candidates:
            second_bit = second_candidates & -second_candidates
            second = second_bit.bit_length() - 1
            above_second = all_bits ^ ((1 << (second + 1)) - 1)
            common = adjacency[left] & adjacency[second] & above_second
            third_candidates = common
            while third_candidates:
                third_bit = third_candidates & -third_candidates
                third = third_bit.bit_length() - 1
                above_third = all_bits ^ ((1 << (third + 1)) - 1)
                fourth = adjacency[third] & common & above_third
                if fourth:
                    fourth_index = (fourth & -fourth).bit_length() - 1
                    return left, second, third, fourth_index
                third_candidates ^= third_bit
            second_candidates ^= second_bit
    return None


def all_k4(adjacency: Sequence[int]) -> list[tuple[int, int, int, int]]:
    count = len(adjacency)
    all_bits = (1 << count) - 1
    cliques: list[tuple[int, int, int, int]] = []
    for left in range(count):
        above_left = all_bits ^ ((1 << (left + 1)) - 1)
        second_candidates = adjacency[left] & above_left
        while second_candidates:
            second_bit = second_candidates & -second_candidates
            second = second_bit.bit_length() - 1
            above_second = all_bits ^ ((1 << (second + 1)) - 1)
            common = adjacency[left] & adjacency[second] & above_second
            third_candidates = common
            while third_candidates:
                third_bit = third_candidates & -third_candidates
                third = third_bit.bit_length() - 1
                above_third = all_bits ^ ((1 << (third + 1)) - 1)
                fourth_candidates = adjacency[third] & common & above_third
                while fourth_candidates:
                    fourth_bit = fourth_candidates & -fourth_candidates
                    fourth = fourth_bit.bit_length() - 1
                    cliques.append((left, second, third, fourth))
                    fourth_candidates ^= fourth_bit
                third_candidates ^= third_bit
            second_candidates ^= second_bit
    return cliques


def _verify_k4(values: Sequence[Fraction], indices: Sequence[int]) -> dict[str, Any]:
    extensions = [values[index] for index in indices]
    candidate_strings = [fraction_text(value) for value in (*BASE_TRIPLE, *extensions)]
    name = "rank12-boolean-cube-k4"
    primary = verify_tuple(candidate_strings, name=name, expect_size=7)
    independent = verify_septuple(candidate_strings, name=name)
    if not primary["valid"] or not independent["valid"]:
        raise ArithmeticError("K4 candidate failed one of the two full verifiers")
    return {
        "vertex_indices": list(indices),
        "values": candidate_strings,
        "primary_verifier": primary,
        "independent_verifier": independent,
    }


def run_search(args: argparse.Namespace) -> int:
    if not args.allow_full_search:
        raise ValueError("full 4096-expression search requires --allow-full-search")
    manifest, manifest_hash, _route_spec, route_hash = validate_manifest(
        args.manifest.resolve(), allow_pending=False
    )
    expected_output = _repo_path(manifest["outputs"]["primary_dir"]) / "summary.json"
    if args.output.resolve() != expected_output.resolve():
        raise ValueError(f"primary output must be the frozen path {expected_output}")
    model_report = model_preflight()
    doubled = tuple(CURVE.double(point) for point in PUBLISHED_POINTS)
    if any(point is None for point in doubled):
        raise ArithmeticError("a published infinite-order point doubled to infinity")

    points_by_mask = [point_for_mask(mask, doubled) for mask in range(EXPRESSION_COUNT)]
    records = [
        classify_expression(mask, point)
        for mask, point in enumerate(points_by_mask)
    ]
    allowed_values, provenance = build_value_catalog(records)
    status_counts = {
        status: sum(record.status == status for record in records)
        for status in ("INF", "ZERO", "BASE", "RETAINED")
    }
    finite_values = [record.d for record in records if record.d is not None]

    output = args.output.resolve()
    expression_path = output.with_name("expressions.tsv.gz")
    values_path = output.with_name("values.tsv.gz")
    edges_path = output.with_name("edges.tsv.gz")
    graph_path = output.with_name(output.stem + ".graph_bits.bin.gz")
    expression_file_hash, expression_ledger_hash, expression_line_count = write_gzip_lines(
        expression_path, (expression_tsv_line(record) for record in records)
    )
    value_file_hash, value_ledger_hash, value_line_count = write_gzip_lines(
        values_path, value_tsv_lines(allowed_values, provenance)
    )

    adjacency, graph_bits, graph_statistics = build_exact_graph(
        allowed_values, manifest["modular_filter"]["primes"]
    )
    edge_file_hash, edge_ledger_hash, edge_line_count = write_gzip_lines(
        edges_path, edge_tsv_lines(adjacency)
    )
    graph_file_hash = write_gzip_bytes(graph_path, graph_bits)
    graph_ledger_hash = hashlib.sha256(graph_bits).hexdigest().upper()
    cliques = all_k4(adjacency)
    hits = [_verify_k4(allowed_values, clique) for clique in cliques]

    result = {
        "schema": "rank12_boolean_cube_primary_result/v1",
        "route_id": ROUTE_ID,
        "status": "HIT" if hits else "NO_HIT",
        "scope": "only the frozen 4096-expression rank-12 Boolean cube",
        "complete": True,
        "manifest_path": str(args.manifest.resolve()),
        "manifest_sha256": manifest_hash,
        "route_spec_sha256": route_hash,
        "engine_sha256": sha256_file(Path(__file__).resolve()),
        "model_preflight": model_report,
        "expression_count": EXPRESSION_COUNT,
        "expression_line_count": expression_line_count,
        "status_counts": status_counts,
        "infinity_expression_count": status_counts["INF"],
        "finite_expression_count": len(finite_values),
        "zero_expression_count": status_counts["ZERO"],
        "base_forbidden_expression_count": status_counts["BASE"],
        "retained_expression_count": status_counts["RETAINED"],
        "unique_finite_value_count": len(set(finite_values)),
        "allowed_unique_vertex_count": len(allowed_values),
        "duplicate_finite_expression_count": len(finite_values) - len(set(finite_values)),
        "expression_ledger": {
            "path": expression_path.name,
            "file_sha256": expression_file_hash,
            "content_sha256": expression_ledger_hash,
            "line_rule": "mask,status,minimal_x_num,minimal_x_den,d_num,d_den; tab separated, LF",
        },
        "value_ledger": {
            "path": values_path.name,
            "file_sha256": value_file_hash,
            "content_sha256": value_ledger_hash,
            "line_count": value_line_count,
            "line_rule": "vertex_index,d_num,d_den,comma-separated provenance masks; tab separated, LF",
        },
        "edge_ledger": {
            "path": edges_path.name,
            "file_sha256": edge_file_hash,
            "content_sha256": edge_ledger_hash,
            "line_count": edge_line_count,
            "line_rule": "one true edge i,j per line in lexicographic order; tab separated, LF",
        },
        "graph_ledger": {
            "path": graph_path.name,
            "file_sha256": graph_file_hash,
            "content_sha256": graph_ledger_hash,
            "byte_count": len(graph_bits),
            "pair_order": "lexicographic (i,j), 0<=i<j<vertex_count",
            "bit_rule": "pair k is bit (k mod 8) of byte floor(k/8), least-significant bit first",
        },
        "graph_statistics": graph_statistics,
        "k4_count": len(cliques),
        "k4_vertex_indices": [list(clique) for clique in cliques],
        "hits": hits,
    }
    if expression_line_count != EXPRESSION_COUNT:
        raise ArithmeticError("expression ledger is incomplete")
    if value_line_count != len(allowed_values):
        raise ArithmeticError("value ledger is incomplete")
    if edge_line_count != graph_statistics["exact_squares"]:
        raise ArithmeticError("edge ledger is incomplete")
    atomic_write_json(output, result)
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "expression_count",
                    "allowed_unique_vertex_count",
                    "graph_statistics",
                    "k4_count",
                    "k4_vertex_indices",
                )
            },
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="check the model and separated masks")
    preflight.add_argument("--manifest", type=Path, required=True)
    preflight.add_argument("--output", type=Path, required=True)
    preflight.set_defaults(handler=run_preflight)

    search = subparsers.add_parser("search", help="consume the complete frozen Boolean cube")
    search.add_argument("--manifest", type=Path, required=True)
    search.add_argument("--output", type=Path, required=True)
    search.add_argument("--allow-full-search", action="store_true")
    search.set_defaults(handler=run_search)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ArithmeticError, FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
