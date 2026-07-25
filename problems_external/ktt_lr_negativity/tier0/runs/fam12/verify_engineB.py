#!/usr/bin/env python3
"""Independent re-verification of selected fam12 records with ENGINE B.

For each triple: recompute the full profile P(0..D+2) with engine B
(python engineB_lrrule.py, the LR-rule implementation -- a different
algorithm from engine A's hive counter), re-interpolate from scratch here
(own Fraction Lagrange, not the screen's Newton routine), re-derive h* from
the definition, and compare with the record produced by tier0_screen.py.

Exact arithmetic only.
"""
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ENGB = os.path.abspath(os.path.join(HERE, "..", "..", "..", "engine",
                                    "engineB_lrrule.py"))


def fmt(p):
    return ",".join(str(x) for x in p) if p else "0"


def engineB(jobs, cap=10 ** 20):
    lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), cap) for l, m, v in jobs]
    fd, path = tempfile.mkstemp(suffix=".batch", text=True)
    with os.fdopen(fd, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    try:
        p = subprocess.run([sys.executable, ENGB, "--batch", path],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError("engineB exit %d: %s" % (p.returncode,
                                                        p.stderr[:300]))
        out = [x.strip() for x in p.stdout.splitlines() if x.strip()]
        assert len(out) == len(lines), (len(out), len(lines))
        return [int(x) if x.lstrip("-").isdigit() else x for x in out]
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def lagrange(pts):
    """exact Lagrange interpolation -> monomial coeffs low-to-high."""
    n = len(pts)
    coeffs = [Fraction(0)] * n
    for i, (xi, yi) in enumerate(pts):
        num = [Fraction(1)]
        den = Fraction(1)
        for j, (xj, _) in enumerate(pts):
            if i == j:
                continue
            num = [Fraction(0)] + num
            for k in range(len(num) - 1):
                num[k] -= Fraction(xj) * num[k + 1]
            den *= (Fraction(xi) - Fraction(xj))
        for k, cc in enumerate(num):
            coeffs[k] += Fraction(yi) * cc / den
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def peval(coeffs, x):
    s = Fraction(0)
    for c in reversed(coeffs):
        s = s * Fraction(x) + c
    return s


def main():
    recs = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    out = []
    for rec in recs:
        lam, mu, nu = rec["lam"], rec["mu"], rec["nu"]
        r = len(nu)
        D = max(0, (r - 1) * (r - 2) // 2)
        jobs = [([n * x for x in lam], [n * x for x in mu], [n * x for x in nu])
                for n in range(D + 3)]
        vals = engineB(jobs)
        res = {"lam": lam, "mu": mu, "nu": nu, "engineB_profile": vals}
        if any(not isinstance(v, int) for v in vals):
            res["verdict"] = "ENGINE_B_CAP_OR_ERROR"
            out.append(res)
            continue
        res["profile_matches_engineA"] = (vals == rec.get("profile"))
        pts = [(n, vals[n]) for n in range(D + 1)]
        co = lagrange(pts)
        d = len(co) - 1
        res["d_engineB"] = d
        res["d_matches"] = (d == rec.get("d"))
        res["heldout_ok"] = all(peval(co, n) == vals[n]
                                for n in (D + 1, D + 2))
        hstar = [sum((-1) ** i * comb(d + 1, i) * Fraction(vals[j - i])
                     for i in range(j + 1)) for j in range(d + 1)]
        res["hstar_engineB"] = [str(h) for h in hstar]
        res["hstar_matches"] = ([Fraction(x) for x in (rec.get("hstar") or [])]
                                == hstar)
        rt = all(sum(hstar[j] * comb(n + d - j, d) for j in range(d + 1))
                 == vals[n] for n in range(D + 3))
        res["hstar_roundtrip_ok"] = rt
        h1 = hstar[1] if d >= 1 else None
        hd = hstar[d]
        res["hstar_1"] = str(h1)
        res["hstar_d"] = str(hd)
        res["JACKPOT_engineB"] = bool(h1 is not None and hd > h1)
        res["TIER0_engineB"] = bool(h1 is not None and h1 == 0 and hd > 0)
        res["NEG_engineB"] = any(c < 0 for c in co)
        res["verdict"] = ("CONFIRMS_A" if (res["profile_matches_engineA"]
                                           and res["d_matches"]
                                           and res["hstar_matches"]
                                           and res["heldout_ok"] and rt)
                          else "MISMATCH")
        out.append(res)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
