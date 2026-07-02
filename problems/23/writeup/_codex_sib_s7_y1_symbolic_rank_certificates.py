"""Symbolic tangent certificates for observed y=1 SIB-S7 support families.

The FJ diagnostic checks augmented-rank nonstationarity at rational sample
points.  This lighter exact bridge records, for every positive-dimensional
observed family, an explicit family parametrization on which Phi has a
nonzero tangent derivative polynomial.  Thus the family is not a flat hidden
stationary stratum; any proof using these observed supports may cite a concrete
nonzero symbolic tangent witness, while the separate positivity gates close the
families themselves.

This is not the full y=1 coverage theorem: unobserved-support exclusion remains
separate.
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


def nonzero_num(expr: sp.Expr) -> sp.Expr:
    num, _den = sp.together(expr).as_numer_denom()
    return sp.factor(num)


def poly_terms(expr: sp.Expr, params: tuple[sp.Symbol, ...]) -> int:
    return len(sp.Poly(sp.expand(expr), *params).terms())


def family_substitution(inv, name: str):
    a, b, c, d, e, f, x, u, v = inv.VARS
    if name == "ALL_TIGHT":
        T = sp.symbols("T", nonnegative=True)
        t = 1 + T
        return (T,), {a: t + 1 - 1 / t, b: 1, c: t, d: 1, e: t, f: 1, x: t, u: 1, v: t}
    if name == "HIGH_A":
        T = sp.symbols("T", nonnegative=True)
        t = 1 + T
        return (T,), {a: 1, b: 1, c: t, d: 1, e: t, f: t, x: t, u: 1, v: t}
    if name == "XQ_A":
        X, R = sp.symbols("X R", nonnegative=True)
        xx = 2 + X
        cc = xx - 1 + R
        return (X, R), {
            x: xx,
            u: 1,
            v: xx - 1,
            f: 1,
            c: cc,
            e: cc,
            b: xx + 1 - cc,
            d: xx + 1 - cc,
            a: (xx * xx - 2) / cc,
        }
    if name == "XQ_B":
        X = sp.symbols("X", nonnegative=True)
        xx = 2 + X
        return (X,), {x: xx, u: 1, v: xx - 1, a: xx + 1, b: 2, c: xx - 1, d: 1, e: xx - 1, f: 1}
    if name == "U1_S7_HIGH":
        B0 = sp.symbols("B0", nonnegative=True)
        return (B0,), {a: 1, b: 1 + B0, c: 1, d: 1, e: 1, f: 1, x: 1, u: 1, v: 1}
    if name == "XQ_S5_HIGH":
        X = sp.symbols("X", nonnegative=True)
        xx = 2 + X
        return (X,), {
            x: xx,
            u: 1,
            v: xx - 1,
            a: 1,
            b: 2,
            c: xx - 1,
            d: 2,
            e: xx - 1,
            f: xx * xx / (xx + 1),
        }
    raise KeyError(name)


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

    checked: list[str] = []
    for row in inv.SUPPORTS:
        name = row["name"]
        if name == "ALL_ONES":
            continue
        params, subs = family_substitution(inv, name)
        phi_fam = sp.together(Phi.subs(subs))

        witnesses: list[tuple[int, sp.Symbol, sp.Expr]] = []
        for param in params:
            deriv_num = nonzero_num(sp.diff(phi_fam, param))
            if deriv_num != 0:
                witnesses.append((poly_terms(deriv_num, params), param, deriv_num))
        assert witnesses, name
        _terms, param, witness = min(witnesses, key=lambda item: item[0])
        assert sp.Poly(sp.expand(witness), *params) != 0
        print(
            "TANGENT-CERT",
            name,
            f"params={','.join(str(p) for p in params)}",
            f"direction={param}",
            f"num_terms={poly_terms(witness, params)}",
            f"degree={sp.Poly(sp.expand(witness), *params).total_degree()}",
        )
        checked.append(name)

    assert checked == ["ALL_TIGHT", "HIGH_A", "XQ_A", "XQ_B", "U1_S7_HIGH", "XQ_S5_HIGH"]
    print("PASS y=1 observed support families have symbolic nonflat tangent certificates")


if __name__ == "__main__":
    main()
