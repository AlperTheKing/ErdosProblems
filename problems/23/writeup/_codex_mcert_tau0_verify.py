"""Exact tau_0 M-certificate verifier.

This implements the first M-cert class from
MCERTS_FORMAT_FIRSTCLASS_GPTPRO.md:

    tau_0 = V2 with L={3,5}, R={4,6}, attachment a true twin of bag 8.

For the equality seed I?BD@g]Qo, side 0001111000, active row
Q*=(7,5,8,6,9), and the eleven tau_0 row types R_j, it verifies

    P_j(w,z) = D0(w,z) * (z + I_Q*(w) - I_Rj(w0..w7,w8+z,w9))

has no denominator and has all coefficients nonnegative in
Z[w0..w9,z].

No floating point arithmetic is used.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path

import sympy as sp

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import (
        EQ,
        b_edges,
        edges_of,
        m_edges,
        shortest_paths,
    )


SIDE = "0001111000"
ACTIVE_ROW = (7, 5, 8, 6, 9)
ROWS = [
    (1, 5, 0, 6, 9),
    (1, 5, 8, 4, 9),
    (1, 5, 8, 6, 9),
    (7, 5, 0, 6, 2),
    (7, 5, 8, 6, 2),
    (7, 3, 8, 6, 2),
    (7, 5, 0, 6, 9),
    (7, 5, 8, 4, 9),
    (7, 5, 8, 6, 9),
    (7, 3, 8, 4, 9),
    (7, 3, 8, 6, 9),
]


def path_weight(path: tuple[int, ...], weights: tuple[sp.Expr, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for v in path[1:-1]:
        out *= weights[v]
    return out


def row_overlap_expr(
    row: tuple[int, ...],
    weights: tuple[sp.Expr, ...],
    paths_by_bad: dict[tuple[int, int], list[tuple[int, ...]]],
) -> sp.Expr:
    """Weighted quotient row-overlap I(row).

    This mirrors _codex_active5_symbolic_margin.symbolic_margin, but accepts
    an explicit weight tuple so the tau_0 twin substitution w8 -> w8+z can be
    applied without rebuilding graph data.
    """

    row_set = set(row)
    total = sp.Integer(0)

    for a, b in sorted(paths_by_bad):
        paths = paths_by_bad[(a, b)]
        denom = sp.Integer(0)
        inner = sp.Integer(0)

        for path in paths:
            wp = path_weight(path, weights)
            denom += wp
            for v in path[1:-1]:
                if v in row_set:
                    inner += wp / weights[v]

        endpoint = sp.Integer(0)
        if a in row_set:
            endpoint += weights[b]
        if b in row_set:
            endpoint += weights[a]

        total += endpoint + weights[a] * weights[b] * inner / denom

    return sp.factor(total)


def tau0_denominator(weights: tuple[sp.Expr, ...], z: sp.Symbol) -> sp.Expr:
    w = weights
    t0 = w[8]
    tz = w[8] + z

    def A(t: sp.Expr) -> sp.Expr:
        return w[0] * w[6] + (w[4] + w[6]) * t

    def B(t: sp.Expr) -> sp.Expr:
        return w[0] * w[5] + (w[3] + w[5]) * t

    def C(t: sp.Expr) -> sp.Expr:
        return w[0] * w[5] * w[6] + t * (
            w[3] * w[4] + w[3] * w[6] + w[4] * w[5] + w[5] * w[6]
        )

    return sp.factor(w[5] * w[6] * A(t0) * B(t0) * C(t0) * A(tz) * B(tz) * C(tz))


def monomial_to_string(monom: tuple[int, ...], names: tuple[str, ...]) -> str:
    parts = []
    for name, power in zip(names, monom):
        if power == 0:
            continue
        if power == 1:
            parts.append(name)
        else:
            parts.append(f"{name}^{power}")
    return "*".join(parts) if parts else "1"


def verify(summary_path: Path | None = None, dump_terms: bool = False) -> dict:
    n, edges = edges_of(EQ)
    if n != 10:
        raise RuntimeError(f"expected 10 bags, got {n}")

    side = tuple(int(c) for c in SIDE)
    B = b_edges(edges, side)
    M = sorted(m_edges(edges, side))
    if M != [(1, 9), (2, 7), (7, 9)]:
        raise RuntimeError(f"unexpected EQ bad edges: {M}")

    paths_by_bad = {edge: shortest_paths(n, B, edge[0], edge[1]) for edge in M}
    for edge, paths in paths_by_bad.items():
        if not paths:
            raise RuntimeError(f"bad edge {edge} has no shortest B-row")

    w = sp.symbols("w0:10")
    z = sp.Symbol("z")
    variables = (*w, z)
    variable_names = tuple(str(v) for v in variables)
    weights = tuple(w)
    weights_z = tuple(w[i] + z if i == 8 else w[i] for i in range(10))

    active_I = row_overlap_expr(ACTIVE_ROW, weights, paths_by_bad)
    D0 = tau0_denominator(weights, z)

    rows_summary = []
    all_ok = True

    for index, row in enumerate(ROWS):
        row_I_z = row_overlap_expr(row, weights_z, paths_by_bad)
        expression = sp.together(D0 * (z + active_I - row_I_z))
        numerator, denominator = expression.as_numer_denom()
        denominator = sp.factor(denominator)
        cleared = denominator == 1
        poly = sp.Poly(sp.expand(numerator), *variables, domain=sp.ZZ)
        terms = poly.terms()
        coeffs = [coeff for _monom, coeff in terms]
        negative = [(monom, coeff) for monom, coeff in terms if coeff < 0]

        row_ok = cleared and not negative
        all_ok = all_ok and row_ok
        min_coeff = min(coeffs) if coeffs else sp.Integer(0)
        max_coeff = max(coeffs) if coeffs else sp.Integer(0)

        record = {
            "index": index,
            "row": list(row),
            "denominator_cleared": cleared,
            "denominator": str(denominator),
            "terms": len(terms),
            "total_degree": poly.total_degree(),
            "negative_coeffs": len(negative),
            "min_coeff": str(min_coeff),
            "max_coeff": str(max_coeff),
        }
        if dump_terms:
            record["coefficients"] = {
                monomial_to_string(monom, variable_names): str(coeff)
                for monom, coeff in terms
                if coeff != 0
            }
        if negative:
            record["first_negative"] = {
                "monomial": monomial_to_string(negative[0][0], variable_names),
                "coeff": str(negative[0][1]),
            }
        rows_summary.append(record)

    summary = {
        "verdict": "PASS" if all_ok else "FAIL",
        "graph": EQ,
        "side": SIDE,
        "active_row": list(ACTIVE_ROW),
        "bad_edges": [list(edge) for edge in M],
        "row_count": len(ROWS),
        "all_denominators_cleared": all(row["denominator_cleared"] for row in rows_summary),
        "all_coefficients_nonnegative": all(row["negative_coeffs"] == 0 for row in rows_summary),
        "D0": str(D0),
        "rows": rows_summary,
    }

    if summary_path is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=Path("tmp/mcert_tau0_v1_summary.json"))
    parser.add_argument("--dump-terms", action="store_true")
    args = parser.parse_args()

    summary = verify(args.summary, dump_terms=args.dump_terms)
    print(
        "PASS" if summary["verdict"] == "PASS" else "FAIL",
        "tau0",
        "rows",
        summary["row_count"],
        "denom_cleared",
        summary["all_denominators_cleared"],
        "coeff_nonneg",
        summary["all_coefficients_nonnegative"],
        "summary",
        args.summary,
    )
    if summary["verdict"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
