"""Symbolic PMS margin for the N=10 equality-atom quotient.

The output is intentionally semi-factored: it keeps the three shortest-path
partition functions as denominators instead of expanding a huge expression.
"""

import sympy as sp

import _codex_ocpms_weight_formula as wf


def main():
    w = sp.symbols("w0:10", positive=True)
    row = set(wf.BASE_ROW)
    terms = []
    for a, b in wf.m_edges():
        paths = wf.base_shortest_paths(a, b)
        z = 0
        inner = 0
        for path in paths:
            wp = sp.Integer(1)
            for v in path[1:-1]:
                wp *= w[v]
            z += wp
            for v in path[1:-1]:
                if v in row:
                    inner += wp / w[v]

        endpoint = 0
        if a in row:
            endpoint += w[b]
        if b in row:
            endpoint += w[a]

        term = endpoint + w[a] * w[b] * inner / z
        terms.append(((a, b), sp.factor(z), sp.factor(inner), sp.factor(term)))

    i_expr = sp.factor(sum(term for _, _, _, term in terms))
    n_expr = sum(w)
    m_expr = sum(w[a] * w[b] for a, b in wf.m_edges())
    margin = sp.factor(2 * (n_expr**2 - 25 * m_expr) - 75 * (i_expr - n_expr))
    numer = sp.factor(sp.together(margin).as_numer_denom()[0])
    denom = sp.factor(sp.together(margin).as_numer_denom()[1])

    print("Terms:")
    for edge, z, inner, term in terms:
        print(f"BAD {edge}:")
        print("  Z     =", z)
        print("  inner =", sp.factor(inner))
        print("  term  =", term)
    print()
    print("I =", i_expr)
    print("m =", m_expr)
    print("margin = 2*(N^2-25m)-75*(I-N)")
    print("denom =", denom)
    print("numer total degree =", sp.Poly(numer, *w).total_degree())
    print("numer terms =", len(sp.Poly(numer, *w).terms()))
    print("numer factor =", sp.factor(numer))


if __name__ == "__main__":
    main()
