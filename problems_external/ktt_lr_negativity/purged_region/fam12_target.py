#!/usr/bin/env python3
"""
fam12_target.py -- exact enumeration of the CHEAPEST h*-vectors (smallest
normalized volume V = sum h*) that force a strictly negative Ehrhart
coefficient, for each degree d.  Pure exact arithmetic (Fraction).

P(n) = sum_j h*_j C(n+d-j, d);  coefficients read off by exact interpolation
of that identity (no formula trusted blind).
"""
import sys
from fractions import Fraction
from math import comb


def coeffs_of_hstar(h, d):
    """monomial coefficients of P(n) = sum_j h_j C(n+d-j,d), exact."""
    # build C(n+d-j,d) = prod_{i=0}^{d-1} (n + d-j-i) / d!
    acc = [Fraction(0)] * (d + 1)
    for j, hj in enumerate(h):
        if hj == 0:
            continue
        poly = [Fraction(1)]
        for i in range(d):
            shift = Fraction(d - j - i)
            new = [Fraction(0)] * (len(poly) + 1)
            for k, c in enumerate(poly):
                new[k + 1] += c
                new[k] += c * shift
            poly = new
        for k, c in enumerate(poly):
            acc[k] += Fraction(hj) * c
    return [c / Fraction(comb(d, d) * _fact(d)) for c in acc]


def _fact(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def search(d, Vmax=30, h1=0):
    """smallest V with a negative coefficient; returns (V, witness, negidx)."""
    best = None
    for V in range(2, Vmax + 1):
        rem = V - 1 - h1
        if rem < 0:
            continue
        # distribute rem over positions 2..d
        found = []
        for h in _compositions(rem, d - 1):
            hv = [1, h1] + list(h)
            c = coeffs_of_hstar(hv, d)
            neg = [k for k, x in enumerate(c) if x < 0]
            if neg:
                found.append((hv, neg, [str(x) for x in c]))
        if found:
            return V, found
    return None, []


def _compositions(total, slots):
    if slots <= 0:
        if total == 0:
            yield ()
        return
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, slots - 1):
            yield (first,) + rest


if __name__ == "__main__":
    dmax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    for d in range(3, dmax + 1):
        V, found = search(d, Vmax=30)
        if V is None:
            print("d=%2d  none with V<=30" % d)
            continue
        print("d=%2d  Vmin=%2d  #witnesses=%d" % (d, V, len(found)))
        for hv, neg, c in found[:8]:
            print("        h*=%s  negidx=%s  coeffs=%s" % (hv, neg, c))
