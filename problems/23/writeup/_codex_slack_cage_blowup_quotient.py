"""Quotient gate for Slack-CAGE on balanced odd-cycle blowups.

This checks the same inequality as _codex_slack_cage_gate.py on rowset
subsets of C_c[t] with the natural maximum cut:

    D_Q(U) <= |U| + (delta_B(U)-delta_M(U)) + eta,
    eta = N^2/25 - |M|.

For balanced C_c[t], every bad row Q is equivalent.  A rowset subset U is
determined, relative to a fixed canonical Q, by:

  * counts u_i of selected vertices in each cycle part, and
  * flags q_i telling whether Q's vertex in part i lies in U.

The quotient avoids enumerating all t^c rows and all concrete row intervals.
"""

import argparse
from fractions import Fraction as F


def boundary_between(a, b, t):
    return a * (t - b) + (t - a) * b


def sigma(counts, t):
    c = len(counts)
    total = 0
    for i in range(c - 1):
        total += boundary_between(counts[i], counts[i + 1], t)
    total -= boundary_between(counts[c - 1], counts[0], t)
    return total


def dq(counts, qin, t):
    """Exact D_Q(U) for balanced C_c[t] in the canonical bad-row class."""
    c = len(counts)
    den = t ** (c - 2)
    mid_prod = 1
    for i in range(1, c - 1):
        mid_prod *= counts[i]

    total = 0
    if mid_prod:
        if qin[0]:
            total += counts[c - 1] * mid_prod
        if qin[c - 1]:
            total += counts[0] * mid_prod

        endpoints = counts[0] * counts[c - 1]
        if endpoints:
            for i in range(1, c - 1):
                if qin[i] and counts[i]:
                    total += endpoints * (mid_prod // counts[i])

    return F(total, den)


def rowset_patterns(c, t):
    yield "empty", [0] * c, [False] * c
    yield "V", [t] * c, [True] * c

    for lo in range(c):
        for hi in range(lo, c):
            length = hi - lo + 1
            max_mask = 1 << length if t > 1 else 1
            for mask in range(max_mask):
                counts = [0] * c
                qin = [False] * c
                for j, part in enumerate(range(lo, hi + 1)):
                    counts[part] = 1
                    qin[part] = bool((mask >> j) & 1) if t > 1 else True
                yield f"I[{lo},{hi}]/qmask={mask}", counts, qin


def concrete_rowset_count(c, t):
    return 2 + sum((c - length + 1) * (t ** length) for length in range(1, c + 1))


def check(c_values, t_values):
    acc = {
        "quotient_checks": 0,
        "expanded_checks": 0,
        "violations": 0,
        "first": None,
        "min": None,
    }

    for c in c_values:
        for t in t_values:
            n = c * t
            m = t * t
            eta = F(n * n, 25) - m
            expanded_per_q = concrete_rowset_count(c, t)
            expanded_rows = t ** c
            patterns = list(rowset_patterns(c, t))
            acc["expanded_checks"] += expanded_rows * expanded_per_q

            for label, counts, qin in patterns:
                lhs = dq(counts, qin, t)
                rhs = F(sum(counts) + sigma(counts, t)) + eta
                margin = rhs - lhs
                acc["quotient_checks"] += 1
                rec = (margin, c, t, label, tuple(counts), tuple(qin), lhs, rhs, eta)
                if acc["min"] is None or margin < acc["min"][0]:
                    acc["min"] = rec
                if margin < 0:
                    acc["violations"] += 1
                    if acc["first"] is None:
                        acc["first"] = rec

    return acc


def parse_ints(text):
    return [int(x) for x in text.split(",") if x]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", default="5,7,9")
    ap.add_argument("--t", default="1,2,3")
    args = ap.parse_args()

    acc = check(parse_ints(args.cycles), parse_ints(args.t))
    print("=== Slack-CAGE balanced blowup quotient gate ===")
    print("quotient_checks:", acc["quotient_checks"])
    print("expanded_checks_represented:", acc["expanded_checks"])
    print("violations:", acc["violations"])
    print("min_margin:", acc["min"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "HOLDS" if acc["violations"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
