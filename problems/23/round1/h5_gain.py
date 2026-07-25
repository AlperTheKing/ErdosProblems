"""H5 decisive experiment: does the non-C5 'gain' grow with N?

For each non-C5-colourable base H we compute, for every N in a range,
        g_H(N) = max_{w >= 0, sum w = N} bip(H[w])  -  B(N)
where B(N) is the C5-blow-up ceiling.  g > 0 means H[w] beats every C5-colourable
graph on N vertices.  A counterexample to Erdos #23 at N = 49 needs
        max_H g_H(49) >= 97 - 90 = 7        (and >= 1 just to beat the blow-up).

Seeding is careful: besides uniform/random starts we explicitly seed every induced
5-cycle of H with the B(N)-optimal C5 weights, so the search can never report less
than B(N) for a base that contains an induced C5.
"""
import sys
import numpy as np
from itertools import combinations
from h5_named import LIB, Blow

_Bcache = {}


def Bopt(N):
    """B(N) and an argmax (w1..w5) for the C5 ceiling."""
    if N in _Bcache:
        return _Bcache[N]
    best, arg = -1, (0, 0, 0, 0, 0)
    for a in range(N + 1):
        for b in range(N - a + 1):
            ab = a * b
            if ab <= best and a * 0 == 0 and ab < best:
                pass
            for c in range(N - a - b + 1):
                for d in range(N - a - b - c + 1):
                    e = N - a - b - c - d
                    v = min(ab, b * c, c * d, d * e, e * a)
                    if v > best:
                        best, arg = v, (a, b, c, d, e)
    _Bcache[N] = (best, arg)
    return best, arg


def induced_c5s(n, E):
    """All induced 5-cycles of H, each as an ordered 5-tuple around the cycle."""
    adj = [[False] * n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = True
    out, seen = [], set()
    for S in combinations(range(n), 5):
        sub = [[adj[a][b] for b in S] for a in S]
        deg = [sum(r) for r in sub]
        if deg != [2, 2, 2, 2, 2]:
            continue          # induced C5 must be exactly 2-regular on 5 vertices
        # order it around the cycle
        order = [0]
        prev = -1
        cur = 0
        for _ in range(4):
            nxt = [k for k in range(5) if sub[cur][k] and k != prev][0]
            order.append(nxt)
            prev, cur = cur, nxt
        key = tuple(sorted(S))
        if key in seen:
            continue
        seen.add(key)
        out.append(tuple(S[k] for k in order))
    return out


def optimise(bl, N, c5s, restarts=30, seed=7, maxstep=3000):
    rng = np.random.default_rng(seed)
    Bv, Barg = Bopt(N)
    starts = []
    w = np.full(bl.n, N // bl.n, dtype=np.int64)
    w[: N % bl.n] += 1
    starts.append(w)
    for cyc in c5s[:40]:
        w = np.zeros(bl.n, dtype=np.int64)
        for k in range(5):
            w[cyc[k]] = Barg[k]
        starts.append(w)
    for _ in range(restarts):
        starts.append(np.bincount(rng.integers(0, bl.n, size=N),
                                  minlength=bl.n).astype(np.int64))
    bestv, bestw = -1, None
    for w in starts:
        w = w.copy()
        cur = bl.bip(w)
        for _ in range(maxstep):
            bv, bij = cur, None
            for i in range(bl.n):
                for j in range(bl.n):
                    if i == j or w[j] == 0:
                        continue
                    w[i] += 1; w[j] -= 1
                    v = bl.bip(w)
                    w[i] -= 1; w[j] += 1
                    if v > bv:
                        bv, bij = v, (i, j)
            if bij is None:
                break
            w[bij[0]] += 1; w[bij[1]] -= 1
            cur = bv
        if cur > bestv:
            bestv, bestw = cur, w.copy()
    return bestv, bestw, Bv


def main():
    bases = sys.argv[1].split(",") if len(sys.argv) > 1 else \
        ["Grotzsch", "rec_N12", "rec_N14", "Petersen", "And(3)", "And(4)", "Clebsch"]
    Nlo = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    Nhi = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    for name in bases:
        n, E = LIB[name]
        bl = Blow(n, E)
        c5s = induced_c5s(n, E)
        print(f"\n### {name}: h={n} |E|={len(E)} induced-C5s={len(c5s)}", flush=True)
        print(f"{'N':>4}{'B(N)':>7}{'best':>7}{'gain':>6}{'floor(N^2/25)':>15}{'ratio':>10}   w")
        for N in range(max(Nlo, 5), Nhi + 1):
            v, w, Bv = optimise(bl, N, c5s)
            assert v == bl.bip_exact(w)
            flag = "  <== BEATS C5 CEILING" if v > Bv else ""
            viol = "  *** VIOLATION ***" if 25 * v > N * N else ""
            print(f"{N:>4}{Bv:>7}{v:>7}{v-Bv:>+6}{N*N//25:>15}{v/(N*N):>10.6f}   "
                  f"{list(map(int,w))}{flag}{viol}", flush=True)


if __name__ == "__main__":
    main()
