#!/usr/bin/env python3
"""Build runs/fam14/manifest.json from the control lane outputs (exact only)."""
import collections
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "runs", "fam14")


def load(path):
    out = []
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            l = l.strip()
            if l:
                out.append(json.loads(l))
    return out


def key(r):
    return (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))


def main():
    base = load(os.path.join(RUN, "control_main.jsonl"))
    by = {key(r): r for r in base}
    n_retried = 0
    for f in ("control_main_retry.jsonl", "control_main_retry2.jsonl"):
        for r in load(os.path.join(RUN, f)):
            k = key(r)
            if k in by and str(by[k]["status"]).startswith("UNRESOLVED") \
               and not str(r["status"]).startswith("UNRESOLVED"):
                r["cell_r"] = by[k].get("cell_r")
                r["cell_N"] = by[k].get("cell_N")
                by[k] = r
                n_retried += 1
    recs = list(by.values())

    st = collections.Counter(str(r["status"]).split("_")[0] if
                             str(r["status"]).startswith("UNRESOLVED")
                             else r["status"] for r in recs)
    pos = [r for r in recs if r.get("status") == "OK" and r.get("d", -1) >= 0]

    byd = {}
    for r in pos:
        d = r["d"]
        a = byd.setdefault(d, {"n": 0, "h1zero": 0, "maxV": 0, "maxV_h1zero": 0})
        a["n"] += 1
        a["maxV"] = max(a["maxV"], r["hstar_sum"])
        if r["hstar_1"] == 0:
            a["h1zero"] += 1
            a["maxV_h1zero"] = max(a["maxV_h1zero"], r["hstar_sum"])

    def top(pred):
        c = [r for r in pos if pred(r)]
        if not c:
            return None
        b = max(c, key=lambda r: r["hstar_sum"])
        return {"sum_hstar": b["hstar_sum"], "lam": b["lam"], "mu": b["mu"],
                "nu": b["nu"], "d": b["d"], "hstar_1": b["hstar_1"],
                "hstar": b["hstar"], "poly": b["poly"]}

    mn = None
    for r in pos:
        for cs in r.get("coeffs_low_to_high", []):
            c = Fraction(cs)
            if mn is None or c < mn[0]:
                mn = (c, r)

    carriers = [{"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "d": r["d"],
                 "c": r["c"], "hstar": r["hstar"], "sum_hstar": r["hstar_sum"],
                 "poly": r["poly"], "profile": r["profile"]}
                for r in pos if r["hstar_1"] == 0 and r["hstar_sum"] >= 2]

    man = {
        "family": "FAM14 = CONTROL (unbiased random hive triples, r=4..7)",
        "role": "null model / base-rate measurement; NOT a hunting family",
        "instrument": "purged_region/lpfree_screen.py (screen_profile) via remine._profile_job "
                      "-- exact engine-A profile P(0..D+2), exact Newton interpolation over Q, "
                      "2 held-out verification points, h* by alternating sum. "
                      "NO LP dimension oracle, NO simplex filter, nothing discarded.",
        "instrument_self_test": {
            "known_hive_refuter": {"lam": [2, 2, 1], "mu": [4, 3, 2, 1],
                                   "nu": [5, 4, 3, 2, 1], "d": 4, "c": 5,
                                   "hstar": [1, 0, 1, 0, 0], "sum_hstar": 2,
                                   "reproduced": True},
            "reeve_T13": {"d": 3, "hstar": [1, 0, 12, 0],
                          "coeffs_low_to_high": ["1", "-1/6", "1", "13/6"],
                          "NEG": True, "reproduced": True}},
        "sampling_design": {
            "exhaustive": False,
            "type": "sampled -- two-stage uniform, stated exactly",
            "stage1": "nu uniform among partitions of N with EXACTLY r parts",
            "stage2": "(lam,mu) uniform among ALL pairs with |lam|+|mu|=N, "
                      "len<=r, lam,mu contained in nu (a drawn with prob "
                      "proportional to L(a,nu)*L(N-a,nu))",
            "post_filter": "none -- c=0 triples are kept and reported",
            "cells": "r=4:N=6..30 K=400; r=5:N=8..30 K=350; r=6:N=10..32 K=250; "
                     "r=7:N=12..34 K=180",
            "seed": 140721,
            "engine_node_cap": 2000000000,
            "per_triple_timeout_s": 180},
        "triples_tested": len(recs),
        "status_counts": dict(st),
        "retried_and_resolved": n_retried,
        "resolved_nonempty": len(pos),
        "empty_c0_P_identically_zero": len([r for r in recs if r.get("status") == "EMPTY"]),
        "still_unresolved": len([r for r in recs
                                 if str(r.get("status", "")).startswith("UNRESOLVED")]),
        "base_rate_hstar1_zero": {
            "note": "d=0 records are single points; h*_1 does not exist there "
                    "(reported as null) and they are excluded from the d>=1 rate",
            "overall_d_ge_1": "%d/%d" % (
                len([r for r in pos if r["d"] >= 1 and r["hstar_1"] == 0]),
                len([r for r in pos if r["d"] >= 1])),
            "d_ge_2": "%d/%d" % (len([r for r in pos if r["d"] >= 2 and r["hstar_1"] == 0]),
                                 len([r for r in pos if r["d"] >= 2])),
            "by_d": {str(d): byd[d] for d in sorted(byd)}},
        "volume_distribution_all": dict(sorted(collections.Counter(
            r["hstar_sum"] for r in pos).items())),
        "volume_distribution_hstar1_zero_d_ge_2": dict(sorted(collections.Counter(
            r["hstar_sum"] for r in pos if r["hstar_1"] == 0 and r["d"] >= 2).items())),
        "best_sum_hstar": top(lambda r: True),
        "best_at_hstar1_zero": top(lambda r: r["hstar_1"] == 0),
        "best_at_hstar1_le_2": top(lambda r: (r["hstar_1"] or 0) <= 2),
        "min_monomial_coefficient": {
            "value": str(mn[0]) if mn else None,
            "lam": mn[1]["lam"] if mn else None, "mu": mn[1]["mu"] if mn else None,
            "nu": mn[1]["nu"] if mn else None, "poly": mn[1]["poly"] if mn else None},
        "hits_negative_coefficient": [
            {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "d": r["d"],
             "hstar": r["hstar"], "poly": r["poly"]}
            for r in pos if r.get("neg")],
        "hstar1_zero_volume_ge_2_carriers": carriers,
        "integrity": {
            "heldout_or_roundtrip_or_tail_failures": len(
                [r for r in pos if not (r.get("heldout_ok") and r.get("hstar_roundtrip_ok")
                                        and r.get("hstar_tail_zero") and r.get("hstar_0_is_1"))]),
            "hstar_with_negative_entry": len([r for r in pos if not r.get("hstar_nonneg")])},
        "files": {
            "primary": "runs/fam14/control_main.jsonl",
            "cells": "runs/fam14/control_main.jsonl.cells.json",
            "retries": ["runs/fam14/control_main_retry.jsonl",
                        "runs/fam14/control_main_retry2.jsonl"],
            "secondary_partial": "runs/fam14/control_b2.jsonl",
            "driver": "control14.py", "analyzer": "control14_analyze.py",
            "retry_driver": "control14_retry.py"},
        "caveats": [
            "A negative census is NOT evidence for the KTT conjecture.",
            "control_b2.jsonl is a SECOND seed (987654) whose run CRASHED "
            "(ProcessPoolExecutor BrokenProcessPool from oversubscribed engine "
            "spawns) after 16576/27018 triples. Because records are written in "
            "COMPLETION order, that truncation is biased toward fast (small) "
            "triples and it is therefore NOT pooled with the primary batch; it "
            "is retained only as a consistency check.",
            "Triples still marked UNRESOLVED exhausted the engine node cap or "
            "the wall-clock budget; that is a search-effort outcome, never a "
            "mathematical verdict."],
    }
    dst = os.path.join(RUN, "manifest.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    print(json.dumps({k: man[k] for k in
                      ("triples_tested", "status_counts", "resolved_nonempty",
                       "still_unresolved", "base_rate_hstar1_zero",
                       "best_sum_hstar", "best_at_hstar1_zero",
                       "best_at_hstar1_le_2", "min_monomial_coefficient",
                       "hits_negative_coefficient",
                       "volume_distribution_hstar1_zero_d_ge_2")}, indent=1))
    print("wrote", dst)


if __name__ == "__main__":
    main()
