#!/usr/bin/env python3
"""
band11_xcheck.py -- validation of the band-11 gap scanner.

(1) MODULI CLAIM: for a fixed gap vector, every partition-level lift (different
    l4/m4/n4 with the same gaps) must give the SAME L(n), V, h*, a1 under the
    independent exact engine hive4.py.
(2) SCANNER AGREEMENT: band11_vcscan.exe --one <gaps> must agree with hive4.py
    on L(1),L(2),L(3), V, h*, 6a1 for every sampled gap vector.
All arithmetic exact (hive4.py uses Fractions/ints).
"""
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402

EXE = os.path.join(HERE, "band11_vcscan.exe")


def gaps_to_parts(a, b, c, extra=0):
    """Lift gaps to partitions; extra >= 0 adds a common shift (a second lift)."""
    Aw = 3 * a[2] + 2 * a[1] + a[0]
    Bw = 3 * b[2] + 2 * b[1] + b[0]
    Cw = 3 * c[2] + 2 * c[1] + c[0]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return None
    k = D // 4
    l4 = m4 = n4 = 0
    if k >= 0:
        l4 = k
    else:
        n4 = -k
    # extra: add 'extra' to every part of lam and nu (a full column) -- a
    # translation of Q; and 'extra' to mu and nu as well.
    l4 += extra
    m4 += extra
    n4 += 2 * extra
    lam = [l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4]
    mu = [m4 + b[2] + b[1] + b[0], m4 + b[2] + b[1], m4 + b[2], m4]
    nu = [n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4]
    assert sum(lam) + sum(mu) == sum(nu), (lam, mu, nu)
    return lam, mu, nu


def scanner_one(g):
    out = subprocess.run([EXE, "--one"] + [str(x) for x in g],
                         capture_output=True, text=True).stdout.strip()
    if out.startswith("INVALID"):
        return None
    # a=(..) b=(..) c=(..) | L=(L1,L2,L3) V=.. c=.. h*=(1,h1,h2,h3) 6a1=..
    seg = out.split("|")[1]
    L = seg.split("L=(")[1].split(")")[0].split(",")
    V = int(seg.split("V=")[1].split()[0])
    hs = seg.split("h*=(")[1].split(")")[0].split(",")
    a1 = int(seg.split("6a1=")[1].split()[0])
    return dict(L=[int(x) for x in L], V=V, h=[int(x) for x in hs], six_a1=a1)


def main(nsample=200, gmax=9, seed=11):
    rnd = random.Random(seed)
    tested = 0
    fails = []
    lift_tested = 0
    while tested < nsample:
        g = [rnd.randint(0, gmax) for _ in range(9)]
        p = gaps_to_parts(g[:3], g[3:6], g[6:])
        if p is None:
            continue
        lam, mu, nu = p
        r = hive4.analyze(lam, mu, nu)
        s = scanner_one(g)
        if r["dim"] < 0 or r["c"] == 0:
            if s is not None:
                fails.append(("scanner_nonempty_but_hive_empty", g, s, r["c"]))
            continue
        tested += 1
        if s is None:
            fails.append(("scanner_invalid", g, lam, mu, nu, r["c"]))
            continue
        L = r["L"][1:4]
        V = r["volume_normalized"]
        P = r["poly"]
        a1 = P[1] if len(P) > 1 else Fraction(0)
        h = r["hstar"] if r["dim"] == 3 else None
        ok = (s["L"] == L and Fraction(s["V"]) == V
              and Fraction(s["six_a1"], 6) == a1)
        if h is not None and s["h"] != list(h):
            ok = False
        if not r["verified"] or not r["vol_crosscheck"]:
            ok = False
        if not ok:
            fails.append(("mismatch", g, lam, mu, nu, s, L, str(V), str(a1),
                          r["hstar"]))
        # (1) moduli invariance: a second lift must give identical data
        p2 = gaps_to_parts(g[:3], g[3:6], g[6:], extra=rnd.randint(1, 4))
        r2 = hive4.analyze(*p2)
        lift_tested += 1
        if r2["L"][1:4] != L or r2["volume_normalized"] != V or r2["hstar"] != r["hstar"]:
            fails.append(("lift_mismatch", g, p, p2, r["L"], r2["L"]))
    print("triples cross-checked hive4.py vs band11_vcscan.exe : %d" % tested)
    print("moduli lift-invariance checks                       : %d" % lift_tested)
    print("FAILURES: %d" % len(fails))
    for f in fails[:10]:
        print("  ", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    gm = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    sys.exit(main(n, gm))
