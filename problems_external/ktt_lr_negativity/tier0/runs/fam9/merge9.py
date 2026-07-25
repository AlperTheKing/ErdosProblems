#!/usr/bin/env python3
"""Merge every fam9 result file into runs/fam9/manifest.json."""
import json, glob, os, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

tot = 0
stat = collections.Counter()
mh = collections.Counter()
nonfull = 0
bhd = (-1, None)
bm = (10 ** 9, None, None, None, None)
bmi = (10 ** 9, None, None, None, None)
hits = []
interior_total = 0
completedN = None
srcs = []

for f in sorted(glob.glob(os.path.join(HERE, "exhaust9_result_*.json"))) + \
        sorted(glob.glob(os.path.join(HERE, "beam9b_result_*.json"))) + \
        sorted(glob.glob(os.path.join(HERE, "beam9_result.json"))):
    j = json.load(open(f))
    srcs.append(os.path.basename(f))
    tot += j["triplesTested"]
    stat.update(j["status_counts"])
    for k, v in j["margin_histogram"].items():
        mh[int(k)] += v
    nonfull += j["nonFullDimCount"]
    interior_total += j.get("interiorRecords_d_ge_2", 0) + len(j.get("interior_d_ge_4", []))
    if j["bestHstarD"]["value"] > bhd[0]:
        bhd = (j["bestHstarD"]["value"], j["bestHstarD"]["triple"])
    m = j["minH1MinusHD"]
    if m["value"] < bm[0]:
        bm = (m["value"], m["triple"], m.get("hstar"), m.get("d"), m.get("c"))
    mi = j.get("minH1MinusHD_amongInterior")
    if mi and mi["value"] < bmi[0]:
        bmi = (mi["value"], mi["triple"], mi.get("hstar"), mi.get("d"), mi.get("c"))
    hits += j["hits"]
    if "fully_completed_N" in j:
        s = set(j["fully_completed_N"])
        completedN = s if completedN is None else (completedN & s)

out = {
    "family": "fam9 -- beam search minimising Sum h* subject to h*_d >= 1 "
              "(independent seed 9009 / 90090+k, own mutation law), plus a "
              "companion EXHAUSTIVE sweep of the r=5 small-|nu| window",
    "generated": datetime.datetime.utcnow().isoformat() + "Z",
    "instrument": "problems_external/ktt_lr_negativity/tier0/tier0_screen.py "
                  "(mandated LP-free exact screen; engine A = lr_hive.exe; "
                  "no LP dimension oracle, no simplex filter; exact Fractions only)",
    "exhaustive_window": {
        "description": "r = 5; nu ranges over ALL partitions of N into exactly "
                       "5 positive parts; (lam,mu) over ALL pairs of partitions "
                       "with at most 5 parts, |lam|+|mu| = N, lam subset nu, "
                       "mu subset nu; lam<->mu quotiented",
        "N_fully_completed": sorted(completedN) if completedN else [],
    },
    "sampled_component": "beam9b.py mid-size (|nu| <= 70, r in {5,6}) beam, "
                         "10-12 independent workers, cap 2e6; SAMPLED, not exhaustive",
    "sources": srcs,
    "triplesTested": tot,
    "status_counts": dict(stat),
    "nonFullDimCount": nonfull,
    "bestHstarD": {"value": bhd[0], "triple": bhd[1]},
    "minH1MinusHD": {"value": bm[0], "triple": bm[1], "hstar": bm[2],
                     "d": bm[3], "c": bm[4]},
    "minH1MinusHD_amongInteriorCarrying": {
        "value": None if bmi[0] == 10 ** 9 else bmi[0],
        "triple": bmi[1], "hstar": bmi[2], "d": bmi[3], "c": bmi[4]},
    "margin_histogram_h1_minus_hd_over_d_ge_2": dict(sorted(mh.items())),
    "interiorCarryingRecords_d_ge_2": interior_total,
    "hits": hits,
    "TIER0_count": sum(1 for h in hits if h.get("TIER0")),
    "JACKPOT_count": sum(1 for h in hits if h.get("JACKPOT")),
    "NEG_count": sum(1 for h in hits if h.get("NEG")),
}
with open(os.path.join(HERE, "manifest.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: out[k] for k in
                  ("triplesTested", "status_counts", "nonFullDimCount",
                   "bestHstarD", "minH1MinusHD",
                   "minH1MinusHD_amongInteriorCarrying",
                   "margin_histogram_h1_minus_hd_over_d_ge_2",
                   "interiorCarryingRecords_d_ge_2", "TIER0_count",
                   "JACKPOT_count", "NEG_count")}, indent=1))
