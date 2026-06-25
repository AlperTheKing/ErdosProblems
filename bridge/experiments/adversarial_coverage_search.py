#!/usr/bin/env python3
"""
ADVERSARIAL 4-BRANCH COVERAGE SEARCH.

Goal: stress the Q11 claim that the two CHEAP rooted certificates (edge-root and C5-root F_C)
cover every generic band triangle-free graph. We hill-climb / anneal over triangle-free graphs
at band density to MAXIMIZE the "cheap gap"
        g_cheap(G) = min( edge_root_bound(G), F_C(G) ) - RHS(G),     RHS=(N^2/5 - e)/2.
g_cheap > 0  <=>  BOTH cheap certificates fail (bound exceeds RHS) -> would need Petersen/Clebsch
or a NEW 5th template. We report any maximiser and whether it is a Petersen/Clebsch-type blow-up.

Simultaneously we track the DIRECT CF gap
        g_CF(G) = tau_K_ub(G) - RHS(G).
tau_K_ub is an UPPER bound on the true tau_K, so g_CF(G) > 0 is only a CANDIDATE CF counterexample
(the true tau_K could still be <= RHS); we SAVE any such graph immediately for exact follow-up.

Moves: add/delete one edge keeping the graph triangle-free and the edge count inside the band
window [x_lo,x_hi]*N^2. Local search with random restarts. Pure single-thread Python, N<=20 — far
under the 64-thread / 192 GB cap.

NO fabrication: this is a search for COUNTEREXAMPLES / coverage gaps, not a proof of coverage.
"""
import itertools, random, sys

random.seed(2023)

labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
Kadj = [set() for _ in range(16)]
for i in range(16):
    for j in range(16):
        if i != j and bin(labels[i] ^ labels[j]).count('1') == 4:
            Kadj[i].add(j)

def cost(x, y):
    return (4 - bin(x ^ y).count('1')) // 2

def tau_K_ub(N, A, restarts=25, sweeps=30):
    nbr = [list(A[v]) for v in range(N)]
    best = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(N)]
        imp, sw = True, 0
        while imp and sw < sweeps:
            imp = False; sw += 1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc:
                        bc, bl = c, L
                if bl != lab[u]:
                    lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w > u)
        if best is None or tot < best:
            best = tot
    return best

def edge_root_bound(N, A, E):
    deg = [len(A[v]) for v in range(N)]
    S = [sum(deg[z] for z in A[v]) for v in range(N)]
    e = len(E)
    if not E:
        return e
    return e - max(S[u] + S[v] for u, v in E) / 2.0

def label_R(j):      return 31 ^ (1 << j)
def label_S(i, eps): return (1 << i) | (1 << ((i + eps) % 5))
def label_D(i):      return (1 << ((i - 1) % 5)) | (1 << ((i + 1) % 5))

def FC_of_cycle(N, A, E, C):
    typ = [None] * N
    for v in range(N):
        P = sorted(i for i in range(5) if C[i] in A[v])
        if len(P) == 0:    typ[v] = ('R',)
        elif len(P) == 1:  typ[v] = ('S', P[0])
        elif len(P) == 2:
            a, b = P
            if   (b - a) % 5 == 2: typ[v] = ('D', (a + 1) % 5)
            elif (a - b) % 5 == 2: typ[v] = ('D', (b + 1) % 5)
            else:                  typ[v] = ('X',)
        else:              typ[v] = ('X',)
    best = None
    for eps in (2, 3):
        for j in range(5):
            lab = [0] * N
            for v in range(N):
                t = typ[v]
                if   t[0] == 'R': lab[v] = label_R(j)
                elif t[0] == 'S': lab[v] = label_S(t[1], eps)
                elif t[0] == 'D': lab[v] = label_D(t[1])
                else:             lab[v] = label_R(j)
            tot = sum(cost(lab[u], lab[w]) for (u, w) in E)
            if best is None or tot < best:
                best = tot
    return best

def min_FC(N, A, E):
    best = None
    for combo in itertools.combinations(range(N), 5):
        sub = [(a, b) for a, b in itertools.combinations(combo, 2) if b in A[a]]
        if len(sub) != 5:
            continue
        d = {v: 0 for v in combo}
        for a, b in sub:
            d[a] += 1; d[b] += 1
        if any(d[v] != 2 for v in combo):
            continue
        start = combo[0]; cyc = [start]; prev = None; cur = start; ok = True
        for _ in range(4):
            cand = [w for w in A[cur] if w in d and w != prev]
            if not cand:
                ok = False; break
            cyc.append(cand[0]); prev, cur = cur, cand[0]
        if not ok:
            continue
        fc = FC_of_cycle(N, A, E, tuple(cyc))
        if best is None or fc < best:
            best = fc
    return best  # None if no induced C5

def edges_of(A, N):
    return [(u, v) for u in range(N) for v in A[u] if v > u]

def tri_free_add_ok(A, u, v):
    return not (A[u] & A[v])

def evaluate(N, A):
    E = edges_of(A, N)
    e = len(E)
    rhs = (N*N/5.0 - e) / 2.0
    er = edge_root_bound(N, A, E)
    fc = min_FC(N, A, E)
    cheap = er if fc is None else min(er, fc)   # if no C5, only edge-root available
    g_cheap = cheap - rhs
    return E, e, rhs, er, fc, g_cheap

def is_blowup_of(N, A, base_adj, bsize):
    """Heuristic: is G a blow-up of the bsize-vertex graph with adjacency base_adj?
    Checks N % bsize == 0 and a canonical partition into equal twin-classes matching base_adj."""
    if bsize == 0 or N % bsize != 0:
        return False
    t = N // bsize
    part = [list(range(i*t, (i+1)*t)) for i in range(bsize)]
    pos = {}
    for pi, blk in enumerate(part):
        for v in blk:
            pos[v] = pi
    for u in range(N):
        for v in range(N):
            if u == v:
                continue
            want = pos[v] in base_adj[pos[u]]
            have = v in A[u]
            if want != have:
                return False
    return True

# Petersen / Clebsch base adjacencies for blow-up detection
two = list(itertools.combinations(range(5), 2))
Padj = [set(j for j in range(10) if i != j and not (set(two[i]) & set(two[j]))) for i in range(10)]
Cadj = [set(Kadj[i]) for i in range(16)]

def classify_blowup(N, A):
    # try detecting a relabeled blow-up is hard; we only flag exact canonical blow-ups,
    # plus report graph as "structured" if it is regular with few distinct neighborhoods.
    tags = []
    if is_blowup_of(N, A, Padj, 10): tags.append("Petersen-blowup(canonical)")
    if is_blowup_of(N, A, Cadj, 16): tags.append("Clebsch-blowup(canonical)")
    # twin-class count (vertices grouped by identical neighborhood) — small => blow-up-like
    sig = {}
    for v in range(N):
        key = frozenset(A[v] - {v})
        sig.setdefault(frozenset(A[v]), []).append(v)
    ntwin = len({frozenset(A[v]) for v in range(N)})
    tags.append(f"distinct-nbhds={ntwin}")
    return tags

def search(N, x_lo, x_hi, restarts=12, iters=400):
    elo, ehi = int(x_lo*N*N) + 1, int(x_hi*N*N)
    best = None  # (g_cheap, A_snapshot, info)
    cf_candidates = []
    for r in range(restarts):
        # random triangle-free start in band
        A = [set() for _ in range(N)]
        pairs = [(u, v) for u in range(N) for v in range(u+1, N)]
        random.shuffle(pairs)
        e = 0; tgt = random.randint(elo, ehi)
        for u, v in pairs:
            if e >= tgt: break
            if tri_free_add_ok(A, u, v):
                A[u].add(v); A[v].add(u); e += 1
        _, e, rhs, er, fc, g = evaluate(N, A)
        cur = g
        for it in range(iters):
            # propose a move: flip one edge (add if absent & tri-free & e<ehi; del if present & e>elo)
            u = random.randrange(N); v = random.randrange(N)
            if u == v: continue
            present = v in A[u]
            if present:
                if e <= elo: continue
                A[u].discard(v); A[v].discard(u)
            else:
                if e >= ehi or not tri_free_add_ok(A, u, v): continue
                A[u].add(v); A[v].add(u)
            _, e2, rhs2, er2, fc2, g2 = evaluate(N, A)
            # accept if improves cheap gap (greedy + small random walk)
            if g2 >= cur or random.random() < 0.05:
                cur = g2; e = e2
            else:
                # revert
                if present:
                    A[u].add(v); A[v].add(u)
                else:
                    A[u].discard(v); A[v].discard(u)
        # final eval of this restart
        Efin, efin, rhsfin, erfin, fcfin, gfin = evaluate(N, A)
        tk = tau_K_ub(N, A)
        gcf = tk - rhsfin
        if gcf > 1e-9:
            cf_candidates.append((gcf, [sorted(A[v]) for v in range(N)], efin, rhsfin, tk))
        info = dict(N=N, e=efin, rhs=rhsfin, er=erfin, fc=fcfin, g_cheap=gfin, tk=tk, gcf=gcf,
                    tags=classify_blowup(N, A))
        if best is None or gfin > best[0]:
            best = (gfin, [sorted(A[v]) for v in range(N)], info)
    return best, cf_candidates

def main():
    print("=== ADVERSARIAL 4-BRANCH COVERAGE SEARCH ===")
    print("Maximise g_cheap = min(edge_root, F_C) - RHS.  g_cheap>0 => BOTH cheap certs fail.")
    print("Track g_CF = tau_K_ub - RHS;  >0 => CANDIDATE CF counterexample (save).\n")
    overall_best = None
    all_cf = []
    for N in (10, 12, 15, 18, 20):
        best, cfc = search(N, 0.1243, 0.16, restarts=10, iters=300)
        g, adj, info = best
        flag = "  <-- BOTH CHEAP FAIL" if g > 1e-9 else ""
        print(f"N={N:2d}: best g_cheap={g:7.2f} (e={info['e']}, RHS={info['rhs']:.1f}, "
              f"edge={info['er']:.1f}, F_C={info['fc']}, tauK_ub={info['tk']}, gCF={info['gcf']:.1f}){flag}")
        print(f"        tags: {info['tags']}")
        if overall_best is None or g > overall_best[0]:
            overall_best = best + (N,)
        all_cf.extend((N,) + c for c in cfc)
    print("\n=== RESULT ===")
    g, adj, info, Nb = overall_best
    if g > 1e-9:
        print(f"FOUND a band graph defeating BOTH cheap certs: N={Nb} g_cheap={g:.2f}, tags={info['tags']}")
        print(f"  -> if NOT Petersen/Clebsch structure, a 5th root template is indicated. Adjacency:")
        print(f"  {adj}")
    else:
        print(f"NO band graph found where both cheap certificates fail (max g_cheap={g:.2f} <= 0).")
        print("  => across the adversarial search, edge-root OR C5-root F_C always covered the graph.")
        print("     Stronger support that the cheap templates suffice on generic band graphs.")
    if all_cf:
        print(f"\n!!! {len(all_cf)} CANDIDATE CF graphs (tau_K_ub > RHS) — SAVED below for EXACT follow-up:")
        for c in all_cf[:5]:
            N0, gcf, adjc, e0, rhs0, tk0 = c
            print(f"  N={N0} e={e0} RHS={rhs0:.1f} tauK_ub={tk0} gCF={gcf:.1f}  adj={adjc}")
        print("  (tau_K_ub is an UPPER bound; exact tau_K may still be <= RHS. NOT yet a counterexample.)")
    else:
        print("\nNo candidate CF counterexample: tau_K_ub <= RHS on every graph visited at search endpoints.")
    print("DONE")

if __name__ == "__main__":
    main()
