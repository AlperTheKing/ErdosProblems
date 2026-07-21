#!/usr/bin/env python3
"""
band10 wave-2 INDEPENDENT verification (hunter 10 of 12, second pass).

Three exact checks, no floating point anywhere:

 (1) HOMOGENEITY.  Q(lam,mu,nu) depends on the 9 gaps only, up to a lattice
     translation, and b is linear-homogeneous in the gap vector g.  Hence
     Q(t g) = t Q(g) (up to translation) and therefore
         L_{Q(tg)}(n) = L_{Q(g)}(t n)   ==>   a_k(t g) = t^k a_k(g).
     In particular a_1 is HOMOGENEOUS OF DEGREE 1 in g, so
         { g : a_1(g) < 0 }  is a CONE.
     Consequence: an exhaustive census of the box [0,G]^9 settles every ray
     through that box, at every weight.  Verified here exactly on random g.

 (2) gapscan4.exe --one  vs  hive4.py  on random gap vectors (6a1, V, L1).

 (3) hive4.py  vs  LR engine A (lr_hive.exe) and engine B (engineB_lrrule.py)
     on the stretched counts c(n nu; n lam, n mu), n = 1..3.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.abspath(os.path.join(HERE, "..", ".."))
ENG = os.path.abspath(os.path.join(R4, "..", "engine"))
sys.path.insert(0, R4)
import hive4  # noqa: E402

GAPSCAN = os.path.join(R4, "gapscan4.exe")
LRA = os.path.join(ENG, "lr_hive.exe")
LRB = os.path.join(ENG, "engineB_lrrule.py")


def triple_from_gaps(g):
    """Exactly the realisation used by gapscan.cpp eval_gaps()."""
    a, b, c = g[0:3], g[3:6], g[6:9]
    Aw = 3 * a[2] + 2 * a[1] + a[0]
    Bw = 3 * b[2] + 2 * b[1] + b[0]
    Cw = 3 * c[2] + 2 * c[1] + c[0]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return None
    k = D // 4
    l4 = k if k >= 0 else 0
    n4 = -k if k < 0 else 0
    m4 = 0
    lam = [l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4]
    mu = [m4 + b[2] + b[1] + b[0], m4 + b[2] + b[1], m4 + b[2], m4]
    nu = [n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4]
    assert sum(lam) + sum(mu) == sum(nu)
    return lam, mu, nu


def rand_gap(rng, G):
    while True:
        g = [rng.randint(0, G) for _ in range(9)]
        t = triple_from_gaps(g)
        if t is None:
            continue
        return g, t


def coeffs(res):
    P = list(res["poly"])
    while len(P) < 4:
        P.append(Fraction(0))
    return P


def main():
    rng = random.Random(20260721 + 10)
    out = {"homogeneity": {"tested": 0, "fail": []},
           "gapscan_vs_hive4": {"tested": 0, "fail": []},
           "lr_engines": {"tested": 0, "fail": [], "capped": 0}}

    # ---------------- (1) homogeneity a_k(t g) = t^k a_k(g) ----------------
    n_h = 0
    for _ in range(400):
        g, t3 = rand_gap(rng, 9)
        r0 = hive4.analyze(*t3)
        if r0["dim"] != 3:
            continue
        P0 = coeffs(r0)
        for t in (2, 3):
            gt = [t * x for x in g]
            t3t = triple_from_gaps(gt)
            if t3t is None:
                continue
            rt = hive4.analyze(*t3t)
            Pt = coeffs(rt)
            ok = all(Pt[k] == Fraction(t) ** k * P0[k] for k in range(4))
            ok = ok and rt["volume_normalized"] == t ** 3 * r0["volume_normalized"]
            n_h += 1
            if not ok:
                out["homogeneity"]["fail"].append(
                    {"g": g, "t": t, "P0": [str(x) for x in P0],
                     "Pt": [str(x) for x in Pt]})
        if n_h >= 300:
            break
    out["homogeneity"]["tested"] = n_h

    # ---------------- (2) gapscan4.exe --one vs hive4.py -------------------
    n_g = 0
    for _ in range(400):
        g, t3 = rand_gap(rng, 12)
        r = hive4.analyze(*t3)
        p = subprocess.run([GAPSCAN, "--one"] + [str(x) for x in g],
                           capture_output=True, text=True)
        kv = dict(tok.split("=") for tok in p.stdout.split())
        L1 = int(kv["L1"])
        six = int(kv["6a1"])
        V = int(kv["V"])
        P = coeffs(r)
        exp_six = 6 * P[1] if r["c"] > 0 else None
        bad = None
        if r["c"] != L1:
            bad = "L1 %s vs %s" % (r["c"], L1)
        elif r["c"] > 0 and (Fraction(six) != 6 * P[1]
                             or Fraction(V) != r["volume_normalized"]):
            bad = "6a1 %s vs %s ; V %s vs %s" % (six, 6 * P[1], V,
                                                 r["volume_normalized"])
        n_g += 1
        if bad:
            out["gapscan_vs_hive4"]["fail"].append({"g": g, "why": bad})
        if n_g >= 250:
            break
    out["gapscan_vs_hive4"]["tested"] = n_g
    _ = exp_six

    # ---------------- (3) hive4 vs LR engines A and B ----------------------
    n_e = 0
    for _ in range(300):
        g, t3 = rand_gap(rng, 5)
        lam, mu, nu = t3
        r = hive4.analyze(lam, mu, nu)
        if r["c"] == 0:
            continue
        for n in (1, 2, 3):
            L = r["L"][n]
            sl = ",".join(str(n * x) for x in lam)
            sm = ",".join(str(n * x) for x in mu)
            sn = ",".join(str(n * x) for x in nu)
            pa = subprocess.run([LRA, sl, sm, sn, "100000000"],
                                capture_output=True, text=True)
            pb = subprocess.run([sys.executable, LRB, sl, sm, sn, "100000000"],
                                capture_output=True, text=True)
            ta = pa.stdout.strip().split()[-1] if pa.stdout.strip() else "ERR"
            tb = pb.stdout.strip().split()[-1] if pb.stdout.strip() else "ERR"
            if "CAP" in ta or "CAP" in tb:
                out["lr_engines"]["capped"] += 1
                continue
            n_e += 1
            if int(ta) != L or int(tb) != L:
                out["lr_engines"]["fail"].append(
                    {"lam": lam, "mu": mu, "nu": nu, "n": n,
                     "hive4": L, "A": ta, "B": tb})
        if n_e >= 120:
            break
    out["lr_engines"]["tested"] = n_e

    out["verdict"] = ("PASS" if not (out["homogeneity"]["fail"]
                                     or out["gapscan_vs_hive4"]["fail"]
                                     or out["lr_engines"]["fail"]) else "FAIL")
    with open(os.path.join(HERE, "b10w2_verify.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1)[:4000])


if __name__ == "__main__":
    main()
