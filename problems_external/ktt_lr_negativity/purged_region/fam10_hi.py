#!/usr/bin/env python3
"""
fam10_hi.py -- extension sweep of the r=6, |nu|<=20 census over the triples
that the primary run could not afford at full dilation: those with
c = P(1) > D+3 = 13 (equivalently h*_1 >= 3).

Engine A is a DFS whose cost is proportional to the lattice-point count, so
P(12) is unaffordable for large c.  Instead of dropping these triples (that is
exactly the mistake that created the purged region) we use the instrument's own
--dbound mechanism with ESCALATION:

  for m in 4, 6, 8, 10:
      compute the exact profile P(0..m+2)
      interpolate exactly through n = 0..m
      if BOTH held-out points n = m+1, m+2 match AND deg <= m-1, accept
  m = 10 = D is the ambient geometric bound, so the last stage is certified.

Every accepted record is produced by lpfree_screen.screen_profile, i.e. the
mandated instrument.  Nothing is discarded for "not a simplex"; no LP
dimension oracle is used.  Triples that blow the engine node cap are reported
UNRESOLVED and never turned into a math verdict.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ladder_scan import gen                       # noqa: E402
from lpfree_screen import screen_profile          # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP   # noqa: E402

R = 6
D = (R - 1) * (R - 2) // 2
LADDER = [4, 6, 8, 10]


def _job(arg):
    trips, node_cap, timeout = arg
    """escalating-dbound profiling of a chunk of triples"""
    pend = list(trips)
    cache = {t: {} for t in pend}          # t -> {n: P(n)}
    done = []
    for m in LADDER:
        if not pend:
            break
        lines = []
        need = []
        for t in pend:
            l, mu, v = t
            for n in range(m + 3):
                if n in cache[t]:
                    continue
                need.append((t, n))
                lines.append("%s;%s;%s;%d" % (
                    fmt(tuple(n * x for x in l)),
                    fmt(tuple(n * x for x in mu)),
                    fmt(tuple(n * x for x in v)), COUNT_CAP))
        if lines:
            out, err = engine_batch(lines, node_cap, timeout)
            if err is not None:
                for t in pend:
                    done.append({"lam": list(t[0]), "mu": list(t[1]),
                                 "nu": list(t[2]), "r": R,
                                 "status": "UNRESOLVED_" + err, "m": m})
                return done
            for (t, n), tok in zip(need, out):
                try:
                    cache[t][n] = int(tok)
                except ValueError:
                    cache[t][n] = None
        nxt = []
        for t in pend:
            prof = {n: cache[t][n] for n in range(m + 3)}
            if any(v is None for v in prof.values()):
                done.append({"lam": list(t[0]), "mu": list(t[1]),
                             "nu": list(t[2]), "r": R,
                             "status": "UNRESOLVED_NODECAP", "m": m})
                continue
            rec = screen_profile(prof, m)
            rec.pop("degree_bound", None)
            ok = (rec.get("status") in ("OK", "EMPTY")
                  and (rec.get("status") == "EMPTY"
                       or (rec.get("heldout_ok") and rec.get("d", 99) <= m - 1)
                       or m == D))
            if ok:
                rec.update({"lam": list(t[0]), "mu": list(t[1]),
                            "nu": list(t[2]), "r": R, "m": m})
                done.append(rec)
            elif m == LADDER[-1]:
                rec.update({"lam": list(t[0]), "mu": list(t[1]),
                            "nu": list(t[2]), "r": R, "m": m})
                done.append(rec)
            else:
                nxt.append(t)
        pend = nxt
    return done


def main(Nlo, Nhi, tag, workers, chunk, node_cap, timeout):
    outdir = os.path.join(HERE, "runs", "fam10")
    os.makedirs(outdir, exist_ok=True)
    fk = open(os.path.join(outdir, "records_%s.jsonl" % tag), "w",
              encoding="utf-8")
    t0 = time.time()
    n_gen = n_hi = n_ok = n_un = 0
    minc = (None, None)
    bh0 = (0, None)
    bh2 = (0, None)
    hits = []
    vhist = {}
    for N in range(Nlo, Nhi + 1):
        trips = gen(R, N)
        n_gen += len(trips)
        hi = []
        CH = 200000
        for s in range(0, len(trips), CH):
            part = trips[s:s + CH]
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
                if c > D + 3:
                    hi.append(t)
        n_hi += len(hi)
        jobs = [(hi[s:s + chunk], node_cap, timeout)
                for s in range(0, len(hi), chunk)]
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for fut in as_completed([ex.submit(_job, j) for j in jobs]):
                for rec in fut.result():
                    if rec.get("status") == "OK":
                        n_ok += 1
                        h = rec["hstar"]
                        V = rec["hstar_sum"]
                        vhist[V] = vhist.get(V, 0) + 1
                        h1 = h[1] if len(h) > 1 else 0
                        if h1 == 0 and V > bh0[0]:
                            bh0 = (V, rec)
                        if h1 <= 2 and V > bh2[0]:
                            bh2 = (V, rec)
                        cf = [Fraction(x) for x in rec["coeffs_low_to_high"]]
                        if minc[0] is None or min(cf) < minc[0]:
                            minc = (min(cf), rec)
                        if rec.get("neg"):
                            hits.append(rec)
                            print("NEGATIVE COEFFICIENT: %s"
                                  % json.dumps(rec), flush=True)
                            fk.write(json.dumps(rec) + "\n")
                        elif V >= 3:
                            fk.write(json.dumps(rec) + "\n")
                    elif rec.get("status") == "EMPTY":
                        pass
                    else:
                        n_un += 1
                        fk.write(json.dumps(rec) + "\n")
        fk.flush()
        print("N=%d gen=%d hi(c>13)=%d ok=%d unres=%d minc=%s Vmax(h1=0)=%d "
              "Vmax(h1<=2)=%d %.0fs"
              % (N, len(trips), len(hi), n_ok, n_un, minc[0], bh0[0], bh2[0],
                 time.time() - t0), flush=True)
    fk.close()
    summ = {"tag": tag, "r": R, "N_range": [Nlo, Nhi], "population": "c > 13",
            "n_generated": n_gen, "n_hi": n_hi, "n_ok": n_ok,
            "n_unresolved": n_un, "min_coeff": str(minc[0]),
            "min_coeff_rec": minc[1], "best_h1zero_V": bh0[0],
            "best_h1zero": bh0[1], "best_h1le2_V": bh2[0],
            "best_h1le2": bh2[1], "n_hits": len(hits), "hits": hits,
            "V_histogram": vhist, "secs": round(time.time() - t0, 1)}
    with open(os.path.join(outdir, "summary_%s.json" % tag), "w",
              encoding="utf-8") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps({k: v for k, v in summ.items()
                      if k not in ("hits", "best_h1zero", "best_h1le2",
                                   "min_coeff_rec")}, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
         int(sys.argv[4]) if len(sys.argv) > 4 else 40,
         int(sys.argv[5]) if len(sys.argv) > 5 else 200,
         int(sys.argv[6]) if len(sys.argv) > 6 else 2 * 10 ** 8,
         int(sys.argv[7]) if len(sys.argv) > 7 else 1800)
