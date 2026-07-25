#!/usr/bin/env python3
"""
Merge the band10 WAVE-2 (second independent pass) results into manifest.json.
Wave-1 content is preserved verbatim; wave 2 is added under its own key.
"""
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.join(HERE, "manifest.json")


def readlog(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return None
    with open(p, errors="replace") as f:
        return f.read()


def grab(txt, pat, cast=str):
    if txt is None:
        return None
    m = re.search(pat, txt)
    return cast(m.group(1)) if m else None


def census(name, kind):
    t = readlog(name)
    if t is None:
        return {"log": name, "status": "missing"}
    d = {"log": name, "kind": kind,
         "vectors": grab(t, r"vectors=(\d+)", int),
         "realisable_gap_classes": grab(t, r"realisable(?:\(4\|D\))?=(\d+)", int),
         "negative_a1_count": grab(t, r"NEGATIVE(?: a1 count)? = (\d+)", int),
         "min_6a1": grab(t, r"min 6a1 = (-?\d+)", int),
         "max_V": grab(t, r"max V\s*=\s*(\d+)", int),
         "max_V_at_c4_hstar1_zero": grab(t, r"max V at c=4 \(h\*_1=0\) = (-?\d+)", int),
         }
    if d["max_V_at_c4_hstar1_zero"] is None:
        d["max_V_at_c4_hstar1_zero"] = grab(t, r"c= 4 : Vmax=\s*(\d+)", int)
    if d["max_V"] is None:
        d["max_V"] = grab(t, r"max V\s+= (\d+)", int)
    return d


def main():
    with open(MAN) as f:
        man = json.load(f)

    w2 = {
        "role": ("second independent pass over band10 by hunter 10 of 12; "
                 "re-verifies wave 1 with the engines re-run from scratch and "
                 "extends it with a strictly larger exhaustive box, three "
                 "geometric-ladder censuses and two slab censuses"),
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "new_engine": {
            "source": "runs/band10/band10w2.cpp -> band10w2.exe",
            "modes": ["--ladder v1,..,vk (exhaustive over a value ladder)",
                      "--slab MAXUV v1,..,vk (g[1],g[7] in [1,MAXUV], other 7 over a ladder)"],
            "eval_core": "identical eval_gaps() as gapscan.cpp (exact int64)",
        },
        "structural_facts_established_this_pass": {
            "homogeneity": ("a_k(t g) = t^k a_k(g) for the gap vector g "
                            "(Q(t g) = t Q(g) up to lattice translation). Hence "
                            "{g : a_1(g) < 0} is a CONE: an exhaustive census of a "
                            "box or ladder settles every ray through it, at every "
                            "weight. Verified exactly on 224 (g,t) pairs, t = 2,3."),
            "only_a1_can_be_negative": ("a_0 = 1; a_3 = V/6 > 0 in dim 3; a_2 is half "
                                        "the lattice-normalized surface area of a lattice "
                                        "3-polytope, hence > 0. So the whole r=4 cell "
                                        "reduces to the sign of "
                                        "6a_1 = 11 + 2h*_1 - h*_2 + 2h*_3 = 3(c+i) - V."),
            "negativity_threshold": ("a_1 < 0 at r=4 <=> h*_2 > 2h*_1 + 2h*_3 + 11 "
                                     "<=> V > 3(c + i). Every census below reports "
                                     "min 6a1 = 11, i.e. a uniform slack of 11."),
            "A3_subsystem_unimodular_in_triples": (
                "of the 15 fixed rhombus directions, the 12 A3/alcoved ones give 0 "
                "triples with |det| > 1; every one of the 49 bad triples (48 with "
                "|det|=2, 1 with |det|=4) contains at least one of the three ODD rows "
                "R_A, R_B, R_C (rhombi A(1,1), B(1,1), C(1,1)). A non-integral vertex "
                "therefore requires an odd row to be tight. "
                "REFUTED en route: the stronger claim '|det|>1 implies >= 2 odd rows' "
                "(18 counterexample triples have exactly one)."),
            "file": "b10w2_integrality_locus.py / .json",
        },
        "independent_verification": {
            "file": "b10w2_verify.py / b10w2_verify.json",
            "homogeneity_pairs_tested": 224,
            "gapscan_vs_hive4_triples": 250,
            "hive4_vs_LR_engines_A_and_B_stretched_counts": 120,
            "slab_regime_overflow_crosscheck": "b10w2_slabxcheck.json (60/60 exact "
                                               "agreement, weights up to 128046)",
            "hive4_selftest": "PASS (Reeve T_q q=1..20, c=1 => P==1, c=2 => P=n+1)",
            "verdict": "PASS -- no disagreement anywhere",
        },
        "atlas_rederived_independently": {
            "file": "b10w2_atlas.py / b10w2_atlas.json",
            "n_distinct_directions": 15,
            "n_4subsets_positively_spanning_and_simple": 36,
            "index_profiles": {"(1,1,1,1)": 18, "(1,1,2,2)": 6, "(1,1,1,4)": 12},
            "constant_index_values": [1],
            "conclusion": ("under the (verified, unproved) hypothesis that hive "
                           "vertices are integral, dim 3 with c = 4 forces an EMPTY "
                           "lattice 3-simplex whose four vertex-cone indices are all "
                           "equal to V; the only constant profile is (1,1,1,1), so "
                           "V = 1 at every weight and the Reeve mechanism (needs "
                           "V = q >= 13) cannot fire at r = 4"),
        },
        "censuses": {
            "exhaustive_box_G14": {
                "log": "scan_G14.log",
                "kind": "exhaustive box [0,14]^9",
                "vectors": 38443359375,
                "status": "IN FLIGHT at the time this manifest was written -- "
                          "NOT complete, NOT used in any conclusion below. Its "
                          "log completes itself when the run ends.",
            },
            "exhaustive_box_G10_reproduce": census("ladder_box10_reproduce.log",
                                                   "exhaustive box [0,10]^9 "
                                                   "(independent reproduction of the "
                                                   "wave-1 box census with a different "
                                                   "binary)"),
            "slab_uv8_max5e4": census("slab_uv8_5e4.log", "slab MAXUV=8, ladder to 5e4"),
            "slab_uv10_max2e4": census("slab_uv10_2e4.log", "slab MAXUV=10, ladder to 2e4"),
            "slab_uv12_max7e3": census("slab_uv12_7e3.log", "slab MAXUV=12, ladder to 7e3"),
            "ladder_fib_max34": census("ladder_fib34.log", "ladder 0,1,2,3,5,8,13,21,34"),
            "ladder_pow2_max128": census("ladder_pow2_128.log", "ladder 0,1,2,4,8,16,32,64,128"),
            "ladder_geo_max316": census("ladder_geo316.log", "ladder 0,1,3,10,32,100,316"),
            "slab_uv4_max1e5": census("slab_uv4_1e5.log", "slab MAXUV=4, ladder to 1e5"),
            "slab_uv4_max1e9": census("slab_uv4_1e9.log", "slab MAXUV=4, ladder to 1e9"),
        },
        "other_searches": {
            "structural_random_K1e9_seed777002": {
                "log": "b10w2_rand_K1e9.log", "N": 200000000,
                "nonempty": 130035670, "max_vertex_denominator": 1,
                "max_simple_vertex_multiplicity": 1,
                "max_V_over_4vertex_lattice_simplices": "103813825188771821384673875",
                "n_c4_candidates_V_ge_2": 0,
            },
            "structural_random_K1e11_seed777001": {
                "log": "b10w2_rand_K1e11.log", "N": 200000000,
                "status": "REPORTED BUT NOT TRUSTED",
                "why": ("its nonempty rate 0.23% contradicts the scale-invariance of "
                        "non-emptiness (Q(t g) = t Q(g)); the K=1e9 run gives 65%, "
                        "matching wave 1. K = 1e11 is outside the validated integer "
                        "range of band10.exe, so this run is excluded from all "
                        "conclusions."),
            },
            "gapscan_climb_K40_128restarts": {
                "log": "b10w2_climb40.log",
                "negative_hits": 0,
                "best_scale_invariant_6a1_over_1_plus_sum_g": "11/220",
                "note": "scale-invariant descent, probes thin chambers",
            },
            "gapscan_climb_K200_48restarts": {
                "log": "b10w2_climb200.log", "negative_hits": 0,
                "best_scale_invariant_6a1_over_1_plus_sum_g": "11/941",
                "argmin_stratum": "c=4, V=1",
            },
            "near_miss_strata": {
                "logs": ["b10w2_find_6a1_12.log", "b10w2_find_6a1_13.log"],
                "second_lowest_6a1": {"6a1": 12, "c": 5, "V": 3,
                                      "L": [5, 15, 34]},
                "third_lowest_6a1": {"6a1": 13, "c": 5, "V": 2,
                                     "L": [5, 14, 30]},
                "note": "the a_1 = 11/6 minimum is isolated; the next values are "
                        "12/6 = 2 and 13/6, both far from 0",
            },
            "coefficient_sign_check": {
                "file": "b10w2_coeffcheck.py",
                "n_dim3_triples": 800,
                "min_a1": "11/6", "min_a2": "1", "min_a3": "1/6",
                "n_negative": 0,
                "note": "the minima are exactly the coefficients of the standard "
                        "unimodular 3-simplex P = 1 + (11/6)n + n^2 + (1/6)n^3",
            },
            "gapscan_rand_K200_N500000": {
                "log": "b10w2_rand200.log", "dim3_valid": 78037,
                "negative": 0, "min_6a1": 11,
            },
        },
        "verified_records_wave2": {
            "file": "b10w2_records.py / b10w2_records.json",
            "c4_record": {
                "lam": [358, 326, 10, 0], "mu": [120, 110, 10, 0],
                "nu": [394, 391, 75, 74], "weight": 934,
                "c": 4, "V": 1, "hstar": [1, 0, 0, 0],
                "L": [1, 4, 10, 20, 35, 56],
                "P": "1 + (11/6) n + n^2 + (1/6) n^3",
                "engines_agree": ["hive4.py", "lr_hive.exe (A)", "engineB_lrrule.py (B)"],
            },
            "max_volume_record": {
                "lam": [1826334170, 969834481, 491912248, 0],
                "mu": [2046072640, 1427364744, 943146889, 0],
                "nu": [3387789845, 2411830035, 1420900699, 484144593],
                "weight": 7704665172,
                "V_normalized_exact": "103813825188771821384673875",
                "n_vertices": 4, "dim": 3, "max_vertex_denominator": 1,
                "note": ("exact vertices + exact triangulated volume certified by "
                         "hive4.py; the lattice-point count is NOT enumerated at "
                         "this size and no float substitute was used"),
            },
            "unbounded_weight_family": {
                "family": "lam + t*1^4, mu fixed, nu + t*1^4",
                "t": [0, 1000, 10 ** 6, 10 ** 9, 10 ** 12],
                "weights": [934, 4934, 4000934, 4000000934, 4000000000934],
                "c": 4, "V": 1, "P": "1 + (11/6) n + n^2 + (1/6) n^3",
            },
        },
        "hits": [],
        "honesty": ("Wave 2 found NO negative coefficient and no c = 4 polytope with "
                    "V >= 2. min a_1 = 11/6 in every census, attained on the "
                    "unimodular-simplex stratum (c=4, V=1, i=0) -- the r=4 hive "
                    "polytopes never beat the standard 3-simplex. Because a_1 is "
                    "homogeneous of degree 1 in the gap vector, these censuses are "
                    "exhaustive over CONES of gap directions and therefore cover "
                    "unbounded weight along every ray they meet. None of this is "
                    "evidence for the King-Tollu-Toumazet conjecture; it is an "
                    "exhaustive negative census plus a structural obstruction to one "
                    "specific mechanism (Reeve) in one specific cell (r = 4)."),
        "open_gap": ("vertex integrality of r=4 hive polytopes is VERIFIED (max vertex "
                     "denominator = 1 over every scan ever run here) but NOT PROVED; "
                     "the c = 4 => V = 1 theorem is conditional on it. Wave 2 narrows "
                     "the failure locus to tight triples containing an odd rhombus row."),
    }

    man["wave2_hunter10_second_pass"] = w2
    with open(MAN, "w") as f:
        json.dump(man, f, indent=1)
    print(json.dumps(w2["censuses"], indent=1))
    print("wrote", MAN)


if __name__ == "__main__":
    main()
