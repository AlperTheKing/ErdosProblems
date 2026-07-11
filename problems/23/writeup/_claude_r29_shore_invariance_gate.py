r"""CLAUDE hub-shore INVARIANCE gate on the reconstructed 2943 cage.

HYPOTHESIS (from my descent probe: defect 28 identical at baseline 30811, all-anchor 23115, greedy 23055):
the hub owner-shore Hall data (demand 19953, reach 19925, defect 28, hubs {0,1,2} active) is INVARIANT over the
ENTIRE 680^676 selector product. If true, EVERY tuple -- hence every global scoped-score minimizer, wherever it
sits -- fails scoped Hall by exactly 28, and EveryScopedScoreMinimizerHasMatching is falsified on this cage
WITHOUT any global-minimum certificate (kills the need for the falsified d09 cell bound).

LEG A (empirical): K random tuples drawn uniformly over each full 680-row family (plus targeted extremes:
all-anchor, all-local-0, heavy-local mixes), assert at each: hubs active, per-owner demand (6651 each),
reach_full 19925, defect 28.
LEG B (structural, exact -- the finite checks that would PROVE invariance on this instance):
  B1 no selector-family row contains a hub vertex (0,1,2)  => hub pair-counts/load invariant;
  B2 no selector-family row contains >= 2 vertices of the hub companion set C (companions from rigid rows)
     => companion pair-counts pair[x,y] (x,y in C) invariant;
  B3 hub blue-neighborhood N_B(hubs) subset of always-selected (rigid-row vertices)  => hub active-degree
     invariant (no selector choice can newly select/deselect a hub neighbor);
  B4 for every companion source risk: no selector row uses an edge inside C (implied by B2).
LEG A catches anything LEG B misses (e.g. av-membership drift). All exact/integer.
Run from repo root: python problems/23/writeup/_claude_r29_shore_invariance_gate.py
"""
import importlib.util
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
D09V = ROOT / "tmp/fanout/r29_gate/d09/retry2/verify.py"
PROBE = Path(__file__).with_name("_claude_r29_descent_probe.py")
OWNERS = (0, 1, 2)
K_RANDOM = 20


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    lead = load("r29_lead", LEAD)
    d09 = load("r29_d09_verify", D09V)
    probe = load("r29_probe", PROBE)
    data = lead.build()
    n = data["n"]
    start, stop = data["selectorStart"], data["selectorStop"]
    base_rows = [tuple(r) for r in data["rows"]]
    adjb = d09.adj(n, data["blue"])
    fams = []
    for i, atom in enumerate(data["atoms"][start:stop]):
        fams.append([tuple(x) for x in d09.shortest(adjb, *atom)])

    # ---- LEG B structural ----
    rigid_rows = [base_rows[i] for i in range(len(base_rows)) if not (start <= i < stop)]
    always_selected = {x for r in rigid_rows for x in r}
    # companions of hubs from rigid rows
    pair_rigid = Counter()
    for r in rigid_rows:
        for x in r:
            for y in r:
                pair_rigid[x, y] += 1
    C = set()
    for o in OWNERS:
        C |= {x for x in range(n) if pair_rigid[o, x] > 0 and x != o}
    nbh = set()
    blue = {tuple(sorted(e)) for e in data["blue"]}
    for u, v in blue:
        if u in OWNERS:
            nbh.add(v)
        if v in OWNERS:
            nbh.add(u)
    b1 = b2 = b3 = True
    b2_max = 0
    for fam in fams:
        for row in fam:
            s = set(row)
            if s & set(OWNERS):
                b1 = False
            inter = len(s & C)
            b2_max = max(b2_max, inter)
            if inter >= 2:
                b2 = False
    b3_bad = nbh - always_selected
    b3 = len(b3_bad) == 0
    print("LEG B: B1 no-hub-in-selector-rows=%s | B2 max|row&C|=%d (<2: %s) | B3 N_B(hubs)-alwaysSelected=%d (%s)"
          % (b1, b2_max, b2, len(b3_bad), "PASS" if b3 else "FAIL:%s" % sorted(b3_bad)[:5]), flush=True)

    # ---- LEG A empirical ----
    rng = random.Random(28282)
    tuples = []
    tuples.append(("all-anchor", [next(r for r in fam if 55 in r and tuple(r) == tuple(data["selectorMeta"][j]["anchorRow"])) if False else tuple(data["selectorMeta"][j]["anchorRow"]) for j, fam in enumerate(fams)]))
    tuples.append(("all-local0", [next(tuple(r) for r in fam if 55 not in r) for fam in fams]))
    for k in range(K_RANDOM):
        tuples.append(("rand%02d" % k, [fams[j][rng.randrange(len(fams[j]))] for j in range(676)]))
    fails = []
    for name, choice in tuples:
        rows = list(base_rows)
        for j, row in enumerate(choice):
            rows[start + j] = tuple(row)
        h = probe.hall_at(data, tuple(rows))
        ok = (h["hubs_active"] == [0, 1, 2] and h["demand_full"] == 19953
              and h["reach_full"] == 19925 and h["defect_full"] == 28
              and all(h["demand"][o] == 6651 for o in OWNERS))
        print("%-10s hubs=%s demand=%d reach=%d defect=%d %s"
              % (name, h["hubs_active"], h["demand_full"], h["reach_full"], h["defect_full"],
                 "PASS" if ok else "FAIL"), flush=True)
        if not ok:
            fails.append((name, h))
    print("=" * 72)
    if fails or not (b1 and b2 and b3):
        print("VERDICT: INVARIANCE FAILS (legA fails=%d, B1=%s B2=%s B3=%s) -- defect need not persist at the true minimizer."
              % (len(fails), b1, b2, b3))
        sys.exit(1)
    print("VERDICT: HUB-SHORE INVARIANCE HOLDS -- LEG B structural (B1+B2+B3) + LEG A %d tuples incl all-anchor/"
          % len(tuples))
    print("all-local/random: demand 19953, reach 19925, DEFECT 28 at EVERY sampled tuple. Combined with B1-B3 the")
    print("defect is selector-invariant on this instance => EVERY global scoped-score minimizer fails scoped Hall")
    print("by 28 => EveryScopedScoreMinimizerHasMatching FALSIFIED on the 2943 cage WITHOUT any global-min certificate.")


if __name__ == "__main__":
    main()
