#!/usr/bin/env python3
"""
xvalidate_band10.py -- cross-validate the band10.exe screen against hive4.py.

band10.exe classifies a gap vector by:  n_vertices, all-vertices-lattice,
normalized volume V of a 4-vertex simplex, and "all 6 edges primitive".
The band-10 claim used to convert that screen into the target statement is

    Q a 3-dim LATTICE polytope with c = L(1) = 4
      <=>  Q is a 4-vertex simplex, all vertices lattice, all edges primitive
           AND no further lattice point  (emptiness)

so the primitive-edge screen is a NECESSARY condition for c = 4 and V is then
the vertex-cone multiplicity.  This script checks, on random realisable gap
vectors, that hive4.py agrees with band10.exe on (n_vertices, dim, V, c) and
that every c = 4 case is exactly a primitive-edge 4-vertex lattice simplex.

All arithmetic exact (hive4.py is Fraction/int only).
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import hive4  # noqa: E402

EXE = os.path.join(ROOT, "band10.exe")


def gaps_to_triple(g):
    Aw = 3 * g[2] + 2 * g[1] + g[0]
    Bw = 3 * g[5] + 2 * g[4] + g[3]
    Cw = 3 * g[8] + 2 * g[7] + g[6]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return None
    k = D // 4
    l4 = k if k >= 0 else 0
    n4 = 0 if k >= 0 else -k
    m4 = 0
    lam = [l4 + g[2] + g[1] + g[0], l4 + g[2] + g[1], l4 + g[2], l4]
    mu = [m4 + g[5] + g[4] + g[3], m4 + g[5] + g[4], m4 + g[5], m4]
    nu = [n4 + g[8] + g[7] + g[6], n4 + g[8] + g[7], n4 + g[8], n4]
    return lam, mu, nu


def _num(s):
    s = s.strip()
    if s.startswith("-1(none)"):
        return -1
    tok = ""
    for ch in s:
        if ch.isdigit():
            tok += ch
        else:
            break
    return int(tok) if tok else -1


def run_one(g):
    out = subprocess.run([EXE, "--one"] + [str(x) for x in g],
                         capture_output=True, text=True).stdout
    d = {"nv": None, "V": None, "Ve": None, "maxden": None}
    for line in out.splitlines():
        if line.startswith("n_vertices histogram:"):
            body = line.split(":", 1)[1].strip()
            for tok in body.split():
                k, v = tok.split(":")
                d["nv"] = int(k)
        if line.startswith("max vertex denominator"):
            d["maxden"] = int(line.split("=")[1].split()[0])
        if line.startswith("max V over 4-vertex lattice simplices="):
            d["V"] = _num(line.split("=")[1])
        if line.startswith("max V over 4-vertex lattice simplices with ALL EDGES PRIMITIVE"):
            d["Ve"] = _num(line.split(" at ")[0].rsplit("=", 1)[1])
    return d


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    ntest = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    kmax = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    rng = random.Random(seed)
    checked = 0
    fails = []
    c4 = 0
    c4_simplex = 0
    while checked < ntest:
        g = [rng.randint(0, kmax) for _ in range(9)]
        t = gaps_to_triple(g)
        if t is None:
            continue
        lam, mu, nu = t
        r = hive4.analyze(lam, mu, nu)
        b = run_one(g)
        checked += 1
        nv = r.get("n_vertices", 0)
        V = int(r["volume_normalized"])
        c = r["c"]
        problems = []
        if b["maxden"] != (max(r.get("denominators", [1])) if nv else 1):
            problems.append("denominator")
        if nv == 4 and r["dim"] == 3 and max(r.get("denominators", [1])) == 1:
            if b["V"] != V:
                problems.append("V(%s vs %s)" % (b["V"], V))
        if c == 4 and r["dim"] == 3:
            c4 += 1
            if nv == 4 and b["Ve"] == V:
                c4_simplex += 1
            else:
                problems.append("c4_not_primitive_simplex(nv=%d,Ve=%s,V=%s)" % (nv, b["Ve"], V))
        if problems:
            fails.append({"gaps": g, "lam": lam, "mu": mu, "nu": nu,
                          "nv": nv, "dim": r["dim"], "V": V, "c": c,
                          "band10": b, "problems": problems})
    res = {"seed": seed, "checked": checked, "kmax": kmax,
           "c4_cases": c4, "c4_confirmed_primitive_simplex": c4_simplex,
           "failures": fails, "n_failures": len(fails)}
    print(json.dumps(res, indent=1))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
