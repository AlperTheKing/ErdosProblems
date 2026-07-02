"""Exact tangent-stationarity diagnostic for observed y=1 support families.

This is not a closure certificate.  It records a useful FJ-coverage fact:
the generic rational sample on every positive-dimensional observed support is
not a stationary point of Phi along that support.  Therefore a true FJ
coverage proof must combine the support inventory with the one-step
neighborhood closures; it cannot close by declaring the generic support
families themselves stationary.
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


def main() -> None:
    inv = load_inventory()
    a, b, c, d, e, f, x, u, v = inv.VARS
    y = sp.Integer(1)
    m = x * u + x * v + v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - (a + b + c + d + e + f))
    grad = [sp.diff(Phi, var) for var in inv.VARS]

    stationary = []
    nonstationary = []
    for row in inv.SUPPORTS:
        eqs = inv.unique_equations(row)
        sample = row["sample"]
        J = sp.Matrix([[sp.diff(expr, var) for var in inv.VARS] for expr in eqs])
        grad_row = sp.Matrix([[g.subs(sample) for g in grad]])
        rank = J.subs(sample).rank()
        aug_rank = J.subs(sample).col_join(grad_row).rank()
        if aug_rank == rank:
            stationary.append(row["name"])
        else:
            nonstationary.append(row["name"])
        print(f"FJ-DIAG {row['name']}: rank={rank} aug_rank={aug_rank}")

    assert stationary == ["ALL_ONES"], stationary
    assert sorted(nonstationary) == sorted(
        ["ALL_TIGHT", "HIGH_A", "XQ_A", "XQ_B", "U1_S7_HIGH", "XQ_S5_HIGH"]
    )
    print("PASS y=1 observed supports are generically nonstationary except ALL_ONES")


if __name__ == "__main__":
    main()
