#!/usr/bin/env python3
"""
fam8_d4.py -- FAMILY 8: exhaustive census of DEGREE-4 hive polytopes.

Enumerates every triple (lam, mu, nu) with len(nu) = r and |nu| <= N
(lam, mu with at most r parts, |lam|+|mu|=|nu|, lam <= mu lexicographically
by the c^nu_{lam,mu} = c^nu_{mu,lam} symmetry) and runs the MANDATED LP-free
instrument on all of them.

The ONLY triples skipped before the profile are those with c = P(1) <= 1:
  * c = 0  ==> P(n) = 0 for all n >= 1 by the saturation theorem (KTW), so
    there is no polytope at all;
  * c = 1  ==> P(n) = 1 for all n by Fulton's conjecture (theorem, KTW),
    so d = 0.
Both are THEOREMS, not heuristics.  No LP dimension oracle is used, no
triple is ever discarded for "not a simplex", and the c <= D+1 prune used by
earlier waves (which throws away every h*_1 > 0 polytope) is NOT applied.

Output: one JSON line per triple that survives to the profile stage.
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from remine import engine_batch, fmt, COUNT_CAP   # noqa: E402
from ladder_scan2 import _chunk_job               # noqa: E402


def partitions(n, maxlen, maxpart=None):
    def rec(n, mx, k):
        if n == 0:
            yield ()
            return
        if k == 0:
            return
        for f in range(min(n, mx), 0, -1):
            for rest in rec(n - f, f, k - 1):
                yield (f,) + rest
    return rec(n, maxpart if maxpart else n, maxlen)


def gen_triples(r, Nlo, Nhi, maxpart=None, plen=0):
    """plen > 0 restricts lam and mu to EXACTLY plen parts (the (p-1)(q-1)
    dimension source); plen = 0 means unrestricted (at most r parts)."""
    for N in range(Nlo, Nhi + 1):
        cache = {a: [p for p in partitions(a, r, maxpart)
                     if not plen or len(p) == plen] for a in range(1, N)}
        for nu in partitions(N, r, maxpart):
            if len(nu) != r:
                continue
            for a in range(1, N):
                lams = cache[a]
                mus = cache[N - a]
                for lam in lams:
                    for mu in mus:
                        if lam > mu:
                            continue
                        # c^nu_{lam,mu} != 0 forces lam, mu contained in nu
                        if any(lam[i] > nu[i] for i in range(len(lam))):
                            continue
                        if any(mu[i] > nu[i] for i in range(len(mu))):
                            continue
                        yield (lam, mu, nu)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--nlo", type=int, required=True)
    ap.add_argument("--nhi", type=int, required=True)
    ap.add_argument("--maxpart", type=int, default=0)
    ap.add_argument("--plen", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--chunk", type=int, default=150)
    ap.add_argument("--node-cap", type=int, default=2 * 10 ** 9)
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--stage1-batch", type=int, default=200000)
    args = ap.parse_args(argv[1:])

    r = args.r
    D = (r - 1) * (r - 2) // 2
    maxpart = args.maxpart or None
    trips = list(gen_triples(r, args.nlo, args.nhi, maxpart, args.plen))
    print("r=%d |nu| in [%d,%d] -> %d triples" % (r, args.nlo, args.nhi,
                                                  len(trips)), flush=True)

    # ---- stage 1: exact c = P(1); keep c >= 2 (theorem-backed prune only)
    keep = []
    t0 = time.time()
    for s in range(0, len(trips), args.stage1_batch):
        blk = trips[s:s + args.stage1_batch]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in blk]
        out, err = engine_batch(lines, args.node_cap, args.timeout)
        if err is not None:
            print("stage1 ERROR %s" % err, flush=True)
            return 1
        for t, tok in zip(blk, out):
            try:
                c = int(tok)
            except ValueError:
                print("stage1 UNRESOLVED", t, tok, flush=True)
                continue
            if c >= 2:
                keep.append(t)
        print("stage1 %d/%d kept %d (%.0fs)" % (s + len(blk), len(trips),
                                                len(keep), time.time() - t0),
              flush=True)

    # ---- stage 2: full exact profile + mandated screen, no further pruning
    jobs = [(keep[s:s + args.chunk], D, args.node_cap, args.timeout)
            for s in range(0, len(keep), args.chunk)]
    done = 0
    nd4 = 0
    bestV = 0
    with open(args.out, "w", encoding="utf-8") as f, \
            ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(_chunk_job, j) for j in jobs]
        for fut in as_completed(futs):
            for rec in fut.result():
                f.write(json.dumps(rec) + "\n")
                if rec.get("d") == 4:
                    nd4 += 1
                    bestV = max(bestV, sum(rec["hstar"]))
                if rec.get("neg"):
                    print("*** NEG ***", json.dumps(rec), flush=True)
            done += 1
            if done % 20 == 0:
                f.flush()
                print("chunk %d/%d  d4=%d bestV(d4)=%d  %.0fs"
                      % (done, len(jobs), nd4, bestV, time.time() - t0),
                      flush=True)
    print("done: %d chunks, d4=%d, bestV(d4)=%d, %.0fs"
          % (len(jobs), nd4, bestV, time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
