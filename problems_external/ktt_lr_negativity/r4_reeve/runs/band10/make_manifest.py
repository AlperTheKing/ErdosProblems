#!/usr/bin/env python3
"""make_manifest.py -- assemble runs/band10/manifest.json from the run logs."""
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def read(p):
    q = os.path.join(HERE, p)
    return open(q, encoding="utf-8-sig", errors="replace").read() if os.path.exists(q) else ""


def grab(txt, pat, cast=str):
    m = re.search(pat, txt)
    return cast(m.group(1)) if m else None


def main():
    g12 = read("scan_G12_perc.log")
    ex12 = read("b10_exh12.log")
    ex6 = read("b10_exh6.log")
    ex8 = read("b10_exh8_c4count.log")
    r1 = read("b10_rand_bigK.log")
    deep = read("b10_rand_K1e9_deep.log")
    sub = json.loads(read("subset_atlas.json") or "{}")
    lat = json.loads(read("lattice_certificate.json") or "{}")

    perc = {}
    for m in re.finditer(r"c=\s*(\d+) : Vmax=\s*(\d+)", g12):
        perc[int(m.group(1))] = int(m.group(2))

    def randblocks(txt):
        out = []
        for blk in re.split(r"(?=BAND10 RANDOM)", txt):
            if not blk.strip().startswith("BAND10 RANDOM"):
                continue
            out.append({
                "K": grab(blk, r"K=(\d+)", int),
                "N": grab(blk, r"N=(\d+)", int),
                "realisable": grab(blk, r"realisable\(4\|D\)=(\d+)", int),
                "nonempty": grab(blk, r"nonempty Q=(\d+)", int),
                "max_vertex_denominator": grab(blk, r"max vertex denominator = (\d+)", int),
                "max_simple_vertex_multiplicity": grab(blk, r"max simple-vertex multiplicity = (\d+)", int),
                "max_V_simplex": grab(blk, r"max V over 4-vertex lattice simplices=(-?\d+)"),
                "max_V_primitive_edge_simplex": grab(blk, r"ALL EDGES PRIMITIVE \(c=4 candidates\)=(-?\d+)"),
                "n_c4_candidates_V_ge_2": grab(blk, r"CANDIDATES\) = (\d+)", int),
            })
        return out

    rnd = randblocks(r1) + randblocks(deep)

    man = {
        "band": "band10 -- r=4 (Reeve dimension), TARGETED c = 4 (h*_1 = 0) with V >= 2, unbounded weight",
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engines": {
            "polytope": "r4_reeve/hive4.py (exact Fraction/int Ehrhart)",
            "scanner": "r4_reeve/band10.cpp -> band10.exe / band10b.exe (exact integer / __int128)",
            "ehrhart_census": "r4_reeve/gapscan.cpp -> gapscan4.exe",
            "LR_A": "engine/lr_hive.exe",
            "LR_B": "engine/engineB_lrrule.py",
        },
        "moduli_framing": (
            "Q depends on (lam,mu,nu) only through the 9 gaps, up to a lattice translation "
            "(verified: 386/386 random pairs agree on dim,c,L(0..5),h*,V,P). One gap class contains "
            "triples of arbitrarily large weight, so a gap-box census is an all-weights census."
        ),
        "exhaustive_ehrhart_census_G12": {
            "log": "scan_G12_perc.log",
            "gap_vectors": grab(g12, r"vectors=(\d+)", int),
            "realisable_gap_classes": grab(g12, r"realisable\(4\|D\)=(\d+)", int),
            "negative_a1_count": grab(g12, r"NEGATIVE a1 count = (\d+)", int),
            "min_6a1": grab(g12, r"min 6a1 = (\d+)", int),
            "max_V": grab(g12, r"max V   = (\d+)", int),
            "max_V_at_fixed_c": perc,
        },
        "exhaustive_structural_census_G12": {
            "log": "b10_exh12.log",
            "realisable_gap_classes": grab(ex12, r"realisable\(4\|D\)=(\d+)", int),
            "nonempty": grab(ex12, r"nonempty Q=(\d+)", int),
            "max_vertex_denominator": grab(ex12, r"max vertex denominator = (\d+)", int),
            "max_simple_vertex_multiplicity": grab(ex12, r"max simple-vertex multiplicity = (\d+)", int),
            "max_V_simplex": grab(ex12, r"max V over 4-vertex lattice simplices=(-?\d+)"),
            "max_V_primitive_edge_simplex": grab(ex12, r"ALL EDGES PRIMITIVE \(c=4 candidates\)=(-?\d+)"),
            "n_c4_candidates_V_ge_2": grab(ex12, r"CANDIDATES\) = (\d+)", int),
            "n_c4_exact": grab(ex12, r"exactly c=4, V=1\) = (\d+)", int),
        },
        "exhaustive_structural_census_G6": {
            "log": "b10_exh6.log",
            "realisable_gap_classes": grab(ex6, r"realisable\(4\|D\)=(\d+)", int),
            "max_vertex_denominator": grab(ex6, r"max vertex denominator = (\d+)", int),
            "n_c4_candidates_V_ge_2": grab(ex6, r"CANDIDATES\) = (\d+)", int),
        },
        "c4_stratum_census_G8": {
            "log": "b10_exh8_c4count.log",
            "realisable_gap_classes": grab(ex8, r"realisable\(4\|D\)=(\d+)", int),
            "n_c4_exact": grab(ex8, r"exactly c=4, V=1\) = (\d+)", int),
            "n_c4_with_V_ge_2": grab(ex8, r"CANDIDATES\) = (\d+)", int),
            "max_V_at_c4": grab(ex8, r"ALL EDGES PRIMITIVE \(c=4 candidates\)=(-?\d+)"),
        },
        "det_gt1_diagnostic": {
            "files": ["det_gt1_probe.json", "det_gt1_violation_structure.json"],
            "feasible_points_from_singular_index_triples": 5070,
            "of_those_non_integral": 0,
            "non_integral_cramer_points_seen_overall": 147614,
            "all_of_them_infeasible": True,
            "no_uniform_violated_row": True,
        },
        "random_unbounded_weight": rnd,
        "normal_fan_atlas": {
            "file": "subset_atlas.json",
            "n_directions": sub.get("n_directions"),
            "triple_multiplicity_histogram": sub.get("triple_multiplicity_histogram"),
            "n_4subsets_positively_spanning": sub.get("n_4subsets_positively_spanning"),
            "multiplicity_profiles": sub.get("multiplicity_profile_histogram_over_bounded_4subsets"),
            "max_common_multiplicity": sub.get("max_common_multiplicity"),
            "verdict": sub.get("VERDICT"),
        },
        "vertex_integrality": {
            "file": "lattice_certificate.json",
            "identical_congruence_certificate": lat.get("CERTIFIED"),
            "det_histogram_over_row_triples": lat.get("det_histogram"),
            "n_violations": lat.get("n_violations"),
            "status": (
                "NOT PROVED. Non-integral Cramer solutions exist for 49 of the 517 non-singular row "
                "triples (|det| = 2 or 4), so integrality is not an identity in b. It is VERIFIED "
                "empirically: max vertex denominator = 1 over every scan performed here "
                "(1.65e9 exhaustive gap classes + 6.4e8 random classes with gaps up to 1e9)."
            ),
        },
        "hits": [],
        "verified_records": [
            {"file": "verify_g12_minA1.json",
             "lam": [9, 7, 6, 0], "mu": [9, 2, 1, 0], "nu": [10, 9, 8, 7], "weight": 34,
             "c": 4, "V": 1, "hstar": [1, 0, 0, 0], "L": [1, 4, 10, 20, 35, 56],
             "P": "1 + (11/6) n + n^2 + (1/6) n^3",
             "engines_agree": ["hive4.py", "lr_hive.exe (A)", "engineB_lrrule.py (B)"],
             "note": "global a_1-minimiser of the exhaustive G=12 census"},
            {"lam": [1570, 1506, 459, 0], "mu": [2677, 1648, 198, 0], "nu": [3042, 1743, 1730, 1543],
             "weight": 8058, "c": 4, "V": 1, "hstar": [1, 0, 0, 0], "L": [1, 4, 10, 20, 35, 56],
             "engines_agree": ["hive4.py", "lr_hive.exe (A) for n=1,2,3"],
             "note": "large-weight c=4 record found by the K=2000 random scan"},
            {"lam": [10774277, 4163047, 2874548, 0], "mu": [14293959, 13601889, 3628836, 0],
             "nu": [23359359, 13729572, 6375702, 5871923], "weight": 49336556,
             "c": 4, "V": 1, "hstar": [1, 0, 0, 0], "L": [1, 4, 10, 20, 35, 56],
             "engines_agree": ["hive4.py"],
             "note": "engine A returns CAP_EXCEEDED at this size (node cap), not a disagreement"},
            {"file": "unbounded_weight_c4.json",
             "family": "lam=(9,7,6,0)+t, mu=(9,2,1,0), nu=(10,9,8,7)+t",
             "t_tested": [0, 1000, 10 ** 6, 10 ** 9, 10 ** 12],
             "weights": [34, 4034, 4000034, 4000000034, 4000000000034],
             "c": 4, "V": 1, "P": "1 + (11/6) n + n^2 + (1/6) n^3",
             "note": "same c=4 class exhibited at unbounded weight"},
        ],
        "honesty": (
            "No negative coefficient was found. This is an exhaustive negative census of the r=4 cell "
            "over gaps <= 12 (all weights) plus a large random census at gaps up to 1e9. Absence of a "
            "counterexample is NOT evidence for the King-Tollu-Toumazet conjecture."
        ),
    }
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(json.dumps(man, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
