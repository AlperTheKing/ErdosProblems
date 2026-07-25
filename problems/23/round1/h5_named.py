"""H5: weighted blow-ups of NAMED non-C5-colourable triangle-free base graphs.

Rationale.  If G -> C5 then G is a subgraph of a C5 blow-up, hence bip(G) <= B(N)
(90 / 100 / 210 / 225 at N = 49 / 51 / 74 / 76).  So a counterexample must be
non-C5-colourable.  By Andrasfai-Erdos-Sos / Haggkvist / Chen-Jin-Koh, triangle-free
graphs with large minimum degree are homomorphic to an Andrasfai graph And(k)
(And(2) = C5, And(3) = Wagner C8(1,4), And(4) = C11(1,4), ...).  So the natural next
family is:  blow-ups of And(k), k >= 3, and of the other classical dense
non-C5-colourable triangle-free graphs (Grotzsch, Clebsch, Mycielskians, the
exact N = 12/13/14 record graphs).

For a blow-up the max cut never splits a part, so
      bip(H[w]) = min over the 2^(h-1) unsplit 2-colourings of  sum_{same-side edges} w_a w_b
exactly.  We hill-climb integer w with sum w = N.
"""
import sys
import numpy as np
from itertools import combinations
from h5_core import from_g6, edges_from_adj, is_triangle_free, adj_from_edges


# ------------------------------------------------------------------ base graphs
def circulant(n, S):
    E = set()
    for v in range(n):
        for s in S:
            E.add(tuple(sorted((v, (v + s) % n))))
            E.add(tuple(sorted((v, (v - s) % n))))
    return n, sorted(E)


def andrasfai(k):
    """And(k): circulant on Z_{3k-1} with connection set {i = 1 mod 3, 1<=i<=3k-2}."""
    n = 3 * k - 1
    S = [i for i in range(1, n) if i % 3 == 1]
    return circulant(n, S)


def mycielski(n, E):
    """Mycielskian: vertices 0..n-1 (original), n..2n-1 (shadows), 2n (apex)."""
    E2 = list(E)
    for (u, v) in E:
        E2.append((u, n + v))
        E2.append((v, n + u))
    for u in range(n):
        E2.append((n + u, 2 * n))
    return 2 * n + 1, sorted(set(tuple(sorted(e)) for e in E2))


def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def clebsch():
    """Folded 5-cube: Z_2^4 with connection set e1..e4 and (1,1,1,1). Triangle-free, 5-regular."""
    conn = [1, 2, 4, 8, 15]
    E = set()
    for v in range(16):
        for c in conn:
            E.add(tuple(sorted((v, v ^ c))))
    return 16, sorted(E)


def kneser(n, k):
    sets = list(combinations(range(n), k))
    idx = {s: i for i, s in enumerate(sets)}
    E = []
    for i, a in enumerate(sets):
        for j in range(i + 1, len(sets)):
            if not (set(a) & set(sets[j])):
                E.append((i, j))
    return len(sets), E


def from_g6_edges(s):
    n, adj = from_g6(s)
    return n, edges_from_adj(n, adj)


def petersen():
    return kneser(5, 2)


LIB = {}


def reg(name, n, E):
    adj = adj_from_edges(n, E)
    assert is_triangle_free(n, adj), f"{name} has a triangle"
    LIB[name] = (n, sorted(set(tuple(sorted(e)) for e in E)))


for k in range(2, 8):
    n, E = andrasfai(k)
    reg(f"And({k})", n, E)
for c in (5, 7, 9, 11, 13):
    n, E = cycle(c)
    reg(f"C{c}", n, E)
reg("Petersen", *petersen())
reg("Grotzsch", *mycielski(*cycle(5)))
reg("Myc(C7)", *mycielski(*cycle(7)))
reg("Clebsch", *clebsch())
reg("C13(1,5)", *circulant(13, (1, 5)))
reg("C14(1,4)", *circulant(14, (1, 4)))
reg("C16(1,4,7)", *circulant(16, (1, 4, 7)))
reg("C17(1,4,7)", *circulant(17, (1, 4, 7)))
reg("C19(1,4,7)", *circulant(19, (1, 4, 7)))
reg("rec_N12", *from_g6_edges("K?ABBBwerwBw"))
reg("rec_N13", *from_g6_edges("L??ED@_~?~^_Fw"))
reg("rec_N14", *from_g6_edges("M?AE@bH{AYN_LgBs?"))
reg("rec_N13b", *from_g6_edges("L?`DAboUdIF_Bo"))


# ------------------------------------------------------------- blow-up machinery
class Blow:
    """Exact bip of H[w] for all integer w, vectorised over the 2^(h-1) cuts."""

    def __init__(self, n, E):
        self.n, self.E = n, list(E)
        self.ne = len(self.E)
        assert n <= 22, "too many cuts"
        ncuts = 1 << (n - 1)
        eu = np.array([e[0] for e in self.E], dtype=np.int64)
        ev = np.array([e[1] for e in self.E], dtype=np.int64)
        t = np.arange(ncuts, dtype=np.int64) << 1        # vertex 0 fixed to side 0
        su = (t[:, None] >> eu[None, :]) & 1
        sv = (t[:, None] >> ev[None, :]) & 1
        # float32 is EXACT here: every entry of M is 0/1, every product w_a w_b <= 76^2,
        # and the row sums are < 2^24, well inside the float32 mantissa.
        self.M = np.ascontiguousarray((su == sv).astype(np.float32))
        self.eu, self.ev = eu, ev
        self.ncuts = ncuts

    def bip(self, w):
        w = np.asarray(w, dtype=np.int64)
        prod = (w[self.eu] * w[self.ev]).astype(np.float32)
        return int((self.M @ prod).min())

    def bip_exact(self, w):
        """int64 recomputation, used to re-verify anything we are going to report."""
        w = np.asarray(w, dtype=np.int64)
        prod = w[self.eu] * w[self.ev]
        return int((self.M.astype(np.int64) @ prod).min())

    def total_edges(self, w):
        w = np.asarray(w, dtype=np.int64)
        return int((w[self.eu] * w[self.ev]).sum())

    def optimise(self, N, restarts=40, maxstep=4000, seed=1):
        rng = np.random.default_rng(seed)
        bestv, bestw = -1, None
        for r in range(restarts):
            if r == 0:
                w = np.full(self.n, N // self.n, dtype=np.int64)
                w[: N % self.n] += 1
            else:
                w = np.bincount(rng.integers(0, self.n, size=N), minlength=self.n).astype(np.int64)
            cur = self.bip(w)
            for _ in range(maxstep):
                bv, bij = cur, None
                for i in range(self.n):
                    for j in range(self.n):
                        if i == j or w[j] == 0:
                            continue
                        w[i] += 1; w[j] -= 1
                        v = self.bip(w)
                        w[i] -= 1; w[j] += 1
                        if v > bv:
                            bv, bij = v, (i, j)
                if bij is None:
                    break
                w[bij[0]] += 1; w[bij[1]] -= 1
                cur = bv
            if cur > bestv:
                bestv, bestw = cur, w.copy()
        return bestv, bestw


def main():
    Ns = [int(x) for x in sys.argv[1:]] or [49, 51, 74, 76]
    from h5_c5bound import B
    Bv = {N: B(N)[0] for N in Ns}
    print("base graphs:", len(LIB))
    print(f"{'base':<12}{'h':>3}{'|E|':>5}{'bip(1..1)':>10}", end="")
    for N in Ns:
        print(f"{('N=%d' % N):>12}", end="")
    print()
    print(" " * 30, end="")
    for N in Ns:
        print(f"{('B=%d' % Bv[N]):>12}", end="")
    print()
    rows = []
    for name, (n, E) in LIB.items():
        bl = Blow(n, E)
        base_bip = bl.bip(np.ones(n, dtype=np.int64))
        line = f"{name:<12}{n:>3}{len(E):>5}{base_bip:>10}"
        rec = {"name": name, "h": n, "base_bip": base_bip}
        for N in Ns:
            if N < n:
                line += f"{'-':>12}"
                continue
            R = 25 if n <= 14 else (10 if n <= 17 else 3)
            v, w = bl.optimise(N, restarts=R)
            assert v == bl.bip_exact(w), "float32 evaluation disagreed with int64"
            gain = v - Bv[N]
            line += f"{('%d(%+d)' % (v, gain)):>12}"
            rec[N] = (v, list(map(int, w)))
        print(line, flush=True)
        rows.append(rec)

    print("\nbest per N over the named library:")
    for N in Ns:
        cands = [(r[N][0], r["name"], r[N][1]) for r in rows if N in r]
        cands.sort(reverse=True)
        v, name, w = cands[0]
        print(f"  N={N}: bip={v} (B(N)={Bv[N]}, floor(N^2/25)={N*N//25}) via {name} w={w}")


if __name__ == "__main__":
    main()
