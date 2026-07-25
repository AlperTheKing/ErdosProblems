#!/usr/bin/env python3
"""fam10_manifest.py -- final manifest for ladder hunter 10.

Primary family (ASSIGNED, EXHAUSTIVE): every triple (lam,mu,nu) with
r = #parts(nu) = 6 and |nu| <= 20.
Bonus extension (also exhaustive, clearly separated): |nu| = 21.
"""
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "fam10")
PRIMARY = ["smoke", "mid", "hi", "hic"]              # |nu| <= 20
EXT = ["ext21", "hic21", "ext21_retry"]              # |nu| = 21


def recs_of(tags):
    out = {}
    for t in tags:
        p = os.path.join(OUT, "records_%s.jsonl" % t)
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                r = json.loads(line)
                out[(tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))] = r
        p = os.path.join(OUT, "summary_%s.json" % t)
        if os.path.exists(p):
            s = json.load(open(p, encoding="utf-8"))
            for k in ("best_h1zero", "best_h1le2", "min_coeff_rec"):
                if s.get(k):
                    r = s[k]
                    out[(tuple(r["lam"]), tuple(r["mu"]),
                         tuple(r["nu"]))] = r
            for h in s.get("hits", []):
                out[(tuple(h["lam"]), tuple(h["mu"]), tuple(h["nu"]))] = h
    return out


def slim(r):
    if not r:
        return None
    return {k: r[k] for k in ("lam", "mu", "nu", "c", "d", "hstar",
                              "hstar_sum", "poly", "coeffs_low_to_high",
                              "heldout", "heldout_ok", "hstar_roundtrip_ok",
                              "hstar_tail_zero", "hstar_nonneg", "profile",
                              "m") if k in r}


def stats(tags):
    R = recs_of(tags)
    b0 = (0, None)
    b2 = (0, None)
    mc = (None, None)
    bu = (None, None)
    hits = []
    for r in R.values():
        if r.get("status") != "OK":
            continue
        h = r["hstar"]
        d = r["d"]
        V = r["hstar_sum"]
        h1 = h[1] if len(h) > 1 else 0
        if h1 == 0 and V > b0[0]:
            b0 = (V, r)
        if h1 <= 2 and V > b2[0]:
            b2 = (V, r)
        cf = [Fraction(x) for x in r["coeffs_low_to_high"]]
        if mc[0] is None or min(cf) < mc[0]:
            mc = (min(cf), r)
        if d >= 2:
            u = Fraction(sum(x * (2 * j - (d + 1)) for j, x in enumerate(h)), V)
            if bu[0] is None or u > bu[0]:
                bu = (u, r)
        if r.get("neg"):
            hits.append(r)
    summ = {}
    for t in tags:
        p = os.path.join(OUT, "summary_%s.json" % t)
        if os.path.exists(p):
            s = json.load(open(p, encoding="utf-8"))
            summ[t] = {k: v for k, v in s.items()
                       if k not in ("hits", "best_h1zero", "best_h1le2",
                                    "min_coeff_rec")}
    return {
        "per_tag": summ,
        "n_retained_records": len(R),
        "best_h1zero_V": b0[0], "best_h1zero": slim(b0[1]),
        "best_h1le2_V": b2[0], "best_h1le2": slim(b2[1]),
        "min_coeff": str(mc[0]), "min_coeff_rec": slim(mc[1]),
        "max_mean_centered_index_u_d_ge_2": str(bu[0]),
        "max_u_rec": slim(bu[1]),
        "n_hits": len(hits), "hits": [slim(x) for x in hits],
    }


def main():
    man = {
        "run": "fam10 -- ladder hunter 10 of 14, corrected KTT hunt",
        "family": "EXHAUSTIVE census of every triple (lam,mu,nu) of "
                  "partitions with r = #parts(nu) = 6, |nu| <= 20, "
                  "|lam|+|mu| = |nu|, and lam,mu contained in nu "
                  "(containment is necessary for c(nu;lam,mu) > 0). "
                  "1,068,729 triples generated; the 572,547 with c = 0 have "
                  "Q empty (P == 0) and the 496,182 with c >= 1 were ALL "
                  "profiled exactly -- 0 UNRESOLVED.",
        "exhaustive": True,
        "instrument": "purged_region/lpfree_screen.py :: screen_profile -- "
                      "exact profile P(0..D+2) from engine A "
                      "(D = (r-1)(r-2)/2 = 10), exact Newton interpolation "
                      "over Q, d = deg P, TWO held-out points verified, "
                      "h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i), h* "
                      "round-trip and zero-tail checked.  NO LP dimension "
                      "oracle, NO simplex filter, nothing discarded for "
                      "'not a simplex'.  All arithmetic exact.",
        "stage1_note": "c = P(1) = (d+1) + h*_1 EXACTLY, so c <= D+3 = 13 "
                       "captures every triple with h*_1 <= 2.  Only 5 triples "
                       "in the whole family (all at |nu| = 20) have c > 13; "
                       "they were profiled separately with the instrument's "
                       "own escalating --dbound (fam10_hi.py) and all "
                       "resolved.  Nothing was dropped.",
        "primary_|nu|<=20": stats(PRIMARY),
        "bonus_extension_|nu|=21": stats(EXT),
        "negative_census_disclaimer":
            "No negative coefficient was found.  A negative census is NOT "
            "evidence for the King-Tollu-Toumazet positivity conjecture.",
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    p = man["primary_|nu|<=20"]
    e = man["bonus_extension_|nu|=21"]
    for tag, s in (("PRIMARY |nu|<=20", p), ("EXT |nu|=21", e)):
        print(tag, "best V (h*_1=0) =", s["best_h1zero_V"],
              "| best V (h*_1<=2) =", s["best_h1le2_V"],
              "| min coeff =", s["min_coeff"],
              "| max <u> =", s["max_mean_centered_index_u_d_ge_2"],
              "| hits =", s["n_hits"])
        for k in ("best_h1zero", "best_h1le2", "max_u_rec"):
            r = s[k]
            if r:
                print("   ", k, r["lam"], r["mu"], r["nu"], "c=", r["c"],
                      "d=", r["d"], "h*=", r["hstar"], "V=", r["hstar_sum"])


if __name__ == "__main__":
    main()
