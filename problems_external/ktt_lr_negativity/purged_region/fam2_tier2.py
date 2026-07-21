#!/usr/bin/env python3
"""
fam2_tier2.py -- adaptive full-profile pass for FAMILY F2 (ladder hunter 2).

For each triple it computes the exact stretched profile P(0), P(1), ... with
engine A, one dilate at a time, and after each new point applies the MANDATED
LP-free instrument (lpfree_screen.screen_profile) with degree bound D = m:
exact Newton interpolation through n = 0..m, TWO held-out points m+1, m+2,
h* by binomial transform, tail-zero check and h*-round-trip check.  The first
m for which all of those pass -- and which is additionally confirmed by a
THIRD held-out point m+3 -- is accepted; the record stores
degree_bound_source = "adaptive_verified_m+3".

There is no LP dimension oracle, no simplex test, and nothing is discarded for
"not a simplex".  A triple that exceeds the wall-clock or dilate budget is
recorded as UNRESOLVED -- a search-budget fact, never a math verdict.

Rigorous outer bound used: Stanley h* >= 0 gives P(1) = c = (d+1) + h*_1,
hence deg P = d <= c - 1.
"""
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("LR_HIVE_NODE_CAP", "6000000000")
from lpfree_screen import (engineA_batch, screen_profile, scale,  # noqa: E402
                           ambient_bound, newton_interpolate, poly_eval)

CAP = 10 ** 18


def profile_one(lam, mu, nu, tbudget=25.0, nmax=16):
    D = ambient_bound(nu)
    prof = {}
    t0 = time.time()
    # c first (cheap) -> certified outer degree bound c-1
    v = engineA_batch([(scale(lam, 1), scale(mu, 1), scale(nu, 1))], cap=CAP)[0]
    if not isinstance(v, int):
        return {"status": "CAP_EXCEEDED", "failed_n": 1}
    prof[0] = 1
    prof[1] = v
    c = v
    if c == 0:
        return {"status": "EMPTY", "c": 0, "d": -1, "neg": False,
                "hstar_sum": 0}
    dmax = min(D, c - 1)
    nlimit = min(nmax, dmax + 3)
    n = 2
    while n <= nlimit:
        v = engineA_batch([(scale(lam, n), scale(mu, n), scale(nu, n))],
                          cap=CAP)[0]
        if not isinstance(v, int):
            return {"status": "CAP_EXCEEDED", "failed_n": n,
                    "profile_partial": [prof[i] for i in sorted(prof)]}
        prof[n] = v
        # try to accept degree m = n-2 (needs nodes 0..m + heldout m+1,m+2)
        m = n - 2
        if m >= 0:
            rec = screen_profile({k: prof[k] for k in range(m + 3)}, m)
            if (rec.get("status") == "OK" and rec.get("heldout_ok")
                    and rec.get("hstar_tail_zero")
                    and rec.get("hstar_roundtrip_ok")
                    and rec.get("hstar_nonneg")):
                # third confirmation point
                if m + 3 in prof:
                    third = prof[m + 3]
                else:
                    if time.time() - t0 > tbudget:
                        return {"status": "TIME_BUDGET", "c": c,
                                "profile_partial": [prof[i] for i in
                                                    sorted(prof)]}
                    tv = engineA_batch([(scale(lam, m + 3), scale(mu, m + 3),
                                         scale(nu, m + 3))], cap=CAP)[0]
                    if not isinstance(tv, int):
                        rec["degree_bound_source"] = \
                            "adaptive_verified_m+2_only(cap at m+3)"
                        rec["third_check"] = "CAP_EXCEEDED"
                        return rec
                    prof[m + 3] = tv
                    third = tv
                coeffs = [__import__("fractions").Fraction(x) for x in
                          rec["coeffs_low_to_high"]]
                pv = poly_eval(coeffs, m + 3)
                rec["third_check"] = {"n": m + 3, "engine": third,
                                      "poly": str(pv), "match": pv == third}
                if pv != third:
                    n += 1
                    continue
                rec["degree_bound_source"] = "adaptive_verified_m+3"
                rec["certified_outer_bound"] = {"ambient_D": D,
                                                "c_minus_1": c - 1}
                return rec
        if time.time() - t0 > tbudget:
            return {"status": "TIME_BUDGET", "c": c,
                    "profile_partial": [prof[i] for i in sorted(prof)]}
        n += 1
    return {"status": "UNRESOLVED_DEGREE", "c": c,
            "profile_partial": [prof[i] for i in sorted(prof)],
            "dmax": dmax}


def work(chunk):
    out = []
    for (lam, mu, nu, tb) in chunk:
        try:
            rec = profile_one(tuple(lam), tuple(mu), tuple(nu), tbudget=tb)
        except Exception as e:                            # noqa: BLE001
            rec = {"status": "ERROR", "err": repr(e)[:200]}
        rec = dict(rec)
        rec["lam"] = list(lam)
        rec["mu"] = list(mu)
        rec["nu"] = list(nu)
        rec["r"] = len(nu)
        out.append(rec)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--chunk", type=int, default=4)
    ap.add_argument("--budget", type=float, default=1500.0)
    ap.add_argument("--tb", type=float, default=25.0)
    args = ap.parse_args()

    todo = []
    for ln in open(args.todo):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        todo.append((r["lam"], r["mu"], r["nu"], args.tb))
    chunks = [todo[i:i + args.chunk] for i in range(0, len(todo), args.chunk)]
    t0 = time.time()
    nrec = 0
    best = (0, None)
    bestz = (0, None)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(work, c) for c in chunks]
        with open(args.out, "w") as f:
            done = 0
            for fu in as_completed(futs):
                done += 1
                try:
                    recs = fu.result()
                except Exception as e:                    # noqa: BLE001
                    print("chunk failed %r" % (e,), flush=True)
                    continue
                for r in recs:
                    f.write(json.dumps(r) + "\n")
                    nrec += 1
                    V = r.get("hstar_sum")
                    if isinstance(V, int):
                        if V > best[0]:
                            best = (V, r)
                            print("BEST V=%d %s %s %s h*=%s h1=%s"
                                  % (V, r["lam"], r["mu"], r["nu"],
                                     r.get("hstar"), r.get("hstar_1")),
                                  flush=True)
                        if r.get("hstar_1") == 0 and V > bestz[0]:
                            bestz = (V, r)
                            print("BEST-h1=0 V=%d %s %s %s h*=%s"
                                  % (V, r["lam"], r["mu"], r["nu"],
                                     r.get("hstar")), flush=True)
                    if r.get("neg"):
                        print("*** NEG *** " + json.dumps(r)[:600], flush=True)
                f.flush()
                if done % 50 == 0:
                    print("%d/%d chunks %d recs %.0fs"
                          % (done, len(chunks), nrec, time.time() - t0),
                          flush=True)
                if time.time() - t0 > args.budget:
                    print("BUDGET STOP at %d/%d chunks" % (done, len(chunks)),
                          flush=True)
                    for g in futs:
                        g.cancel()
                    break
    print("done %d recs %.0fs" % (nrec, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
