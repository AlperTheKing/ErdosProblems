#!/usr/bin/env python3
"""Aggregate fam1 screening records: ladder trackers (i)-(iv)."""
import sys, json
from fractions import Fraction

best_sum = None
best_h1zero = None
best_h1le2 = None
min_coeff = None
hits = []
n = 0
status = {}
by_d = {}

for path in sys.argv[1:]:
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            n += 1
            st = r.get("status")
            status[st] = status.get(st, 0) + 1
            if st != "OK":
                continue
            d = r["d"]
            hs = r["hstar"]
            S = r["hstar_sum"]
            h1 = r["hstar_1"]
            key = (d, tuple(hs))
            by_d.setdefault(d, {})
            by_d[d][tuple(hs)] = by_d[d].get(tuple(hs), 0) + 1
            tag = (r["lam"], r["mu"], r["nu"])
            if best_sum is None or S > best_sum[0]:
                best_sum = (S, tag, hs, d)
            if h1 == 0:
                if best_h1zero is None or S > best_h1zero[0]:
                    best_h1zero = (S, tag, hs, d)
            if h1 is not None and h1 <= 2:
                if best_h1le2 is None or S > best_h1le2[0]:
                    best_h1le2 = (S, tag, hs, d)
            cs = [Fraction(c) for c in r["coeffs_low_to_high"]]
            mc = min(cs)
            if min_coeff is None or mc < min_coeff[0]:
                min_coeff = (mc, tag, r["poly"], hs, d)
            if r.get("neg"):
                hits.append(r)

out = {
    "n_records": n,
    "status_counts": status,
    "best_sum_hstar": best_sum and {"sum": best_sum[0], "triple": best_sum[1],
                                    "hstar": best_sum[2], "d": best_sum[3]},
    "best_at_h1_zero": best_h1zero and {"sum": best_h1zero[0], "triple": best_h1zero[1],
                                        "hstar": best_h1zero[2], "d": best_h1zero[3]},
    "best_at_h1_le2": best_h1le2 and {"sum": best_h1le2[0], "triple": best_h1le2[1],
                                      "hstar": best_h1le2[2], "d": best_h1le2[3]},
    "min_coeff": min_coeff and {"value": str(min_coeff[0]), "triple": min_coeff[1],
                                "poly": min_coeff[2], "hstar": min_coeff[3],
                                "d": min_coeff[4]},
    "n_hits": len(hits),
    "hits": hits[:10],
    "hstar_multiset_by_d": {str(k): sorted(((list(h), c) for h, c in v.items()),
                                           key=lambda z: -sum(z[0]))[:8]
                            for k, v in sorted(by_d.items())},
}
print(json.dumps(out, indent=1))
