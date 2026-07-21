#!/usr/bin/env python3
"""
ladder_climb.py -- BFS neighbourhood search around the known ladder-carrying
triples (h*_1 = 0 AND normalized volume sum h* >= 2), looking for sum h* >= 3.

Only the mandated LP-free instrument decides anything; nothing is filtered by
simplex-hood or by any LP dimension oracle.  The single admissible pruning is
the NECESSARY condition h*_1 = 0 <=> c = d+1 <= D+1 used to skip the exact
profile when c already exceeds D+1.

Moves: add/remove one box from lam or mu together with one box from nu so that
|lam| + |mu| = |nu| is preserved and all three stay partitions.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ladder_scan2 import _chunk_job          # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP  # noqa: E402


def norm(p):
    p = tuple(x for x in p if x > 0)
    return p if all(p[i] >= p[i + 1] for i in range(len(p) - 1)) else None


def box_moves(p, maxlen):
    """all partitions obtained by adding or removing exactly one box"""
    out = []
    for i in range(len(p) + 1):
        q = list(p) + ([0] if i == len(p) else [])
        if i >= len(q):
            continue
        q = list(p)
        if i == len(p):
            if len(p) + 1 <= maxlen:
                q = list(p) + [1]
            else:
                continue
        else:
            q[i] += 1
        n = norm(q)
        if n:
            out.append(n)
    for i in range(len(p)):
        q = list(p)
        q[i] -= 1
        n = norm(q)
        if n:
            out.append(n)
    return out


def neighbours(t, rmax=7):
    lam, mu, nu = t
    out = set()
    for j, nv in enumerate((True, False)):
        pass
    for newlam in box_moves(lam, rmax):
        d = sum(newlam) - sum(lam)
        for newnu in ([nu] if d == 0 else box_moves(nu, rmax)):
            if sum(newnu) - sum(nu) == d:
                out.add((newlam, mu, newnu))
    for newmu in box_moves(mu, rmax):
        d = sum(newmu) - sum(mu)
        for newnu in ([nu] if d == 0 else box_moves(nu, rmax)):
            if sum(newnu) - sum(nu) == d:
                out.add((lam, newmu, newnu))
    return {t2 for t2 in out
            if sum(t2[0]) + sum(t2[1]) == sum(t2[2]) and len(t2[2]) >= 3}


def screen(trips, workers=20, chunk=200):
    """returns list of records; groups by r so each chunk has one D"""
    byr = {}
    for t in trips:
        byr.setdefault(len(t[2]), []).append(t)
    jobs = []
    for r, ts in byr.items():
        D = (r - 1) * (r - 2) // 2
        # stage 1: cheap necessary condition
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in ts]
        out, err = engine_batch(lines, 2 * 10 ** 9, 100000)
        keep = []
        if err is None:
            for t, tok in zip(ts, out):
                try:
                    c = int(tok)
                except ValueError:
                    continue
                if 1 <= c <= D + 1:
                    keep.append(t)
        for s in range(0, len(keep), chunk):
            jobs.append((keep[s:s + chunk], D, 2 * 10 ** 9, 2000))
    res = []
    if not jobs:
        return res
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(_chunk_job, j) for j in jobs]):
            res.extend(fut.result())
    return res


def main(argv):
    seeds = []
    for l in open(os.path.join(HERE, "vm_V2.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        seeds.append((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"])))
    rounds = int(argv[1]) if len(argv) > 1 else 3
    dst = os.path.join(HERE, "ladder_climb.jsonl")
    seen = set(seeds)
    frontier = set(seeds)
    best = 2
    fout = open(dst, "w", encoding="utf-8")
    for rd in range(rounds):
        cand = set()
        for t in frontier:
            cand |= neighbours(t)
        cand -= seen
        seen |= cand
        print("round %d: %d candidates" % (rd, len(cand)), flush=True)
        recs = screen(list(cand))
        newf = set()
        for r in recs:
            if r["status"] != "OK" or not r.get("hstar") or r["d"] < 1:
                continue
            if r["hstar"][1] != 0:
                continue
            V = r["hstar_sum"]
            if V >= 2:
                fout.write(json.dumps(r) + "\n")
                newf.add((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"])))
                if V > best:
                    best = V
                    print("NEW MAX V=%d %s|%s|%s h*=%s" %
                          (V, r["lam"], r["mu"], r["nu"], r["hstar"]), flush=True)
            if r["neg"]:
                print("NEGATIVE COEFFICIENT: %s" % json.dumps(r), flush=True)
        fout.flush()
        print("round %d: %d screened, %d new ladder triples, best V=%d"
              % (rd, len(recs), len(newf), best), flush=True)
        frontier = newf
        if not frontier:
            break
    fout.close()
    print("best V =", best)


if __name__ == "__main__":
    main(sys.argv)
