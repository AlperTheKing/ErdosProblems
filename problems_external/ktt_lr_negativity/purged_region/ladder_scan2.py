#!/usr/bin/env python3
"""
ladder_scan2.py -- chunked (low process-spawn) version of ladder_scan.

Same mathematics, same mandated LP-free instrument; the only difference is that
one engine-A --batch call now serves CHUNK triples at once instead of one.

Stage 1 (necessary condition only): c = P(1) with 1 <= c <= D+1, since
h*_1 = c - (d+1) and d <= D = (r-1)(r-2)/2.  Nothing else is filtered.
Stage 2: exact profile P(0..D+2) -> exact interpolation -> d, h*, coefficients.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lpfree_screen import screen_profile          # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP   # noqa: E402
from ladder_scan import gen                       # noqa: E402


def _chunk_job(arg):
    trips, D, node_cap, timeout = arg
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


def main(argv):
    r = int(argv[1]); Nlo = int(argv[2]); Nhi = int(argv[3]); dst = argv[4]
    workers = int(argv[5]) if len(argv) > 5 else 24
    chunk = int(argv[6]) if len(argv) > 6 else 300
    D = (r - 1) * (r - 2) // 2
    allt = []
    for N in range(Nlo, Nhi + 1):
        t = gen(r, N)
        print("r=%d N=%d -> %d" % (r, N, len(t)), flush=True)
        allt.extend(t)
    print("total %d" % len(allt), flush=True)

    keep = []
    CH = 200000
    for s in range(0, len(allt), CH):
        part = allt[s:s + CH]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in part]
        out, err = engine_batch(lines, 2 * 10 ** 9, 200000)
        if err:
            raise SystemExit("stage1 %s" % err)
        for t, tok in zip(part, out):
            try:
                c = int(tok)
            except ValueError:
                continue
            if 1 <= c <= D + 1:
                keep.append(t)
        print("stage1 %d/%d kept %d" % (min(s + CH, len(allt)), len(allt),
                                        len(keep)), flush=True)

    jobs = [(keep[s:s + chunk], D, 2 * 10 ** 9, 3000)
            for s in range(0, len(keep), chunk)]
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_chunk_job, j) for j in jobs]
            for fut in as_completed(futs):
                for rec in fut.result():
                    f.write(json.dumps(rec) + "\n")
                f.flush()
                n += 1
                if n % 20 == 0:
                    print("stage2 chunk %d/%d" % (n, len(jobs)), flush=True)
    print("done %d chunks" % n)


if __name__ == "__main__":
    main(sys.argv)
