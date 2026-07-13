#!/usr/bin/env python3
"""Exact audit of P56 completion defects and residual-label charges."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable


def pair_sums(values: Iterable[int]) -> Counter[int]:
    ordered = tuple(sorted(values))
    counts: Counter[int] = Counter()
    for j, right in enumerate(ordered):
        for left in ordered[: j + 1]:
            counts[left + right] += 1
    return counts


def positive_differences(values: Iterable[int]) -> set[int]:
    ordered = tuple(sorted(values))
    return {
        right - left
        for j, right in enumerate(ordered)
        for left in ordered[:j]
    }


def analyze(a: tuple[int, ...]) -> dict | None:
    sums = pair_sums(a)
    repeated = [label for label, count in sums.items() if count >= 2]
    if len(repeated) != 1:
        return None
    sigma = repeated[0]
    aset = set(a)
    core = tuple(x for x in a if sigma - x in aset)
    residual = tuple(x for x in a if sigma - x not in aset)
    if not residual:
        return None

    delta = int(sigma % 2 == 0 and sigma // 2 in aset)
    p = (len(core) - delta) // 2
    c = len(core)
    u = len(residual)
    k = len(a)
    span = a[-1] - a[0]
    tau = abs(sigma - a[0] - a[-1])
    core_span = core[-1] - core[0]
    if span - tau < core_span:
        raise AssertionError("core/shift geometry failed")
    differences = positive_differences(a)

    residual_sum_labels = {
        left + right
        for j, right in enumerate(a)
        for left in a[: j + 1]
        if left in residual or right in residual
    }
    residual_difference_labels = {
        right - left
        for j, right in enumerate(a)
        for left in a[:j]
        if left in residual or right in residual
    }
    virtual_pairs = [
        (abs(left + right - sigma), i, j)
        for j, right in enumerate(residual)
        for i, left in enumerate(residual[: j + 1])
    ]
    virtual_counts = Counter(label for label, _, _ in virtual_pairs)
    if max(virtual_counts.values(), default=0) > 2:
        raise AssertionError("three residual sums have the same folded label")
    internal_beta = sum(count - 1 for count in virtual_counts.values())
    old_overlap_beta = sum(label in differences for label in virtual_counts)
    beta = sum(
        max(0, int(label in differences) + count - 1)
        for label, count in virtual_counts.items()
    )

    marked: list[tuple[int, int, int]] = []
    for label in sorted(virtual_counts):
        pairs = [(i, j) for item, i, j in virtual_pairs if item == label]
        if label in differences:
            marked.extend((label, i, j) for i, j in pairs)
        else:
            marked.extend((label, i, j) for i, j in pairs[1:])
    if len(marked) != beta:
        raise AssertionError("marked-pair count differs from beta")

    # P56's deterministic repair, retained here to audit the hybrid label bound.
    deleted = {i for _, i, _ in marked}
    kept = tuple(r for i, r in enumerate(residual) if i not in deleted)
    repaired = tuple(sorted(set(core) | set(kept) | {sigma - r for r in kept}))
    if sum(count >= 2 for count in pair_sums(repaired).values()) > 1:
        raise AssertionError("P56 repair is not admissible")
    t = len(deleted)
    q = p + u - t
    repaired_difference_count = q * (q + delta)
    lost_difference_count = t * k - t * (t + 1) // 2
    hybrid_support = repaired_difference_count + lost_difference_count
    if hybrid_support > span + tau:
        raise AssertionError("hybrid difference supports do not pack")

    difference_count = p * (p + delta) + c * u + u * (u - 1) // 2
    sum_count = 2 * p * (p + delta) + c * u + u * (u + 1) // 2
    if len(differences) != difference_count:
        raise AssertionError("P56 difference count failed")
    if len(residual_difference_labels) != c * u + u * (u - 1) // 2:
        raise AssertionError("residual difference labels are not injective")
    if len(residual_sum_labels) != c * u + u * (u + 1) // 2:
        raise AssertionError("residual sum labels are not injective")

    b = min(u, beta)
    bq = p + u - b
    b_label_bound = difference_count + (u - b) * (u - b + 1) // 2
    b_deletion_form = bq * (bq + delta) + b * k - b * (b + 1) // 2
    if b_label_bound != b_deletion_form:
        raise AssertionError("support/deletion forms of the P61 bound differ")
    if b_label_bound > span + tau:
        raise AssertionError("P61 label-retention bound failed")

    return {
        "A": list(a),
        "span": span,
        "k": k,
        "sigma": sigma,
        "core": list(core),
        "residual": list(residual),
        "p": p,
        "delta": delta,
        "u": u,
        "tau": tau,
        "core_span": core_span,
        "beta": beta,
        "internal_beta": internal_beta,
        "old_overlap_beta": old_overlap_beta,
        "residual_difference_count": len(residual_difference_labels),
        "collision_budget_margin": len(residual_difference_labels) - u - 2 * beta,
        "difference_slack": span - difference_count,
        "sum_slack": 2 * span - sum_count,
        "repair_t": t,
        "repair_q": q,
        "lost_difference_count": lost_difference_count,
        "hybrid_support": hybrid_support,
        "b_label_bound": b_label_bound,
        "marked": [
            [label, residual[i], residual[j]] for label, i, j in marked
        ],
    }


def smaller(record: dict, current: dict | None) -> bool:
    if current is None:
        return True
    return (record["span"], record["k"], record["A"]) < (
        current["span"],
        current["k"],
        current["A"],
    )


def census(max_n: int) -> dict:
    candidates: dict[str, Callable[[dict], bool]] = {
        "two_beta_le_sum_slack": lambda r: 2 * r["beta"] <= r["sum_slack"],
        "collision_budget": lambda r: 2 * r["beta"] + r["u"]
        <= r["residual_difference_count"],
        "beta_le_cross_count": lambda r: r["beta"]
        <= len(r["core"]) * r["u"],
        "beta_le_difference_slack": lambda r: r["beta"] <= r["difference_slack"],
        "beta_tau_le_difference_slack": lambda r: r["beta"] + r["tau"]
        <= r["difference_slack"],
        "two_beta_tau_le_sum_slack": lambda r: 2 * r["beta"] + r["tau"]
        <= r["sum_slack"],
        "beta_tau_le_total_slack": lambda r: r["beta"] + r["tau"]
        <= r["difference_slack"] + r["sum_slack"],
    }
    first_failures: dict[str, dict | None] = {name: None for name in candidates}
    minima = {
        "difference_slack_minus_beta": None,
        "sum_slack_minus_2beta": None,
        "total_slack_minus_beta_tau": None,
    }
    counts = Counter()
    profiles: dict[tuple[int, int], dict] = {}

    def consume(a: tuple[int, ...]) -> None:
        counts["admissible"] += 1
        record = analyze(a)
        if record is None:
            return
        counts["p56_records"] += 1
        b = min(record["u"], record["beta"])
        old_credit_cleared = 3 * (
            (record["k"] + record["u"] - 2 * b) ** 2 - record["k"] ** 2
        ) - 4 * record["tau"]
        two_scale_credit_base = (
            record["u"] ** 2
            - 2 * b * (record["k"] + record["u"])
            + 2 * b**2
        )
        if old_credit_cleared >= 0:
            counts["p56_zero_error_credit_holds"] += 1
        if two_scale_credit_base >= 0:
            counts["two_scale_zero_error_credit_holds"] += 1
        if old_credit_cleared < 0 <= two_scale_credit_base:
            counts["two_scale_holds_but_p56_fails"] += 1
            witness = dict(record)
            witness["old_credit_cleared"] = old_credit_cleared
            witness["two_scale_credit_base"] = two_scale_credit_base
            current = first_failures.get("p56_missed_by_two_scale")
            if smaller(witness, current):
                first_failures["p56_missed_by_two_scale"] = witness
            if 3 * record["u"] >= record["k"]:
                counts["two_scale_only_with_u_at_least_k_over_3"] += 1
                current = first_failures.get("positive_residual_two_scale_only")
                if smaller(witness, current):
                    first_failures["positive_residual_two_scale_only"] = witness
            if record["beta"] > 0:
                counts["two_scale_only_with_beta_positive"] += 1
                current = first_failures.get("blocked_two_scale_only")
                if smaller(witness, current):
                    first_failures["blocked_two_scale_only"] = witness
        profile_key = (len(record["core"]), record["u"])
        current_profile = profiles.get(profile_key)
        profile_score = (
            record["beta"],
            -record["collision_budget_margin"],
            -record["span"],
        )
        if current_profile is None or profile_score > tuple(current_profile["score"]):
            profiles[profile_key] = {
                "score": list(profile_score),
                "max_beta": record["beta"],
                "min_collision_budget_margin_at_max_beta": record[
                    "collision_budget_margin"
                ],
                "witness": record,
            }
        for name, predicate in candidates.items():
            if not predicate(record) and smaller(record, first_failures[name]):
                first_failures[name] = record
        values = {
            "difference_slack_minus_beta": record["difference_slack"]
            - record["beta"],
            "sum_slack_minus_2beta": record["sum_slack"] - 2 * record["beta"],
            "total_slack_minus_beta_tau": record["difference_slack"]
            + record["sum_slack"]
            - record["beta"]
            - record["tau"],
        }
        for name, value in values.items():
            current = minima[name]
            if current is None or (value, record["span"], record["A"]) < (
                current["value"],
                current["record"]["span"],
                current["record"]["A"],
            ):
                minima[name] = {"value": value, "record": record}

    for n in range(2, max_n + 1):
        a = [0]
        sum_counts: dict[int, int] = {0: 1}

        def try_add(x: int, repeated: int, continuation: Callable[[int], None]) -> None:
            changed: list[tuple[int, int]] = []
            new_repeated = repeated
            valid = True
            for old in (*a, x):
                label = x + old
                old_count = sum_counts.get(label, 0)
                sum_counts[label] = old_count + 1
                changed.append((label, old_count))
                if old_count == 1:
                    new_repeated += 1
                if new_repeated > 1:
                    valid = False
                    break
            if valid:
                a.append(x)
                continuation(new_repeated)
                a.pop()
            for label, old_count in reversed(changed):
                if old_count:
                    sum_counts[label] = old_count
                else:
                    del sum_counts[label]

        def recurse(x: int, repeated: int) -> None:
            if x == n - 1:
                try_add(x, repeated, lambda _: consume(tuple(a)))
                return
            recurse(x + 1, repeated)
            try_add(x, repeated, lambda value: recurse(x + 1, value))

        recurse(1, 0)

    return {
        "arithmetic": "integer only",
        "domain": f"all endpoint-normalized subsets with 2 <= N <= {max_n}",
        "counts": dict(counts),
        "first_failures": first_failures,
        "minima": minima,
        "profiles": {
            f"c={c},u={u}": profile for (c, u), profile in sorted(profiles.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=22)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p61/census_label_charges.json"),
    )
    args = parser.parse_args()
    result = census(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], separators=(",", ":")))
    for name, record in result["first_failures"].items():
        print(name, None if record is None else record["A"])


if __name__ == "__main__":
    main()
