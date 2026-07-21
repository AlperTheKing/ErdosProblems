#!/usr/bin/env python3
"""
validate_hive4.py -- mandatory validation gate for hive4.py.

(i)   >= 400 random valid r=4 triples: hive4 L(1) must equal the LR coefficient
      from engine A (lr_hive.exe) AND engine B (engineB_lrrule.py) -- all three
      exactly equal.
(ii)  >= 60 of those: hive4's interpolated P must reproduce the stretched counts
      c(n*nu; n*lam, n*mu) from BOTH engines at n = 2, 3, 4.
(iii) Reeve tetrahedron T_q, q = 1..20 (in hive4.reeve_test).

Any mismatch is reported verbatim and makes the gate FAIL.  No tolerance, no
rounding, no float anywhere.
"""

import json
import os
import random
import subprocess
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive4  # noqa: E402

ENG = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "engine"))
ENGINE_A = os.path.join(ENG, "lr_hive.exe")
ENGINE_B = os.path.join(ENG, "engineB_lrrule.py")
CAP = 10 ** 12
HERE = os.path.dirname(os.path.abspath(__file__))


def ps(p):
    p = [x for x in p if x > 0]
    return ",".join(map(str, p)) if p else "0"


def run_batch(lines, tag):
    """Run both engines on the same batch file; return (outA, outB)."""
    bf = os.path.join(HERE, "_val_%s.batch" % tag)
    with open(bf, "w") as f:
        f.write("\n".join(lines) + "\n")
    a = subprocess.run([ENGINE_A, "--batch", bf], capture_output=True, text=True)
    b = subprocess.run([sys.executable, ENGINE_B, "--batch", bf],
                       capture_output=True, text=True)
    if a.returncode != 0:
        raise RuntimeError("engine A failed: " + a.stderr[:500])
    if b.returncode != 0:
        raise RuntimeError("engine B failed: " + b.stderr[:500])
    oa = [x for x in a.stdout.replace("\r", "").split("\n") if x.strip() != ""]
    ob = [x for x in b.stdout.replace("\r", "").split("\n") if x.strip() != ""]
    if len(oa) != len(lines) or len(ob) != len(lines):
        raise RuntimeError("engine output line count mismatch: %d/%d vs %d"
                           % (len(oa), len(ob), len(lines)))
    return oa, ob


def rand_partition(N, kmax, rng):
    """Uniform-ish random partition of N into at most kmax positive parts."""
    if N == 0:
        return []
    while True:
        k = rng.randint(1, kmax)
        cuts = sorted(rng.randint(0, N) for _ in range(k - 1))
        parts = []
        prev = 0
        for c in cuts + [N]:
            parts.append(c - prev)
            prev = c
        parts = sorted((x for x in parts if x > 0), reverse=True)
        if parts:
            return parts


def rand_partition_exact(N, k, rng):
    """Random partition of N into EXACTLY k positive parts (None if impossible)."""
    if N < k:
        return None
    p = rand_partition(N - k, k, rng)
    p = p + [0] * (k - len(p))
    return sorted((x + 1 for x in p), reverse=True)


def build_pool(target_pos=300, target_zero=100, seed=20260721404):
    rng = random.Random(seed)
    pos, zero = [], []
    tries = 0
    while (len(pos) < target_pos or len(zero) < target_zero) and tries < 400000:
        tries += 1
        N = rng.randint(4, 34)
        nu = rand_partition_exact(N, 4, rng)
        if nu is None:
            continue
        a = rng.randint(1, N - 1)
        lam = rand_partition(a, 4, rng)
        mu = rand_partition(N - a, 4, rng)
        key = (tuple(lam), tuple(mu), tuple(nu))
        r = hive4.analyze(lam, mu, nu)
        item = (lam, mu, nu, r)
        if r["c"] > 0:
            if len(pos) < target_pos and key not in [(tuple(x[0]), tuple(x[1]), tuple(x[2])) for x in pos[-0:]]:
                pos.append(item)
        else:
            if len(zero) < target_zero:
                zero.append(item)
    return pos, zero, tries


def main():
    print("=" * 78)
    print("hive4.py VALIDATION GATE")
    print("=" * 78)

    # ---------------------------------------------------------------- (iii)
    print("\n[iii] Reeve tetrahedron unit test, q = 1..20 (bypasses hives)")
    ok3, rows = hive4.reeve_test(20, verbose=False)
    neg_qs = [r["q"] for r in rows if r["neg"]]
    hstar_ok = all(r["hstar"] == [1, 0, r["q"] - 1, 0] for r in rows)
    sign_ok = neg_qs == list(range(13, 21))
    print("    all per-q checks pass : %s" % ok3)
    print("    h* = (1,0,q-1,0) all q: %s" % hstar_ok)
    print("    NEG detected exactly for q = %s  (expected 13..20): %s"
          % (neg_qs, sign_ok))
    print("    a1 at q=12,13         : %s , %s"
          % (rows[11]["a1"], rows[12]["a1"]))
    ok3 = ok3 and hstar_ok and sign_ok

    # ---------------------------------------------------------------- pool
    print("\n[pool] building random r=4 triples (nu has exactly 4 positive parts)")
    pos, zero, tries = build_pool()
    pool = pos + zero
    print("    %d triples with c>0, %d with c=0  (%d samples drawn)"
          % (len(pos), len(zero), tries))
    dims = {}
    for _, _, _, r in pool:
        dims[r["dim"]] = dims.get(r["dim"], 0) + 1
    print("    dim histogram: %s" % sorted(dims.items()))
    maxc = max(r["c"] for _, _, _, r in pool)
    print("    max c in pool: %d ; max vertex denominator: %d"
          % (maxc, max((r.get("max_denominator", 1) for _, _, _, r in pool))))

    # ---------------------------------------------------------------- (i)
    print("\n[i] cross-engine check of L(1) on %d triples" % len(pool))
    lines = ["%s;%s;%s;%d" % (ps(l), ps(m), ps(n), CAP) for l, m, n, _ in pool]
    oa, ob = run_batch(lines, "i")
    bad = []
    for (l, m, n, r), la, lb in zip(pool, oa, ob):
        mine = str(r["c"])
        if not (mine == la.strip() == lb.strip()):
            bad.append((ps(l), ps(m), ps(n), mine, la.strip(), lb.strip()))
    print("    agreements: %d / %d" % (len(pool) - len(bad), len(pool)))
    for x in bad[:20]:
        print("    MISMATCH lam=%s mu=%s nu=%s  hive4=%s A=%s B=%s" % x)
    ok1 = not bad

    # ---------------------------------------------------------------- (ii)
    print("\n[ii] stretched-count check at n = 2,3,4 (dilation == stretching)")
    cand = sorted(pos, key=lambda t: (-t[3]["dim"], -t[3]["c"]))
    sel = cand[:40] + cand[40:][:0]
    rest = [t for t in pos if t not in sel]
    rng = random.Random(777)
    rng.shuffle(rest)
    sel = sel + rest[:30]
    print("    selected %d triples (dim histogram %s)"
          % (len(sel), sorted({t[3]["dim"]: 0 for t in sel}.keys())))
    slines, meta = [], []
    for l, m, n, r in sel:
        for k in (2, 3, 4):
            slines.append("%s;%s;%s;%d" % (ps([k * x for x in l]),
                                           ps([k * x for x in m]),
                                           ps([k * x for x in n]), CAP))
            meta.append((l, m, n, r, k))
    sa, sb = run_batch(slines, "ii")
    bad2 = []
    for (l, m, n, r, k), la, lb in zip(meta, sa, sb):
        mine = hive4.polyval(r["poly"], k)
        assert mine.denominator == 1, (l, m, n, k, mine)
        s = str(mine.numerator)
        if not (s == la.strip() == lb.strip()):
            bad2.append((ps(l), ps(m), ps(n), k, s, la.strip(), lb.strip()))
    print("    agreements: %d / %d  (%d triples x 3 dilations)"
          % (len(meta) - len(bad2), len(meta), len(sel)))
    for x in bad2[:20]:
        print("    MISMATCH lam=%s mu=%s nu=%s n=%d  P(n)=%s A=%s B=%s" % x)
    ok2 = not bad2

    # ------------------------------------------------------- internal audits
    print("\n[internal] structural audits over the whole pool")
    nv = [r for _, _, _, r in pool if not r["empty"] and not r["verified"]]
    vx = [r for _, _, _, r in pool if not r["empty"] and not r["vol_crosscheck"]]
    de = [r for _, _, _, r in pool if not r["empty"] and not r["deg_eq_dim"]]
    print("    P interpolated from L(0..3) reproduces L(4),L(5): %d failures" % len(nv))
    print("    normalized volume == 6*lead(P)                  : %d failures" % len(vx))
    print("    deg P == dim Q                                  : %d failures" % len(de))
    ok4 = not nv and not vx and not de
    negs = [(l, m, n, r) for l, m, n, r in pool if r["neg"]]
    print("    triples with a strictly NEGATIVE coefficient    : %d" % len(negs))
    for l, m, n, r in negs[:10]:
        print("       NEG %s;%s;%s  P=%s" % (ps(l), ps(m), ps(n),
                                             [hive4._fmt_frac(c) for c in r["poly"]]))

    verdict = ok1 and ok2 and ok3 and ok4
    print("\n" + "=" * 78)
    print("GATE: %s  [i]=%s [ii]=%s [iii]=%s [internal]=%s"
          % ("PASS" if verdict else "FAIL", ok1, ok2, ok3, ok4))
    print("=" * 78)

    with open(os.path.join(HERE, "validation_report.json"), "w") as f:
        json.dump({
            "n_triples_i": len(pool), "mismatches_i": bad,
            "n_triples_ii": len(sel), "n_checks_ii": len(meta), "mismatches_ii": bad2,
            "reeve": rows, "reeve_neg_qs": neg_qs,
            "dim_histogram": {str(k): v for k, v in sorted(dims.items())},
            "max_c": maxc,
            "internal_failures": {"interp": len(nv), "volume": len(vx), "degree": len(de)},
            "negatives_found": len(negs),
            "verdict": "PASS" if verdict else "FAIL",
        }, f, indent=1, default=str)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
