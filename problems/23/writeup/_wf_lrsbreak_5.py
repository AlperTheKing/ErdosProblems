"""ADVERSARIAL FAMILY #5: HIGH-RATIO regime |M|/(N^2/25) -> 1, where the +N^2/25-|M| slack
that saves the LRS family vanishes. The extremal C5[t] sits exactly AT ratio 1 with PATH/ROW/LRS
margin = 0 (tight). Question: can a near-C5[t] graph push |M| ABOVE t^2 (ratio>1) on a CP-SAT
GLOBAL-max connected-B cut while keeping load concentrated, breaking a local form?

Strategy:
  (a) C5[t] base, add extra triangle-free bad chords inside parts / across non-adjacent parts to raise |M|.
  (b) C5[t] with one enlarged part (concentrate load AND ratio).
  (c) Petersen / Kneser-like dense triangle-free with |M| near N^2/25.
Each candidate: triangle-free + Bconn + CP-SAT GLOBAL-max (parity or best cut == true max) ->
test B2/PATH-LRS/ROW-LRS/LRS exact. Use the GAMMA-MIN connected-B max cut (the cert's actual cut).

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from ortools.sat.python import cp_model
import subprocess, itertools

from _wf_lrsbreak_1 import adjof, trifree, cutsize, cpmax, test_forms


def gammamin_globalmax(n, E, tlimit=120):
    """Find the GAMMA-MIN connected-B cut among ALL CP-SAT global-max cuts.
    Returns (side, gamma) for the gamma-min global-max connected-B cut with a bad edge, plus the
    CP-SAT proof (opt==bound). Enumerate global-max cuts by brute force (n<=24) restricted to true max."""
    adj = adjof(n, E)
    opt, bound, status = cpmax(n, E, tlimit)
    if opt != bound:
        return None, None, False, opt, bound  # not proven optimal
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = None
    # brute force over all cuts achieving opt
    for m in range(1 << (n - 1)):
        side = [(m >> u) & 1 for u in range(n)]
        c = sum(1 for u, v in edges if side[u] != side[v])
        if c != opt:
            continue
        if not Bconn(n, adj, side):
            continue
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not M:
            continue
        G = 0; ok = True
        for (u, v) in M:
            d = bdist_restr(adj, side, u, v)
            if d < 0:
                ok = False; break
            G += (d + 1) ** 2
        if not ok:
            continue
        if best is None or G < best[1]:
            best = (side, G)
    if best is None:
        return None, None, True, opt, bound
    return best[0], best[1], True, opt, bound


def evaluate(name, n, E, tlimit=120):
    adj = adjof(n, E)
    if not trifree(n, adj):
        return None
    side, gamma, proven, opt, bound = gammamin_globalmax(n, E, tlimit)
    if not proven:
        print(f"[{name}] N={n} CP-SAT NOT proven optimal (opt={opt} bound={bound}); skip")
        return None
    if side is None:
        print(f"[{name}] N={n} no connected-B global-max cut with a bad edge")
        return None
    r = test_forms(n, adj, side)
    if r is None:
        return None
    ratio = F(r['beta']) / F(n * n, 25)
    flags = []
    if r['b2_slack'] < 0: flags.append('B2')
    if r['path_worst'][0] < 0: flags.append('PATH')
    if r['row_worst'][0] < 0: flags.append('ROW')
    if r['lrs_slack'] < 0: flags.append('LRS')
    print(f"[{name}] N={n} GLOBALmax opt={opt} |M|={r['beta']} Gamma={r['Gamma']} "
          f"ratio={float(ratio):.4f} | B2={float(r['b2_slack']):.3f} PATH={float(r['path_worst'][0]):.3f} "
          f"ROW={float(r['row_worst'][0]):.3f} LRS={float(r['lrs_slack']):.3f} "
          f"{'*** BREAK '+','.join(flags)+' ***' if flags else 'all HOLD'}")
    r['name'] = name; r['ratio'] = ratio
    return r


# ---- constructors ----
def C5blow(parts):
    """C5 blow-up with given part sizes (list of 5). returns n,E."""
    off = [0];
    for p in parts: off.append(off[-1] + p)
    n = off[5]; E = []
    for i in range(5):
        j = (i + 1) % 5
        for a in range(parts[i]):
            for b in range(parts[j]):
                E.append((off[i] + a, off[j] + b))
    return n, E


def C5blow_plus_chords(parts, extra):
    n, E = C5blow(parts); E = list(E) + list(extra); return n, E


if __name__ == "__main__":
    print("=== FAMILY #5: HIGH-RATIO |M|->N^2/25 regime ===\n")
    results = []

    # (a) balanced C5[t] baseline (sanity, ratio=1 tight)
    for t in (1, 2, 3, 4):
        n, E = C5blow([t]*5)
        r = evaluate(f"C5[{t}] balanced", n, E, tlimit=60)
        if r: results.append(r)

    # (b) unbalanced C5 blow-ups: concentrate load, push ratio
    print()
    seen = set()
    for parts in itertools.product(range(1, 5), repeat=5):
        if sum(parts) > 18:  # keep CP-SAT/brute feasible (n<=18 -> 2^17)
            continue
        key = min(tuple(parts[i:] + parts[:i]) for i in range(5))  # rotation canon
        key = min(key, min(tuple((parts[::-1])[i:] + (parts[::-1])[:i]) for i in range(5)))
        if key in seen:
            continue
        seen.add(key)
        if len(set(parts)) == 1:
            continue  # balanced already done
        n, E = C5blow(list(parts))
        r = evaluate(f"C5{list(parts)}", n, E, tlimit=45)
        if r: results.append(r)

    # (c) C5[2] + extra triangle-free bad chord(s) to push |M| above t^2
    print()
    # C5[2]: parts of 2, vertices: part i = {2i,2i+1}. Add an edge inside a part-PAIR that
    # stays triangle-free? Within a part there's no edge; across non-adjacent parts (i,i+2) is allowed
    # only if it doesn't create a triangle. Try a few.
    base_parts = [2, 2, 2, 2, 2]
    n0, E0 = C5blow(base_parts)
    adj0 = adjof(n0, E0)
    # candidate extra edges across non-adjacent parts (distance-2 in C5) -- these are NON-bad normally;
    # to make them BAD (monochromatic) we rely on the gamma-min cut; just add and let CP-SAT decide.
    cand = []
    for u in range(n0):
        for v in range(u + 1, n0):
            if v in adj0[u]:
                continue
            if adj0[u] & adj0[v]:
                continue  # triangle
            cand.append((u, v))
    # add single extra edges
    for e in cand[:30]:
        n, E = C5blow_plus_chords(base_parts, [e])
        r = evaluate(f"C5[2]+chord{e}", n, E, tlimit=45)
        if r: results.append(r)

    # SUMMARY
    print("\n=== SUMMARY (gamma-min CP-SAT-global-max cuts) ===")
    print(f"qualifying candidates: {len(results)}")
    mins = {'B2': None, 'PATH-LRS': None, 'ROW-LRS': None, 'LRS': None}
    brk = {'B2': [], 'PATH-LRS': [], 'ROW-LRS': [], 'LRS': []}
    best_ratio = None
    for r in results:
        sl = {'B2': r['b2_slack'], 'PATH-LRS': r['path_worst'][0],
              'ROW-LRS': r['row_worst'][0], 'LRS': r['lrs_slack']}
        if best_ratio is None or r['ratio'] > best_ratio[0]:
            best_ratio = (r['ratio'], r['name'])
        for k, v in sl.items():
            if mins[k] is None or v < mins[k][0]:
                mins[k] = (v, r['name'])
            if v < 0:
                brk[k].append((r['name'], float(v)))
    for k in ['B2', 'PATH-LRS', 'ROW-LRS', 'LRS']:
        ms = mins[k]
        print(f"  {k}: min slack = {float(ms[0]) if ms else 'na'} at {ms[1] if ms else ''}  breaks={brk[k]}")
    print(f"  max ratio |M|/(N^2/25) = {float(best_ratio[0]):.4f} at {best_ratio[1]}")
