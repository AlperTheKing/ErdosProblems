#!/usr/bin/env python3
"""Standalone terminal referee for the fixed rank-12 Boolean cube.

This program imports neither search engine.  It validates the frozen manifest
and every referenced source artifact, parses both implementations' canonical
ledgers, reconstructs the complete compatibility graph with exact arithmetic,
compares every mathematical record, enumerates every K4, and invokes both
standalone seven-value verifiers for each K4.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path
from typing import Any, Iterable, Sequence


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_SCHEMA = "rank12_boolean_cube_manifest/v1"
ROUTE_SCHEMA = "rank12_boolean_cube_route/v1"
EXPRESSION_COUNT = 4096
SHA_RE = re.compile(r"[0-9A-F]{64}")
UNSIGNED_RE = re.compile(r"0|[1-9][0-9]*")
SIGNED_RE = re.compile(r"0|-?[1-9][0-9]*")


class RefereeError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExpressionRow:
    mask: int
    status: str
    x: Fraction | None
    d: Fraction | None


@dataclass(frozen=True)
class ValueRow:
    index: int
    value: Fraction
    masks: tuple[int, ...]


@dataclass(frozen=True)
class FrozenContext:
    manifest_path: Path
    manifest_sha256: str
    manifest: dict[str, Any]
    route_path: Path
    route_sha256: str
    route: dict[str, Any]
    source_sha256: str
    triple: tuple[Fraction, Fraction, Fraction]
    d_coefficient: Fraction
    x_translation: int
    primary_dir: Path
    independent_dir: Path
    comparison_path: Path
    terminal_path: Path


@dataclass(frozen=True)
class ParsedRun:
    summary_path: Path
    summary: dict[str, Any]
    expressions_raw: bytes
    expressions: tuple[ExpressionRow, ...]
    values_raw: bytes
    values: tuple[ValueRow, ...]
    edges_raw: bytes
    edges: tuple[tuple[int, int], ...]
    graph_bits: bytes | None


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RefereeError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path, label: str) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise RefereeError(f"{label} must use LF and end with LF")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=duplicate_rejecting_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RefereeError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RefereeError(f"{label} root must be an object")
    return value


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RefereeError(f"{label} must be an object")
    return value


def require_keys(value: dict[str, Any], keys: Iterable[str], label: str) -> None:
    missing = set(keys) - set(value)
    if missing:
        raise RefereeError(f"{label} missing keys: {sorted(missing)}")


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise RefereeError(f"{label} must be an uppercase SHA-256")
    return value


def contains_pending(value: Any) -> bool:
    if value == "PENDING":
        return True
    if isinstance(value, dict):
        return any(contains_pending(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_pending(item) for item in value)
    return False


def workspace_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise RefereeError(f"{label} must be a nonempty relative path")
    supplied = Path(value)
    if supplied.is_absolute():
        raise RefereeError(f"{label} must be workspace-relative")
    resolved = (WORKSPACE_ROOT / supplied).resolve()
    try:
        resolved.relative_to(WORKSPACE_ROOT.resolve())
    except ValueError as exc:
        raise RefereeError(f"{label} escapes the workspace") from exc
    return resolved


def child_path(directory: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise RefereeError(f"{label} must be a nonempty relative path")
    supplied = Path(value)
    if supplied.is_absolute():
        raise RefereeError(f"{label} must be relative")
    resolved = (directory / supplied).resolve()
    try:
        resolved.relative_to(directory.resolve())
    except ValueError as exc:
        raise RefereeError(f"{label} escapes its output directory") from exc
    return resolved


def parse_int(text: str, label: str, *, nonnegative: bool = False) -> int:
    pattern = UNSIGNED_RE if nonnegative else SIGNED_RE
    if pattern.fullmatch(text) is None:
        raise RefereeError(f"noncanonical integer at {label}: {text!r}")
    return int(text)


def parse_fraction_fields(num_text: str, den_text: str, label: str) -> Fraction:
    numerator = parse_int(num_text, f"{label}.numerator")
    denominator = parse_int(den_text, f"{label}.denominator", nonnegative=True)
    if denominator <= 0 or gcd(abs(numerator), denominator) != 1:
        raise RefereeError(f"noncanonical reduced fraction at {label}")
    return Fraction(numerator, denominator)


def rational(value: Any, label: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise RefereeError(f"{label} is not an exact rational")
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or not value:
        raise RefereeError(f"{label} is not an exact rational string")
    try:
        parsed = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise RefereeError(f"invalid rational at {label}") from exc
    return parsed


def is_rational_square(value: Fraction) -> bool:
    if value < 0:
        return False
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    return (
        numerator_root * numerator_root == value.numerator
        and denominator_root * denominator_root == value.denominator
    )


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def validate_hash_contract(contract: dict[str, Any], label: str) -> Path:
    require_keys(contract, ("path", "sha256"), label)
    path = workspace_path(contract["path"], f"{label}.path")
    expected = require_sha(contract["sha256"], f"{label}.sha256")
    if not path.is_file() or sha256_file(path) != expected:
        raise RefereeError(f"{label} file or SHA-256 mismatch")
    return path


def load_context(manifest_path: Path) -> FrozenContext:
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path, "manifest")
    if manifest.get("schema") != MANIFEST_SCHEMA or contains_pending(manifest):
        raise RefereeError("manifest is not a final rank-12 manifest")
    require_keys(
        manifest,
        ("route_spec", "engines", "verifiers", "runtime", "calibration", "modular_filter", "search", "outputs"),
        "manifest",
    )
    manifest_sha = sha256_file(manifest_path)

    route_contract = require_mapping(manifest["route_spec"], "manifest.route_spec")
    route_path = validate_hash_contract(route_contract, "manifest.route_spec")
    route_sha = require_sha(route_contract["sha256"], "manifest.route_spec.sha256")
    route = load_json(route_path, "route spec")
    if route.get("schema") != ROUTE_SCHEMA:
        raise RefereeError("route spec schema mismatch")
    cube = require_mapping(route.get("cube"), "route.cube")
    if (
        cube.get("dimension"), cube.get("mask_min"), cube.get("mask_max"), cube.get("declared_expressions")
    ) != (12, 0, 4095, EXPRESSION_COUNT):
        raise RefereeError("route cube contract mismatch")

    source = require_mapping(route.get("source"), "route.source")
    source_path = workspace_path(source.get("local_path"), "route.source.local_path")
    source_sha = require_sha(source.get("sha256"), "route.source.sha256")
    if not source_path.is_file() or sha256_file(source_path) != source_sha:
        raise RefereeError("route source SHA-256 mismatch")

    engines = require_mapping(manifest["engines"], "manifest.engines")
    require_keys(engines, ("primary", "independent", "referee"), "manifest.engines")
    primary_engine = validate_hash_contract(require_mapping(engines["primary"], "engines.primary"), "engines.primary")
    independent_engine = validate_hash_contract(require_mapping(engines["independent"], "engines.independent"), "engines.independent")
    referee_contract = require_mapping(engines["referee"], "engines.referee")
    require_keys(referee_contract, ("path", "sha256", "report_path", "report_sha256"), "engines.referee")
    referee_path = validate_hash_contract(referee_contract, "engines.referee")
    referee_report_path = workspace_path(referee_contract["report_path"], "engines.referee.report_path")
    referee_report_sha = require_sha(referee_contract["report_sha256"], "engines.referee.report_sha256")
    if not referee_report_path.is_file() or sha256_file(referee_report_path) != referee_report_sha:
        raise RefereeError("referee report SHA-256 mismatch")
    referee_report = load_json(referee_report_path, "referee report")
    if referee_report.get("status") != "PASS":
        raise RefereeError("frozen referee report is not PASS")
    route_audit = require_mapping(referee_report.get("route_spec_audit"), "referee_report.route_spec_audit")
    if route_audit.get("status") != "PASS" or route_audit.get("sha256") != route_sha:
        raise RefereeError("referee report is not bound to the frozen route spec")

    verifiers = require_mapping(manifest["verifiers"], "manifest.verifiers")
    require_keys(verifiers, ("primary", "independent"), "manifest.verifiers")
    primary_verifier = validate_hash_contract(require_mapping(verifiers["primary"], "verifiers.primary"), "verifiers.primary")
    independent_verifier = validate_hash_contract(require_mapping(verifiers["independent"], "verifiers.independent"), "verifiers.independent")

    for path, expected_name in (
        (primary_engine, "rank12_cube_primary.py"),
        (independent_engine, "rank12_cube_independent.py"),
        (referee_path, "referee_rank12_cube.py"),
        (primary_verifier, "verify_tuple.py"),
        (independent_verifier, "verify_septuple_independent.py"),
    ):
        if path.name != expected_name:
            raise RefereeError(f"unexpected frozen artifact path for {expected_name}")

    runtime = require_mapping(manifest["runtime"], "manifest.runtime")
    require_keys(runtime, ("implementation", "version", "executable", "primary_command", "independent_command"), "manifest.runtime")
    runtime_executable = Path(str(runtime["executable"])).resolve()
    if (
        runtime.get("implementation") != "CPython"
        or runtime.get("version") != platform.python_version()
        or runtime_executable != Path(sys.executable).resolve()
        or not runtime_executable.is_file()
    ):
        raise RefereeError("active runtime does not match the frozen manifest")
    if not all(isinstance(runtime.get(key), str) and runtime[key] for key in ("primary_command", "independent_command")):
        raise RefereeError("manifest commands are not final")

    search = require_mapping(manifest["search"], "manifest.search")
    if (
        search.get("mask_min"), search.get("mask_max"), search.get("declared_expressions"),
        search.get("target_clique_size"), search.get("candidate_tuple_size"), search.get("candidate_pair_count")
    ) != (0, 4095, 4096, 4, 7, 21):
        raise RefereeError("manifest search contract mismatch")
    modular = require_mapping(manifest["modular_filter"], "manifest.modular_filter")
    primes = modular.get("primes")
    if not isinstance(primes, list) or not primes or any(not isinstance(p, int) or p < 3 for p in primes):
        raise RefereeError("invalid modular prime list")
    if modular.get("exact_confirmation_of_every_retained_pair") is not True:
        raise RefereeError("manifest does not require exact pair confirmation")

    triple_data = require_mapping(route.get("triple"), "route.triple")
    values = triple_data.get("values")
    roots = triple_data.get("pair_roots")
    if not isinstance(values, list) or len(values) != 3 or not isinstance(roots, list) or len(roots) != 3:
        raise RefereeError("route triple contract mismatch")
    triple = tuple(rational(value, f"route.triple.values[{index}]") for index, value in enumerate(values))
    pair_indices = ((0, 1), (0, 2), (1, 2))
    for index, ((left, right), root_value) in enumerate(zip(pair_indices, roots)):
        root = rational(root_value, f"route.triple.pair_roots[{index}]")
        if root * root != triple[left] * triple[right] + 1:
            raise RefereeError("route triple root mismatch")

    iso = require_mapping(route.get("isomorphism"), "route.isomorphism")
    d_map = require_mapping(iso.get("d_from_minimal_x"), "route.isomorphism.d_from_minimal_x")
    coefficient = rational(d_map.get("coefficient"), "d coefficient")
    translation = rational(iso.get("m"), "x translation")
    if translation.denominator != 1:
        raise RefereeError("x translation is not integral")

    outputs = require_mapping(manifest["outputs"], "manifest.outputs")
    require_keys(outputs, ("primary_dir", "independent_dir", "comparison_path", "terminal_referee_path"), "manifest.outputs")
    primary_dir = workspace_path(outputs["primary_dir"], "outputs.primary_dir")
    independent_dir = workspace_path(outputs["independent_dir"], "outputs.independent_dir")
    comparison_path = workspace_path(outputs["comparison_path"], "outputs.comparison_path")
    terminal_path = workspace_path(outputs["terminal_referee_path"], "outputs.terminal_referee_path")
    if len({primary_dir, independent_dir, comparison_path, terminal_path}) != 4:
        raise RefereeError("manifest output paths overlap")

    return FrozenContext(
        manifest_path=manifest_path,
        manifest_sha256=manifest_sha,
        manifest=manifest,
        route_path=route_path,
        route_sha256=route_sha,
        route=route,
        source_sha256=source_sha,
        triple=triple,  # type: ignore[arg-type]
        d_coefficient=coefficient,
        x_translation=translation.numerator,
        primary_dir=primary_dir,
        independent_dir=independent_dir,
        comparison_path=comparison_path,
        terminal_path=terminal_path,
    )


def canonical_lines(raw: bytes, label: str) -> list[str]:
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise RefereeError(f"{label} must end with LF and contain no CR")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise RefereeError(f"{label} is not ASCII") from exc
    lines = text.splitlines(keepends=True)
    if any(not line.endswith("\n") or line == "\n" for line in lines):
        raise RefereeError(f"{label} contains a malformed line")
    return [line[:-1] for line in lines]


def parse_expressions(raw: bytes, context: FrozenContext, label: str) -> tuple[ExpressionRow, ...]:
    lines = canonical_lines(raw, label)
    if len(lines) != EXPRESSION_COUNT:
        raise RefereeError(f"{label} does not contain 4096 rows")
    result: list[ExpressionRow] = []
    base = set(context.triple)
    for expected_mask, line in enumerate(lines):
        fields = line.split("\t")
        if len(fields) != 6:
            raise RefereeError(f"{label} row {expected_mask} does not have six fields")
        mask = parse_int(fields[0], f"{label}[{expected_mask}].mask", nonnegative=True)
        if mask != expected_mask:
            raise RefereeError(f"{label} masks are not exactly 0..4095")
        status = fields[1]
        if status not in {"INF", "ZERO", "BASE", "RETAINED"}:
            raise RefereeError(f"invalid status in {label} row {mask}")
        if status == "INF":
            if fields[2:] != ["", "", "", ""]:
                raise RefereeError(f"nonempty infinity fields in {label} row {mask}")
            result.append(ExpressionRow(mask, status, None, None))
            continue
        x_value = parse_fraction_fields(fields[2], fields[3], f"{label}[{mask}].x")
        d_value = parse_fraction_fields(fields[4], fields[5], f"{label}[{mask}].d")
        if d_value != context.d_coefficient * (x_value + context.x_translation):
            raise RefereeError(f"extension map mismatch in {label} row {mask}")
        expected_status = "ZERO" if d_value == 0 else "BASE" if d_value in base else "RETAINED"
        if status != expected_status:
            raise RefereeError(f"classification mismatch in {label} row {mask}")
        if any(not is_rational_square(base_value * d_value + 1) for base_value in context.triple):
            raise RefereeError(f"base-square failure in {label} row {mask}")
        result.append(ExpressionRow(mask, status, x_value, d_value))
    return tuple(result)


def parse_values(raw: bytes, expressions: Sequence[ExpressionRow], label: str) -> tuple[ValueRow, ...]:
    lines = canonical_lines(raw, label)
    result: list[ValueRow] = []
    for expected_index, line in enumerate(lines):
        fields = line.split("\t")
        if len(fields) != 4:
            raise RefereeError(f"{label} row {expected_index} does not have four fields")
        index = parse_int(fields[0], f"{label}[{expected_index}].index", nonnegative=True)
        if index != expected_index:
            raise RefereeError(f"{label} vertex indices are not consecutive")
        value = parse_fraction_fields(fields[1], fields[2], f"{label}[{index}].value")
        mask_tokens = fields[3].split(",")
        if not mask_tokens or any(not token for token in mask_tokens):
            raise RefereeError(f"empty provenance in {label} row {index}")
        masks = tuple(parse_int(token, f"{label}[{index}].mask", nonnegative=True) for token in mask_tokens)
        if tuple(sorted(set(masks))) != masks:
            raise RefereeError(f"noncanonical provenance in {label} row {index}")
        result.append(ValueRow(index, value, masks))
    if any(result[index - 1].value >= result[index].value for index in range(1, len(result))):
        raise RefereeError(f"{label} values are not strictly increasing")

    grouped: dict[Fraction, list[int]] = {}
    for record in expressions:
        if record.status == "RETAINED":
            if record.d is None:
                raise RefereeError("retained expression lacks a value")
            grouped.setdefault(record.d, []).append(record.mask)
    expected = tuple(
        ValueRow(index, value, tuple(grouped[value]))
        for index, value in enumerate(sorted(grouped))
    )
    if tuple(result) != expected:
        raise RefereeError(f"{label} does not exactly deduplicate its expression ledger")
    return tuple(result)


def parse_edges(raw: bytes, vertex_count: int, label: str) -> tuple[tuple[int, int], ...]:
    lines = canonical_lines(raw, label)
    result: list[tuple[int, int]] = []
    previous: tuple[int, int] | None = None
    for row_index, line in enumerate(lines):
        fields = line.split("\t")
        if len(fields) != 2:
            raise RefereeError(f"{label} row {row_index} does not have two fields")
        left = parse_int(fields[0], f"{label}[{row_index}].left", nonnegative=True)
        right = parse_int(fields[1], f"{label}[{row_index}].right", nonnegative=True)
        pair = (left, right)
        if not 0 <= left < right < vertex_count or (previous is not None and pair <= previous):
            raise RefereeError(f"noncanonical edge in {label} row {row_index}")
        result.append(pair)
        previous = pair
    return tuple(result)


def read_primary_ledger(directory: Path, contract: Any, label: str) -> tuple[bytes, Path]:
    contract = require_mapping(contract, label)
    require_keys(contract, ("path", "file_sha256", "content_sha256"), label)
    path = child_path(directory, contract["path"], f"{label}.path")
    file_sha = require_sha(contract["file_sha256"], f"{label}.file_sha256")
    content_sha = require_sha(contract["content_sha256"], f"{label}.content_sha256")
    if not path.is_file() or sha256_file(path) != file_sha:
        raise RefereeError(f"{label} compressed file SHA-256 mismatch")
    try:
        raw = gzip.decompress(path.read_bytes())
    except (gzip.BadGzipFile, EOFError) as exc:
        raise RefereeError(f"invalid gzip stream for {label}") from exc
    if sha256_bytes(raw) != content_sha:
        raise RefereeError(f"{label} content SHA-256 mismatch")
    return raw, path


def load_primary(context: FrozenContext) -> ParsedRun:
    summary_path = context.primary_dir / "summary.json"
    summary = load_json(summary_path, "primary summary")
    if (
        summary.get("schema") != "rank12_boolean_cube_primary_result/v1"
        or summary.get("complete") is not True
        or summary.get("manifest_sha256") != context.manifest_sha256
        or summary.get("route_spec_sha256") != context.route_sha256
        or summary.get("engine_sha256") != context.manifest["engines"]["primary"]["sha256"]
        or summary.get("expression_count") != EXPRESSION_COUNT
    ):
        raise RefereeError("primary summary is not bound to the frozen full run")
    expressions_raw, _ = read_primary_ledger(context.primary_dir, summary.get("expression_ledger"), "primary expression ledger")
    expressions = parse_expressions(expressions_raw, context, "primary expression ledger")
    values_raw, _ = read_primary_ledger(context.primary_dir, summary.get("value_ledger"), "primary value ledger")
    values = parse_values(values_raw, expressions, "primary value ledger")
    edges_raw, _ = read_primary_ledger(context.primary_dir, summary.get("edge_ledger"), "primary edge ledger")
    edges = parse_edges(edges_raw, len(values), "primary edge ledger")
    graph_bits, _ = read_primary_ledger(context.primary_dir, summary.get("graph_ledger"), "primary graph ledger")

    expression_contract = require_mapping(summary["expression_ledger"], "primary expression ledger")
    value_contract = require_mapping(summary["value_ledger"], "primary value ledger")
    edge_contract = require_mapping(summary["edge_ledger"], "primary edge ledger")
    graph_contract = require_mapping(summary["graph_ledger"], "primary graph ledger")
    if summary.get("expression_line_count") != len(expressions):
        raise RefereeError("primary expression line count mismatch")
    if value_contract.get("line_count") != len(values) or edge_contract.get("line_count") != len(edges):
        raise RefereeError("primary value or edge line count mismatch")
    if graph_contract.get("byte_count") != len(graph_bits):
        raise RefereeError("primary graph byte count mismatch")
    if "line_count" in expression_contract and expression_contract["line_count"] != len(expressions):
        raise RefereeError("primary expression contract count mismatch")
    return ParsedRun(summary_path, summary, expressions_raw, expressions, values_raw, values, edges_raw, edges, graph_bits)


def load_independent(context: FrozenContext) -> ParsedRun:
    summary_path = context.independent_dir / "summary.json"
    summary = load_json(summary_path, "independent summary")
    if (
        summary.get("engine") != "rank12_cube_independent.py"
        or summary.get("mode") != "full"
        or summary.get("manifest_sha256") != context.manifest_sha256
        or summary.get("route_spec_sha256") != context.route_sha256
        or summary.get("source_sha256") != context.source_sha256
        or summary.get("selected_mask_count") != EXPRESSION_COUNT
        or summary.get("selected_masks") != list(range(EXPRESSION_COUNT))
    ):
        raise RefereeError("independent summary is not bound to the frozen full run")
    paths = {
        "expression": context.independent_dir / "expression.tsv",
        "value": context.independent_dir / "value.tsv",
        "edge": context.independent_dir / "edge.tsv",
    }
    for path in paths.values():
        if not path.is_file():
            raise RefereeError(f"missing independent ledger: {path.name}")
    expressions_raw = paths["expression"].read_bytes()
    values_raw = paths["value"].read_bytes()
    edges_raw = paths["edge"].read_bytes()
    expected_hashes = {
        "expression": summary.get("expression_ledger_sha256"),
        "value": summary.get("value_ledger_sha256"),
        "edge": summary.get("edge_ledger_sha256"),
    }
    for name, raw in (("expression", expressions_raw), ("value", values_raw), ("edge", edges_raw)):
        if sha256_bytes(raw) != require_sha(expected_hashes[name], f"independent {name} SHA-256"):
            raise RefereeError(f"independent {name} ledger SHA-256 mismatch")
    expressions = parse_expressions(expressions_raw, context, "independent expression ledger")
    values = parse_values(values_raw, expressions, "independent value ledger")
    edges = parse_edges(edges_raw, len(values), "independent edge ledger")
    return ParsedRun(summary_path, summary, expressions_raw, expressions, values_raw, values, edges_raw, edges, None)


def status_counts(expressions: Sequence[ExpressionRow]) -> dict[str, int]:
    return {status: sum(row.status == status for row in expressions) for status in ("INF", "ZERO", "BASE", "RETAINED")}


def pair_offset(vertex_count: int, left: int, right: int) -> int:
    return left * (2 * vertex_count - left - 1) // 2 + (right - left - 1)


def graph_bits_from_edges(vertex_count: int, edges: Sequence[tuple[int, int]]) -> bytes:
    pair_count = vertex_count * (vertex_count - 1) // 2
    result = bytearray((pair_count + 7) // 8)
    for left, right in edges:
        index = pair_offset(vertex_count, left, right)
        result[index >> 3] |= 1 << (index & 7)
    return bytes(result)


def recompute_graph(values: Sequence[ValueRow], primes: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], dict[str, int]]:
    rationals = [row.value for row in values]
    vertex_count = len(rationals)
    square_sets = [frozenset((entry * entry) % prime for entry in range(prime)) for prime in primes]
    residues = [
        [(value.numerator % prime, value.denominator % prime) for value in rationals]
        for prime in primes
    ]
    edges: list[tuple[int, int]] = []
    pair_count = 0
    modular_rejections = 0
    exact_tests = 0
    exact_nonsquares = 0
    for left in range(vertex_count):
        left_value = rationals[left]
        for right in range(left + 1, vertex_count):
            pair_count += 1
            rejected = False
            for prime_index, prime in enumerate(primes):
                left_num, left_den = residues[prime_index][left]
                right_num, right_den = residues[prime_index][right]
                if left_den == 0 or right_den == 0:
                    continue
                denominator_mod = left_den * right_den % prime
                numerator_mod = (left_num * right_num + denominator_mod) % prime
                if numerator_mod * denominator_mod % prime not in square_sets[prime_index]:
                    rejected = True
                    break
            if rejected:
                modular_rejections += 1
                continue
            exact_tests += 1
            right_value = rationals[right]
            denominator = left_value.denominator * right_value.denominator
            numerator = left_value.numerator * right_value.numerator + denominator
            if numerator >= 0:
                witness = numerator * denominator
                root = isqrt(witness)
                if root * root == witness:
                    edges.append((left, right))
                    continue
            exact_nonsquares += 1
    expected_pairs = vertex_count * (vertex_count - 1) // 2
    if pair_count != expected_pairs or modular_rejections + exact_tests != expected_pairs:
        raise RefereeError("terminal graph pair accounting is incomplete")
    return tuple(edges), {
        "pair_count": pair_count,
        "modular_rejections": modular_rejections,
        "exact_tests": exact_tests,
        "exact_squares": len(edges),
        "exact_nonsquares": exact_nonsquares,
    }


def adjacency_from_edges(vertex_count: int, edges: Sequence[tuple[int, int]]) -> list[int]:
    adjacency = [0] * vertex_count
    for left, right in edges:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    return adjacency


def enumerate_k4(adjacency: Sequence[int]) -> tuple[tuple[int, int, int, int], ...]:
    vertex_count = len(adjacency)
    result: list[tuple[int, int, int, int]] = []
    for first in range(vertex_count):
        second_bits = adjacency[first] & ~((1 << (first + 1)) - 1)
        while second_bits:
            second_bit = second_bits & -second_bits
            second = second_bit.bit_length() - 1
            second_bits ^= second_bit
            common = adjacency[first] & adjacency[second] & ~((1 << (second + 1)) - 1)
            third_bits = common
            while third_bits:
                third_bit = third_bits & -third_bits
                third = third_bit.bit_length() - 1
                third_bits ^= third_bit
                fourth_bits = common & adjacency[third] & ~((1 << (third + 1)) - 1)
                while fourth_bits:
                    fourth_bit = fourth_bits & -fourth_bits
                    fourth = fourth_bit.bit_length() - 1
                    fourth_bits ^= fourth_bit
                    result.append((first, second, third, fourth))
    return tuple(result)


def verify_matching_structure(
    values: Sequence[ValueRow], edges: Sequence[tuple[int, int]]
) -> dict[str, Any]:
    """Check the observed 2,047-edge matching in provenance-mask coordinates."""

    if any(len(row.masks) != 1 for row in values):
        raise RefereeError("matching invariant requires one provenance mask per retained value")
    adjacency = adjacency_from_edges(len(values), edges)
    degrees = [neighbors.bit_count() for neighbors in adjacency]
    degree_histogram = {
        str(degree): degrees.count(degree) for degree in sorted(set(degrees))
    }
    mask_pairs: list[tuple[int, int]] = []
    for left, right in edges:
        pair = tuple(sorted((values[left].masks[0], values[right].masks[0])))
        if pair[0] ^ pair[1] != 1:
            raise RefereeError("an edge's provenance masks do not differ by XOR 1")
        mask_pairs.append(pair)  # type: ignore[arg-type]
    expected = [(2 * index, 2 * index + 1) for index in range(1, 2048)]
    if (
        len(edges) != 2047
        or degree_histogram != {"0": 1, "1": 4094}
        or sorted(mask_pairs) != expected
    ):
        raise RefereeError("the terminal graph is not the declared 2,047-edge matching")
    isolated_vertices = [index for index, degree in enumerate(degrees) if degree == 0]
    if len(isolated_vertices) != 1 or values[isolated_vertices[0]].masks != (1,):
        raise RefereeError("the unique isolated vertex does not have provenance mask 1")
    return {
        "degree_histogram": degree_histogram,
        "isolated_vertex_index": isolated_vertices[0],
        "isolated_provenance_mask": 1,
        "edge_mask_rule": "{2*t,2*t+1} for t=1..2047",
        "all_edge_mask_xors": 1,
        "edge_mask_pair_count": len(mask_pairs),
    }


def parse_reported_k4(value: Any, label: str) -> tuple[tuple[int, int, int, int], ...]:
    if not isinstance(value, list):
        raise RefereeError(f"{label} must be a list")
    result: list[tuple[int, int, int, int]] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, list) or len(entry) != 4 or any(not isinstance(item, int) for item in entry):
            raise RefereeError(f"invalid K4 at {label}[{index}]")
        clique = tuple(entry)
        if not clique[0] < clique[1] < clique[2] < clique[3]:
            raise RefereeError(f"noncanonical K4 at {label}[{index}]")
        result.append(clique)  # type: ignore[arg-type]
    if tuple(sorted(set(result))) != tuple(result):
        raise RefereeError(f"{label} is not a strict lexicographic list")
    return tuple(result)


def verifier_report_valid(value: Any, label: str) -> bool:
    report = value
    if isinstance(report, dict) and "report" in report:
        if report.get("exit_code") != 0 or report.get("stderr") not in ("", None):
            raise RefereeError(f"embedded {label} process failed")
        report = report.get("report")
    if not isinstance(report, dict) or report.get("valid") is not True:
        raise RefereeError(f"embedded {label} report is not valid")
    return True


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def run_verifiers(context: FrozenContext, k4s: Sequence[tuple[int, int, int, int]], values: Sequence[ValueRow]) -> list[dict[str, Any]]:
    runtime = str(context.manifest["runtime"]["executable"])
    contracts = context.manifest["verifiers"]
    results: list[dict[str, Any]] = []
    for clique_index, clique in enumerate(k4s):
        candidate = [fraction_text(value) for value in context.triple]
        candidate.extend(fraction_text(values[index].value) for index in clique)
        if len(set(candidate)) != 7 or "0" in candidate:
            raise RefereeError(f"K4 {clique_index} does not form seven distinct nonzero values")
        payload = json.dumps({"name": f"rank12-terminal-k4-{clique_index}", "values": candidate}, sort_keys=True) + "\n"
        replay: dict[str, Any] = {"vertex_indices": list(clique), "values": candidate, "verifiers": {}}
        for name in ("primary", "independent"):
            verifier_path = workspace_path(contracts[name]["path"], f"verifiers.{name}.path")
            command = [runtime, str(verifier_path), "--json", "-", "--format", "json"]
            if name == "primary":
                command.extend(("--expect-size", "7"))
            completed = subprocess.run(
                command,
                input=payload,
                text=True,
                capture_output=True,
                cwd=WORKSPACE_ROOT,
                check=False,
                timeout=300,
            )
            try:
                report = json.loads(completed.stdout, object_pairs_hook=duplicate_rejecting_object)
            except json.JSONDecodeError as exc:
                raise RefereeError(f"{name} verifier returned invalid JSON") from exc
            if completed.returncode != 0 or completed.stderr or not isinstance(report, dict) or report.get("valid") is not True:
                raise RefereeError(f"{name} verifier rejected K4 {clique_index}")
            replay["verifiers"][name] = {
                "command": command,
                "exit_code": completed.returncode,
                "stderr": completed.stderr,
                "report": report,
                "stdout_sha256": sha256_bytes(completed.stdout.encode("utf-8")),
            }
        results.append(replay)
    return results


def validate_summaries(context: FrozenContext, primary: ParsedRun, independent: ParsedRun, exact_edges: Sequence[tuple[int, int]], k4s: Sequence[tuple[int, int, int, int]]) -> None:
    counts = status_counts(primary.expressions)
    primary_summary = primary.summary
    independent_summary = independent.summary
    if primary_summary.get("status_counts") != counts:
        raise RefereeError("primary status counts mismatch")
    independent_counts = {
        "infinity": counts["INF"],
        "zero": counts["ZERO"],
        "base_value": counts["BASE"],
        "retained": counts["RETAINED"],
    }
    if independent_summary.get("status_counts") != independent_counts:
        raise RefereeError("independent status counts mismatch")
    finite_values = [row.d for row in primary.expressions if row.d is not None]
    unique_finite_values = set(finite_values)
    if (
        primary_summary.get("infinity_expression_count") != counts["INF"]
        or primary_summary.get("finite_expression_count") != len(finite_values)
        or primary_summary.get("zero_expression_count") != counts["ZERO"]
        or primary_summary.get("base_forbidden_expression_count") != counts["BASE"]
        or primary_summary.get("unique_finite_value_count") != len(unique_finite_values)
        or primary_summary.get("duplicate_finite_expression_count")
        != len(finite_values) - len(unique_finite_values)
    ):
        raise RefereeError("primary expression summary counts mismatch")
    vertex_count = len(primary.values)
    pair_count = vertex_count * (vertex_count - 1) // 2
    if (
        primary_summary.get("retained_expression_count") != counts["RETAINED"]
        or primary_summary.get("allowed_unique_vertex_count") != vertex_count
        or independent_summary.get("deduplicated_value_count") != vertex_count
        or primary_summary.get("graph_statistics", {}).get("pair_count") != pair_count
        or independent_summary.get("pair_count") != pair_count
        or primary_summary.get("edge_ledger", {}).get("line_count") != len(exact_edges)
        or independent_summary.get("edge_count") != len(exact_edges)
    ):
        raise RefereeError("terminal expression, vertex, pair, or edge count mismatch")
    primary_stats = require_mapping(primary_summary.get("graph_statistics"), "primary graph statistics")
    if (
        primary_stats.get("negative_rejections", 0)
        + primary_stats.get("modular_rejections", 0)
        + primary_stats.get("exact_tests", 0)
        != pair_count
        or primary_stats.get("exact_squares", 0) + primary_stats.get("exact_nonsquares", 0)
        != primary_stats.get("exact_tests", 0)
        or primary_stats.get("exact_squares") != len(exact_edges)
    ):
        raise RefereeError("primary complete-pair accounting mismatch")
    if independent_summary.get("modular_rejections", 0) + independent_summary.get("exact_pair_tests", 0) != pair_count:
        raise RefereeError("independent complete-pair accounting mismatch")
    if independent_summary.get("modular_primes") != context.manifest["modular_filter"]["primes"]:
        raise RefereeError("independent modular-prime contract mismatch")

    reported_primary = parse_reported_k4(primary_summary.get("k4_vertex_indices"), "primary K4 list")
    if reported_primary != tuple(k4s) or primary_summary.get("k4_count") != len(k4s):
        raise RefereeError("primary K4 list mismatch")
    hits = primary_summary.get("hits")
    if not isinstance(hits, list) or len(hits) != len(k4s):
        raise RefereeError("primary K4 verifier list mismatch")
    for index, (hit, clique) in enumerate(zip(hits, k4s)):
        hit = require_mapping(hit, f"primary hit {index}")
        if hit.get("vertex_indices") != list(clique):
            raise RefereeError(f"primary hit {index} indices mismatch")
        verifier_report_valid(hit.get("primary_verifier"), f"primary hit {index} primary verifier")
        verifier_report_valid(hit.get("independent_verifier"), f"primary hit {index} independent verifier")

    expected_first = list(k4s[0]) if k4s else None
    expected_first_values = [fraction_text(primary.values[index].value) for index in k4s[0]] if k4s else None
    if independent_summary.get("first_k4_indices") != expected_first or independent_summary.get("first_k4_values") != expected_first_values:
        raise RefereeError("independent first K4 mismatch")
    embedded = independent_summary.get("candidate_verifiers")
    if k4s:
        embedded = require_mapping(embedded, "independent candidate verifiers")
        for name in ("primary", "independent"):
            verifier_report_valid(embedded.get(name), f"independent {name} verifier")
    elif embedded is not None:
        raise RefereeError("independent summary reports verifiers without a K4")

    expected_status = "HIT" if k4s else "NO_HIT"
    if primary_summary.get("status") != expected_status:
        raise RefereeError("primary terminal status mismatch")
    calibration = require_mapping(independent_summary.get("referee_calibration"), "independent referee calibration")
    expected_calibration = context.manifest["calibration"]["referee_subsets"]
    for name, expected in expected_calibration.items():
        row = require_mapping(calibration.get(name), f"independent referee calibration {name}")
        if row.get("rows_sha256") != expected["expected_rows_sha256"] or row.get("expected_rows_sha256") != expected["expected_rows_sha256"]:
            raise RefereeError(f"independent referee calibration mismatch: {name}")


def compare(context: FrozenContext) -> tuple[dict[str, Any], dict[str, Any]]:
    primary = load_primary(context)
    independent = load_independent(context)
    if primary.expressions != independent.expressions or primary.expressions_raw != independent.expressions_raw:
        raise RefereeError("primary and independent expression ledgers differ")
    if primary.values != independent.values or primary.values_raw != independent.values_raw:
        raise RefereeError("primary and independent value ledgers differ")
    if primary.edges != independent.edges or primary.edges_raw != independent.edges_raw:
        raise RefereeError("primary and independent edge ledgers differ")

    vertex_count = len(primary.values)
    pair_count = vertex_count * (vertex_count - 1) // 2
    expected_graph_bits = graph_bits_from_edges(vertex_count, primary.edges)
    if primary.graph_bits != expected_graph_bits or len(expected_graph_bits) != (pair_count + 7) // 8:
        raise RefereeError("primary complete graph bit ledger disagrees with its edge ledger")

    primes = context.manifest["modular_filter"]["primes"]
    exact_edges, terminal_graph_stats = recompute_graph(primary.values, primes)
    if exact_edges != primary.edges:
        raise RefereeError("terminal exact graph reconstruction disagrees with both engines")
    matching_structure = verify_matching_structure(primary.values, exact_edges)
    k4s = enumerate_k4(adjacency_from_edges(vertex_count, exact_edges))
    validate_summaries(context, primary, independent, exact_edges, k4s)
    verifier_replays = run_verifiers(context, k4s, primary.values)

    k4_payload = [list(clique) for clique in k4s]
    result = "HIT" if k4s else "NO_HIT"
    scope = context.manifest["search"]["no_hit_scope"]
    comparison = {
        "schema": "rank12_boolean_cube_comparison/v1",
        "status": "MATCH",
        "result": result,
        "scope": scope,
        "manifest": {"path": str(context.manifest_path), "sha256": context.manifest_sha256},
        "route_spec": {"path": str(context.route_path), "sha256": context.route_sha256},
        "frozen_artifacts": {
            "engines": context.manifest["engines"],
            "verifiers": context.manifest["verifiers"],
            "source_sha256": context.source_sha256,
        },
        "summaries": {
            "primary": {"path": str(primary.summary_path), "sha256": sha256_file(primary.summary_path)},
            "independent": {"path": str(independent.summary_path), "sha256": sha256_file(independent.summary_path)},
        },
        "counts": {
            "expressions": len(primary.expressions),
            "status_counts": status_counts(primary.expressions),
            "deduplicated_vertices": vertex_count,
            "tested_pairs": pair_count,
            "edges": len(exact_edges),
            "k4": len(k4s),
        },
        "canonical_ledger_hashes": {
            "expression": sha256_bytes(primary.expressions_raw),
            "value": sha256_bytes(primary.values_raw),
            "edge": sha256_bytes(primary.edges_raw),
            "graph_bits": sha256_bytes(expected_graph_bits),
            "k4": sha256_bytes((json.dumps(k4_payload, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")),
        },
        "terminal_exact_graph": terminal_graph_stats,
        "terminal_graph_structure": matching_structure,
        "k4_vertex_indices": k4_payload,
        "k4_values": [
            [fraction_text(primary.values[index].value) for index in clique]
            for clique in k4s
        ],
        "verifier_replays": verifier_replays,
        "acceptance_checks": {
            "all_frozen_hashes_match": True,
            "all_4096_masks_accounted": True,
            "canonical_expression_ledgers_match": True,
            "canonical_value_ledgers_match": True,
            "complete_graph_ledgers_match": True,
            "all_pairs_recomputed_exactly": True,
            "k4_lists_match": True,
            "matching_structure_verified": True,
            "every_k4_passes_both_full_verifiers": True,
        },
    }
    terminal = {
        "schema": "rank12_boolean_cube_terminal_referee/v1",
        "status": "PASS",
        "result": "VERIFIED_HIT" if k4s else "SCOPED_NO_HIT",
        "scope": scope,
        "manifest_sha256": context.manifest_sha256,
        "route_spec_sha256": context.route_sha256,
        "counts": comparison["counts"],
        "canonical_ledger_hashes": comparison["canonical_ledger_hashes"],
        "terminal_graph_structure": matching_structure,
        "comparison_path": str(context.comparison_path),
        "k4_vertex_indices": k4_payload,
        "verifier_replay_count": len(verifier_replays),
        "negative_result_is_not_global_nonexistence": not bool(k4s),
    }
    return comparison, terminal


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--manifest", required=True, type=Path)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    context: FrozenContext | None = None
    try:
        context = load_context(args.manifest)
        comparison, terminal = compare(context)
        atomic_write_json(context.comparison_path, comparison)
        terminal["comparison_sha256"] = sha256_file(context.comparison_path)
        atomic_write_json(context.terminal_path, terminal)
        print(json.dumps({"status": "PASS", "result": terminal["result"], "counts": terminal["counts"]}, sort_keys=True))
        return 0
    except (OSError, RefereeError, subprocess.SubprocessError, ValueError) as exc:
        failure = {"schema": "rank12_boolean_cube_terminal_referee/v1", "status": "FAILED", "error": str(exc)}
        if context is not None:
            failure["manifest_sha256"] = context.manifest_sha256
            atomic_write_json(context.terminal_path, failure)
        print(json.dumps({"status": "FAILED", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
