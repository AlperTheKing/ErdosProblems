#!/usr/bin/env python3
"""Per-dimension refinement of the fam4 aggregate: the tier-0 target lives at
d >= 4, and at d = 1 the margin h*_1 - h*_d is identically 0, so a global
minimum of 0 is uninformative.  This reports the margin per d."""
import glob, json, os, sys

dirs = sys.argv[1:] or ["out_r5", "out_r6", "out_r7"]
base = os.path.dirname(os.path.abspath(__file__))

per_d = {}          # d -> dict(min_margin, arg, max_hd, arg, n, n_h1zero)
tot = 0
ok = 0
hits = {"TIER0": [], "JACKPOT": [], "NEG": []}
audit = 0
h1zero_d4 = []


def brief(r):
    return {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "r": r["r"],
            "c": r.get("c"), "d": r.get("d"), "hstar": r.get("hstar"),
            "hstar_1": r.get("hstar_1"), "hstar_d": r.get("hstar_d"),
            "hstar_sum": r.get("hstar_sum"), "poly": r.get("poly")}


for dd in dirs:
    for fn in sorted(glob.glob(os.path.join(base, dd, "*.jsonl"))):
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            tot += 1
            for k in ("TIER0", "JACKPOT", "NEG"):
                if r.get(k):
                    hits[k].append(brief(r))
            if r.get("status") != "OK":
                continue
            ok += 1
            for k in ("heldout_ok", "hstar_roundtrip_ok", "hstar_tail_zero",
                      "hstar_nonneg", "interior_check_ok",
                      "hstar_1_identity_ok", "moment_criteria_consistent"):
                if r.get(k) is False:
                    audit += 1
            d = r["d"]
            h1, hd = r.get("hstar_1"), r.get("hstar_d")
            e = per_d.setdefault(d, {"n": 0, "min_margin": None, "argmin": None,
                                     "max_hd": -1, "argmax": None,
                                     "n_h1zero": 0, "min_hsum": None,
                                     "argminvol": None})
            e["n"] += 1
            if hd is not None and hd > e["max_hd"]:
                e["max_hd"] = hd
                e["argmax"] = brief(r)
            hs = r.get("hstar_sum")
            if hs is not None and (e["min_hsum"] is None or hs < e["min_hsum"]):
                e["min_hsum"] = hs
                e["argminvol"] = brief(r)
            if h1 is None or hd is None:
                continue
            if h1 == 0:
                e["n_h1zero"] += 1
                if d >= 4:
                    h1zero_d4.append(brief(r))
            m = h1 - hd
            if e["min_margin"] is None or m < e["min_margin"]:
                e["min_margin"] = m
                e["argmin"] = brief(r)

# global minimum restricted to the meaningful range d >= 2
g = None
for d, e in per_d.items():
    if d >= 2 and e["min_margin"] is not None:
        if g is None or e["min_margin"] < g[0]:
            g = (e["min_margin"], d, e["argmin"])
g4 = None
for d, e in per_d.items():
    if d >= 4 and e["min_margin"] is not None:
        if g4 is None or e["min_margin"] < g4[0]:
            g4 = (e["min_margin"], d, e["argmin"])

print(json.dumps({
    "total": tot, "ok": ok, "audit_failures": audit,
    "n_TIER0": len(hits["TIER0"]), "n_JACKPOT": len(hits["JACKPOT"]),
    "n_NEG": len(hits["NEG"]),
    "TIER0": hits["TIER0"][:20], "JACKPOT": hits["JACKPOT"][:20],
    "NEG": hits["NEG"][:20],
    "per_d": {str(k): per_d[k] for k in sorted(per_d)},
    "min_margin_d_ge_2": g,
    "min_margin_d_ge_4": g4,
    "n_h1zero_d_ge_4": len(h1zero_d4),
    "h1zero_d_ge_4_sample": h1zero_d4[:25],
}, indent=1))
