"""ADVERSARIAL hunt for a counterexample to lemma (M):
A triangle-free graph with a connected-B GLOBAL MAXIMUM cut that has a
P-contained interior-overlap (for a unique-geodesic bad edge f).

CRITICAL: a hit only counts if the cut is a VERIFIED global maximum cut:
  - cut size == true max via maxcut_all (N<=24), OR
  - heuristic multi-restart hillclimb finds NO strictly larger cut (stated heuristic).

We enumerate gamma-min connected-B max cuts (gmins, which are drawn from maxcut_all
=> already global-max by construction) AND many random/local cuts (NOT necessarily max;
those overlaps are NEAR-MISSES unless we verify max).

Families:
  #0 Iterated Mycielskians: C5 -> Grotzsch(N11) -> Myc(N23) -> Myc(N47)
  also: odd cycles C5,C7,C9,C11; non-uniform odd-cycle blow-ups; glued islands;
  census N<=11 (all connected-B cuts, exact maxcut via maxcut_all).

Exact integer cut sizes only (no floats for pass/fail).
"""
import subprocess, itertools, random
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free


def adj_of(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return adj


def cutsize(n, adj, s):
    return sum(1 for u in range(n) for v in adj[u] if v > u and s[u] != s[v])


def true_maxcut_size(n, adj):
    """EXACT max cut size via maxcut_all (feasible to ~N=26)."""
    cuts = maxcut_all(n, adj)
    s0 = cuts[0]
    return cutsize(n, adj, s0)


def hill_max_size(n, adj, restarts=400, seed=0):
    """Heuristic: best cut size found over many random-restart hillclimbs.
    Returns the best size (a LOWER bound on the true max). If a given cut has
    size < this, it is provably NOT max. If equal, it is max under the heuristic."""
    rng = random.Random(seed)
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = -1
    for _ in range(restarts):
        s = [rng.randint(0, 1) for _ in range(n)]
        improved = True
        while improved:
            improved = False
            for u in range(n):
                # gain of flipping u
                g = 0
                for w in adj[u]:
                    g += 1 if s[u] == s[w] else -1
                if g > 0:
                    s[u] ^= 1; improved = True
        c = cutsize(n, adj, s)
        if c > best:
            best = c
    return best


def find_overlaps_on_cut(n, adj, s):
    """Return list of overlap records for this cut (no max-check).
    Each record: (f, P_f, chord1, chord2). Only unique-geodesic f considered."""
    if not Bconn(n, adj, s):
        return []
    st = struct_for_side(n, adj, s)
    if st is None:
        return []
    M, ell, T, mu, cyc = st
    out = []
    for f in M:
        if len(cyc[f]) != 1:
            continue  # require UNIQUE geodesic for f
        P_f = cyc[f][0]; L = len(P_f)
        pos = {x: i for i, x in enumerate(P_f)}; Pset = set(P_f)
        chords = []
        for g in M:
            if g == f:
                continue
            for Q in cyc[g]:
                if set(Q) <= Pset:
                    pp = sorted(pos[v] for v in Q)
                    if pp[-1] - pp[0] == len(pp) - 1:  # contiguous subpath
                        chords.append((pp[0], pp[-1], g))
                        break
        for i in range(len(chords)):
            for j in range(i + 1, len(chords)):
                a1, b1, g1 = chords[i]; a2, b2, g2 = chords[j]
                if a1 > a2:
                    a1, b1, g1, a2, b2, g2 = a2, b2, g2, a1, b1, g1
                r = min(b1, b2)
                if a2 < r:  # interior-overlap: share more than one position
                    out.append((f, tuple(P_f), (a1, b1), (a2, b2), g1, g2))
    return out


def classify_hit(n, adj, s, exact_max=None, heur_max=None):
    """Return 'GLOBAL-MAX' / 'NON-MAX' / 'HEUR-MAX' for cut s."""
    c = cutsize(n, adj, s)
    if exact_max is not None:
        return 'GLOBAL-MAX' if c == exact_max else 'NON-MAX'
    if heur_max is not None:
        if c < heur_max:
            return 'NON-MAX'
        return 'HEUR-MAX'  # c >= heur_max; heuristic says max (could be wrong if heur underestimated, but c>=heur best)
    return '?'


def scan_graph(name, n, E, exact_limit=24, heur_restarts=400, random_cuts=2000, seed=1,
               report_each=False):
    """Scan one graph. Returns dict with counts and any GLOBAL-MAX / HEUR-MAX hits."""
    if not is_triangle_free(n, E):
        return None
    adj = adj_of(n, E)
    res = dict(name=name, n=n, global_hits=[], heur_hits=[], nearmiss=0, maxcut_cuts_scanned=0)

    exact_max = None
    if n <= exact_limit:
        exact_max = true_maxcut_size(n, adj)
        # enumerate ALL global max cuts exactly
        allcuts = [s for s in maxcut_all(n, adj)]
        # maxcut_all already returns only the best; all have size exact_max
        for s in allcuts:
            res['maxcut_cuts_scanned'] += 1
            ovs = find_overlaps_on_cut(n, adj, s)
            for ov in ovs:
                # this cut IS global max by construction
                res['global_hits'].append((tuple(s), ov))
    else:
        heur_max = hill_max_size(n, adj, restarts=heur_restarts, seed=seed)
        # gmins gives connected-B cuts that are global max among maxcut... but for N>24
        # we cannot run maxcut_all. Use random cuts + hillclimb-found cuts; verify each
        # against heur_max.
        rng = random.Random(seed)
        cand = set()
        # random + hillclimbed cuts
        for _ in range(random_cuts):
            s = [rng.randint(0, 1) for _ in range(n)]
            improved = True
            while improved:
                improved = False
                for u in range(n):
                    g = 0
                    for w in adj[u]:
                        g += 1 if s[u] == s[w] else -1
                    if g > 0:
                        s[u] ^= 1; improved = True
            cand.add(tuple(s))
        for st in cand:
            s = list(st)
            cls = classify_hit(n, adj, s, heur_max=heur_max)
            if cls == 'NON-MAX':
                # any overlap here is a near-miss
                ovs = find_overlaps_on_cut(n, adj, s)
                if ovs:
                    res['nearmiss'] += len(ovs)
                continue
            # HEUR-MAX
            ovs = find_overlaps_on_cut(n, adj, s)
            for ov in ovs:
                res['heur_hits'].append((tuple(s), ov, heur_max, cutsize(n, adj, s)))
    return res


def iterated_mycielskians():
    """C5 -> Grotzsch(N11) -> Myc(N23) -> Myc(N47)."""
    out = []
    cur = (5, Cn(5))
    out.append(("C5", cur[0], cur[1]))
    cur = mycielski(*cur)
    out.append(("Grotzsch_N11", cur[0], cur[1]))
    cur = mycielski(*cur)
    out.append(("Myc2_N23", cur[0], cur[1]))
    cur = mycielski(*cur)
    out.append(("Myc3_N47", cur[0], cur[1]))
    return out


def main():
    print("=== _wf_mhunt_0: adversarial hunt for lemma (M) counterexample ===", flush=True)
    global_witnesses = []
    heur_witnesses = []
    nearmiss_total = 0
    families_tried = []

    # ---------- Family #0: iterated Mycielskians ----------
    families_tried.append("iterated_mycielskians")
    print("\n--- Family #0: iterated Mycielskians ---", flush=True)
    for name, n, E in iterated_mycielskians():
        r = scan_graph(name, n, E, exact_limit=24, heur_restarts=600, random_cuts=4000)
        if r is None:
            print(f"  {name} N={n}: NOT triangle-free?!", flush=True); continue
        gh = len(r['global_hits']); hh = len(r['heur_hits'])
        nearmiss_total += r['nearmiss']
        tag = ""
        if gh:
            tag = " *** GLOBAL-MAX HITS ***"; global_witnesses += [(name, n, E, s, ov) for (s, ov) in r['global_hits']]
        if hh:
            tag += " *** HEUR-MAX HITS ***"; heur_witnesses += [(name, n, E, s, ov, hm, cs) for (s, ov, hm, cs) in r['heur_hits']]
        print(f"  {name} N={n}: exact-maxcuts-scanned={r['maxcut_cuts_scanned']} "
              f"GLOBAL-MAX-overlap={gh} HEUR-MAX-overlap={hh} near-miss(non-max overlaps)={r['nearmiss']}{tag}",
              flush=True)

    # ---------- Family #1: odd cycles ----------
    families_tried.append("odd_cycles")
    print("\n--- Family #1: odd cycles C5..C11 ---", flush=True)
    for k in (5, 7, 9, 11):
        name = f"C{k}"; n, E = k, Cn(k)
        r = scan_graph(name, n, E, exact_limit=24)
        gh = len(r['global_hits']); nearmiss_total += r['nearmiss']
        if gh:
            global_witnesses += [(name, n, E, s, ov) for (s, ov) in r['global_hits']]
        print(f"  {name} N={n}: GLOBAL-MAX-overlap={gh} near-miss={r['nearmiss']}", flush=True)

    # ---------- Family #2: non-uniform odd-cycle blow-ups ----------
    families_tried.append("nonuniform_oddcycle_blowups")
    print("\n--- Family #2: non-uniform odd-cycle blow-ups (N<=24 exact) ---", flush=True)
    def blowg(m, sizes):
        n = sum(sizes); start = [0] * m
        for i in range(1, m):
            start[i] = start[i - 1] + sizes[i - 1]
        E = []
        for i in range(m):
            j = (i + 1) % m
            for a in range(sizes[i]):
                for b in range(sizes[j]):
                    E.append((start[i] + a, start[j] + b))
        return n, E
    # cap total size to keep exact maxcut_all fast (2^(n-1)); N<=18 exact.
    BLOW_CAP = 18
    cfgs = []
    for sizes in itertools.product([1, 2, 3, 4], repeat=5):
        if sum(sizes) > BLOW_CAP or sum(sizes) < 6:
            continue
        cfgs.append((5, sizes))
    for sizes in itertools.product([1, 2, 3], repeat=7):
        if sum(sizes) > BLOW_CAP or sum(sizes) < 8:
            continue
        cfgs.append((7, sizes))
    for sizes in itertools.product([1, 2], repeat=9):
        if sum(sizes) > BLOW_CAP or sum(sizes) < 10:
            continue
        cfgs.append((9, sizes))
    seen_n = 0
    for m, sizes in cfgs:
        n, E = blowg(m, sizes)
        if not is_triangle_free(n, E):
            continue
        r = scan_graph(f"C{m}{sizes}", n, E, exact_limit=BLOW_CAP)
        if r is None:
            continue
        seen_n += 1
        gh = len(r['global_hits']); nearmiss_total += r['nearmiss']
        if gh:
            global_witnesses += [(f"C{m}{sizes}", n, E, s, ov) for (s, ov) in r['global_hits']]
            print(f"  C{m}{sizes} N={n}: *** GLOBAL-MAX-overlap={gh} ***", flush=True)
    print(f"  non-uniform blow-ups scanned (tri-free, N<=24) = {seen_n}", flush=True)

    # ---------- Family #3: glued islands ----------
    families_tried.append("glued_islands")
    print("\n--- Family #3: glued islands (cycle + Mycielski gadget, single bridge) ---", flush=True)
    grot = mycielski(5, Cn(5))  # N11
    mycC7 = mycielski(7, Cn(7))  # N15
    glue_battery = []
    for iN, iE in [(5, Cn(5)), (7, Cn(7)), (9, Cn(9))]:
        for gN, gE in [grot, mycC7, (5, Cn(5)), (7, Cn(7))]:
            for u in (0, 1):
                for v in (0, 1, 2):
                    if v >= gN:
                        continue
                    n, E = union_disjoint((iN, iE), (gN, gE))
                    E = E + [(u, iN + v)]
                    if n > 20 or not is_triangle_free(n, E):
                        continue
                    glue_battery.append((f"isl{iN}+gad{gN}_b({u},{v})", n, E))
    gscan = 0
    for name, n, E in glue_battery:
        r = scan_graph(name, n, E, exact_limit=20)
        if r is None:
            continue
        gscan += 1
        gh = len(r['global_hits']); nearmiss_total += r['nearmiss']
        if gh:
            global_witnesses += [(name, n, E, s, ov) for (s, ov) in r['global_hits']]
            print(f"  {name} N={n}: *** GLOBAL-MAX-overlap={gh} ***", flush=True)
    print(f"  glued islands scanned (tri-free, N<=24) = {gscan}", flush=True)

    # ---------- Family #4: census N<=11 ALL global-max cuts ----------
    families_tried.append("census_N<=11_all_maxcuts")
    print("\n--- Family #4: triangle-free census N=6..11, ALL exact global-max cuts ---", flush=True)
    for nn in range(6, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        ghits = 0; nm = 0; ngraphs = 0
        for g6 in outg:
            n, E = dec(g6)
            r = scan_graph(g6, n, E, exact_limit=24)
            if r is None:
                continue
            ngraphs += 1
            if r['global_hits']:
                ghits += len(r['global_hits'])
                global_witnesses += [(g6, n, E, s, ov) for (s, ov) in r['global_hits']]
                print(f"    {g6} N={n}: *** {len(r['global_hits'])} GLOBAL-MAX overlap(s) ***", flush=True)
            nm += r['nearmiss']
        nearmiss_total += nm
        print(f"  census N={nn}: graphs={ngraphs} GLOBAL-MAX-overlaps={ghits} near-miss(non-max)={nm}", flush=True)

    # ---------- SUMMARY ----------
    print("\n=== SUMMARY ===", flush=True)
    print(f"GLOBAL-MAX overlap witnesses (exact maxcut_all): {len(global_witnesses)}", flush=True)
    print(f"HEUR-MAX overlap witnesses (heuristic, N>24): {len(heur_witnesses)}", flush=True)
    print(f"near-miss overlaps (on NON-max cuts): {nearmiss_total}", flush=True)
    if global_witnesses:
        print("\n!!! LEMMA (M) COUNTEREXAMPLE(S) FOUND (VERIFIED GLOBAL MAX) !!!", flush=True)
        for (name, n, E, s, ov) in global_witnesses[:5]:
            f, P_f, c1, c2, g1, g2 = ov
            print(f"  graph={name} N={n} side={''.join(map(str,s))} f={f} P={P_f} chord1={c1}(g={g1}) chord2={c2}(g={g2})", flush=True)
    else:
        print("NO global-max counterexample found. Lemma (M) holds on all scanned global-max cuts.", flush=True)
    if heur_witnesses:
        print("\n(HEUR-MAX hits — heuristic-verified only, treat with caution):", flush=True)
        for (name, n, E, s, ov, hm, cs) in heur_witnesses[:5]:
            f, P_f, c1, c2, g1, g2 = ov
            print(f"  graph={name} N={n} heurmax={hm} cutsize={cs} side={''.join(map(str,s))} f={f} chords={c1},{c2}", flush=True)
    return global_witnesses, heur_witnesses, nearmiss_total, families_tried


if __name__ == "__main__":
    main()
