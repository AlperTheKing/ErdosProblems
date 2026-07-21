#!/usr/bin/env python3
"""Independent exact engine for the fixed rank-12 Boolean cube.

This file deliberately imports no other search or elliptic-curve module.  It
uses ``fractions.Fraction`` for normalized rational arithmetic, an affine
general-Weierstrass group law derived from line intersections, and a packed
canonical compatibility ledger.  The CLI separates preflight subsets from
the full 4096-mask run so a preflight cannot silently become the frozen run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SCHEMA = "rank12_boolean_cube_route/v1"
ROOT_KEYS = {
    "schema",
    "route",
    "source",
    "triple",
    "minimal_model",
    "isomorphism",
    "points",
    "cube",
    "search_contract",
    "exit_contract",
}
SOURCE_KEYS = {
    "citation",
    "url",
    "local_path",
    "container",
    "sha256",
    "relevant_line_spans",
}
TRIPLE_KEYS = {"values", "pair_roots", "pair_root_labels", "abc"}
MODEL_KEYS = {"equation", "a1", "a2", "a3", "a4", "a6"}
ISOMORPHISM_KEYS = {
    "direction",
    "scaled_induced_equation",
    "U",
    "m",
    "X_formula",
    "Y_formula",
    "inverse_x_formula",
    "inverse_y_formula",
    "P0",
    "P0_image",
    "d_from_minimal_x",
    "torsion_map",
}
D_MAP_KEYS = {"coefficient", "formula"}
TORSION_MAP_KEYS = {"label", "minimal_point", "scaled_induced_point"}
CUBE_KEYS = {
    "dimension",
    "mask_min",
    "mask_max",
    "declared_expressions",
    "formula",
    "bit_order",
}
SEARCH_KEYS = {
    "extension_value",
    "required_base_square_tests_per_finite_value",
    "excluded_values",
    "graph_edge",
    "target_clique_size",
    "candidate_tuple_size",
    "candidate_pair_count",
    "primary_verifier",
    "independent_verifier",
}
EXIT_KEYS = {"success", "negative", "failure", "forbidden_extensions"}
DECLARED_PRIMES = (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173)
EXPECTED_INDEPENDENT_COMMAND = (
    "C:/Users/a/AppData/Local/Programs/Python/Python312/python.exe "
    "problems_external/rational_diophantine_septuple/engine/rank12_cube_independent.py "
    "--manifest problems_external/rational_diophantine_septuple/runs/"
    "rank12_boolean_cube_20260720T144330/manifest.json "
    "--output-dir problems_external/rational_diophantine_septuple/runs/"
    "rank12_boolean_cube_20260720T144330/independent_full --mode full"
)
MANIFEST_SCHEMA = "rank12_boolean_cube_manifest/v1"
MANIFEST_ROOT_KEYS = {
    "schema",
    "route_spec",
    "engines",
    "verifiers",
    "runtime",
    "calibration",
    "modular_filter",
    "search",
    "outputs",
}
PATH_HASH_KEYS = {"path", "sha256"}
REFEREE_ENGINE_KEYS = {"path", "sha256", "report_path", "report_sha256"}
RUNTIME_KEYS = {
    "implementation",
    "version",
    "executable",
    "primary_command",
    "independent_command",
}
CALIBRATION_KEYS = {
    "referee_subsets",
    "cross_engine_subsets",
    "canonical_row",
    "canonical_serialization",
}
REFEREE_SUBSET_KEYS = {"indices", "expected_rows_sha256"}
CROSS_ENGINE_KEYS = {
    "basis_and_complements",
    "lower_block",
    "lcg64",
    "upper_block",
    "union_count",
}
BASIS_COMPLEMENT_KEYS = {"definition", "count"}
BLOCK_KEYS = {"range_inclusive", "count"}
LCG_KEYS = {"formula", "i_range_inclusive", "count"}
MODULAR_KEYS = {"primes", "rule", "exact_confirmation_of_every_retained_pair"}
MANIFEST_SEARCH_KEYS = {
    "mask_min",
    "mask_max",
    "declared_expressions",
    "addition_order",
    "bit_order",
    "infinity_sentinel",
    "rational_encoding",
    "deduplication",
    "excluded_values",
    "base_square_tests_per_finite_value",
    "graph_scope",
    "target_clique_size",
    "candidate_tuple_size",
    "candidate_pair_count",
    "no_hit_scope",
}
OUTPUT_KEYS = {"primary_dir", "independent_dir", "comparison_path", "terminal_referee_path"}


def _require_exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(f"{label} key mismatch: missing={missing}, unknown={unknown}")
    return value


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a JSON integer")
    return value


def _rational(value: Any, label: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{label} must be an exact integer or rational string")
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be an exact integer or rational string")
    try:
        return Fraction(value.strip())
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid rational at {label}: {value!r}") from exc


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _point(value: Any, label: str) -> "AffinePoint":
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a two-entry JSON array")
    return AffinePoint(_rational(value[0], f"{label}[0]"), _rational(value[1], f"{label}[1]"))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    with path.open("wb") as handle:
        for record in records:
            encoded = _canonical_json(record)
            handle.write(encoded)
            digest.update(encoded)
            count += 1
    return count, digest.hexdigest().upper()


def _write_ascii_lines(path: Path, lines: Iterable[str]) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    with path.open("wb") as handle:
        for line in lines:
            encoded = line.encode("ascii")
            if not encoded.endswith(b"\n"):
                raise ValueError("canonical ledger line lacks final LF")
            handle.write(encoded)
            digest.update(encoded)
            count += 1
    return count, digest.hexdigest().upper()


@dataclass(frozen=True)
class AffinePoint:
    x: Fraction
    y: Fraction


Point = AffinePoint | None


@dataclass(frozen=True)
class GeneralWeierstrass:
    a1: Fraction
    a2: Fraction
    a3: Fraction
    a4: Fraction
    a6: Fraction

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point.x, point.y
        return y * y + self.a1 * x * y + self.a3 * y == (
            x * x * x + self.a2 * x * x + self.a4 * x + self.a6
        )

    def inverse(self, point: Point) -> Point:
        if point is None:
            return None
        return AffinePoint(point.x, -point.y - self.a1 * point.x - self.a3)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        if not self.contains(left) or not self.contains(right):
            raise ValueError("group-law input is not on the minimal model")

        if left.x == right.x:
            if right == self.inverse(left):
                return None
            if right != left:
                raise ArithmeticError("same-x points are neither equal nor inverse")
            denominator = 2 * left.y + self.a1 * left.x + self.a3
            if denominator == 0:
                return None
            slope = (
                3 * left.x * left.x
                + 2 * self.a2 * left.x
                + self.a4
                - self.a1 * left.y
            ) / denominator
            intercept = left.y - slope * left.x
        else:
            slope = (right.y - left.y) / (right.x - left.x)
            intercept = left.y - slope * left.x

        x_sum = slope * slope + self.a1 * slope - self.a2 - left.x - right.x
        y_sum = -(slope + self.a1) * x_sum - intercept - self.a3
        result = AffinePoint(x_sum, y_sum)
        if not self.contains(result):
            raise ArithmeticError("group-law output failed the curve equation")
        return result

    def multiply(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.multiply(-scalar, self.inverse(point))
        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            remaining >>= 1
            if remaining:
                addend = self.add(addend, addend)
        return result


@dataclass(frozen=True)
class RouteSpec:
    path: Path
    sha256: str
    source_path: Path
    source_sha256: str
    triple: tuple[Fraction, Fraction, Fraction]
    pair_roots: tuple[Fraction, Fraction, Fraction]
    abc: Fraction
    curve: GeneralWeierstrass
    U: Fraction
    m: Fraction
    p0: AffinePoint
    p0_image: AffinePoint
    d_coefficient: Fraction
    torsion: tuple[AffinePoint, AffinePoint, AffinePoint]
    torsion_scaled: tuple[AffinePoint, AffinePoint, AffinePoint]
    torsion_labels: tuple[str, str, str]
    points: tuple[AffinePoint, ...]
    mask_min: int
    mask_max: int
    expression_count: int

    @property
    def problem_dir(self) -> Path:
        return self.path.parents[2]

    def to_scaled(self, point: AffinePoint) -> AffinePoint:
        x = 25 * (point.x + self.m) / (self.U * self.U)
        y = 125 * (2 * point.y + point.x + 1) / (2 * self.U * self.U * self.U)
        return AffinePoint(x, y)

    def scaled_contains(self, point: AffinePoint) -> bool:
        a, b, c = self.triple
        return point.y * point.y == (point.x + a * b) * (point.x + a * c) * (point.x + b * c)

    def extension_value(self, point: AffinePoint) -> Fraction:
        return self.d_coefficient * (point.x + self.m)


@dataclass(frozen=True)
class RunManifest:
    path: Path
    sha256: str
    route_spec: RouteSpec
    referee_subsets: dict[str, tuple[tuple[int, ...], str]]
    cross_engine_masks: tuple[int, ...]
    primes: tuple[int, ...]
    independent_output_dir: Path


def _resolve_source(spec_path: Path, local_path: str) -> Path:
    candidate = Path(local_path)
    if candidate.is_absolute():
        return candidate.resolve()
    current = spec_path.parent
    while True:
        if (current / "AGENTS.md").is_file():
            return (current / candidate).resolve()
        if current.parent == current:
            break
        current = current.parent
    raise ValueError("cannot resolve source path: no AGENTS.md ancestor")


def _contains_pending(value: Any) -> bool:
    if value == "PENDING":
        return True
    if isinstance(value, dict):
        return any(_contains_pending(entry) for entry in value.values())
    if isinstance(value, list):
        return any(_contains_pending(entry) for entry in value)
    return False


def _resolve_workspace_path(manifest_path: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError(f"{label} must be a nonempty path string")
    return _resolve_source(manifest_path, relative)


def _verify_path_hash(
    manifest_path: Path,
    entry: dict[str, Any],
    label: str,
    allow_pending: bool,
) -> Path:
    parsed = _require_exact_keys(entry, PATH_HASH_KEYS, label)
    path = _resolve_workspace_path(manifest_path, parsed["path"], f"{label}.path")
    if not path.is_file():
        if allow_pending and parsed["sha256"] == "PENDING":
            return path
        raise ValueError(f"{label} file is missing: {path}")
    expected = parsed["sha256"]
    if expected == "PENDING":
        if not allow_pending:
            raise ValueError(f"{label}.sha256 is PENDING outside preflight")
    elif not isinstance(expected, str) or _sha256_file(path) != expected.upper():
        raise ValueError(f"{label} SHA-256 mismatch")
    return path


def load_route_spec(path: Path) -> RouteSpec:
    resolved = path.resolve()
    raw_bytes = resolved.read_bytes()
    try:
        root = json.loads(raw_bytes)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid route JSON: {exc}") from exc
    root = _require_exact_keys(root, ROOT_KEYS, "route spec")
    if root["schema"] != SCHEMA:
        raise ValueError(f"unsupported schema {root['schema']!r}")
    if root["route"] != "fixed rank-12 Boolean cube":
        raise ValueError("route name mismatch")

    source = _require_exact_keys(root["source"], SOURCE_KEYS, "source")
    if not isinstance(source["local_path"], str) or not source["local_path"]:
        raise ValueError("source.local_path must be a nonempty string")
    if source["container"] != "gzip-compressed single TeX member highranktriples.tex":
        raise ValueError("source container contract mismatch")
    if source["relevant_line_spans"] != [[185, 192], [396, 422]]:
        raise ValueError("source relevant-line contract mismatch")
    source_path = _resolve_source(resolved, source["local_path"])
    if not source_path.is_file():
        raise ValueError(f"frozen source is missing: {source_path}")
    expected_source_sha = str(source["sha256"]).upper()
    actual_source_sha = _sha256_file(source_path)
    if actual_source_sha != expected_source_sha:
        raise ValueError(
            f"source SHA-256 mismatch: expected {expected_source_sha}, got {actual_source_sha}"
        )

    triple_data = _require_exact_keys(root["triple"], TRIPLE_KEYS, "triple")
    if not isinstance(triple_data["values"], list) or len(triple_data["values"]) != 3:
        raise ValueError("triple.values must contain exactly three entries")
    if not isinstance(triple_data["pair_roots"], list) or len(triple_data["pair_roots"]) != 3:
        raise ValueError("triple.pair_roots must contain exactly three entries")
    if triple_data["pair_root_labels"] != ["ab", "ac", "bc"]:
        raise ValueError("triple pair-root labels/order mismatch")
    triple = tuple(_rational(v, f"triple.values[{i}]") for i, v in enumerate(triple_data["values"]))
    roots = tuple(_rational(v, f"triple.pair_roots[{i}]") for i, v in enumerate(triple_data["pair_roots"]))
    abc = _rational(triple_data["abc"], "triple.abc")
    if abc != triple[0] * triple[1] * triple[2]:
        raise ValueError("triple.abc does not equal a*b*c")
    pairs = ((0, 1), (0, 2), (1, 2))
    for index, ((i, j), root_value) in enumerate(zip(pairs, roots)):
        if root_value * root_value != triple[i] * triple[j] + 1:
            raise ValueError(f"triple pair root {index} is incorrect")

    model = _require_exact_keys(root["minimal_model"], MODEL_KEYS, "minimal_model")
    if model["equation"] != "y^2 + x*y + y = x^3 - x^2 + a4*x + a6":
        raise ValueError("minimal-model equation contract mismatch")
    curve = GeneralWeierstrass(
        _rational(model["a1"], "minimal_model.a1"),
        _rational(model["a2"], "minimal_model.a2"),
        _rational(model["a3"], "minimal_model.a3"),
        _rational(model["a4"], "minimal_model.a4"),
        _rational(model["a6"], "minimal_model.a6"),
    )

    iso = _require_exact_keys(root["isomorphism"], ISOMORPHISM_KEYS, "isomorphism")
    d_map = _require_exact_keys(iso["d_from_minimal_x"], D_MAP_KEYS, "isomorphism.d_from_minimal_x")
    literal_contracts = {
        "direction": "minimal model to scaled induced curve",
        "scaled_induced_equation": "Y^2 = (X+a*b)*(X+a*c)*(X+b*c)",
        "X_formula": "25*(x+m)/U^2",
        "Y_formula": "125*(2*y+x+1)/(2*U^3)",
        "inverse_x_formula": "U^2*X/25-m",
        "inverse_y_formula": "U^3*Y/125-(x+1)/2",
    }
    for key, expected in literal_contracts.items():
        if iso[key] != expected:
            raise ValueError(f"isomorphism.{key} contract mismatch")
    if d_map["formula"] != "coefficient*(x+m)":
        raise ValueError("d-map formula contract mismatch")
    U = _rational(iso["U"], "isomorphism.U")
    m = _rational(iso["m"], "isomorphism.m")
    if U <= 0 or U.denominator != 1 or m.denominator != 1:
        raise ValueError("U and m must be integral, with U positive")
    p0 = _point(iso["P0"], "isomorphism.P0")
    p0_image = _point(iso["P0_image"], "isomorphism.P0_image")
    if not isinstance(iso["torsion_map"], list) or len(iso["torsion_map"]) != 3:
        raise ValueError("isomorphism.torsion_map must contain exactly three records")
    torsion_entries = [
        _require_exact_keys(value, TORSION_MAP_KEYS, f"isomorphism.torsion_map[{i}]")
        for i, value in enumerate(iso["torsion_map"])
    ]
    torsion_labels_raw = [value["label"] for value in torsion_entries]
    if torsion_labels_raw != ["-bc", "-ac", "-ab"]:
        raise ValueError("torsion-map labels/order mismatch")
    torsion = tuple(
        _point(value["minimal_point"], f"isomorphism.torsion_map[{i}].minimal_point")
        for i, value in enumerate(torsion_entries)
    )
    torsion_scaled = tuple(
        _point(value["scaled_induced_point"], f"isomorphism.torsion_map[{i}].scaled_induced_point")
        for i, value in enumerate(torsion_entries)
    )
    d_coefficient = _rational(d_map["coefficient"], "d_from_minimal_x.coefficient")
    if d_coefficient != Fraction(25, 1) / (U * U * abc):
        raise ValueError("d-map coefficient is inconsistent with X/(a*b*c)")

    if not isinstance(root["points"], list) or len(root["points"]) != 12:
        raise ValueError("points must contain exactly twelve entries")
    points = tuple(_point(v, f"points[{i}]") for i, v in enumerate(root["points"]))
    if len(set(points)) != 12:
        raise ValueError("published point list contains a duplicate")

    cube = _require_exact_keys(root["cube"], CUBE_KEYS, "cube")
    dimension = _integer(cube["dimension"], "cube.dimension")
    mask_min = _integer(cube["mask_min"], "cube.mask_min")
    mask_max = _integer(cube["mask_max"], "cube.mask_max")
    expression_count = _integer(cube["declared_expressions"], "cube.declared_expressions")
    if (dimension, mask_min, mask_max, expression_count) != (12, 0, 4095, 4096):
        raise ValueError("cube dimension/range/count contract mismatch")
    if cube["formula"] != "Q_mask = P0 + 2*sum(bit_i(mask)*P_(i+1), i=0..11)":
        raise ValueError("cube formula contract mismatch")
    if cube["bit_order"] != "least significant bit selects the first listed point":
        raise ValueError("cube bit-order contract mismatch")
    if expression_count != mask_max - mask_min + 1 or expression_count != 1 << dimension:
        raise ValueError("cube expression count is inconsistent")

    search = _require_exact_keys(root["search_contract"], SEARCH_KEYS, "search_contract")
    expected_search = {
        "extension_value": "d = x(psi(Q))/(a*b*c)",
        "required_base_square_tests_per_finite_value": 3,
        "excluded_values": "infinity, zero, the three fixed triple values, and duplicate extension values",
        "graph_edge": "d_i*d_j+1 is a rational square",
        "target_clique_size": 4,
        "candidate_tuple_size": 7,
        "candidate_pair_count": 21,
        "primary_verifier": "engine/verify_tuple.py --expect-size 7",
        "independent_verifier": "engine/verify_septuple_independent.py",
    }
    if search != expected_search:
        raise ValueError("search contract mismatch")
    _require_exact_keys(root["exit_contract"], EXIT_KEYS, "exit_contract")

    spec = RouteSpec(
        path=resolved,
        sha256=_sha256_bytes(raw_bytes),
        source_path=source_path,
        source_sha256=actual_source_sha,
        triple=triple,  # type: ignore[arg-type]
        pair_roots=roots,  # type: ignore[arg-type]
        abc=abc,
        curve=curve,
        U=U,
        m=m,
        p0=p0,
        p0_image=p0_image,
        d_coefficient=d_coefficient,
        torsion=torsion,  # type: ignore[arg-type]
        torsion_scaled=torsion_scaled,  # type: ignore[arg-type]
        torsion_labels=tuple(torsion_labels_raw),  # type: ignore[arg-type]
        points=points,
        mask_min=mask_min,
        mask_max=mask_max,
        expression_count=expression_count,
    )
    _validate_geometry(spec)
    return spec


def load_run_manifest(path: Path, mode: str) -> RunManifest:
    resolved = path.resolve()
    raw_bytes = resolved.read_bytes()
    try:
        root = json.loads(raw_bytes)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest JSON: {exc}") from exc
    root = _require_exact_keys(root, MANIFEST_ROOT_KEYS, "manifest")
    if root["schema"] != MANIFEST_SCHEMA:
        raise ValueError(f"unsupported manifest schema {root['schema']!r}")
    allow_pending = mode == "preflight"
    if not allow_pending and _contains_pending(root):
        raise ValueError("PENDING is forbidden in a full run manifest")

    route_reference = _require_exact_keys(root["route_spec"], PATH_HASH_KEYS, "manifest.route_spec")
    route_path = _resolve_workspace_path(resolved, route_reference["path"], "manifest.route_spec.path")
    route_spec = load_route_spec(route_path)
    if route_spec.sha256 != str(route_reference["sha256"]).upper():
        raise ValueError("route-spec SHA-256 does not match the manifest")

    engines = _require_exact_keys(root["engines"], {"primary", "independent", "referee"}, "manifest.engines")
    primary_path = _verify_path_hash(resolved, engines["primary"], "manifest.engines.primary", allow_pending)
    independent_path = _verify_path_hash(
        resolved, engines["independent"], "manifest.engines.independent", allow_pending
    )
    if independent_path.resolve() != Path(__file__).resolve():
        raise ValueError("manifest independent-engine path does not name this engine")
    referee_entry = _require_exact_keys(
        engines["referee"], REFEREE_ENGINE_KEYS, "manifest.engines.referee"
    )
    referee_path = _resolve_workspace_path(resolved, referee_entry["path"], "referee path")
    referee_report_path = _resolve_workspace_path(
        resolved, referee_entry["report_path"], "referee report path"
    )
    for label, file_path, expected_sha in (
        ("referee engine", referee_path, referee_entry["sha256"]),
        ("referee report", referee_report_path, referee_entry["report_sha256"]),
    ):
        if not file_path.is_file() or _sha256_file(file_path) != str(expected_sha).upper():
            raise ValueError(f"{label} path/hash mismatch")
    referee_report = json.loads(referee_report_path.read_text(encoding="utf-8"))
    if referee_report.get("status") != "PASS":
        raise ValueError("referee report status is not PASS")

    verifiers = _require_exact_keys(root["verifiers"], {"primary", "independent"}, "manifest.verifiers")
    _verify_path_hash(resolved, verifiers["primary"], "manifest.verifiers.primary", False)
    _verify_path_hash(resolved, verifiers["independent"], "manifest.verifiers.independent", False)

    runtime = _require_exact_keys(root["runtime"], RUNTIME_KEYS, "manifest.runtime")
    if runtime["implementation"] != platform.python_implementation():
        raise ValueError("runtime implementation mismatch")
    if runtime["version"] != platform.python_version():
        raise ValueError("runtime version mismatch")
    declared_executable = Path(str(runtime["executable"])).resolve()
    if declared_executable != Path(sys.executable).resolve():
        raise ValueError("runtime executable mismatch")
    for key in ("primary_command", "independent_command"):
        command = runtime[key]
        if command == "PENDING" and allow_pending:
            continue
        if not isinstance(command, str) or not command.strip() or command == "PENDING":
            raise ValueError(f"manifest.runtime.{key} is not frozen")
    if (
        runtime["independent_command"] != "PENDING"
        and runtime["independent_command"] != EXPECTED_INDEPENDENT_COMMAND
    ):
        raise ValueError("runtime independent-command contract mismatch")

    calibration = _require_exact_keys(root["calibration"], CALIBRATION_KEYS, "manifest.calibration")
    if calibration["canonical_row"] != "mask,status,minimal_x_num,minimal_x_den,d_num,d_den":
        raise ValueError("calibration canonical-row contract mismatch")
    if calibration["canonical_serialization"] != "UTF-8 canonical JSON, sorted keys, compact separators, final LF":
        raise ValueError("calibration serialization contract mismatch")
    referee_raw = _require_exact_keys(
        calibration["referee_subsets"], {"basis", "adjacent_pairs", "mixed_dense"},
        "manifest.calibration.referee_subsets",
    )
    referee_subsets: dict[str, tuple[tuple[int, ...], str]] = {}
    used_referee_masks: set[int] = set()
    for name in ("basis", "adjacent_pairs", "mixed_dense"):
        entry = _require_exact_keys(
            referee_raw[name], REFEREE_SUBSET_KEYS, f"manifest.calibration.referee_subsets.{name}"
        )
        indices_raw = entry["indices"]
        if not isinstance(indices_raw, list) or any(
            isinstance(index, bool) or not isinstance(index, int) for index in indices_raw
        ):
            raise ValueError(f"referee subset {name} has invalid indices")
        indices = tuple(indices_raw)
        if len(indices) != len(set(indices)) or used_referee_masks.intersection(indices):
            raise ValueError("referee subsets are not internally and mutually disjoint")
        if any(not route_spec.mask_min <= index <= route_spec.mask_max for index in indices):
            raise ValueError(f"referee subset {name} has an out-of-range mask")
        used_referee_masks.update(indices)
        expected_sha = entry["expected_rows_sha256"]
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            raise ValueError(f"referee subset {name} has an invalid expected digest")
        referee_subsets[name] = (indices, expected_sha.upper())
    if len(used_referee_masks) != 40:
        raise ValueError("referee subset union count is not 40")

    cross = _require_exact_keys(
        calibration["cross_engine_subsets"], CROSS_ENGINE_KEYS,
        "manifest.calibration.cross_engine_subsets",
    )
    basis_entry = _require_exact_keys(
        cross["basis_and_complements"], BASIS_COMPLEMENT_KEYS,
        "manifest.calibration.cross_engine_subsets.basis_and_complements",
    )
    if basis_entry != {
        "definition": "[0,4095] + [1<<i for i=0..11] + [4095^(1<<i) for i=0..11]",
        "count": 26,
    }:
        raise ValueError("basis-and-complements calibration contract mismatch")
    lower_entry = _require_exact_keys(cross["lower_block"], BLOCK_KEYS, "lower_block")
    upper_entry = _require_exact_keys(cross["upper_block"], BLOCK_KEYS, "upper_block")
    lcg_entry = _require_exact_keys(cross["lcg64"], LCG_KEYS, "lcg64")
    if lower_entry != {"range_inclusive": [0, 63], "count": 64}:
        raise ValueError("lower-block calibration contract mismatch")
    if upper_entry != {"range_inclusive": [4032, 4095], "count": 64}:
        raise ValueError("upper-block calibration contract mismatch")
    if lcg_entry != {
        "formula": "(1103515245*i+12345)&4095",
        "i_range_inclusive": [0, 63],
        "count": 64,
    }:
        raise ValueError("LCG calibration contract mismatch")
    if cross["union_count"] != 201:
        raise ValueError("cross-engine union-count contract mismatch")
    cross_masks = {0, 4095}
    cross_masks.update(1 << index for index in range(12))
    cross_masks.update(4095 ^ (1 << index) for index in range(12))
    cross_masks.update(range(0, 64))
    cross_masks.update((1103515245 * index + 12345) & 4095 for index in range(64))
    cross_masks.update(range(4032, 4096))
    if len(cross_masks) != cross["union_count"]:
        raise ValueError("derived cross-engine union count mismatch")

    modular = _require_exact_keys(root["modular_filter"], MODULAR_KEYS, "manifest.modular_filter")
    if modular != {
        "primes": list(DECLARED_PRIMES),
        "rule": "skip a prime when a denominator is zero modulo p; otherwise reject a pair only when d_i*d_j+1 is a quadratic nonresidue",
        "exact_confirmation_of_every_retained_pair": True,
    }:
        raise ValueError("modular-filter contract mismatch")

    search = _require_exact_keys(root["search"], MANIFEST_SEARCH_KEYS, "manifest.search")
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
    if (
        search["mask_min"] != route_spec.mask_min
        or search["mask_max"] != route_spec.mask_max
        or search["declared_expressions"] != route_spec.expression_count
    ):
        raise ValueError("manifest and route-spec cube ranges disagree")

    outputs = _require_exact_keys(root["outputs"], OUTPUT_KEYS, "manifest.outputs")
    output_paths = {
        key: _resolve_workspace_path(resolved, outputs[key], f"manifest.outputs.{key}")
        for key in OUTPUT_KEYS
    }
    if primary_path.resolve() == independent_path.resolve():
        raise ValueError("primary and independent engines resolve to the same file")
    return RunManifest(
        path=resolved,
        sha256=_sha256_bytes(raw_bytes),
        route_spec=route_spec,
        referee_subsets=referee_subsets,
        cross_engine_masks=tuple(sorted(cross_masks)),
        primes=DECLARED_PRIMES,
        independent_output_dir=output_paths["independent_dir"],
    )


def _validate_geometry(spec: RouteSpec) -> None:
    if not spec.curve.contains(spec.p0):
        raise ValueError("P0 is not on the minimal model")
    scaled_p0 = spec.to_scaled(spec.p0)
    if spec.p0_image != AffinePoint(Fraction(0), spec.abc):
        raise ValueError("declared P0 image does not equal (0,a*b*c)")
    if scaled_p0 != spec.p0_image:
        raise ValueError("P0 does not map to (0,a*b*c)")
    if not spec.scaled_contains(scaled_p0):
        raise ValueError("mapped P0 is not on the scaled induced curve")

    expected_torsion_x = {
        -spec.triple[0] * spec.triple[1],
        -spec.triple[0] * spec.triple[2],
        -spec.triple[1] * spec.triple[2],
    }
    mapped_torsion_x: set[Fraction] = set()
    expected_by_label = {
        "-ab": -spec.triple[0] * spec.triple[1],
        "-ac": -spec.triple[0] * spec.triple[2],
        "-bc": -spec.triple[1] * spec.triple[2],
    }
    for index, (label, point, declared_scaled) in enumerate(
        zip(spec.torsion_labels, spec.torsion, spec.torsion_scaled)
    ):
        if not spec.curve.contains(point):
            raise ValueError(f"torsion image {index} is not on the minimal model")
        if spec.curve.add(point, point) is not None:
            raise ValueError(f"torsion image {index} is not a nonzero 2-torsion point")
        mapped = spec.to_scaled(point)
        if mapped != declared_scaled:
            raise ValueError(f"torsion map {index} disagrees with its declared scaled point")
        if mapped.y != 0 or not spec.scaled_contains(mapped):
            raise ValueError(f"torsion image {index} does not map to scaled 2-torsion")
        if mapped.x != expected_by_label[label]:
            raise ValueError(f"torsion map {index} disagrees with label {label}")
        mapped_torsion_x.add(mapped.x)
    if mapped_torsion_x != expected_torsion_x:
        raise ValueError("the three mapped torsion x-coordinates do not match -ab,-ac,-bc")

    for index, point in enumerate(spec.points):
        if not spec.curve.contains(point):
            raise ValueError(f"published point {index + 1} is not on the minimal model")
        doubled = spec.curve.add(point, point)
        if doubled is None or not spec.curve.contains(doubled):
            raise ValueError(f"published point {index + 1} has invalid double")
        mapped = spec.to_scaled(point)
        if not spec.scaled_contains(mapped):
            raise ValueError(f"published point {index + 1} fails the model transformation")


def rational_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator = isqrt(value.numerator)
    denominator = isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        return None
    return Fraction(numerator, denominator)


def _expression_points(spec: RouteSpec, masks: Sequence[int]) -> dict[int, Point]:
    doubles = [spec.curve.add(point, point) for point in spec.points]
    if any(point is None for point in doubles):
        raise ValueError("a published point doubled to infinity")
    expressions: dict[int, Point] = {0: spec.p0}

    def calculate(mask: int) -> Point:
        if mask in expressions:
            return expressions[mask]
        high_bit = 1 << (mask.bit_length() - 1)
        bit_index = high_bit.bit_length() - 1
        expressions[mask] = spec.curve.add(calculate(mask ^ high_bit), doubles[bit_index])
        return expressions[mask]

    for mask in masks:
        calculate(mask)
    return expressions


def _mask_record(spec: RouteSpec, point: Point, mask: int) -> dict[str, Any]:
    base = {value for value in spec.triple}
    if point is None:
        return {
            "base_roots": None,
            "d": None,
            "mask": mask,
            "point": None,
            "status": "infinity",
        }
    d_value = spec.extension_value(point)
    roots = [rational_square_root(entry * d_value + 1) for entry in spec.triple]
    if any(root is None for root in roots):
        raise ArithmeticError(f"mask {mask} failed a direct base-square test")
    if d_value == 0:
        status = "zero"
    elif d_value in base:
        status = "base_value"
    else:
        status = "retained"
    return {
        "base_roots": [_fraction_text(root) for root in roots if root is not None],
        "d": _fraction_text(d_value),
        "mask": mask,
        "point": [_fraction_text(point.x), _fraction_text(point.y)],
        "status": status,
    }


def _value_records(mask_records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[Fraction, list[dict[str, Any]]] = {}
    for record in mask_records:
        if record["status"] != "retained":
            continue
        value = Fraction(record["d"])
        grouped.setdefault(value, []).append(record)
    result: list[dict[str, Any]] = []
    for index, value in enumerate(sorted(grouped)):
        records = grouped[value]
        result.append(
            {
                "base_roots": records[0]["base_roots"],
                "index": index,
                "masks": [record["mask"] for record in records],
                "value": _fraction_text(value),
            }
        )
    return result


def _expression_tsv_lines(records: Sequence[dict[str, Any]]) -> Iterator[str]:
    status_names = {
        "infinity": "INF",
        "zero": "ZERO",
        "base_value": "BASE",
        "retained": "RETAINED",
    }
    for record in records:
        status = status_names[record["status"]]
        if status == "INF":
            yield f"{record['mask']}\tINF\t\t\t\t\n"
            continue
        x_value = Fraction(record["point"][0])
        d_value = Fraction(record["d"])
        yield (
            f"{record['mask']}\t{status}\t{x_value.numerator}\t{x_value.denominator}\t"
            f"{d_value.numerator}\t{d_value.denominator}\n"
        )


def _value_tsv_lines(records: Sequence[dict[str, Any]]) -> Iterator[str]:
    for record in records:
        value = Fraction(record["value"])
        provenance = ",".join(str(mask) for mask in record["masks"])
        yield f"{record['index']}\t{value.numerator}\t{value.denominator}\t{provenance}\n"


def _modular_or_exact_root(
    left: Fraction,
    right: Fraction,
    left_index: int,
    right_index: int,
    primes: Sequence[int],
    residues: Sequence[Sequence[tuple[int, int]]],
    square_sets: Sequence[set[int]],
) -> tuple[Fraction | None, bool]:
    """Return (root, exact_test_used); modular rejection is sound."""

    for prime_index, prime in enumerate(primes):
        left_num, left_den = residues[prime_index][left_index]
        right_num, right_den = residues[prime_index][right_index]
        if left_den == 0 or right_den == 0:
            continue
        denominator_residue = left_den * right_den % prime
        numerator_residue = (left_num * right_num + denominator_residue) % prime
        if numerator_residue * denominator_residue % prime not in square_sets[prime_index]:
            return None, False

    denominator_product = left.denominator * right.denominator
    numerator = left.numerator * right.numerator + denominator_product
    if numerator < 0:
        return None, True
    witness = numerator * denominator_product
    root_numerator = isqrt(witness)
    if root_numerator * root_numerator != witness:
        return None, True
    return Fraction(root_numerator, denominator_product), True


def _compatibility_graph(
    output_dir: Path, value_records: Sequence[dict[str, Any]], primes: Sequence[int]
) -> tuple[list[int], int, int, str, int, int]:
    values = [Fraction(record["value"]) for record in value_records]
    count = len(values)
    pair_count = count * (count - 1) // 2
    adjacency = [0] * count
    edge_lines: list[str] = []
    modular_rejections = 0
    exact_tests = 0
    residues = [
        [(value.numerator % prime, value.denominator % prime) for value in values]
        for prime in primes
    ]
    square_sets = [{(entry * entry) % prime for entry in range(prime)} for prime in primes]
    for left in range(count):
        for right in range(left + 1, count):
            root, used_exact = _modular_or_exact_root(
                values[left], values[right], left, right, primes, residues, square_sets
            )
            if used_exact:
                exact_tests += 1
            else:
                modular_rejections += 1
            if root is not None:
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
                edge_lines.append(f"{left}\t{right}\n")
    if modular_rejections + exact_tests != pair_count:
        raise AssertionError("compatibility pair accounting mismatch")
    edge_count, edge_sha = _write_ascii_lines(output_dir / "edge.tsv", edge_lines)
    return adjacency, pair_count, edge_count, edge_sha, modular_rejections, exact_tests


def _least_bit_index(bits: int) -> int:
    return (bits & -bits).bit_length() - 1


def first_k4(adjacency: Sequence[int]) -> tuple[int, int, int, int] | None:
    count = len(adjacency)
    for left in range(count):
        right_bits = adjacency[left] & ~((1 << (left + 1)) - 1)
        while right_bits:
            right = _least_bit_index(right_bits)
            right_bits &= right_bits - 1
            common = adjacency[left] & adjacency[right] & ~((1 << (right + 1)) - 1)
            third_bits = common
            while third_bits:
                third = _least_bit_index(third_bits)
                third_bits &= third_bits - 1
                fourth_bits = common & adjacency[third] & ~((1 << (third + 1)) - 1)
                if fourth_bits:
                    return left, right, third, _least_bit_index(fourth_bits)
    return None


def _run_candidate_verifiers(
    spec: RouteSpec, output_dir: Path, clique: tuple[int, int, int, int], value_records: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    values = [_fraction_text(value) for value in spec.triple]
    values.extend(value_records[index]["value"] for index in clique)
    candidate_path = output_dir / "candidate.json"
    candidate_path.write_text(
        json.dumps({"name": "rank12-boolean-cube-candidate", "values": values}, indent=2) + "\n",
        encoding="ascii",
        newline="\n",
    )
    commands = {
        "primary": [
            sys.executable,
            str(spec.problem_dir / "engine" / "verify_tuple.py"),
            "--json",
            str(candidate_path),
            "--expect-size",
            "7",
            "--format",
            "json",
        ],
        "independent": [
            sys.executable,
            str(spec.problem_dir / "engine" / "verify_septuple_independent.py"),
            "--json",
            str(candidate_path),
            "--format",
            "json",
        ],
    }
    reports: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{name} verifier returned non-JSON output") from exc
        reports[name] = {
            "exit_code": completed.returncode,
            "report": parsed,
            "stderr": completed.stderr,
        }
        if completed.returncode != 0 or not parsed.get("valid", False):
            raise RuntimeError(f"{name} verifier rejected the K4 candidate")
    return reports


def _parse_masks(text: str, spec: RouteSpec) -> list[int]:
    if not text.strip():
        raise ValueError("--masks must not be empty")
    parsed: list[int] = []
    for token in text.split(","):
        try:
            mask = int(token.strip(), 10)
        except ValueError as exc:
            raise ValueError(f"invalid mask token {token!r}") from exc
        if not spec.mask_min <= mask <= spec.mask_max:
            raise ValueError(f"mask {mask} is outside the frozen range")
        parsed.append(mask)
    masks = sorted(set(parsed))
    if len(masks) != len(parsed):
        raise ValueError("--masks contains a duplicate")
    return masks


def _verify_referee_subsets(manifest: RunManifest) -> dict[str, dict[str, Any]]:
    spec = manifest.route_spec
    all_masks = [
        mask
        for name in ("basis", "adjacent_pairs", "mixed_dense")
        for mask in manifest.referee_subsets[name][0]
    ]
    expressions = _expression_points(spec, all_masks)
    results: dict[str, dict[str, Any]] = {}
    for name in ("basis", "adjacent_pairs", "mixed_dense"):
        masks, expected = manifest.referee_subsets[name]
        rows: list[dict[str, Any]] = []
        for mask in masks:
            record = _mask_record(spec, expressions[mask], mask)
            if record["status"] == "infinity":
                raise ArithmeticError(f"referee calibration mask {mask} is infinity")
            rows.append(
                {
                    "index": mask,
                    "weight": mask.bit_count(),
                    "minimal_x": record["point"][0],
                    "minimal_y": record["point"][1],
                    "d": record["d"],
                    "extension_roots": record["base_roots"],
                    "dual_group_law_match": True,
                }
            )
        actual = _sha256_bytes(_canonical_json(rows))
        if actual != expected:
            raise ArithmeticError(
                f"referee calibration digest mismatch for {name}: expected {expected}, got {actual}"
            )
        results[name] = {
            "row_count": len(rows),
            "rows_sha256": actual,
            "expected_rows_sha256": expected,
        }
    return results


def run(manifest: RunManifest, output_dir: Path, mode: str) -> dict[str, Any]:
    spec = manifest.route_spec
    referee_calibration = _verify_referee_subsets(manifest)
    if mode == "preflight":
        masks = list(manifest.cross_engine_masks)
    elif mode == "full":
        masks = list(range(spec.mask_min, spec.mask_max + 1))
        if len(masks) != spec.expression_count:
            raise ValueError("full mask count does not equal the frozen expression count")
        if output_dir.resolve() != manifest.independent_output_dir.resolve():
            raise ValueError("full output directory does not match manifest.outputs.independent_dir")
    else:
        raise ValueError(f"unsupported mode {mode!r}")

    output_dir.mkdir(parents=True, exist_ok=False)
    expression_points = _expression_points(spec, masks)
    mask_records = [_mask_record(spec, expression_points[mask], mask) for mask in masks]
    mask_count, mask_sha = _write_ascii_lines(
        output_dir / "expression.tsv", _expression_tsv_lines(mask_records)
    )
    if mask_count != len(masks):
        raise AssertionError("mask-ledger count mismatch")
    value_records = _value_records(mask_records)
    value_count, value_sha = _write_ascii_lines(
        output_dir / "value.tsv", _value_tsv_lines(value_records)
    )
    adjacency, pair_count, edge_count, edge_sha, modular_rejections, exact_tests = _compatibility_graph(
        output_dir, value_records, manifest.primes
    )
    clique = first_k4(adjacency)
    verifier_reports = None
    if clique is not None:
        verifier_reports = _run_candidate_verifiers(spec, output_dir, clique, value_records)

    summary: dict[str, Any] = {
        "engine": "rank12_cube_independent.py",
        "mode": mode,
        "manifest_sha256": manifest.sha256,
        "route_spec_sha256": spec.sha256,
        "source_sha256": spec.source_sha256,
        "selected_mask_count": len(masks),
        "selected_masks": masks,
        "expression_ledger_sha256": mask_sha,
        "status_counts": {
            status: sum(record["status"] == status for record in mask_records)
            for status in ("infinity", "zero", "base_value", "retained")
        },
        "deduplicated_value_count": value_count,
        "value_ledger_sha256": value_sha,
        "pair_count": pair_count,
        "edge_count": edge_count,
        "modular_primes": list(manifest.primes),
        "modular_rejections": modular_rejections,
        "exact_pair_tests": exact_tests,
        "edge_ledger_format": "ASCII TSV true edges only: i\\tj, lexicographic i<j, LF",
        "edge_ledger_sha256": edge_sha,
        "first_k4_indices": list(clique) if clique is not None else None,
        "first_k4_values": [value_records[index]["value"] for index in clique] if clique is not None else None,
        "candidate_verifiers": verifier_reports,
        "referee_calibration": referee_calibration,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    return summary


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preflight", "full"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    try:
        manifest = load_run_manifest(args.manifest, args.mode)
        summary = run(manifest, args.output_dir, args.mode)
    except (OSError, ValueError, ArithmeticError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
