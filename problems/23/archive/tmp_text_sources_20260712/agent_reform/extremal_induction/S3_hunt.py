"""S3: counterexample hunt for the Pentagon Alignment Lemma L*:
    L*: every triangle-free G with an induced C5 has SOME induced C5 P with
        beta(G) - beta(G-P) <= (2N-5)/5.
Exact arithmetic throughout. For each graph: beta(G) brute-force; enumerate induced C5s;
early-exit when some P meets budget; else record violation with full margins.
Families: Petersen, Grotzsch, Mycielski(C7), Andrasfai(k), GP(n,2), perturbed C5-blowups,
random maximal triangle-free, circulant scan, generalized Mycielski M3(C7) (odd girth 7 -> C7 test too).
"""
import numpy as np, itertools, random, sys
from fractions import Fraction
sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_reform\extremal_induction")
from S1_sanity import beta, is_triangle_free, induced_subgraph, petersen, c5_blowup, ck_blowup

random.seed(23)

def adj_sets(n, edges):
    a = [set() for _ in range(n)]
    for i, j in edges:
        a[i].add(j); a[j].add(i)
    return a

def is_bipartite(n, edges):
    a = adj_sets(n, edges)
    col = [-1] * n
    for s in range(n):
        if col[s] >= 0: continue
        col[s] = 0; st = [s]
        while st:
            u = st.pop()
            for v in a[u]:
                if col[v] < 0:
                    col[v] = 1 - col[u]; st.append(v)
                elif col[v] == col[u]:
                    return False
    return True

def induced_c5s(n, edges):
    """All 5-subsets inducing a C5."""
    a = adj_sets(n, edges)
    out = []
    for S in itertools.combinations(range(n), 5):
        deg = []
        cnt = 0
        for u in S:
            d = len(a[u] & set(S))
            deg.append(d); cnt += d
        if cnt != 10 or any(d != 2 for d in deg):
            continue
        # 5 vertices all degree 2 and 5 edges: either C5 or C3+C2(impossible: C2 not simple) -> C5 or C3+P2? C3+P2 has degs (2,2,2,1,1). So C5.
        out.append(S)
    return out

def induced_odd_cycles(n, edges, k):
    """All k-subsets inducing C_k (for C7 test)."""
    a = adj_sets(n, edges)
    out = []
    for S in itertools.combinations(range(n), k):
        Sset = set(S)
        degs = [len(a[u] & Sset) for u in S]
        if sum(degs) != 2 * k or any(d != 2 for d in degs):
            continue
        # all degree 2, k edges: disjoint cycles; C_k iff connected
        seen = {S[0]}; st = [S[0]]
        while st:
            u = st.pop()
            for v in a[u] & Sset:
                if v not in seen:
                    seen.add(v); st.append(v)
        if len(seen) == k:
            out.append(S)
    return out

def test_lemma(name, n, edges, cyc_len=5, verbose=True, list_all=False):
    """Return (verdict, data). verdict True = some induced C_cyc meets budget."""
    assert is_triangle_free(n, edges), name
    budget = Fraction(2 * cyc_len * n - cyc_len * cyc_len, 25)
    if cyc_len == 5:
        budget = Fraction(2 * n - 5, 5)
    cycles = induced_c5s(n, edges) if cyc_len == 5 else induced_odd_cycles(n, edges, cyc_len)
    if not cycles:
        if verbose: print(f"{name}: N={n} e={len(edges)} -- NO induced C{cyc_len}; skip")
        return None, None
    bG = beta(n, edges)
    best_inc = None; incs = []
    for P in cycles:
        keep = [v for v in range(n) if v not in set(P)]
        n2, E2 = induced_subgraph(n, edges, keep)
        bH = beta(n2, E2)
        inc = bG - bH
        incs.append(inc)
        if best_inc is None or inc < best_inc:
            best_inc = inc
        if not list_all and Fraction(inc) <= budget:
            if verbose:
                print(f"{name}: N={n} e={len(edges)} beta={bG} #C{cyc_len}={len(cycles)} "
                      f"minInc<= {inc} budget={budget} PASS")
            return True, dict(bG=bG, inc=inc, budget=budget, ncyc=len(cycles))
    ok = Fraction(best_inc) <= budget
    if verbose:
        print(f"{name}: N={n} e={len(edges)} beta={bG} #C{cyc_len}={len(cycles)} "
              f"minInc={best_inc} maxInc={max(incs)} budget={budget} {'PASS' if ok else '*** VIOLATION ***'}")
    return ok, dict(bG=bG, inc=best_inc, budget=budget, ncyc=len(cycles), incs=incs)

# ---------- constructions ----------
def mycielski(n, edges):
    """M(G): vertices 0..n-1 (orig), n..2n-1 (shadow), 2n (apex)."""
    E = list(edges)
    for (i, j) in edges:
        E.append((i, n + j)); E.append((j, n + i))
    for i in range(n):
        E.append((n + i, 2 * n))
    return 2 * n + 1, E

def gen_mycielski(n_cyc, levels):
    """Generalized Mycielski M_levels(C_{n_cyc}); odd girth = min(n_cyc, 2*levels+1)... levels>=1.
    V=(i,j) i in Z_n, j=0..levels-1, plus apex. (i,0)~(i+-1,0); (i,j)~(i+-1,j-1); apex~(i,levels-1)."""
    def vid(i, j): return j * n_cyc + (i % n_cyc)
    N = n_cyc * levels + 1
    apex = N - 1
    E = set()
    for i in range(n_cyc):
        E.add(tuple(sorted((vid(i, 0), vid(i + 1, 0)))))
    for j in range(1, levels):
        for i in range(n_cyc):
            E.add(tuple(sorted((vid(i, j), vid(i + 1, j - 1)))))
            E.add(tuple(sorted((vid(i, j), vid(i - 1, j - 1)))))
    for i in range(n_cyc):
        E.add(tuple(sorted((vid(i, levels - 1), apex))))
    return N, sorted(E)

def andrasfai(k):
    """And(k): circulant on 3k-1 vertices, connections {k..2k-1}."""
    n = 3 * k - 1
    E = set()
    for i in range(n):
        for s in range(k, 2 * k):
            E.add(tuple(sorted((i, (i + s) % n))))
    return n, sorted(E)

def gp(n, k):
    """Generalized Petersen GP(n,k): outer 0..n-1, inner n..2n-1."""
    E = []
    for i in range(n):
        E.append((i, (i + 1) % n))
        E.append((n + i, n + (i + k) % n))
        E.append((i, n + i))
    E = sorted(set(tuple(sorted(e)) for e in E))
    return 2 * n, E

def circulant(n, S):
    E = set()
    for i in range(n):
        for s in S:
            E.add(tuple(sorted((i, (i + s) % n))))
    return n, sorted(E)

def random_maximal_tf(n, seed):
    rnd = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    a = [set() for _ in range(n)]
    E = []
    for (i, j) in pairs:
        if not (a[i] & a[j]):
            a[i].add(j); a[j].add(i); E.append((i, j))
    return n, E

def main():
    violations = []
    results = []

    print("== structured families, pentagon lemma ==")
    n, E = petersen()
    results.append(("Petersen", test_lemma("Petersen", n, E, list_all=True)))

    n, E = mycielski(5, [(i, (i + 1) % 5) for i in range(5)])
    results.append(("Grotzsch=M(C5)", test_lemma("Grotzsch=M(C5)", n, E, list_all=True)))

    n, E = mycielski(7, [(i, (i + 1) % 7) for i in range(7)])
    results.append(("M(C7)", test_lemma("M(C7)", n, E)))

    for k in range(2, 8):
        n, E = andrasfai(k)
        results.append((f"Andrasfai({k})", test_lemma(f"Andrasfai({k}) N={n}", n, E)))

    for m in (7, 9, 11):
        n, E = gp(m, 2)
        results.append((f"GP({m},2)", test_lemma(f"GP({m},2)", n, E)))

    print("== perturbed blowups ==")
    for t, dels in [(3, 3), (3, 6), (4, 5), (4, 12)]:
        n, E = c5_blowup([t] * 5)
        rnd = random.Random(100 + t * 17 + dels)
        E2 = list(E)
        rnd.shuffle(E2)
        E2 = sorted(E2[dels:])
        results.append((f"C5[{t}]-{dels}e", test_lemma(f"C5[{t}] minus {dels} random edges", n, E2)))
    for sizes in [(5, 4, 4, 4, 3), (6, 2, 5, 3, 4), (2, 6, 2, 6, 2), (7, 3, 4, 3, 3)]:
        n, E = c5_blowup(list(sizes))
        results.append((f"C5{sizes}", test_lemma(f"C5{sizes} N={n}", n, E)))

    print("== random maximal triangle-free ==")
    for i in range(40):
        n = random.choice([14, 16, 18, 20])
        gn, gE = random_maximal_tf(n, 1000 + i)
        if is_bipartite(gn, gE):
            continue
        v, d = test_lemma(f"rmtf#{i} N={n}", gn, gE, verbose=False)
        if v is None:
            continue
        results.append((f"rmtf#{i}", (v, d)))
        if not v:
            print(f"*** rmtf#{i} N={n} VIOLATION: {d}")
            violations.append((f"rmtf#{i}", gn, gE, d))
    print(f"random maximal TF: tested {sum(1 for r in results if r[0].startswith('rmtf'))} non-bipartite w/ C5, "
          f"violations={sum(1 for v in violations if v[0].startswith('rmtf'))}")

    print("== circulant scan n=10..22, |S|<=3 ==")
    ncirc = 0
    for n in range(10, 23):
        for S in itertools.chain(itertools.combinations(range(1, n // 2 + 1), 2),
                                 itertools.combinations(range(1, n // 2 + 1), 3)):
            gn, gE = circulant(n, S)
            if not is_triangle_free(gn, gE) or is_bipartite(gn, gE):
                continue
            v, d = test_lemma(f"C{n}{S}", gn, gE, verbose=False)
            if v is None:
                continue
            ncirc += 1
            if not v:
                print(f"*** circulant C{n}{S} VIOLATION: {d}")
                violations.append((f"C{n}{S}", gn, gE, d))
    print(f"circulants tested (non-bip, has C5): {ncirc}, violations={sum(1 for v in violations if v[0].startswith('C'))}")

    print("== odd girth 7: C7-deletion lemma, budget (14N-49)/25 ==")
    n, E = gen_mycielski(7, 3)  # odd girth 7, N=22
    results.append(("M3(C7)", test_lemma("M3(C7) N=22", n, E, cyc_len=7)))
    for t in (2, 3):
        n, E = ck_blowup(7, [t] * 7)
        results.append((f"C7[{t}]", test_lemma(f"C7[{t}] N={n}", n, E, cyc_len=7)))

    print("=== SUMMARY ===")
    nv = len(violations)
    print(f"total violations of L*: {nv}")
    if nv:
        for name, gn, gE, d in violations:
            print(" VIOL:", name, d)
    return violations

if __name__ == "__main__":
    main()
