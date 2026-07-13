"""CHECK A — the weighted parity-switch lemma (row-C5 aggregation).

CLAIM (t-uniform, elementary):
  For any circuit fixture, any row tuple omega, and ANY vertex subset S of the
  support graph: badCross(S) <= sum_{e in delta(S)} s_omega(e), where
    badCross(S) = #{atoms {u,v} with exactly one endpoint in S},
    s_omega(e)  = #{atoms whose SELECTED row uses support edge e}.
  Proof shape: the selected row of a crossing atom is a 4-path between the two
  endpoints; a path between vertices separated by S crosses delta(S) an odd
  number (>=1) of times.  (GF(2) telescoping.)

  Stronger per-row form checked here: EVERY row of EVERY crossing atom crosses
  delta(S) an odd number of times; every row of a non-crossing atom an even
  number of times.

Consequence fed to the report: kappa(S) = badCross(S) - |B0 cap delta(S)|
  <= sum_{e in delta(S) cap B0} (s_omega(e) - 1)  -- demand is bounded by the
  selected-multiplicity EXCESS on the crossing edges, a canonical
  CheckedWeightedSwitchCapacity weighting nobody has written down.

Also computes, on hit264's archived decisive switch S = {4,5,6,7,8,11,14,16}:
  badCross, crossing selected-support edges, their s-values, kappa -- to show
  the demand-21 kill is carried by two hub edges of huge multiplicity.

Exact integer arithmetic only.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_hunt\matroid")
import fixtures  # noqa: E402


def crossings(row, mask):
    """number of edges of the 5-vertex row crossing the subset-mask cut"""
    c = 0
    for k in range(4):
        u, v = row[k], row[k + 1]
        if ((mask >> u) & 1) != ((mask >> v) & 1):
            c += 1
    return c


def check_fixture(circ, exhaustive, n_random_masks, n_random_tuples, rng):
    n = circ.n
    atoms = circ.atoms
    # per-row parity check helper
    def per_mask_all_rows(mask):
        for a in atoms:
            sep = ((mask >> a["u"]) & 1) != ((mask >> a["v"]) & 1)
            for row in a["rows"]:
                c = crossings(row, mask)
                if sep:
                    assert c % 2 == 1 and c >= 1, (circ.name, mask, a["u"], a["v"], row)
                else:
                    assert c % 2 == 0, (circ.name, mask, a["u"], a["v"], row)

    def per_mask_tuple(mask, tup):
        """verify badCross <= sum s(e) over crossing edges for tuple tup"""
        bad_cross = 0
        s = {}
        for a, ridx in zip(atoms, tup):
            row = a["rows"][ridx]
            if ((mask >> a["u"]) & 1) != ((mask >> a["v"]) & 1):
                bad_cross += 1
            for k in range(4):
                e = fixtures.norm(row[k], row[k + 1])
                if ((mask >> e[0]) & 1) != ((mask >> e[1]) & 1):
                    s[e] = s.get(e, 0) + 1
        total = sum(s.values())
        assert bad_cross <= total, (circ.name, mask, bad_cross, total)
        return bad_cross, s

    checked_masks = 0
    if exhaustive:
        for mask in range(1 << n):
            per_mask_all_rows(mask)
            checked_masks += 1
    else:
        for _ in range(n_random_masks):
            mask = rng.randrange(1 << n)
            per_mask_all_rows(mask)
            checked_masks += 1

    # tuple-level aggregated check on random tuples + canonical tuple
    rowcounts = [len(a["rows"]) for a in atoms]
    tuples = [tuple(0 for _ in atoms)]
    for _ in range(n_random_tuples):
        tuples.append(tuple(rng.randrange(rc) for rc in rowcounts))
    tuple_masks = [rng.randrange(1 << n) for _ in range(2000)]
    for tup in tuples:
        for mask in tuple_masks:
            per_mask_tuple(mask, tup)

    print(f"[{circ.name}] per-row parity: {checked_masks} masks "
          f"({'EXHAUSTIVE' if exhaustive else 'random'}) PASS; "
          f"aggregated badCross<=sum s(e): {len(tuples)} tuples x "
          f"{len(tuple_masks)} masks PASS")
    return per_mask_tuple


def main():
    rng = random.Random(23)
    fx = fixtures.load_all()

    # nearcand: exhaustive over all 2^18 masks (constructed fixture)
    check_fixture(fx["nearcand"], exhaustive=True, n_random_masks=0,
                  n_random_tuples=60, rng=rng)
    # hits: random masks (per-row parity is a theorem; this is an audit)
    f298 = check_fixture(fx["hit298"], exhaustive=False, n_random_masks=40000,
                         n_random_tuples=60, rng=rng)
    f264 = check_fixture(fx["hit264"], exhaustive=False, n_random_masks=40000,
                         n_random_tuples=60, rng=rng)

    # ---- decisive switch on hit264 (archived: S={4,5,6,7,8,11,14,16}) ----
    circ = fx["hit264"]
    S = {4, 5, 6, 7, 8, 11, 14, 16}
    mask = 0
    for v in S:
        mask |= (1 << v)
    rowcounts = [len(a["rows"]) for a in circ.atoms]
    print(f"[hit264] decisive switch S={sorted(S)}  rowcount vector "
          f"{sorted(set(rowcounts))} (product over atoms of #rows sampled below)")
    # canonical tuple + minimum over a large random tuple sample
    best = None
    worst = None
    stats_canonical = None
    ntup = 20000
    for i in range(ntup + 1):
        if i == 0:
            tup = tuple(0 for _ in circ.atoms)
        else:
            tup = tuple(rng.randrange(rc) for rc in rowcounts)
        bad_cross = 0
        s = {}
        for a, ridx in zip(circ.atoms, tup):
            row = a["rows"][ridx]
            if ((mask >> a["u"]) & 1) != ((mask >> a["v"]) & 1):
                bad_cross += 1
            for k in range(4):
                e = fixtures.norm(row[k], row[k + 1])
                if ((mask >> e[0]) & 1) != ((mask >> e[1]) & 1):
                    s[e] = s.get(e, 0) + 1
        n_cross_edges = len(s)
        total = sum(s.values())
        kappa = bad_cross - n_cross_edges
        rec = (kappa, bad_cross, n_cross_edges, total, dict(s))
        if i == 0:
            stats_canonical = rec
        if best is None or kappa > best[0]:
            best = rec
        if worst is None or kappa < worst[0]:
            worst = rec
        assert bad_cross <= total
    print(f"[hit264] canonical tuple: kappa={stats_canonical[0]} "
          f"badCross={stats_canonical[1]} crossingSelectedEdges={stats_canonical[2]} "
          f"sum_s={stats_canonical[3]} s-map={stats_canonical[4]}")
    print(f"[hit264] over {ntup} random tuples: max kappa={best[0]} "
          f"(badCross={best[1]}, crossing={best[2]}, sum_s={best[3]}, s={best[4]})")
    print(f"[hit264] min kappa={worst[0]} (badCross={worst[1]}, "
          f"crossing={worst[2]}, sum_s={worst[3]})")
    print("CHECK A: ALL ASSERTS GREEN")


if __name__ == "__main__":
    main()
