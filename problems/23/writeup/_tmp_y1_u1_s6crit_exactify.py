from __future__ import annotations

import sympy as sp


def main() -> None:
    b, t = sp.symbols("b t", positive=True)
    d = f = y = u = sp.Integer(1)
    c = e = v = t
    x = b + t - 1
    q = 1 + t
    a = sp.factor(((b + t - 1) * (t + 1) - 1) / t)

    S = a + b + c + d + e + f
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    M = a * c + d * f + e * f
    m = x * q + v
    N = S + x + y + u + v
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)
    dPhi = 4 * N * (1 - (M + 1) / q ** 2) - 75 * (-A / Z + B / (e * Y))

    print("a =", a)
    print("m-M =", sp.factor(m - M))
    print("Y =", sp.factor(Y))
    print("Z =", sp.factor(Z))
    print("Phi num factor:")
    print(sp.factor(sp.together(Phi).as_numer_denom()[0]))
    print("crit factor:")
    crit = sp.factor(sp.together(dPhi).as_numer_denom()[0])
    print(crit)
    print("crit degree", sp.Poly(crit, b, t).total_degree())
    print("resultant Phi/crit wrt b:")
    res = sp.factor(sp.resultant(sp.together(Phi).as_numer_denom()[0], crit, b))
    print(res)


if __name__ == "__main__":
    main()
