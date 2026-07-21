#!/usr/bin/env python3
"""
fam10_census.py -- ladder hunter 10: EXHAUSTIVE census over all triples with
r = #parts(nu) = 6 and |nu| <= 20, using ONLY the mandated LP-free instrument
(lpfree_screen.screen_profile).  No LP dimension oracle, no simplex filter,
nothing discarded for "not a simplex".  All arithmetic exact.

Stage 1 (EXACT, not a heuristic): c = P(1) via engine A.  Because
c = P(1) = sum_j h*_j C(d+1-j, d) = (d+1) + h*_1 exactly, the condition
h*_1 <= 2 is EQUIVALENT to c <= d+3, and since d <= D = (r-1)(r-2)/2 = 10 it
is IMPLIED by c <= D+3 = 13.  So keeping c <= 13 keeps EVERY triple with
h*_1 <= 2 (it also keeps some with larger h*_1, which are profiled too).
Triples with c > 13 have h*_1 >= 3; they are profiled only in the separate
sampled sweep (--stage hi) because engine A is a DFS whose cost is
proportional to the lattice-point count, which explodes at n = D+2 = 12.
That restriction is a COMPUTE limit and is reported as such; it is never
described as evidence.

Stage 2: exact profile P(0..D+2) -> exact interpolation -> d, h*, coefficients.
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
from ladder_scan2 import _chunk_job               # noqa: E402
from remine import engine_batch, fmt, COUNT_CAP   # noqa: E402

R = 6
D = (R - 1) * (R - 2) // 2          # 10
CKEEP = D + 3                       # 13


class Stats:
    def __init__(self):
        self.n_gen = 0
        self.n_stage1 = 0
        self.n_profiled = 0
        self.n_ok = 0
        self.n_unresolved = 0
        self.best_h1zero = (0, None)     # (sum h*, rec)
        self.best_h1le2 = (0, None)
        self.min_coeff = (None, None)    # (Fraction, rec)
        self.hits = []
        self.dhist = {}
        self.vhist = {}

    def add(self, rec):
        self.n_profiled += 1
        if rec.get("status") != "OK":
            self.n_unresolved += 1
            return
        self.n_ok += 1
        h = rec.get("hstar")
        if not h:
            return
        d = rec["d"]
        self.dhist[d] = self.dhist.get(d, 0) + 1
        V = rec["hstar_sum"]
        self.vhist[V] = self.vhist.get(V, 0) + 1
        h1 = h[1] if len(h) > 1 else 0
        if h1 == 0 and V > self.best_h1zero[0]:
            self.best_h1zero = (V, rec)
        if h1 <= 2 and V > self.best_h1le2[0]:
            self.best_h1le2 = (V, rec)
        cf = [Fraction(x) for x in rec["coeffs_low_to_high"]]
        m = min(cf)
        if self.min_coeff[0] is None or m < self.min_coeff[0]:
            self.min_coeff = (m, rec)
        if rec.get("neg"):
            self.hits.append(rec)


def run(Nlo, Nhi, tag, workers, chunk, ckeep=CKEEP, sample=None):
    st = Stats()
    outdir = os.path.join(HERE, "runs", "fam10")
    os.makedirs(outdir, exist_ok=True)
    fkeep = open(os.path.join(outdir, "records_%s.jsonl" % tag), "w",
                 encoding="utf-8")
    t0 = time.time()
    for N in range(Nlo, Nhi + 1):
        trips = gen(R, N)
        st.n_gen += len(trips)
        keep = []
        CH = 200000
        for s in range(0, len(trips), CH):
            part = trips[s:s + CH]
            lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                     for (l, m, v) in part]
            out, err = engine_batch(lines, 2 * 10 ** 9, 200000)
            if err:
                raise SystemExit("stage1 N=%d %s" % (N, err))
            for t, tok in zip(part, out):
                try:
                    c = int(tok)
                except ValueError:
                    continue
                if 1 <= c <= ckeep:
                    keep.append(t)
        st.n_stage1 += len(keep)
        if sample is not None and len(keep) > sample:
            import random
            random.Random(12345 + N).shuffle(keep)
            keep = keep[:sample]
        jobs = [(keep[s:s + chunk], D, 2 * 10 ** 9, 3000)
                for s in range(0, len(keep), chunk)]
        nb = 0
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for fut in as_completed([ex.submit(_chunk_job, j) for j in jobs]):
                for rec in fut.result():
                    st.add(rec)
                    h = rec.get("hstar") or []
                    interesting = (rec.get("neg")
                                   or (len(h) > 1 and h[1] == 0
                                       and rec.get("hstar_sum", 0) >= 2)
                                   or (len(h) > 1 and h[1] <= 2
                                       and rec.get("hstar_sum", 0) >= 3)
                                   or rec.get("status") != "OK")
                    if interesting:
                        fkeep.write(json.dumps(rec) + "\n")
                    if rec.get("neg"):
                        print("NEGATIVE COEFFICIENT: %s" % json.dumps(rec),
                              flush=True)
                nb += 1
        fkeep.flush()
        print("N=%d gen=%d keep=%d ok=%d unres=%d bestV(h1=0)=%d "
              "bestV(h1<=2)=%d min=%s  %.0fs"
              % (N, len(trips), len(keep), st.n_ok, st.n_unresolved,
                 st.best_h1zero[0], st.best_h1le2[0],
                 st.min_coeff[0], time.time() - t0), flush=True)
    fkeep.close()

    summ = {
        "tag": tag, "r": R, "D": D, "N_range": [Nlo, Nhi], "ckeep": ckeep,
        "sample_per_N": sample,
        "n_generated": st.n_gen, "n_stage1_kept": st.n_stage1,
        "n_profiled": st.n_profiled, "n_ok": st.n_ok,
        "n_unresolved": st.n_unresolved,
        "best_h1zero_V": st.best_h1zero[0], "best_h1zero": st.best_h1zero[1],
        "best_h1le2_V": st.best_h1le2[0], "best_h1le2": st.best_h1le2[1],
        "min_coeff": str(st.min_coeff[0]), "min_coeff_rec": st.min_coeff[1],
        "n_hits": len(st.hits), "hits": st.hits,
        "d_histogram": st.dhist, "V_histogram": st.vhist,
        "secs": round(time.time() - t0, 1),
    }
    with open(os.path.join(outdir, "summary_%s.json" % tag), "w",
              encoding="utf-8") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps({k: v for k, v in summ.items()
                      if k not in ("hits", "best_h1zero", "best_h1le2",
                                   "min_coeff_rec")}, indent=1))
    return summ


if __name__ == "__main__":
    Nlo, Nhi, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    chunk = int(sys.argv[5]) if len(sys.argv) > 5 else 300
    ckeep = int(sys.argv[6]) if len(sys.argv) > 6 else CKEEP
    sample = int(sys.argv[7]) if len(sys.argv) > 7 else None
    run(Nlo, Nhi, tag, workers, chunk, ckeep, sample)
