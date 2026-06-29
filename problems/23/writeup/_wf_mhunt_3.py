"""ADVERSARIAL hunt for a counterexample to LEMMA (M):
A triangle-free graph with a connected-B GLOBAL MAXIMUM cut that has a
P-contained interior-overlap (two P-contained chords sharing >1 position).

Family #3: path+detour+chord layouts (build_pd) with chord sets engineered to
interior-overlap (nested/crossing) PLUS ballast (extra detours/leaves).

CRITICAL: a counterexample only counts if the cut is a VERIFIED GLOBAL MAXIMUM
cut: cut size == true max via maxcut_all (N<=24), else hillclimb heuristic
(state it's heuristic). Most overlaps live on NON-max (locally max) cuts:
those are NEAR-MISSES, reported but do NOT count.

EXACT integer arithmetic for cut sizes (no floats for pass/fail).
"""
import sys, itertools, random
from collections import deque
sys.path.insert(0, "E:/Projects/ErdosProblems/problems/23/writeup")
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from _M_tailswitch_gate import build_pd, tri_free

def cutsize(n, adj, s):
    return sum(1 for u in range(n) for v in adj[u] if v > u and s[u] != s[v])

def adj_from_E(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return adj

def overlaps_on_cut(n, adj, s):
    """Return list of interior-overlap records on connected-B cut s.
    Each record: (f, P_f, (a1,b1), (a2,b2)). Empty if none / not connected-B."""
    if not Bconn(n, adj, s):
        return None  # not connected-B: not eligible
    st = struct_for_side(n, adj, s)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    out = []
    for f in M:
        if len(cyc[f]) != 1:
            continue  # need unique geodesic for f
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
                        chords.append((pp[0], pp[-1]))
                        break
        for i in range(len(chords)):
            for j in range(i + 1, len(chords)):
                a1, b1 = chords[i]; a2, b2 = chords[j]
                if a1 > a2:
                    a1, b1, a2, b2 = a2, b2, a1, b1
                r = min(b1, b2)
                if a2 < r:  # interior-overlap: share more than one position
                    out.append((f, tuple(P_f), (a1, b1), (a2, b2)))
    return out

def hillclimb_maxcut(n, adj, restarts=400, seed=0):
    """Heuristic max cut: many random restarts + local 1-flip improvement.
    Returns (best_cut_size, list_of_best_sides_found)."""
    rng = random.Random(seed)
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = -1; bestsides = []
    for _ in range(restarts):
        s = [rng.randint(0, 1) for _ in range(n)]
        improved = True
        while improved:
            improved = False
            for u in range(n):
                same = sum(1 for w in adj[u] if s[w] == s[u])
                diff = len(adj[u]) - same
                if same > diff:
                    s[u] ^= 1; improved = True
        c = sum(1 for u, v in edges if s[u] != s[v])
        if c > best:
            best = c; bestsides = [s[:]]
        elif c == best:
            if s not in bestsides and len(bestsides) < 5000:
                bestsides.append(s[:])
    return best, bestsides

def analyze_graph(name, n, E, exact_limit=24, restarts=400):
    """Find true max cut; among GLOBAL-MAX connected-B cuts, check for interior-overlaps.
    Returns dict with verdict."""
    adj = adj_from_E(n, E)
    if not tri_free(n, adj):
        return dict(name=name, n=n, status="not-tri-free")
    rec = dict(name=name, n=n, status="ok", exact=False,
               maxcut=None, n_globalmax=0, n_connB_globalmax=0,
               counterexample=None, near_miss=None,
               ov_on_globalmax_disconnB=0)
    if n <= exact_limit:
        cuts = maxcut_all(n, adj)  # all global-max cuts (exact)
        rec["exact"] = True
        rec["maxcut"] = cutsize(n, adj, cuts[0])
        rec["n_globalmax"] = len(cuts)
        globalmax = cuts
    else:
        best, sides = hillclimb_maxcut(n, adj, restarts=restarts, seed=hash(name) & 0xffff)
        rec["exact"] = False
        rec["maxcut"] = best
        rec["n_globalmax"] = len(sides)
        globalmax = sides
    # check each global-max cut
    for s in globalmax:
        ov = overlaps_on_cut(n, adj, s)
        if ov is None:
            continue  # not connected-B
        rec["n_connB_globalmax"] += 1
        if ov:
            # COUNTEREXAMPLE: global max + connected-B + interior-overlap
            rec["counterexample"] = dict(side=''.join(map(str, s)), overlaps=ov)
            return rec
    return rec

def near_miss_scan(name, n, E, exact_limit=24):
    """Among NON-global-max connected-B cuts: do interior-overlaps exist?
    (these are the well-known near-misses). Report count + an example."""
    adj = adj_from_E(n, E)
    if not tri_free(n, adj):
        return None
    if n > exact_limit:
        return None  # only exact scan for near-miss census
    # enumerate all cuts, group by size
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = -1
    allcuts = []
    for m in range(1 << (n - 1)):
        s = [(m >> u) & 1 for u in range(n)]
        c = sum(1 for u, v in edges if s[u] != s[v])
        allcuts.append((c, s))
        if c > best:
            best = c
    nm_count = 0; example = None
    for c, s in allcuts:
        if c == best:
            continue  # global max handled elsewhere
        ov = overlaps_on_cut(n, adj, s)
        if ov:
            nm_count += 1
            if example is None:
                example = dict(cut=c, maxcut=best, side=''.join(map(str, s)),
                               overlaps=ov[:2])
    return dict(name=name, near_miss_count=nm_count, example=example, maxcut=best)

# ---------------- engineered chord layouts -------------------
def layouts():
    """(name, pend, chords) engineered to interior-overlap on the parity cut.
    build_pd: path 0..pend, detour making f=(0,pend) unique-geodesic bad edge,
    chords engineered nested/crossing along the path."""
    L = []
    # nested pairs
    L += [("nested-8-4", 12, [(0, 8), (2, 6)]),
          ("nested-10-6", 14, [(0, 10), (2, 8)]),
          ("crossing-6-8", 12, [(0, 6), (2, 8)]),
          ("crossing-4-10", 14, [(0, 4), (2, 10)])]  # wait (2,10) interior with (0,4)? share none
    # crossing (overlap): [0,6],[2,8] -> r=6,a2=2 -> interior overlap
    L += [("cross-overlap-a", 12, [(0, 6), (4, 10)]),  # r=6, a2=4<6 overlap
          ("cross-overlap-b", 14, [(0, 8), (4, 12)]),
          ("triple-chain-ov", 14, [(0, 6), (4, 10), (8, 14)]),
          ("nested-triple", 16, [(0, 12), (2, 10), (4, 8)])]
    # short overlap pairs at varying parity
    for pend in (8, 10, 12, 14):
        for (a1, b1) in [(0, 4), (0, 6)]:
            for (a2, b2) in [(2, 6), (2, 8), (4, 8), (4, 10)]:
                if a2 < b2 and b2 <= pend and a1 < a2 < min(b1, b2):
                    L.append((f"ov-p{pend}-{a1}_{b1}-{a2}_{b2}", pend, [(a1, b1), (a2, b2)]))
    return L

def run():
    print("=== _wf_mhunt_3: hunting GLOBAL-MAX interior-overlap counterexample to (M) ===", flush=True)
    found = []
    near = []
    tried = []
    seen = set()
    for name, pend, chords in layouts():
        try:
            n, E = build_pd(pend, chords)
        except Exception as ex:
            print(f"  {name}: build error {ex}", flush=True); continue
        key = (n, tuple(sorted(E)))
        if key in seen:
            continue
        seen.add(key)
        tried.append(name)
        rec = analyze_graph(name, n, E)
        if rec["status"] != "ok":
            print(f"  {name} N={n}: {rec['status']}", flush=True); continue
        nm = near_miss_scan(name, n, E)
        nmc = nm["near_miss_count"] if nm else 0
        tag = "  EXACT" if rec["exact"] else "  HEUR"
        flag = ""
        if rec["counterexample"]:
            flag = "  *** COUNTEREXAMPLE (global-max connB interior-overlap) ***"
            found.append(rec)
        elif nmc:
            flag = f"  near-miss(non-max overlaps={nmc})"
            if nm["example"]:
                near.append(nm)
        print(f"{tag} {name} N={n} maxcut={rec['maxcut']} "
              f"globalmax-cuts={rec['n_globalmax']} connB-globalmax={rec['n_connB_globalmax']}"
              f"{flag}", flush=True)
    print("\n--- summary ---", flush=True)
    print(f"  layouts tried: {len(tried)}", flush=True)
    print(f"  COUNTEREXAMPLES (global-max connB interior-overlap): {len(found)}", flush=True)
    print(f"  near-misses (non-max overlaps): {len(near)}", flush=True)
    if found:
        f0 = found[0]
        print(f"\n  WITNESS: {f0['name']} N={f0['n']} maxcut={f0['maxcut']}", flush=True)
        print(f"    side={f0['counterexample']['side']}", flush=True)
        print(f"    overlaps={f0['counterexample']['overlaps']}", flush=True)
    if near:
        nm = near[0]
        print(f"\n  example near-miss: {nm['name']} maxcut={nm['maxcut']} "
              f"non-max overlap example={nm['example']}", flush=True)
    return found, near

if __name__ == "__main__":
    run()
