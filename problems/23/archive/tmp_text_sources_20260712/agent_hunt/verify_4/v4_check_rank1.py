"""verify_4 CHECK 1 — adversarial re-verification of corpus_miner2 RANK 1
(weighted parity-switch demand bound) with EXHAUSTIVE sweeps everywhere
(supersedes the report's random-mask audits).

Definitions verified against the archives:
  badCross(S)   = #atoms with exactly one endpoint in S
  s_w(e)        = #atoms whose SELECTED row uses support edge e
  kappa_full(S) = badCross(S) - |delta(S) cap B0|      (R47: all support blue)
  kappa_sel(S)  = badCross(S) - |delta(S) cap Sel_w|   (selected-support form)
Claims:
  (L)  badCross(S) <= sum_{e in delta(S)} s_w(e)            [all S, all tuples]
  (E)  kappa_sel(S) <= sum_{e in delta(S) cap Sel}(s_w(e)-1) [equiv to (L)]
       kappa_full(S) <= same RHS                             [a fortiori]
  engine kills: max_S kappa_full = 20 (#298) / 21 (#264), argmax = engine switch
  #264 archived switch S={4,5,6,7,8,11,14,16}: badCross 23, fixedBlue 2,
       canonical s-map {(2,14):11,(3,11):12}, kappa tuple-invariant = 21
  sum_e s_w(e) = 4*25 = 100; |S_w| >= 3t-1 = 14; max kappa_sel <= 100-|S_w|
  8-vtx rotor: per state max_S kappa_sel = 1 attained with excess exactly 1
       paid by the doubly-selected middle edge (equality case)
Exact integer arithmetic (numpy int64 / python int).
"""

import random
import sys

import numpy as np

sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_hunt\verify_4")
from v4_fixtures import load_all, norm  # noqa: E402

rng = random.Random(20260712)


def bit_cols(n):
    """(2^n, n) uint8 array: column v = bit v of the mask index."""
    masks = np.arange(1 << n, dtype=np.uint32)
    return ((masks[:, None] >> np.arange(n, dtype=np.uint32)[None, :]) & 1
            ).astype(np.uint8)


def analyse(f, tuples_to_try=40):
    n = f.n
    B = bit_cols(n)                      # (2^n, n)
    atoms = f.atoms
    nat = len(atoms)

    # ---- (A) anchoring / path validity of EVERY row (already asserted in
    # loader for hits vs recomputed families; re-assert structurally here)
    for (u, v, rows) in atoms:
        for r in rows:
            assert len(r) == 5 and len(set(r)) == 5
            assert (r[0], r[-1]) in ((u, v), (v, u))
            for k in range(4):
                assert norm(r[k], r[k + 1]) in f.support_set
    print(f"[{f.name}] anchoring: all {sum(len(r) for _,_,r in atoms)} rows "
          f"are simple support 4-paths between their atom endpoints")

    # ---- (B) per-row parity, EXHAUSTIVE over all 2^n masks
    ok_rows = 0
    for (u, v, rows) in atoms:
        sep = (B[:, u] ^ B[:, v]).astype(np.int64)      # (2^n,)
        for r in rows:
            c = np.zeros(len(B), dtype=np.int64)
            for k in range(4):
                c += (B[:, r[k]] ^ B[:, r[k + 1]])
            assert np.all((c & 1) == sep), (f.name, u, v, r)
            assert np.all(c[sep == 1] >= 1)
            ok_rows += 1
    print(f"[{f.name}] per-row parity: EXHAUSTIVE 2^{n} masks x {ok_rows} "
          f"rows: 0 violations")

    # ---- badCross vector (tuple-independent)
    badcross = np.zeros(len(B), dtype=np.int64)
    for (u, v, _) in atoms:
        badcross += (B[:, u] ^ B[:, v])

    # ---- support crossing count (tuple-independent)
    crossblue = np.zeros(len(B), dtype=np.int64)
    for (u, v) in f.support:
        crossblue += (B[:, u] ^ B[:, v])
    kappa_full = badcross - crossblue

    def tuple_stats(tup):
        """selected multiplicities for tuple tup -> dict edge->count"""
        s = {}
        for (u, v, rows), ri in zip(atoms, tup):
            r = rows[ri]
            for k in range(4):
                e = norm(r[k], r[k + 1])
                s[e] = s.get(e, 0) + 1
        return s

    def check_tuple(tup, tag):
        s = tuple_stats(tup)
        assert sum(s.values()) == 4 * nat
        # sum_{e in delta(S)} s(e)  and  |delta cap Sel|  and  excess sums
        sum_s = np.zeros(len(B), dtype=np.int64)
        cnt_sel = np.zeros(len(B), dtype=np.int64)
        excess = np.zeros(len(B), dtype=np.int64)
        for (e, m) in s.items():
            x = (B[:, e[0]] ^ B[:, e[1]]).astype(np.int64)
            sum_s += m * x
            cnt_sel += x
            excess += (m - 1) * x
        # (L) aggregated parity bound
        assert np.all(badcross <= sum_s), (f.name, tag, "L violated")
        # (E) excess bounds, both kappa forms
        kappa_sel = badcross - cnt_sel
        assert np.all(kappa_sel <= excess), (f.name, tag, "E-sel violated")
        assert np.all(kappa_full <= excess), (f.name, tag, "E-full violated")
        return s, kappa_sel, excess

    canonical = tuple(0 for _ in atoms)
    s0, kappa_sel0, excess0 = check_tuple(canonical, "canonical")
    rowcounts = [len(r) for (_, _, r) in atoms]
    for t in range(tuples_to_try):
        tup = tuple(rng.randrange(rc) for rc in rowcounts)
        check_tuple(tup, f"rnd{t}")
    print(f"[{f.name}] aggregated bound (L) + excess bounds (E): EXHAUSTIVE "
          f"2^{n} masks x (canonical + {tuples_to_try} random tuples): "
          f"0 violations")

    # ---- selected support floor + ceiling
    S_w = len(s0)
    mk_sel = int(kappa_sel0.max())
    mk_full = int(kappa_full.max())
    print(f"[{f.name}] canonical tuple: |S_w|={S_w}, sum s=100? "
          f"{sum(s0.values())} ; max kappa_sel={mk_sel}, "
          f"max kappa_full={mk_full}, 4t^2-|S_w|={4*nat - S_w}")
    assert mk_sel <= 4 * nat - S_w
    return B, badcross, crossblue, kappa_full, tuple_stats


def engine_kill_checks(f, B, badcross, crossblue, kappa_full, tuple_stats):
    n = f.n
    mask = 0
    for v in f.switch:
        mask |= 1 << v
    kf = int(kappa_full[mask])
    mx = int(kappa_full.max())
    print(f"[{f.name}] engine switch {f.switch}: kappa_full={kf}; "
          f"exhaustive max kappa_full={mx}; engine sigma={f.sigma}")
    assert kf == mx == -f.sigma, "engine kill NOT reproduced"


def hit264_archived_switch(f, B, badcross, crossblue, tuple_stats):
    S = [4, 5, 6, 7, 8, 11, 14, 16]
    mask = 0
    for v in S:
        mask |= 1 << v
    bc = int(badcross[mask])
    fixedblue = int(crossblue[mask])
    crossing_blue = [e for e in f.support
                     if ((mask >> e[0]) & 1) != ((mask >> e[1]) & 1)]
    s0 = tuple_stats(tuple(0 for _ in f.atoms))
    smap = {e: s0.get(e, 0) for e in crossing_blue}
    print(f"[hit264] archived switch: badCross={bc} fixedBlue={fixedblue} "
          f"crossing blue edges={crossing_blue} canonical s on them={smap}")
    assert bc == 23 and fixedblue == 2
    # tuple-invariance of kappa_sel at this switch, decided EXACTLY:
    # kappa_sel = 23 - #crossing SELECTED edges; = 21 for every tuple iff
    # every tuple selects both crossing blue edges iff for each crossing edge
    # some atom uses it in ALL of its rows.
    always = {}
    for e in crossing_blue:
        found = None
        for (u, v, rows) in f.atoms:
            if all(any(norm(r[k], r[k + 1]) == e for k in range(4))
                   for r in rows):
                found = (u, v, len(rows))
                break
        always[e] = found
    print(f"[hit264] per-crossing-edge 'used by ALL rows of some atom': "
          f"{always}")
    assert all(v is not None for v in always.values()), \
        "tuple-invariance NOT established exactly"
    print("[hit264] => kappa_sel = 23-2 = 21 for EVERY tuple (exact, "
          "not sampled); bound tight iff sum s = 23:",
          sum(smap.values()))


def rotor_checks(f):
    print("=== rotor8 (R39) ===")
    B = bit_cols(8)
    atoms = f.atoms
    badcross = np.zeros(256, dtype=np.int64)
    for (u, v, _) in atoms:
        badcross += (B[:, u] ^ B[:, v])
    inv = {v: k for k, v in f.names.items()}
    for state, tup in f.state_tuples.items():
        s = {}
        for (u, v, rows), ri in zip(atoms, tup):
            r = rows[ri]
            for k in range(4):
                e = norm(r[k], r[k + 1])
                s[e] = s.get(e, 0) + 1
        cnt_sel = np.zeros(256, dtype=np.int64)
        excess = np.zeros(256, dtype=np.int64)
        exc_edges = [e for e, m in s.items() if m >= 2]
        for (e, m) in s.items():
            x = (B[:, e[0]] ^ B[:, e[1]]).astype(np.int64)
            cnt_sel += x
            excess += (m - 1) * x
        kappa_sel = badcross - cnt_sel
        assert np.all(kappa_sel <= excess)
        mx = int(kappa_sel.max())
        argmx = np.nonzero(kappa_sel == mx)[0]
        # equality case audit: at every argmax the excess equals kappa
        eq = np.all(excess[argmx] == mx)
        dbl = [(inv[e[0]], inv[e[1]], m) for e, m in s.items() if m >= 2]
        print(f"  state {state}: |Sel|={len(s)} doubly-selected={dbl} "
              f"max kappa_sel={mx} #argmax={len(argmx)} "
              f"excess==kappa at every argmax: {eq}")
        assert mx == 1 and len(dbl) == 1 and dbl[0][2] == 2
        # the payer: at each argmax exactly one crossing edge has excess,
        # and it is the doubly-selected middle
        e2 = exc_edges[0]
        x2 = (B[:, e2[0]] ^ B[:, e2[1]]).astype(np.int64)
        assert np.all(x2[argmx] == 1), "doubly-selected edge not crossing"
        assert eq
    print("  rotor equality case: max kappa_sel = 1 = excess of the rotating "
          "doubly-selected middle edge, ALL 4 states, exhaustive 2^8")


def main():
    fx = load_all()
    for name in ("nearcand", "hit298", "hit264"):
        f = fx[name]
        B, bc, cb, kf, ts = analyse(f)
        if hasattr(f, "sigma"):
            engine_kill_checks(f, B, bc, cb, kf, ts)
        if name == "hit264":
            hit264_archived_switch(f, B, bc, cb, ts)
        del B
    rotor_checks(fx["rotor8"])
    print("V4 CHECK RANK1: ALL ASSERTS GREEN")


if __name__ == "__main__":
    main()
