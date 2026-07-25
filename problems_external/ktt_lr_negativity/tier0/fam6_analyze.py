#!/usr/bin/env python3
"""fam6_analyze.py -- aggregate fam6 jsonl shards: max h*_d, min(h*_1 - h*_d),
TIER0 / JACKPOT / NEG hits, audit-flag failures."""
import glob
import json
import sys
from collections import Counter


def main(pats):
    files = []
    for p in pats:
        files.extend(glob.glob(p))
    tot = 0
    ok = 0
    st = Counter()
    dcnt = Counter()
    best_hd = (-1, None)
    best_margin = (10 ** 9, None)
    h1zero = 0
    h1zero_sumh = Counter()
    hits = {"TIER0": [], "JACKPOT": [], "NEG": []}
    audit_fail = []
    nonlattice_proxy = 0
    for fn in files:
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            tot += 1
            s = rec.get("status")
            st[s] += 1
            if s != "OK":
                continue
            ok += 1
            d = rec["d"]
            h = rec["hstar"]
            dcnt[d] += 1
            if d < 1:
                continue
            h1 = h[1]
            hd = h[d]
            key = {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"],
                   "d": d, "c": rec["c"], "hstar": h,
                   "hstar_sum": sum(h)}
            if hd > best_hd[0]:
                best_hd = (hd, key)
            if h1 - hd < best_margin[0]:
                best_margin = (h1 - hd, key)
            if h1 == 0:
                h1zero += 1
                h1zero_sumh[sum(h)] += 1
            if rec.get("TIER0"):
                hits["TIER0"].append(key)
            if rec.get("JACKPOT"):
                hits["JACKPOT"].append(key)
            if rec.get("NEG") or rec.get("neg"):
                k2 = dict(key)
                k2["coeffs"] = rec.get("coeffs_low_to_high")
                hits["NEG"].append(k2)
            for f in ("hstar_0_is_1", "hstar_nonneg", "hstar_tail_zero",
                      "hstar_roundtrip_ok", "heldout_ok",
                      "hstar_1_identity_ok", "interior_check_ok",
                      "moment_criteria_consistent"):
                if f in rec and rec[f] is False:
                    audit_fail.append((fn, rec["lam"], rec["mu"], rec["nu"], f))
            # proxy for "not a lattice polytope": Sum h* not equal to the
            # normalized volume a lattice simplex with c=d+1 would force
            if h1 == 0 and sum(h) > 1:
                nonlattice_proxy += 1
    out = {
        "files": len(files), "records": tot, "ok": ok,
        "status": dict(st), "deg_hist": dict(sorted(dcnt.items())),
        "max_hstar_d": best_hd[0], "max_hstar_d_triple": best_hd[1],
        "min_h1_minus_hd": best_margin[0],
        "min_h1_minus_hd_triple": best_margin[1],
        "h1_zero_count": h1zero,
        "h1_zero_sumh_hist": dict(sorted(h1zero_sumh.items())),
        "nontrivial_volume_at_h1_zero": nonlattice_proxy,
        "hits": {k: (len(v), v[:20]) for k, v in hits.items()},
        "audit_failures": audit_fail[:20],
        "audit_failure_count": len(audit_fail),
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
