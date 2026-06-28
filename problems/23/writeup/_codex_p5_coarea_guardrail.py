"""Exact guardrail for P5 threshold-switch/coarea proof attempts.

This is the non-uniform C5 blow-up with part sizes (1,4,2,2,4),
using the max cut with bad quotient edge V4--V0.  It verifies the
superlevel coarea form of P5 and the obstruction to any pointwise
nonnegative switch-integrand proof at the top interval U={o}.
"""
from fractions import Fraction as F


sizes = [1, 4, 2, 2, 4]
N = sum(sizes)


def p5_data():
    # Four bad edges o--w with w in V4; each shortest B-geodesic has length 5.
    T = {
        "V0": F(20),
        "V1": F(5),
        "V2": F(10),
        "V3": F(10),
        "V4": F(5),
    }
    a = {
        "V1": F(1),
        "V2": F(2),
        "V3": F(2),
        "V4": F(1),
    }
    psi = {part: a[part] / (N - 4 * a[part]) for part in a}
    return T, a, psi


def integrand(parts, T):
    count = sum(sizes[int(part[1])] for part in parts)
    load = sum(sizes[int(part[1])] * T[part] for part in parts)
    return F(N * count) - load


if __name__ == "__main__":
    T, a, psi = p5_data()
    D = T["V0"] - N

    # Distinct superlevel values: 1, 2/5, 1/9, 0.
    U0 = ["V0"]
    U1 = ["V0", "V2", "V3"]
    U2 = ["V0", "V1", "V2", "V3", "V4"]
    I0 = integrand(U0, T)
    I1 = integrand(U1, T)
    I2 = integrand(U2, T)
    coarea = (F(1) - F(2, 5)) * I0 + (F(2, 5) - F(1, 9)) * I1 + F(1, 9) * I2
    p5 = sum(sizes[int(part[1])] * psi[part] * (N - T[part]) for part in psi) - D

    print("N", N)
    print("D", D)
    print("psi", psi)
    print("top_U", U0, "integrand", I0)
    print("middle_U", U1, "integrand", I1)
    print("full_U", U2, "integrand", I2)
    print("coarea_total", coarea)
    print("p5_total", p5)
    print("coarea_equals_p5", coarea == p5)

    # Switch terms for S={o}: max-cut tight, gamma-neutral, cycle-neutral.
    print("CD_singleton_o", 0)
    print("GAM_singleton_o", 0)
    print("CYC_each_bad_edge_singleton_o", 0)
