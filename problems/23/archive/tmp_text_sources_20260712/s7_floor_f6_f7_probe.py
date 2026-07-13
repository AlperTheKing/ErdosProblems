from __future__ import annotations

import sympy as sp


def poly_stats(poly: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> dict:
    P = sp.Poly(sp.expand(poly), *vars_)
    coeffs = P.coeffs()
    neg = [(mon, coeff) for mon, coeff in zip(P.monoms(), coeffs) if coeff < 0]
    return {
        "terms": len(coeffs),
        "degree": P.total_degree(),
        "min_coeff": min(coeffs) if coeffs else 0,
        "negative_coeffs": len(neg),
        "first_negative": neg[:8],
    }


def f6_target():
    C, E, U, X, Y0, d, L = sp.symbols("C E U X Y0 d L")
    c = 1 + C
    e = c + E
    u = 1 + U
    x = 1 + X
    y = 1 + Y0
    P = x + y
    q = u + e
    M = e * P + u * x
    D = q + d
    R = D + L
    T = R + 1 + (M - c) / D
    N = T + D + P + q
    Phi = (
        2 * N**2
        + 4 * u * N * x / e
        - 50 * M
        - 75 * M / e
        + 75 * D
        + 75 * T * L / (M + L)
        - 15
    )
    target = sp.factor(e * D**2 * (M + L) * Phi)
    return target, (C, E, U, X, Y0, d, L)


def f7_target():
    E, C, U, X, Y0, d, L = sp.symbols("E C U X Y0 d L")
    e = 1 + E
    c = e + C
    u = 1 + U
    x = 1 + X
    y = 1 + Y0
    P = x + y
    q = u + e
    M = e * P + u * x
    D = q + d
    R = D + L
    gap = C + L
    T = R + 1 + (M - e) / D
    N = T + D + P + q
    Phi = (
        2 * N**2
        + 4 * u * N * x / e
        - 50 * M
        - 75 * M / e
        + 75 * D
        + 75 * T * gap / (M + gap)
        - 15
    )
    target = sp.factor(e * D**2 * (M + gap) * Phi)
    return target, (E, C, U, X, Y0, d, L)


if __name__ == "__main__":
    for name, builder in (("F6", f6_target), ("F7", f7_target)):
        target, vars_ = builder()
        stats = poly_stats(target, vars_)
        print(name, stats)

def eval_f6_candidate(c, e, u, x, y, D, R):
    P = x + y
    q = u + e
    M = e * P + u * x
    L = R - D
    T = R + 1 + sp.Rational(M - c, D)
    N = T + D + P + q
    return (
        2 * N**2
        + sp.Rational(4 * u * x, e) * N
        - 50 * M
        - sp.Rational(75 * M, e)
        + 75 * D
        + sp.Rational(75 * T * L, M + L)
        - 15
    )


def eval_f7_candidate(c, e, u, x, y, D, R):
    P = x + y
    q = u + e
    M = e * P + u * x
    gap = (c - e) + (R - D)
    T = R + 1 + sp.Rational(M - e, D)
    N = T + D + P + q
    return (
        2 * N**2
        + sp.Rational(4 * u * x, e) * N
        - 50 * M
        - sp.Rational(75 * M, e)
        + 75 * D
        + sp.Rational(75 * T * gap, M + gap)
        - 15
    )


if __name__ == "__main__":
    for name, evaluator, extra in (
        ("F6", eval_f6_candidate, lambda c, e, u, x, y, D, R: e >= c and R >= D),
        ("F7", eval_f7_candidate, lambda c, e, u, x, y, D, R: c >= e and R >= D),
    ):
        worst = None
        count = 0
        for c in range(1, 7):
            for e in range(1, 7):
                for u in range(1, 7):
                    for x in range(1, 7):
                        for y in range(1, 7):
                            P = x + y
                            q = u + e
                            for D in range(q, 13):
                                for R in range(max(D, P), 13):
                                    if not extra(c, e, u, x, y, D, R):
                                        continue
                                    count += 1
                                    val = evaluator(c, e, u, x, y, D, R)
                                    if worst is None or val < worst[0]:
                                        worst = (val, (c, e, u, x, y, D, R))
        print(name, "domain_points", count, "worst", worst)
