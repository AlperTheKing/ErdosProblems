#!/usr/bin/env python3
"""fam6_beam.py -- targeted push on the ONLY non-trivial part of family 6.

Every family-6 record with h*_1 = 0 and Sum h* >= 2 seen so far has
h* = (1,0,1,0,...,0): the extra unit sits at j = 2, never at j = d.
TIER0 needs it at j = d.  This script explores the combinatorial
neighbourhood of those carriers, scoring by

    topj = max{ j : h*_j > 0 }        (want topj = d)
    score = (topj - 2, Sum h*, topj - d)

Neighbours: move one box between lam/mu/nu keeping |lam|+|mu| = |nu| and
all three weakly decreasing.  Full mandated LP-free screen on every
candidate; no LP oracle, no simplex filter.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PURGED = os.path.join(ROOT, "purged_region")
sys.path.insert(0, HERE)
sys.path.insert(0, PURGED)
from tier0_screen import screen_profile          # noqa: E402
from remine import engine_batch, fmt             # noqa: E402

COUNT_CAP = 10 ** 18


def valid(p):
    p = tuple(x for x in p if x > 0)
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)), p


def bump(p, i, delta):
    q = list(p)
    while len(q) <= i:
        q.append(0)
    q[i] += delta
    if q[i] < 0:
        return None
    ok, q = valid(q)
    return tuple(q) if ok else None


def neighbours(lam, mu, nu, rmax):
    out = set()
    LM = [("l", lam), ("m", mu)]
    for i in range(len(nu) + 1):
        for dn in (+1, -1):
            nu2 = bump(nu, i, dn)
            if nu2 is None or not nu2 or len(nu2) > rmax:
                continue
            for tag, p in LM:
                for j in range(len(p) + 1):
                    p2 = bump(p, j, dn)
                    if p2 is None:
                        continue
                    if len(p2) > len(nu2):
                        continue
                    if tag == "l":
                        cand = (p2, mu, nu2)
                    else:
                        cand = (lam, p2, nu2)
                    if sum(cand[0]) + sum(cand[1]) != sum(nu2):
                        continue
                    out.add(cand)
    # also two-box moves inside nu with a compensating move
    return out


def _job(arg):
    trips, node_cap, timeout = arg
    res = []
    lines = []
    meta = []
    for (l, m, v) in trips:
        D = (len(v) - 1) * (len(v) - 2) // 2
        meta.append(D)
        for n in range(D + 3):
            lines.append("%s;%s;%s;%d" % (
                fmt(tuple(n * x for x in l)), fmt(tuple(n * x for x in m)),
                fmt(tuple(n * x for x in v)), COUNT_CAP))
    out, err = engine_batch(lines, node_cap, timeout)
    if err is not None:
        return [{"lam": list(l), "mu": list(m), "nu": list(v),
                 "status": "UNRESOLVED_" + err} for (l, m, v) in trips]
    off = 0
    for i, (l, m, v) in enumerate(trips):
        D = meta[i]
        W = D + 3
        vals = []
        for tok in out[off:off + W]:
            try:
                vals.append(int(tok))
            except ValueError:
                vals.append(tok)
        off += W
        head = {"lam": list(l), "mu": list(m), "nu": list(v),
                "r": len(v), "D": D}
        if any(not isinstance(x, int) for x in vals):
            head["status"] = "UNRESOLVED_NODECAP"
            res.append(head)
            continue
        rec = screen_profile({n: vals[n] for n in range(W)}, D)
        rec.pop("degree_bound", None)
        head.update(rec)
        res.append(head)
    return res


def score(rec):
    if rec.get("status") != "OK":
        return None
    d = rec["d"]
    if d is None or d < 2:
        return None
    h = rec["hstar"]
    if h[1] != 0:
        return None
    S = sum(h)
    if S < 2:
        return None
    topj = max(j for j in range(d + 1) if h[j] > 0)
    return (topj, S, d, topj - d)


def main(argv):
    carriers = json.load(open(argv[1], encoding="utf-8"))
    dst = argv[2]
    rounds = int(argv[3]) if len(argv) > 3 else 3
    rmax = int(argv[4]) if len(argv) > 4 else 8
    workers = int(argv[5]) if len(argv) > 5 else 8
    beam = int(argv[6]) if len(argv) > 6 else 400

    frontier = [(tuple(z["lam"]), tuple(z["mu"]), tuple(z["nu"]))
                for z in carriers]
    seen = set(frontier)
    best = []
    hits = []
    t0 = time.time()
    fout = open(dst, "w", encoding="utf-8")
    for rd in range(rounds):
        cands = set()
        for (l, m, v) in frontier:
            cands |= neighbours(l, m, v, rmax)
        cands = [c for c in cands if c not in seen]
        seen |= set(cands)
        print("round %d: %d candidates (frontier %d)  %.0fs"
              % (rd, len(cands), len(frontier), time.time() - t0), flush=True)
        if not cands:
            break
        CH = 120
        jobs = [(cands[s:s + CH], 2 * 10 ** 9, 3000)
                for s in range(0, len(cands), CH)]
        newf = []
        nok = 0
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_job, j) for j in jobs]
            for fut in as_completed(futs):
                for rec in fut.result():
                    if rec.get("status") == "OK":
                        nok += 1
                    if rec.get("TIER0") or rec.get("JACKPOT") or \
                       rec.get("NEG") or rec.get("neg"):
                        hits.append(rec)
                        fout.write(json.dumps(rec) + "\n")
                    sc = score(rec)
                    if sc is not None:
                        fout.write(json.dumps(rec) + "\n")
                        newf.append((sc, (tuple(rec["lam"]),
                                          tuple(rec["mu"]),
                                          tuple(rec["nu"]))))
                        best.append((sc, rec["lam"], rec["mu"], rec["nu"],
                                     rec["hstar"]))
                fout.flush()
        newf.sort(key=lambda z: (-z[0][0], -z[0][1], z[0][3]))
        print("  round %d: %d screened OK, %d carriers, best topj=%s  hits=%d"
              % (rd, nok, len(newf), newf[0][0] if newf else None, len(hits)),
              flush=True)
        frontier = [z[1] for z in newf[:beam]]
        if not frontier:
            break
    fout.close()
    best.sort(key=lambda z: (-z[0][0], -z[0][1]))
    print("BEST:", json.dumps(best[:8]))
    print("hits:", len(hits))


if __name__ == "__main__":
    main(sys.argv)
