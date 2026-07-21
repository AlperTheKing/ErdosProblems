"""PLAN-only referee for the terminal embedded-triple canonical shift.

This program is intentionally not the search engine.  It independently parses
the source catalogue with a normalized-integer rational type, validates every
source sextuple, audits every canonical-shift identity, and emits a strict run
contract plus deterministic calibration rows.  Complement compatibility is
evaluated only on the calibration rows; a full 80,040-row complement search is
outside this referee's scope.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Iterable


RECORD_RE = re.compile(r"^\((\d+)\)\s+\[([^\]]+)\]\s*(.*)$")
RECORD_START_RE = re.compile(r"^\(\d+\)")
RAT_RE = re.compile(r"^([+-]?\d+)(?:/([+-]?\d+))?$")
POSITIONS = tuple(itertools.combinations(range(6), 3))
SIGNS = (-1, 1)
CALIBRATION_RECORD_IDS = (1, 2, 5, 12, 100, 251, 501, 1000, 1500, 2001)
LEDGER_HEADER = (
    "ordinal\trecord_id\ti\tj\tk\tposition_mask\tsign\t"
    "r_num\tr_den\ts_num\ts_den\tt_num\tt_den\td_num\td_den\t"
    "degeneracy\tcomp0\tcomp1\tcomp2\tsurvivor"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


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
        g = math.gcd(abs(n), d)
        object.__setattr__(self, "n", n // g)
        object.__setattr__(self, "d", d // g)

    @classmethod
    def parse(cls, text: str) -> "Rat":
        match = RAT_RE.fullmatch(text.strip())
        if match is None:
            raise ValueError(f"invalid rational token: {text!r}")
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

    def bit_size(self) -> int:
        return abs(self.n).bit_length() + self.d.bit_length()


def as_rat(value: object) -> Rat:
    if isinstance(value, Rat):
        return value
    if isinstance(value, int):
        return Rat(value)
    return NotImplemented  # type: ignore[return-value]


def exact_sqrt(value: Rat) -> Rat | None:
    if value.n < 0:
        return None
    rn = math.isqrt(value.n)
    rd = math.isqrt(value.d)
    if rn * rn != value.n or rd * rd != value.d:
        return None
    return Rat(rn, rd)


@dataclass(frozen=True)
class Record:
    index: int
    values: tuple[Rat, ...]
    annotation: str


@dataclass(frozen=True)
class ShiftContext:
    record: Record
    ordinal: int
    positions: tuple[int, int, int]
    complements: tuple[int, int, int]
    roots: tuple[Rat, Rat, Rat]
    candidates: tuple[Rat, Rat]
    identity_roots: tuple[tuple[Rat, Rat, Rat], tuple[Rat, Rat, Rat]]
    degeneracies: tuple[str, str]
    sign_collapsed: bool


def parse_catalog(path: Path) -> tuple[list[Record], dict[str, int]]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    records: list[Record] = []
    malformed_record_starts = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        match = RECORD_RE.fullmatch(line)
        if match is None:
            if RECORD_START_RE.match(line):
                malformed_record_starts += 1
                raise ValueError(f"malformed record-like line {line_number}: {line!r}")
            continue
        values = tuple(Rat.parse(token) for token in match.group(2).split(","))
        if len(values) != 6:
            raise ValueError(f"record {match.group(1)} has {len(values)} entries")
        records.append(Record(int(match.group(1)), values, match.group(3)))
    return records, {
        "byte_count": len(raw),
        "line_count": len(text.splitlines()),
        "malformed_record_starts": malformed_record_starts,
    }


def mask_for(positions: Iterable[int]) -> int:
    answer = 0
    for position in positions:
        answer |= 1 << position
    return answer


def classify_candidate(candidate: Rat, selected: tuple[Rat, Rat, Rat], complements: tuple[Rat, Rat, Rat]) -> str:
    if candidate == Rat(0):
        return "ZERO"
    if candidate in selected:
        return "DUPLICATE_SELECTED"
    if candidate in complements:
        return "DUPLICATE_COMPLEMENT"
    return "ELIGIBLE"


def audit_record(record: Record) -> int:
    values = record.values
    if record.index < 1:
        raise ValueError("record index is not positive")
    if any(value == Rat(0) for value in values):
        raise ValueError(f"record {record.index} contains zero")
    if len(set(values)) != 6:
        raise ValueError(f"record {record.index} is not distinct")
    checked = 0
    for left, right in itertools.combinations(values, 2):
        if exact_sqrt(left * right + 1) is None:
            raise ArithmeticError(f"record {record.index} fails pair {left.text()}, {right.text()}")
        checked += 1
    return checked


def make_context(record: Record, ordinal: int, positions: tuple[int, int, int]) -> ShiftContext:
    complement_positions = tuple(position for position in range(6) if position not in positions)
    selected = tuple(record.values[position] for position in positions)
    complements = tuple(record.values[position] for position in complement_positions)
    a, b, c = selected
    r = exact_sqrt(a * b + 1)
    s = exact_sqrt(a * c + 1)
    t = exact_sqrt(b * c + 1)
    if r is None or s is None or t is None:
        raise ArithmeticError(f"record {record.index}, ordinal {ordinal}: missing selected root")
    base = a + b + c + 2 * a * b * c
    delta = 2 * r * s * t
    candidates = (base - delta, base + delta)
    identity_roots: list[tuple[Rat, Rat, Rat]] = []
    degeneracies: list[str] = []
    for sign, candidate in zip(SIGNS, candidates, strict=True):
        roots = (
            a * t + sign * r * s,
            b * s + sign * r * t,
            c * r + sign * s * t,
        )
        left_sides = (a * candidate + 1, b * candidate + 1, c * candidate + 1)
        if left_sides != tuple(root * root for root in roots):
            raise ArithmeticError(f"record {record.index}, ordinal {ordinal}, sign {sign}: identity failure")
        identity_roots.append(roots)
        degeneracies.append(classify_candidate(candidate, selected, complements))

    # Changing root signs multiplies rst by the parity product.  Check every
    # sign choice rather than relying only on the symbolic observation.
    for er, es, et in itertools.product(SIGNS, repeat=3):
        parity = er * es * et
        signed_delta = 2 * (er * r) * (es * s) * (et * t)
        for sign in SIGNS:
            signed_candidate = base + sign * signed_delta
            expected = candidates[SIGNS.index(sign * parity)]
            if signed_candidate != expected:
                raise ArithmeticError(f"record {record.index}, ordinal {ordinal}: root-sign invariance failure")

    return ShiftContext(
        record=record,
        ordinal=ordinal,
        positions=positions,
        complements=complement_positions,
        roots=(r, s, t),
        candidates=candidates,
        identity_roots=(identity_roots[0], identity_roots[1]),
        degeneracies=(degeneracies[0], degeneracies[1]),
        sign_collapsed=candidates[0] == candidates[1],
    )


def context_key(context: ShiftContext) -> tuple[Rat, Rat, Rat]:
    return tuple(sorted(context.record.values[position] for position in context.positions))  # type: ignore[return-value]


def key_text(key: tuple[Rat, Rat, Rat]) -> str:
    return "|".join(value.text() for value in key)


def calibration_row(context: ShiftContext, sign: int) -> dict[str, object]:
    sign_index = SIGNS.index(sign)
    selected = tuple(context.record.values[position] for position in context.positions)
    complements = tuple(context.record.values[position] for position in context.complements)
    candidate = context.candidates[sign_index]
    complement_roots = tuple(exact_sqrt(value * candidate + 1) for value in complements)
    bits = "".join("1" if root is not None else "0" for root in complement_roots)
    row: dict[str, object] = {
        "record_id": context.record.index,
        "triple_ordinal": context.ordinal,
        "position_mask": mask_for(context.positions),
        "sign": sign,
        "selected_positions": list(context.positions),
        "complement_positions": list(context.complements),
        "selected_values": [value.text() for value in selected],
        "complement_values": [value.text() for value in complements],
        "selected_pair_roots": [value.text() for value in context.roots],
        "candidate": candidate.text(),
        "selected_extension_roots": [value.text() for value in context.identity_roots[sign_index]],
        "degeneracy": context.degeneracies[sign_index],
        "sign_collapsed": int(context.sign_collapsed),
        "complement_bits": bits,
        "complement_roots": [None if root is None else root.text() for root in complement_roots],
        "survivor": int(context.degeneracies[sign_index] == "ELIGIBLE" and bits == "111"),
    }
    row["row_sha256"] = sha256_bytes(canonical_json(row))
    return row


def manifest_degeneracy(label: str) -> str:
    return {
        "ZERO": "ZERO",
        "DUPLICATE_SELECTED": "SELECTED_DUPLICATE",
        "DUPLICATE_COMPLEMENT": "COMPLEMENT_DUPLICATE",
        "ELIGIBLE": "DISTINCT_NONZERO",
    }[label]


def manifest_ledger_row(context: ShiftContext, sign: int) -> tuple[str, str, int]:
    """Return the exact placeholder-manifest row, bit pattern, and survivor."""
    sign_index = SIGNS.index(sign)
    candidate = context.candidates[sign_index]
    complements = tuple(context.record.values[position] for position in context.complements)
    complement_roots = tuple(exact_sqrt(value * candidate + 1) for value in complements)
    bits = "".join("1" if root is not None else "0" for root in complement_roots)
    label = manifest_degeneracy(context.degeneracies[sign_index])
    survivor = int(label == "DISTINCT_NONZERO" and bits == "111")
    ordinal = (context.record.index - 1) * 40 + context.ordinal * 2 + sign_index
    i, j, k = context.positions
    r, s, t = context.roots
    fields: tuple[object, ...] = (
        ordinal,
        context.record.index,
        i,
        j,
        k,
        mask_for(context.positions),
        sign,
        r.n,
        r.d,
        s.n,
        s.d,
        t.n,
        t.d,
        candidate.n,
        candidate.d,
        label,
        bits[0],
        bits[1],
        bits[2],
        survivor,
    )
    return "\t".join(str(field) for field in fields), bits, survivor


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def prior_artifact(path: Path, root: Path) -> dict[str, object]:
    return {"path": relative(path, root), "sha256": sha256_file(path), "byte_count": path.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    catalog = args.catalog.resolve()
    records, source_shape = parse_catalog(catalog)
    if [record.index for record in records] != list(range(1, 2002)):
        raise ValueError("record identifiers are not exactly 1..2001")

    sextuple_pair_checks = sum(audit_record(record) for record in records)
    distinct_sextuple_keys = {tuple(sorted(record.values)) for record in records}
    if len(distinct_sextuple_keys) != len(records):
        raise ValueError("duplicate sextuple value set")
    contexts: list[ShiftContext] = []
    triple_contexts: dict[tuple[Rat, Rat, Rat], list[tuple[int, int]]] = defaultdict(list)
    degeneracy_counts: Counter[str] = Counter()
    sign_collapse_count = 0
    maximum_candidate: tuple[int, ShiftContext, int] | None = None
    first_by_degeneracy: dict[str, tuple[ShiftContext, int]] = {}

    for record in records:
        for ordinal, positions in enumerate(POSITIONS):
            context = make_context(record, ordinal, positions)
            contexts.append(context)
            triple_contexts[context_key(context)].append((record.index, ordinal))
            sign_collapse_count += int(context.sign_collapsed)
            for sign_index, (sign, candidate, category) in enumerate(zip(SIGNS, context.candidates, context.degeneracies, strict=True)):
                degeneracy_counts[category] += 1
                first_by_degeneracy.setdefault(category, (context, sign))
                score = candidate.bit_size()
                if maximum_candidate is None or (score, record.index, ordinal, sign_index) > (
                    maximum_candidate[0],
                    maximum_candidate[1].record.index,
                    maximum_candidate[1].ordinal,
                    SIGNS.index(maximum_candidate[2]),
                ):
                    maximum_candidate = (score, context, sign)

    multiplicity_histogram = Counter(len(refs) for refs in triple_contexts.values())
    repeated_keys = sorted((key for key, refs in triple_contexts.items() if len(refs) > 1), key=key_text)
    repeated_key = repeated_keys[0]
    repeated_refs = sorted(triple_contexts[repeated_key])[:2]
    context_lookup = {(context.record.index, context.ordinal): context for context in contexts}

    calibration_refs: list[tuple[ShiftContext, int]] = [
        (context_lookup[(1, 0)], -1),
        (context_lookup[(1, 0)], 1),
        (context_lookup[(2001, 19)], -1),
        (context_lookup[(2001, 19)], 1),
    ]
    for category in ("ZERO", "DUPLICATE_SELECTED", "DUPLICATE_COMPLEMENT", "ELIGIBLE"):
        if category in first_by_degeneracy:
            calibration_refs.append(first_by_degeneracy[category])
    for ref in repeated_refs:
        calibration_refs.extend((context_lookup[ref], sign) for sign in SIGNS)
    assert maximum_candidate is not None
    calibration_refs.append((maximum_candidate[1], maximum_candidate[2]))

    unique_calibration_refs: list[tuple[ShiftContext, int]] = []
    seen_refs: set[tuple[int, int, int]] = set()
    for context, sign in calibration_refs:
        ref = (context.record.index, context.ordinal, sign)
        if ref not in seen_refs:
            unique_calibration_refs.append((context, sign))
            seen_refs.add(ref)
    calibration_rows = [calibration_row(context, sign) for context, sign in unique_calibration_refs]
    calibration_stream = b"".join(canonical_json(row) for row in calibration_rows)

    manifest_ledger_lines = [LEDGER_HEADER]
    manifest_degeneracy_counts: Counter[str] = Counter()
    manifest_complement_patterns: Counter[str] = Counter()
    manifest_survivor_count = 0
    for record_id in CALIBRATION_RECORD_IDS:
        for ordinal in range(len(POSITIONS)):
            context = context_lookup[(record_id, ordinal)]
            for sign in SIGNS:
                line, bits, survivor = manifest_ledger_row(context, sign)
                manifest_ledger_lines.append(line)
                manifest_degeneracy_counts[manifest_degeneracy(context.degeneracies[SIGNS.index(sign)])] += 1
                manifest_complement_patterns[bits] += 1
                manifest_survivor_count += survivor
    manifest_ledger_bytes = ("\n".join(manifest_ledger_lines) + "\n").encode("ascii")
    manifest_calibration_summary = {
        "schema": "canonical_shift_calibration_summary/v1",
        "source_sha256": sha256_file(catalog),
        "record_ids": list(CALIBRATION_RECORD_IDS),
        "record_count": len(CALIBRATION_RECORD_IDS),
        "context_count": len(CALIBRATION_RECORD_IDS) * len(POSITIONS) * len(SIGNS),
        "source_pair_checks": len(CALIBRATION_RECORD_IDS) * 15,
        "extension_identity_checks": len(CALIBRATION_RECORD_IDS) * len(POSITIONS) * len(SIGNS) * 3,
        "ledger_byte_count": len(manifest_ledger_bytes),
        "ledger_sha256": sha256_bytes(manifest_ledger_bytes),
        "degeneracy_counts": {
            label: manifest_degeneracy_counts.get(label, 0)
            for label in ("ZERO", "SELECTED_DUPLICATE", "COMPLEMENT_DUPLICATE", "DISTINCT_NONZERO")
        },
        "complement_pattern_counts": {
            f"{bits:03b}": manifest_complement_patterns.get(f"{bits:03b}", 0) for bits in range(8)
        },
        "survivor_count": manifest_survivor_count,
    }
    manifest_calibration_summary_bytes = canonical_json(manifest_calibration_summary)

    base = workspace / "problems_external" / "rational_diophantine_septuple"
    prior_paths = {
        "catalog_scan_engine": base / "engine" / "catalog_scan.py",
        "catalog_scan_manifest": base / "runs" / "catalog_scan_20260720T0643" / "manifest.json",
        "catalog_scan_summary": base / "runs" / "catalog_scan_20260720T0643" / "summary.json",
        "multiseed_manifest": base / "runs" / "catalog_multiseed_box1_20260720T0655" / "manifest.json",
        "multiseed_summary": base / "runs" / "catalog_multiseed_box1_20260720T0655" / "summary.json",
        "multiseed_fullgraph_manifest": base / "runs" / "catalog_multiseed_fullgraph_box1_20260720T071327" / "manifest.json",
        "multiseed_fullgraph_summary": base / "runs" / "catalog_multiseed_fullgraph_box1_20260720T071327" / "summary.json",
        "z6x2_manifest": base / "runs" / "z6x2_max_region_20260720T142412" / "manifest.json",
        "z6x2_summary": base / "runs" / "z6x2_max_region_20260720T142412" / "primary_full" / "summary.json",
    }
    prior_evidence = {name: prior_artifact(path, workspace) for name, path in prior_paths.items()}

    catalog_scan_manifest = json.loads(prior_paths["catalog_scan_manifest"].read_text(encoding="utf-8"))
    catalog_scan_summary = json.loads(prior_paths["catalog_scan_summary"].read_text(encoding="utf-8"))
    multiseed_summary = json.loads(prior_paths["multiseed_summary"].read_text(encoding="utf-8"))
    multiseed_fullgraph_summary = json.loads(prior_paths["multiseed_fullgraph_summary"].read_text(encoding="utf-8"))
    if catalog_scan_manifest["algorithm"]["vertices"] != "all remaining elements from every catalog sextuple containing the triple":
        raise ValueError("catalog scan scope changed")
    if catalog_scan_summary["induced_triples"] != 39490:
        raise ValueError("catalog scan triple count changed")
    if multiseed_summary["processed_seed_count"] != 341 or multiseed_fullgraph_summary["processed_seed_count"] != 341:
        raise ValueError("multiseed scope changed")

    verifier_paths = {
        "primary": base / "engine" / "verify_tuple.py",
        "independent": base / "engine" / "verify_septuple_independent.py",
    }
    verifiers = {name: prior_artifact(path, workspace) for name, path in verifier_paths.items()}

    audit = {
        "status": "PASS",
        "mode": "PLAN_ONLY_NO_FULL_COMPLEMENT_SCAN",
        "referee_engine": {
            "path": relative(Path(__file__), workspace),
            "sha256": sha256_file(Path(__file__)),
        },
        "source": {
            "path": relative(catalog, workspace),
            "sha256": sha256_file(catalog),
            **source_shape,
        },
        "parser_contract": {
            "record_regex": RECORD_RE.pattern,
            "rational_regex": RAT_RE.pattern,
            "nonrecord_lines": "ignored",
            "record_like_malformed_lines": "fatal",
            "normalization": "gcd-reduced numerator/positive-denominator",
            "record_ids": "exactly contiguous 1..2001",
        },
        "catalogue_audit": {
            "record_count": len(records),
            "record_id_min": records[0].index,
            "record_id_max": records[-1].index,
            "sextuple_pair_checks": sextuple_pair_checks,
            "distinct_unordered_sextuple_sets": len(distinct_sextuple_keys),
            "all_records_nonzero_distinct": True,
            "all_pair_products_plus_one_square": True,
        },
        "position_contract": [
            {
                "ordinal": ordinal,
                "positions": list(positions),
                "letters": "".join("abcdef"[position] for position in positions),
                "mask": mask_for(positions),
            }
            for ordinal, positions in enumerate(POSITIONS)
        ],
        "sign_contract": {
            "ordered_signs": list(SIGNS),
            "pair_root_convention": "nonnegative exact rational square root",
            "invariance_rule": "root sign product +1 preserves d sign label; -1 exchanges d- and d+",
            "root_sign_assertions": len(contexts) * 8 * 2,
            "sign_collapsed_triple_contexts": sign_collapse_count,
        },
        "identity_audit": {
            "triple_context_count": len(contexts),
            "signed_context_count": len(contexts) * 2,
            "extension_identity_checks": len(contexts) * 2 * 3,
            "all_extension_identities_exact": True,
        },
        "triple_key_audit": {
            "distinct_unordered_keys": len(triple_contexts),
            "duplicate_excess": len(contexts) - len(triple_contexts),
            "keys_with_multiplicity_gt_1": len(repeated_keys),
            "contexts_on_repeated_keys": sum(len(triple_contexts[key]) for key in repeated_keys),
            "multiplicity_histogram": {str(k): v for k, v in sorted(multiplicity_histogram.items())},
            "calibration_repeated_key": key_text(repeated_key),
            "calibration_repeated_refs": [list(ref) for ref in repeated_refs],
        },
        "degeneracy_audit": {
            "precedence": ["ZERO", "DUPLICATE_SELECTED", "DUPLICATE_COMPLEMENT", "ELIGIBLE"],
            "row_counts": {key: degeneracy_counts.get(key, 0) for key in ("ZERO", "DUPLICATE_SELECTED", "DUPLICATE_COMPLEMENT", "ELIGIBLE")},
            "orthogonal_context_classes": {
                "RST_ZERO_SIGN_COLLAPSE": sign_collapse_count,
                "DISTINCT_SIGN_PAIR": len(contexts) - sign_collapse_count,
            },
        },
        "calibration": {
            "selection": "first/last, first observed row class, first lexicographic repeated key in two contexts, maximum candidate bit-size",
            "row_count": len(calibration_rows),
            "complement_pair_tests_only": len(calibration_rows) * 3,
            "bundle_sha256": sha256_bytes(calibration_stream),
            "rows": calibration_rows,
        },
        "placeholder_manifest_calibration": {
            "record_ids": list(CALIBRATION_RECORD_IDS),
            "context_count": len(CALIBRATION_RECORD_IDS) * len(POSITIONS) * len(SIGNS),
            "ordinal_rule": "(record_id-1)*40 + 2*triple_ordinal + sign_index, where sign_index is 0 for -1 and 1 for +1",
            "ledger_hash_scope": "ASCII header plus all 400 rows, LF after every line including the final row",
            "ledger_sha256": sha256_bytes(manifest_ledger_bytes),
            "ledger_byte_count": len(manifest_ledger_bytes),
            "summary_encoding": "canonical compact ASCII JSON with sorted keys and one final LF",
            "summary": manifest_calibration_summary,
            "summary_sha256": sha256_bytes(manifest_calibration_summary_bytes),
        },
        "prior_work_noncoverage": {
            "conclusion": "No preserved prior manifest exhausts the 80040 signed canonical-shift contexts.",
            "catalog_scan_scope": "39490 triple keys, catalogue-listed remaining values only; no canonical-shift generation",
            "multiseed_scope": "341 selected non-Z6x2 shared triples in declared coefficient boxes",
            "multiseed_fullgraph_scope": "compatibility graphs only inside the same 341 declared boxes",
            "z6x2_scope": "one fixed triple and its 531441-expression region",
            "uncovered_key_lower_bound_after_multiseed_plus_z6x2": len(triple_contexts) - 342,
            "evidence": prior_evidence,
        },
        "verifiers": verifiers,
    }

    contract = {
        "schema": "canonical-shift-run-manifest-v1",
        "manifest_required_fields": {
            "run_id": "nonempty ASCII string",
            "route": "terminal embedded-triple canonical shift",
            "source.path": audit["source"]["path"],
            "source.sha256": audit["source"]["sha256"],
            "source.byte_count": audit["source"]["byte_count"],
            "parser.record_regex": RECORD_RE.pattern,
            "parser.rational_regex": RAT_RE.pattern,
            "records.expected": 2001,
            "records.identifiers": "1..2001",
            "positions": audit["position_contract"],
            "signs": list(SIGNS),
            "root_convention": "nonnegative exact rational square root",
            "triple_contexts.expected": 40020,
            "signed_contexts.expected": 80040,
            "distinct_triple_keys.expected": 39490,
            "duplicate_excess.expected": 530,
            "calibration.bundle_sha256": audit["calibration"]["bundle_sha256"],
            "primary_engine.sha256": "exactly 64 uppercase hexadecimal characters; frozen before launch",
            "independent_engine.sha256": "exactly 64 uppercase hexadecimal characters; frozen before launch; no import of primary arithmetic/search code",
            "verifiers": verifiers,
            "resources.aggregate_workers_max": 64,
            "interpretation.no_hit": "NO_HIT only for the frozen 80040 canonical-shift contexts",
        },
        "canonical_ledger": {
            "encoding": "ASCII",
            "newline": "LF",
            "format": "TSV",
            "header": "record_id\ttriple_ordinal\tposition_mask\tsign\tcandidate\tdegeneracy\tsign_collapsed\tcomplement_bits\tsurvivor",
            "row_order": "record_id ascending, triple_ordinal ascending, sign order -1 then +1",
            "field_contract": {
                "record_id": "decimal 1..2001",
                "triple_ordinal": "decimal 0..19 indexing the frozen position list",
                "position_mask": "decimal frozen six-bit mask",
                "sign": "-1 or 1",
                "candidate": "canonical reduced integer or numerator/positive-denominator",
                "degeneracy": "ZERO, DUPLICATE_SELECTED, DUPLICATE_COMPLEMENT, or ELIGIBLE using frozen precedence",
                "sign_collapsed": "0 or 1; same for both signs of one triple context",
                "complement_bits": "three bits in ascending complement-position order",
                "survivor": "1 iff degeneracy=ELIGIBLE and complement_bits=111, else 0",
            },
            "expected_rows": 80040,
            "expected_unique_context_keys": 80040,
        },
        "terminal_acceptance": [
            "source bytes and every frozen executable/script hash match the manifest",
            "both engines independently parse exactly records 1..2001 and validate all 30015 source pairs",
            "both engines check all 240120 selected-extension identities and all 640320 root-sign assertions",
            "each engine emits exactly one row for every frozen record/ordinal/sign key in canonical order",
            "both canonical ledger byte streams have identical SHA-256 hashes and byte-for-byte content",
            "an independent terminal referee recomputes every candidate, degeneracy, complement bit, and survivor bit",
            "every survivor is exactly the source sextuple plus candidate and passes both frozen 21-pair verifiers",
            "HIT requires at least one dual-verified survivor; NO_HIT requires zero survivors and every preceding check; otherwise FAILED",
        ],
        "calibration": audit["calibration"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = args.output_dir / "referee_audit.json"
    contract_path = args.output_dir / "manifest_contract.json"
    calibration_ledger_path = args.output_dir / "calibration_expected.tsv"
    calibration_summary_path = args.output_dir / "calibration_expected_summary.json"
    audit_path.write_bytes(json.dumps(audit, indent=2, sort_keys=True).encode("ascii") + b"\n")
    contract_path.write_bytes(json.dumps(contract, indent=2, sort_keys=True).encode("ascii") + b"\n")
    calibration_ledger_path.write_bytes(manifest_ledger_bytes)
    calibration_summary_path.write_bytes(manifest_calibration_summary_bytes)
    summary = {
        "status": "PASS",
        "audit_path": str(audit_path.resolve()),
        "audit_sha256": sha256_file(audit_path),
        "contract_path": str(contract_path.resolve()),
        "contract_sha256": sha256_file(contract_path),
        "records": len(records),
        "signed_contexts": len(contexts) * 2,
        "distinct_triple_keys": len(triple_contexts),
        "duplicate_excess": len(contexts) - len(triple_contexts),
        "calibration_sha256": audit["calibration"]["bundle_sha256"],
        "manifest_calibration_ledger_sha256": sha256_file(calibration_ledger_path),
        "manifest_calibration_summary_sha256": sha256_file(calibration_summary_path),
        "full_complement_search_performed": False,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
