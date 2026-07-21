#!/usr/bin/env python3
"""
ladder_scan.py -- exhaustive small-triple hunt for the ONLY thing that can climb
the negativity ladder: hive polytopes with  h*_1 = 0  and normalized volume
sum h* >= 2.

h*_1 = c - (d+1), so h*_1 = 0  <=>  c = d + 1 <= D + 1 with D = (r-1)(r-2)/2.
Stage 1 therefore batch-computes c = P(1) (one engine-A call) and keeps every
triple with 1 <= c <= D+1 -- a NECESSARY condition, no other filter.
Stage 2 runs the mandated LP-free instrument on the survivors.

Nothing is discarded for "not a simplex" and no LP dimension oracle is used.
"""
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENGINE_A = os.path.join(ROOT, "engine", "lr_hive.exe")
sys.path.insert(0, HERE)
from lpfree_screen import screen_profile  # noqa: E402
from remine import engine_batch, fmt, ambient_bound, COUNT_CAP, _profile_job  # noqa: E402


def parts_exact(N, k, maxpart=None):
    """partitions of N into EXACTLY k positive parts, weakly decreasing"""
    if maxpart is None:
        maxpart = N
    out = []

    def rec(rem, k, mx, cur):
        if k == 0:
            if rem == 0:
                out.append(tuple(cur))
            return
        if rem < k:
            return
        for p in range(min(mx, rem - (k - 1)), 0, -1):
            cur.append(p)
            rec(rem - p, k - 1, p, cur)
            cur.pop()
    rec(N, k, maxpart, [])
    return out


def parts_upto(N, kmax):
    out = []
    for k in range(1, kmax + 1):
        out.extend(parts_exact(N, k))
    return out


def contained(p, nu):
    for i, x in enumerate(p):
        if i >= len(nu) or x > nu[i]:
            return False
    return True


def gen(r, N):
    """all (lam,mu,nu): nu has exactly r parts, |nu|=N, |lam|+|mu|=N,
    lam,mu contained in nu (necessary for c>0)."""
    nus = parts_exact(N, r)
    cache = {}
    trips = []
    for nu in nus:
        for a in range(0, N + 1):
            pa = cache.setdefault(a, parts_upto(a, r) if a else [()])
            pb = cache.setdefault(N - a, parts_upto(N - a, r) if N - a else [()])
            for lam in pa:
                if not contained(lam, nu):
                    continue
                for mu in pb:
                    if not contained(mu, nu):
                        continue
                    trips.append((lam, mu, nu))
    return trips


def main(argv):
    r = int(argv[1])
    Nlo, Nhi = int(argv[2]), int(argv[3])
    dst = argv[4]
    workers = int(argv[5]) if len(argv) > 5 else 48
    D = (r - 1) * (r - 2) // 2
    allt = []
    for N in range(Nlo, Nhi + 1):
        t = gen(r, N)
        print("r=%d N=%d -> %d triples" % (r, N, len(t)), flush=True)
        allt.extend(t)
    print("total %d triples" % len(allt), flush=True)

    # stage 1: c
    keep = []
    CH = 200000
    for s in range(0, len(allt), CH):
        chunk = allt[s:s + CH]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in chunk]
        out, err = engine_batch(lines, 2 * 10 ** 9, 100000)
        if err:
            raise SystemExit("stage1 %s" % err)
        for t, tok in zip(chunk, out):
            try:
                c = int(tok)
            except ValueError:
                continue
            if 1 <= c <= D + 1:
                keep.append(t)
        print("stage1 %d/%d  kept %d" % (min(s + CH, len(allt)), len(allt), len(keep)),
              flush=True)

    jobs = [(i, l, m, v, 2 * 10 ** 9, 300) for i, (l, m, v) in enumerate(keep)]
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_profile_job, j) for j in jobs]
            for fut in as_completed(futs):
                f.write(json.dumps(fut.result()) + "\n")
                f.flush()
                n += 1
                if n % 500 == 0:
                    print("stage2 %d/%d" % (n, len(jobs)), flush=True)
    print("wrote %d" % n)


if __name__ == "__main__":
    main(sys.argv)
