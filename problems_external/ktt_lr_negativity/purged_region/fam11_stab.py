#!/usr/bin/env python3
"""
fam11_stab.py -- FAMILY 11, arm 2: the STABILISED asymmetric limit.

Observed (fam11 arm-1 experiment, exact): for every ladder carrier tested,
replacing (lam, mu, nu) by (lam, mu + t*e_1, nu + t*e_1) -- i.e. lengthening
the first row of mu and of nu together, which drives |lam|/|mu| -> 0 -- leaves
the whole Ehrhart profile, hence h* and every coefficient, INVARIANT for all
t >= 1.  So in the asymmetric limit only the TAIL (rows 2..r of mu and nu) and
lam matter; the weight ratio itself is not a free parameter.

This arm therefore enumerates the limit directly: pick lam, the tails
mu_t = (mu_2..mu_r), nu_t = (nu_2..nu_r), then set

    mu_1 = M = max(nu_2, mu_2) + s ,   nu_1 = M + delta ,
    delta = |lam| + |mu_t| - |nu_t|  (must be >= 0)

which realises an arbitrarily asymmetric split at bounded cost, and lets the
TAIL complexity go far past anything an |nu| <= N scan can reach.

The instrument is the mandated LP-free screen; stage 1 uses only the necessary
condition c <= D + 1 + hmax, and c <= 2 is skipped because it provably gives
normalized volume 1.
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


def sub_tails(nut):
    """all mu_t with 0 <= mu_i <= nu_i and mu_t weakly decreasing"""
    k = len(nut)
    out = []
    cur = [0] * k

    def rec(i):
        if i == k:
            out.append(tuple(cur))
            return
        hi = nut[i] if i == 0 else min(nut[i], cur[i - 1])
        for v in range(hi, -1, -1):
            cur[i] = v
            rec(i + 1)
        cur[i] = 0
    rec(0)
    return out


def gen_stab(r, tlo, thi, amax, s_list):
    """triples in the stabilised asymmetric limit; returns list"""
    trips = set()
    lamcache = {}
    k = r - 1
    for T in range(tlo, thi + 1):
        for nut in parts_exact(T, k):
            for mut in sub_tails(nut):
                mtail = sum(mut)
                for a in range(1, amax + 1):
                    delta = a + mtail - T
                    if delta < 0:
                        continue
                    lams = lamcache.setdefault(a, parts_upto(a, r))
                    for s in s_list:
                        M = max(nut[0], mut[0] if mut else 0) + s
                        mu = (M,) + tuple(x for x in mut if x > 0)
                        nu = (M + delta,) + nut
                        if len(nu) != r:
                            continue
                        for lam in lams:
                            if contained(lam, nu):
                                trips.add((lam, mu, nu))
    return sorted(trips)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--T", type=int, nargs=2, required=True,
                    help="range of |nu_2..nu_r|")
    ap.add_argument("--amax", type=int, default=8)
    ap.add_argument("--s", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--hmax", type=int, default=2)
    ap.add_argument("--cmin", type=int, default=3)
    ap.add_argument("--node-cap", type=int, default=2 * 10 ** 9)
    ap.add_argument("--timeout", type=int, default=4000)
    a = ap.parse_args(argv[1:])

    D = (a.r - 1) * (a.r - 2) // 2
    trips = gen_stab(a.r, a.T[0], a.T[1], a.amax, a.s)
    print("r=%d T=%d..%d amax=%d -> %d triples" %
          (a.r, a.T[0], a.T[1], a.amax, len(trips)), flush=True)
    keep = []
    CH = 200000
    for st in range(0, len(trips), CH):
        part = trips[st:st + CH]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in part]
        out, err = engine_batch(lines, a.node_cap, 100000)
        if err:
            raise SystemExit("stage1 %s" % err)
        for t, tok in zip(part, out):
            try:
                c = int(tok)
            except ValueError:
                continue
            if a.cmin <= c <= D + 1 + a.hmax:
                keep.append(t)
        print("stage1 %d/%d kept %d" % (min(st + CH, len(trips)), len(trips),
                                        len(keep)), flush=True)
    jobs = [(keep[s:s + a.chunk], D, a.node_cap, a.timeout)
            for s in range(0, len(keep), a.chunk)]
    n = 0
    t0 = time.time()
    with open(a.out, "a", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(_chunk_job, j) for j in jobs]
            for fut in as_completed(futs):
                for rec in fut.result():
                    f.write(json.dumps(rec) + "\n")
                f.flush()
                n += 1
                if n % 10 == 0:
                    print("stage2 chunk %d/%d %.0fs" % (n, len(jobs),
                                                        time.time() - t0),
                          flush=True)
    print("done %d generated %d screened %.0fs"
          % (len(trips), len(keep), time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
