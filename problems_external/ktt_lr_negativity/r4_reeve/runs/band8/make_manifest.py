#!/usr/bin/env python3
"""
make_manifest.py -- assemble manifest.json for band 8 (W = |nu| in [61,90]).

Collects: aggregate.json (stage 1 nu-steering + stage 2 exhaustive splits),
plus the extra bandscan2 runs (uniform random band census, large max-V climb,
exhaustive single weights).  All numbers are exact integers produced by
bandscan.exe / bandscan2.exe; a_1 is reported as the exact fraction 6a1/6.
"""
import glob
import json
import os
import re
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

ACC = re.compile(r"^\[(.*?)\] tested=(\d+) pruned_contain=(\d+) nonempty=(\d+) dim3=(\d+) NEG=(\d+)")
KV = {
    "min6a1": re.compile(r"^\[.*?\] min6a1=(-?\d+) \(V=(\d+)\)"),
    "maxV": re.compile(r"^\[.*?\] maxV=(-?\d+)"),
    "maxVh1z": re.compile(r"^\[.*?\] maxV_hstar1_zero=(-?\d+)"),
    "maxh2": re.compile(r"^\[.*?\] max_hstar2=(-?\d+)"),
}
ARG = re.compile(r"lam=\((.*?)\) mu=\((.*?)\) nu=\((.*?)\)")
VC = re.compile(r"^\[.*?\] maxV_at_c=(\d+) : V=(-?\d+)\s+lam=\((.*?)\) mu=\((.*?)\) nu=\((.*?)\)")
HIST = re.compile(r"^\[.*?\] hist6a1 (\d+) (\d+)")
BIG = re.compile(r"^\[.*?\] min6a1_at_V_ge_100=(-?\d+) \(V=(\d+)\)")
HIT = re.compile(r"^\[.*?\] HIT (.*)$")


def blank():
    return {"tested": 0, "pruned": 0, "nonempty": 0, "dim3": 0, "neg": 0,
            "min6a1": None, "min6a1_V": None, "argmin": None,
            "maxV": -1, "argmaxV": None, "maxVh1z": -1, "argmaxVh1z": None,
            "maxh2": -1, "argmaxh2": None, "maxV_at_c": {}, "hist": {},
            "minBig": None, "minBigV": None, "argminBig": None, "hits": []}


def parse_text(txt, G=None):
    G = G or blank()
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        m = ACC.match(ln)
        if m:
            G["tested"] += int(m.group(2)); G["pruned"] += int(m.group(3))
            G["nonempty"] += int(m.group(4)); G["dim3"] += int(m.group(5)); G["neg"] += int(m.group(6))
            continue
        m = KV["min6a1"].match(ln)
        if m:
            v = int(m.group(1))
            if G["min6a1"] is None or v < G["min6a1"]:
                G["min6a1"] = v; G["min6a1_V"] = int(m.group(2)); G["argmin"] = ARG.search(lines[i+1]).groups()
            continue
        m = BIG.match(ln)
        if m:
            v = int(m.group(1))
            if G["minBig"] is None or v < G["minBig"]:
                G["minBig"] = v; G["minBigV"] = int(m.group(2)); G["argminBig"] = ARG.search(lines[i+1]).groups()
            continue
        for key, rx in (("maxV", KV["maxV"]), ("maxVh1z", KV["maxVh1z"]), ("maxh2", KV["maxh2"])):
            m = rx.match(ln)
            if m:
                v = int(m.group(1))
                if v > G[key]:
                    G[key] = v; G["arg" + key] = ARG.search(lines[i+1]).groups()
                break
        m = VC.match(ln)
        if m:
            c, v = int(m.group(1)), int(m.group(2))
            if v > G["maxV_at_c"].get(c, (-1, None))[0]:
                G["maxV_at_c"][c] = (v, m.group(3), m.group(4), m.group(5))
            continue
        m = HIST.match(ln)
        if m:
            G["hist"][int(m.group(1))] = G["hist"].get(int(m.group(1)), 0) + int(m.group(2))
            continue
        m = HIT.match(ln)
        if m:
            G["hits"].append(m.group(1))
    return G


def frac(six):
    f = Fraction(six, 6)
    return "%d/%d" % (f.numerator, f.denominator) if f.denominator != 1 else str(f.numerator)


def main():
    G = blank()
    files = []
    for pat in ("nutop_*.log", "nu_*.log", "randband*.log", "climbv*.log", "wexh_*.log"):
        for f in sorted(glob.glob(os.path.join(HERE, pat))):
            files.append(os.path.basename(f))
            parse_text(open(f).read(), G)

    agg = json.load(open(os.path.join(HERE, "aggregate.json"))) if os.path.exists(os.path.join(HERE, "aggregate.json")) else {}
    exh = []
    for f in sorted(glob.glob(os.path.join(HERE, "wexh_*.log"))):
        W = int(re.search(r"wexh_(\d+)", f).group(1))
        d = parse_text(open(f).read())
        exh.append({"weight": W, "kind": "ALL triples with |nu|=W (every nu with <=4 parts, every ordered split)",
                    "tested": d["tested"], "pruned_contain": d["pruned"], "nonempty": d["nonempty"],
                    "dim3": d["dim3"], "neg": d["neg"], "min6a1": d["min6a1"], "min_a1": frac(d["min6a1"]),
                    "maxV": d["maxV"], "maxV_hstar1_zero": d["maxVh1z"], "max_hstar2": d["maxh2"]})

    nu_exh = []
    for f in sorted(glob.glob(os.path.join(HERE, "nu_*.log"))):
        nu = [int(x) for x in re.search(r"nu_(\d+)_(\d+)_(\d+)_(\d+)", f).groups()]
        d = parse_text(open(f).read())
        nu_exh.append({"nu": nu, "W": sum(nu), "tested_all_splits": d["tested"],
                       "pruned_contain": d["pruned"], "nonempty": d["nonempty"], "dim3": d["dim3"],
                       "neg": d["neg"], "min6a1": d["min6a1"], "maxV": d["maxV"],
                       "maxV_hstar1_zero": d["maxVh1z"], "max_hstar2": d["maxh2"]})
    nu_exh.sort(key=lambda r: -r["maxV"])

    man = {
        "band": "W = |nu| in [61,90]  (band 8 of 12, r = 4 Reeve-dimension sweep)",
        "hunter": "band8",
        "target": "King-Tollu-Toumazet positivity conjecture (2004): a stretched LR polynomial P(n)=c(n.nu;n.lam,n.mu) with a strictly negative coefficient",
        "cell": "r = 4  =>  hive polytope Q(lam,mu,nu) has ambient dimension (r-1)(r-2)/2 = 3 (the Reeve dimension)",
        "identities_used": {
            "P": "P(n) = L(n) = #(nQ cap Z^3), deg <= 3, P(0)=1",
            "6a1": "6*a1 = -11 + 18 L(1) - 9 L(2) + 2 L(3) = 11 + 2h*_1 - h*_2 + 2h*_3",
            "V": "V = 6*a3 = L(3) - 3L(2) + 3L(1) - 1 = 1 + h*_1 + h*_2 + h*_3",
            "negativity_criterion": "a1 < 0  <=>  h*_2 > 11 + 2 h*_1 + 2 h*_3   (a0=1, a2 = 1 + (h*_1-h*_3)/2 >= 0, a3 = V/6 > 0)"
        },
        "engines": {
            "primary": "bandscan.exe / bandscan2.exe (this dir) -- exact 64-bit integer fibre counting, rhombus rows verbatim from the validated gapscan.cpp",
            "reference": "hive4.py (exact Fraction Ehrhart engine)",
            "LR_cross": ["engine/lr_hive.exe (A)", "engine/engineB_lrrule.py (B)"]
        },
        "validation": json.load(open(os.path.join(HERE, "validation_band8.json")))
        if os.path.exists(os.path.join(HERE, "validation_band8.json")) else None,
        "logs": files,
        "totals": {
            "triples_tested": G["tested"],
            "pruned_by_containment_P_identically_zero": G["pruned"],
            "Q_nonempty": G["nonempty"],
            "dim_Q_eq_3": G["dim3"],
            "negative_coefficient_hits": G["neg"],
        },
        "min_6a1": G["min6a1"],
        "min_a1_exact": frac(G["min6a1"]) if G["min6a1"] is not None else None,
        "argmin_a1": G["argmin"],
        "min_6a1_restricted_V_ge_100": G["minBig"],
        "argmin_V_ge_100": G["argminBig"],
        "max_V": G["maxV"], "argmax_V": G["argmaxV"],
        "max_V_at_hstar1_zero": G["maxVh1z"], "argmax_V_at_hstar1_zero": G["argmaxVh1z"],
        "max_hstar2": G["maxh2"], "argmax_hstar2": G["argmaxh2"],
        "max_V_at_fixed_lattice_point_count_c": {str(k): {"V": v[0], "lam": v[1], "mu": v[2], "nu": v[3]}
                                                 for k, v in sorted(G["maxV_at_c"].items())},
        "hist_6a1": {str(k): v for k, v in sorted(G["hist"].items())},
        "hits": G["hits"],
        "exhaustive_weights": exh,
        "exhaustive_nu_slices_all_splits": nu_exh,
        "stage1_nu_steering": agg.get("stage1"),
        "exhaustive": {
            "band_as_a_whole": False,
            "why": "the band contains 1.32e12 ordered triples (see band_size); a full enumeration is out of reach at ~1e6 exact Ehrhart evaluations/s",
            "exhaustive_sublevels": [
                "every weight W listed in exhaustive_weights is CLOSED: all nu with at most 4 parts and all ordered splits",
                "every nu listed in exhaustive_nu_slices_all_splits is CLOSED over ALL ordered splits (lam,mu)"
            ]
        },
        "honesty_note": "The absence of a negative coefficient proves NOTHING about the King-Tollu-Toumazet conjecture and is not evidence for it. It only closes the enumerated window.",
    }
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(json.dumps({"triples_tested": G["tested"], "dim3": G["dim3"], "neg": G["neg"],
                      "min6a1": G["min6a1"], "min_a1": man["min_a1_exact"], "maxV": G["maxV"],
                      "maxV_h1zero": G["maxVh1z"], "max_hstar2": G["maxh2"],
                      "exh_weights": [e["weight"] for e in exh], "n_nu_slices": len(nu_exh)}, indent=1))


if __name__ == "__main__":
    main()
