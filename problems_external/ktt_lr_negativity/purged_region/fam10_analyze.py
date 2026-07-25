#!/usr/bin/env python3
"""fam10_analyze.py -- merge the fam10 census summaries + interesting-record
files into one manifest; compute the ladder statistics and the exact
second-moment diagnostic  <u> = sum_j h*_j (2j-(d+1)) / sum_j h*_j , whose
positivity is EQUIVALENT to [n^{d-1}] P < 0."""
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "fam10")


def load(tags):
    recs = []
    for t in tags:
        p = os.path.join(OUT, "records_%s.jsonl" % t)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            recs.append(json.loads(line))
    return recs


def key(r):
    return (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))


def main(tags):
    summs = {}
    for t in tags:
        p = os.path.join(OUT, "summary_%s.json" % t)
        if os.path.exists(p):
            summs[t] = json.load(open(p, encoding="utf-8"))
    recs = {}
    for r in load(tags):
        recs[key(r)] = r
    for t, s in summs.items():
        for k in ("best_h1zero", "best_h1le2", "min_coeff_rec"):
            if s.get(k):
                recs[key(s[k])] = s[k]
        for h in s.get("hits", []):
            recs[key(h)] = h

    best0 = (0, None)
    best2 = (0, None)
    minc = (None, None)
    bestu = (None, None)
    hits = []
    for r in recs.values():
        if r.get("status") != "OK":
            continue
        h = r["hstar"]
        d = r["d"]
        V = r["hstar_sum"]
        h1 = h[1] if len(h) > 1 else 0
        if h1 == 0 and V > best0[0]:
            best0 = (V, r)
        if h1 <= 2 and V > best2[0]:
            best2 = (V, r)
        cf = [Fraction(x) for x in r["coeffs_low_to_high"]]
        if minc[0] is None or min(cf) < minc[0]:
            minc = (min(cf), r)
        if d >= 1 and V:
            u = Fraction(sum(hj * (2 * j - (d + 1)) for j, hj in enumerate(h)), V)
            if bestu[0] is None or u > bestu[0]:
                bestu = (u, r)
        if r.get("neg"):
            hits.append(r)

    def slim(r):
        if not r:
            return None
        return {k: r[k] for k in ("lam", "mu", "nu", "c", "d", "hstar",
                                  "hstar_sum", "poly", "coeffs_low_to_high",
                                  "heldout_ok", "hstar_roundtrip_ok",
                                  "hstar_tail_zero", "profile") if k in r}

    man = {
        "family": "EXHAUSTIVE census: all triples (lam,mu,nu) with "
                  "r = #parts(nu) = 6 and |nu| <= 20 (|lam|+|mu|=|nu|, "
                  "lam,mu contained in nu)",
        "tags": tags,
        "per_tag": {t: {k: v for k, v in s.items()
                        if k not in ("hits", "best_h1zero", "best_h1le2",
                                     "min_coeff_rec")}
                    for t, s in summs.items()},
        "best_h1zero_V": best0[0], "best_h1zero": slim(best0[1]),
        "best_h1le2_V": best2[0], "best_h1le2": slim(best2[1]),
        "min_coeff": str(minc[0]), "min_coeff_rec": slim(minc[1]),
        "max_mean_centered_index_u": str(bestu[0]),
        "max_u_rec": slim(bestu[1]),
        "n_hits": len(hits), "hits": [slim(h) for h in hits],
        "instrument": "purged_region/lpfree_screen.py screen_profile "
                      "(exact profile P(0..D+2), exact Newton interpolation "
                      "over Q, two held-out points, h* by the alternating "
                      "binomial sum); NO LP dimension oracle, NO simplex "
                      "filter, nothing discarded for 'not a simplex'",
        "negative_census_disclaimer":
            "A census with no negative coefficient is NOT evidence for the "
            "King-Tollu-Toumazet positivity conjecture.",
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    print(json.dumps({k: v for k, v in man.items() if k != "per_tag"},
                     indent=1)[:4000])


if __name__ == "__main__":
    main(sys.argv[1:])
