"""Exact finite audit of P48's heterogeneous span claim.

The search is exhaustive over endpoint-normalized subsets of [0, max_span].
All arithmetic and all acceptance decisions are integral or rational.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Ruler:
    values: tuple[int, ...]
    differences: frozenset[int]
    difference_mask: int

    @property
    def span(self) -> int:
        return self.values[-1]


def unordered_pair_sums(values: Sequence[int]) -> tuple[int, ...]:
    """Unordered sums, explicitly including diagonal pairs i = j."""
    return tuple(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def off_diagonal_pair_sums(values: Sequence[int]) -> tuple[int, ...]:
    return tuple(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )


def positive_difference_list(values: Sequence[int]) -> tuple[int, ...]:
    """Positive differences only: j > i, with no zero diagonal."""
    return tuple(
        values[j] - values[i]
        for j in range(1, len(values))
        for i in range(j)
    )


def unordered_triple_sums(values: Sequence[int]) -> set[int]:
    """All triples i <= j <= k, so repeated summands are retained."""
    return {
        values[i] + values[j] + values[k]
        for i in range(len(values))
        for j in range(i, len(values))
        for k in range(j, len(values))
    }


def all_distinct(values: Iterable[int]) -> bool:
    values = tuple(values)
    return len(values) == len(set(values))


def is_strong_sidon(values: Sequence[int]) -> bool:
    return all_distinct(unordered_pair_sums(values))


def enumerate_rulers(max_span: int) -> tuple[list[Ruler], dict[str, int]]:
    rulers: list[Ruler] = []
    candidate_count = 0
    weak_not_strong = 0

    for span in range(max_span + 1):
        masks = range(1) if span == 0 else range(1 << (span - 1))
        for subset_mask in masks:
            candidate_count += 1
            if span == 0:
                values = (0,)
            else:
                interior = tuple(
                    x for x in range(1, span) if subset_mask & (1 << (x - 1))
                )
                values = (0,) + interior + (span,)

            pair_sidon = is_strong_sidon(values)
            difference_list = positive_difference_list(values)
            difference_sidon = all_distinct(difference_list)
            assert pair_sidon == difference_sidon

            weak_sidon = all_distinct(off_diagonal_pair_sums(values))
            if weak_sidon and not pair_sidon:
                weak_not_strong += 1

            if not pair_sidon:
                continue
            differences = frozenset(difference_list)
            assert 0 not in differences
            difference_mask = sum(1 << d for d in differences)
            rulers.append(Ruler(values, differences, difference_mask))

    return rulers, {
        "endpoint_normalized_candidates": candidate_count,
        "strong_sidon_rulers": len(rulers),
        "off_diagonal_sidon_but_not_diagonal_sidon": weak_not_strong,
    }


def lag_differences(values: Sequence[int], h: int) -> list[int]:
    return [
        values[i + r] - values[i]
        for r in range(1, h + 1)
        for i in range(len(values) - r)
    ]


def uniform_bound(p: int) -> Fraction:
    h = isqrt(p)
    return Fraction(h, h + 1) * Fraction(2 * p - 3 * h - 1, 2) ** 2


def check_lag_certificate(x: Ruler, y: Ruler) -> tuple[str, Fraction, Fraction]:
    """Check the exact packing proof and return case, exact, uniform bounds."""
    m = len(x.values)
    n = len(y.values)
    p = m + n
    assert p >= 9
    h = isqrt(p)

    if min(m, n) >= h + 1:
        case = "joint"
        selected = lag_differences(x.values, h) + lag_differences(y.values, h)
        count = h * (p - h - 1)
        cap_twice = h * (h + 1) * (x.span + y.span)
        exact_bound = Fraction(count * (count + 1), h * (h + 1))
    else:
        case = "one_large_component"
        large = x if m >= n else y
        q = len(large.values)
        assert q >= h + 1
        selected = lag_differences(large.values, h)
        count = h * q - h * (h + 1) // 2
        cap_twice = h * (h + 1) * large.span
        exact_bound = Fraction(count * (count + 1), h * (h + 1))

    assert len(selected) == count
    assert len(selected) == len(set(selected))
    assert all(d > 0 for d in selected)
    assert count * (count + 1) <= 2 * sum(selected)
    assert 2 * sum(selected) <= cap_twice
    assert x.span + y.span >= exact_bound

    finite_uniform_bound = uniform_bound(p)
    assert exact_bound >= finite_uniform_bound
    assert x.span + y.span >= finite_uniform_bound
    return case, exact_bound, finite_uniform_bound


def guarded_lift(x: Ruler, y: Ruler) -> tuple[int, int, tuple[int, ...], tuple[int, ...]]:
    gap = max(x.span, y.span) + 1
    shift = gap + 3 * x.span + 1
    z = x.values + tuple(shift + value for value in y.values)
    e = tuple(gap + 2 * value for value in z)
    return gap, shift, z, e


def fraction_record(value: Fraction) -> dict[str, object]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def witness_record(x: Ruler, y: Ruler) -> dict[str, object]:
    total = x.span + y.span
    p = len(x.values) + len(y.values)
    return {
        "X": x.values,
        "Y": y.values,
        "U_plus_V": total,
        "p": p,
        "ratio": fraction_record(Fraction(total, p * p)),
    }


def audit(max_span: int, gate_span: int) -> dict[str, object]:
    rulers, enumeration = enumerate_rulers(max_span)
    gate_rulers = [ruler for ruler in rulers if ruler.span <= gate_span]

    gate_pairs = 0
    gate_difference_disjoint_pairs = 0
    for x in gate_rulers:
        for y in gate_rulers:
            gate_pairs += 1
            disjoint = not (x.difference_mask & y.difference_mask)
            gap, shift, z, e = guarded_lift(x, y)
            assert gap > max(x.span, y.span)
            assert shift > gap + 3 * x.span
            assert is_strong_sidon(z) == disjoint
            assert is_strong_sidon(e) == disjoint
            assert set(e).isdisjoint(unordered_triple_sums(e))
            if disjoint:
                gate_difference_disjoint_pairs += 1

    strict_guard_examples = [
        {
            "label": "G_equals_U",
            "E": (2, 6, 20, 22),
            "target": 6,
            "summands": (2, 2, 2),
        },
        {
            "label": "G_equals_V",
            "E": (2, 4, 14, 18),
            "target": 18,
            "summands": (2, 2, 14),
        },
        {
            "label": "T_equals_G_plus_3U",
            "E": (3, 5, 15, 19),
            "target": 15,
            "summands": (5, 5, 5),
        },
    ]
    for example in strict_guard_examples:
        values = example["E"]
        assert is_strong_sidon(values)
        assert example["target"] in values
        assert sum(example["summands"]) == example["target"]
        assert len(set(example["summands"])) < 3

    cross_disjoint_only_falsifiers = []
    for q in (8, 16, 32, 64):
        x_values = (0, 1)
        y_values = tuple(2 * i for i in range(q))
        x_differences = set(positive_difference_list(x_values))
        y_difference_list = positive_difference_list(y_values)
        assert x_differences.isdisjoint(y_difference_list)
        assert not all_distinct(y_difference_list)
        assert not is_strong_sidon(y_values)
        p = len(x_values) + len(y_values)
        cross_disjoint_only_falsifiers.append(
            {
                "q": q,
                "X": x_values,
                "Y_formula": "{0,2,...,2(q-1)}",
                "U_plus_V": 2 * q - 1,
                "p": p,
                "ratio": fraction_record(Fraction(2 * q - 1, p * p)),
            }
        )

    unbalanced_branch_checks = []
    for p in (9, 16, 25, 36):
        q = p - 2
        x_values = (0, 1)
        y_values = tuple(2 * ((1 << i) - 1) for i in range(q))
        x_difference_list = positive_difference_list(x_values)
        y_difference_list = positive_difference_list(y_values)
        assert set(x_difference_list).isdisjoint(y_difference_list)
        assert all_distinct(x_difference_list)
        assert all_distinct(y_difference_list)
        x = Ruler(x_values, frozenset(x_difference_list), 0)
        y = Ruler(y_values, frozenset(y_difference_list), 0)
        case, exact_bound, finite_uniform_bound = check_lag_certificate(x, y)
        assert case == "one_large_component"
        unbalanced_branch_checks.append(
            {
                "p": p,
                "X": "{0,1}",
                "Y_formula": "{2(2^i-1): 0 <= i < p-2}",
                "U_plus_V": x.span + y.span,
                "exact_lag_bound": fraction_record(exact_bound),
                "uniform_bound": fraction_record(finite_uniform_bound),
            }
        )

    compatible_pairs = 0
    lag_pairs = 0
    lag_cases = {"joint": 0, "one_large_component": 0}
    minimum_uniform_slack: Fraction | None = None
    minimum_uniform_slack_witness: tuple[Ruler, Ruler] | None = None
    minimum_by_p: dict[int, tuple[int, Ruler, Ruler]] = {}

    for x in rulers:
        for y in rulers:
            if x.difference_mask & y.difference_mask:
                continue
            compatible_pairs += 1
            p = len(x.values) + len(y.values)
            total = x.span + y.span

            previous = minimum_by_p.get(p)
            if previous is None or total < previous[0]:
                minimum_by_p[p] = (total, x, y)

            if p < 9:
                continue
            case, _exact_bound, finite_uniform_bound = check_lag_certificate(x, y)
            lag_pairs += 1
            lag_cases[case] += 1
            slack = Fraction(total) - finite_uniform_bound
            if minimum_uniform_slack is None or slack < minimum_uniform_slack:
                minimum_uniform_slack = slack
                minimum_uniform_slack_witness = (x, y)

    minima = []
    for p, (total, x, y) in sorted(minimum_by_p.items()):
        row = witness_record(x, y)
        row["search_box"] = f"U,V <= {max_span}"
        if p >= 9:
            row["uniform_lower_bound"] = fraction_record(uniform_bound(p))
        minima.append(row)

    if minimum_uniform_slack is None:
        minimum_slack_record = None
        minimum_slack_witness_record = None
    else:
        assert minimum_uniform_slack_witness is not None
        slack_x, slack_y = minimum_uniform_slack_witness
        minimum_slack_record = fraction_record(minimum_uniform_slack)
        minimum_slack_witness_record = witness_record(slack_x, slack_y)

    return {
        "parameters": {"max_span": max_span, "gate_span": gate_span},
        "conventions": {
            "integer_sets": True,
            "endpoint_normalized": "minima are 0 and displayed spans are attained",
            "pair_sums": "unordered i <= j, including diagonals",
            "differences": "positive j > i only; zero is excluded",
            "triple_sums": "unordered i <= j <= k, including repetitions",
        },
        "enumeration": enumeration,
        "validity_gate": {
            "ordered_ruler_pairs": gate_pairs,
            "difference_disjoint_pairs": gate_difference_disjoint_pairs,
            "sidon_iff_difference_disjoint_checked": True,
            "three_sum_free_for_every_guarded_pair_checked": True,
            "strict_guard_examples": strict_guard_examples,
        },
        "hypothesis_audit": {
            "cross_disjointness_alone_is_insufficient": True,
            "falsifier_family": "X={0,1}, Y={0,2,...,2(q-1)}",
            "checked_falsifier_instances": cross_disjoint_only_falsifiers,
            "unbalanced_strong_sidon_branch_checks": unbalanced_branch_checks,
        },
        "span_audit": {
            "ordered_difference_disjoint_pairs": compatible_pairs,
            "pairs_with_p_at_least_9": lag_pairs,
            "lag_cases": lag_cases,
            "minimum_uniform_bound_slack": minimum_slack_record,
            "minimum_uniform_bound_slack_witness": minimum_slack_witness_record,
            "minimum_span_sum_by_p_in_search_box": minima,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-span", type=int, default=18)
    parser.add_argument("--gate-span", type=int, default=9)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p55/audit_span_results.json"),
    )
    args = parser.parse_args()
    if not 0 <= args.gate_span <= args.max_span:
        parser.error("require 0 <= gate-span <= max-span")

    result = audit(args.max_span, args.gate_span)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")

    print("PASS: P55 span and convention audit")
    print("strong Sidon rulers:", result["enumeration"]["strong_sidon_rulers"])
    print(
        "difference-disjoint ordered pairs:",
        result["span_audit"]["ordered_difference_disjoint_pairs"],
    )
    print("lag cases:", result["span_audit"]["lag_cases"])
    print("output:", args.output)


if __name__ == "__main__":
    main()
