#!/usr/bin/env python3
"""
beam_fam5.py -- LADDER HUNTER 5: beam search over hive triples.

FITNESS  : V = Sum h*  under the HARD constraint h*_1 = 0; tie-break smaller d.
POPULATION: 40 elites, with a diversity reservation (per-d elites) so that
            large-d carriers are not crowded out by the mandated tie-break.
MOVES    : multi-box perturbations (+/-k on one part, or a new row of size k)
           applied to lam or mu together with a compensating move on nu so that
           |lam| + |mu| = |nu| is preserved and all three stay partitions.

INSTRUMENT: ONLY the mandated LP-free screen (lpfree_screen.screen_profile via
ladder_scan2._chunk_job): exact profile P(0..D+2) from engine A, exact
interpolation over Q, two held-out points, exact h*.  No LP dimension oracle,
no simplex filter, nothing discarded for "not a simplex".

The single admissible pruning is the NECESSARY condition
    h*_1 = c - (d+1),  d <= D  ==>  h*_1 <= K  requires  c <= D + 1 + K,
used with K = 2 so that the h*_1 <= 2 statistic is also collected.
"""
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ladder_scan2 import _chunk_job              # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP  # noqa: E402

RUN = os.path.join(HERE, "runs", "fam5")
os.makedirs(RUN, exist_ok=True)

RMAX = 7
KMAX = 6
NCAP = {4: 40, 5: 34, 6: 26, 7: 20}
POP = 40
H1_SLACK = 2
NODE_CAP = 3 * 10 ** 8      # SEARCH-EFFORT cap only; exceeded => UNRESOLVED

# regions already screened exhaustively by earlier waves of this campaign
# (ladder_r5/_hi/_n20: r=5, N<=20; ladder_r6/_hi/_n18b: r=6, N<=18;
#  ladder_r7: r=7, N<=14).  Every carrier found there had V = 2.
def covered(t):
    r = len(t[2])
    N = sum(t[2])
    return (r == 5 and N <= 20) or (r == 6 and N <= 18) or (r == 7 and N <= 14)


def is_part(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and all(x > 0 for x in p)


def variants(p, kmax=KMAX, rmax=RMAX):
    """(new partition, delta) obtained by +/-k on one part or a new row of k"""
    out = set()
    L = len(p)
    for i in range(L):
        for k in range(1, kmax + 1):
            q = list(p)
            q[i] += k
            if i == 0 or q[i] <= q[i - 1]:
                out.add((tuple(q), k))
            q = list(p)
            q[i] -= k
            if q[i] >= 0 and (i + 1 >= L or q[i] >= q[i + 1]):
                qq = tuple(x for x in q if x > 0)
                if is_part(qq):
                    out.add((qq, -k))
    for k in range(1, kmax + 1):
        if L < rmax and (L == 0 or k <= p[-1]):
            out.add((tuple(list(p) + [k]), k))
    return out


def neighbours(t, kmax=KMAX):
    lam, mu, nu = t
    nuv = variants(nu, kmax)
    nuby = {}
    for q, d in nuv:
        nuby.setdefault(d, []).append(q)
    nuby.setdefault(0, []).append(nu)
    out = set()
    for src, other, which in ((lam, mu, 0), (mu, lam, 1)):
        for q, d in variants(src, kmax):
            for nq in nuby.get(d, ()):
                if len(nq) < 3:
                    continue
                a, b = (q, other) if which == 0 else (other, q)
                if sum(a) + sum(b) != sum(nq):
                    continue
                out.add((a, b, nq))
    return out


def screen(trips, workers=16, chunk=25, timeout=180, wall=600):
    """exact instrument on a list of triples; returns records"""
    byr = {}
    for t in trips:
        byr.setdefault(len(t[2]), []).append(t)
    jobs = []
    n_stage1 = 0
    for r, ts in byr.items():
        D = (r - 1) * (r - 2) // 2
        keep = []
        CH = 100000
        for s in range(0, len(ts), CH):
            part = ts[s:s + CH]
            lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                     for (l, m, v) in part]
            out, err = engine_batch(lines, 2 * 10 ** 9, 100000)
            n_stage1 += len(part)
            if err is not None:
                print("  stage1 FAILED r=%d: %s" % (r, err), flush=True)
                continue
            for t, tok in zip(part, out):
                try:
                    c = int(tok)
                except ValueError:
                    continue
                if 1 <= c <= D + 1 + H1_SLACK:
                    keep.append(t)
        for s in range(0, len(keep), chunk):
            jobs.append((keep[s:s + chunk], D, NODE_CAP, timeout))
    res = []
    if jobs:
        ex = ProcessPoolExecutor(max_workers=workers)
        futs = [ex.submit(_chunk_job, j) for j in jobs]
        done = 0
        try:
            for fut in as_completed(futs, timeout=wall):
                done += 1
                try:
                    res.extend(fut.result())
                except Exception as e:      # a chunk that died is UNRESOLVED
                    print("  chunk failed: %r" % (e,), flush=True)
                if done % 20 == 0:
                    print("  chunks %d/%d" % (done, len(jobs)), flush=True)
        except Exception:
            print("  WALL: %d/%d chunks finished, rest abandoned"
                  % (done, len(jobs)), flush=True)
        ex.shutdown(wait=False, cancel_futures=True)
    return res, n_stage1


def frac(s):
    if "/" in s:
        a, b = s.split("/")
        return (int(a), int(b))
    return (int(s), 1)


def fless(x, y):
    return x[0] * y[1] < y[0] * x[1]


def main(argv):
    budget = float(argv[1]) if len(argv) > 1 else 2400.0
    t_end = time.time() + budget
    random.seed(20260721)

    seeds = set()
    car = json.load(open(os.path.join(HERE, "LADDER_CARRIERS_ALL.json")))
    for r in car:
        seeds.add((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"])))
    # the refuter and its infinite family (explicit)
    for k in range(4, 13):
        seeds.add(((2, 2, 1), (k, 3, 2, 1), (k + 1, 4, 3, 2, 1)))
    print("seeds: %d" % len(seeds), flush=True)

    pool = {}          # triple -> record (h*_1 = 0 carriers)
    for r in car:
        t = (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
        pool[t] = {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"],
                   "d": r["d"], "hstar": r["hstar"], "hstar_sum": r["V"],
                   "coeffs_low_to_high": r["coeffs"], "hstar_1": 0}

    seen = set(seeds)
    tested = 0
    best_V = 2
    best_rec = pool[((2, 2, 1), (4, 3, 2, 1), (5, 4, 3, 2, 1))]
    best_h1le2 = None
    best_M1 = None
    minco = None
    minco_rec = None
    hits = []
    traj = []
    fout = open(os.path.join(RUN, "carriers.jsonl"), "w", encoding="utf-8")
    fall = open(os.path.join(RUN, "screened_summary.jsonl"), "w", encoding="utf-8")

    beam = list(seeds)
    random.shuffle(beam)
    beam = beam[:POP]
    # make sure the refuter is in the beam
    beam = [((2, 2, 1), (4, 3, 2, 1), (5, 4, 3, 2, 1))] + beam[:POP - 1]

    gen = 0
    while time.time() < t_end:
        gen += 1
        cand = set()
        for t in beam:
            cand |= neighbours(t)
        cand = {t for t in cand if t not in seen and not covered(t)
                and 4 <= len(t[2]) <= RMAX
                and sum(t[2]) <= NCAP.get(len(t[2]), 0)}
        if not cand:
            print("gen %d: no new candidates" % gen, flush=True)
            break
        cand = list(cand)
        random.shuffle(cand)
        cand = cand[:6000]
        seen |= set(cand)
        t0 = time.time()
        recs, n1 = screen(cand)
        tested += len(cand)
        newcar = []
        for rec in recs:
            if rec.get("status") != "OK" or not rec.get("hstar"):
                continue
            d = rec["d"]
            if d < 1:
                continue
            h1 = rec["hstar"][1] if len(rec["hstar"]) > 1 else 0
            V = rec["hstar_sum"]
            # exact first moment: [n^{d-1}] P < 0  <=>  M1 > 0
            M1 = sum(hj * (2 * j - (d + 1))
                     for j, hj in enumerate(rec["hstar"]))
            if d >= 2 and (best_M1 is None or M1 > best_M1[0]):
                best_M1 = (M1, rec)
                print("NEW MAX M1=%d d=%d %s h*=%s"
                      % (M1, d, (rec["lam"], rec["mu"], rec["nu"]),
                         rec["hstar"]), flush=True)
            fall.write(json.dumps({"lam": rec["lam"], "mu": rec["mu"],
                                   "nu": rec["nu"], "d": d, "h1": h1,
                                   "V": V}) + "\n")
            if rec.get("neg"):
                print("NEGATIVE COEFFICIENT: %s" % json.dumps(rec), flush=True)
                hits.append(rec)
                json.dump(rec, open(os.path.join(
                    RUN, "hit_%d.json" % len(hits)), "w"), indent=1)
            for cs in rec["coeffs_low_to_high"]:
                f = frac(cs)
                if minco is None or fless(f, minco):
                    minco, minco_rec = f, rec
            if h1 <= 2:
                if best_h1le2 is None or V > best_h1le2["hstar_sum"]:
                    best_h1le2 = rec
            if h1 != 0:
                continue
            t = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
            if V >= 2:
                pool[t] = rec
                fout.write(json.dumps(rec) + "\n")
                newcar.append(t)
                if V > best_V:
                    best_V = V
                    best_rec = rec
                    print("NEW MAX V=%d %s h*=%s" %
                          (V, t, rec["hstar"]), flush=True)
        fout.flush()
        fall.flush()
        # ---- selection: fitness (V, -d) with per-d diversity reservation ----
        allc = sorted(pool.items(),
                      key=lambda kv: (-kv[1]["hstar_sum"], kv[1]["d"]))
        chosen, byd = [], {}
        for t, rec in allc:                    # per-d elite first (diversity)
            if rec["d"] not in byd:
                byd[rec["d"]] = t
        chosen.extend(byd.values())
        for t, rec in allc:
            if len(chosen) >= POP // 2:
                break
            if t not in chosen:
                chosen.append(t)
        fresh = [t for t in newcar if t not in chosen]
        random.shuffle(fresh)
        chosen.extend(fresh[:POP - len(chosen)])
        if len(chosen) < POP:
            rest = [t for t, _ in allc if t not in chosen]
            random.shuffle(rest)
            chosen.extend(rest[:POP - len(chosen)])
        beam = chosen
        line = {"gen": gen, "candidates": len(cand), "stage1": n1,
                "records": len(recs), "new_carriers": len(newcar),
                "pool": len(pool), "best_V": best_V,
                "secs": round(time.time() - t0, 1),
                "beam_d": sorted(len(t[2]) for t in beam)}
        traj.append(line)
        print(json.dumps(line), flush=True)
        json.dump(traj, open(os.path.join(RUN, "trajectory.json"), "w"), indent=1)

    fout.close()
    fall.close()
    summary = {
        "family": "beam search, fitness Sum h* under h*_1 = 0, tie-break smaller d",
        "generations": gen,
        "triples_tested": tested,
        "pool_size": len(pool),
        "best_V": best_V,
        "best_rec": best_rec,
        "best_h1le2": best_h1le2,
        "best_M1": ({"M1": best_M1[0], "rec": best_M1[1]} if best_M1 else None),
        "min_coeff": ("%d/%d" % minco) if minco else None,
        "min_coeff_rec": {k: minco_rec[k] for k in
                          ("lam", "mu", "nu", "d", "hstar",
                           "coeffs_low_to_high")} if minco_rec else None,
        "hits": hits,
        "trajectory": traj,
    }
    json.dump(summary, open(os.path.join(RUN, "summary.json"), "w"), indent=1)
    print(json.dumps({k: summary[k] for k in
                      ("generations", "triples_tested", "best_V",
                       "min_coeff")}, indent=1))


if __name__ == "__main__":
    main(sys.argv)
