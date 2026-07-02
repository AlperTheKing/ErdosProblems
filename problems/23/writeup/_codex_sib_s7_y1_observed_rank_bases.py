"""Exact Jacobian rank bases for observed y=1 SIB-S7 supports.

This is a coverage-support artifact, not the full unobserved-support exclusion.
For each observed family in `_codex_sib_s7_y1_fj_support_inventory.py`, it
finds a small subset of the active labels whose equations, together with the
fixed branch/cap equations, have the same Jacobian rank at the exact rational
family sample as the full observed support.

The point is bookkeeping for the next exhaustive FJ step: every observed family
has a rank basis of size at most seven in the seven-variable branch/cap charts.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
INV_PATH = HERE / "_codex_sib_s7_y1_fj_support_inventory.py"


EXPECTED_BASES = {
    "ALL_TIGHT": ("b1", "d1", "f1", "s1", "s3", "s5"),
    "HIGH_A": ("a1", "b1", "d1", "s1", "s3", "s5"),
    "XQ_A": ("f1", "s3", "s5", "s6", "u1"),
    "XQ_B": ("d1", "f1", "s1", "s2", "s3", "s7"),
    "U1_S7_HIGH": ("a1", "c1", "d1", "e1", "f1", "s1"),
    "XQ_S5_HIGH": ("a1", "s1", "s3", "s4", "s6", "u1"),
    "ALL_ONES": ("a1", "b1", "c1", "d1", "e1", "f1", "s1"),
}


def load_inventory():
    spec = importlib.util.spec_from_file_location("inv", INV_PATH)
    inv = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(inv)
    return inv


def rank_for(inv, row: dict, labels: tuple[str, ...]) -> int:
    probe = {"branch": row["branch"], "cap": row["cap"], "active": labels}
    eqs = inv.unique_equations(probe)
    sample = row["sample"]
    for expr in eqs:
        assert sp.factor(expr.subs(sample)) == 0, (row["name"], labels, expr)
    jac = sp.Matrix([[sp.diff(expr, var) for var in inv.VARS] for expr in eqs])
    return jac.subs(sample).rank()


def greedy_basis(inv, row: dict) -> tuple[str, ...]:
    labels = tuple(row["active"])
    target = rank_for(inv, row, labels)
    basis: list[str] = []
    current = rank_for(inv, row, tuple(basis))
    for label in labels:
        trial = tuple([*basis, label])
        trial_rank = rank_for(inv, row, trial)
        if trial_rank > current:
            basis.append(label)
            current = trial_rank
        if current == target:
            break
    assert current == target, row["name"]
    return tuple(basis)


def main() -> None:
    inv = load_inventory()
    seen: list[str] = []
    for row in inv.SUPPORTS:
        name = row["name"]
        basis = greedy_basis(inv, row)
        assert basis == EXPECTED_BASES[name], (name, basis, EXPECTED_BASES[name])
        full_rank = rank_for(inv, row, tuple(row["active"]))
        basis_rank = rank_for(inv, row, basis)
        assert basis_rank == full_rank == row["rank"], name
        assert len(basis) <= 7, name
        print(
            "RANK-BASIS",
            name,
            f"rank={full_rank}",
            f"basis_size={len(basis)}",
            "basis=" + ",".join(basis),
        )
        seen.append(name)
    assert seen == list(EXPECTED_BASES)
    print("PASS y=1 observed support rank bases have size at most seven")


if __name__ == "__main__":
    main()