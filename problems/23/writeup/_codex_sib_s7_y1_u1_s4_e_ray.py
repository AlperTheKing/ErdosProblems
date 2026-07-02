"""Exact positivity for a newly exposed y=1,u=1,s4 boundary ray.

The inactive-slack closure profiler leaves the support

    a=b=c=d=f=x=v=u=1,  s3=s4=0,

with e free.  Feasibility is e>=1; the remaining slacks are nonnegative:

    s1=s2=s5=s6=e-1,  s7=2(e-1).

After clearing the positive denominator e(3e+2), Phi has numerator

    6e^4 + 337e^3 + 483e^2 - 551e - 150.

With e=1+E this becomes

    6E^4 + 361E^3 + 1530E^2 + 1450E + 125,

which is strictly positive for E>=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    E = sp.symbols("E", nonnegative=True)
    e = 1 + E
    numerator = sp.expand(6 * e**4 + 337 * e**3 + 483 * e**2 - 551 * e - 150)
    expected = 6 * E**4 + 361 * E**3 + 1530 * E**2 + 1450 * E + 125
    assert sp.expand(numerator - expected) == 0
    coeffs = [sp.Integer(coeff) for coeff in sp.Poly(expected, E).coeffs()]
    assert all(coeff > 0 for coeff in coeffs)
    print("PASS y=1,u=1,s4 E-ray is coefficientwise positive after e=1+E")


if __name__ == "__main__":
    main()
