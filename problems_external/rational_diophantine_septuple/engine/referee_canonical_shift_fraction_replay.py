"""Independent Fraction replay of the 10-record canonical-shift calibration."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path


RECORD_RE = re.compile(r"^\((\d+)\)\s+\[([^\]]+)\]")
POSITIONS = tuple(itertools.combinations(range(6), 3))
SIGNS = (-1, 1)
RECORD_IDS = (1, 2, 5, 12, 100, 251, 501, 1000, 1500, 2001)
HEADER = (
    "ordinal\trecord_id\ti\tj\tk\tposition_mask\tsign\t"
    "r_num\tr_den\ts_num\ts_den\tt_num\tt_den\td_num\td_den\t"
    "degeneracy\tcomp0\tcomp1\tcomp2\tsurvivor"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        return None
    return Fraction(numerator, denominator)


def mask(positions: tuple[int, int, int]) -> int:
    return sum(1 << position for position in positions)


def parse(path: Path) -> dict[int, tuple[Fraction, ...]]:
    records: dict[int, tuple[Fraction, ...]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = RECORD_RE.match(line)
        if match is not None:
            records[int(match.group(1))] = tuple(Fraction(token.strip()) for token in match.group(2).split(","))
    if sorted(records) != list(range(1, 2002)) or any(len(values) != 6 for values in records.values()):
        raise ValueError("catalogue shape failure")
    return records


def label(candidate: Fraction, selected: tuple[Fraction, ...], complements: tuple[Fraction, ...]) -> str:
    if candidate == 0:
        return "ZERO"
    if candidate in selected:
        return "SELECTED_DUPLICATE"
    if candidate in complements:
        return "COMPLEMENT_DUPLICATE"
    return "DISTINCT_NONZERO"


def full_plan_audit(records: dict[int, tuple[Fraction, ...]]) -> dict[str, object]:
    pair_checks = 0
    identity_checks = 0
    sign_assertions = 0
    sign_collapses = 0
    degeneracies: Counter[str] = Counter()
    triple_multiplicities: Counter[tuple[Fraction, ...]] = Counter()
    sextuple_keys: set[tuple[Fraction, ...]] = set()
    for record_id in range(1, 2002):
        values = records[record_id]
        if any(value == 0 for value in values) or len(set(values)) != 6:
            raise ArithmeticError(f"invalid source record {record_id}")
        sextuple_keys.add(tuple(sorted(values)))
        for left, right in itertools.combinations(values, 2):
            if root(left * right + 1) is None:
                raise ArithmeticError(f"source pair failure in record {record_id}")
            pair_checks += 1
        for positions in POSITIONS:
            complement_positions = tuple(position for position in range(6) if position not in positions)
            selected = tuple(values[position] for position in positions)
            complements = tuple(values[position] for position in complement_positions)
            triple_multiplicities[tuple(sorted(selected))] += 1
            a, b, c = selected
            r, s, t = root(a * b + 1), root(a * c + 1), root(b * c + 1)
            if r is None or s is None or t is None:
                raise ArithmeticError("selected root failure")
            base = a + b + c + 2 * a * b * c
            delta = 2 * r * s * t
            candidates = (base - delta, base + delta)
            sign_collapses += int(candidates[0] == candidates[1])
            for sign_index, sign in enumerate(SIGNS):
                candidate = candidates[sign_index]
                expected_roots = (
                    a * t + sign * r * s,
                    b * s + sign * r * t,
                    c * r + sign * s * t,
                )
                if (a * candidate + 1, b * candidate + 1, c * candidate + 1) != tuple(
                    value * value for value in expected_roots
                ):
                    raise ArithmeticError("identity failure")
                identity_checks += 3
                degeneracies[label(candidate, selected, complements)] += 1
            for er, es, et in itertools.product(SIGNS, repeat=3):
                parity = er * es * et
                signed_delta = 2 * (er * r) * (es * s) * (et * t)
                for sign in SIGNS:
                    if base + sign * signed_delta != candidates[SIGNS.index(sign * parity)]:
                        raise ArithmeticError("root-sign invariance failure")
                    sign_assertions += 1
    multiplicity_histogram = Counter(triple_multiplicities.values())
    repeated = [multiplicity for multiplicity in triple_multiplicities.values() if multiplicity > 1]
    return {
        "records": len(records),
        "distinct_sextuple_sets": len(sextuple_keys),
        "source_pair_checks": pair_checks,
        "triple_contexts": sum(triple_multiplicities.values()),
        "signed_contexts": 2 * sum(triple_multiplicities.values()),
        "identity_checks": identity_checks,
        "root_sign_assertions": sign_assertions,
        "sign_collapses": sign_collapses,
        "distinct_triple_keys": len(triple_multiplicities),
        "duplicate_excess": sum(triple_multiplicities.values()) - len(triple_multiplicities),
        "repeated_keys": len(repeated),
        "contexts_on_repeated_keys": sum(repeated),
        "multiplicity_histogram": {str(key): value for key, value in sorted(multiplicity_histogram.items())},
        "degeneracy_counts": {
            category: degeneracies.get(category, 0)
            for category in ("ZERO", "SELECTED_DUPLICATE", "COMPLEMENT_DUPLICATE", "DISTINCT_NONZERO")
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("expected_ledger", type=Path)
    parser.add_argument("expected_summary", type=Path)
    parser.add_argument("--full-plan-audit", action="store_true")
    args = parser.parse_args()
    records = parse(args.catalog)

    lines = [HEADER]
    degeneracies: Counter[str] = Counter()
    patterns: Counter[str] = Counter()
    survivors = 0
    pair_checks = 0
    identity_checks = 0
    for record_id in RECORD_IDS:
        values = records[record_id]
        if any(value == 0 for value in values) or len(set(values)) != 6:
            raise ArithmeticError(f"invalid source record {record_id}")
        for left, right in itertools.combinations(values, 2):
            if root(left * right + 1) is None:
                raise ArithmeticError(f"source pair failure in record {record_id}")
            pair_checks += 1
        for triple_ordinal, positions in enumerate(POSITIONS):
            complement_positions = tuple(position for position in range(6) if position not in positions)
            selected = tuple(values[position] for position in positions)
            complements = tuple(values[position] for position in complement_positions)
            a, b, c = selected
            r, s, t = root(a * b + 1), root(a * c + 1), root(b * c + 1)
            if r is None or s is None or t is None:
                raise ArithmeticError("selected root failure")
            base = a + b + c + 2 * a * b * c
            for sign_index, sign in enumerate(SIGNS):
                candidate = base + sign * 2 * r * s * t
                expected_roots = (
                    a * t + sign * r * s,
                    b * s + sign * r * t,
                    c * r + sign * s * t,
                )
                left_sides = (a * candidate + 1, b * candidate + 1, c * candidate + 1)
                if left_sides != tuple(value * value for value in expected_roots):
                    raise ArithmeticError("identity failure")
                identity_checks += 3
                category = label(candidate, selected, complements)
                bits = "".join("1" if root(value * candidate + 1) is not None else "0" for value in complements)
                survivor = int(category == "DISTINCT_NONZERO" and bits == "111")
                degeneracies[category] += 1
                patterns[bits] += 1
                survivors += survivor
                ordinal = (record_id - 1) * 40 + 2 * triple_ordinal + sign_index
                i, j, k = positions
                fields: tuple[object, ...] = (
                    ordinal,
                    record_id,
                    i,
                    j,
                    k,
                    mask(positions),
                    sign,
                    r.numerator,
                    r.denominator,
                    s.numerator,
                    s.denominator,
                    t.numerator,
                    t.denominator,
                    candidate.numerator,
                    candidate.denominator,
                    category,
                    bits[0],
                    bits[1],
                    bits[2],
                    survivor,
                )
                lines.append("\t".join(str(field) for field in fields))

    ledger = ("\n".join(lines) + "\n").encode("ascii")
    source_sha = sha(args.catalog.read_bytes())
    summary = {
        "schema": "canonical_shift_calibration_summary/v1",
        "source_sha256": source_sha,
        "record_ids": list(RECORD_IDS),
        "record_count": len(RECORD_IDS),
        "context_count": 400,
        "source_pair_checks": pair_checks,
        "extension_identity_checks": identity_checks,
        "ledger_byte_count": len(ledger),
        "ledger_sha256": sha(ledger),
        "degeneracy_counts": {
            category: degeneracies.get(category, 0)
            for category in ("ZERO", "SELECTED_DUPLICATE", "COMPLEMENT_DUPLICATE", "DISTINCT_NONZERO")
        },
        "complement_pattern_counts": {f"{value:03b}": patterns.get(f"{value:03b}", 0) for value in range(8)},
        "survivor_count": survivors,
    }
    summary_bytes = (
        json.dumps(summary, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode("ascii")
    expected_ledger = args.expected_ledger.read_bytes()
    expected_summary = args.expected_summary.read_bytes()
    result = {
        "status": "PASS" if ledger == expected_ledger and summary_bytes == expected_summary else "FAILED",
        "ledger_sha256": sha(ledger),
        "ledger_bytes_match": ledger == expected_ledger,
        "summary_sha256": sha(summary_bytes),
        "summary_bytes_match": summary_bytes == expected_summary,
        "contexts": len(lines) - 1,
        "source_pair_checks": pair_checks,
        "identity_checks": identity_checks,
        "survivors": survivors,
    }
    if args.full_plan_audit:
        result["full_plan_audit"] = full_plan_audit(records)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
