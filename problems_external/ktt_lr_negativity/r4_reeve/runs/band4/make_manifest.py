#!/usr/bin/env python3
"""Build manifest.json for the r=4 exhaustive weight band W in [27,32] (hunter 4/12)."""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.abspath(os.path.join(HERE, "..", ".."))
ENG = os.path.abspath(os.path.join(R4, "..", "engine"))
SCAN = os.path.join(HERE, "band4_W27_32.txt")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


txt = open(SCAN).read()
per_W = []
for m in re.finditer(r"^W=(\d+) (.*)$", txt, re.M):
    kv = dict(t.split("=", 1) for t in m.group(2).split())
    per_W.append({"W": int(m.group(1)),
                  **{k: int(v) for k, v in kv.items()}})
tot = {}
for k in ("triples", "nonempty", "empty"):
    tot[k] = int(re.search(r"\b%s=(\d+)" % k, txt.split("TOTALS")[1]).group(1))
dh = re.search(r"dim histogram: 0=(\d+) 1=(\d+) 2=(\d+) 3=(\d+)", txt)
hist = {}
for m in re.finditer(r"^  6a1=(\d+) : (\d+)$", txt, re.M):
    hist[int(m.group(1))] = int(m.group(2))

man = {
    "hunter": "r=4 census hunter 4 of 12 (Reeve-dimension sweep)",
    "date_utc": subprocess.run([sys.executable, "-c",
                                "import datetime;print(datetime.datetime.utcnow().isoformat()+'Z')"],
                               capture_output=True, text=True).stdout.strip(),
    "target": "King-Tollu-Toumazet (2004) positivity conjecture: a stretched LR polynomial "
              "P(n)=c(n nu; n lam, n mu) with a strictly negative coefficient",
    "cell": "r = 4  (hive polytope ambient dimension (r-1)(r-2)/2 = 3, the Reeve dimension)",
    "band": "W = |nu| = |lam|+|mu| in [27, 32]",
    "exhaustive": True,
    "scope": ("EVERY ordered triple (lam, mu, nu) of partitions with at most 4 parts and "
              "|lam|+|mu|=|nu|=W, for each W in 27..32.  No symmetry reduction, no sampling, "
              "no pruning.  Triples with l(lam)>4 or l(mu)>4 are excluded because c(nu;lam,mu)=0 "
              "unless lam,mu subset nu and l(nu)<=4, so P == 0 there and no coefficient can be "
              "negative; triples with l(nu)>4 are outside the r=4 cell by definition."),
    "triples_tested": tot["triples"],
    "nonempty_polytopes": tot["nonempty"],
    "empty_polytopes": tot["empty"],
    "dim_histogram": {"0": int(dh.group(1)), "1": int(dh.group(2)),
                      "2": int(dh.group(3)), "3": int(dh.group(4))},
    "per_W": per_W,
    "min_a1_over_nonconstant_P": "1",
    "min_a1_over_dim3": "11/6",
    "note_min_a1": ("a_1 is the ONLY coefficient that can be negative for a 3-dim lattice "
                    "polytope (a_0 = 1, a_3 = vol > 0, a_2 = half the sum of the relative "
                    "facet volumes > 0).  Constant P (dim 0, c = 1) has no linear term; "
                    "empty polytopes give P == 0.  The reported minimum is over all triples "
                    "with dim >= 1; restricted to the only live stratum dim = 3 the minimum "
                    "is 11/6, exactly the unimodular-3-simplex value, attained and never beaten."),
    "max_normalized_volume": 43,
    "max_normalized_volume_at_hstar1_zero": 1,
    "dim3_with_hstar1_zero": hist.get(11, 0),
    "dim3_6a1_histogram": {str(k): v for k, v in sorted(hist.items())},
    "hits_negative_coefficient": [],
    "structural_finding": ("Every one of the %d dim-3 triples in the band with h*_1 = 0 "
                           "(c = dim+1 = 4 lattice points) has normalized volume 1, i.e. is a "
                           "UNIMODULAR 3-simplex (h* = (1,0,0,0), 6a1 = 11).  No empty lattice "
                           "3-simplex T(p,q) with q >= 2 -- and a fortiori no Reeve tetrahedron "
                           "T_q with q >= 13 -- occurs as an r=4 hive polytope of weight 27..32."
                           % hist.get(11, 0)),
    "honesty": ("This is an exhaustive NEGATIVE census of the stated band.  It closes the band "
                "and nothing else.  Absence of a counterexample proves nothing about the KTT "
                "conjecture and is NOT evidence for it."),
    "arithmetic": "exact integers throughout (C++ long long / Python int+Fraction); no floating point",
    "validation": {
        "aggregate_gate": ("band4.exe re-derived independently by hive4.py over the FULL triple "
                           "sets of W = 4..12 (52,068 triples): triples, nonempty, dim histogram, "
                           "min 6a1, min 6a1 (dim3), max V, max V at h*_1=0, negative count -- "
                           "all MATCH, 9/9 weights (see _val_agg.log); W=10..12 re-run MATCH"),
        "dim3_cross_engine": ("random dim-3 triples of weight 32: band4 vs hive4 vs engine A "
                              "(n=1,2,3) vs engine B (n=1,2), plus hive4 held-out interpolation "
                              "check at n=4,5 and the volume cross-route -- 0 failures "
                              "(_val_dim3_W32.log)"),
        "extremal_records_cross_engine": ("max-V record (V=43), min-a1 dim-3 record and three "
                                          "high-volume dim-3 triples (V=25,26) each confirmed by "
                                          "engine A and engine B at n=1,2 (A also at n=3)"),
        "triple_counts": "per-W triple counts re-derived independently from partition counts in Python",
    },
    "artifacts": {},
}
for p in [os.path.join(R4, "band4.cpp"), os.path.join(R4, "band4.exe"),
          os.path.join(R4, "band4b.exe"), os.path.join(R4, "band4c.exe"),
          os.path.join(R4, "validate_band4.py"), os.path.join(R4, "validate_band4_dim3.py"),
          os.path.join(R4, "hive4.py"), os.path.join(ENG, "lr_hive.exe"),
          os.path.join(ENG, "engineB_lrrule.py"), SCAN]:
    if os.path.exists(p):
        man["artifacts"][os.path.relpath(p, R4).replace("\\", "/")] = sha(p)

with open(os.path.join(HERE, "manifest.json"), "w") as f:
    json.dump(man, f, indent=1)
print(json.dumps({k: man[k] for k in ("band", "triples_tested", "dim_histogram",
                                      "min_a1_over_nonconstant_P", "min_a1_over_dim3",
                                      "max_normalized_volume",
                                      "max_normalized_volume_at_hstar1_zero",
                                      "hits_negative_coefficient")}, indent=1))
