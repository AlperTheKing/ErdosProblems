#!/usr/bin/env python3
"""
fam11_asym.py -- FAMILY 11: hive polytopes from HIGHLY ASYMMETRIC weight splits
(|lam| much smaller than |mu|), swept systematically over ratio, shape and
weight.

Rationale.  The prior exhaustive scans covered r=5 up to |nu|=20, r=6 up to
|nu|=18, r=7 up to |nu|~14 -- all splits, symmetric and asymmetric.  The only
unexplored part of the asymmetric family is |nu| BEYOND those bounds, which is
exactly where the asymmetric parametrisation is cheap: with a = |lam| small the
number of (lam,mu) pairs per nu stays bounded (nu/mu is a skew shape with a
boxes), so |nu| can be pushed far past the exhaustive frontier.

Instrument: the mandated LP-free screen (lpfree_screen.screen_profile) via
ladder_scan2._chunk_job.  No LP dimension oracle, no simplex filter, nothing
discarded for "not a simplex".  Stage-1 uses ONLY the necessary condition
h*_1 = c - (d+1) with d <= D, i.e. c <= D + 1 + HMAX, so that h*_1 <= HMAX
survivors are all retained.

Usage:
  python fam11_asym.py --r 5 --N 21 24 --amax 8 --out runs/fam11/r5_n21_24.jsonl
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ladder_scan import parts_exact, parts_upto, contained   # noqa: E402
from ladder_scan2 import _chunk_job                           # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP               # noqa: E402


AMIN = [1]


def sub_partitions_removing(nu, a):
    """all partitions mu with mu subset nu and |nu| - |mu| = a (nu/mu = a boxes)"""
    r = len(nu)
    out = []
    cur = [0] * r

    def rec(i, rem):
        if i == r:
            if rem == 0:
                out.append(tuple(x for x in cur if x > 0))
            return
        # mu_i can range over [max(0, nu_i - rem) .. nu_i], and mu_i <= mu_{i-1}
        hi = nu[i] if i == 0 else min(nu[i], cur[i - 1])
        lo = max(0, nu[i] - rem)
        # remaining rows can absorb at most sum(nu[i+1:]) boxes
        tail = sum(nu[i + 1:])
        for v in range(hi, lo - 1, -1):
            drop = nu[i] - v
            if rem - drop > tail:
                continue
            cur[i] = v
            rec(i + 1, rem - drop)
        cur[i] = 0

    rec(0, a)
    return out


def gen_asym(r, N, amax):
    """triples with |nu| = N, nu exactly r parts, |lam| = a <= amax, |mu| = N-a.
    Both orders (lam,mu) and (mu,lam) give the same LR coefficient, so only the
    |lam| <= |mu| orientation is generated (a <= N/2 enforced)."""
    trips = []
    lamcache = {}
    for nu in parts_exact(N, r):
        for a in range(AMIN[0], min(amax, N // 2) + 1):
            lams = lamcache.setdefault(a, parts_upto(a, r))
            mus = sub_partitions_removing(nu, a)
            for mu in mus:
                for lam in lams:
                    if contained(lam, nu):
                        trips.append((lam, mu, nu))
    return trips


def run(r, Nlo, Nhi, amax, dst, workers, chunk, hmax, node_cap, timeout,
        stage1_timeout, cmin=3, amin=1):
    D = (r - 1) * (r - 2) // 2
    allt = []
    for N in range(Nlo, Nhi + 1):
        t = gen_asym(r, N, amax)
        print("r=%d N=%d amax=%d -> %d triples" % (r, N, amax, len(t)), flush=True)
        allt.extend(t)
    allt = sorted(set(allt))
    print("total %d distinct triples" % len(allt), flush=True)
    if not allt:
        return 0, 0

    keep = []
    CH = 200000
    for s in range(0, len(allt), CH):
        part = allt[s:s + CH]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in part]
        out, err = engine_batch(lines, node_cap, stage1_timeout)
        if err:
            raise SystemExit("stage1 %s" % err)
        for t, tok in zip(part, out):
            try:
                c = int(tok)
            except ValueError:
                continue
            # c <= 2 is provably V = 1 (c=1 => d=0; c=2 => d<=1 since h*_1 =
            # c-(d+1) >= 0, so V = 1): no ladder value, no negativity.
            if cmin <= c <= D + 1 + hmax:
                keep.append(t)
        print("stage1 %d/%d kept %d" % (min(s + CH, len(allt)), len(allt),
                                        len(keep)), flush=True)

    jobs = [(keep[s:s + chunk], D, node_cap, timeout)
            for s in range(0, len(keep), chunk)]
    n = 0
    t0 = time.time()
    with open(dst, "a", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_chunk_job, j) for j in jobs]
            for fut in as_completed(futs):
                for rec in fut.result():
                    f.write(json.dumps(rec) + "\n")
                f.flush()
                n += 1
                if n % 10 == 0:
                    print("stage2 chunk %d/%d  %.0fs" % (n, len(jobs),
                                                         time.time() - t0),
                          flush=True)
    print("done: %d generated, %d screened, %.0fs"
          % (len(allt), len(keep), time.time() - t0), flush=True)
    return len(allt), len(keep)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--N", type=int, nargs=2, required=True)
    ap.add_argument("--amax", type=int, default=8)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--chunk", type=int, default=120)
    ap.add_argument("--hmax", type=int, default=2)
    ap.add_argument("--node-cap", type=int, default=2 * 10 ** 9)
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--stage1-timeout", type=int, default=100000)
    ap.add_argument("--cmin", type=int, default=3)
    ap.add_argument("--amin", type=int, default=1)
    a = ap.parse_args(argv[1:])
    AMIN[0] = a.amin
    run(a.r, a.N[0], a.N[1], a.amax, a.out, a.workers, a.chunk, a.hmax,
        a.node_cap, a.timeout, a.stage1_timeout, a.cmin, a.amin)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
