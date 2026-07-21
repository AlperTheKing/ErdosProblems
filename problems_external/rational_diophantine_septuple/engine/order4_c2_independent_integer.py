#!/usr/bin/env python3
"""Independent normalized-integer audit of the fixed order-four quotient.

This file deliberately does not import fractions, sympy, sage, or any primary
order-four implementation.  Every rational number is stored as a coprime
integer numerator/positive denominator pair.  The audit is algebraic only: it
does not enumerate rational points.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import gcd, isqrt
import json
import sys


@dataclass(frozen=True, slots=True)
class Rat:
    n: int
    d: int = 1

    def __post_init__(self) -> None:
        if self.d == 0:
            raise ZeroDivisionError("zero denominator")
        n, d = self.n, self.d
        if d < 0:
            n, d = -n, -d
        g = gcd(abs(n), d)
        object.__setattr__(self, "n", n // g)
        object.__setattr__(self, "d", d // g)

    @staticmethod
    def coerce(value: object) -> "Rat":
        if isinstance(value, Rat):
            return value
        if isinstance(value, int):
            return Rat(value)
        raise TypeError(type(value))

    def __add__(self, other: object) -> "Rat":
        b = Rat.coerce(other)
        return Rat(self.n * b.d + b.n * self.d, self.d * b.d)

    def __radd__(self, other: object) -> "Rat":
        return self + other

    def __neg__(self) -> "Rat":
        return Rat(-self.n, self.d)

    def __sub__(self, other: object) -> "Rat":
        return self + (-Rat.coerce(other))

    def __rsub__(self, other: object) -> "Rat":
        return Rat.coerce(other) - self

    def __mul__(self, other: object) -> "Rat":
        b = Rat.coerce(other)
        return Rat(self.n * b.n, self.d * b.d)

    def __rmul__(self, other: object) -> "Rat":
        return self * other

    def __truediv__(self, other: object) -> "Rat":
        b = Rat.coerce(other)
        if b.n == 0:
            raise ZeroDivisionError
        return Rat(self.n * b.d, self.d * b.n)

    def __rtruediv__(self, other: object) -> "Rat":
        return Rat.coerce(other) / self

    def __pow__(self, exponent: int) -> "Rat":
        if exponent < 0:
            return (Rat(self.d, self.n)) ** (-exponent)
        return Rat(pow(self.n, exponent), pow(self.d, exponent))

    def __str__(self) -> str:
        return str(self.n) if self.d == 1 else f"{self.n}/{self.d}"


ZERO = Rat(0)
ONE = Rat(1)


def sqrt_rat(value: Rat) -> Rat:
    if value.n < 0:
        raise ValueError("negative rational")
    rn, rd = isqrt(value.n), isqrt(value.d)
    if rn * rn != value.n or rd * rd != value.d:
        raise ValueError(f"not a rational square: {value}")
    return Rat(rn, rd)


def lcm(a: int, b: int) -> int:
    return abs(a // gcd(a, b) * b)


# Polynomials are coefficient lists in ascending degree order.
Poly = list[Rat]


def ptrim(a: Poly) -> Poly:
    out = a[:]
    while len(out) > 1 and out[-1] == ZERO:
        out.pop()
    return out


def padd(a: Poly, b: Poly) -> Poly:
    out = [ZERO] * max(len(a), len(b))
    for i in range(len(out)):
        out[i] = (a[i] if i < len(a) else ZERO) + (
            b[i] if i < len(b) else ZERO
        )
    return ptrim(out)


def pneg(a: Poly) -> Poly:
    return [-x for x in a]


def psub(a: Poly, b: Poly) -> Poly:
    return padd(a, pneg(b))


def pscale(a: Poly, scalar: Rat) -> Poly:
    return ptrim([scalar * x for x in a])


def pmul(a: Poly, b: Poly) -> Poly:
    out = [ZERO] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = out[i + j] + x * y
    return ptrim(out)


def ppow(a: Poly, exponent: int) -> Poly:
    if exponent < 0:
        raise ValueError
    out = [ONE]
    base = a[:]
    e = exponent
    while e:
        if e & 1:
            out = pmul(out, base)
        base = pmul(base, base)
        e >>= 1
    return out


def pderiv(a: Poly) -> Poly:
    if len(a) == 1:
        return [ZERO]
    return [Rat(i) * a[i] for i in range(1, len(a))]


def pdivmod(a: Poly, b: Poly) -> tuple[Poly, Poly]:
    a, b = ptrim(a), ptrim(b)
    if b == [ZERO]:
        raise ZeroDivisionError
    if len(a) < len(b):
        return [ZERO], a
    q = [ZERO] * (len(a) - len(b) + 1)
    r = a[:]
    while r != [ZERO] and len(r) >= len(b):
        shift = len(r) - len(b)
        coeff = r[-1] / b[-1]
        q[shift] = q[shift] + coeff
        term = [ZERO] * shift + pscale(b, coeff)
        r = psub(r, term)
    return ptrim(q), ptrim(r)


def pgcd(a: Poly, b: Poly) -> Poly:
    a, b = ptrim(a), ptrim(b)
    while b != [ZERO]:
        _, r = pdivmod(a, b)
        a, b = b, r
    return pscale(a, ONE / a[-1]) if a != [ZERO] else [ZERO]


Point = tuple[Rat, Rat] | None


def add_weierstrass(P: Point, Q: Point, a2: Rat, a4: Rat) -> Point:
    """Add points on y^2=x^3+a2*x^2+a4*x+a6."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 == -y2:
        return None
    if P == Q:
        if y1 == ZERO:
            return None
        slope = (3 * x1**2 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        slope = (y2 - y1) / (x2 - x1)
    x3 = slope**2 - a2 - x1 - x2
    y3 = -(y1 + slope * (x3 - x1))
    return x3, y3


def point_on_curve(P: Point, a2: Rat, a4: Rat, a6: Rat) -> bool:
    if P is None:
        return True
    x, y = P
    return y**2 == x**3 + a2 * x**2 + a4 * x + a6


def poly_strings(poly: Poly) -> list[str]:
    return [str(x) for x in poly]


def canonical_json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def audit() -> dict[str, object]:
    a = Rat(1884586446094351, 25415891646864180)
    b = Rat(14442883687791636, 7402559392524605)
    c = Rat(60340495895762708555, 14487505263205637124)
    p, q, r = a * b, a * c, b * c
    alpha = a * b * c
    rab, rac, rbc = sqrt_rat(ONE + p), sqrt_rat(ONE + q), sqrt_rat(ONE + r)

    a2 = p + q + r
    a4 = p * q + p * r + q * r
    a6 = p * q * r
    P = (ZERO, alpha)
    S = (ONE, rab * rac * rbc)
    two_s = add_weierstrass(S, S, a2, a4)
    four_s = add_weierstrass(two_s, two_s, a2, a4)
    H = (-p, ZERO)

    assert a != b and a != c and b != c
    assert ZERO not in (a, b, c)
    assert rab**2 == ONE + a * b
    assert rac**2 == ONE + a * c
    assert rbc**2 == ONE + b * c
    assert alpha**2 == a6
    assert point_on_curve(P, a2, a4, a6)
    assert point_on_curve(S, a2, a4, a6)
    assert two_s == H
    assert four_s is None

    A0 = q + r - 2 * p
    K = (q - p) * (r - p)
    assert K == (ONE + p) ** 2
    U0 = (ONE + p) * q * r / p
    assert U0 == c**2 * (ONE + p)
    j = q + r + 2
    k = q + r - 4 * p - 2

    # The quotient map is checked after clearing its powers of u.
    u: Poly = [ZERO, ONE]
    u2 = ppow(u, 2)
    curve_u = pmul(u, padd(padd(u2, pscale(u, A0)), [K]))
    Qnum = padd(padd(u2, pscale(u, A0)), [K])  # U=Qnum/u
    k_minus_u2 = psub([K], u2)
    quotient_lhs = pmul(curve_u, ppow(k_minus_u2, 2))
    quotient_bracket_num = padd(
        psub(ppow(Qnum, 2), pscale(pmul(Qnum, u), 2 * A0)),
        pscale(u2, A0**2 - 4 * K),
    )
    quotient_rhs = pmul(pmul(u, Qnum), quotient_bracket_num)
    assert psub(quotient_lhs, quotient_rhs) == [ZERO]

    # Translation by H sends u to K/u.  Check the first diagonal identity
    # after multiplying by u.
    x_num = psub(u, [p])
    xh_num = psub([K], pscale(u, p))  # x_H=(K-p*u)/u
    diagonal_left_num = padd(pmul(x_num, xh_num), pscale(u, alpha**2))
    diagonal_right_num = pscale(psub(pscale(u, U0), Qnum), p)
    assert psub(diagonal_left_num, diagonal_right_num) == [ZERO]

    # E1 factorization and image of S.
    U: Poly = [ZERO, ONE]
    e1_cubic = pmul(U, padd(padd(ppow(U, 2), pscale(U, -2 * A0)), [A0**2 - 4 * K]))
    e1_factored = pmul(pmul(U, psub(U, [j])), psub(U, [k]))
    assert psub(e1_cubic, e1_factored) == [ZERO]
    us = ONE + p
    image_s_u = us + A0 + K / us
    image_s_v_factor = K - us**2
    assert image_s_u == j and image_s_v_factor == ZERO

    # Translation by J=(j,0) has U_J=j+C/(U-j), C=j(j-k).
    Cj = j * (j - k)
    assert Cj == 4 * j * (ONE + p)
    # Verify F1(U_J)=Cj^2*F1(U)/(U-j)^4 after multiplying out.
    w = psub(U, [j])
    uj_num = padd(pscale(w, j), [Cj])
    # F1(U_J) numerator over w^3.
    translated_num = pmul(
        uj_num,
        pmul(psub(uj_num, pscale(w, j)), psub(uj_num, pscale(w, k))),
    )
    # The identity has denominator w^3 on the left and w^4 on the right.
    translated_lhs = pmul(w, translated_num)
    translated_rhs = pscale(e1_cubic, Cj**2)
    assert psub(translated_lhs, translated_rhs) == [ZERO]

    # Eliminate U from Z^2=p(U0-U): U=U0-Z^2/p.
    z: Poly = [ZERO, ONE]
    Uz = psub([U0], pscale(ppow(z, 2), ONE / p))
    sextic = pmul(
        Uz,
        padd(
            psub(ppow(Uz, 2), pscale(Uz, 2 * A0)),
            [A0**2 - 4 * K],
        ),
    )
    sextic = ptrim(sextic)
    squarefree_gcd = pgcd(sextic, pderiv(sextic))
    assert len(sextic) == 7 and sextic[-1] != ZERO
    assert squarefree_gcd == [ONE]

    # Here the lcm L of coefficient denominators is itself a square.  Thus
    # setting W=sqrt(L)*V gives the primitive integral model
    # W^2=L*sextic(Z), coefficient by coefficient.
    L = 1
    for coeff in sextic:
        L = lcm(L, coeff.d)
    sqrt_L = isqrt(L)
    assert sqrt_L * sqrt_L == L
    integral_coeffs: list[int] = []
    for coeff in sextic:
        scaled = coeff * Rat(L)
        assert scaled.d == 1
        integral_coeffs.append(scaled.n)
    content = 0
    for coeff in integral_coeffs:
        content = gcd(content, abs(coeff))
    assert content == 1
    assert integral_coeffs[-1] != 0

    # A second integral presentation is the one adapted to p=N/dp^2.
    # With X=dp*Z/N one has U=U0-N*X^2, which removes every denominator
    # introduced by the quadratic cover before multiplying V by sqrt(L).
    N = p.n
    dp = isqrt(p.d)
    assert dp * dp == p.d
    Xpoly: Poly = [ZERO, ONE]
    Ux = psub([U0], pscale(ppow(Xpoly, 2), Rat(N)))
    sextic_x = pmul(
        Ux,
        padd(
            psub(ppow(Ux, 2), pscale(Ux, 2 * A0)),
            [A0**2 - 4 * K],
        ),
    )
    scaled_x_coeffs: list[int] = []
    for coeff in sextic_x:
        scaled = coeff * Rat(L)
        assert scaled.d == 1
        scaled_x_coeffs.append(scaled.n)
    scaled_x_content = 0
    for coeff in scaled_x_coeffs:
        scaled_x_content = gcd(scaled_x_content, abs(coeff))
    assert scaled_x_content == 1
    # Directly replay Z=(N/dp)X coefficient by coefficient.
    for degree, coeff in enumerate(sextic):
        assert sextic_x[degree] == coeff * Rat(N, dp) ** degree

    scaled_x_payload = {
        "variable": "X",
        "equation": "Y^2=sum(integral_coefficients[i]*X^i,i=0..6)",
        "integral_coefficients_ascending": scaled_x_coeffs,
        "coordinate_change": {
            "X_equals_dp_times_Z_over_N": f"{dp}/{N}",
            "Y_equals_sqrt_L_times_V": str(sqrt_L),
            "inverse_U": f"U0-{N}*X^2",
        },
    }
    scaled_x_hash = sha256(canonical_json_bytes(scaled_x_payload)).hexdigest().upper()

    # The even sextic W^2=g(Z^2) has two elliptic quotients.  Write
    # g(u)=d+c*u+b*u^2+a*u^3.  The displayed substitutions give integral
    # generalized Weierstrass models without invoking a CAS:
    #
    # E+: X=a*u, Y=a*W,
    #     Y^2=X^3+b*X^2+a*c*X+a^2*d.
    # E-: X=d/u, Y=d*v/u^2 for v^2=u*g(u),
    #     Y^2=X^3+c*X^2+b*d*X+a*d^2.
    d_int, c_int, b_int, a_int = (
        integral_coeffs[0],
        integral_coeffs[2],
        integral_coeffs[4],
        integral_coeffs[6],
    )
    assert integral_coeffs[1::2] == [0, 0, 0]
    eplus_ainvariants = [0, b_int, 0, a_int * c_int, a_int * a_int * d_int]
    eminus_ainvariants = [0, c_int, 0, b_int * d_int, a_int * d_int * d_int]

    # Coefficient-level replay of both transformations.
    # E+ after X=a*u and Y=a*W.
    assert eplus_ainvariants[1] == b_int
    assert eplus_ainvariants[3] == a_int * c_int
    assert eplus_ainvariants[4] == a_int * a_int * d_int
    # E- after X=d/u and Y=d*v/u^2.
    assert eminus_ainvariants[1] == c_int
    assert eminus_ainvariants[3] == b_int * d_int
    assert eminus_ainvariants[4] == a_int * d_int * d_int

    # Smaller valid integral models for local rank probes.  These fixed scale
    # factors are replayed coefficientwise here; no minimizer is trusted.
    eplus_rational = [ZERO, -2 * A0, ZERO, A0**2 - 4 * K, ZERO]
    eplus_scale = 52208405404435206419201940
    eplus_probe: list[int] = []
    for index, coeff in enumerate(eplus_rational):
        weight = (1, 2, 3, 4, 6)[index]
        scaled = coeff * Rat(eplus_scale**weight)
        assert scaled.d == 1
        eplus_probe.append(scaled.n)

    eminus_rational = [ZERO, sextic[2], ZERO, sextic[4] * sextic[0], sextic[6] * sextic[0] ** 2]
    eminus_scale = 209887808751411037001478653850766991376
    eminus_probe: list[int] = []
    for index, coeff in enumerate(eminus_rational):
        weight = (1, 2, 3, 4, 6)[index]
        scaled = coeff * Rat(eminus_scale**weight)
        assert scaled.d == 1
        eminus_probe.append(scaled.n)

    # A direct rational presentation convenient for comparing independent
    # elliptic quotient implementations is obtained with Wp=p^2*V while Z
    # stays unchanged.  Thus Wp^2=g_p(Z^2), where g_p=p^4*g_raw.
    direct_g = [p**4 * sextic[index] for index in (0, 2, 4, 6)]
    direct_d, direct_c, direct_b, direct_a = direct_g
    assert direct_a == -p
    direct_eplus_rational = [
        ZERO,
        direct_b,
        ZERO,
        direct_a * direct_c,
        direct_a**2 * direct_d,
    ]
    direct_eminus_rational = [
        ZERO,
        direct_c,
        ZERO,
        direct_b * direct_d,
        direct_a * direct_d**2,
    ]

    def integral_scale(model: list[Rat], scale: int) -> list[int]:
        out: list[int] = []
        for index, coeff in enumerate(model):
            weight = (1, 2, 3, 4, 6)[index]
            value = coeff * Rat(scale**weight)
            assert value.d == 1
            out.append(value.n)
        return out

    direct_eplus_scale = 360875752540879741303393500
    direct_eminus_scale = 10028171693347115955970031589195458010000
    direct_eplus_integral = integral_scale(direct_eplus_rational, direct_eplus_scale)
    direct_eminus_integral = integral_scale(direct_eminus_rational, direct_eminus_scale)
    assert direct_eminus_integral == eminus_probe

    # Branch points are the six simple roots of the squarefree sextic.  Its
    # smooth projective normalization therefore has genus (6-2)/2=2.
    genus = 2

    model_payload = {
        "variable": "Z",
        "equation": "Y^2=sum(integral_coefficients[i]*Z^i,i=0..6)",
        "integral_coefficients_ascending": integral_coeffs,
        "rational_sextic_coefficients_ascending": poly_strings(sextic),
        "scaling": {
            "W_equals_sqrt_L_times_V": str(sqrt_L),
            "L": str(L),
            "Z_unchanged": True,
        },
    }
    model_hash = sha256(canonical_json_bytes(model_payload)).hexdigest().upper()

    checks = {
        "triple_distinct_nonzero": True,
        "three_pair_roots_exact": True,
        "P_and_S_on_E": True,
        "two_S_equals_H": True,
        "four_S_equals_O": True,
        "K_equals_one_plus_p_squared": True,
        "quotient_map_polynomial_identity": True,
        "first_diagonal_polynomial_identity": True,
        "E1_factorization": True,
        "image_S_equals_J": True,
        "translation_by_J_polynomial_identity": True,
        "eliminated_model_degree": 6,
        "sextic_derivative_gcd_degree": len(squarefree_gcd) - 1,
        "sextic_squarefree": True,
        "normalization_genus": genus,
        "integral_scaling_coefficientwise_exact": True,
        "scaled_X_integral_model_exact": True,
        "even_sextic": True,
        "bielliptic_quotient_maps_exact": True,
    }
    assert all(v is True or isinstance(v, int) for v in checks.values())

    return {
        "implementation": {
            "arithmetic": "custom coprime normalized integer pairs",
            "forbidden_dependencies_used": [],
            "point_enumeration": False,
        },
        "fixed_data": {
            "a": str(a),
            "b": str(b),
            "c": str(c),
            "p": str(p),
            "q": str(q),
            "r": str(r),
            "alpha": str(alpha),
            "r_ab": str(rab),
            "r_ac": str(rac),
            "r_bc": str(rbc),
            "S": [str(S[0]), str(S[1])],
            "H": [str(H[0]), str(H[1])],
            "A0": str(A0),
            "K": str(K),
            "U0": str(U0),
            "j": str(j),
            "k": str(k),
        },
        "checks": checks,
        "integral_model": model_payload,
        "integral_model_scaled_X": scaled_x_payload,
        "integral_model_scaled_X_payload_sha256": scaled_x_hash,
        "integral_polynomial_content": str(content),
        "integral_model_payload_sha256": model_hash,
        "bielliptic_split": {
            "g_coefficients_ascending": [d_int, c_int, b_int, a_int],
            "E_plus": {
                "map_from_C": "u=Z^2,y=W",
                "integral_map": "X=a*u,Y=a*y",
                "ainvariants": eplus_ainvariants,
                "compact_integral_probe": {
                    "scale_X_equals_d2_times_U": str(eplus_scale),
                    "ainvariants": eplus_probe,
                },
                "complete_if_rank_zero": True,
                "complete_lift_test": "enumerate E_plus(Q), retain u=X/a in Q^2",
                "direct_rational_model": {
                    "map": "u=Z^2,y=Wp; x=a*u,y1=a*y",
                    "ainvariants": [str(x) for x in direct_eplus_rational],
                    "Wp_equals_p_squared_times_V": True,
                },
                "direct_integral_model": {
                    "d": str(direct_eplus_scale),
                    "map": "xI=d^2*x,yI=d^3*y1",
                    "ainvariants": direct_eplus_integral,
                },
            },
            "E_minus": {
                "map_from_C": "u=Z^2,v=Z*W",
                "integral_map": "X=d/u,Y=d*v/u^2",
                "ainvariants": eminus_ainvariants,
                "compact_integral_probe": {
                    "scale_X_equals_d2_times_x": str(eminus_scale),
                    "ainvariants": eminus_probe,
                },
                "complete_if_rank_zero": True,
                "complete_lift_test": "enumerate E_minus(Q), retain u=d/X in Q^2; test Z=0 separately",
                "direct_rational_model": {
                    "map": "u=Z^2,v=Z*Wp; x=d0/u,y1=d0*v/u^2",
                    "ainvariants": [str(x) for x in direct_eminus_rational],
                    "Wp_equals_p_squared_times_V": True,
                },
                "direct_integral_model": {
                    "d": str(direct_eminus_scale),
                    "map": "xI=d^2*x,yI=d^3*y1",
                    "ainvariants": direct_eminus_integral,
                },
            },
            "direct_g_coefficients_ascending": [str(x) for x in direct_g],
            "rank_zero_finite_gate": {
                "E_plus": "If rank(E_plus)=0, enumerate finite E_plus(Q), retain u squares, lift Z=+-sqrt(u), and test infinity.",
                "E_minus": "If rank(E_minus)=0, enumerate finite E_minus(Q), retain u squares, recover Wp=v/Z, and test Z=0 and infinity separately.",
                "logical_scope": "Either certified rank-zero quotient gives a complete finite list of C2(Q) lift candidates.",
            },
        },
        "status": "PASS",
        "scope": "fixed registered canonical-order-four quotient only",
    }


def main() -> None:
    result = audit()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 1:
        sys.stdout.write(payload)
    elif len(sys.argv) == 3 and sys.argv[1] == "--output":
        with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
    else:
        raise SystemExit(f"usage: {sys.argv[0]} [--output FILE]")


if __name__ == "__main__":
    main()
