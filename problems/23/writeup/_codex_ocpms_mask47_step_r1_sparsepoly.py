"""Sparse-polynomial certificate search for mask-47 current-r=1 step.

This avoids SymPy simplification.  It builds the rational PMS step difference
with a tiny exact sparse-polynomial engine, then clears denominators by the
product of the displayed positive denominators.

Faces:
  xy1   x=y=1, q=p+e
  x1    x=1, y=1+d, q=p+d+e
  x1_epos  x=1, y=1+d, q=p+d+e with e>=1
  x1_e0_dpos  x=1, y=1+d, q=p+d with d>=1
  d0    x=y=1+h, q=p+e
  full  x=1+h, y=x+d, q=p+d+e
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from operator import mul


NVAR_BY_FACE = {"xy1": 2, "x1": 3, "x1_epos": 3, "x1_e0_dpos": 2, "d0": 3, "full": 4}


def clean(poly):
    return {m: c for m, c in poly.items() if c}


def padd(a, b):
    out = dict(a)
    for m, c in b.items():
        out[m] = out.get(m, Fraction(0)) + c
        if not out[m]:
            del out[m]
    return out


def pneg(a):
    return {m: -c for m, c in a.items()}


def psub(a, b):
    return padd(a, pneg(b))


def pscale(a, c):
    c = Fraction(c)
    if not c:
        return {}
    return {m: v * c for m, v in a.items() if v * c}


def pmul(a, b):
    if not a or not b:
        return {}
    n = len(next(iter(a)))
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = tuple(ma[i] + mb[i] for i in range(n))
            out[m] = out.get(m, Fraction(0)) + ca * cb
    return clean(out)


def ppow(a, k):
    n = len(next(iter(a))) if a else 1
    out = {tuple([0] * n): Fraction(1)}
    for _ in range(k):
        out = pmul(out, a)
    return out


def pconst(c, n):
    c = Fraction(c)
    return {} if not c else {tuple([0] * n): c}


def pvar(i, n):
    m = [0] * n
    m[i] = 1
    return {tuple(m): Fraction(1)}


def pterms(a):
    return len(a)


def pkey(a):
    return tuple(sorted(a.items()))


@dataclass
class Rat:
    num: dict
    den: dict

    @staticmethod
    def const(c, n):
        return Rat(pconst(c, n), pconst(1, n))

    @staticmethod
    def poly(p, n):
        return Rat(p, pconst(1, n))

    def add(self, other: "Rat") -> "Rat":
        return Rat(padd(pmul(self.num, other.den), pmul(other.num, self.den)), pmul(self.den, other.den))

    def sub(self, other: "Rat") -> "Rat":
        return Rat(psub(pmul(self.num, other.den), pmul(other.num, self.den)), pmul(self.den, other.den))

    def mul(self, other: "Rat") -> "Rat":
        return Rat(pmul(self.num, other.num), pmul(self.den, other.den))

    def div(self, other: "Rat") -> "Rat":
        return Rat(pmul(self.num, other.den), pmul(self.den, other.num))

    def scale(self, c) -> "Rat":
        return Rat(pscale(self.num, c), self.den)


def rsum(items, n):
    out = Rat.const(0, n)
    for item in items:
        out = out.add(item)
    return out


def pms_terms(w, n, sign=1):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    z27 = w6.mul(rsum([w0.mul(w5), w3.mul(w8), w5.mul(w8)], n))
    a27 = rsum(
        [
            w0.mul(w5),
            w0.mul(w6),
            w3.mul(w6),
            w3.mul(w8),
            w5.mul(w6),
            w5.mul(w8),
            w6.mul(w8),
        ],
        n,
    )
    z19 = w5.mul(rsum([w0.mul(w6), w4.mul(w8), w6.mul(w8)], n))
    a19 = rsum(
        [
            w0.mul(w5),
            w0.mul(w6),
            w4.mul(w5),
            w4.mul(w8),
            w5.mul(w6),
            w5.mul(w8),
            w6.mul(w8),
        ],
        n,
    )
    z79 = rsum(
        [
            w0.mul(w5).mul(w6),
            w3.mul(w4).mul(w8),
            w3.mul(w6).mul(w8),
            w4.mul(w5).mul(w8),
            w5.mul(w6).mul(w8),
        ],
        n,
    )
    a79 = rsum(
        [
            w0.mul(w5),
            w0.mul(w6),
            w3.mul(w4),
            w3.mul(w6),
            w3.mul(w8),
            w4.mul(w5),
            w4.mul(w8),
            w5.mul(w6),
            w5.mul(w8),
            w6.mul(w8),
        ],
        n,
    )
    core = rsum([w0, w3, w4, w5, w6, w8], n)
    endpoints = rsum([w1, w2, w7, w9], n)
    total = core.add(endpoints)
    f0 = total.mul(total).scale(2).add(core.scale(75))
    f0 = f0.sub(w1.mul(w9).scale(225)).sub(w2.mul(w7).scale(225)).sub(w7.mul(w9).scale(200))

    t19 = w1.mul(w9).scale(175).sub(w1.mul(w9).mul(a19).div(z19).scale(75))
    t27 = w2.mul(w7).scale(175).sub(w2.mul(w7).mul(a27).div(z27).scale(75))
    t79 = w7.mul(w9).scale(150).sub(w7.mul(w9).mul(a79).div(z79).scale(75))
    return [f0.scale(sign), t19.scale(sign), t27.scale(sign), t79.scale(sign)]


def make_vars(face):
    n = NVAR_BY_FACE[face]
    one = Rat.const(1, n)
    p = Rat.poly(padd(pvar(0, n), pconst(1, n)), n)  # p=P+1
    if face == "xy1":
        e = Rat.poly(padd(pvar(1, n), pconst(1, n)), n)  # e=E+1
        d = Rat.const(0, n)
        h = Rat.const(0, n)
    elif face == "x1":
        d = Rat.poly(pvar(1, n), n)
        e = Rat.poly(pvar(2, n), n)
        h = Rat.const(0, n)
    elif face == "x1_epos":
        d = Rat.poly(pvar(1, n), n)
        e = Rat.poly(padd(pvar(2, n), pconst(1, n)), n)
        h = Rat.const(0, n)
    elif face == "x1_e0_dpos":
        d = Rat.poly(padd(pvar(1, n), pconst(1, n)), n)
        e = Rat.const(0, n)
        h = Rat.const(0, n)
    elif face == "d0":
        e = Rat.poly(padd(pvar(1, n), pconst(1, n)), n)
        d = Rat.const(0, n)
        h = Rat.poly(pvar(2, n), n)
    elif face == "full":
        d = Rat.poly(pvar(1, n), n)
        e = Rat.poly(pvar(2, n), n)
        h = Rat.poly(pvar(3, n), n)
    else:
        raise ValueError(face)
    q = p.add(d).add(e)
    x = one.add(h)
    y = x.add(d)
    r = one
    # a=(x*p+y*q+q*p-y-p)/p
    a_num = x.mul(p).add(y.mul(q)).add(q.mul(p)).sub(y).sub(p)
    a = a_num.div(p)
    r_prev = one.add(p.div(y.add(p)))
    current = (a, x, y, y, x, p, q, q, r, p)
    previous = (a.sub(one), x, y, y, x, p, q, q, r_prev, p)
    return current, previous, n


def clear_terms(terms, n):
    dens = []
    seen = set()
    for t in terms:
        key = pkey(t.den)
        if key in seen:
            continue
        seen.add(key)
        dens.append(t.den)
    print("unique_denominators", len(dens), "of", len(terms), flush=True)
    numerator = {}
    common = pconst(1, n)
    for den in dens:
        common = pmul(common, den)
    for i, term in enumerate(terms):
        other_den = pconst(1, n)
        # Multiply by every unique denominator except the term's own
        # denominator.  If another term shares the same denominator, that
        # factor still appears only once in the common positive denominator.
        term_key = pkey(term.den)
        for den in dens:
            if pkey(den) != term_key:
                other_den = pmul(other_den, den)
        numerator = padd(numerator, pmul(term.num, other_den))
        print("assembled", i, "terms", pterms(numerator), flush=True)
    return numerator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--face", choices=sorted(NVAR_BY_FACE), default="xy1")
    args = ap.parse_args()
    current, previous, n = make_vars(args.face)
    terms = pms_terms(current, n, 1) + pms_terms(previous, n, -1)
    print("face", args.face, "nterms", len(terms), flush=True)
    print("term_den_terms", [pterms(t.den) for t in terms], flush=True)
    numerator = clear_terms(terms, n)
    coeffs = list(numerator.values())
    neg = [(m, c) for m, c in numerator.items() if c < 0]
    print("terms", len(numerator), "negative", len(neg), "min_coeff", min(coeffs), flush=True)
    if neg:
        print("first_negative", neg[0], flush=True)
        raise SystemExit(1)
    print("VERDICT PASS", flush=True)


if __name__ == "__main__":
    main()
