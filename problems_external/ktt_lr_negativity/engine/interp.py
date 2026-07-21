#!/usr/bin/env python3
"""
interp.py -- exact rational interpolation + held-out verification for the
KTT stretched-LR polynomial hunt.

Usage:
    python interp.py <samples.txt>
    python interp.py --selftest

samples.txt: one sample per line, "n value" (value may be an integer or an
exact fraction "p/q"; blank lines and lines starting with '#' are ignored).
The caller passes EXACTLY the points: the LAST TWO lines are held-out
verification points; every earlier line (the first D+1 points) is an
interpolation node. Newton divided-difference interpolation over exact
Fractions -- no floating point anywhere.

Output (machine-parseable):
    POINTS:<m>                          number of interpolation nodes
    DEGREE:<d>                          degree after stripping trailing zeros
    COEFFS_LOW_TO_HIGH:c0 c1 ... cd     exact Fractions, e.g. "1 3/2 1/2"
    NEGATIVE_COEFF:<k>                  one line per strictly negative coeff
    HELDOUT n=<n> file=<v> poly=<P(n)> match=<yes|no>     (two lines)
    EXTRA_POINT_MATCH:<yes|no>          yes iff BOTH held-out points match

Exit codes: 0 = ran, both held-out points matched; 3 = ran, mismatch
(DEGREE_ANOMALY signal for the caller -- never a hit); 2 = bad input.
"""

import os
import sys
import tempfile
from fractions import Fraction


def parse_samples(path):
    pts = []
    with open(path, "r") as f:
        for ln, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            toks = line.split()
            if len(toks) != 2:
                raise ValueError(f"line {ln}: expected 'n value', got {raw!r}")
            n = int(toks[0])
            val = Fraction(toks[1])
            pts.append((Fraction(n), val))
    if len(pts) < 3:
        raise ValueError("need at least 3 lines (>=1 node + 2 held-out)")
    nodes, heldout = pts[:-2], pts[-2:]
    xs = [x for x, _ in nodes]
    if len(set(xs)) != len(xs):
        raise ValueError("duplicate n among interpolation nodes")
    return nodes, heldout


def newton_coeffs(nodes):
    """Monomial coefficients (low->high) of the Newton interpolant."""
    xs = [x for x, _ in nodes]
    dd = [y for _, y in nodes]          # divided-difference table, in place
    m = len(nodes)
    coefs = [dd[0]]                     # top diagonal, built incrementally
    for j in range(1, m):
        for i in range(m - 1, j - 1, -1):
            dd[i] = (dd[i] - dd[i - 1]) / (xs[i] - xs[i - j])
        coefs.append(dd[j])
    # expand Newton form sum_j coefs[j] * prod_{i<j} (x - xs[i])
    poly = [Fraction(0)] * m
    basis = [Fraction(1)]               # prod so far, low->high
    for j in range(m):
        for k, b in enumerate(basis):
            poly[k] += coefs[j] * b
        if j < m - 1:                   # basis *= (x - xs[j])
            new = [Fraction(0)] * (len(basis) + 1)
            for k, b in enumerate(basis):
                new[k] -= xs[j] * b
                new[k + 1] += b
            basis = new
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_eval(poly, x):
    acc = Fraction(0)
    for c in reversed(poly):
        acc = acc * x + c
    return acc


def fmt(fr):
    return str(fr)                      # Fraction str: "7" or "3/2"


def run(path):
    nodes, heldout = parse_samples(path)
    poly = newton_coeffs(nodes)
    negatives = [k for k, c in enumerate(poly) if c < 0]
    checks = []
    for x, v in heldout:
        pv = poly_eval(poly, x)
        checks.append((x, v, pv, pv == v))
    return {"points": len(nodes), "poly": poly, "negatives": negatives,
            "heldout": checks, "match": all(ok for *_, ok in checks)}


def report(res):
    print(f"POINTS:{res['points']}")
    print(f"DEGREE:{len(res['poly']) - 1}")
    print("COEFFS_LOW_TO_HIGH:" + " ".join(fmt(c) for c in res["poly"]))
    for k in res["negatives"]:
        print(f"NEGATIVE_COEFF:{k}")
    for x, v, pv, ok in res["heldout"]:
        print(f"HELDOUT n={x} file={fmt(v)} poly={fmt(pv)} "
              f"match={'yes' if ok else 'no'}")
    print(f"EXTRA_POINT_MATCH:{'yes' if res['match'] else 'no'}")


# ----------------------------------------------------------------- selftest

def _write(tmpdir, name, rows):
    p = os.path.join(tmpdir, name)
    with open(p, "w") as f:
        f.write("\n".join(f"{n} {v}" for n, v in rows) + "\n")
    return p


def selftest():
    import subprocess
    F = Fraction
    fails = []

    def check(label, cond):
        print(f"  {'PASS' if cond else 'FAIL'}: {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as td:
        # T1: constant P=1 (KTW c=1 shape), nodes n=0..4, held-out 5,6
        r = run(_write(td, "t1.txt", [(n, 1) for n in range(7)]))
        check("T1 P=1: coeffs==[1]", r["poly"] == [F(1)])
        check("T1 P=1: no negatives", r["negatives"] == [])
        check("T1 P=1: heldout match", r["match"])

        # T2: P=n+1 (c=2 shape), nodes 0..3, held-out 4,5
        r = run(_write(td, "t2.txt", [(n, n + 1) for n in range(6)]))
        check("T2 P=n+1: coeffs==[1,1]", r["poly"] == [F(1), F(1)])
        check("T2 P=n+1: heldout match", r["match"])

        # T3: P=(n+1)(n+2)/2, fractional coeffs 1,3/2,1/2
        r = run(_write(td, "t3.txt",
                       [(n, (n + 1) * (n + 2) // 2) for n in range(6)]))
        check("T3 binom: coeffs==[1,3/2,1/2]",
              r["poly"] == [F(1), F(3, 2), F(1, 2)])
        check("T3 binom: no negatives", r["negatives"] == [])
        check("T3 binom: heldout match", r["match"])

        # T4: NEGATIVE coefficient: P=2n^3-5n^2+3n+7 -> NEGATIVE_COEFF:2 only
        def p4(n):
            return 2 * n ** 3 - 5 * n ** 2 + 3 * n + 7
        p4f = _write(td, "t4.txt", [(n, p4(n)) for n in range(6)])
        r = run(p4f)
        check("T4 negcoeff: coeffs==[7,3,-5,2]",
              r["poly"] == [F(7), F(3), F(-5), F(2)])
        check("T4 negcoeff: negatives==[2]", r["negatives"] == [2])
        check("T4 negcoeff: heldout match", r["match"])

        # T5: corrupted held-out -> EXTRA_POINT_MATCH:no (P=n^2, last value +1)
        rows = [(n, n * n) for n in range(6)]
        rows[-1] = (5, 26)
        p5f = _write(td, "t5.txt", rows)
        r = run(p5f)
        check("T5 corrupt: coeffs==[0,0,1]", r["poly"] == [F(0), F(0), F(1)])
        check("T5 corrupt: EXTRA_POINT_MATCH no", not r["match"])

        # T6: degree-6 huge coefficients (r=5 hunt shape D=6), nodes 0..6
        def p6(n):
            return (10 ** 30 * n ** 6 - 10 ** 29 * n ** 5
                    + 12345678901234567890 * n - 3)
        r = run(_write(td, "t6.txt", [(n, p6(n)) for n in range(9)]))
        check("T6 bigint: exact coeffs",
              r["poly"] == [F(-3), F(12345678901234567890), F(0), F(0),
                            F(0), F(-10 ** 29), F(10 ** 30)])
        check("T6 bigint: negatives==[0,5]", r["negatives"] == [0, 5])
        check("T6 bigint: heldout match", r["match"])

        # T7: fraction-valued samples P=n/2
        r = run(_write(td, "t7.txt",
                       [(n, Fraction(n, 2)) for n in range(5)]))
        check("T7 fractions: coeffs==[0,1/2]", r["poly"] == [F(0), F(1, 2)])
        check("T7 fractions: heldout match", r["match"])

        # T8: duplicate node n -> input error
        p8f = _write(td, "t8.txt", [(0, 1), (0, 1), (1, 2), (2, 3), (3, 4)])
        try:
            run(p8f)
            check("T8 duplicate-n rejected", False)
        except ValueError:
            check("T8 duplicate-n rejected", True)

        # CLI contract: exit codes + exact output lines via subprocess
        py = sys.executable
        me = os.path.abspath(__file__)
        r4 = subprocess.run([py, me, p4f], capture_output=True, text=True)
        check("CLI T4 exit 0", r4.returncode == 0)
        out4 = r4.stdout.splitlines()
        check("CLI T4 COEFFS line",
              "COEFFS_LOW_TO_HIGH:7 3 -5 2" in out4)
        check("CLI T4 NEGATIVE_COEFF:2 printed", "NEGATIVE_COEFF:2" in out4)
        check("CLI T4 EXTRA_POINT_MATCH:yes", "EXTRA_POINT_MATCH:yes" in out4)
        r5 = subprocess.run([py, me, p5f], capture_output=True, text=True)
        check("CLI T5 exit 3 (anomaly)", r5.returncode == 3)
        check("CLI T5 EXTRA_POINT_MATCH:no",
              "EXTRA_POINT_MATCH:no" in r5.stdout.splitlines())

    print(f"SELFTEST: {'ALL PASS' if not fails else 'FAILURES: ' + str(fails)}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        res = run(argv[1])
    except (ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    report(res)
    return 0 if res["match"] else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
