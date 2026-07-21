#!/usr/bin/env python3
"""Assemble runs/band9/manifest.json from ALL scan logs in this directory (v2).

v2 adds: the wcone S=72 exhaustive scan, the wbox 32/32/140 exhaustive scan,
the a1-steered descent (aclimb), the second cross-engine check (xcheck2.json),
and an INDEPENDENT exact union count of the exhaustive regions (union_count.py).
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import union_count as UC  # noqa: E402


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def parse(path):
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    blocks = txt.split("MODE ")
    out = []
    for b in blocks[1:]:
        d = {"mode": b.splitlines()[0].strip()}
        m = re.search(r"tested=(\d+) nonempty\(L1>0\)=(\d+) dim3\(V>0\)=(\d+) NEGATIVE=(\d+) bandTriplesCovered=(\d+)", b)
        if m:
            d["gap_classes_tested"] = int(m.group(1))
            d["Q_nonempty"] = int(m.group(2))
            d["dim3"] = int(m.group(3))
            d["negative_a1"] = int(m.group(4))
            d["band_triples_covered"] = int(m.group(5))
        m = re.search(r"min 6a1 \(all\)\s+= (-?\d+) \(V=(-?\d+) L1=(-?\d+)\) at\s+a=\(([\d,]+)\) b=\(([\d,]+)\) c=\(([\d,]+)\)", b)
        if m:
            d["min_6a1_all"] = int(m.group(1))
            d["min_6a1_all_at"] = {"a": m.group(4), "b": m.group(5), "c": m.group(6), "V": int(m.group(2)), "L1": int(m.group(3))}
        m = re.search(r"min 6a1 \(dim3\) = (-?\d+) \(V=(-?\d+) L1=(-?\d+)\) at\s+a=\(([\d,]+)\) b=\(([\d,]+)\) c=\(([\d,]+)\)", b)
        if m:
            d["min_6a1_dim3"] = int(m.group(1))
            d["min_6a1_dim3_at"] = {"a": m.group(4), "b": m.group(5), "c": m.group(6), "V": int(m.group(2)), "L1": int(m.group(3))}
        m = re.search(r"max V at L1=4/5/6 : (-?\d+) / (-?\d+) / (-?\d+)", b)
        if m:
            d["maxV_at_c4"] = int(m.group(1))
            d["maxV_at_c5"] = int(m.group(2))
            d["maxV_at_c6"] = int(m.group(3))
        m = re.search(r"max V\s+= (-?\d+) \(L1=(-?\d+)\) at\s+a=\(([\d,]+)\) b=\(([\d,]+)\) c=\(([\d,]+)\)", b)
        if m:
            d["maxV"] = int(m.group(1))
            d["maxV_at"] = {"a": m.group(3), "b": m.group(4), "c": m.group(5), "L1": int(m.group(2))}
        m = re.search(r"max V at h\*_1=0 \(L1=4\) = (-?\d+) at\s+a=\(([\d,]+)\) b=\(([\d,]+)\) c=\(([\d,]+)\)", b)
        if m:
            d["maxV_hstar1_zero"] = int(m.group(1))
            d["maxV_hstar1_zero_at"] = {"a": m.group(2), "b": m.group(3), "c": m.group(4)}
        m = re.search(r"max h\*_2 = (-?\d+) \(6a1=(-?\d+)\) at\s+a=\(([\d,]+)\) b=\(([\d,]+)\) c=\(([\d,]+)\)", b)
        if m:
            d["max_hstar2"] = int(m.group(1))
            d["max_hstar2_6a1"] = int(m.group(2))
        m = re.search(r"aclimb best 6a1 = (-?\d+) \(V=(-?\d+) L1=(-?\d+)\) lam=\(([\d,]+)\) mu=\(([\d,]+)\) nu=\(([\d,]+)\)", b)
        if m:
            d["aclimb_best_6a1"] = int(m.group(1))
            d["aclimb_best_at"] = {"lam": m.group(4), "mu": m.group(5), "nu": m.group(6),
                                   "V": int(m.group(2)), "L1": int(m.group(3))}
        m = re.search(r"climb best V at L1=4 : V=(-?\d+) 6a1=(-?\d+) lam=\(([\d,]+)\) mu=\(([\d,]+)\) nu=\(([\d,]+)\)", b)
        if m:
            d["climb_best_V_at_c4"] = int(m.group(1))
            d["climb_best_V_at_c4_at"] = {"lam": m.group(3), "mu": m.group(4), "nu": m.group(5), "six_a1": int(m.group(2))}
        out.append(d)
    return out


LOGS = ["wcone64.final.log", "wcone72.log", "wbox323240.log", "wbox444444.log",
        "wbox_asym.log", "rand.log", "climb_c6.log", "climb2.log", "aclimb.log"]

# regions whose EXHAUSTIVE coverage we claim (must exist in union_count.REGIONS)
CLAIMED = ["wcone S=72", "wbox 44/44/44", "wbox 140/8/8", "wbox 8/8/140",
           "wbox 8/140/8", "wbox 20/20/140"]


def main():
    scans = []
    for fn in LOGS:
        p = os.path.join(HERE, fn)
        blocks = parse(p)
        if not blocks:
            continue
        for b in blocks:
            if "gap_classes_tested" not in b:
                continue
            b["log"] = fn
            b["exhaustive"] = ("EXHAUSTIVE" in b["mode"])
            scans.append(b)

    claimed = list(CLAIMED)
    if os.path.exists(os.path.join(HERE, "wbox323240.log")):
        claimed.append("wbox 32/32/140")

    uni = union_of(claimed)

    tested = sum(s["gap_classes_tested"] for s in scans)
    neg = sum(s["negative_a1"] for s in scans)
    dim3 = sum(s["dim3"] for s in scans)
    maxV = max(s.get("maxV", -1) for s in scans)
    maxV0 = max(s.get("maxV_hstar1_zero", -1) for s in scans)
    min6d3 = min(s.get("min_6a1_dim3", 10 ** 18) for s in scans)
    min6all = min(s.get("min_6a1_all", 10 ** 18) for s in scans)
    maxh2 = max(s.get("max_hstar2", -1) for s in scans)

    xc = {}
    p = os.path.join(HERE, "xcheck2.json")
    if os.path.exists(p):
        j = json.load(open(p))
        xc = {"n": j["n"], "mismatches": j["mismatches"]}

    man = {
        "run": "band9",
        "hunter": "9 of 12 (Reeve-dimension sweep, r = 4)",
        "date": "2026-07-21",
        "target": "King-Tollu-Toumazet (2004) positivity conjecture: a triple (lam,mu,nu), "
                  "|lam|+|mu|=|nu|, whose stretched LR polynomial P(n)=c(n nu; n lam, n mu) "
                  "has a strictly negative coefficient. Also a FrontierMath open problem.",
        "band": "W = |nu| in [91,140]",
        "band_total_triples": uni["band_total_triples"],
        "band_total_gap_classes": uni["band_total_gap_classes"],
        "band_gap_region": "{(a,b,c) in Z_{>=0}^9 : Aw+Bw <= 140, Cw <= 140, 4 | (Cw-Aw-Bw)} "
                           "-- proved EXACTLY equal to the set of gap classes realised by a "
                           "triple with |nu| in [91,140]",
        "exhaustive_over_band": False,
        "exhaustive_sub_regions": claimed,
        "gap_classes_tested_total": tested,
        "dim3_polytopes_seen": dim3,
        "negative_coefficient_hits": neg,
        "min_a1_dim3": "%d/6" % min6d3,
        "min_a1_all_strata": "%d/6 (attained only where dim Q = 0, i.e. P is the constant 1)" % min6all,
        "max_normalized_volume": maxV,
        "max_normalized_volume_at_hstar1_zero": maxV0,
        "max_hstar2": maxh2,
        "negativity_criterion": "6*a1 = -11 + 18 L1 - 9 L2 + 2 L3 < 0, equivalently "
                                "h*_2 > 11 + 2 h*_1 + 2 h*_3 ; a3 = V/6 > 0 and a0 = 1 always",
        "scans": scans,
        "union_of_exhaustive_regions_gap_classes": uni["union_gap_classes"],
        "union_of_exhaustive_regions_band_triples": uni["union_band_triples"],
        "union_fraction_of_band_gap_classes": uni["union_fraction_gap_classes"],
        "union_fraction_of_band_triples": uni["union_fraction_band_triples"],
        "union_per_region": uni["per_region"],
        "union_independently_recomputed_by": "runs/band9/union_count.py (pure integer, reproduces the "
                                             "scanner's own bandTriplesCovered counter for every region "
                                             "and the band totals 7820553811824 / 171496406264085)",
        "engines": {
            "polytope_engine_exact": "r4_reeve/hive4.py (exact Fraction/int Ehrhart)",
            "fast_band_scanner": "r4_reeve/bandscan9.cpp -> bandscan9.exe/9b/9c ; "
                                 "r4_reeve/bandscan9d.cpp -> bandscan9d.exe (adds --aclimb, a1-steered descent)",
            "LR_engine_A": "engine/lr_hive.exe",
            "LR_engine_B": "engine/engineB_lrrule.py",
        },
        "cross_validation": {
            "round1": "40/40 exact agreement between hive4.py and the fast scanner on random dim-3 "
                      "triples with |nu| in [91,140]; 5 explicit band triples at stretch n=1,2,3 "
                      "against BOTH LR engines; both S=64 extremal records re-derived by hive4.py.",
            "round2_xcheck2": xc,
            "round2_detail": "runs/band9/xcheck2.py: fresh random dim-3 gap classes -> scanner (--one) vs "
                             "hive4.py exact Ehrhart (with held-out P(4),P(5)) vs LR engine A vs LR engine B "
                             "at stretch n=1 and n=2; L3 and V also compared scanner-vs-hive4.",
            "detector_unit_test": "reeve_detector_check.log -- on T_q, q=1..40, the integer criterion "
                                  "returns 6a1 = 12-q and V = q, firing NEGATIVE exactly for q >= 13.",
        },
        "honesty": "NO counterexample was found. Absence of a counterexample proves nothing "
                   "whatsoever about the King-Tollu-Toumazet conjecture and must NEVER be reported "
                   "as evidence for it. The only claim made here is that the enumerated windows are "
                   "closed. The band as a whole is NOT exhausted.",
    }
    files = {}
    for fn in ["bandscan9.cpp", "bandscan9.exe", "bandscan9b.exe", "bandscan9c.exe",
               "bandscan9d.cpp", "bandscan9d.exe", "hive4.py"]:
        p = os.path.join(ROOT, "r4_reeve", fn)
        if os.path.exists(p):
            files["r4_reeve/" + fn] = sha256(p)
    for fn in ["lr_hive.exe", "engineB_lrrule.py"]:
        p = os.path.join(ROOT, "engine", fn)
        if os.path.exists(p):
            files["engine/" + fn] = sha256(p)
    man["sha256"] = files
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(json.dumps({k: man[k] for k in
                      ["band", "gap_classes_tested_total", "dim3_polytopes_seen",
                       "negative_coefficient_hits", "min_a1_dim3", "max_normalized_volume",
                       "max_normalized_volume_at_hstar1_zero", "max_hstar2",
                       "union_of_exhaustive_regions_band_triples",
                       "union_fraction_of_band_triples"]}, indent=1))
    return 0


def union_of(names):
    preds = [UC.REGIONS[n] for n in names]
    N, MAXW = UC.N, UC.MAXW
    tot_cls = tot_tri = uni_cls = uni_tri = 0
    per = {n: [0, 0] for n in names}
    for A in range(MAXW + 1):
        nA = N[A]
        for B in range(MAXW + 1 - A):
            nAB = nA * N[B]
            for C in range(MAXW + 1):
                if (C - A - B) % 4:
                    continue
                m = UC.mult(A, B, C)
                if m == 0:
                    continue
                cls = nAB * N[C]
                tot_cls += cls
                tot_tri += cls * m
                inany = False
                for n, p in zip(names, preds):
                    if p(A, B, C):
                        per[n][0] += cls
                        per[n][1] += cls * m
                        inany = True
                if inany:
                    uni_cls += cls
                    uni_tri += cls * m
    return {
        "band_total_gap_classes": tot_cls,
        "band_total_triples": tot_tri,
        "union_gap_classes": uni_cls,
        "union_band_triples": uni_tri,
        "union_fraction_gap_classes": "%.4f%%" % (100.0 * uni_cls / tot_cls),
        "union_fraction_band_triples": "%.4f%%" % (100.0 * uni_tri / tot_tri),
        "per_region": {n: {"gap_classes": v[0], "band_triples": v[1]} for n, v in per.items()},
    }


if __name__ == "__main__":
    sys.exit(main())
