#!/usr/bin/env python3
"""Mandatory cross-engine validation of the r=5 hive-polytope constructor.

For >= 300 varied triples with parts of length <= 5 it checks
    #( Q(lam,mu,nu) cap Z^6 )  ==  engine A  ==  engine B .
A single disagreement fails the run.
"""

import json
import random
import subprocess
import sys
import os

from count5 import lr_count

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGA = os.path.join(ROOT, "engine", "lr_hive.exe")
ENGB = os.path.join(ROOT, "engine", "engineB_lrrule.py")


def rand_partition(rng, r, maxpart):
    k = rng.randint(1, r)
    parts = sorted((rng.randint(0, maxpart) for _ in range(k)), reverse=True)
    while parts and parts[-1] == 0:
        parts.pop()
    return parts


def make_triples(n, seed=20260722):
    rng = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < 400 * n:
        tries += 1
        maxpart = rng.choice([2, 3, 4, 5, 6, 8, 10])
        lam = rand_partition(rng, 5, maxpart)
        mu = rand_partition(rng, 5, maxpart)
        if not lam or not mu:
            continue
        # build nu of length <= 5 containing lam with |nu| = |lam|+|mu|
        total = sum(lam) + sum(mu)
        nu = rand_partition(rng, 5, maxpart * 2)
        if not nu or sum(nu) == 0:
            continue
        # rescale-free fix: adjust nu greedily to hit the total weight
        d = total - sum(nu)
        nu = nu + [0] * (5 - len(nu))
        i = 0
        while d != 0 and i < 5:
            if d > 0:
                cap = (nu[i - 1] - nu[i]) if i > 0 else d
                add = min(d, cap if i > 0 else d)
                nu[i] += add
                d -= add
            else:
                lo = nu[i + 1] if i < 4 else 0
                sub = min(-d, nu[i] - lo)
                nu[i] -= sub
                d += sub
            i += 1
        if d != 0:
            continue
        while nu and nu[-1] == 0:
            nu.pop()
        if not nu or sum(nu) != total:
            continue
        if any(nu[j] < nu[j + 1] for j in range(len(nu) - 1)):
            continue
        out.append((lam, mu, nu))
    return out


def s(p):
    return ",".join(map(str, p)) if p else "0"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 320
    trips = make_triples(n)
    batch = "\n".join("%s;%s;%s;100000000" % (s(a), s(b), s(c)) for a, b, c in trips)
    bf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_val5.batch")
    with open(bf, "w") as f:
        f.write(batch + "\n")
    ra = subprocess.run([ENGA, "--batch", bf], capture_output=True, text=True)
    rb = subprocess.run([sys.executable, ENGB, "--batch", bf], capture_output=True, text=True)
    la = ra.stdout.split()
    lb = rb.stdout.split()
    assert len(la) == len(trips), (len(la), len(trips), ra.stdout[:400], ra.stderr[:400])
    assert len(lb) == len(trips), (len(lb), len(trips), rb.stdout[:400], rb.stderr[:400])
    bad = []
    for i, (lam, mu, nu) in enumerate(trips):
        mine = lr_count(lam, mu, nu, 5)
        a = int(la[i]) if la[i].lstrip("-").isdigit() else None
        b = int(lb[i]) if lb[i].lstrip("-").isdigit() else None
        if a != mine or b != mine:
            bad.append({"lam": lam, "mu": mu, "nu": nu, "mine": mine, "A": la[i], "B": lb[i]})
    print(json.dumps({"triples": len(trips), "mismatches": len(bad),
                      "examples": bad[:5],
                      "verdict": "PASS" if not bad else "FAIL"}, indent=1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
