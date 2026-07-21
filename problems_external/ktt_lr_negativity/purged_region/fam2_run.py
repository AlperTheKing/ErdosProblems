#!/usr/bin/env python3
"""
fam2_run.py -- LADDER HUNTER 2 ("part growth" family).

FAMILY F2: take the known hive refuter cell
    lam = (2,2,1), mu = (4,3,2,1), nu = (5,4,3,2,1)      (r=5, d=4, h*=(1,0,1,0,0))
and GROW THE NUMBER OF PARTS while keeping the "one SHORT partition against one
LONG partition" asymmetry that made dim Q < ambient D.

Blocks
  A  staircase lift (exhaustive in lam, k):
        mu  = (k, t-1, t-2, ..., 2, 1)          (t parts, k >= t-1)
        nu  = (k+1, t, t-1, ..., 2, 1)          (t+1 parts)
        lam = any partition of t+1
     t = 4 reproduces the refuter cell; t = 5,6 are the 6- and 7-part lifts.
  B  general short-vs-long (exhaustive inside stated boxes):
        mu  ranges over LONG shapes with 5 or 6 parts (staircase-like and
            perturbations), lam over SHORT partitions with |lam| <= 8 and
            <= 4 parts, nu over EVERY partition with nu superset mu,
            |nu/mu| = |lam| and len(nu) <= len(mu)+2 <= 7.

INSTRUMENT: purged_region/lpfree_screen.py (screen_triples / screen_profile).
No LP dimension oracle, no simplex filter, nothing discarded for "not a simplex".

TIERING (stated honestly; the only pruning used)
  Tier 1  exact P(1) = c and P(2) for every family triple (engine A, exact).
          Stanley h*_j >= 0 gives  c = P(1) = (d+1) + h*_1, hence
              d = c - 1 - h*_1 <= c - 1,
          a CERTIFIED degree bound that is far smaller than the ambient
          D = (r-1)(r-2)/2 for the small-c triples we want.  When h*_1 = 0,
              h*_2 = P(2) - C(c+1, 2),
          so the cheap pair (P(1), P(2)) already measures the ladder.
  Tier 2  full mandated profile P(0..Db+2) with Db = min(D, c+1)   (two extra
          degrees of slack above the certified bound c-1), exact interpolation,
          two held-out points, h* by binomial transform, round-trip check.
          Run on every triple with c <= CMAX, and on every triple with
          P(2) > C(c+1,2) regardless of c (the ladder signal).
  Triples with c > CMAX and no ladder signal are recorded as TIER1_ONLY --
          this is a SEARCH BUDGET decision, never a math verdict.

All arithmetic exact (int / Fraction).  A negative census is NOT evidence for
the conjecture.
"""
import argparse
import itertools
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lpfree_screen import (engineA_batch, screen_triples, scale,  # noqa: E402
                           ambient_bound)

os.environ.setdefault("LR_HIVE_NODE_CAP", "4000000000")
CAP = 10 ** 18


# ---------------------------------------------------------------- partitions
def partitions(n, maxpart=None, maxlen=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    if maxlen is not None and maxlen <= 0:
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - k, k,
                               None if maxlen is None else maxlen - 1):
            yield (k,) + rest


def add_boxes(mu, m, maxlen):
    """every partition nu with nu >= mu (containment), |nu|-|mu| = m,
    len(nu) <= maxlen."""
    t = len(mu)
    slots = maxlen
    base = list(mu) + [0] * (slots - t)
    out = []

    def rec(i, left, prev_cap, cur):
        if i == slots:
            if left == 0:
                out.append(tuple(x for x in cur if x > 0))
            return
        # nu_i can be anything with base[i] <= nu_i <= prev_cap
        lo = base[i]
        hi = min(prev_cap, base[i] + left)
        if lo > prev_cap:
            return
        for v in range(lo, hi + 1):
            rec(i + 1, left - (v - base[i]), v, cur + [v])

    rec(0, m, 10 ** 9, [])
    return out


# ---------------------------------------------------------------- the family
def staircase(t):
    return tuple(range(t, 0, -1))


def block_A(tvals, kmax_extra):
    """mu=(k, t-1..1), nu=(k+1, t..1), lam |- t+1 (exhaustive in lam and k)."""
    out = []
    for t in tvals:
        tail = staircase(t - 1)           # (t-1, ..., 1)
        for k in range(t - 1, t - 1 + kmax_extra + 1):
            mu = (k,) + tail
            nu = (k + 1,) + staircase(t)
            if any(mu[i] < mu[i + 1] for i in range(len(mu) - 1)):
                continue
            for lam in partitions(t + 1):
                if sum(lam) + sum(mu) != sum(nu):
                    continue
                out.append((lam, mu, nu))
    return out


def block_B(mus, lam_size_max, lam_len_max, extra_len):
    out = []
    for mu in mus:
        maxlen = min(7, len(mu) + extra_len)
        for m in range(1, lam_size_max + 1):
            lams = [l for l in partitions(m) if len(l) <= lam_len_max]
            if not lams:
                continue
            nus = add_boxes(mu, m, maxlen)
            for nu in nus:
                if len(nu) < 3:
                    continue
                for lam in lams:
                    out.append((lam, mu, nu))
    return out


def long_mus():
    """LONG shapes: 5- and 6-part staircase-like partitions."""
    ms = set()
    for t in (5, 6):
        st = staircase(t)
        for k in range(t, t + 8):          # (k, t-1, ..., 1)
            ms.add((k,) + st[1:])
        ms.add(st)
        # mild perturbations of the staircase (still strictly long)
        for i in range(t):
            for delta in (1, 2):
                q = list(st)
                q[i] += delta
                if all(q[j] >= q[j + 1] for j in range(t - 1)):
                    ms.add(tuple(q))
    return sorted(ms)


# ---------------------------------------------------------------- tier 1
def tier1_chunk(trips):
    jobs = []
    for (lam, mu, nu) in trips:
        for n in (1, 2):
            jobs.append((scale(lam, n), scale(mu, n), scale(nu, n)))
    vals = engineA_batch(jobs, cap=CAP)
    out = []
    for i, t in enumerate(trips):
        out.append((t, vals[2 * i], vals[2 * i + 1]))
    return out


# ---------------------------------------------------------------- tier 2
def tier2_chunk(items):
    """items: list of (triple, Db).  Grouped by Db inside."""
    res = []
    byd = {}
    for t, Db in items:
        byd.setdefault(Db, []).append(t)
    for Db, trips in byd.items():
        res.extend(screen_triples(trips, cap=CAP, dbound=Db))
    return res


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "fam2"))
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--cmax", type=int, default=10)
    ap.add_argument("--tier1-chunk", type=int, default=60)
    ap.add_argument("--tier2-chunk", type=int, default=6)
    ap.add_argument("--budget", type=float, default=1800.0)
    ap.add_argument("--tag", default="run1")
    ap.add_argument("--blocks", default="AB")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    trips = []
    if "A" in args.blocks:
        trips += block_A([4, 5, 6], 6)
    if "B" in args.blocks:
        trips += block_B(long_mus(), 8, 4, 2)
    seen = set()
    fam = []
    for t in trips:
        if sum(t[0]) + sum(t[1]) != sum(t[2]):
            continue
        if len(t[2]) < 3 or len(t[2]) > 7:
            continue
        if t in seen:
            continue
        seen.add(t)
        fam.append(t)
    fam.sort(key=lambda t: (len(t[2]), sum(t[2])))
    print("family size %d" % len(fam), flush=True)

    t0 = time.time()
    t1_path = os.path.join(args.out, "tier1_%s.jsonl" % args.tag)
    t2_path = os.path.join(args.out, "tier2_%s.jsonl" % args.tag)

    # ---- tier 1
    chunks = [fam[i:i + args.tier1_chunk]
              for i in range(0, len(fam), args.tier1_chunk)]
    tier1 = []
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(tier1_chunk, c): c for c in chunks}
        with open(t1_path, "w") as f:
            for fu in as_completed(futs):
                try:
                    rows = fu.result()
                except Exception as e:                    # noqa: BLE001
                    print("tier1 chunk failed: %r" % (e,), flush=True)
                    continue
                for (t, c, p2) in rows:
                    rec = {"lam": list(t[0]), "mu": list(t[1]), "nu": list(t[2]),
                           "c": c if isinstance(c, int) else str(c),
                           "P2": p2 if isinstance(p2, int) else str(p2)}
                    f.write(json.dumps(rec) + "\n")
                    tier1.append((t, c, p2))
                done += 1
                if done % 20 == 0:
                    print("tier1 %d/%d chunks  %.0fs"
                          % (done, len(chunks), time.time() - t0), flush=True)
    print("tier1 done: %d triples, %.0fs" % (len(tier1), time.time() - t0),
          flush=True)

    # ---- select tier 2
    sel = []
    tier1_only = 0
    for (t, c, p2) in tier1:
        if not isinstance(c, int) or c <= 0:
            continue
        D = ambient_bound(t[2])
        ladder = isinstance(p2, int) and p2 > math.comb(c + 1, 2)
        if c <= args.cmax or ladder:
            Db = min(D, c + 1)
            if Db < 1:
                continue
            sel.append((t, Db))
        else:
            tier1_only += 1
    sel.sort(key=lambda x: (x[1], len(x[0][2])))
    print("tier2 selected %d (tier1_only %d)" % (len(sel), tier1_only),
          flush=True)

    chunks = [sel[i:i + args.tier2_chunk]
              for i in range(0, len(sel), args.tier2_chunk)]
    nrec = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(tier2_chunk, c): c for c in chunks}
        with open(t2_path, "w") as f:
            done = 0
            for fu in as_completed(futs):
                done += 1
                try:
                    recs = fu.result()
                except Exception as e:                    # noqa: BLE001
                    print("tier2 chunk failed: %r" % (e,), flush=True)
                    continue
                for r in recs:
                    f.write(json.dumps(r) + "\n")
                    nrec += 1
                    if r.get("neg"):
                        print("*** NEG *** %s" % json.dumps(r)[:500],
                              flush=True)
                f.flush()
                if done % 25 == 0:
                    print("tier2 %d/%d chunks  %d recs  %.0fs"
                          % (done, len(chunks), nrec, time.time() - t0),
                          flush=True)
                if time.time() - t0 > args.budget:
                    print("BUDGET REACHED after %d/%d tier2 chunks"
                          % (done, len(chunks)), flush=True)
                    for g in futs:
                        g.cancel()
                    break
    print("tier2 done: %d records, %.0fs" % (nrec, time.time() - t0),
          flush=True)


if __name__ == "__main__":
    main()
