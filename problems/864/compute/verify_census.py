#!/usr/bin/env python3
"""Exact, dependency-free verifier for Erdos Problem 864 candidate records.

The command accepts a JSON object, a JSON array of objects, or JSONL.  It
prints one deterministic JSON report per candidate and exits nonzero if any
candidate is invalid.  All arithmetic is integer arithmetic.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
from itertools import combinations
import json
from pathlib import Path
import sys
import unittest
from typing import Any, Iterable, Sequence


DEFAULT_SIDON_LIMIT = 24
REQUIRED_FIELDS = (
    "N",
    "A",
    "exceptional_sum",
    "exceptional_multiplicity",
    "objective",
    "bound",
    "status",
)

STATUS_ALIASES = {
    "optimal": "optimal",
    "optimum": "optimal",
    "proven_optimal": "optimal",
    "feasible": "feasible",
    "sat": "feasible",
    "satisfiable": "feasible",
    "candidate": "feasible",
    "unknown": "unknown",
    "timeout": "unknown",
    "time_limit": "unknown",
    "not_solved": "unknown",
}


class InputFormatError(ValueError):
    """Raised when JSON/JSONL input cannot be interpreted unambiguously."""


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


class JSONDecimal(str):
    """Exact lexical representation of a JSON number containing a decimal."""


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _error(code: str, message: str, **details: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "message": message}
    if details:
        result["details"] = details
    return result


def _no_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonstandard_number(token: str) -> None:
    raise ValueError(f"non-standard JSON number {token!r}")


def _json_loads(text: str, location: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_no_duplicate_json_keys,
            parse_float=JSONDecimal,
            parse_constant=_reject_nonstandard_number,
        )
    except (json.JSONDecodeError, DuplicateJSONKeyError, ValueError) as exc:
        raise InputFormatError(f"{location}: {exc}") from exc


def parse_records(
    text: str,
    input_format: str,
    source: str = "<memory>",
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Parse records and return each object with source-location metadata."""

    if input_format not in {"json", "jsonl", "auto"}:
        raise ValueError(f"unsupported input format {input_format!r}")

    text = text.removeprefix("\ufeff")
    selected_format = input_format
    if selected_format == "auto":
        suffix = Path(source).suffix.lower()
        if suffix in {".jsonl", ".ndjson"}:
            selected_format = "jsonl"
        elif suffix == ".json":
            selected_format = "json"
        else:
            try:
                parsed = _json_loads(text, source)
            except InputFormatError:
                selected_format = "jsonl"
            else:
                return _records_from_json_value(parsed, source)

    if selected_format == "json":
        return _records_from_json_value(_json_loads(text, source), source)

    records: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        value = _json_loads(line, f"{source}:{line_number}")
        if not isinstance(value, dict):
            raise InputFormatError(
                f"{source}:{line_number}: each JSONL line must be an object"
            )
        records.append((value, {"path": source, "line": line_number}))
    return records


def _records_from_json_value(
    value: Any,
    source: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if isinstance(value, dict):
        return [(value, {"path": source, "record": 1})]
    if not isinstance(value, list):
        raise InputFormatError(f"{source}: top-level JSON must be an object or array")

    records: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for index, record in enumerate(value, start=1):
        if not isinstance(record, dict):
            raise InputFormatError(
                f"{source}: JSON array item {index} must be an object"
            )
        records.append((record, {"path": source, "record": index}))
    return records


def unordered_sum_representations(
    values: Sequence[int],
) -> dict[int, list[tuple[int, int]]]:
    """Return all a <= b representations, including every diagonal a = b."""

    ordered = sorted(values)
    representations: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for index, left in enumerate(ordered):
        for right in ordered[index:]:
            representations[left + right].append((left, right))
    return dict(sorted(representations.items()))


def _conflict_masks(values: Sequence[int]) -> tuple[int, ...]:
    indexed_representations: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for left_index, left in enumerate(values):
        for right_index in range(left_index, len(values)):
            indexed_representations[left + values[right_index]].append(
                (left_index, right_index)
            )

    masks: set[int] = set()
    for representations in indexed_representations.values():
        for first, second in combinations(representations, 2):
            mask = 0
            for index in first + second:
                mask |= 1 << index
            masks.add(mask)

    # If one forbidden selected-set is contained in another, hitting the
    # smaller set automatically hits the larger one.
    minimal: list[int] = []
    for mask in sorted(masks, key=lambda item: (item.bit_count(), item)):
        if not any(existing & mask == existing for existing in minimal):
            minimal.append(mask)
    return tuple(minimal)


def _greedy_hitting_set(constraints: Sequence[int]) -> int:
    removed = 0
    while True:
        unhit = [mask for mask in constraints if not mask & removed]
        if not unhit:
            return removed
        frequencies: Counter[int] = Counter()
        for mask in unhit:
            remaining = mask
            while remaining:
                bit = remaining & -remaining
                frequencies[bit.bit_length() - 1] += 1
                remaining ^= bit
        chosen = max(frequencies, key=lambda index: (frequencies[index], -index))
        removed |= 1 << chosen


def _disjoint_constraint_lower_bound(constraints: Sequence[int]) -> int:
    used_vertices = 0
    count = 0
    for mask in sorted(constraints, key=lambda item: (item.bit_count(), item)):
        if not mask & used_vertices:
            used_vertices |= mask
            count += 1
    return count


def maximum_sidon_subset(values: Sequence[int]) -> dict[str, Any]:
    """Find an exact maximum-cardinality Sidon subset by branch and bound."""

    ordered = sorted(values)
    if len(set(ordered)) != len(ordered):
        raise ValueError("maximum_sidon_subset requires distinct values")
    if not all(_is_integer(value) for value in ordered):
        raise ValueError("maximum_sidon_subset requires integer values")

    constraints = _conflict_masks(ordered)
    if not constraints:
        return {
            "computed": True,
            "method": "exact conflict hitting set",
            "search_nodes": 1,
            "size": len(ordered),
            "subset": ordered,
        }

    best_removed = _greedy_hitting_set(constraints)
    seen: set[int] = set()
    search_nodes = 0

    def search(removed: int) -> None:
        nonlocal best_removed, search_nodes
        search_nodes += 1
        if removed in seen or removed.bit_count() >= best_removed.bit_count():
            return
        seen.add(removed)

        unhit = [mask for mask in constraints if not mask & removed]
        if not unhit:
            best_removed = removed
            return

        lower_bound = _disjoint_constraint_lower_bound(unhit)
        if removed.bit_count() + lower_bound >= best_removed.bit_count():
            return

        frequencies: Counter[int] = Counter()
        for mask in unhit:
            remaining = mask
            while remaining:
                bit = remaining & -remaining
                frequencies[bit.bit_length() - 1] += 1
                remaining ^= bit

        branch_mask = min(
            unhit,
            key=lambda mask: (
                mask.bit_count(),
                -sum(
                    frequencies[index]
                    for index in range(len(ordered))
                    if mask & (1 << index)
                ),
                mask,
            ),
        )
        branch_indices = [
            index for index in range(len(ordered)) if branch_mask & (1 << index)
        ]
        branch_indices.sort(key=lambda index: (-frequencies[index], index))
        for index in branch_indices:
            search(removed | (1 << index))

    search(0)
    subset = [
        value for index, value in enumerate(ordered) if not best_removed & (1 << index)
    ]
    return {
        "computed": True,
        "method": "exact conflict hitting set",
        "search_nodes": search_nodes,
        "size": len(subset),
        "subset": subset,
    }


def _one_exception_sidon_subset(
    values: Sequence[int],
    representations: Sequence[tuple[int, int]],
) -> list[int]:
    """Construct a maximum Sidon subset when exactly one sum is repeated."""

    removed: set[int] = set()
    for left, right in representations[1:]:
        removed.add(right if left != right else left)
    return [value for value in values if value not in removed]


def _normalize_status(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    key = value.strip().lower().replace("-", "_").replace(" ", "_")
    return STATUS_ALIASES.get(key)


def _normalize_bound(value: Any) -> int | None:
    if _is_integer(value):
        return value if value >= 0 else None
    if isinstance(value, JSONDecimal):
        decimal = Decimal(value)
        integral = decimal.to_integral_value()
        if decimal == integral and integral >= 0:
            return int(integral)
    return None


def _analyze_candidate(
    N: int,
    values: list[int],
    sidon_limit: int,
) -> dict[str, Any]:
    representations = unordered_sum_representations(values)
    repeated = [
        (sum_value, pairs)
        for sum_value, pairs in representations.items()
        if len(pairs) >= 2
    ]
    exceptional_sum = repeated[0][0] if len(repeated) == 1 else None
    exceptional_pairs = repeated[0][1] if len(repeated) == 1 else []
    exceptional_multiplicity = len(exceptional_pairs) if exceptional_pairs else 0

    histogram = Counter(len(pairs) for pairs in representations.values())
    diagonal_collision_sums = [
        sum_value
        for sum_value, pairs in representations.items()
        if len(pairs) >= 2 and any(left == right for left, right in pairs)
    ]
    reflected_elements = {
        value for pair in exceptional_pairs for value in pair
    }

    if len(values) <= sidon_limit:
        sidon = maximum_sidon_subset(values)
        sidon["limit"] = sidon_limit
    elif len(repeated) <= 1:
        if repeated:
            subset = _one_exception_sidon_subset(values, exceptional_pairs)
        else:
            subset = list(values)
        sidon = {
            "computed": True,
            "limit": sidon_limit,
            "method": "exact one-exception formula",
            "search_nodes": 0,
            "size": len(subset),
            "subset": subset,
        }
    else:
        sidon = {
            "computed": False,
            "limit": sidon_limit,
            "method": None,
            "reason": "cardinality exceeds exact-search limit",
            "search_nodes": 0,
            "size": None,
            "subset": None,
        }

    pair_count = len(values) * (len(values) + 1) // 2
    distinct_sum_count = len(representations)
    return {
        "N": N,
        "A": values,
        "cardinality": len(values),
        "exceptional_sum": exceptional_sum,
        "exceptional_multiplicity": exceptional_multiplicity,
        "sum_multiplicities": [
            {"sum": sum_value, "multiplicity": len(pairs)}
            for sum_value, pairs in representations.items()
        ],
        "repeated_sums": [
            {
                "sum": sum_value,
                "multiplicity": len(pairs),
                "representations": [list(pair) for pair in pairs],
            }
            for sum_value, pairs in repeated
        ],
        "statistics": {
            "admissible": len(repeated) <= 1,
            "collision_excess": pair_count - distinct_sum_count,
            "diagonal_collision_sums": diagonal_collision_sums,
            "diagonal_pair_count": len(values),
            "distinct_sum_count": distinct_sum_count,
            "maximum_sidon_subset": sidon,
            "maximum_sidon_subset_size": sidon["size"],
            "max_sum_multiplicity": max(histogram, default=0),
            "multiplicity_histogram": [
                {"multiplicity": multiplicity, "sum_count": histogram[multiplicity]}
                for multiplicity in sorted(histogram)
            ],
            "reflection_center": exceptional_sum,
            "reflection_pair_count": len(exceptional_pairs),
            "reflection_pairs": [list(pair) for pair in exceptional_pairs],
            "reflected_element_count": len(reflected_elements),
            "reflection_fixed_point": next(
                (left for left, right in exceptional_pairs if left == right),
                None,
            ),
            "reflection_closed_about_exception": bool(exceptional_pairs)
            and len(reflected_elements) == len(values),
            "unpaired_element_count": len(values) - len(reflected_elements),
            "repeated_sum_count": len(repeated),
            "sum_domain": [2, 2 * N],
            "total_unordered_pair_count": pair_count,
            "zero_multiplicity_sum_count": max(0, 2 * N - 1 - distinct_sum_count),
        },
    }


def verify_record(
    record: Any,
    *,
    sidon_limit: int = DEFAULT_SIDON_LIMIT,
) -> dict[str, Any]:
    """Verify one record and return a complete machine-readable report."""

    if sidon_limit < 0:
        raise ValueError("sidon_limit must be nonnegative")

    errors: list[dict[str, Any]] = []
    if not isinstance(record, dict):
        return {
            "valid": False,
            "errors": [_error("record_type", "candidate record must be an object")],
            "claims": None,
            "metadata": None,
            "computed": None,
        }

    missing = [
        field
        for field in REQUIRED_FIELDS
        if field != "bound" and field not in record
    ]
    if "bound" not in record and "diagnostic_best_bound" not in record:
        missing.append("bound")
    for field in missing:
        errors.append(_error("missing_field", f"missing required field {field!r}", field=field))

    N = record.get("N")
    valid_N = _is_integer(N) and N >= 1
    if "N" in record and not valid_N:
        errors.append(_error("invalid_N", "N must be a positive integer", value=N))

    raw_A = record.get("A")
    valid_A_container = isinstance(raw_A, list)
    integer_A = False
    distinct_A = False
    in_range_A = False
    ordered_A: list[int] | None = None
    if "A" in record and not valid_A_container:
        errors.append(_error("invalid_A", "A must be a JSON array"))
    elif valid_A_container:
        bad_elements = [
            {"index": index, "value": value}
            for index, value in enumerate(raw_A)
            if not _is_integer(value)
        ]
        integer_A = not bad_elements
        if bad_elements:
            errors.append(
                _error(
                    "noninteger_element",
                    "every element of A must be an integer (booleans are not integers)",
                    elements=bad_elements,
                )
            )
        if integer_A:
            counts = Counter(raw_A)
            duplicates = sorted(value for value, count in counts.items() if count > 1)
            distinct_A = not duplicates
            if duplicates:
                errors.append(
                    _error(
                        "duplicate_element",
                        "A must not contain duplicate elements",
                        values=duplicates,
                    )
                )
            if valid_N:
                out_of_range = sorted({value for value in raw_A if not 1 <= value <= N})
                in_range_A = not out_of_range
                if out_of_range:
                    errors.append(
                        _error(
                            "out_of_range_element",
                            "every element of A must lie in [1, N]",
                            values=out_of_range,
                        )
                    )
            if distinct_A and valid_N and in_range_A:
                ordered_A = sorted(raw_A)

    claimed_sum = record.get("exceptional_sum")
    valid_claimed_sum = claimed_sum is None or _is_integer(claimed_sum)
    if "exceptional_sum" in record and not valid_claimed_sum:
        errors.append(
            _error(
                "invalid_exceptional_sum",
                "exceptional_sum must be an integer or null",
                value=claimed_sum,
            )
        )

    claimed_multiplicity = record.get("exceptional_multiplicity")
    valid_claimed_multiplicity = (
        _is_integer(claimed_multiplicity) and claimed_multiplicity >= 0
    )
    if "exceptional_multiplicity" in record and not valid_claimed_multiplicity:
        errors.append(
            _error(
                "invalid_exceptional_multiplicity",
                "exceptional_multiplicity must be a nonnegative integer",
                value=claimed_multiplicity,
            )
        )

    objective = record.get("objective")
    valid_objective = _is_integer(objective) and objective >= 0
    if "objective" in record and not valid_objective:
        errors.append(
            _error("invalid_objective", "objective must be a nonnegative integer", value=objective)
        )

    bound_fields = [
        field for field in ("bound", "diagnostic_best_bound") if field in record
    ]
    normalized_bounds = {
        field: _normalize_bound(record[field]) for field in bound_fields
    }
    for field, normalized_bound in normalized_bounds.items():
        if normalized_bound is None:
            errors.append(
                _error(
                    "invalid_bound",
                    "bound must be an exact nonnegative integer",
                    field=field,
                    value=record[field],
                )
            )
    valid_bound = bool(bound_fields) and all(
        value is not None for value in normalized_bounds.values()
    )
    bound_field = "bound" if "bound" in record else None
    if bound_field is None and "diagnostic_best_bound" in record:
        bound_field = "diagnostic_best_bound"
    bound_raw = record[bound_field] if bound_field is not None else None
    bound = normalized_bounds.get(bound_field) if bound_field is not None else None
    if (
        len(bound_fields) == 2
        and valid_bound
        and normalized_bounds["bound"] != normalized_bounds["diagnostic_best_bound"]
    ):
        errors.append(
            _error(
                "conflicting_bound_fields",
                "bound and diagnostic_best_bound must agree when both are present",
                bound=normalized_bounds["bound"],
                diagnostic_best_bound=normalized_bounds["diagnostic_best_bound"],
            )
        )
        valid_bound = False

    raw_status = record.get("status")
    normalized_status = _normalize_status(raw_status)
    if "status" in record and normalized_status is None:
        errors.append(
            _error(
                "invalid_status",
                "status must denote optimal, feasible, or unknown",
                value=raw_status,
            )
        )

    if ordered_A is not None and valid_objective and objective != len(ordered_A):
        errors.append(
            _error(
                "objective_mismatch",
                "objective must equal |A|",
                claimed=objective,
                actual=len(ordered_A),
            )
        )
    if valid_objective and valid_bound and bound < objective:
        errors.append(
            _error(
                "bound_below_objective",
                "bound is an upper bound for maximization and must be at least objective",
                objective=objective,
                bound=bound,
            )
        )
    if (
        normalized_status == "optimal"
        and valid_objective
        and valid_bound
        and bound != objective
    ):
        errors.append(
            _error(
                "optimal_bound_mismatch",
                "optimal status requires bound equal to objective",
                objective=objective,
                bound=bound,
            )
        )

    computed = None
    if ordered_A is not None:
        computed = _analyze_candidate(N, ordered_A, sidon_limit)
        repeated_sum_count = computed["statistics"]["repeated_sum_count"]
        if repeated_sum_count > 1:
            errors.append(
                _error(
                    "multiple_repeated_sums",
                    "A is not admissible: more than one sum has multiplicity at least two",
                    sums=[item["sum"] for item in computed["repeated_sums"]],
                )
            )

        actual_sum = computed["exceptional_sum"]
        actual_multiplicity = computed["exceptional_multiplicity"]
        if repeated_sum_count <= 1 and valid_claimed_sum and claimed_sum != actual_sum:
            errors.append(
                _error(
                    "exceptional_sum_mismatch",
                    "claimed exceptional sum does not match the recomputed value",
                    claimed=claimed_sum,
                    actual=actual_sum,
                )
            )
        if (
            repeated_sum_count <= 1
            and valid_claimed_multiplicity
            and claimed_multiplicity != actual_multiplicity
        ):
            errors.append(
                _error(
                    "exceptional_multiplicity_mismatch",
                    "claimed exceptional multiplicity does not match the recomputed value",
                    claimed=claimed_multiplicity,
                    actual=actual_multiplicity,
                )
            )

    claims = {
        "exceptional_sum": claimed_sum,
        "exceptional_multiplicity": claimed_multiplicity,
    }
    metadata = {
        "objective": objective,
        "bound": bound if valid_bound else bound_raw,
        "bound_field": bound_field,
        "status": raw_status,
        "normalized_status": normalized_status,
        "interpretation": "maximum-cardinality objective with an upper bound",
        "optimality_certificate_checked": False,
    }
    return {
        "valid": not errors,
        "errors": errors,
        "claims": claims,
        "metadata": metadata,
        "computed": computed,
    }


def _base_record(**updates: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "N": 12,
        "A": [1, 2],
        "exceptional_sum": None,
        "exceptional_multiplicity": 0,
        "objective": 2,
        "bound": 2,
        "status": "OPTIMAL",
    }
    record.update(updates)
    return record


class VerifierSelfTests(unittest.TestCase):
    def assert_error(self, report: dict[str, Any], code: str) -> None:
        self.assertFalse(report["valid"])
        self.assertIn(code, {error["code"] for error in report["errors"]})

    def test_genuine_sidon_set(self) -> None:
        report = verify_record(_base_record())
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["computed"]["sum_multiplicities"], [
            {"sum": 2, "multiplicity": 1},
            {"sum": 3, "multiplicity": 1},
            {"sum": 4, "multiplicity": 1},
        ])

    def test_off_diagonal_exception(self) -> None:
        report = verify_record(_base_record(
            N=9,
            A=[9, 1, 7, 3],
            exceptional_sum=10,
            exceptional_multiplicity=2,
            objective=4,
            bound=7,
            status="feasible",
        ))
        self.assertTrue(report["valid"], report["errors"])
        stats = report["computed"]["statistics"]
        self.assertEqual(stats["reflection_pairs"], [[1, 9], [3, 7]])
        self.assertTrue(stats["reflection_closed_about_exception"])
        self.assertEqual(stats["maximum_sidon_subset_size"], 3)

    def test_diagonal_collision_is_counted(self) -> None:
        report = verify_record(_base_record(
            N=3,
            A=[1, 2, 3],
            exceptional_sum=4,
            exceptional_multiplicity=2,
            objective=3,
            bound=3,
        ))
        self.assertTrue(report["valid"], report["errors"])
        repeated = report["computed"]["repeated_sums"]
        self.assertEqual(repeated[0]["representations"], [[1, 3], [2, 2]])
        self.assertEqual(report["computed"]["statistics"]["diagonal_collision_sums"], [4])
        self.assertEqual(report["computed"]["statistics"]["maximum_sidon_subset_size"], 2)

    def test_diagonal_and_two_reflection_pairs(self) -> None:
        report = verify_record(_base_record(
            N=11,
            A=[1, 3, 6, 9, 11],
            exceptional_sum=12,
            exceptional_multiplicity=3,
            objective=5,
            bound=5,
        ))
        self.assertTrue(report["valid"], report["errors"])
        stats = report["computed"]["statistics"]
        self.assertEqual(stats["reflection_fixed_point"], 6)
        self.assertEqual(stats["maximum_sidon_subset_size"], 3)

    def test_multiple_repeated_sums_rejected_but_analyzed(self) -> None:
        report = verify_record(_base_record(
            N=4,
            A=[1, 2, 3, 4],
            exceptional_sum=4,
            exceptional_multiplicity=2,
            objective=4,
            bound=4,
        ))
        self.assert_error(report, "multiple_repeated_sums")
        self.assertGreater(report["computed"]["statistics"]["repeated_sum_count"], 1)
        self.assertEqual(report["computed"]["statistics"]["maximum_sidon_subset_size"], 3)

    def test_duplicate_and_out_of_range_rejected(self) -> None:
        duplicate = verify_record(_base_record(A=[1, 1], objective=2))
        self.assert_error(duplicate, "duplicate_element")
        out_of_range = verify_record(_base_record(N=3, A=[0, 4], objective=2))
        self.assert_error(out_of_range, "out_of_range_element")

    def test_boole_and_floats_are_not_integers(self) -> None:
        self.assert_error(verify_record(_base_record(N=True)), "invalid_N")
        self.assert_error(verify_record(_base_record(A=[1, 2.0])), "noninteger_element")
        self.assert_error(verify_record(_base_record(objective=2.0)), "invalid_objective")

    def test_claim_and_metadata_mismatches(self) -> None:
        self.assert_error(
            verify_record(_base_record(exceptional_sum=3, exceptional_multiplicity=1)),
            "exceptional_sum_mismatch",
        )
        self.assert_error(verify_record(_base_record(objective=1)), "objective_mismatch")
        self.assert_error(verify_record(_base_record(bound=1)), "bound_below_objective")
        self.assert_error(verify_record(_base_record(bound=3)), "optimal_bound_mismatch")
        self.assert_error(verify_record(_base_record(status="INFEASIBLE")), "invalid_status")

    def test_large_admissible_formula(self) -> None:
        report = verify_record(_base_record(
            N=9,
            A=[1, 3, 7, 9],
            exceptional_sum=10,
            exceptional_multiplicity=2,
            objective=4,
            bound=4,
        ), sidon_limit=0)
        sidon = report["computed"]["statistics"]["maximum_sidon_subset"]
        self.assertEqual(sidon["method"], "exact one-exception formula")
        self.assertEqual(sidon["size"], 3)

    def test_json_and_jsonl_parsing(self) -> None:
        json_records = parse_records(json.dumps([_base_record(), _base_record()]), "json")
        self.assertEqual(len(json_records), 2)
        jsonl = "\n".join(json.dumps(_base_record()) for _ in range(2))
        jsonl_records = parse_records(jsonl, "jsonl", "records.jsonl")
        self.assertEqual([source["line"] for _, source in jsonl_records], [1, 2])

    def test_solver_bound_alias_is_normalized_exactly(self) -> None:
        record = _base_record()
        record.pop("bound")
        text = json.dumps(record)[:-1] + ', "diagnostic_best_bound": 2.0}'
        parsed = parse_records(text, "json")[0][0]
        report = verify_record(parsed)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["metadata"]["bound"], 2)
        self.assertEqual(report["metadata"]["bound_field"], "diagnostic_best_bound")

    def test_fractional_bound_is_rejected(self) -> None:
        text = json.dumps(_base_record()).replace('"bound": 2', '"bound": 2.5')
        parsed = parse_records(text, "json")[0][0]
        self.assert_error(verify_record(parsed), "invalid_bound")

    def test_duplicate_json_key_rejected(self) -> None:
        with self.assertRaisesRegex(InputFormatError, "duplicate JSON key"):
            parse_records('{"N": 3, "N": 4}', "json")


def run_self_tests() -> bool:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(VerifierSelfTests)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    return result.wasSuccessful()


def _read_input(path_text: str) -> str:
    if path_text == "-":
        return sys.stdin.read()
    return Path(path_text).read_text(encoding="utf-8-sig")


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exactly verify Erdos 864 candidate records in JSON or JSONL.",
    )
    parser.add_argument("inputs", nargs="*", help="input paths; use - for standard input")
    parser.add_argument(
        "--input-format",
        choices=("auto", "json", "jsonl"),
        default="auto",
        help="input encoding (default: infer from suffix/content)",
    )
    parser.add_argument(
        "--sidon-limit",
        type=int,
        default=DEFAULT_SIDON_LIMIT,
        help="largest non-admissible record for exact maximum-Sidon search",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run embedded regression tests and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _make_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        if args.inputs:
            parser.error("--self-test does not accept input paths")
        return 0 if run_self_tests() else 1
    if not args.inputs:
        parser.error("at least one input path is required (use - for standard input)")
    if args.sidon_limit < 0:
        parser.error("--sidon-limit must be nonnegative")
    if args.inputs.count("-") > 1:
        parser.error("standard input may be specified only once")

    valid_count = 0
    invalid_count = 0
    input_failed = False
    for path_text in args.inputs:
        try:
            text = _read_input(path_text)
            records = parse_records(text, args.input_format, path_text)
        except (OSError, InputFormatError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            input_failed = True
            continue

        for record, source in records:
            report = verify_record(record, sidon_limit=args.sidon_limit)
            report["source"] = source
            print(json.dumps(report, sort_keys=True, separators=(",", ":")))
            if report["valid"]:
                valid_count += 1
            else:
                invalid_count += 1

    print(
        f"verified {valid_count + invalid_count} record(s): "
        f"{valid_count} valid, {invalid_count} invalid",
        file=sys.stderr,
    )
    if input_failed:
        return 2
    return 1 if invalid_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
