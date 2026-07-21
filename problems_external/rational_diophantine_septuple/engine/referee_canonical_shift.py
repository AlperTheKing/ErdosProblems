#!/usr/bin/env python3
"""Independent plan and terminal referee for the canonical-shift route.

The referee imports neither search engine.  It uses a private normalized
integer rational type and a strict catalogue parser.

``plan`` audits all 2,001 sextuples, all 40,020 selected triples, both signs,
all canonical extension identities, and root-sign invariance.  It evaluates
complement compatibility only for the frozen 400-row calibration, so plan mode
is not the full search.

``terminal`` is authorization-gated.  It independently reconstructs every one
of the 80,040 rows, compares both engine ledgers and both canonical survivor
files byte-for-byte, and invokes both standalone septuple verifiers for every
survivor derived by the referee itself.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Sequence


MANIFEST_SCHEMA = "canonical_shift_manifest/v1"
ROUTE = "terminal embedded-triple canonical shift"
PLAN_SCHEMA = "canonical_shift_referee_plan/v1"
TERMINAL_SCHEMA = "canonical_shift_terminal_referee/v1"
SURVIVORS_SCHEMA = "canonical_shift_survivors/v1"
CALIBRATION_SUMMARY_SCHEMA = "canonical_shift_calibration_summary/v1"
TERMINAL_TOKEN = "CANONICAL_SHIFT_TERMINAL_REPLAY_80040_V1"

SOURCE_REL = "problems_external/rational_diophantine_septuple/sources/2001.sextuples.txt"
PRIMARY_ENGINE_REL = "problems_external/rational_diophantine_septuple/engine/canonical_shift_primary.py"
INDEPENDENT_SOURCE_REL = "problems_external/rational_diophantine_septuple/engine/canonical_shift_independent.cpp"
INDEPENDENT_BINARY_REL = "problems_external/rational_diophantine_septuple/engine/canonical_shift_independent.exe"
REFEREE_REL = "problems_external/rational_diophantine_septuple/engine/referee_canonical_shift.py"
PRIMARY_VERIFIER_REL = "problems_external/rational_diophantine_septuple/engine/verify_tuple.py"
INDEPENDENT_VERIFIER_REL = "problems_external/rational_diophantine_septuple/engine/verify_septuple_independent.py"

SOURCE_SHA256 = "426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933"
PRIMARY_VERIFIER_SHA256 = "E0B86F53FFA3769EBF2D37F5571DC20414272DC0024944E75E61F217DAD36D33"
INDEPENDENT_VERIFIER_SHA256 = "0750D1B36B8ADCCC191072BE4C2011AA7126986F3E16EAD64BE2CB17FB934679"

RECORD_RE = re.compile(r"^\((\d+)\)\s+\[([^\]]+)\]\s*(.*)$")
RECORD_PREFIX_RE = re.compile(r"^\(\d+\)")
RAT_RE = re.compile(r"^([+-]?\d+)(?:/([+-]?\d+))?$")
POSITIONS = tuple(itertools.combinations(range(6), 3))
MASKS = tuple(sum(1 << position for position in triple) for triple in POSITIONS)
SIGNS = (-1, 1)
CALIBRATION_RECORD_IDS = (1, 2, 5, 12, 100, 251, 501, 1000, 1500, 2001)
DEGENERACY_LABELS = ("ZERO", "SELECTED_DUPLICATE", "COMPLEMENT_DUPLICATE", "DISTINCT_NONZERO")
LEDGER_HEADER = (
    "ordinal\trecord_id\ti\tj\tk\tposition_mask\tsign\t"
    "r_num\tr_den\ts_num\ts_den\tt_num\tt_den\td_num\td_den\t"
    "degeneracy\tcomp0\tcomp1\tcomp2\tsurvivor"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def compact_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def pretty_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def atomic_write(path: Path, payload: bytes, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"temporary output already exists: {temporary}")
    temporary.write_bytes(payload)
    temporary.replace(path)


@total_ordering
@dataclass(frozen=True)
class Rat:
    n: int
    d: int = 1

    def __post_init__(self) -> None:
        if self.d == 0:
            raise ZeroDivisionError("zero denominator")
        n, d = self.n, self.d
        if d < 0:
            n, d = -n, -d
        divisor = math.gcd(abs(n), d)
        object.__setattr__(self, "n", n // divisor)
        object.__setattr__(self, "d", d // divisor)

    @classmethod
    def parse(cls, token: str) -> "Rat":
        match = RAT_RE.fullmatch(token.strip())
        if match is None:
            raise ValueError(f"invalid rational token {token!r}")
        return cls(int(match.group(1)), int(match.group(2) or 1))

    def __add__(self, other: object) -> "Rat":
        right = as_rat(other)
        return Rat(self.n * right.d + right.n * self.d, self.d * right.d)

    def __radd__(self, other: object) -> "Rat":
        return self + other

    def __neg__(self) -> "Rat":
        return Rat(-self.n, self.d)

    def __sub__(self, other: object) -> "Rat":
        return self + (-as_rat(other))

    def __rsub__(self, other: object) -> "Rat":
        return as_rat(other) - self

    def __mul__(self, other: object) -> "Rat":
        right = as_rat(other)
        return Rat(self.n * right.n, self.d * right.d)

    def __rmul__(self, other: object) -> "Rat":
        return self * other

    def __truediv__(self, other: object) -> "Rat":
        right = as_rat(other)
        if right.n == 0:
            raise ZeroDivisionError("division by zero")
        return Rat(self.n * right.d, self.d * right.n)

    def __pow__(self, exponent: int) -> "Rat":
        if exponent < 0:
            return Rat(self.d, self.n) ** (-exponent)
        return Rat(pow(self.n, exponent), pow(self.d, exponent))

    def __lt__(self, other: object) -> bool:
        right = as_rat(other)
        return self.n * right.d < right.n * self.d

    def text(self) -> str:
        return str(self.n) if self.d == 1 else f"{self.n}/{self.d}"


def as_rat(value: object) -> Rat:
    if isinstance(value, Rat):
        return value
    if isinstance(value, int):
        return Rat(value)
    raise TypeError(f"cannot coerce {type(value).__name__} to Rat")


def exact_sqrt(value: Rat) -> Rat | None:
    if value.n < 0:
        return None
    numerator = math.isqrt(value.n)
    denominator = math.isqrt(value.d)
    if numerator * numerator != value.n or denominator * denominator != value.d:
        return None
    return Rat(numerator, denominator)


@dataclass(frozen=True)
class Record:
    record_id: int
    values: tuple[Rat, Rat, Rat, Rat, Rat, Rat]
    annotation: str


@dataclass(frozen=True)
class Context:
    record: Record
    triple_ordinal: int
    positions: tuple[int, int, int]
    complement_positions: tuple[int, int, int]
    roots: tuple[Rat, Rat, Rat]
    candidates: tuple[Rat, Rat]
    degeneracies: tuple[str, str]
    sign_collapsed: bool


def parse_catalogue(path: Path) -> tuple[list[Record], dict[str, int]]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    records: list[Record] = []
    malformed = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        match = RECORD_RE.fullmatch(line)
        if match is None:
            if RECORD_PREFIX_RE.match(line):
                malformed += 1
                raise ValueError(f"malformed record-like line {line_number}")
            continue
        values = tuple(Rat.parse(part) for part in match.group(2).split(","))
        if len(values) != 6:
            raise ValueError(f"record {match.group(1)} does not contain six values")
        records.append(Record(int(match.group(1)), values, match.group(3)))  # type: ignore[arg-type]
    if [record.record_id for record in records] != list(range(1, 2002)):
        raise ValueError("record identifiers are not exactly contiguous 1..2001")
    return records, {
        "byte_count": len(raw),
        "line_count": len(text.splitlines()),
        "malformed_record_like_lines": malformed,
    }


def validate_source(records: Sequence[Record]) -> dict[str, int]:
    pair_checks = 0
    sextuple_keys: set[tuple[Rat, ...]] = set()
    for record in records:
        if any(value == Rat(0) for value in record.values):
            raise ArithmeticError(f"record {record.record_id} contains zero")
        if len(set(record.values)) != 6:
            raise ArithmeticError(f"record {record.record_id} contains a duplicate")
        sextuple_keys.add(tuple(sorted(record.values)))
        for left, right in itertools.combinations(record.values, 2):
            if exact_sqrt(left * right + 1) is None:
                raise ArithmeticError(f"record {record.record_id} has a nonsquare source pair")
            pair_checks += 1
    if pair_checks != 30015 or len(sextuple_keys) != 2001:
        raise ArithmeticError("source catalogue accounting mismatch")
    return {
        "record_count": len(records),
        "pair_check_count": pair_checks,
        "distinct_unordered_sextuple_sets": len(sextuple_keys),
    }


def classify(candidate: Rat, selected: Sequence[Rat], complements: Sequence[Rat]) -> str:
    if candidate == Rat(0):
        return "ZERO"
    if candidate in selected:
        return "SELECTED_DUPLICATE"
    if candidate in complements:
        return "COMPLEMENT_DUPLICATE"
    return "DISTINCT_NONZERO"


def make_context(record: Record, triple_ordinal: int) -> Context:
    positions = POSITIONS[triple_ordinal]
    complement_positions = tuple(position for position in range(6) if position not in positions)
    selected = tuple(record.values[position] for position in positions)
    complements = tuple(record.values[position] for position in complement_positions)
    a, b, c = selected
    r = exact_sqrt(a * b + 1)
    s = exact_sqrt(a * c + 1)
    t = exact_sqrt(b * c + 1)
    if r is None or s is None or t is None:
        raise ArithmeticError(f"record {record.record_id}, triple {triple_ordinal}: missing selected root")
    base = a + b + c + 2 * a * b * c
    delta = 2 * r * s * t
    candidates = (base - delta, base + delta)
    degeneracies: list[str] = []
    for sign_index, sign in enumerate(SIGNS):
        candidate = candidates[sign_index]
        identity_roots = (
            a * t + sign * r * s,
            b * s + sign * r * t,
            c * r + sign * s * t,
        )
        if (a * candidate + 1, b * candidate + 1, c * candidate + 1) != tuple(
            root * root for root in identity_roots
        ):
            raise ArithmeticError(f"record {record.record_id}, triple {triple_ordinal}: identity failure")
        degeneracies.append(classify(candidate, selected, complements))

    for er, es, et in itertools.product(SIGNS, repeat=3):
        parity = er * es * et
        signed_delta = 2 * (er * r) * (es * s) * (et * t)
        for sign in SIGNS:
            if base + sign * signed_delta != candidates[SIGNS.index(sign * parity)]:
                raise ArithmeticError(f"record {record.record_id}, triple {triple_ordinal}: sign invariance failure")

    return Context(
        record,
        triple_ordinal,
        positions,
        complement_positions,  # type: ignore[arg-type]
        (r, s, t),
        candidates,
        (degeneracies[0], degeneracies[1]),
        candidates[0] == candidates[1],
    )


def ledger_row(context: Context, sign: int) -> tuple[bytes, str, int, Rat]:
    sign_index = SIGNS.index(sign)
    candidate = context.candidates[sign_index]
    complements = tuple(context.record.values[position] for position in context.complement_positions)
    bits = "".join("1" if exact_sqrt(candidate * value + 1) is not None else "0" for value in complements)
    survivor = int(context.degeneracies[sign_index] == "DISTINCT_NONZERO" and bits == "111")
    ordinal = (context.record.record_id - 1) * 40 + 2 * context.triple_ordinal + sign_index
    i, j, k = context.positions
    r, s, t = context.roots
    fields: tuple[object, ...] = (
        ordinal,
        context.record.record_id,
        i,
        j,
        k,
        MASKS[context.triple_ordinal],
        sign,
        r.n,
        r.d,
        s.n,
        s.d,
        t.n,
        t.d,
        candidate.n,
        candidate.d,
        context.degeneracies[sign_index],
        bits[0],
        bits[1],
        bits[2],
        survivor,
    )
    return ("\t".join(str(field) for field in fields) + "\n").encode("ascii"), bits, survivor, candidate


def survivor_object(context: Context, sign: int, candidate: Rat) -> dict[str, object]:
    sign_index = SIGNS.index(sign)
    return {
        "candidate": candidate.text(),
        "ordinal": (context.record.record_id - 1) * 40 + 2 * context.triple_ordinal + sign_index,
        "position_triple": list(context.positions),
        "record_id": context.record.record_id,
        "sign": sign,
        "source_values": [value.text() for value in context.record.values],
    }


def collect_pending(value: object, prefix: str = "") -> list[str]:
    pending: list[str] = []
    if value == "PENDING":
        pending.append(prefix)
    elif isinstance(value, dict):
        for key, child in value.items():
            pending.extend(collect_pending(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            pending.extend(collect_pending(child, f"{prefix}[{index}]"))
    return pending


def require(observed: object, expected: object, label: str) -> None:
    if observed != expected:
        raise ValueError(f"manifest {label} mismatch: observed {observed!r}, expected {expected!r}")


def get_path(manifest: dict[str, Any], dotted: str) -> Any:
    value: Any = manifest
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"manifest field missing: {dotted}")
        value = value[part]
    return value


def validate_manifest_values(manifest: dict[str, Any]) -> None:
    require(manifest.get("schema"), MANIFEST_SCHEMA, "schema")
    require(manifest.get("route"), ROUTE, "route")
    expected_scalars = {
        "source.path": SOURCE_REL,
        "source.sha256": SOURCE_SHA256,
        "source.byte_count": 255092,
        "source.record_regex": r"^\((\d+)\)\s+\[([^]]+)\]",
        "source.rational_regex": r"^([+-]?\d+)(?:/([+-]?\d+))?$",
        "source.record_count": 2001,
        "source.record_ids": "exactly contiguous 1..2001",
        "source.nonrecord_lines": "ignored",
        "source.record_like_malformed_lines": "fatal",
        "source.values_per_record": 6,
        "source.required_square_pairs_per_record": 15,
        "enumeration.position_base": 0,
        "enumeration.root_convention": "nonnegative reduced rational roots for ab+1, ac+1, bc+1",
        "enumeration.candidate_formula": "d=a+b+c+2*a*b*c+sign*2*r*s*t",
        "enumeration.record_order": "increasing record_id 1..2001",
        "enumeration.triple_order": "listed lexicographic order",
        "enumeration.sign_order": "-1 then +1",
        "enumeration.declared_contexts": 80040,
        "enumeration.declared_triple_contexts": 40020,
        "enumeration.distinct_unordered_triple_keys": 39490,
        "enumeration.duplicate_context_excess": 530,
        "enumeration.repeated_triple_keys": 400,
        "enumeration.contexts_on_repeated_keys": 930,
        "enumeration.expected_extension_identity_checks": 240120,
        "enumeration.expected_root_sign_assertions": 640320,
        "enumeration.expected_sign_collapses": 0,
        "runtime.primary": "CPython 3.12.4",
        "runtime.independent": "g++ 16.1.0 with boost::multiprecision::cpp_int",
        "runtime.aggregate_workers_max": 64,
        "calibration.declared_contexts": 400,
        "calibration.ordinal_rule": "(record_id-1)*40 + 2*triple_ordinal + sign_index, with sign_index 0 for -1 and 1 for +1",
        "calibration.ledger_hash_scope": "ASCII header plus 400 rows, LF after every line including the final row",
        "calibration.expected_ledger_byte_count": 35384,
        "calibration.expected_ledger_sha256": "BE43F7D69037C4D19B86760085EF33A124719A9B4E879E72681C5E18899EEFF1",
        "calibration.summary_schema": CALIBRATION_SUMMARY_SCHEMA,
        "calibration.summary_serialization": "compact ASCII JSON with sorted keys and one final LF",
        "calibration.expected_summary_sha256": "8E4E89F5E2C68B5FF2B8550C09BFA4E13B7932040A64A756B7125A41F830A15E",
        "calibration.expected_survivor_count": 0,
        "ledger.encoding": "ASCII TSV with LF",
        "ledger.header": LEDGER_HEADER,
        "ledger.rational_normalization": "gcd-reduced numerator and positive denominator",
        "ledger.complement_bits": "three exact 0/1 square-test results in increasing complementary-position order",
        "ledger.survivor_rule": "1 exactly when degeneracy is DISTINCT_NONZERO and comp0=comp1=comp2=1",
        "ledger.retain_every_context": True,
        "ledger.full_ledger_filename": "ledger.tsv",
        "ledger.full_summary_filename": "summary.json",
        "ledger.full_survivors_filename": "survivors.json",
    }
    for dotted, expected in expected_scalars.items():
        require(get_path(manifest, dotted), expected, dotted)
    require(get_path(manifest, "enumeration.signs"), list(SIGNS), "enumeration.signs")
    expected_triples = [
        {"positions": list(positions), "mask": mask}
        for positions, mask in zip(POSITIONS, MASKS, strict=True)
    ]
    require(get_path(manifest, "enumeration.position_triples"), expected_triples, "enumeration.position_triples")
    require(
        get_path(manifest, "enumeration.expected_degeneracy_counts"),
        {"ZERO": 291, "SELECTED_DUPLICATE": 102, "COMPLEMENT_DUPLICATE": 8416, "DISTINCT_NONZERO": 71231},
        "enumeration.expected_degeneracy_counts",
    )
    require(get_path(manifest, "calibration.record_ids"), list(CALIBRATION_RECORD_IDS), "calibration.record_ids")
    require(
        get_path(manifest, "calibration.expected_degeneracy_counts"),
        {"ZERO": 4, "SELECTED_DUPLICATE": 1, "COMPLEMENT_DUPLICATE": 52, "DISTINCT_NONZERO": 343},
        "calibration.expected_degeneracy_counts",
    )
    require(
        get_path(manifest, "calibration.expected_complement_pattern_counts"),
        {"000": 342, "001": 0, "010": 0, "011": 28, "100": 1, "101": 17, "110": 7, "111": 5},
        "calibration.expected_complement_pattern_counts",
    )
    require(get_path(manifest, "ledger.ordinal_range"), [0, 80039], "ledger.ordinal_range")
    require(get_path(manifest, "ledger.degeneracy_labels"), list(DEGENERACY_LABELS), "ledger.degeneracy_labels")
    require(get_path(manifest, "ledger.degeneracy_precedence"), list(DEGENERACY_LABELS), "ledger.degeneracy_precedence")
    expected_paths = {
        "engines.primary.path": PRIMARY_ENGINE_REL,
        "engines.independent_source.path": INDEPENDENT_SOURCE_REL,
        "engines.independent_binary.path": INDEPENDENT_BINARY_REL,
        "engines.referee.path": REFEREE_REL,
        "verifiers.primary.path": PRIMARY_VERIFIER_REL,
        "verifiers.independent.path": INDEPENDENT_VERIFIER_REL,
    }
    for dotted, expected in expected_paths.items():
        require(get_path(manifest, dotted), expected, dotted)
    require(get_path(manifest, "verifiers.primary.sha256"), PRIMARY_VERIFIER_SHA256, "verifiers.primary.sha256")
    require(
        get_path(manifest, "verifiers.independent.sha256"),
        INDEPENDENT_VERIFIER_SHA256,
        "verifiers.independent.sha256",
    )


def load_manifest(path: Path, expected_sha256: str) -> tuple[dict[str, Any], str]:
    observed = sha256_file(path)
    if observed != expected_sha256.upper():
        raise ValueError(f"manifest SHA-256 mismatch: observed {observed}, expected {expected_sha256.upper()}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest root is not an object")
    validate_manifest_values(manifest)
    return manifest, observed


def artifact_observations(workspace: Path, manifest: dict[str, Any]) -> dict[str, object]:
    observations: dict[str, object] = {}
    fields = {
        "source": "source",
        "primary_engine": "engines.primary",
        "independent_source": "engines.independent_source",
        "independent_binary": "engines.independent_binary",
        "referee": "engines.referee",
        "primary_verifier": "verifiers.primary",
        "independent_verifier": "verifiers.independent",
    }
    for name, dotted in fields.items():
        contract = get_path(manifest, dotted)
        path = workspace / contract["path"]
        observations[name] = {
            "path": contract["path"],
            "exists": path.is_file(),
            "observed_sha256": sha256_file(path) if path.is_file() else None,
            "byte_count": path.stat().st_size if path.is_file() else None,
        }
    return observations


def validate_terminal_artifacts(workspace: Path, manifest: dict[str, Any]) -> None:
    contracts = (
        "source",
        "engines.primary",
        "engines.independent_source",
        "engines.independent_binary",
        "engines.referee",
        "verifiers.primary",
        "verifiers.independent",
    )
    for dotted in contracts:
        contract = get_path(manifest, dotted)
        declared = contract["sha256"]
        if not isinstance(declared, str) or re.fullmatch(r"[0-9A-F]{64}", declared) is None:
            raise ValueError(f"terminal artifact hash is not frozen: {dotted}")
        path = workspace / contract["path"]
        if not path.is_file() or sha256_file(path) != declared:
            raise ValueError(f"terminal artifact hash mismatch: {dotted}")
    report_contract = get_path(manifest, "engines.referee")
    report_path = workspace / report_contract["report_path"]
    report_sha = report_contract["report_sha256"]
    if not report_path.is_file() or sha256_file(report_path) != report_sha:
        raise ValueError("frozen plan referee report hash mismatch")


def validate_runtime_commands(manifest: dict[str, Any]) -> None:
    """Validate load-bearing fragments of the two frozen launch commands."""
    primary = get_path(manifest, "runtime.primary_command")
    independent = get_path(manifest, "runtime.independent_command")
    if not isinstance(primary, str) or not isinstance(independent, str):
        raise ValueError("runtime commands must be strings")
    primary_required = (
        PRIMARY_ENGINE_REL,
        get_path(manifest, "engines.referee.report_path").rsplit("/", 1)[0] + "/manifest.json",
        "{MANIFEST_SHA256}",
        "--mode full",
        get_path(manifest, "outputs.primary_dir"),
        "CANONICAL_SHIFT_FULL_80040_V1",
    )
    independent_required = (
        INDEPENDENT_BINARY_REL,
        get_path(manifest, "engines.referee.report_path").rsplit("/", 1)[0] + "/manifest.json",
        "{MANIFEST_SHA256}",
        "--mode full",
        get_path(manifest, "outputs.independent_dir") + "/ledger.tsv",
        get_path(manifest, "outputs.independent_dir") + "/summary.json",
        get_path(manifest, "outputs.independent_dir") + "/survivors.json",
        "CANONICAL_SHIFT_ALL_80040_FROZEN",
    )
    for fragment in primary_required:
        if fragment not in primary:
            raise ValueError(f"primary runtime command is missing frozen fragment: {fragment}")
    for fragment in independent_required:
        if fragment not in independent:
            raise ValueError(f"independent runtime command is missing frozen fragment: {fragment}")
    if "--workspace-root ." not in independent and "--workspace-root E:/Projects/ErdosProblems" not in independent:
        raise ValueError("independent runtime command must use '.' or a forward-slash absolute workspace root")


def multiplicity_report(counter: Counter[tuple[Rat, ...]]) -> dict[str, object]:
    histogram = Counter(counter.values())
    repeated = [multiplicity for multiplicity in counter.values() if multiplicity > 1]
    return {
        "distinct_unordered_triple_keys": len(counter),
        "duplicate_context_excess": sum(counter.values()) - len(counter),
        "repeated_triple_keys": len(repeated),
        "contexts_on_repeated_keys": sum(repeated),
        "multiplicity_histogram": {str(key): value for key, value in sorted(histogram.items())},
    }


def calibration_summary(
    ledger_bytes: bytes,
    degeneracies: Counter[str],
    patterns: Counter[str],
    survivors: int,
) -> dict[str, object]:
    return {
        "schema": CALIBRATION_SUMMARY_SCHEMA,
        "source_sha256": SOURCE_SHA256,
        "record_ids": list(CALIBRATION_RECORD_IDS),
        "record_count": len(CALIBRATION_RECORD_IDS),
        "context_count": 400,
        "source_pair_checks": 150,
        "extension_identity_checks": 1200,
        "ledger_byte_count": len(ledger_bytes),
        "ledger_sha256": sha256_bytes(ledger_bytes),
        "degeneracy_counts": {label: degeneracies.get(label, 0) for label in DEGENERACY_LABELS},
        "complement_pattern_counts": {f"{value:03b}": patterns.get(f"{value:03b}", 0) for value in range(8)},
        "survivor_count": survivors,
    }


def compare_optional_ledger(path: Path | None, oracle: bytes) -> dict[str, object] | None:
    if path is None:
        return None
    observed = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "byte_count": len(observed),
        "sha256": sha256_bytes(observed),
        "byte_identical_to_oracle": observed == oracle,
    }


def prior_work_report(workspace: Path) -> dict[str, object]:
    paths = {
        "catalog_scan_engine": "problems_external/rational_diophantine_septuple/engine/catalog_scan.py",
        "catalog_scan_manifest": "problems_external/rational_diophantine_septuple/runs/catalog_scan_20260720T0643/manifest.json",
        "catalog_scan_summary": "problems_external/rational_diophantine_septuple/runs/catalog_scan_20260720T0643/summary.json",
        "multiseed_manifest": "problems_external/rational_diophantine_septuple/runs/catalog_multiseed_box1_20260720T0655/manifest.json",
        "multiseed_summary": "problems_external/rational_diophantine_septuple/runs/catalog_multiseed_box1_20260720T0655/summary.json",
        "z6x2_manifest": "problems_external/rational_diophantine_septuple/runs/z6x2_max_region_20260720T142412/manifest.json",
        "z6x2_summary": "problems_external/rational_diophantine_septuple/runs/z6x2_max_region_20260720T142412/primary_full/summary.json",
    }
    evidence = {
        name: {"path": relative, "sha256": sha256_file(workspace / relative)}
        for name, relative in paths.items()
    }
    catalog_manifest = json.loads((workspace / paths["catalog_scan_manifest"]).read_text(encoding="utf-8"))
    catalog_summary = json.loads((workspace / paths["catalog_scan_summary"]).read_text(encoding="utf-8"))
    multiseed_summary = json.loads((workspace / paths["multiseed_summary"]).read_text(encoding="utf-8"))
    if catalog_manifest["algorithm"]["vertices"] != "all remaining elements from every catalog sextuple containing the triple":
        raise ValueError("prior catalogue scan scope changed")
    if catalog_summary["induced_triples"] != 39490 or multiseed_summary["processed_seed_count"] != 341:
        raise ValueError("prior coverage count changed")
    return {
        "conclusion": "No preserved prior manifest exhausts the 80040 signed canonical-shift contexts.",
        "catalog_scan_scope": "39490 keys with catalogue-listed remaining values only",
        "multiseed_scope": "341 selected non-Z6x2 shared keys in declared coefficient boxes",
        "z6x2_scope": "one fixed key in its 531441-expression region",
        "uncovered_key_lower_bound_after_multiseed_plus_z6x2": 39148,
        "evidence": evidence,
    }


def plan_audit(
    workspace: Path,
    manifest: dict[str, Any],
    records: Sequence[Record],
    source_shape: dict[str, int],
    primary_calibration: Path | None,
    independent_calibration: Path | None,
) -> dict[str, object]:
    source_validation = validate_source(records)
    triple_multiplicities: Counter[tuple[Rat, ...]] = Counter()
    degeneracies: Counter[str] = Counter()
    sign_collapses = 0
    calibration_lines = [LEDGER_HEADER]
    calibration_degeneracies: Counter[str] = Counter()
    calibration_patterns: Counter[str] = Counter()
    calibration_survivors = 0
    calibration_ids = set(CALIBRATION_RECORD_IDS)

    for record in records:
        for triple_ordinal in range(20):
            context = make_context(record, triple_ordinal)
            triple_multiplicities[tuple(sorted(record.values[position] for position in context.positions))] += 1
            sign_collapses += int(context.sign_collapsed)
            for sign_index, sign in enumerate(SIGNS):
                degeneracies[context.degeneracies[sign_index]] += 1
                if record.record_id in calibration_ids:
                    row, bits, survivor, _ = ledger_row(context, sign)
                    calibration_lines.append(row.decode("ascii").rstrip("\n"))
                    calibration_degeneracies[context.degeneracies[sign_index]] += 1
                    calibration_patterns[bits] += 1
                    calibration_survivors += survivor

    calibration_ledger = ("\n".join(calibration_lines) + "\n").encode("ascii")
    neutral_summary = calibration_summary(
        calibration_ledger,
        calibration_degeneracies,
        calibration_patterns,
        calibration_survivors,
    )
    neutral_summary_bytes = compact_json_bytes(neutral_summary)
    if sha256_bytes(calibration_ledger) != get_path(manifest, "calibration.expected_ledger_sha256"):
        raise ArithmeticError("calibration ledger hash disagrees with manifest")
    if len(calibration_ledger) != get_path(manifest, "calibration.expected_ledger_byte_count"):
        raise ArithmeticError("calibration ledger byte count disagrees with manifest")
    if sha256_bytes(neutral_summary_bytes) != get_path(manifest, "calibration.expected_summary_sha256"):
        raise ArithmeticError("calibration neutral summary hash disagrees with manifest")
    if neutral_summary["degeneracy_counts"] != get_path(manifest, "calibration.expected_degeneracy_counts"):
        raise ArithmeticError("calibration degeneracy counts disagree with manifest")
    if neutral_summary["complement_pattern_counts"] != get_path(
        manifest, "calibration.expected_complement_pattern_counts"
    ):
        raise ArithmeticError("calibration pattern counts disagree with manifest")
    full_counts = {label: degeneracies.get(label, 0) for label in DEGENERACY_LABELS}
    if full_counts != get_path(manifest, "enumeration.expected_degeneracy_counts"):
        raise ArithmeticError("full formula degeneracy counts disagree with manifest")
    multiplicities = multiplicity_report(triple_multiplicities)
    for key in ("distinct_unordered_triple_keys", "duplicate_context_excess", "repeated_triple_keys", "contexts_on_repeated_keys"):
        if multiplicities[key] != get_path(manifest, f"enumeration.{key}"):
            raise ArithmeticError(f"triple multiplicity field disagrees with manifest: {key}")
    if sign_collapses != get_path(manifest, "enumeration.expected_sign_collapses"):
        raise ArithmeticError("sign-collapse count disagrees with manifest")

    comparisons = {
        "primary": compare_optional_ledger(primary_calibration, calibration_ledger),
        "independent": compare_optional_ledger(independent_calibration, calibration_ledger),
    }
    for name, comparison in comparisons.items():
        if comparison is not None and not comparison["byte_identical_to_oracle"]:
            raise ArithmeticError(f"{name} calibration ledger differs from referee oracle")

    return {
        "schema": PLAN_SCHEMA,
        "status": "PASS",
        "scope": "plan audit; no full 80040-row complement search",
        "source": {"sha256": SOURCE_SHA256, **source_shape, **source_validation},
        "formula_audit": {
            "triple_context_count": 40020,
            "signed_context_count": 80040,
            "extension_identity_checks": 240120,
            "root_sign_assertions": 640320,
            "sign_collapses": sign_collapses,
            "degeneracy_counts": full_counts,
            **multiplicities,
        },
        "calibration": {
            "record_ids": list(CALIBRATION_RECORD_IDS),
            "context_count": 400,
            "complement_tests": 1200,
            "ledger_sha256": sha256_bytes(calibration_ledger),
            "ledger_byte_count": len(calibration_ledger),
            "neutral_summary": neutral_summary,
            "neutral_summary_sha256": sha256_bytes(neutral_summary_bytes),
            "engine_comparisons": comparisons,
        },
        "artifact_observations": artifact_observations(workspace, manifest),
        "pending_manifest_fields_at_plan": collect_pending(manifest),
        "prior_work_noncoverage": prior_work_report(workspace),
        "terminal_contract": {
            "authorization_token": TERMINAL_TOKEN,
            "recompute_rows": 80040,
            "compare_primary_and_independent_ledgers": True,
            "derive_and_compare_both_survivor_files": True,
            "dual_verify_every_referee_survivor": True,
            "no_hit_interpretation": "NO_HIT only for the frozen 80040 canonical-shift contexts",
        },
    }


def expected_engine_paths(
    workspace: Path, manifest: dict[str, Any]
) -> tuple[Path, Path, Path, Path, Path, Path]:
    primary_dir = workspace / get_path(manifest, "outputs.primary_dir")
    independent_dir = workspace / get_path(manifest, "outputs.independent_dir")
    ledger_name = get_path(manifest, "ledger.full_ledger_filename")
    summary_name = get_path(manifest, "ledger.full_summary_filename")
    survivors_name = get_path(manifest, "ledger.full_survivors_filename")
    return (
        primary_dir / ledger_name,
        independent_dir / ledger_name,
        primary_dir / summary_name,
        independent_dir / summary_name,
        primary_dir / survivors_name,
        independent_dir / survivors_name,
    )


def validate_full_summaries(
    primary_path: Path,
    independent_path: Path,
    *,
    manifest_sha256: str,
    ledger_sha256: str,
    ledger_byte_count: int,
    degeneracy_counts: dict[str, int],
    complement_pattern_counts: dict[str, int],
    survivor_count: int,
    survivors_sha256: str,
) -> dict[str, object]:
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    independent = json.loads(independent_path.read_text(encoding="utf-8"))
    if primary.get("schema") != "rational_diophantine_septuple/canonical_shift_primary_result/v1":
        raise ArithmeticError("primary full summary schema mismatch")
    if independent.get("schema") != "canonical_shift_independent_summary/v1":
        raise ArithmeticError("independent full summary schema mismatch")
    primary_expected = {
        "mode": "full",
        "context_count": 80040,
        "expected_context_count": 80040,
        "status_counts": degeneracy_counts,
        "complement_pattern_counts": complement_pattern_counts,
        "extension_identity_check_count": 240120,
        "survivor_count": survivor_count,
        "manifest_sha256": manifest_sha256,
    }
    for key, expected in primary_expected.items():
        if primary.get(key) != expected:
            raise ArithmeticError(f"primary full summary field mismatch: {key}")
    expected_status = "HIT" if survivor_count else "NO_HIT"
    if primary.get("status") != expected_status:
        raise ArithmeticError("primary full summary status mismatch")
    primary_catalogue = primary.get("catalogue_validation")
    if not isinstance(primary_catalogue, dict) or primary_catalogue.get("pair_check_count") != 30015:
        raise ArithmeticError("primary full summary source-pair count mismatch")
    primary_ledger = primary.get("ledger")
    if not isinstance(primary_ledger, dict) or {
        "sha256": primary_ledger.get("sha256"),
        "byte_count": primary_ledger.get("byte_count"),
        "data_row_count": primary_ledger.get("data_row_count"),
    } != {
        "sha256": ledger_sha256,
        "byte_count": ledger_byte_count,
        "data_row_count": 80040,
    }:
        raise ArithmeticError("primary full summary ledger facts mismatch")
    primary_survivors = primary.get("survivors")
    if not isinstance(primary_survivors, dict) or {
        "sha256": primary_survivors.get("sha256"),
        "record_count": primary_survivors.get("record_count"),
    } != {"sha256": survivors_sha256, "record_count": survivor_count}:
        raise ArithmeticError("primary full summary survivor facts mismatch")

    independent_expected = {
        "context_count": 80040,
        "degeneracy_counts": degeneracy_counts,
        "complement_pattern_counts": complement_pattern_counts,
        "extension_identity_checks": 240120,
        "ledger_byte_count": ledger_byte_count,
        "ledger_sha256": ledger_sha256,
        "record_count": 2001,
        "record_ids": list(range(1, 2002)),
        "source_pair_checks": 30015,
        "source_sha256": SOURCE_SHA256,
        "survivor_count": survivor_count,
    }
    for key, expected in independent_expected.items():
        if independent.get(key) != expected:
            raise ArithmeticError(f"independent full summary field mismatch: {key}")
    return {
        "primary": {
            "path": str(primary_path.resolve()),
            "sha256": sha256_file(primary_path),
            "schema": primary["schema"],
        },
        "independent": {
            "path": str(independent_path.resolve()),
            "sha256": sha256_file(independent_path),
            "schema": independent["schema"],
        },
        "common_facts_match_referee": True,
    }


def verify_candidate(workspace: Path, values: list[str]) -> dict[str, object]:
    payload = json.dumps(values, separators=(",", ":"))
    commands = {
        "primary": [
            sys.executable,
            str(workspace / PRIMARY_VERIFIER_REL),
            "--json",
            payload,
            "--format",
            "json",
            "--expect-size",
            "7",
        ],
        "independent": [
            sys.executable,
            str(workspace / INDEPENDENT_VERIFIER_REL),
            "--json",
            payload,
            "--format",
            "json",
        ],
    }
    reports: dict[str, object] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise ArithmeticError(f"{name} verifier rejected referee survivor: {completed.stderr.strip()}")
        parsed = json.loads(completed.stdout)
        if not parsed.get("valid") or parsed.get("pair_count") != 21:
            raise ArithmeticError(f"{name} verifier returned an invalid survivor report")
        reports[name] = {
            "returncode": completed.returncode,
            "stdout_sha256": sha256_bytes(completed.stdout.encode("utf-8")),
            "valid": parsed["valid"],
            "pair_count": parsed["pair_count"],
        }
    return reports


def terminal_replay(
    workspace: Path,
    manifest: dict[str, Any],
    records: Sequence[Record],
    manifest_sha256: str,
) -> dict[str, object]:
    source_validation = validate_source(records)
    (
        primary_ledger_path,
        independent_ledger_path,
        primary_summary_path,
        independent_summary_path,
        primary_survivors_path,
        independent_survivors_path,
    ) = expected_engine_paths(workspace, manifest)
    for path in (
        primary_ledger_path,
        independent_ledger_path,
        primary_summary_path,
        independent_summary_path,
        primary_survivors_path,
        independent_survivors_path,
    ):
        if not path.is_file():
            raise FileNotFoundError(f"required terminal artifact is missing: {path}")

    expected_hash = hashlib.sha256()
    primary_hash = hashlib.sha256()
    independent_hash = hashlib.sha256()
    expected_bytes = 0
    row_count = 0
    degeneracies: Counter[str] = Counter()
    patterns: Counter[str] = Counter()
    triple_multiplicities: Counter[tuple[Rat, ...]] = Counter()
    sign_collapses = 0
    derived_survivors: list[dict[str, object]] = []
    header = (LEDGER_HEADER + "\n").encode("ascii")

    with primary_ledger_path.open("rb") as primary, independent_ledger_path.open("rb") as independent:
        primary_header = primary.readline()
        independent_header = independent.readline()
        if primary_header != header or independent_header != header:
            raise ArithmeticError("terminal ledger header mismatch")
        expected_hash.update(header)
        primary_hash.update(primary_header)
        independent_hash.update(independent_header)
        expected_bytes += len(header)

        for record in records:
            for triple_ordinal in range(20):
                context = make_context(record, triple_ordinal)
                triple_multiplicities[tuple(sorted(record.values[position] for position in context.positions))] += 1
                sign_collapses += int(context.sign_collapsed)
                for sign_index, sign in enumerate(SIGNS):
                    expected, bits, survivor, candidate = ledger_row(context, sign)
                    primary_line = primary.readline()
                    independent_line = independent.readline()
                    if primary_line != expected:
                        ordinal = (record.record_id - 1) * 40 + 2 * triple_ordinal + sign_index
                        raise ArithmeticError(f"primary ledger mismatch at ordinal {ordinal}")
                    if independent_line != expected:
                        ordinal = (record.record_id - 1) * 40 + 2 * triple_ordinal + sign_index
                        raise ArithmeticError(f"independent ledger mismatch at ordinal {ordinal}")
                    expected_hash.update(expected)
                    primary_hash.update(primary_line)
                    independent_hash.update(independent_line)
                    expected_bytes += len(expected)
                    row_count += 1
                    degeneracies[context.degeneracies[sign_index]] += 1
                    patterns[bits] += 1
                    if survivor:
                        derived_survivors.append(survivor_object(context, sign, candidate))
        if primary.read(1) or independent.read(1):
            raise ArithmeticError("terminal ledger has trailing rows or bytes")

    if row_count != 80040:
        raise ArithmeticError(f"terminal row count is {row_count}, expected 80040")
    expected_sha = expected_hash.hexdigest().upper()
    primary_sha = primary_hash.hexdigest().upper()
    independent_sha = independent_hash.hexdigest().upper()
    if expected_sha != primary_sha or expected_sha != independent_sha:
        raise ArithmeticError("terminal ledger digest disagreement")
    full_counts = {label: degeneracies.get(label, 0) for label in DEGENERACY_LABELS}
    if full_counts != get_path(manifest, "enumeration.expected_degeneracy_counts"):
        raise ArithmeticError("terminal degeneracy counts disagree with manifest")
    multiplicities = multiplicity_report(triple_multiplicities)
    for key in ("distinct_unordered_triple_keys", "duplicate_context_excess", "repeated_triple_keys", "contexts_on_repeated_keys"):
        if multiplicities[key] != get_path(manifest, f"enumeration.{key}"):
            raise ArithmeticError(f"terminal multiplicity mismatch: {key}")
    if sign_collapses != get_path(manifest, "enumeration.expected_sign_collapses"):
        raise ArithmeticError("terminal sign-collapse count mismatch")

    survivor_payload = {
        "schema": SURVIVORS_SCHEMA,
        "survivor_count": len(derived_survivors),
        "survivors": derived_survivors,
    }
    survivor_bytes = compact_json_bytes(survivor_payload)
    primary_survivor_bytes = primary_survivors_path.read_bytes()
    independent_survivor_bytes = independent_survivors_path.read_bytes()
    if primary_survivor_bytes != survivor_bytes:
        raise ArithmeticError("primary survivors.json differs from referee derivation")
    if independent_survivor_bytes != survivor_bytes:
        raise ArithmeticError("independent survivors.json differs from referee derivation")

    pattern_counts = {f"{value:03b}": patterns.get(f"{value:03b}", 0) for value in range(8)}
    summary_validation = validate_full_summaries(
        primary_summary_path,
        independent_summary_path,
        manifest_sha256=manifest_sha256,
        ledger_sha256=expected_sha,
        ledger_byte_count=expected_bytes,
        degeneracy_counts=full_counts,
        complement_pattern_counts=pattern_counts,
        survivor_count=len(derived_survivors),
        survivors_sha256=sha256_bytes(survivor_bytes),
    )

    verifier_reports: list[dict[str, object]] = []
    for survivor in derived_survivors:
        values = list(survivor["source_values"]) + [str(survivor["candidate"])]
        verifier_reports.append(
            {
                "ordinal": survivor["ordinal"],
                "values": values,
                "verifiers": verify_candidate(workspace, values),
            }
        )
    status = "VERIFIED_HIT" if derived_survivors else "VERIFIED_NO_HIT"
    return {
        "schema": TERMINAL_SCHEMA,
        "status": status,
        "scope": "the frozen 80040 terminal canonical-shift contexts",
        "interpretation": (
            "at least one candidate passed both full septuple verifiers"
            if derived_survivors
            else "NO_HIT only for this finite scope; not rational-septuple nonexistence"
        ),
        "source_validation": source_validation,
        "formula_audit": {
            "triple_context_count": 40020,
            "signed_context_count": row_count,
            "extension_identity_checks": 240120,
            "root_sign_assertions": 640320,
            "sign_collapses": sign_collapses,
            "degeneracy_counts": full_counts,
            "complement_pattern_counts": pattern_counts,
            **multiplicities,
        },
        "ledgers": {
            "byte_count": expected_bytes,
            "row_count": row_count,
            "referee_sha256": expected_sha,
            "primary": {"path": str(primary_ledger_path.resolve()), "sha256": primary_sha},
            "independent": {"path": str(independent_ledger_path.resolve()), "sha256": independent_sha},
            "all_bytes_match_referee": True,
        },
        "survivor_files": {
            "sha256": sha256_bytes(survivor_bytes),
            "byte_count": len(survivor_bytes),
            "survivor_count": len(derived_survivors),
            "primary": str(primary_survivors_path.resolve()),
            "independent": str(independent_survivors_path.resolve()),
            "all_bytes_match_referee": True,
        },
        "summaries": summary_validation,
        "survivors": verifier_reports,
        "standalone_verifier_invocation_count": 2 * len(verifier_reports),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("plan", "terminal"), required=True)
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--primary-calibration-ledger", type=Path)
    parser.add_argument("--independent-calibration-ledger", type=Path)
    parser.add_argument("--terminal-token")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        workspace = args.workspace_root.resolve()
        manifest_path = args.manifest.resolve()
        output = args.output.resolve()
        manifest, manifest_sha = load_manifest(manifest_path, args.expected_manifest_sha256)
        source_path = workspace / SOURCE_REL
        if sha256_file(source_path) != SOURCE_SHA256:
            raise ValueError("source SHA-256 mismatch")
        records, source_shape = parse_catalogue(source_path)
        if args.mode == "plan":
            if args.terminal_token is not None:
                raise ValueError("plan mode does not accept a terminal token")
            report = plan_audit(
                workspace,
                manifest,
                records,
                source_shape,
                args.primary_calibration_ledger.resolve() if args.primary_calibration_ledger else None,
                args.independent_calibration_ledger.resolve() if args.independent_calibration_ledger else None,
            )
            expected_report = workspace / get_path(manifest, "engines.referee.report_path")
            if output != expected_report.resolve():
                raise ValueError(f"plan output must equal manifest referee report path {expected_report}")
        else:
            if args.terminal_token != TERMINAL_TOKEN:
                raise ValueError("terminal mode requires the exact authorization token")
            if collect_pending(manifest):
                raise ValueError("terminal mode rejects every PENDING manifest field")
            validate_terminal_artifacts(workspace, manifest)
            validate_runtime_commands(manifest)
            expected_terminal = workspace / get_path(manifest, "outputs.terminal_referee_path")
            if output != expected_terminal.resolve():
                raise ValueError(f"terminal output must equal manifest terminal referee path {expected_terminal}")
            comparison_path = (workspace / get_path(manifest, "outputs.comparison_path")).resolve()
            if not args.overwrite:
                for guarded in (output, comparison_path):
                    if guarded.exists() or guarded.with_name(guarded.name + ".tmp").exists():
                        raise FileExistsError(f"refusing to overwrite terminal artifact {guarded}")
            report = terminal_replay(workspace, manifest, records, manifest_sha)
            report["manifest_sha256"] = manifest_sha
            comparison = {
                "schema": "canonical_shift_comparison/v1",
                "status": report["status"],
                "scope": report["scope"],
                "manifest_sha256": manifest_sha,
                "row_count": report["ledgers"]["row_count"],
                "ledger_sha256": report["ledgers"]["referee_sha256"],
                "ledger_bytes_match_referee": report["ledgers"]["all_bytes_match_referee"],
                "survivor_count": report["survivor_files"]["survivor_count"],
                "survivors_sha256": report["survivor_files"]["sha256"],
                "survivor_files_match_referee": report["survivor_files"]["all_bytes_match_referee"],
                "standalone_verifier_invocation_count": report["standalone_verifier_invocation_count"],
            }
            comparison_payload = compact_json_bytes(comparison)
            atomic_write(comparison_path, comparison_payload, overwrite=args.overwrite)
            report["comparison"] = {
                "path": str(comparison_path),
                "sha256": sha256_bytes(comparison_payload),
            }
        payload = pretty_json_bytes(report)
        atomic_write(output, payload, overwrite=args.overwrite)
        result = {
            "mode": args.mode,
            "status": report["status"],
            "output": str(output),
            "output_sha256": sha256_bytes(payload),
        }
        if args.mode == "plan":
            result["pending_manifest_fields"] = report["pending_manifest_fields_at_plan"]
            result["calibration_ledger_sha256"] = report["calibration"]["ledger_sha256"]
            result["calibration_summary_sha256"] = report["calibration"]["neutral_summary_sha256"]
        else:
            result["ledger_sha256"] = report["ledgers"]["referee_sha256"]
            result["survivor_count"] = report["survivor_files"]["survivor_count"]
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ArithmeticError, FileExistsError, FileNotFoundError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
