#!/usr/bin/env python3
"""
fam6_scan.py -- TIER-0 FAMILY 6: MINIMAL-LATTICE-POINT hunt.

Family definition (exhaustive per (r, N)):
    all (lam, mu, nu) with nu a partition of N into EXACTLY r parts,
    |lam| + |mu| = N, lam and mu contained in nu (necessary for c > 0).

Stage 1 (one engine-A call per triple, n = 1): keep 1 <= c <= D+1 where
D = (r-1)(r-2)/2.  This is a NECESSARY condition for h*_1 = 0, since
h*_1 = c - (d+1) and d <= D.  Nothing else is filtered: no LP dimension
oracle, no simplex filter.

Stage 2: full exact profile P(0..D+2) from engine A -> the mandated LP-free
screen (tier0_screen.screen_profile) -> exact d, h*, coefficients, plus the
tier-0 fields h*_1, h*_d, TIER0, JACKPOT, NEG.

Tracked: max h*_d, min (h*_1 - h*_d), every TIER0 / JACKPOT / NEG record.
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

from tier0_screen import screen_profile              # noqa: E402  mandated
from remine import engine_batch, fmt                 # noqa: E402
from ladder_scan import gen                          # noqa: E402

COUNT_CAP = 10 ** 18


def _chunk_job(arg):
    trips, D, node_cap, timeout, full = arg
    lo = 0 if full else 0
    lines = []
    for (l, m, v) in trips:
        for n in range(D + 3):
            lines.append("%s;%s;%s;%d" % (
                fmt(tuple(n * x for x in l)), fmt(tuple(n * x for x in m)),
                fmt(tuple(n * x for x in v)), COUNT_CAP))
    out, err = engine_batch(lines, node_cap, timeout)
    res = []
    W = D + 3
    for i, (l, m, v) in enumerate(trips):
        head = {"lam": list(l), "mu": list(m), "nu": list(v),
                "r": len(v), "D": D}
        if err is not None:
            head["status"] = "UNRESOLVED_" + err
            res.append(head)
            continue
        vals = []
        for tok in out[i * W:(i + 1) * W]:
            try:
                vals.append(int(tok))
            except ValueError:
                vals.append(tok)
        if any(not isinstance(x, int) for x in vals):
            head["status"] = "UNRESOLVED_NODECAP"
            res.append(head)
            continue
        rec = screen_profile({n: vals[n] for n in range(W)}, D)
        rec.pop("degree_bound", None)
        head.update(rec)
        res.append(head)
    return res


def stage1(allt, D, node_cap, timeout, block=200000):
    keep = []
    ce = 0
    empt = 0
    rej = 0
    for s in range(0, len(allt), block):
        part = allt[s:s + block]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in part]
        out, err = engine_batch(lines, node_cap, timeout)
        if err:
            raise SystemExit("stage1 %s" % err)
        for t, tok in zip(part, out):
            try:
                c = int(tok)
            except ValueError:
                ce += 1
                continue
            if c == 0:
                empt += 1
            elif c <= D + 1:
                keep.append(t)
            else:
                rej += 1
        print("  stage1 %d/%d kept=%d empty=%d rejected=%d capfail=%d"
              % (min(s + block, len(allt)), len(allt), len(keep), empt,
                 rej, ce), flush=True)
    return keep, {"empty": empt, "rejected_c_gt_D1": rej, "cap_fail": ce}


def main(argv):
    r = int(argv[1])
    Nlo = int(argv[2])
    Nhi = int(argv[3])
    dst = argv[4]
    workers = int(argv[5]) if len(argv) > 5 else 32
    chunk = int(argv[6]) if len(argv) > 6 else 200
    timeout = int(argv[7]) if len(argv) > 7 else 3000
    D = (r - 1) * (r - 2) // 2
    t0 = time.time()
    allt = []
    for N in range(Nlo, Nhi + 1):
        t = gen(r, N)
        print("gen r=%d N=%d -> %d" % (r, N, len(t)), flush=True)
        allt.extend(t)
    print("total %d triples (r=%d, N=%d..%d, D=%d)"
          % (len(allt), r, Nlo, Nhi, D), flush=True)

    keep, s1 = stage1(allt, D, 2 * 10 ** 9, 200000)
    print("stage1 done: %d survivors of %d  %s  (%.1fs)"
          % (len(keep), len(allt), s1, time.time() - t0), flush=True)

    jobs = [(keep[s:s + chunk], D, 2 * 10 ** 9, timeout, True)
            for s in range(0, len(keep), chunk)]
    n = 0
    stats = {"OK": 0, "other": 0}
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_chunk_job, j) for j in jobs]
            for fut in as_completed(futs):
                for rec in fut.result():
                    f.write(json.dumps(rec) + "\n")
                    if rec.get("status") == "OK":
                        stats["OK"] += 1
                    else:
                        stats["other"] += 1
                f.flush()
                n += 1
                if n % 20 == 0 or n == len(jobs):
                    print("  stage2 chunk %d/%d  ok=%d other=%d  %.1fs"
                          % (n, len(jobs), stats["OK"], stats["other"],
                             time.time() - t0), flush=True)
    print("DONE r=%d N=%d..%d gen=%d surv=%d ok=%d other=%d wall=%.1fs"
          % (r, Nlo, Nhi, len(allt), len(keep), stats["OK"], stats["other"],
             time.time() - t0), flush=True)
    meta = {"r": r, "Nlo": Nlo, "Nhi": Nhi, "D": D, "generated": len(allt),
            "stage1": s1, "survivors": len(keep), "ok": stats["OK"],
            "other": stats["other"], "wall_s": round(time.time() - t0, 1),
            "out": dst, "exhaustive": True}
    with open(dst + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)


if __name__ == "__main__":
    main(sys.argv)
