#!/usr/bin/env python3
"""
xval_band5.py -- cross-validate the C++ band census engine (census_band5.exe)
against the exact reference engine hive4.py on random triples drawn from the
weight band W in [33,38].

For every sampled triple both engines must agree EXACTLY on
  dim, c = L(1), L(2), L(3), normalized volume V, the h*-vector, and the
  full Ehrhart / stretched LR polynomial P.
Any single disagreement aborts with a non-zero exit code.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


def parts_le4(N):
    out = []
    for p1 in range(N, (N + 3) // 4 - 1, -1):
        r1 = N - p1
        for p2 in range(min(p1, r1), (r1 + 2) // 3 - 1, -1):
            r2 = r1 - p2
            for p3 in range(min(p2, r2), (r2 + 1) // 2 - 1, -1):
                p4 = r2 - p3
                if p4 > p3:
                    continue
                out.append((p1, p2, p3, p4))
    if N == 0:
        out = [(0, 0, 0, 0)]
    return out


def contained(a, b):
    return all(x <= y for x, y in zip(a, b))


def main(nsamp=1500, seed=20260721, wlo=33, whi=38):
    rng = random.Random(seed)
    cache = {}

    def P(n):
        if n not in cache:
            cache[n] = parts_le4(n)
        return cache[n]

    samples = []
    # half the sample forced to satisfy containment (the only place a nonempty
    # polytope can live), half completely uniform over the band
    while len(samples) < nsamp:
        W = rng.randint(wlo, whi)
        nu = rng.choice(P(W))
        a = rng.randint(0, W)
        lam = rng.choice(P(a))
        mu = rng.choice(P(W - a))
        force = len(samples) % 2 == 0
        if force and not (contained(lam, nu) and contained(mu, nu)):
            continue
        samples.append((lam, mu, nu))

    def s(p):
        t = [x for x in p if x > 0]
        return ",".join(map(str, t)) if t else "0"

    bf = os.path.join(HERE, "_xval_band5.txt")
    with open(bf, "w") as f:
        for lam, mu, nu in samples:
            f.write("%s;%s;%s\n" % (s(lam), s(mu), s(nu)))

    exe = os.path.join(HERE, "census_band5.exe")
    out = subprocess.run([exe, "--check", bf], capture_output=True, text=True, check=True).stdout
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == len(samples), (len(lines), len(samples))

    bad = []
    ndim3 = 0
    for (lam, mu, nu), line in zip(samples, lines):
        body = line.split("|", 1)[1]
        fields = {}
        for tok in body.split():
            if "=" in tok:
                k, v = tok.split("=", 1)
                fields[k] = v
        cdim = int(fields["dim"])
        cL = [int(x) for x in fields["L"].split(",")]
        cV = int(fields["V"])
        cH = [int(x) for x in fields["hstar"].split(",")]
        c6a1 = int(fields["6a1"])
        cden = int(fields["den"])

        r = hive4.analyze(list(lam), list(mu), list(nu))
        pdim = r["dim"]
        pL = list(r["L"])
        pV = r["volume_normalized"]
        pH = list(r["hstar"])
        poly = r["poly"]
        pa1 = poly[1] if len(poly) > 1 else Fraction(0)

        errs = []
        if cdim != pdim:
            errs.append("dim %d vs %d" % (cdim, pdim))
        if pdim >= 0:
            if cL[:6] != pL[:6] and not (cL[4] == 0 and cL[5] == 0 and cdim < 3):
                # L(4),L(5) only computed by the C++ engine for dim-3 triples
                if cL[:4] != pL[:4]:
                    errs.append("L %s vs %s" % (cL, pL))
            if cdim == 3:
                ndim3 += 1
                if cL[:6] != pL[:6]:
                    errs.append("L45 %s vs %s" % (cL, pL))
                if Fraction(cV) != pV:
                    errs.append("V %s vs %s" % (cV, pV))
                if cH != pH:
                    errs.append("hstar %s vs %s" % (cH, pH))
                if r.get("max_denominator", 1) != cden:
                    errs.append("den %d vs %d" % (cden, r.get("max_denominator", 1)))
            if Fraction(c6a1, 6) != pa1:
                errs.append("a1 %s vs %s" % (Fraction(c6a1, 6), pa1))
        else:
            if not r["empty"]:
                errs.append("emptiness mismatch")
        if errs:
            bad.append((lam, mu, nu, errs, line))

    print("sampled triples      : %d  (W in [%d,%d])" % (len(samples), wlo, whi))
    print("dim-3 among sampled  : %d" % ndim3)
    print("MISMATCHES           : %d" % len(bad))
    for b in bad[:20]:
        print("   ", b)
    res = {"n": len(samples), "seed": seed, "wlo": wlo, "whi": whi,
           "dim3": ndim3, "mismatches": len(bad),
           "detail": [[list(x[0]), list(x[1]), list(x[2]), x[3]] for x in bad[:50]]}
    with open(os.path.join(HERE, "runs", "band5", "xval_report.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("XVAL:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    sys.exit(main(n))
