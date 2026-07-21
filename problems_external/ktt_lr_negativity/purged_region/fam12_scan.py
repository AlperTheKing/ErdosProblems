#!/usr/bin/env python3
"""
fam12_scan.py -- ladder hunter 12 driver.

Family: STRUCTURED repeated-part / hook-shaped lam and mu (the exhaustive
fat-hook box (a^p,1^q)) against LONG nu (all partitions of |lam|+|mu| with
exactly r parts).

Instrument: ONLY lpfree_screen.screen_profile (exact profile -> exact
interpolation -> d -> h*).  No LP dimension oracle, no simplex test, nothing
discarded for "not a simplex".

The single admissible pre-filter is the NECESSARY arithmetic identity
    c = P(1) = (d+1) + h*_1,  d <= D = (r-1)(r-2)/2
so h*_1 <= H  =>  c <= D + 1 + H.  Triples above that bound have h*_1 > H and
are outside the tracked window; they are COUNTED, never called a verdict.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ladder_scan2 import _chunk_job                # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP    # noqa: E402
from fam12_gen import gen                          # noqa: E402


def run(triples, D, hmax, dst_f, stats, workers, chunk, node_cap, timeout):
    """stage 1 (c) then stage 2 (exact profile) for one r-class."""
    kept = []
    CH = 150000
    for s in range(0, len(triples), CH):
        part = triples[s:s + CH]
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (l, m, v) in part]
        out, err = engine_batch(lines, node_cap, 200000)
        if err:
            raise SystemExit("stage1 failed: %s" % err)
        for t, tok in zip(part, out):
            try:
                c = int(tok)
            except ValueError:
                stats["stage1_unresolved"] += 1
                continue
            if c == 0:
                stats["c_zero"] += 1
            elif c <= D + 1 + hmax:
                kept.append(t)
            else:
                stats["c_above_window"] += 1
    stats["stage1_total"] += len(triples)
    stats["stage2_total"] += len(kept)
    if not kept:
        return
    jobs = [(kept[s:s + chunk], D, node_cap, timeout)
            for s in range(0, len(kept), chunk)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_chunk_job, j) for j in jobs]
        ndone = 0
        for fut in as_completed(futs):
            for rec in fut.result():
                absorb(rec, stats, dst_f)
            ndone += 1
            if ndone % 25 == 0:
                print("   stage2 %d/%d chunks  bestV=%s bestV0=%s"
                      % (ndone, len(jobs), stats["bestV"], stats["bestV0"]),
                      flush=True)


def absorb(rec, stats, dst_f):
    st = rec.get("status")
    stats.setdefault("status_" + str(st), 0)
    stats["status_" + str(st)] += 1
    if st != "OK":
        return
    h = rec.get("hstar")
    if not h or rec.get("d", -1) < 1:
        return
    if not (rec.get("heldout_ok") and rec.get("hstar_roundtrip_ok")
            and rec.get("hstar_tail_zero")):
        stats["cert_fail"] += 1
        print("CERT FAIL: %s" % json.dumps(rec), flush=True)
        return
    V = rec["hstar_sum"]
    h1 = h[1]
    key = (V, rec["d"])
    if V > stats["bestV"]:
        stats["bestV"] = V
        stats["bestV_rec"] = rec
        print("NEW MAX V=%d (h1=%d, d=%d) %s|%s|%s h*=%s"
              % (V, h1, rec["d"], rec["lam"], rec["mu"], rec["nu"], h),
              flush=True)
        dst_f.write(json.dumps(rec) + "\n")
    if h1 == 0 and V > stats["bestV0"]:
        stats["bestV0"] = V
        stats["bestV0_rec"] = rec
        print("NEW MAX V(h1=0)=%d d=%d %s|%s|%s h*=%s"
              % (V, rec["d"], rec["lam"], rec["mu"], rec["nu"], h), flush=True)
        dst_f.write(json.dumps(rec) + "\n")
    if h1 <= 2 and V > stats["bestV2"]:
        stats["bestV2"] = V
        stats["bestV2_rec"] = rec
    # global minimum monomial coefficient (exact, as a string fraction)
    from fractions import Fraction
    mc = min(Fraction(c) for c in rec["coeffs_low_to_high"])
    if stats["minCoeff"] is None or mc < stats["minCoeff"]:
        stats["minCoeff"] = mc
        stats["minCoeff_rec"] = rec
    if h1 == 0:
        stats["h1zero"] += 1
        if V >= 2:
            stats["ladder_carriers"] += 1
            dst_f.write(json.dumps(rec) + "\n")
    if rec.get("neg"):
        stats["hits"].append(rec)
        print("*** NEGATIVE COEFFICIENT *** %s" % json.dumps(rec), flush=True)
        dst_f.write(json.dumps(rec) + "\n")
    dst_f.flush()


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", required=True, help="comma list of r values")
    ap.add_argument("--maxsize", type=int, required=True)
    ap.add_argument("--maxlen", type=int, required=True)
    ap.add_argument("--maxpart", type=int, default=None)
    ap.add_argument("--mu-all", action="store_true",
                    help="regime B: mu ranges over ALL partitions")
    ap.add_argument("--mu-maxsize", type=int, default=None)
    ap.add_argument("--hmax", type=int, default=2)
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--chunk", type=int, default=60)
    ap.add_argument("--node-cap", type=int, default=2 * 10 ** 9)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv[1:])

    rset = [int(x) for x in args.r.split(",")]
    stats = {"bestV": 0, "bestV0": 0, "bestV2": 0, "bestV_rec": None,
             "bestV0_rec": None, "bestV2_rec": None, "minCoeff": None,
             "minCoeff_rec": None, "h1zero": 0, "ladder_carriers": 0,
             "hits": [], "cert_fail": 0, "stage1_total": 0,
             "stage2_total": 0, "stage1_unresolved": 0, "c_zero": 0,
             "c_above_window": 0}
    t0 = time.time()
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rset:
            D = (r - 1) * (r - 2) // 2
            trips = gen([r], args.maxsize, args.maxlen, args.maxpart,
                        mu_all=args.mu_all, mu_maxsize=args.mu_maxsize)
            print("r=%d D=%d generated %d triples (%.0fs)"
                  % (r, D, len(trips), time.time() - t0), flush=True)
            run(trips, D, args.hmax, f, stats, args.workers, args.chunk,
                args.node_cap, args.timeout)
            print("r=%d done: stage2=%d h1zero=%d carriers=%d bestV=%d "
                  "bestV0=%d  (%.0fs)"
                  % (r, stats["stage2_total"], stats["h1zero"],
                     stats["ladder_carriers"], stats["bestV"],
                     stats["bestV0"], time.time() - t0), flush=True)
    stats["minCoeff"] = str(stats["minCoeff"])
    stats["secs"] = round(time.time() - t0, 1)
    stats["args"] = vars(args)
    with open(args.out + ".stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps({k: v for k, v in stats.items()
                      if k not in ("bestV_rec", "bestV0_rec", "bestV2_rec",
                                   "minCoeff_rec", "hits")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
