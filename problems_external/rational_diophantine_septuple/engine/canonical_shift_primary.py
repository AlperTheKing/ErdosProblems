#!/usr/bin/env python3
"""Primary exact engine for the terminal embedded-triple canonical shift.

The full mode enumerates the frozen 80,040 catalogue contexts.  It is guarded
by a frozen manifest hash and an explicit authorization token.  Preflight mode
validates all 2,001 source sextuples but emits only the fixed 400-context
calibration ledger.

Only exact ``Fraction`` arithmetic and integer square roots are used.  A
survivor is passed, as exact rational strings, to both standalone septuple
verifiers in separate subprocesses.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SCHEMA = "canonical_shift_manifest/v1"
RESULT_SCHEMA = "rational_diophantine_septuple/canonical_shift_primary_result/v1"
ROUTE_ID = "terminal_embedded_triple_canonical_shift"
FULL_AUTHORIZATION_TOKEN = "CANONICAL_SHIFT_FULL_80040_V1"

CATALOGUE_REL = "sources/2001.sextuples.txt"
PRIMARY_ENGINE_REL = "engine/canonical_shift_primary.py"
INDEPENDENT_SOURCE_REL = "engine/canonical_shift_independent.cpp"
INDEPENDENT_EXECUTABLE_REL = "engine/canonical_shift_independent.exe"
PRIMARY_VERIFIER_REL = "engine/verify_tuple.py"
INDEPENDENT_VERIFIER_REL = "engine/verify_septuple_independent.py"

CATALOGUE_SHA256 = "426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933"
PRIMARY_VERIFIER_SHA256 = "E0B86F53FFA3769EBF2D37F5571DC20414272DC0024944E75E61F217DAD36D33"
INDEPENDENT_VERIFIER_SHA256 = "0750D1B36B8ADCCC191072BE4C2011AA7126986F3E16EAD64BE2CB17FB934679"

EXPECTED_RECORD_COUNT = 2001
EXPECTED_VALUES_PER_RECORD = 6
PAIR_CHECKS_PER_RECORD = 15
EXPECTED_CATALOGUE_PAIR_CHECKS = EXPECTED_RECORD_COUNT * PAIR_CHECKS_PER_RECORD
POSITION_TRIPLES = tuple(itertools.combinations(range(6), 3))
POSITION_MASKS = tuple(sum(1 << position for position in triple) for triple in POSITION_TRIPLES)
SIGNS = (-1, 1)
CONTEXTS_PER_RECORD = len(POSITION_TRIPLES) * len(SIGNS)
EXPECTED_CONTEXT_COUNT = EXPECTED_RECORD_COUNT * CONTEXTS_PER_RECORD
CALIBRATION_RECORD_IDS = (1, 2, 5, 12, 100, 251, 501, 1000, 1500, 2001)
EXPECTED_CALIBRATION_CONTEXT_COUNT = len(CALIBRATION_RECORD_IDS) * CONTEXTS_PER_RECORD

DEGENERACY_LABELS = (
    "ZERO",
    "SELECTED_DUPLICATE",
    "COMPLEMENT_DUPLICATE",
    "DISTINCT_NONZERO",
)
LEDGER_FIELDS = (
    "ordinal",
    "record_id",
    "i",
    "j",
    "k",
    "position_mask",
    "sign",
    "r_num",
    "r_den",
    "s_num",
    "s_den",
    "t_num",
    "t_den",
    "d_num",
    "d_den",
    "degeneracy",
    "comp0",
    "comp1",
    "comp2",
    "survivor",
)
LEDGER_HEADER = "\t".join(LEDGER_FIELDS) + "\n"

RECORD_PATTERN_TEXT = r"^\((\d+)\)\s+\[([^\]]+)\]\s*(.*)$"
RECORD_RE = re.compile(RECORD_PATTERN_TEXT)
RECORD_PREFIX_RE = re.compile(r"^\(\d+\)")
RATIONAL_PATTERN_TEXT = r"^([+-]?\d+)(?:/([+-]?\d+))?$"
RATIONAL_RE = re.compile(RATIONAL_PATTERN_TEXT)


def default_problem_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def repository_root(problem_dir: Path) -> Path:
    resolved = problem_dir.resolve()
    expected_suffix = Path("problems_external") / "rational_diophantine_septuple"
    if Path(*resolved.parts[-2:]) != expected_suffix:
        raise ValueError(
            "--problem-dir must end with problems_external/rational_diophantine_septuple"
        )
    return resolved.parent.parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def pretty_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(token: str, *, label: str) -> Fraction:
    stripped = token.strip()
    if not stripped:
        raise ValueError(f"{label}: empty rational token")
    if RATIONAL_RE.fullmatch(stripped) is None:
        raise ValueError(f"{label}: rational token violates the frozen grammar: {token!r}")
    try:
        return Fraction(stripped)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{label}: invalid exact rational {token!r}") from exc


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


def compatibility_root(left: Fraction, right: Fraction) -> Fraction | None:
    return rational_square_root(left * right + 1)


@dataclass(frozen=True)
class CatalogueRecord:
    record_id: int
    values: tuple[Fraction, ...]
    annotation: str
    source_line: int


def parse_catalogue(path: Path) -> tuple[CatalogueRecord, ...]:
    records: list[CatalogueRecord] = []
    text = path.read_text(encoding="utf-8")
    for source_line, line in enumerate(text.splitlines(), start=1):
        match = RECORD_RE.match(line)
        if match is None:
            if RECORD_PREFIX_RE.match(line):
                raise ValueError(f"malformed catalogue record at source line {source_line}")
            continue
        record_id = int(match.group(1))
        parts = match.group(2).split(",")
        if len(parts) != EXPECTED_VALUES_PER_RECORD:
            raise ValueError(
                f"record {record_id}: expected {EXPECTED_VALUES_PER_RECORD} values, found {len(parts)}"
            )
        values = tuple(
            parse_fraction(part, label=f"record {record_id} value {offset + 1}")
            for offset, part in enumerate(parts)
        )
        records.append(CatalogueRecord(record_id, values, match.group(3), source_line))

    expected_ids = list(range(1, EXPECTED_RECORD_COUNT + 1))
    observed_ids = [record.record_id for record in records]
    if len(records) != EXPECTED_RECORD_COUNT:
        raise ValueError(
            f"expected {EXPECTED_RECORD_COUNT} catalogue records, parsed {len(records)}"
        )
    if observed_ids != expected_ids:
        raise ValueError("catalogue record identifiers are not exactly 1..2001 in source order")
    return tuple(records)


def validate_catalogue(records: Sequence[CatalogueRecord]) -> dict[str, int]:
    pair_checks = 0
    zero_records = 0
    duplicate_records = 0
    for record in records:
        record_has_zero = any(value == 0 for value in record.values)
        record_has_duplicate = len(set(record.values)) != EXPECTED_VALUES_PER_RECORD
        if record_has_zero:
            zero_records += 1
        if record_has_duplicate:
            duplicate_records += 1
        if record_has_zero or record_has_duplicate:
            raise ArithmeticError(
                f"record {record.record_id} contains zero or duplicate source values"
            )
        for left, right in itertools.combinations(record.values, 2):
            pair_checks += 1
            if compatibility_root(left, right) is None:
                raise ArithmeticError(
                    f"record {record.record_id} fails source pair {fraction_text(left)}, {fraction_text(right)}"
                )
    if pair_checks != EXPECTED_CATALOGUE_PAIR_CHECKS:
        raise ArithmeticError(
            f"catalogue validation performed {pair_checks} pair checks, expected {EXPECTED_CATALOGUE_PAIR_CHECKS}"
        )
    return {
        "record_count": len(records),
        "pair_check_count": pair_checks,
        "zero_record_count": zero_records,
        "duplicate_record_count": duplicate_records,
    }


def catalogue_triple_statistics(records: Sequence[CatalogueRecord]) -> dict[str, int]:
    multiplicities: dict[tuple[Fraction, Fraction, Fraction], int] = {}
    for record in records:
        for positions in POSITION_TRIPLES:
            key = tuple(sorted(record.values[position] for position in positions))
            multiplicities[key] = multiplicities.get(key, 0) + 1
    triple_contexts = sum(multiplicities.values())
    distinct_keys = len(multiplicities)
    repeated = [count for count in multiplicities.values() if count > 1]
    statistics = {
        "triple_context_count": triple_contexts,
        "distinct_unordered_triple_key_count": distinct_keys,
        "duplicate_context_excess": triple_contexts - distinct_keys,
        "repeated_triple_key_count": len(repeated),
        "contexts_on_repeated_keys": sum(repeated),
    }
    expected = {
        "triple_context_count": 40020,
        "distinct_unordered_triple_key_count": 39490,
        "duplicate_context_excess": 530,
        "repeated_triple_key_count": 400,
        "contexts_on_repeated_keys": 930,
    }
    if statistics != expected:
        raise ArithmeticError(
            f"catalogue triple statistics mismatch: {statistics} != {expected}"
        )
    return statistics


@dataclass(frozen=True)
class ContextRow:
    ordinal: int
    record_id: int
    positions: tuple[int, int, int]
    position_mask: int
    sign: int
    roots: tuple[Fraction, Fraction, Fraction]
    candidate: Fraction
    degeneracy: str
    complement_bits: tuple[int, int, int]
    survivor: int

    def ledger_line(self) -> str:
        i, j, k = self.positions
        r, s, t = self.roots
        comp0, comp1, comp2 = self.complement_bits
        fields: tuple[object, ...] = (
            self.ordinal,
            self.record_id,
            i,
            j,
            k,
            self.position_mask,
            self.sign,
            r.numerator,
            r.denominator,
            s.numerator,
            s.denominator,
            t.numerator,
            t.denominator,
            self.candidate.numerator,
            self.candidate.denominator,
            self.degeneracy,
            comp0,
            comp1,
            comp2,
            self.survivor,
        )
        return "\t".join(str(field) for field in fields) + "\n"


@dataclass(frozen=True)
class Survivor:
    row: ContextRow
    source_values: tuple[Fraction, ...]


def classify_degeneracy(
    candidate: Fraction,
    selected: Sequence[Fraction],
    complements: Sequence[Fraction],
) -> str:
    if candidate == 0:
        return "ZERO"
    if candidate in selected:
        return "SELECTED_DUPLICATE"
    if candidate in complements:
        return "COMPLEMENT_DUPLICATE"
    return "DISTINCT_NONZERO"


def context_row(
    record: CatalogueRecord,
    position_index: int,
    positions: tuple[int, int, int],
    sign: int,
) -> ContextRow:
    if sign not in SIGNS:
        raise ValueError(f"invalid sign {sign}")
    i, j, k = positions
    a, b, c = (record.values[i], record.values[j], record.values[k])
    complement_positions = tuple(position for position in range(6) if position not in positions)
    complements = tuple(record.values[position] for position in complement_positions)

    r = compatibility_root(a, b)
    s = compatibility_root(a, c)
    t = compatibility_root(b, c)
    if r is None or s is None or t is None:
        raise ArithmeticError(
            f"record {record.record_id}, positions {positions}: selected triple is not Diophantine"
        )
    candidate = a + b + c + 2 * a * b * c + sign * 2 * r * s * t
    opposite_candidate = a + b + c + 2 * a * b * c - sign * 2 * r * s * t

    # Check all eight root-sign choices.  Even root-sign parity preserves the
    # current sign label; odd parity exchanges the two canonical candidates.
    for r_sign, s_sign, t_sign in itertools.product(SIGNS, repeat=3):
        signed_candidate = (
            a
            + b
            + c
            + 2 * a * b * c
            + sign * 2 * (r_sign * r) * (s_sign * s) * (t_sign * t)
        )
        expected_candidate = (
            candidate if r_sign * s_sign * t_sign == 1 else opposite_candidate
        )
        if signed_candidate != expected_candidate:
            raise ArithmeticError(
                f"record {record.record_id}, positions {positions}, sign {sign}: root-sign assertion failed"
            )

    identities = (
        a * candidate + 1 == (a * t + sign * r * s) ** 2,
        b * candidate + 1 == (b * s + sign * r * t) ** 2,
        c * candidate + 1 == (c * r + sign * s * t) ** 2,
    )
    if not all(identities):
        raise ArithmeticError(
            f"record {record.record_id}, positions {positions}, sign {sign}: canonical identities failed"
        )

    degeneracy = classify_degeneracy(candidate, (a, b, c), complements)
    if degeneracy not in DEGENERACY_LABELS:
        raise ArithmeticError("internal degeneracy label is outside the frozen contract")
    complement_bits = tuple(
        int(compatibility_root(candidate, value) is not None) for value in complements
    )
    survivor = int(degeneracy == "DISTINCT_NONZERO" and complement_bits == (1, 1, 1))
    sign_offset = 0 if sign == -1 else 1
    ordinal = (record.record_id - 1) * CONTEXTS_PER_RECORD + position_index * 2 + sign_offset
    position_mask = sum(1 << position for position in positions)
    if position_mask != POSITION_MASKS[position_index]:
        raise ArithmeticError("position-mask ordering contract failed")
    return ContextRow(
        ordinal,
        record.record_id,
        positions,
        position_mask,
        sign,
        (r, s, t),
        candidate,
        degeneracy,
        complement_bits,  # type: ignore[arg-type]
        survivor,
    )


def enumerate_rows(
    records: Sequence[CatalogueRecord], selected_record_ids: Sequence[int]
) -> Iterator[tuple[ContextRow, CatalogueRecord]]:
    selected = set(selected_record_ids)
    if len(selected) != len(selected_record_ids):
        raise ValueError("selected record identifiers must be distinct")
    for record in records:
        if record.record_id not in selected:
            continue
        for position_index, positions in enumerate(POSITION_TRIPLES):
            for sign in SIGNS:
                yield context_row(record, position_index, positions, sign), record


def _expect_equal(observed: Any, expected: Any, label: str) -> None:
    if observed != expected:
        raise ValueError(f"manifest {label} contract mismatch")


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9A-F]{64}", value) is not None


def _contains_pending(value: Any) -> bool:
    if value == "PENDING":
        return True
    if isinstance(value, dict):
        return any(_contains_pending(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_pending(item) for item in value)
    return False


def _validate_artifact(
    repo_root: Path,
    contract: Any,
    *,
    expected_path: str,
    allow_pending: bool,
    registered_sha256: str | None = None,
) -> None:
    if not isinstance(contract, dict) or set(contract) != {"path", "sha256"}:
        raise ValueError(f"manifest artifact shape mismatch for {expected_path}")
    if contract["path"] != expected_path:
        raise ValueError(f"manifest artifact path mismatch for {expected_path}")
    artifact_path = repo_root / expected_path
    declared_hash = contract["sha256"]
    if declared_hash == "PENDING":
        if not allow_pending:
            raise ValueError(f"full mode forbids PENDING artifact {expected_path}")
        return
    if not _is_sha256(declared_hash):
        raise ValueError(f"manifest artifact SHA-256 is invalid for {expected_path}")
    if registered_sha256 is not None and declared_hash != registered_sha256:
        raise ValueError(f"manifest registered SHA-256 mismatch for {expected_path}")
    if not artifact_path.is_file():
        raise FileNotFoundError(f"frozen artifact is missing: {artifact_path}")
    if sha256_file(artifact_path) != declared_hash:
        raise ValueError(f"frozen artifact SHA-256 mismatch for {expected_path}")


def validate_manifest_contract(
    problem_dir: Path,
    manifest_path: Path,
    manifest: Any,
    *,
    allow_pending: bool,
) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be an object")
    repo_root = repository_root(problem_dir)
    try:
        manifest_relative = manifest_path.resolve().relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError("manifest must be inside the repository") from exc
    if manifest_path.name != "manifest.json":
        raise ValueError("manifest filename must be manifest.json")
    run_relative = Path(manifest_relative).parent.as_posix()

    _expect_equal(manifest.get("schema"), SCHEMA, "schema")
    _expect_equal(manifest.get("route"), "terminal embedded-triple canonical shift", "route")
    source_path = (
        "problems_external/rational_diophantine_septuple/"
        "sources/2001.sextuples.txt"
    )
    expected_source = {
        "path": source_path,
        "sha256": CATALOGUE_SHA256,
        "byte_count": 255092,
        "record_regex": r"^\((\d+)\)\s+\[([^]]+)\]",
        "rational_regex": RATIONAL_PATTERN_TEXT,
        "record_count": EXPECTED_RECORD_COUNT,
        "record_ids": "exactly contiguous 1..2001",
        "nonrecord_lines": "ignored",
        "record_like_malformed_lines": "fatal",
        "values_per_record": EXPECTED_VALUES_PER_RECORD,
        "required_square_pairs_per_record": PAIR_CHECKS_PER_RECORD,
    }
    _expect_equal(manifest.get("source"), expected_source, "source")
    _validate_artifact(
        repo_root,
        {"path": source_path, "sha256": manifest["source"]["sha256"]},
        expected_path=source_path,
        allow_pending=False,
        registered_sha256=CATALOGUE_SHA256,
    )
    if (repo_root / source_path).stat().st_size != manifest["source"]["byte_count"]:
        raise ValueError("manifest source byte-count contract mismatch")

    expected_enumeration = {
        "position_base": 0,
        "position_triples": [
            {"positions": list(triple), "mask": mask}
            for triple, mask in zip(POSITION_TRIPLES, POSITION_MASKS)
        ],
        "signs": list(SIGNS),
        "root_convention": "nonnegative reduced rational roots for ab+1, ac+1, bc+1",
        "candidate_formula": "d=a+b+c+2*a*b*c+sign*2*r*s*t",
        "record_order": "increasing record_id 1..2001",
        "triple_order": "listed lexicographic order",
        "sign_order": "-1 then +1",
        "declared_contexts": EXPECTED_CONTEXT_COUNT,
        "declared_triple_contexts": EXPECTED_RECORD_COUNT * len(POSITION_TRIPLES),
        "distinct_unordered_triple_keys": 39490,
        "duplicate_context_excess": 530,
        "repeated_triple_keys": 400,
        "contexts_on_repeated_keys": 930,
        "expected_extension_identity_checks": 3 * EXPECTED_CONTEXT_COUNT,
        "expected_root_sign_assertions": 8 * EXPECTED_CONTEXT_COUNT,
        "expected_sign_collapses": 0,
        "expected_degeneracy_counts": {
            "ZERO": 291,
            "SELECTED_DUPLICATE": 102,
            "COMPLEMENT_DUPLICATE": 8416,
            "DISTINCT_NONZERO": 71231,
        },
    }
    _expect_equal(manifest.get("enumeration"), expected_enumeration, "enumeration")

    expected_engine_paths = {
        "primary": "problems_external/rational_diophantine_septuple/engine/canonical_shift_primary.py",
        "independent_source": "problems_external/rational_diophantine_septuple/engine/canonical_shift_independent.cpp",
        "independent_binary": "problems_external/rational_diophantine_septuple/engine/canonical_shift_independent.exe",
    }
    engines = manifest.get("engines")
    if not isinstance(engines, dict) or set(engines) != {
        "primary",
        "independent_source",
        "independent_binary",
        "referee",
    }:
        raise ValueError("manifest engines contract mismatch")
    for name, expected_path in expected_engine_paths.items():
        _validate_artifact(
            repo_root,
            engines[name],
            expected_path=expected_path,
            allow_pending=allow_pending,
        )
    referee = engines["referee"]
    expected_referee_path = (
        "problems_external/rational_diophantine_septuple/engine/referee_canonical_shift.py"
    )
    expected_report_path = f"{run_relative}/referee_report.json"
    if not isinstance(referee, dict) or set(referee) != {
        "path",
        "sha256",
        "report_path",
        "report_sha256",
    }:
        raise ValueError("manifest referee contract mismatch")
    if referee["path"] != expected_referee_path or referee["report_path"] != expected_report_path:
        raise ValueError("manifest referee paths mismatch")
    for key, path_key in (("sha256", "path"), ("report_sha256", "report_path")):
        declared_hash = referee[key]
        if declared_hash == "PENDING":
            if not allow_pending:
                raise ValueError(f"full mode forbids PENDING referee {key}")
            continue
        if not _is_sha256(declared_hash):
            raise ValueError(f"manifest referee {key} is not a SHA-256")
        artifact_path = repo_root / referee[path_key]
        if not artifact_path.is_file() or sha256_file(artifact_path) != declared_hash:
            raise ValueError(f"manifest referee {path_key} hash mismatch")

    expected_verifiers = {
        "primary": {
            "path": "problems_external/rational_diophantine_septuple/engine/verify_tuple.py",
            "sha256": PRIMARY_VERIFIER_SHA256,
        },
        "independent": {
            "path": "problems_external/rational_diophantine_septuple/engine/verify_septuple_independent.py",
            "sha256": INDEPENDENT_VERIFIER_SHA256,
        },
    }
    _expect_equal(manifest.get("verifiers"), expected_verifiers, "verifiers")
    for contract in expected_verifiers.values():
        _validate_artifact(
            repo_root,
            contract,
            expected_path=contract["path"],
            allow_pending=False,
            registered_sha256=contract["sha256"],
        )

    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict) or set(runtime) != {
        "primary",
        "independent",
        "aggregate_workers_max",
        "primary_command",
        "independent_command",
    }:
        raise ValueError("manifest runtime contract mismatch")
    _expect_equal(runtime["primary"], f"CPython {platform.python_version()}", "runtime.primary")
    _expect_equal(
        runtime["independent"],
        "g++ 16.1.0 with boost::multiprecision::cpp_int",
        "runtime.independent",
    )
    _expect_equal(runtime["aggregate_workers_max"], 64, "runtime.aggregate_workers_max")
    for key in ("primary_command", "independent_command"):
        if runtime[key] == "PENDING":
            if not allow_pending:
                raise ValueError(f"full mode forbids PENDING runtime {key}")
        elif not isinstance(runtime[key], str) or not runtime[key].strip():
            raise ValueError(f"manifest runtime {key} must be a nonempty frozen string")

    calibration = manifest.get("calibration")
    if not isinstance(calibration, dict) or set(calibration) != {
        "record_ids",
        "declared_contexts",
        "ordinal_rule",
        "ledger_hash_scope",
        "expected_ledger_byte_count",
        "expected_ledger_sha256",
        "summary_schema",
        "summary_serialization",
        "expected_summary_sha256",
        "expected_degeneracy_counts",
        "expected_complement_pattern_counts",
        "expected_survivor_count",
    }:
        raise ValueError("manifest calibration contract mismatch")
    _expect_equal(calibration["record_ids"], list(CALIBRATION_RECORD_IDS), "calibration.record_ids")
    _expect_equal(
        calibration["declared_contexts"],
        EXPECTED_CALIBRATION_CONTEXT_COUNT,
        "calibration.declared_contexts",
    )
    _expect_equal(
        calibration["ordinal_rule"],
        "(record_id-1)*40 + 2*triple_ordinal + sign_index, with sign_index 0 for -1 and 1 for +1",
        "calibration.ordinal_rule",
    )
    _expect_equal(
        calibration["ledger_hash_scope"],
        "ASCII header plus 400 rows, LF after every line including the final row",
        "calibration.ledger_hash_scope",
    )
    _expect_equal(calibration["expected_ledger_byte_count"], 35384, "calibration.expected_ledger_byte_count")
    _expect_equal(calibration["summary_schema"], "canonical_shift_calibration_summary/v1", "calibration.summary_schema")
    _expect_equal(
        calibration["summary_serialization"],
        "compact ASCII JSON with sorted keys and one final LF",
        "calibration.summary_serialization",
    )
    _expect_equal(
        calibration["expected_degeneracy_counts"],
        {"ZERO": 4, "SELECTED_DUPLICATE": 1, "COMPLEMENT_DUPLICATE": 52, "DISTINCT_NONZERO": 343},
        "calibration.expected_degeneracy_counts",
    )
    _expect_equal(
        calibration["expected_complement_pattern_counts"],
        {"000": 342, "001": 0, "010": 0, "011": 28, "100": 1, "101": 17, "110": 7, "111": 5},
        "calibration.expected_complement_pattern_counts",
    )
    _expect_equal(calibration["expected_survivor_count"], 0, "calibration.expected_survivor_count")
    for key in ("expected_ledger_sha256", "expected_summary_sha256"):
        if calibration[key] == "PENDING":
            if not allow_pending:
                raise ValueError(f"full mode forbids PENDING calibration {key}")
        elif not _is_sha256(calibration[key]):
            raise ValueError(f"manifest calibration {key} is not a SHA-256")

    expected_ledger = {
        "encoding": "ASCII TSV with LF",
        "header": LEDGER_HEADER.rstrip("\n"),
        "ordinal_range": [0, EXPECTED_CONTEXT_COUNT - 1],
        "degeneracy_labels": list(DEGENERACY_LABELS),
        "degeneracy_precedence": list(DEGENERACY_LABELS),
        "rational_normalization": "gcd-reduced numerator and positive denominator",
        "complement_bits": "three exact 0/1 square-test results in increasing complementary-position order",
        "survivor_rule": "1 exactly when degeneracy is DISTINCT_NONZERO and comp0=comp1=comp2=1",
        "retain_every_context": True,
        "full_ledger_filename": "ledger.tsv",
        "full_summary_filename": "summary.json",
        "full_survivors_filename": "survivors.json",
    }
    _expect_equal(manifest.get("ledger"), expected_ledger, "ledger")

    expected_outputs = {
        "primary_dir": f"{run_relative}/primary_full",
        "independent_dir": f"{run_relative}/independent_full",
        "comparison_path": f"{run_relative}/comparison.json",
        "terminal_referee_path": f"{run_relative}/terminal_referee.json",
    }
    _expect_equal(manifest.get("outputs"), expected_outputs, "outputs")
    expected_acceptance = {
        "success": "at least one survivor accepted by both full septuple verifiers",
        "scoped_no_hit": "both engines account for all 80040 contexts with matching canonical ledgers and no survivor",
        "failure": "any source, count, identity, ledger, engine, or verifier disagreement",
        "negative_scope": "only these 80040 terminal canonical-shift contexts",
        "forbidden_followup": "any further catalogue transform or bounded catalogue family",
    }
    _expect_equal(manifest.get("acceptance"), expected_acceptance, "acceptance")
    _expect_equal(set(manifest), {
        "schema", "route", "source", "enumeration", "engines", "verifiers",
        "runtime", "calibration", "ledger", "outputs", "acceptance"
    }, "top-level keys")
    if not allow_pending and _contains_pending(manifest):
        raise ValueError("full mode forbids every PENDING manifest field")


def load_and_validate_manifest(
    problem_dir: Path,
    manifest_path: Path,
    expected_sha256: str,
    *,
    allow_pending: bool,
) -> tuple[dict[str, Any], str]:
    expected_sha256 = expected_sha256.strip().upper()
    if not re.fullmatch(r"[0-9A-F]{64}", expected_sha256):
        raise ValueError("--expected-manifest-sha256 must be 64 uppercase/lowercase hexadecimal digits")
    observed_sha256 = sha256_file(manifest_path)
    if observed_sha256 != expected_sha256:
        raise ValueError(
            f"manifest SHA-256 mismatch: observed {observed_sha256}, expected {expected_sha256}"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot parse manifest {manifest_path}") from exc
    validate_manifest_contract(
        problem_dir, manifest_path, manifest, allow_pending=allow_pending
    )
    return manifest, observed_sha256


def atomic_write(path: Path, payload: bytes, *, overwrite: bool) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temporary.exists():
        raise FileExistsError(f"temporary output already exists: {temporary}")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise


class AtomicLedger:
    def __init__(self, path: Path, *, overwrite: bool) -> None:
        self.path = path.resolve()
        self.overwrite = overwrite
        self.temporary = self.path.with_name(f".{self.path.name}.tmp-{os.getpid()}")
        self.stream: Any = None
        self.digest = hashlib.sha256()
        self.byte_count = 0
        self.data_row_count = 0

    def __enter__(self) -> "AtomicLedger":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and not self.overwrite:
            raise FileExistsError(f"refusing to overwrite existing artifact: {self.path}")
        if self.temporary.exists():
            raise FileExistsError(f"temporary output already exists: {self.temporary}")
        self.stream = self.temporary.open("xb")
        self.write_raw(LEDGER_HEADER.encode("ascii"))
        return self

    def write_raw(self, payload: bytes) -> None:
        if self.stream is None:
            raise RuntimeError("ledger is not open")
        self.stream.write(payload)
        self.digest.update(payload)
        self.byte_count += len(payload)

    def write_row(self, row: ContextRow) -> None:
        self.write_raw(row.ledger_line().encode("ascii"))
        self.data_row_count += 1

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.stream is not None:
            if exc_type is None:
                self.stream.flush()
                os.fsync(self.stream.fileno())
            self.stream.close()
        if exc_type is None:
            os.replace(self.temporary, self.path)
        elif self.temporary.exists():
            self.temporary.unlink()

    @property
    def sha256(self) -> str:
        return self.digest.hexdigest().upper()


def invoke_json_verifier(
    executable: Sequence[str], payload: dict[str, Any], *, label: str
) -> dict[str, Any]:
    completed = subprocess.run(
        list(executable),
        input=json.dumps(payload, sort_keys=True, separators=(",", ":")),
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise ArithmeticError(
            f"{label} verifier exited {completed.returncode}; stderr={completed.stderr.strip()!r}"
        )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ArithmeticError(f"{label} verifier emitted invalid JSON") from exc
    if not isinstance(report, dict):
        raise ArithmeticError(f"{label} verifier report is not an object")
    if report.get("valid") is not True or report.get("pair_count") != 21:
        raise ArithmeticError(f"{label} verifier rejected an engine survivor")
    return report


def verify_survivor(
    problem_dir: Path, survivor: Survivor, survivor_index: int
) -> dict[str, Any]:
    candidate_values = tuple(survivor.source_values) + (survivor.row.candidate,)
    candidate_strings = [fraction_text(value) for value in candidate_values]
    name = (
        f"canonical-shift-record-{survivor.row.record_id}-"
        f"mask-{survivor.row.position_mask}-sign-{survivor.row.sign}"
    )
    payload = {"name": name, "values": candidate_strings}
    primary = invoke_json_verifier(
        [
            sys.executable,
            str(problem_dir / PRIMARY_VERIFIER_REL),
            "--json",
            "-",
            "--format",
            "json",
            "--expect-size",
            "7",
        ],
        payload,
        label="primary",
    )
    independent = invoke_json_verifier(
        [
            sys.executable,
            str(problem_dir / INDEPENDENT_VERIFIER_REL),
            "--json",
            "-",
            "--format",
            "json",
        ],
        payload,
        label="independent",
    )
    if primary.get("values") != candidate_strings or independent.get("values") != candidate_strings:
        raise ArithmeticError("standalone verifier canonical values disagree with the exact-string handoff")
    return {
        "survivor_index": survivor_index,
        "ordinal": survivor.row.ordinal,
        "record_id": survivor.row.record_id,
        "positions": list(survivor.row.positions),
        "position_mask": survivor.row.position_mask,
        "sign": survivor.row.sign,
        "candidate": fraction_text(survivor.row.candidate),
        "values": candidate_strings,
        "primary_report": primary,
        "independent_report": independent,
        "independently_verified": True,
    }


def run_enumeration(
    *,
    problem_dir: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
    manifest_sha256: str,
    output_dir: Path,
    mode: str,
    overwrite: bool,
) -> dict[str, Any]:
    catalogue_path = problem_dir / CATALOGUE_REL
    records = parse_catalogue(catalogue_path)
    validation = validate_catalogue(records)
    triple_statistics = catalogue_triple_statistics(records)
    selected_record_ids: Sequence[int]
    expected_rows: int
    if mode == "preflight":
        selected_record_ids = CALIBRATION_RECORD_IDS
        expected_rows = EXPECTED_CALIBRATION_CONTEXT_COUNT
    elif mode == "full":
        selected_record_ids = tuple(range(1, EXPECTED_RECORD_COUNT + 1))
        expected_rows = EXPECTED_CONTEXT_COUNT
    else:
        raise ValueError(f"unsupported enumeration mode {mode}")

    output_dir = output_dir.resolve()
    ledger_path = output_dir / "ledger.tsv"
    survivors_path = output_dir / "survivors.json"
    verifier_reports_path = output_dir / "verifier_reports.json"
    summary_path = output_dir / "summary.json"
    calibration_summary_path = output_dir / "calibration_summary.json"
    guarded_paths = [ledger_path, survivors_path, verifier_reports_path, summary_path]
    if mode == "preflight":
        guarded_paths.append(calibration_summary_path)
    for path in guarded_paths:
        if path.exists() and not overwrite:
            raise FileExistsError(f"refusing to overwrite existing artifact: {path}")

    status_counts = {label: 0 for label in DEGENERACY_LABELS}
    complement_mask_histogram = {str(mask): 0 for mask in range(8)}
    complement_pattern_counts = {f"{mask:03b}": 0 for mask in range(8)}
    survivors: list[Survivor] = []
    previous_ordinal = -1
    sign_collapse_count = 0

    with AtomicLedger(ledger_path, overwrite=overwrite) as ledger:
        for row, record in enumerate_rows(records, selected_record_ids):
            if row.ordinal <= previous_ordinal:
                raise ArithmeticError("canonical row order is not strictly increasing by global ordinal")
            previous_ordinal = row.ordinal
            ledger.write_row(row)
            status_counts[row.degeneracy] += 1
            complement_mask = sum(bit << offset for offset, bit in enumerate(row.complement_bits))
            complement_mask_histogram[str(complement_mask)] += 1
            pattern = "".join(str(bit) for bit in row.complement_bits)
            complement_pattern_counts[pattern] += 1
            if row.sign == -1 and any(root == 0 for root in row.roots):
                sign_collapse_count += 1
            if row.survivor:
                survivors.append(Survivor(row, record.values))

    if ledger.data_row_count != expected_rows:
        raise ArithmeticError(
            f"enumerated {ledger.data_row_count} rows, expected {expected_rows} in {mode} mode"
        )
    if sum(status_counts.values()) != expected_rows:
        raise ArithmeticError("degeneracy counts do not sum to the exact row count")
    if sum(complement_mask_histogram.values()) != expected_rows:
        raise ArithmeticError("complement-mask counts do not sum to the exact row count")
    if sum(complement_pattern_counts.values()) != expected_rows:
        raise ArithmeticError("complement-pattern counts do not sum to the exact row count")
    if sign_collapse_count != 0:
        raise ArithmeticError(f"observed {sign_collapse_count} root-sign candidate collapses")
    expected_calibration_ledger = manifest["calibration"]["expected_ledger_sha256"]
    if (
        mode == "preflight"
        and expected_calibration_ledger != "PENDING"
        and ledger.sha256 != expected_calibration_ledger
    ):
        raise ArithmeticError(
            "primary calibration ledger SHA-256 differs from the frozen manifest"
        )
    if (
        mode == "preflight"
        and ledger.byte_count != manifest["calibration"]["expected_ledger_byte_count"]
    ):
        raise ArithmeticError("primary calibration ledger byte count differs from the frozen manifest")
    if mode == "preflight":
        if status_counts != manifest["calibration"]["expected_degeneracy_counts"]:
            raise ArithmeticError("primary calibration degeneracy counts differ from the frozen manifest")
        if complement_pattern_counts != manifest["calibration"]["expected_complement_pattern_counts"]:
            raise ArithmeticError("primary calibration complement patterns differ from the frozen manifest")
        if len(survivors) != manifest["calibration"]["expected_survivor_count"]:
            raise ArithmeticError("primary calibration survivor count differs from the frozen manifest")
    else:
        if status_counts != manifest["enumeration"]["expected_degeneracy_counts"]:
            raise ArithmeticError("full degeneracy counts differ from the frozen manifest")

    survivor_reports = [
        verify_survivor(problem_dir, survivor, index)
        for index, survivor in enumerate(survivors)
    ]
    survivor_rows = [
        {
            "candidate": fraction_text(survivor.row.candidate),
            "ordinal": survivor.row.ordinal,
            "position_triple": list(survivor.row.positions),
            "record_id": survivor.row.record_id,
            "sign": survivor.row.sign,
            "source_values": [fraction_text(value) for value in survivor.source_values],
        }
        for survivor in survivors
    ]
    if [row["ordinal"] for row in survivor_rows] != sorted(
        row["ordinal"] for row in survivor_rows
    ):
        raise ArithmeticError("survivor rows are not ordered by ordinal")
    survivor_payload = canonical_json_bytes(
        {
            "schema": "canonical_shift_survivors/v1",
            "survivor_count": len(survivor_rows),
            "survivors": survivor_rows,
        }
    )
    atomic_write(survivors_path, survivor_payload, overwrite=overwrite)
    verifier_reports_payload = canonical_json_bytes(
        {
            "schema": "canonical_shift_primary_verifier_reports/v1",
            "report_count": len(survivor_reports),
            "reports": survivor_reports,
        }
    )
    atomic_write(
        verifier_reports_path, verifier_reports_payload, overwrite=overwrite
    )

    calibration_summary_sha256: str | None = None
    if mode == "preflight":
        calibration_summary = {
            "schema": manifest["calibration"]["summary_schema"],
            "source_sha256": CATALOGUE_SHA256,
            "record_ids": list(CALIBRATION_RECORD_IDS),
            "record_count": len(CALIBRATION_RECORD_IDS),
            "source_pair_checks": len(CALIBRATION_RECORD_IDS) * PAIR_CHECKS_PER_RECORD,
            "context_count": ledger.data_row_count,
            "extension_identity_checks": 3 * ledger.data_row_count,
            "degeneracy_counts": status_counts,
            "complement_pattern_counts": complement_pattern_counts,
            "survivor_count": len(survivor_reports),
            "ledger_byte_count": ledger.byte_count,
            "ledger_sha256": ledger.sha256,
        }
        calibration_payload = canonical_json_bytes(calibration_summary)
        calibration_summary_sha256 = hashlib.sha256(calibration_payload).hexdigest().upper()
        if calibration_summary_sha256 != manifest["calibration"]["expected_summary_sha256"]:
            raise ArithmeticError(
                "primary neutral calibration summary SHA-256 differs from the frozen manifest"
            )
        atomic_write(calibration_summary_path, calibration_payload, overwrite=overwrite)

    status = "HIT" if survivor_reports else ("PREFLIGHT_PASS" if mode == "preflight" else "NO_HIT")
    summary: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "route_id": ROUTE_ID,
        "implementation": "primary-python-fraction-isqrt",
        "mode": mode,
        "status": status,
        "scope": (
            "all source sextuples plus the fixed 400-context calibration subset"
            if mode == "preflight"
            else "the frozen 80040 canonical-shift contexts"
        ),
        "problem_dir": str(problem_dir.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "engine_sha256": sha256_file(Path(__file__).resolve()),
        "runtime": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable": str(Path(sys.executable).resolve()),
        },
        "catalogue_validation": validation,
        "catalogue_triple_statistics": triple_statistics,
        "selected_record_ids": list(selected_record_ids),
        "expected_context_count": expected_rows,
        "context_count": ledger.data_row_count,
        "status_counts": status_counts,
        "complement_mask_histogram": complement_mask_histogram,
        "complement_pattern_counts": complement_pattern_counts,
        "extension_identity_check_count": 3 * ledger.data_row_count,
        "root_sign_assertion_count": 8 * ledger.data_row_count,
        "sign_collapse_count": sign_collapse_count,
        "survivor_count": len(survivor_reports),
        "standalone_verifier_invocation_count": 2 * len(survivor_reports),
        "ledger": {
            "path": str(ledger_path),
            "sha256": ledger.sha256,
            "byte_count": ledger.byte_count,
            "header": LEDGER_HEADER.rstrip("\n"),
            "data_row_count": ledger.data_row_count,
        },
        "survivors": {
            "path": str(survivors_path),
            "sha256": hashlib.sha256(survivor_payload).hexdigest().upper(),
            "byte_count": len(survivor_payload),
            "record_count": len(survivor_reports),
        },
        "verifier_reports": {
            "path": str(verifier_reports_path),
            "sha256": hashlib.sha256(verifier_reports_payload).hexdigest().upper(),
            "byte_count": len(verifier_reports_payload),
            "record_count": len(survivor_reports),
        },
    }
    if mode == "preflight":
        summary["neutral_calibration_summary"] = {
            "path": str(calibration_summary_path),
            "sha256": calibration_summary_sha256,
        }
    if mode == "full":
        summary["manifest_sha256"] = manifest_sha256
    summary_payload = pretty_json_bytes(summary)
    observed_summary_sha256 = hashlib.sha256(summary_payload).hexdigest().upper()
    atomic_write(summary_path, summary_payload, overwrite=overwrite)
    summary["summary_path"] = str(summary_path)
    summary["summary_sha256"] = observed_summary_sha256
    return summary


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--problem-dir",
        type=Path,
        default=default_problem_dir(),
        help="problem root; manifest artifact paths are relative to this directory",
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=("preflight", "full"), required=True)
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--full-token")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(argv)
    problem_dir = args.problem_dir.resolve()
    manifest_path = args.manifest.resolve()
    try:
        if args.expected_manifest_sha256 is None:
            raise ValueError("preflight/full mode requires --expected-manifest-sha256")
        if args.output is None:
            raise ValueError("preflight/full mode requires --output")
        if args.mode == "preflight" and args.full_token is not None:
            raise ValueError("preflight mode does not accept --full-token")
        if args.mode == "full" and args.full_token != FULL_AUTHORIZATION_TOKEN:
            raise ValueError("full mode requires the exact frozen --full-token")

        manifest, manifest_sha256 = load_and_validate_manifest(
            problem_dir,
            manifest_path,
            args.expected_manifest_sha256,
            allow_pending=args.mode == "preflight",
        )
        if args.mode == "full":
            repo_root = repository_root(problem_dir)
            expected_output = (repo_root / manifest["outputs"]["primary_dir"]).resolve()
            if args.output.resolve() != expected_output:
                raise ValueError(
                    f"full output must equal the frozen primary_dir {expected_output}"
                )
        result = run_enumeration(
            problem_dir=problem_dir,
            manifest=manifest,
            manifest_path=manifest_path,
            manifest_sha256=manifest_sha256,
            output_dir=args.output,
            mode=args.mode,
            overwrite=args.overwrite,
        )
        print(
            json.dumps(
                {
                    key: result[key]
                    for key in (
                        "mode",
                        "status",
                        "context_count",
                        "survivor_count",
                        "summary_path",
                        "summary_sha256",
                    )
                },
                sort_keys=True,
            )
        )
        return 0
    except (ArithmeticError, FileExistsError, FileNotFoundError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
