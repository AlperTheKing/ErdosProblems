#!/usr/bin/env python3
"""Aggregate fam4 screen records: TIER0 / JACKPOT / NEG hits, max h*_d,
min (h*_1 - h*_d), status histogram, audit-flag violations."""
import glob, json, os, sys
from fractions import Fraction

dirs = sys.argv[1:] or ["out_r5", "out_r6", "out_r7"]
base = os.path.dirname(os.path.abspath(__file__))

tot = 0
status = {}
byr = {}
hits = {"TIER0": [], "JACKPOT": [], "NEG": []}
audit_fail = []
best_hd = (-1, None)
min_margin = (None, None)          # min over OK records of h*_1 - h*_d
margin_hist = {}
d_hist = {}
hstar1_zero = []                   # h*_1 == 0 records (near misses)
hstar1_neg = []                    # h*_1 < 0  (would be spectacular)
nonlattice_lb = 0                  # records that CANNOT be lattice polytopes

for dd in dirs:
    for fn in sorted(glob.glob(os.path.join(base, dd, "*.jsonl"))):
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            tot += 1
            st = r.get("status", "?")
            status[st] = status.get(st, 0) + 1
            rr = r.get("r")
            byr[rr] = byr.get(rr, 0) + 1
            if r.get("TIER0"):
                hits["TIER0"].append(r)
            if r.get("JACKPOT"):
                hits["JACKPOT"].append(r)
            if r.get("NEG"):
                hits["NEG"].append(r)
            if st != "OK":
                continue
            for k in ("heldout_ok", "hstar_roundtrip_ok", "hstar_tail_zero",
                      "hstar_nonneg", "hstar_0_is_1", "interior_check_ok",
                      "hstar_1_identity_ok", "moment_criteria_consistent"):
                if r.get(k) is False:
                    audit_fail.append((fn, r["lam"], r["mu"], r["nu"], k))
            d = r.get("d")
            d_hist[d] = d_hist.get(d, 0) + 1
            hd = r.get("hstar_d")
            h1 = r.get("hstar_1")
            if hd is not None and hd > best_hd[0]:
                best_hd = (hd, r)
            if h1 is not None and hd is not None:
                m = h1 - hd
                margin_hist[m] = margin_hist.get(m, 0) + 1
                if min_margin[0] is None or m < min_margin[0]:
                    min_margin = (m, r)
                if h1 == 0 and d >= 1:
                    hstar1_zero.append(r)
                if h1 < 0:
                    hstar1_neg.append(r)
            # Sum h* = normalized volume; c = #lattice pts.
            # A lattice polytope of dim d has >= d+1 lattice points AND
            # Sum h* >= 1.  c == d+1 with an interior point is impossible
            # for a lattice polytope -> certificate of non-latticeness.
            c = r.get("c")
            if c is not None and d is not None and d >= 1 and c == d + 1 \
                    and hd and hd > 0:
                nonlattice_lb += 1

def brief(r):
    if r is None:
        return None
    return {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "r": r["r"],
            "c": r.get("c"), "d": r.get("d"), "hstar": r.get("hstar"),
            "hstar_1": r.get("hstar_1"), "hstar_d": r.get("hstar_d"),
            "hstar_sum": r.get("hstar_sum"), "poly": r.get("poly")}

out = {
    "total_records": tot,
    "by_r": byr,
    "status": status,
    "d_histogram": {str(k): v for k, v in sorted(d_hist.items())},
    "best_hstar_d": {"value": best_hd[0], "triple": brief(best_hd[1])},
    "min_h1_minus_hd": {"value": min_margin[0], "triple": brief(min_margin[1])},
    "margin_histogram": {str(k): v for k, v in sorted(margin_hist.items())[:40]},
    "n_hstar1_zero_dpos": len(hstar1_zero),
    "n_hstar1_negative": len(hstar1_neg),
    "hstar1_zero_examples": [brief(x) for x in hstar1_zero[:15]],
    "hstar1_zero_with_interior": [brief(x) for x in hstar1_zero
                                  if x.get("hstar_d")],
    "n_TIER0": len(hits["TIER0"]),
    "n_JACKPOT": len(hits["JACKPOT"]),
    "n_NEG": len(hits["NEG"]),
    "TIER0": [brief(x) for x in hits["TIER0"][:50]],
    "JACKPOT": [brief(x) for x in hits["JACKPOT"][:50]],
    "NEG": [brief(x) for x in hits["NEG"][:50]],
    "audit_failures": audit_fail[:50],
    "n_audit_failures": len(audit_fail),
    "nonlattice_certificates": nonlattice_lb,
}
print(json.dumps(out, indent=1))
