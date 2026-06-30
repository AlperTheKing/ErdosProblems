"""Inspect shifted coefficients of the corrected seven-cut PMS numerator."""

import sympy as sp


def main():
    w = sp.symbols("w0:10")
    x = sp.symbols("x0:10")
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w

    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    i27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    i19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z79 = (
        w0 * w5 * w6
        + w3 * w4 * w8
        + w3 * w6 * w8
        + w4 * w5 * w8
        + w5 * w6 * w8
    )
    i79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    n = sum(w)
    m = w1 * w9 + w2 * w7 + w7 * w9
    endpoint = w1 + w2 + w7 + w9
    den = z27 * z19 * z79
    numer = (2 * (n * n - 25 * m) - 75 * (endpoint - n)) * den
    numer -= 75 * w2 * w7 * i27 * z19 * z79
    numer -= 75 * w1 * w9 * i19 * z27 * z79
    numer -= 75 * w7 * w9 * i79 * z27 * z19

    shifted = sp.Poly(sp.expand(numer.subs({w[i]: x[i] + 1 for i in range(10)})), *x)
    coeffs = shifted.terms()
    neg = [(monom, coeff) for monom, coeff in coeffs if coeff < 0]
    zero_const = shifted.coeff_monomial(tuple([0] * 10))
    print("terms", len(coeffs), "negative", len(neg), "constant", zero_const)
    print("min_coeff", min(c for _, c in coeffs))
    print("first negatives:")
    for monom, coeff in neg[:40]:
        print(monom, coeff)


if __name__ == "__main__":
    main()
