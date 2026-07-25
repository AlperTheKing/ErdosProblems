#!/usr/bin/env python3
"""fam6_final.py -- final family-6 aggregate.

Reports, over every screened record:
  (i)   max h*_d and the triple attaining it
  (ii)  min (h*_1 - h*_d) and the triple attaining it   [ = distance to JACKPOT ]
  (iii) every TIER0 / JACKPOT record
  (iv)  every record with a strictly negative monomial coefficient
plus the family-6 specific law: for records with h*_1 = 0 (c = d+1), the
h*-degree  s = max{j : h*_j > 0}  ( = d+1-codegree ).  TIER0 needs s = d.
"""
import glob
import json
import sys
from collections import Counter


def main(pats, dst):
    files = []
    for p in pats:
        files.extend(glob.glob(p))
    tot = ok = 0
    st = Counter()
    dhist = Counter()
    s_at_h1zero = Counter()          # (d, s)
    sumh_at_h1zero = Counter()       # (d, Sum h*)
    best_hd = (-1, None)
    best_hd_dge2 = (-1, None)
    best_margin = (10 ** 9, None)
    best_margin_dge2 = (10 ** 9, None)
    margin_hist = Counter()
    hits = {"TIER0": [], "JACKPOT": [], "NEG": []}
    audit_fail = []
    seen = set()
    dup = 0
    # first pass: which triples were resolved OK somewhere (retry shards)
    resolved = set()
    for fn in files:
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r0 = json.loads(line)
            if r0.get("status") == "OK":
                resolved.add((tuple(r0["lam"]), tuple(r0["mu"]),
                              tuple(r0["nu"])))
    nonunimodular_minimal = 0
    for fn in files:
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            key = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
            if key in seen:
                dup += 1
                continue
            if rec.get("status") != "OK" and key in resolved:
                dup += 1
                continue
            seen.add(key)
            tot += 1
            s = rec.get("status")
            st[s] += 1
            if s != "OK":
                continue
            ok += 1
            for f in ("hstar_0_is_1", "hstar_nonneg", "hstar_tail_zero",
                      "hstar_roundtrip_ok", "heldout_ok",
                      "hstar_1_identity_ok", "interior_check_ok",
                      "moment_criteria_consistent"):
                if f in rec and rec[f] is False:
                    audit_fail.append([fn, rec["lam"], rec["mu"],
                                       rec["nu"], f])
            d = rec["d"]
            dhist[d] += 1
            if d is None or d < 1:
                continue
            h = rec["hstar"]
            h1, hd = h[1], h[d]
            info = {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"],
                    "r": len(rec["nu"]), "d": d, "c": rec["c"], "hstar": h,
                    "hstar_sum": sum(h)}
            if hd > best_hd[0]:
                best_hd = (hd, info)
            if d >= 2 and hd > best_hd_dge2[0]:
                best_hd_dge2 = (hd, info)
            if h1 - hd < best_margin[0]:
                best_margin = (h1 - hd, info)
            if d >= 2 and h1 - hd < best_margin_dge2[0]:
                best_margin_dge2 = (h1 - hd, info)
            margin_hist[h1 - hd] += 1
            if h1 == 0:
                topj = max(j for j in range(d + 1) if h[j] > 0)
                s_at_h1zero[(d, topj)] += 1
                sumh_at_h1zero[(d, sum(h))] += 1
                if sum(h) > 1:
                    nonunimodular_minimal += 1
            if rec.get("TIER0"):
                hits["TIER0"].append(info)
            if rec.get("JACKPOT"):
                hits["JACKPOT"].append(info)
            if rec.get("NEG") or rec.get("neg"):
                i2 = dict(info)
                i2["coeffs"] = rec.get("coeffs_low_to_high")
                hits["NEG"].append(i2)
    out = {
        "files": sorted(files), "distinct_triples": tot, "duplicates": dup,
        "ok": ok, "status": dict(st),
        "deg_hist": {str(k): v for k, v in sorted(dhist.items(),
                                                  key=lambda z: (z[0] is None,
                                                                 z[0]))},
        "max_hstar_d_all": best_hd[0], "max_hstar_d_all_at": best_hd[1],
        "max_hstar_d_d_ge_2": best_hd_dge2[0],
        "max_hstar_d_d_ge_2_at": best_hd_dge2[1],
        "min_h1_minus_hd_all": best_margin[0],
        "min_h1_minus_hd_all_at": best_margin[1],
        "min_h1_minus_hd_d_ge_2": best_margin_dge2[0],
        "min_h1_minus_hd_d_ge_2_at": best_margin_dge2[1],
        "h1_minus_hd_hist": {str(k): margin_hist[k]
                             for k in sorted(margin_hist)[:12]},
        "h1_zero_(d,hstar_degree_s)": {"%s,%s" % k: v
                                       for k, v in sorted(s_at_h1zero.items())},
        "h1_zero_(d,Sum_hstar)": {"%s,%s" % k: v
                                  for k, v in sorted(sumh_at_h1zero.items())},
        "minimal_c_nonunimodular": nonunimodular_minimal,
        "hits_counts": {k: len(v) for k, v in hits.items()},
        "hits": {k: v[:25] for k, v in hits.items()},
        "audit_failure_count": len(audit_fail),
        "audit_failures": audit_fail[:20],
    }
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    o = dict(out)
    o.pop("files")
    o.pop("hits")
    print(json.dumps(o, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:-1], sys.argv[-1])
