"""Rank bases for all observed y=1 branch/cap clusters.

This extends `_codex_sib_s7_y1_observed_rank_bases.py`, which covers the
support families in `_codex_sib_s7_y1_fj_support_inventory.py`.  The numerical
observed-coverage scan also sees the all-tight family in several other
branch/cap charts, plus the s2 and s3 critical survivor families.  This script
records exact Jacobian rank bases for that full observed cluster list.

It is still a bookkeeping artifact for the coverage theorem, not an
unobserved-support exclusion.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
INV_PATH = HERE / "_codex_sib_s7_y1_fj_support_inventory.py"


def load_inventory():
    spec = importlib.util.spec_from_file_location("inv", INV_PATH)
    inv = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(inv)
    return inv


def rank_for(inv, branch: str, cap: str, labels: tuple[str, ...], sample: dict) -> int:
    eqs = inv.unique_equations({"branch": branch, "cap": cap, "active": labels})
    for expr in eqs:
        assert sp.factor(expr.subs(sample)) == 0, (branch, cap, labels, expr)
    jac = sp.Matrix([[sp.diff(expr, var) for var in inv.VARS] for expr in eqs])
    return jac.subs(sample).rank()


def main() -> None:
    inv = load_inventory()
    a, b, c, d, e, f, x, u, v = inv.VARS
    central = {a: sp.Rational(5, 2), b: 1, c: 2, d: 1, e: 2, f: 1, x: 2, u: 1, v: 2}
    high_a = {a: 1, b: 1, c: 2, d: 1, e: 2, f: 2, x: 2, u: 1, v: 2}
    s3_surv = {a: sp.Rational(3, 2), b: 1, c: 3, d: 3, e: 2, f: 1, x: 3, u: 1, v: 1}
    xq_a = {a: sp.Rational(7, 2), b: 2, c: 2, d: 2, e: 2, f: 1, x: 3, u: 1, v: 2}
    xq_s5_high = {a: 1, b: 2, c: 2, d: 2, e: 2, f: sp.Rational(9, 4), x: 3, u: 1, v: 2}

    rows = [
        ("ALL_TIGHT", "s2", "s4", ("b1", "d1", "f1", "s1", "s3", "s5"), 8, central),
        ("ALL_TIGHT", "s2", "s5", ("b1", "d1", "f1", "s1", "s3", "s4"), 8, central),
        ("ALL_TIGHT", "s2", "s6", ("b1", "d1", "f1", "s1", "s3", "s4"), 8, central),
        ("ALL_TIGHT", "s3", "s4", ("b1", "d1", "f1", "s1", "s2", "s5"), 8, central),
        ("ALL_TIGHT", "s3", "s5", ("b1", "d1", "f1", "s1", "s2", "s4"), 8, central),
        ("ALL_TIGHT", "u1", "s4", ("b1", "d1", "f1", "s1", "s3", "s5"), 8, central),
        ("ALL_TIGHT", "u1", "s5", ("b1", "d1", "f1", "s1", "s3", "s4"), 8, central),
        ("ALL_TIGHT", "u1", "s6", ("b1", "d1", "f1", "s1", "s3", "s4"), 8, central),
        ("HIGH_A", "u1", "s5", ("a1", "b1", "d1", "s1", "s3", "s4"), 8, high_a),
        ("S2_SURV", "s2", "s4", ("b1", "f1", "s1", "s5"), 6, central),
        ("S2_SURV", "s2", "s7", ("b1", "f1", "s1", "s5"), 6, central),
        ("S3_SURV", "s3", "s5", ("b1", "f1", "u1", "v1"), 6, s3_surv),
        ("XQ_A", "xq", "s5", ("f1", "s3", "s5", "s6", "u1"), 6, xq_a),
        ("XQ_S5_HIGH", "xq", "s5", ("a1", "s1", "s3", "s4", "s6", "u1"), 8, xq_s5_high),
    ]

    seen = set()
    for name, branch, cap, basis, expected_rank, sample in rows:
        assert len(basis) <= 7, (name, branch, cap, basis)
        rank = rank_for(inv, branch, cap, basis, sample)
        assert rank == expected_rank, (name, branch, cap, rank, expected_rank)
        key = (name, branch, cap, basis)
        assert key not in seen
        seen.add(key)
        print(f"CLUSTER-RANK-BASIS {name} branch={branch} cap={cap} rank={rank} size={len(basis)} basis={','.join(basis)}")

    assert len(seen) == len(rows)
    print("PASS y=1 observed scan clusters have rank bases of size at most seven")


if __name__ == "__main__":
    main()