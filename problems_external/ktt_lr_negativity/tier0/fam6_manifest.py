#!/usr/bin/env python3
"""fam6_manifest.py -- assemble runs/fam6/manifest.json from the shard metas,
the final aggregate and the auxiliary measurements."""
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "runs", "fam6")


def sha(path):
    try:
        import hashlib
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()[:16]
    except OSError:
        return None


def main():
    final = json.load(open(os.path.join(RUN, "final_fam.json"),
                           encoding="utf-8"))
    metas = []
    for p in sorted(glob.glob(os.path.join(RUN, "*.meta.json"))):
        metas.append(json.load(open(p, encoding="utf-8")))
    vm = [json.loads(l) for l in
          open(os.path.join(RUN, "carriers_all_vm.out.jsonl"), encoding="utf-8")]
    dens = {}
    for r in vm:
        dens[str(r.get("maxden"))] = dens.get(str(r.get("maxden")), 0) + 1
    carriers = json.load(open(os.path.join(RUN, "carriers_all.json"),
                              encoding="utf-8"))
    xb = json.load(open(os.path.join(RUN, "engineB_crosscheck.json"),
                        encoding="utf-8"))
    man = {
        "family": "fam6 -- MINIMAL-LATTICE-POINT hunt (c = d+1 exactly): "
                  "stage 1 keeps every triple with 1 <= c <= D+1 "
                  "(necessary for h*_1 = 0 since h*_1 = c-(d+1), d <= D); "
                  "stage 2 = the mandated LP-free exact screen on every "
                  "survivor.  No LP dimension oracle, no simplex filter.",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "instrument": "tier0/tier0_screen.py (screen_profile), engine A "
                      "engine/lr_hive.exe, cross-check engine B "
                      "engine/engineB_lrrule.py",
        "drivers": ["tier0/fam6_scan.py", "tier0/fam6_control.py",
                    "tier0/fam6_beam.py", "tier0/fam6_carriers.py",
                    "tier0/fam6_retry.py", "tier0/fam6_final.py",
                    "tier0/fam6_analyze.py", "tier0/fam6_mine_pos.py"],
        "regions_exhaustive": metas,
        "aggregate": {k: final[k] for k in
                      ("distinct_triples", "ok", "status", "deg_hist",
                       "max_hstar_d_all", "max_hstar_d_all_at",
                       "max_hstar_d_d_ge_2", "max_hstar_d_d_ge_2_at",
                       "min_h1_minus_hd_all", "min_h1_minus_hd_all_at",
                       "min_h1_minus_hd_d_ge_2",
                       "min_h1_minus_hd_d_ge_2_at",
                       "h1_minus_hd_hist",
                       "h1_zero_(d,hstar_degree_s)",
                       "h1_zero_(d,Sum_hstar)",
                       "minimal_c_nonunimodular",
                       "hits_counts", "audit_failure_count")},
        "carriers": {
            "definition": "h*_1 = 0 (c = d+1) AND Sum h* >= 2 -- the only "
                          "non-unimodular members of the family",
            "count": len(carriers),
            "hstar_shapes_observed": sorted(set(
                "%s@d=%d" % (json.dumps(z["hstar"]), z["d"])
                for z in carriers)),
            "vertex_denominator_hist": dens,
            "vstatus_all": sorted(set(r.get("vstatus") for r in vm)),
            "non_lattice_count": sum(v for k, v in dens.items()
                                     if k not in ("1", "None")),
            "file": "runs/fam6/carriers_all.json",
        },
        "engineB_crosscheck": {
            "triples": len(xb),
            "all_match": all(z["match"] for z in xb),
            "file": "runs/fam6/engineB_crosscheck.json",
        },
        "hits": final["hits"],
        "verdict": (
            "0 TIER0, 0 JACKPOT, 0 NEGATIVE.  Every family-6 record with "
            "h*_1 = 0 has h*-degree s = max{j : h*_j > 0} in {0, 2}: either "
            "Sum h* = 1 (unimodular simplex, s = 0) or h* = (1,0,1,0,...,0) "
            "(s = 2), and s = 2 occurs only at d >= 4.  h*_d = 0 on every "
            "record with d >= 2, so min(h*_1 - h*_d) = 0 throughout and no "
            "lattice-polytope inequality is violated.  A null census is NOT "
            "evidence for the KTT conjecture."),
    }
    dst = os.path.join(RUN, "manifest.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    print("wrote", dst)
    print(json.dumps({k: man[k] for k in ("carriers", "engineB_crosscheck")},
                     indent=1))


if __name__ == "__main__":
    main()
