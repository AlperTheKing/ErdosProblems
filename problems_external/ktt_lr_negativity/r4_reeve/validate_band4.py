#!/usr/bin/env python3
"""
validate_band4.py -- gate the fast C++ band scanner band4.exe against the
already-cross-calibrated exact Python engine hive4.py, and (on a sample) against
the two independent exact LR counters (engine A lr_hive.exe, engine B
engineB_lrrule.py).

Mode 1 (--agg WLO WHI):
  Enumerate the SAME triple set band4.exe enumerates (nu, lam, mu all partitions
  into at most 4 parts, |lam|+|mu|=|nu|=W, ordered pairs, no symmetry reduction)
  and recompute every aggregate with hive4.analyze.  Then compare against
  band4.exe's own per-W line.  Any mismatch is a hard failure.

Mode 2 (--sample W N SEED):
  Draw N random triples of weight W, and for each compare
      band4.exe --one   vs   hive4.analyze   vs   engine A   vs   engine B
  at n = 1, 2 (stretched LR counts).  Any mismatch is a hard failure.
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

BAND4 = os.path.join(HERE, "band4.exe")
ENGA = os.path.abspath(os.path.join(HERE, "..", "engine", "lr_hive.exe"))
ENGB = os.path.abspath(os.path.join(HERE, "..", "engine", "engineB_lrrule.py"))


def parts_le(N, k=4):
    out = []

    def rec(rem, mx, cur):
        if rem == 0:
            out.append(tuple(cur))
            return
        if len(cur) == k:
            return
        for v in range(min(rem, mx), 0, -1):
            cur.append(v)
            rec(rem - v, v, cur)
            cur.pop()

    rec(N, N, [])
    return out


def agg(wlo, whi):
    fail = 0
    for W in range(wlo, whi + 1):
        PT = {a: parts_le(a) for a in range(W + 1)}
        ntrip = 0
        nonempty = 0
        dimhist = {0: 0, 1: 0, 2: 0, 3: 0}
        min6a1 = None
        min6a1_d3 = None
        maxV = -1
        maxVh1 = -1
        negs = []
        for nu in PT[W]:
            for a in range(W + 1):
                for lam in PT[a]:
                    for mu in PT[W - a]:
                        ntrip += 1
                        r = hive4.analyze(list(lam), list(mu), list(nu))
                        if r["empty"]:
                            continue
                        nonempty += 1
                        d = r["dim"]
                        dimhist[d] = dimhist.get(d, 0) + 1
                        P = r["poly"]
                        a1 = P[1] if len(P) > 1 else Fraction(0)
                        six = 6 * a1
                        assert six.denominator == 1
                        six = int(six)
                        V = int(r["volume_normalized"])
                        if d >= 1 and (min6a1 is None or six < min6a1):
                            min6a1 = six
                        if d == 3 and (min6a1_d3 is None or six < min6a1_d3):
                            min6a1_d3 = six
                        if V > maxV:
                            maxV = V
                        if r["c"] == d + 1 and V > maxVh1:
                            maxVh1 = V
                        if r["neg"]:
                            negs.append((lam, mu, nu, [str(x) for x in P]))
                        if not (r["verified"] and r["vol_crosscheck"] and r["deg_eq_dim"]):
                            print("INTERNAL AUDIT FAIL", lam, mu, nu)
                            fail += 1
        out = subprocess.run([BAND4, str(W), str(W)], capture_output=True, text=True).stdout
        line = [l for l in out.splitlines() if l.startswith("W=%d " % W)][0]
        kv = dict(t.split("=", 1) for t in line.split())
        exp = {
            "triples": ntrip, "nonempty": nonempty,
            "dim0": dimhist[0], "dim1": dimhist[1], "dim2": dimhist[2], "dim3": dimhist[3],
            "maxV": maxV, "maxV_h1zero": maxVh1, "NEG": len(negs),
        }
        bad = []
        for k, v in exp.items():
            if int(kv[k]) != v:
                bad.append((k, kv[k], v))
        if min6a1 is not None and int(kv["min6a1"]) != min6a1:
            bad.append(("min6a1", kv["min6a1"], min6a1))
        if min6a1_d3 is not None and int(kv["min6a1_d3"]) != min6a1_d3:
            bad.append(("min6a1_d3", kv["min6a1_d3"], min6a1_d3))
        print("W=%-3d python: triples=%d nonempty=%d dims=%s min6a1=%s min6a1_d3=%s maxV=%d maxVh1=%d neg=%d  -> %s"
              % (W, ntrip, nonempty, [dimhist[i] for i in range(4)], min6a1, min6a1_d3,
                 maxV, maxVh1, len(negs), "MATCH" if not bad else "MISMATCH %s" % bad))
        if bad:
            fail += 1
    return fail


def _ps(p):
    return ",".join(str(x) for x in p) if p else "0"


def engineA(lam, mu, nu):
    r = subprocess.run([ENGA, _ps(lam), _ps(mu), _ps(nu), "100000000"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def engineB(lam, mu, nu):
    r = subprocess.run([sys.executable, ENGB, _ps(lam), _ps(mu), _ps(nu), "100000000"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def band4_one(lam, mu, nu):
    p = list(lam) + [0] * (4 - len(lam))
    q = list(mu) + [0] * (4 - len(mu))
    s = list(nu) + [0] * (4 - len(nu))
    r = subprocess.run([BAND4, "--one", ",".join(map(str, p)), ",".join(map(str, q)),
                        ",".join(map(str, s))], capture_output=True, text=True)
    return r.stdout.strip()


def sample(W, N, seed):
    random.seed(seed)
    PT = {a: parts_le(a) for a in range(W + 1)}
    fail = 0
    done = 0
    tried = 0
    while done < N and tried < 400 * N:
        tried += 1
        nu = random.choice(PT[W])
        a = random.randrange(W + 1)
        lam = random.choice(PT[a])
        mu = random.choice(PT[W - a])
        r = hive4.analyze(list(lam), list(mu), list(nu))
        if r["empty"]:
            continue
        done += 1
        b4 = band4_one(lam, mu, nu)
        kv = dict(t.split("=", 1) for t in b4.split())
        L = [int(x) for x in kv["L"].split(",")]
        ok = (L[:5] == r["L"][1:6])
        # stretched LR cross-engines at n = 1, 2
        ea1 = engineA(lam, mu, nu)
        eb1 = engineB(lam, mu, nu)
        lam2 = [2 * x for x in lam]
        mu2 = [2 * x for x in mu]
        nu2 = [2 * x for x in nu]
        ea2 = engineA(lam2, mu2, nu2)
        eb2 = engineB(lam2, mu2, nu2)
        ok2 = (ea1 == str(r["L"][1]) and eb1 == str(r["L"][1])
               and ea2 == str(r["L"][2]) and eb2 == str(r["L"][2]))
        if not (ok and ok2):
            fail += 1
            print("MISMATCH", lam, mu, nu, "hive4 L=", r["L"][1:6], "band4=", b4,
                  "A1/B1=", ea1, eb1, "A2/B2=", ea2, eb2)
        else:
            print("ok %-14s %-14s %-16s L=%s  A/B n=1:%s,%s n=2:%s,%s"
                  % (_ps(lam), _ps(mu), _ps(nu), r["L"][1:4], ea1, eb1, ea2, eb2))
    print("sample W=%d: %d nonempty triples checked, %d failures" % (W, done, fail))
    return fail


if __name__ == "__main__":
    if sys.argv[1] == "--agg":
        sys.exit(1 if agg(int(sys.argv[2]), int(sys.argv[3])) else 0)
    if sys.argv[1] == "--sample":
        sys.exit(1 if sample(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])) else 0)
    print("usage: --agg WLO WHI | --sample W N SEED")
    sys.exit(2)
