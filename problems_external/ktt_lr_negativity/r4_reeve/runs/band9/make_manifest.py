#!/usr/bin/env python3
"""Assemble runs/band9/manifest.json from the scan logs in this directory."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def parse(path):
    """Parse one bandscan9 report block (last one in the file)."""
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
        out.append(d)
    return out


def main():
    scans = []
    for fn in ["wcone64.final.log", "wbox444444.log", "wbox_asym.log", "rand.log", "climb_c6.log"]:
        p = os.path.join(HERE, fn)
        blocks = parse(p)
        if not blocks:
            continue
        for b in blocks:
            b["log"] = fn
            b["exhaustive"] = ("EXHAUSTIVE" in b["mode"])
            scans.append(b)

    tested = sum(s["gap_classes_tested"] for s in scans)
    neg = sum(s["negative_a1"] for s in scans)
    dim3 = sum(s["dim3"] for s in scans)
    covered = sum(s["band_triples_covered"] for s in scans)
    maxV = max(s.get("maxV", -1) for s in scans)
    maxV0 = max(s.get("maxV_hstar1_zero", -1) for s in scans)
    min6d3 = min(s.get("min_6a1_dim3", 10 ** 18) for s in scans)
    min6all = min(s.get("min_6a1_all", 10 ** 18) for s in scans)
    maxh2 = max(s.get("max_hstar2", -1) for s in scans)

    man = {
        "run": "band9",
        "hunter": "9 of 12 (Reeve-dimension sweep, r = 4)",
        "date": "2026-07-21",
        "target": "King-Tollu-Toumazet (2004) positivity conjecture: a triple (lam,mu,nu), "
                  "|lam|+|mu|=|nu|, whose stretched LR polynomial P(n)=c(n nu; n lam, n mu) "
                  "has a strictly negative coefficient. Also a FrontierMath open problem.",
        "band": "W = |nu| in [91,140]",
        "band_total_triples": 171496406264085,
        "band_total_gap_classes": 7820553811824,
        "band_gap_region": "{(a,b,c) in Z_{>=0}^9 : Aw+Bw <= 140, Cw <= 140, 4 | (Cw-Aw-Bw)} "
                           "-- proved EXACTLY equal to the set of gap classes realised by a "
                           "triple with |nu| in [91,140]",
        "exhaustive_over_band": False,
        "exhaustive_sub_regions": [s["mode"] for s in scans if s["exhaustive"]],
        "gap_classes_tested_total": tested,
        "band_triples_covered_by_exhaustive_scans": covered,
        "dim3_polytopes_seen": dim3,
        "negative_coefficient_hits": neg,
        "min_a1_dim3": "%d/6" % min6d3,
        "min_a1_all_strata": "%d/6" % min6all,
        "max_normalized_volume": maxV,
        "max_normalized_volume_at_hstar1_zero": maxV0,
        "max_hstar2": maxh2,
        "negativity_criterion": "6*a1 = -11 + 18 L1 - 9 L2 + 2 L3 < 0, equivalently "
                                "h*_2 > 11 + 2 h*_1 + 2 h*_3 ; a3 = V/6 > 0 and a0 = 1 always",
        "scans": scans,
        "engines": {
            "polytope_engine_exact": "r4_reeve/hive4.py (exact Fraction/int Ehrhart)",
            "fast_band_scanner": "r4_reeve/bandscan9.cpp -> bandscan9.exe / bandscan9b.exe (integer only)",
            "LR_engine_A": "engine/lr_hive.exe",
            "LR_engine_B": "engine/engineB_lrrule.py",
        },
        "cross_validation": "40/40 exact agreement between hive4.py and the fast scanner on random "
                            "dim-3 triples with |nu| in [91,140]; 5 explicit band triples verified at "
                            "stretch n=1,2,3 against BOTH LR engines A and B; both extremal records of "
                            "the S=64 exhaustive scan re-derived exactly by hive4.py (held-out P(4),P(5) "
                            "checks passed, max vertex denominator 1, 6*lead(P)=V).",
        "honesty": "NO counterexample was found. Absence of a counterexample proves nothing "
                   "whatsoever about the King-Tollu-Toumazet conjecture and must NEVER be reported "
                   "as evidence for it. The only claim made here is that the enumerated windows are "
                   "closed.",
    }
    files = {}
    for fn in ["bandscan9.cpp", "bandscan9.exe", "bandscan9b.exe", "hive4.py"]:
        p = os.path.join(ROOT, "r4_reeve", fn)
        if os.path.exists(p):
            files[fn] = sha256(p)
    for fn in ["lr_hive.exe", "engineB_lrrule.py"]:
        p = os.path.join(ROOT, "engine", fn)
        if os.path.exists(p):
            files[fn] = sha256(p)
    man["sha256"] = files
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(json.dumps({k: man[k] for k in
                      ["band", "gap_classes_tested_total", "band_triples_covered_by_exhaustive_scans",
                       "dim3_polytopes_seen", "negative_coefficient_hits", "min_a1_dim3",
                       "min_a1_all_strata", "max_normalized_volume",
                       "max_normalized_volume_at_hstar1_zero", "max_hstar2"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
