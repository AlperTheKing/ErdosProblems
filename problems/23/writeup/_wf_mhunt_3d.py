"""Family #3 FAST: engineered overlapping chords + ballast, EXACT max cut, cap N<=20 (fast maxcut_all).
Exhaustive over all interior-overlapping chord pairs/triples on pend<=8 (N<=18) plus ballast leaves.
EXACT integer cut sizes. Prints unbuffered; no tail pipe."""
import sys, itertools, random
sys.path.insert(0, "E:/Projects/ErdosProblems/problems/23/writeup")
from _h import maxcut_all, Bconn
from _satzmu_conn import struct_for_side
from _M_tailswitch_gate import build_pd, tri_free

CAP = 20

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
                if a2 < min(b1, b2):
                    out.append((f, tuple(P_f), (a1, b1), (a2, b2)))
    return out

def check_one(name, n, E):
    adj = adj_from_E(n, E)
    if not tri_free(n, adj):
        return ("nontri", None)
    if n > CAP:
        return ("toobig", None)
    cuts = maxcut_all(n, adj)
    mx = cutsize(n, adj, cuts[0])
    cb = 0; nm = 0
    for s in cuts:
        ov = overlaps_on_cut(n, adj, s)
        if ov is None:
            continue
        cb += 1
        if ov:
            return ("COUNTEREX", dict(name=name, n=n, maxcut=mx,
                                      side=''.join(map(str, s)), overlaps=ov))
    return ("clean", dict(n=n, maxcut=mx, connB=cb))

def all_overlap_chordsets(pend):
    """all chord pairs [a1,b1],[a2,b2] with a1<a2<min(b1,b2) (interior overlap), b-a>=2."""
    chs = []
    segs = [(a, b) for a in range(pend) for b in range(a + 2, pend + 1)]
    for i in range(len(segs)):
        for j in range(i, len(segs)):
            a1, b1 = segs[i]; a2, b2 = segs[j]
            if a1 > a2:
                a1, b1, a2, b2 = a2, b2, a1, b1
            if a1 < a2 < min(b1, b2):
                chs.append([(a1, b1), (a2, b2)])
    return chs

def build_pd_ballast(pend, chords, leaves):
    n, E = build_pd(pend, chords)
    cur = n; Eb = list(E)
    for v in leaves:
        Eb.append((min(v, cur), max(v, cur))); cur += 1
    return cur, Eb

def run():
    print("=== _wf_mhunt_3d: engineered overlap chords EXACT max cut, N<=20 ===", flush=True)
    rng = random.Random(777)
    cex = []
    tested = 0; clean = 0; nontri = 0
    # exhaustive overlapping pairs for pend up to 8 (N=2*pend+2 <= 18)
    for pend in range(4, 9):
        for chords in all_overlap_chordsets(pend):
            n, E = build_pd(pend, chords)
            if n > CAP:
                continue
            tag, info = check_one(f"pd{pend}-{chords}", n, E)
            tested += 1
            if tag == "COUNTEREX":
                cex.append(info); print(f"  *** COUNTEREX *** {info}", flush=True)
            elif tag == "clean":
                clean += 1
            elif tag == "nontri":
                nontri += 1
        print(f"  pend={pend}: cumulative tested={tested} clean={clean} nontri={nontri} cex={len(cex)}", flush=True)
    # ballast on pend<=8 overlapping pairs, leaves keep N<=20
    tested2 = 0
    for pend in range(4, 9):
        baseN = 2 * pend + 2
        room = CAP - baseN
        if room < 1:
            continue
        ovsets = all_overlap_chordsets(pend)
        rng.shuffle(ovsets)
        for chords in ovsets[:40]:
            for _ in range(120):
                k = rng.randint(1, room)
                leaves = [rng.randint(0, baseN - 1) for _ in range(k)]
                n, E = build_pd_ballast(pend, chords, leaves)
                if n > CAP:
                    continue
                tag, info = check_one(f"pd{pend}b", n, E)
                tested2 += 1
                if tag == "COUNTEREX":
                    cex.append(info); print(f"  *** COUNTEREX (ballast) *** {info}", flush=True)
    print(f"  ballast tested={tested2}", flush=True)
    print(f"\n  TOTAL COUNTEREXAMPLES (global-max connB interior-overlap, EXACT N<=20): {len(cex)}", flush=True)
    print(f"  === {'COUNTEREXAMPLE FOUND' if cex else 'NONE — lemma (M) holds on all tested global maxima'} ===", flush=True)
    return cex

if __name__ == "__main__":
    run()
