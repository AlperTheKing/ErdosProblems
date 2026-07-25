#!/usr/bin/env python3
"""fam12 aggregator: exact base-rate statistics over tier0_screen.py records.

Everything reported is an exact integer / exact count.  No float decides
anything.  The three protocol quantities:

  (i)   max h*_d observed (with the triple)
  (ii)  min (h*_1 - h*_d) observed (with the triple)   <- distance to JACKPOT
  (iii) every record with TIER0 / JACKPOT / NEG true
"""
import json
import sys
from collections import Counter

files = sys.argv[1:]
rows = []
for f in files:
    tag = f
    for ln in open(f):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
        except Exception:
            continue
        rec["_src"] = tag
        rows.append(rec)

status = Counter(r.get("status", "?") for r in rows)
by_r = Counter(r.get("r") for r in rows)

ok = [r for r in rows if r.get("status") == "OK"]
nonempty = ok  # status OK <=> nonempty and fully screened

# audit gates -- every OK record must pass all of them
audit_fields = ["heldout_ok", "hstar_0_is_1", "hstar_nonneg", "hstar_tail_zero",
                "hstar_roundtrip_ok", "interior_check_ok", "hstar_1_identity_ok",
                "moment_criteria_consistent"]
audit_fail = []
for r in ok:
    for fld in audit_fields:
        if fld in r and r[fld] is not True:
            audit_fail.append((r["lam"], r["mu"], r["nu"], fld, r[fld]))
            break

hits = [r for r in rows if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG")]

# --- protocol quantities -------------------------------------------------
best_hd, best_hd_rec = None, None
min_gap, min_gap_rec = None, None
gapdist = Counter()
h1_zero = 0
hd_pos = 0
both = 0
ddist = Counter()
neg_hstar = 0
hd_le_h1_viol = 0

for r in ok:
    d = r.get("d")
    ddist[d] += 1
    h1 = r.get("hstar_1")
    hd = r.get("hstar_d")
    if isinstance(hd, int):
        if best_hd is None or hd > best_hd:
            best_hd, best_hd_rec = hd, r
        if hd > 0:
            hd_pos += 1
    if isinstance(h1, int):
        if h1 == 0:
            h1_zero += 1
        if isinstance(hd, int):
            g = h1 - hd
            gapdist[g] += 1
            if min_gap is None or g < min_gap:
                min_gap, min_gap_rec = g, r
            if g < 0:
                hd_le_h1_viol += 1
    if isinstance(h1, int) and isinstance(hd, int) and h1 == 0 and hd > 0:
        both += 1
    hs = r.get("hstar") or []
    if any((isinstance(x, int) and x < 0) for x in hs):
        neg_hstar += 1

# non-lattice evidence proxy: hstar_sum vs c/d relations cannot certify
# rationality directly; we count records whose h*-vector is NOT achievable
# by any lattice polytope under the standard inequalities.
nonlattice = 0
nonlat_ex = []
for r in ok:
    h1 = r.get("hstar_1")
    hd = r.get("hstar_d")
    hs = r.get("hstar") or []
    d = r.get("d") or 0
    viol = []
    if isinstance(h1, int) and isinstance(hd, int) and hd > h1:
        viol.append("hstar_d>hstar_1")
    # Hibi's LOWER BOUND theorem: valid only for a LATTICE polytope that
    # HAS an interior lattice point.  Applying it without that hypothesis
    # is unsound, so gate on h*_d >= 1.
    if isinstance(h1, int) and isinstance(hd, int) and hd >= 1 and d >= 2:
        for j in range(1, d):
            if isinstance(hs[j], int) and hs[j] < h1:
                viol.append("hibi_lower_bound_j=%d" % j)
                break
    if viol:
        nonlattice += 1
        if len(nonlat_ex) < 20:
            nonlat_ex.append({"lam": r["lam"], "mu": r["mu"], "nu": r["nu"],
                              "hstar": hs, "viol": viol})

# --- stratified by d (the hunt zone is d >= 4; d=0 has no h*_1 and
# --- h*_d = h*_0 = 1 trivially; d=1 forces h*_1 = h*_d identically) ------
strata = {}
for name, pred in (("d>=2", lambda d: d >= 2),
                   ("d>=4", lambda d: d >= 4),
                   ("d>=5", lambda d: d >= 5)):
    sub = [r for r in ok if isinstance(r.get("d"), int) and pred(r["d"])
           and isinstance(r.get("hstar_1"), int)
           and isinstance(r.get("hstar_d"), int)]
    if not sub:
        strata[name] = {"n": 0}
        continue
    gaps = [(r["hstar_1"] - r["hstar_d"], r) for r in sub]
    mg, mr = min(gaps, key=lambda t: t[0])
    bh, br = max(((r["hstar_d"], r) for r in sub), key=lambda t: t[0])
    strata[name] = {
        "n": len(sub),
        "count_hstar1_eq_0": sum(1 for r in sub if r["hstar_1"] == 0),
        "count_hstar_d_gt_0": sum(1 for r in sub if r["hstar_d"] > 0),
        "count_TIER0": sum(1 for r in sub
                           if r["hstar_1"] == 0 and r["hstar_d"] > 0),
        "count_JACKPOT": sum(1 for r in sub if r["hstar_d"] > r["hstar_1"]),
        "min_gap": mg,
        "max_hstar_d": bh,
        "_mg_rec": mr, "_bh_rec": br,
    }
    # the informative sub-case: gap among records that actually HAVE an
    # interior lattice point (h*_d > 0).  h*_1 = 0 records all turn out to
    # be unimodular simplices h* = (1,0,...,0), where h*_d = 0 forces gap 0.
    pos = [(r["hstar_1"] - r["hstar_d"], r) for r in sub if r["hstar_d"] > 0]
    if pos:
        pg, pr = min(pos, key=lambda t: t[0])
        strata[name]["n_hstar_d_pos"] = len(pos)
        strata[name]["min_gap_given_interior_point"] = pg
        strata[name]["_pg_rec"] = pr
    else:
        strata[name]["n_hstar_d_pos"] = 0
        strata[name]["min_gap_given_interior_point"] = None
    shapes = Counter(tuple(r["hstar"]) for r in sub if r["hstar_1"] == 0)
    strata[name]["hstar_shapes_when_hstar1_zero"] = {
        str(list(k)): v for k, v in shapes.most_common(8)}


def brief(r):
    if r is None:
        return None
    return {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "r": r["r"],
            "d": r["d"], "c": r["c"], "hstar": r.get("hstar"),
            "hstar_1": r.get("hstar_1"), "hstar_d": r.get("hstar_d"),
            "hstar_sum": r.get("hstar_sum"), "src": r["_src"]}

res = {
    "records_total": len(rows),
    "status_counts": dict(status),
    "records_by_r": {str(k): v for k, v in sorted(by_r.items(), key=lambda x: str(x[0]))},
    "nonempty_OK": len(ok),
    "audit_failures": len(audit_fail),
    "audit_failure_examples": audit_fail[:10],
    "d_distribution": {str(k): v for k, v in sorted(ddist.items(), key=lambda x: (x[0] is None, x[0]))},
    "count_hstar1_eq_0": h1_zero,
    "count_hstar_d_gt_0": hd_pos,
    "count_both_hstar1_0_and_hstar_d_gt_0__TIER0": both,
    "count_hstar_d_gt_hstar_1__JACKPOT": hd_le_h1_viol,
    "count_negative_hstar_entry": neg_hstar,
    "best_hstar_d": best_hd,
    "best_hstar_d_triple": brief(best_hd_rec),
    "min_hstar1_minus_hstar_d": min_gap,
    "min_gap_triple": brief(min_gap_rec),
    "gap_distribution_low20": dict(sorted(gapdist.items())[:20]),
    "lattice_inequality_violations": nonlattice,
    "lattice_inequality_violation_examples": nonlat_ex,
    "hits": [brief(r) for r in hits][:50],
    "per_source": {f: {"total": sum(1 for r in rows if r["_src"] == f),
                       "OK": sum(1 for r in rows
                                 if r["_src"] == f and r.get("status") == "OK"),
                       "EMPTY": sum(1 for r in rows
                                    if r["_src"] == f
                                    and r.get("status") == "EMPTY"),
                       "other": sum(1 for r in rows
                                    if r["_src"] == f
                                    and r.get("status") not in ("OK", "EMPTY"))}
                   for f in files},
    "strata": {k: ({kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                   | ({"min_gap_triple": brief(v["_mg_rec"]),
                       "max_hstar_d_triple": brief(v["_bh_rec"]),
                       "min_gap_given_interior_triple": brief(v.get("_pg_rec"))}
                      if v.get("n") else {}))
               for k, v in strata.items()},
}
print(json.dumps(res, indent=2))
