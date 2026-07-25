#!/usr/bin/env python3
"""Final fam4 aggregate -> manifest.json."""
import glob, json, os, sys, time

base = os.path.dirname(os.path.abspath(__file__))
DIRS = sys.argv[1:]


def brief(r):
    return {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "r": r["r"],
            "c": r.get("c"), "d": r.get("d"), "hstar": r.get("hstar"),
            "hstar_1": r.get("hstar_1"), "hstar_d": r.get("hstar_d"),
            "hstar_sum": r.get("hstar_sum"), "poly": r.get("poly"),
            "coeffs_low_to_high": r.get("coeffs_low_to_high"),
            "profile": r.get("profile")}


tot = 0
status = {}
byr = {}
per_d = {}
hits = {"TIER0": [], "JACKPOT": [], "NEG": []}
audit = []
best_hd = (-1, None)
min_margin_all = (None, None)
min_margin_d2 = (None, None)
min_margin_d4 = (None, None)
margin_hist = {}
frontier = {}          # d -> (min h*_1 among h*_d>=1, rec)
h1zero_maxvol = (None, None)
n_h1zero = 0
n_h1neg = 0
n_interior = 0
B_min_by_d = {}

for dd in DIRS:
    for fn in sorted(glob.glob(os.path.join(base, dd, "*.jsonl"))):
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            tot += 1
            st = r.get("status", "?")
            status[st] = status.get(st, 0) + 1
            byr[r.get("r")] = byr.get(r.get("r"), 0) + 1
            for k in ("TIER0", "JACKPOT", "NEG"):
                if r.get(k):
                    hits[k].append(brief(r))
            if st != "OK":
                continue
            for k in ("heldout_ok", "hstar_roundtrip_ok", "hstar_tail_zero",
                      "hstar_nonneg", "hstar_0_is_1", "interior_check_ok",
                      "hstar_1_identity_ok", "moment_criteria_consistent"):
                if r.get(k) is False:
                    audit.append([r["lam"], r["mu"], r["nu"], k])
            d = r["d"]
            h1, hd, c = r.get("hstar_1"), r.get("hstar_d"), r.get("c")
            e = per_d.setdefault(d, {"n": 0, "min_margin": None,
                                     "max_hstar_d": 0, "max_hstar_sum": 0,
                                     "n_hstar1_zero": 0, "n_interior": 0})
            e["n"] += 1
            e["max_hstar_sum"] = max(e["max_hstar_sum"], r.get("hstar_sum") or 0)
            if hd is not None:
                e["max_hstar_d"] = max(e["max_hstar_d"], hd)
                if hd > best_hd[0]:
                    best_hd = (hd, brief(r))
                if hd >= 1 and d >= 1:
                    e["n_interior"] += 1
                    n_interior += 1
                    if h1 is not None:
                        cur = frontier.get(d)
                        if cur is None or h1 < cur[0]:
                            frontier[d] = (h1, brief(r))
            if c is not None and hd is not None and d >= 1:
                B = c - hd           # relative-boundary lattice points
                if d not in B_min_by_d or B - d < B_min_by_d[d][0]:
                    B_min_by_d[d] = (B - d, B, brief(r))
            if h1 is None or hd is None:
                continue
            if h1 == 0:
                n_h1zero += 1
                e["n_hstar1_zero"] += 1
                if h1zero_maxvol[0] is None or \
                        (r.get("hstar_sum") or 0) > h1zero_maxvol[0]:
                    h1zero_maxvol = (r.get("hstar_sum"), brief(r))
            if h1 < 0:
                n_h1neg += 1
            m = h1 - hd
            margin_hist[m] = margin_hist.get(m, 0) + 1
            if e["min_margin"] is None or m < e["min_margin"]:
                e["min_margin"] = m
            if min_margin_all[0] is None or m < min_margin_all[0]:
                min_margin_all = (m, brief(r))
            if d >= 2 and (min_margin_d2[0] is None or m < min_margin_d2[0]):
                min_margin_d2 = (m, brief(r))
            if d >= 4 and (min_margin_d4[0] is None or m < min_margin_d4[0]):
                min_margin_d4 = (m, brief(r))

out = {
    "family": "FAM4 asymmetric-weight (|mu| >= 2|lam|), r=5,6,7",
    "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "dirs": DIRS,
    "total_records": tot,
    "by_r": {str(k): v for k, v in sorted(byr.items(), key=lambda x: str(x[0]))},
    "status": status,
    "nonempty_screened": status.get("OK", 0),
    "audit_failures": audit[:40],
    "n_audit_failures": len(audit),
    "n_TIER0": len(hits["TIER0"]),
    "n_JACKPOT": len(hits["JACKPOT"]),
    "n_NEG": len(hits["NEG"]),
    "TIER0": hits["TIER0"][:40],
    "JACKPOT": hits["JACKPOT"][:40],
    "NEG": hits["NEG"][:40],
    "best_hstar_d": {"value": best_hd[0], "triple": best_hd[1]},
    "min_h1_minus_hd_all_d": {"value": min_margin_all[0],
                              "triple": min_margin_all[1]},
    "min_h1_minus_hd_d_ge_2": {"value": min_margin_d2[0],
                               "triple": min_margin_d2[1]},
    "min_h1_minus_hd_d_ge_4": {"value": min_margin_d4[0],
                               "triple": min_margin_d4[1]},
    "margin_histogram": {str(k): margin_hist[k]
                         for k in sorted(margin_hist)[:30]},
    "per_d": {str(k): per_d[k] for k in sorted(per_d)},
    "n_hstar1_zero": n_h1zero,
    "n_hstar1_negative": n_h1neg,
    "n_with_interior_lattice_point": n_interior,
    "hstar1_zero_max_volume": {"hstar_sum": h1zero_maxvol[0],
                               "triple": h1zero_maxvol[1]},
    "frontier_min_hstar1_given_interior":
        {str(k): {"hstar_1": frontier[k][0], "triple": frontier[k][1]}
         for k in sorted(frontier)},
    "min_boundary_excess_B_minus_d":
        {str(k): {"B_minus_d": B_min_by_d[k][0], "B": B_min_by_d[k][1],
                  "triple": B_min_by_d[k][2]} for k in sorted(B_min_by_d)},
}
json.dump(out, open(os.path.join(base, "manifest_agg.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in
                  ("total_records", "status", "by_r", "n_TIER0", "n_JACKPOT",
                   "n_NEG", "n_audit_failures", "n_hstar1_zero",
                   "n_hstar1_negative", "n_with_interior_lattice_point",
                   "best_hstar_d", "min_h1_minus_hd_all_d",
                   "min_h1_minus_hd_d_ge_2", "min_h1_minus_hd_d_ge_4",
                   "per_d", "margin_histogram",
                   "frontier_min_hstar1_given_interior")}, indent=1))
