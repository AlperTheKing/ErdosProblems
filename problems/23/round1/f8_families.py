"""
f8_families.py -- build structured triangle-free candidate graphs and screen them.

For n<=30 exact bip is computed by f8_bip.exe (Gray-code over all 2^(n-1) cuts).
For n>30 we only need an UPPER bound on bip to REJECT a candidate:  any cut C
gives bip <= m - |C|, so a heuristic cut suffices for rejection (rigorously).

Writes  f8_fam_small.g6   (n<=30, exact pipeline)
        f8_fam_big.txt    (n>30, heuristic upper bound on bip)
"""
import itertools, sys, math, random
from f8_core import g6_encode, is_triangle_free, edges_of

random.seed(20260725)


def mk(n, edges):
    adj = [0] * n
    for (i, j) in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return n, adj


def cayley_Z(n, S):
    S = set(x % n for x in S) | set((-x) % n for x in S)
    S.discard(0)
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) % n in S]
    return mk(n, E)


def andrasfai(k):
    n = 3 * k - 1
    S = [1 + 3 * t for t in range(k)]
    return cayley_Z(n, S)


def kneser(nn, kk):
    V = list(itertools.combinations(range(nn), kk))
    idx = {v: i for i, v in enumerate(V)}
    E = [(i, j) for i in range(len(V)) for j in range(i + 1, len(V))
         if not (set(V[i]) & set(V[j]))]
    return mk(len(V), E)


def clebsch():
    # folded 5-cube: Cayley on F_2^4 with S = {e1,e2,e3,e4,e1+e2+e3+e4}
    S = [1, 2, 4, 8, 15]
    E = [(i, j) for i in range(16) for j in range(i + 1, 16) if (i ^ j) in S]
    return mk(16, E)


def cayley_F2(k, S):
    n = 1 << k
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if (i ^ j) in S]
    return mk(n, E)


def circular(n, lo, hi):
    """i ~ j iff (i-j) mod n in (lo, hi) -- the 'continuous C5' when lo=2n/5,hi=3n/5"""
    S = [d for d in range(1, n) if lo < d < hi]
    return cayley_Z(n, S)


def hoffman_singleton():
    # Robertson construction: 5 pentagons P_h, 5 pentagrams Q_i
    # P_h vertex j  ~ P_h vertex j+-1 ; Q_i vertex j ~ Q_i vertex j+-2
    # P_h j ~ Q_i k  iff  k = h*i + j (mod 5)
    idx = {}
    c = 0
    for h in range(5):
        for j in range(5):
            idx[('P', h, j)] = c; c += 1
    for i in range(5):
        for j in range(5):
            idx[('Q', i, j)] = c; c += 1
    E = []
    for h in range(5):
        for j in range(5):
            E.append((idx[('P', h, j)], idx[('P', h, (j + 1) % 5)]))
    for i in range(5):
        for j in range(5):
            E.append((idx[('Q', i, j)], idx[('Q', i, (j + 2) % 5)]))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.append((idx[('P', h, j)], idx[('Q', i, (h * i + j) % 5)]))
    E = sorted(set(tuple(sorted(e)) for e in E))
    return mk(50, E)


def pg24_points_lines():
    # PG(2,4): 1-dim subspaces of F_4^3.  F_4 = {0,1,w,w2} with w^2=w+1.
    add = [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]]
    mul = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]
    vecs = [(a, b, c) for a in range(4) for b in range(4) for c in range(4)]
    vecs.remove((0, 0, 0))
    pts, seen = [], set()
    for v in vecs:
        if v in seen:
            continue
        cls = set()
        for s in range(1, 4):
            cls.add(tuple(mul[s][x] for x in v))
        seen |= cls
        pts.append(min(cls))
    assert len(pts) == 21
    pidx = {p: i for i, p in enumerate(pts)}

    def norm(v):
        for s in range(1, 4):
            w = tuple(mul[s][x] for x in v)
            if w in pidx:
                return pidx[w]
        return None
    lines = set()
    for i in range(21):
        for j in range(i + 1, 21):
            L = set()
            for s in range(4):
                for t in range(4):
                    if s == 0 and t == 0:
                        continue
                    v = tuple(add[mul[s][pts[i][k]]][mul[t][pts[j][k]]] for k in range(3))
                    if v != (0, 0, 0):
                        L.add(norm(v))
            lines.add(frozenset(L))
    lines = sorted(lines, key=sorted)
    assert len(lines) == 21 and all(len(L) == 5 for L in lines), (len(lines), [len(L) for L in lines])
    return pts, lines


def steiner_3_6_22():
    pts, lines = pg24_points_lines()
    P = list(range(21))
    # hyperovals: 6-sets of points, no 3 collinear
    linesets = [set(L) for L in lines]
    hyper = []
    for comb in itertools.combinations(P, 6):
        s = set(comb)
        if all(len(s & L) <= 2 for L in linesets):
            hyper.append(frozenset(s))
    assert len(hyper) == 168, len(hyper)
    # split into 3 classes of 56: same class <=> |H n H'| even
    cls = {}
    for H in hyper:
        placed = False
        for c, rep in cls.items():
            if len(H & rep) % 2 == 0:
                placed = True
                break
        if not placed:
            cls[len(cls)] = H
    groups = {c: [] for c in cls}
    for H in hyper:
        for c, rep in cls.items():
            if len(H & rep) % 2 == 0:
                groups[c].append(H)
                break
    sizes = sorted(len(g) for g in groups.values())
    assert sizes == [56, 56, 56], sizes
    C = groups[0]
    INF = 21
    blocks = [frozenset(set(L) | {INF}) for L in lines] + [frozenset(H) for H in C]
    assert len(blocks) == 77
    # verify Steiner S(3,6,22)
    from collections import Counter
    cnt = Counter()
    for B in blocks:
        for t in itertools.combinations(sorted(B), 3):
            cnt[t] += 1
    assert len(cnt) == 1540 and set(cnt.values()) == {1}, (len(cnt), set(cnt.values()))
    return 22, blocks


def higman_sims():
    npts, blocks = steiner_3_6_22()
    N = 1 + npts + len(blocks)          # 1 + 22 + 77 = 100
    inf = 0
    pt = {p: 1 + p for p in range(npts)}
    bl = {i: 1 + npts + i for i in range(len(blocks))}
    E = []
    for p in range(npts):
        E.append((inf, pt[p]))
    for i, B in enumerate(blocks):
        for p in B:
            E.append((pt[p], bl[i]))
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            if not (blocks[i] & blocks[j]):
                E.append((bl[i], bl[j]))
    E = sorted(set(tuple(sorted(e)) for e in E))
    return mk(N, E)


def grotzsch():
    # Mycielskian of C5
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        for j in [(i + 1) % 5, (i - 1) % 5]:
            E.append((5 + i, j))
        E.append((5 + i, 10))
    return mk(11, sorted(set(tuple(sorted(e)) for e in E)))


def mycielski(n, adj):
    E = edges_of(n, adj)
    E2 = list(E)
    for (i, j) in E:
        E2.append((n + i, j))
        E2.append((n + j, i))
    for i in range(n):
        E2.append((n + i, 2 * n))
    return mk(2 * n + 1, sorted(set(tuple(sorted(e)) for e in E2)))


def tf_process(n, seed):
    rnd = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    adj = [0] * n
    E = []
    for (i, j) in pairs:
        if adj[i] & adj[j]:
            continue
        adj[i] |= 1 << j
        adj[j] |= 1 << i
        E.append((i, j))
    return n, adj


def blowup(n, adj, sizes):
    N = sum(sizes)
    start = [0] * n
    s = 0
    for i in range(n):
        start[i] = s
        s += sizes[i]
    E = []
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                for x in range(sizes[i]):
                    for y in range(sizes[j]):
                        E.append((start[i] + x, start[j] + y))
    return mk(N, E)


# ------------------------------------------------------------------ registry
def catalogue():
    out = []   # (name, n, adj)

    def add(name, g):
        n, adj = g
        assert is_triangle_free(n, adj), f"{name} has a triangle!"
        out.append((name, n, adj))

    for k in range(2, 11):
        add(f"Andrasfai({k})", andrasfai(k))
    add("Petersen=Kneser(5,2)", kneser(5, 2))
    add("Kneser(7,3)", kneser(7, 3))
    add("Kneser(8,3)", kneser(8, 3))
    add("Clebsch", clebsch())
    add("Grotzsch", grotzsch())
    add("Mycielski(C7)", mycielski(*cayley_Z(7, [1])))
    add("HoffmanSingleton", hoffman_singleton())
    add("HigmanSims", higman_sims())
    # circular "continuous C5" graphs
    for n in range(5, 41):
        lo, hi = 2 * n / 5.0, 3 * n / 5.0
        g = circular(n, lo, hi)
        if len(edges_of(*g)) > 0:
            add(f"Circular({n})", g)
    # exhaustive triangle-free circulants with enough density
    for n in range(5, 31):
        half = n // 2
        need_deg = 4.0 * n / 25.0                 # bip<=m/2 forces d > 4n/25
        for r in range(2, half + 1):
            for S in itertools.combinations(range(1, half + 1), r):
                d = sum(1 if (2 * s) % n == 0 else 2 for s in S)
                if d <= need_deg or d > 2 * n / 5.0:
                    continue                      # Andrasfai-Erdos-Sos: delta<=2n/5
                g = cayley_Z(n, S)
                if is_triangle_free(*g):
                    add(f"Circ({n};{'.'.join(map(str,S))})", g)
    # sum-free Cayley graphs on F_2^k
    for k in range(3, 6):
        N = 1 << k
        elems = list(range(1, N))
        best = []
        for _ in range(4000):
            rnd = random.Random(random.randrange(10**9))
            rnd.shuffle(elems)
            S = []
            for x in elems:
                if all((x ^ y) not in S for y in S):
                    S.append(x)
            S = tuple(sorted(S))
            if S not in best:
                best.append(S)
        for S in best[:40]:
            g = cayley_F2(k, set(S))
            if is_triangle_free(*g) and len(edges_of(*g)) > 2 * N * N / 25.0:
                add(f"CayF2({k};{'.'.join(map(str,S))})", g)
    # triangle-free process
    for n in list(range(10, 31)):
        for s in range(12):
            add(f"TFproc({n},{s})", tf_process(n, s))
    # unbalanced C5 blow-ups (sanity: should never beat balanced)
    c5 = cayley_Z(5, [1])
    for sizes in itertools.combinations_with_replacement(range(1, 7), 5):
        if 5 <= sum(sizes) <= 30:
            add(f"C5blow{sizes}", blowup(*c5, list(sizes)))
    return out


if __name__ == '__main__':
    cat = catalogue()
    small = open('f8_fam_small.g6', 'w')
    names = open('f8_fam_names.txt', 'w')
    big = []
    seen = set()
    for name, n, adj in cat:
        if n <= 30:
            s = g6_encode(n, adj)
            if s in seen:
                continue
            seen.add(s)
            small.write(s + "\n")
            names.write(f"{s}\t{name}\n")
        else:
            big.append((name, n, adj))
    small.close(); names.close()
    import pickle
    pickle.dump(big, open('f8_fam_big.pkl', 'wb'))
    print(f"catalogue: {len(cat)} graphs, {len(seen)} distinct with n<=30, {len(big)} with n>30")
    for name, n, adj in big:
        print(f"  BIG: {name} n={n} m={len(edges_of(n,adj))}")
