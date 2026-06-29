"""Family #3 EXTENDED: aggressive randomized chord+ballast search, EXACT max cut only (N<=24).
Goal: a triangle-free graph with a connected-B GLOBAL-MAX cut having a P-contained interior-overlap.
We engineer many random chord sets (nested/crossing) + ballast leaves/detours on build_pd, keep N<=24
so maxcut_all gives the TRUE global max, and check every connected-B global-max cut for interior-overlap.
EXACT integer cut sizes."""
import sys, itertools, random
sys.path.insert(0, "E:/Projects/ErdosProblems/problems/23/writeup")
from _h import dec, maxcut_all, Bconn
from _satzmu_conn import struct_for_side
from _M_tailswitch_gate import build_pd, tri_free

def adj_from_E(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return adj

def cutsize(n, adj, s):
    return sum(1 for u in range(n) for v in adj[u] if v > u and s[u] != s[v])

def overlaps_on_cut(n, adj, s):
    if not Bconn(n, adj, s):
        return None
    st = struct_for_side(n, adj, s)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    out = []
    for f in M:
        if len(cyc[f]) != 1:
            continue
        P_f = cyc[f][0]
        pos = {x: i for i, x in enumerate(P_f)}; Pset = set(P_f)
        chords = []
        for g in M:
            if g == f:
                continue
            for Q in cyc[g]:
                if set(Q) <= Pset:
                    pp = sorted(pos[v] for v in Q)
                    if pp[-1] - pp[0] == len(pp) - 1:
                        chords.append((pp[0], pp[-1])); break
        for i in range(len(chords)):
            for j in range(i + 1, len(chords)):
                a1, b1 = chords[i]; a2, b2 = chords[j]
                if a1 > a2:
                    a1, b1, a2, b2 = a2, b2, a1, b1
                r = min(b1, b2)
                if a2 < r:
                    out.append((f, tuple(P_f), (a1, b1), (a2, b2)))
    return out

def build_pd_ballast(pend, chords, leaves):
    """build_pd then attach pendant leaves to given path vertices (extra ballast that
    can shift the max cut). Returns (n,E). Keeps f=(0,pend) structure."""
    n, E = build_pd(pend, chords)
    cur = n
    Eb = list(E)
    for v in leaves:
        Eb.append((min(v, cur), max(v, cur))); cur += 1
    return cur, Eb

def check_one(name, n, E):
    adj = adj_from_E(n, E)
    if not tri_free(n, adj):
        return ("nontri", None)
    if n > 24:
        return ("toobig", None)
    cuts = maxcut_all(n, adj)
    mx = cutsize(n, adj, cuts[0])
    cb = 0
    for s in cuts:
        ov = overlaps_on_cut(n, adj, s)
        if ov is None:
            continue
        cb += 1
        if ov:
            return ("COUNTEREX", dict(name=name, n=n, maxcut=mx,
                                      side=''.join(map(str, s)), overlaps=ov))
    return ("clean", dict(n=n, maxcut=mx, connB_globalmax=cb))

def run():
    print("=== _wf_mhunt_3b: randomized chord+ballast, EXACT max cut N<=24 ===", flush=True)
    rng = random.Random(12345)
    ntested = 0; ncex = 0; nclean = 0; nnontri = 0
    cex = []
    # systematic overlapping chord pairs/triples on small pend so N stays <=24
    # build_pd(pend) -> N = 2*pend+2, so pend<=11 for N<=24
    for pend in (5, 6, 7, 8, 9, 10, 11):
        # all interior-overlapping chord pairs
        pairs = []
        for a1 in range(0, pend):
            for b1 in range(a1 + 2, pend + 1):
                for a2 in range(a1 + 1, b1):  # a1<a2<b1 -> interior overlap with [a1,b1]
                    for b2 in range(a2 + 2, pend + 1):
                        if (b2 > b1) or (a2 > a1):  # crossing or nested
                            pairs.append([(a1, b1), (a2, b2)])
        # sample to keep runtime bounded
        rng.shuffle(pairs)
        for chords in pairs[:120]:
            n, E = build_pd(pend, chords)
            if n > 24:
                continue
            tag, info = check_one(f"pd{pend}-{chords}", n, E)
            ntested += 1
            if tag == "COUNTEREX":
                ncex += 1; cex.append(info)
                print(f"  *** COUNTEREX *** {info}", flush=True)
            elif tag == "clean":
                nclean += 1
            elif tag == "nontri":
                nnontri += 1
    print(f"  [pairs] tested={ntested} clean={nclean} nontri={nnontri} COUNTEREX={ncex}", flush=True)

    # ballast: overlapping chord pair + random pendant leaves to perturb the max cut
    ntested2 = 0; ncex2 = 0
    for pend in (5, 6, 7, 8, 9):
        baseN = 2 * pend + 2
        room = 24 - baseN
        if room < 1:
            continue
        chordsets = [[(0, 4), (2, 6)], [(0, 4), (1, 5)], [(0, 5), (2, 6)],
                     [(0, 6), (2, 8)], [(0, 4), (2, 8)], [(1, 5), (3, 7)]]
        chordsets = [cs for cs in chordsets if all(b <= pend for _, b in cs)]
        for chords in chordsets:
            for _ in range(200):
                k = rng.randint(1, room)
                leaves = [rng.randint(0, baseN - 1) for _ in range(k)]
                n, E = build_pd_ballast(pend, chords, leaves)
                if n > 24:
                    continue
                tag, info = check_one(f"pd{pend}-{chords}-lv{leaves}", n, E)
                ntested2 += 1
                if tag == "COUNTEREX":
                    ncex2 += 1; cex.append(info)
                    print(f"  *** COUNTEREX (ballast) *** {info}", flush=True)
    print(f"  [ballast] tested={ntested2} COUNTEREX={ncex2}", flush=True)

    print(f"\n  TOTAL COUNTEREXAMPLES (global-max connB interior-overlap, EXACT): {len(cex)}", flush=True)
    return cex

if __name__ == "__main__":
    run()
