"""Exact diagnostics for the c=25 deposit-half structural slack.

For a full-low load band [a,b] with 2*b <= N and H={T>a}, the
PREFIX-LOAD-PSC-25 deposit term is equivalent to

    N * (non_cross(H) + 2*delta_M(H))
      >= |H| * (25*|M| - N*|H| - 25*(N-a-b)).

This script scans the local census/structured battery used by Codex and
prints the active positive-RHS cases.  It is diagnostic only; Claude owns the
full-battery acceptance gate.
"""

from collections import Counter, defaultdict
from fractions import Fraction as F

from _codex_prefix_loadpsc_gate import adj_of, census_cases, structured_cases
from _satzmu_conn import struct_for_side


def deposit_rows(name, n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, T, _mu, _cyc = st
    if not M:
        return
    T = [F(t) for t in T]
    bad = {(min(u, v), max(u, v)) for u, v in M}
    edge = {(min(u, v), max(u, v)) for u, v in edges}
    levels = sorted(set([F(0)] + T))
    for idx, (a, b) in enumerate(zip(levels, levels[1:]), start=1):
        if 2 * b > n:
            continue
        H = {i for i, t in enumerate(T) if t > a}
        h = len(H)
        db = dm = non = 0
        for u in H:
            for v in range(n):
                if v in H:
                    continue
                e = (min(u, v), max(u, v))
                if e in bad:
                    dm += 1
                elif e in edge:
                    db += 1
                else:
                    non += 1
        sigma = db - dm
        lhs = F(n) * (non + 2 * dm)
        rhs = F(h) * (25 * len(M) - n * h - 25 * (n - a - b))
        margin = lhs - rhs
        yield {
            "name": name,
            "n": n,
            "m": len(M),
            "idx": idx,
            "a": a,
            "b": b,
            "h": h,
            "db": db,
            "dm": dm,
            "sigma": sigma,
            "non": non,
            "lhs": lhs,
            "rhs": rhs,
            "margin": margin,
            "active": rhs > 0,
        }


def main():
    total = active = 0
    min_margin = None
    min_active = None
    keys = Counter()
    by_key_margin = defaultdict(lambda: None)
    examples = {}

    for case in list(census_cases(11)) + list(structured_cases()):
        for row in deposit_rows(*case):
            total += 1
            if min_margin is None or row["margin"] < min_margin["margin"]:
                min_margin = row
            if row["active"]:
                active += 1
                key = (row["n"], row["m"], row["h"], row["dm"], row["non"], row["sigma"])
                keys[key] += 1
                examples.setdefault(key, row)
                if by_key_margin[key] is None or row["margin"] < by_key_margin[key]["margin"]:
                    by_key_margin[key] = row
                if min_active is None or row["margin"] < min_active["margin"]:
                    min_active = row

    print("total_full_low", total)
    print("active_rhs_positive", active)
    print("unique_active_keys", len(keys))
    print("min_margin", min_margin)
    print("min_active_margin", min_active)
    print()
    print("top_active_keys")
    for key, count in keys.most_common(40):
        ex = by_key_margin[key]
        print(count, key, "min_margin", ex["margin"], "example", ex["name"], ex["idx"], ex["a"], ex["b"])

    print()
    print("smallest_active_margins")
    rows = sorted(by_key_margin.values(), key=lambda r: r["margin"])
    for row in rows[:40]:
        print(row)


if __name__ == "__main__":
    main()
