"""Safe implied-slack closure for SIB-S7 y=1,u=1 terminal supports.

This is a targeting/exact-pruning artifact.  Starting from the still-unobserved
u1 terminal supports produced by the monomial-hit filter, it repeatedly:

* applies the existing exact lower-bound propagation;
* adds any inactive slack label whose polynomial is identically zero after the
  currently forced lower-bound substitutions.

The second step is a safe logical closure: if the current lower labels force a
slack to vanish for all remaining variables, the support lies on that slack
face and can be compared against the observed bases with that label included.
"""

from __future__ import annotations

from collections import Counter

import sympy as sp

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_far_support_linear_filter as lin
import _codex_sib_s7_y1_terminal_rank_profile as rankprof


def forced_zero_slacks(support: frozenset[str]) -> frozenset[str]:
    fixed_labels = frozenset(label for label in support if label in lin.LOWER_LABEL_TO_VAR)
    out: set[str] = set()
    for label in lin.SLACK_LABELS:
        if label in support:
            continue
        poly, _remaining = lin.shifted_poly(lin.EQUATION_EXPR[label], fixed_labels)
        if poly is None:
            value = sp.factor(lin.EQUATION_EXPR[label].subs({lin.LOWER_LABEL_TO_VAR[x]: 1 for x in fixed_labels}))
            if value == 0:
                out.add(label)
        elif poly.is_zero:
            out.add(label)
    return frozenset(out)


def close_support(branch: str, cap: str, support_tuple: tuple[str, ...]) -> tuple[str, frozenset[str]]:
    support = frozenset(support_tuple)
    while True:
        status, closure = lin.propagate(branch, cap, support)
        if status == "contradiction":
            return "contradiction", closure
        implied = forced_zero_slacks(closure)
        next_support = closure | implied
        if next_support == support:
            return "alive", closure
        support = next_support


def main() -> None:
    states = sorted(rankprof.collect_unique_still("u1", None))
    assert len(states) == 20152

    status_counts: Counter[str] = Counter()
    by_cap: Counter[tuple[str, str]] = Counter()
    growth: Counter[int] = Counter()
    implied_slack_freq: Counter[str] = Counter()
    examples: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {}
    still_unique: set[tuple[str, str, tuple[str, ...]]] = set()

    for branch, cap, support_tuple in states:
        start = frozenset(support_tuple)
        status, closure = close_support(branch, cap, support_tuple)
        if status == "contradiction":
            cls = "contradiction"
        elif lin.observed_closure_class(branch, cap, closure) == "closes_to_observed_basis":
            cls = "closes_to_observed_basis"
        else:
            cls = "still_unobserved"
            still_unique.add((branch, cap, tuple(sorted(closure))))

        added = closure - start
        for label in added:
            if label in lin.SLACK_LABELS:
                implied_slack_freq[label] += 1
        growth[len(added)] += 1
        status_counts[cls] += 1
        by_cap[(cap, cls)] += 1
        examples.setdefault(cls, (cap, support_tuple, tuple(sorted(closure))))

    print("U1-IMPLIED-SLACK " + " ".join(f"{key}={status_counts[key]}" for key in sorted(status_counts)))
    print(f"U1-IMPLIED-SLACK-STILL-UNIQUE={len(still_unique)}")
    print("U1-IMPLIED-SLACK-GROWTH " + " ".join(f"{key}:{growth[key]}" for key in sorted(growth)))
    print("U1-IMPLIED-SLACK-FREQ " + " ".join(f"{label}:{implied_slack_freq[label]}" for label in sorted(lin.SLACK_LABELS)))
    for cap in census.CAPS:
        pieces = []
        for cls in ("contradiction", "closes_to_observed_basis", "still_unobserved"):
            pieces.append(f"{cls}={by_cap[(cap, cls)]}")
        print(f"U1-IMPLIED-SLACK-CAP cap={cap} " + " ".join(pieces))
    for cls, (cap, support, closure) in sorted(examples.items()):
        print(f"U1-IMPLIED-SLACK-EXAMPLE {cls} cap={cap} support={','.join(support)} closure={','.join(closure)}")
    print("PASS u1 terminal supports closed under forced-zero slack labels")


if __name__ == "__main__":
    main()
