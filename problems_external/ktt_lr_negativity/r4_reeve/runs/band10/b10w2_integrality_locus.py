#!/usr/bin/env python3
"""
band10 wave-2: LOCALISING the one open gap (vertex integrality).

The c = 4 ==> V = 1 theorem of this band rests on one unproved hypothesis:
every vertex of an r=4 hive polytope is a lattice point.  This file pins down
exactly where that hypothesis can fail.

In the unimodular coordinates (x,u,v) = (h11, h12-h11, h21-h11) the 15 fixed
rhombus directions split by their x-coefficient s:

    s = +1 :  (1,0,0), (1,1,0), (1,0,1)                     [3 rows]
    s =  0 :  the six A2 directions (+-1,0),(0,+-1),(1,-1),(-1,1)   [6 rows]
    s = -1 :  (-1,0,0), (-1,-1,0), (-1,0,-1)                [3 "even" rows]
              (-1,-1,-1), (-1,1,-1), (-1,-1,1)              [3 "ODD" rows]

The three ODD rows are exactly the images of the three rhombus inequalities
A(1,1), B(1,1), C(1,1):
    R_A :  x + u + v >= |lam| + mu_1 + mu_2
    R_B :  x - u + v >= nu_1 + nu_2
    R_C :  x + u - v >= lam_1 + lam_2

Hypothesis TESTED AND REFUTED here: "every 3-subset with |det| > 1 contains at
least two of {R_A, R_B, R_C}".  FALSE -- 18 of the 49 bad triples contain only
one odd row (histogram of odd-row count among |det|>1 triples: 1 -> 18,
2 -> 30, 3 -> 1).  The refuted claim is kept on the record; the TRUE statement
it collapses to is the weaker one, which the same computation certifies:

    every 3-subset of the 18 rows with |det| > 1 contains AT LEAST ONE of the
    three odd rows R_A, R_B, R_C,

equivalently: the 12 rows whose directions are the A3 ("alcoved / polytrope")
directions are unimodular in triples -- every non-singular triple among them
has |det| = 1 and hence an integral solution for any integer right-hand side.
So a non-integral vertex REQUIRES at least one odd rhombus row to be tight.

Exact integer arithmetic only.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, R4)
import hive4  # noqa: E402


def det3(M):
    (a, b, c), (d, e, f), (g, h, i) = M
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def to_xuv(co):
    """(x,y,z) row -> (x,u,v) row, x = h11, u = h12-h11, v = h21-h11."""
    return (co[0] + co[1] + co[2], co[1], co[2])


def main():
    H = hive4.build_hive4([9, 7, 6, 0], [9, 2, 1, 0], [10, 9, 8, 7])
    rows_xyz = [tuple(r) for r in H["A"]]
    rows = [to_xuv(r) for r in rows_xyz]
    ODD_XYZ = {(1, -1, -1), (-1, 1, -1), (-1, -1, 1)}
    odd_idx = {i for i, r in enumerate(rows_xyz) if r in ODD_XYZ}

    out = {"n_rows": len(rows),
           "rows_xuv": [list(r) for r in rows],
           "odd_row_indices": sorted(odd_idx),
           "s_split": {}}
    for s in (1, 0, -1):
        out["s_split"][str(s)] = sorted(set(r for r in rows if r[0] == s))
    out["s_split"] = {k: [list(t) for t in v] for k, v in out["s_split"].items()}

    nonsing = 0
    bad = []
    for tri in itertools.combinations(range(len(rows)), 3):
        M = [rows[t] for t in tri]
        d = abs(det3(M))
        if d == 0:
            continue
        nonsing += 1
        if d > 1:
            n_odd = len(set(tri) & odd_idx)
            bad.append({"tri": list(tri), "det": d, "n_odd_rows": n_odd,
                        "rows": [list(rows[t]) for t in tri]})
    out["n_nonsingular_triples"] = nonsing
    out["n_triples_det_gt_1"] = len(bad)
    out["det_histogram"] = {}
    for e in bad:
        out["det_histogram"][str(e["det"])] = out["det_histogram"].get(str(e["det"]), 0) + 1
    out["min_odd_rows_among_det_gt_1"] = min(e["n_odd_rows"] for e in bad)
    out["claim_every_det_gt_1_triple_has_>=2_odd_rows"] = \
        all(e["n_odd_rows"] >= 2 for e in bad)
    out["odd_row_count_histogram_among_det_gt_1"] = {}
    for e in bad:
        k = str(e["n_odd_rows"])
        out["odd_row_count_histogram_among_det_gt_1"][k] = \
            out["odd_row_count_histogram_among_det_gt_1"].get(k, 0) + 1

    # and the converse control: how many triples contain >= 2 odd rows at all
    cnt2 = sum(1 for tri in itertools.combinations(range(len(rows)), 3)
               if len(set(tri) & odd_idx) >= 2 and det3([rows[t] for t in tri]) != 0)
    out["n_nonsingular_triples_with_>=2_odd_rows"] = cnt2

    # the A3-only sub-system: is it unimodular in triples?
    a3_rows = [i for i in range(len(rows)) if i not in odd_idx]
    a3_bad = [tri for tri in itertools.combinations(a3_rows, 3)
              if abs(det3([rows[t] for t in tri])) > 1]
    out["A3_only_triples_with_det_gt_1"] = len(a3_bad)

    out["refuted_hypothesis"] = (
        "FALSE: '|det|>1 implies >=2 odd rows'.  18 counterexample triples have "
        "exactly one odd row.")
    out["conclusion"] = (
        "TRUE and certified here: every 3-subset of the 18 rhombus rows with "
        "|det| > 1 contains at least one of the three ODD rows R_A, R_B, R_C "
        "(rhombi A(1,1), B(1,1), C(1,1)); the 12 A3/alcoved rows are unimodular "
        "in triples (%d triples among them with |det|>1).  Hence a non-integral "
        "vertex of an r=4 hive polytope REQUIRES an odd rhombus row to be tight. "
        "This narrows, but does NOT close, the one open hypothesis of the "
        "c = 4 ==> V = 1 theorem." % len(a3_bad))

    with open(os.path.join(HERE, "b10w2_integrality_locus.json"), "w") as f:
        json.dump(out, f, indent=1)
    for k in ("n_rows", "odd_row_indices", "s_split", "n_nonsingular_triples",
              "n_triples_det_gt_1", "det_histogram",
              "min_odd_rows_among_det_gt_1",
              "claim_every_det_gt_1_triple_has_>=2_odd_rows",
              "odd_row_count_histogram_among_det_gt_1",
              "n_nonsingular_triples_with_>=2_odd_rows",
              "A3_only_triples_with_det_gt_1", "refuted_hypothesis"):
        print(k, "=", out[k])
    print()
    print(out["conclusion"])


if __name__ == "__main__":
    main()
