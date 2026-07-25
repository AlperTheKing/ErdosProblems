"""G12 task (c)/(d): explicit COVERING mechanisms (odd-cycle edge transversals)
and their exact tight/breaking witnesses.

Mechanisms (all give an explicit edge set meeting every odd cycle):

 M1  neighbourhood cut          bip(G) <= e(G - N(v))            (N(v) independent)
 M2  best independent-set cut   bip(G) <= min_{I independent} e(G - I)
                                       = |E| - max_{I ind} sum_{v in I} d(v)
 M3  BFS-layer parity cut       bip(G) <= # edges inside a BFS layer
 M4  averaged M1 (Cauchy-Schwarz)  bip(G) <= |E| - (1/N) sum_v d(v)^2 <= |E| - 4|E|^2/N^2
 M5  Mantel applied to M1       bip(G) <= (N - Delta)^2 / 4

All arithmetic here is integer / Fraction.
"""
from fractions import Fraction as F
import itertools
import networkx as nx
import G12_core as C


# ------------------------------------------------------------------ graphs
def nx_to_pair(G):
    vs = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(vs)}
    E = sorted(tuple(sorted((idx[u], idx[v]))) for u, v in G.edges())
    return len(vs), E


def clebsch():
    """Folded 5-cube: V = F_2^4, u~v iff u+v in {e1,e2,e3,e4,1111}. 16 vtx, 5-regular."""
    S = [1, 2, 4, 8, 15]
    E = set()
    for u in range(16):
        for s in S:
            v = u ^ s
            E.add(tuple(sorted((u, v))))
    return 16, sorted(E)


def grotzsch():
    G = nx.mycielski_graph(4)          # Mycielskian of C5 = Grotzsch, 11 vertices
    return nx_to_pair(G)


def andrasfai(k):
    """And(k): vertices Z_{3k-1}, i~j iff i-j = 1 mod 3 ; And(2)=C5, And(3)=Moebius-Kantor? """
    n = 3 * k - 1
    E = set()
    for i in range(n):
        for j in range(n):
            if i < j and (j - i) % 3 == 1:
                E.add((i, j))
    return n, sorted(E)


def hoffman_singleton():
    G = nx.hoffman_singleton_graph()
    return nx_to_pair(G)


def kneser(n, k):
    V = list(itertools.combinations(range(n), k))
    idx = {v: i for i, v in enumerate(V)}
    E = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if not set(V[i]) & set(V[j]):
                E.append((i, j))
    return len(V), E


# ------------------------------------------------------------------ mechanisms
def degrees(n, E):
    d = [0] * n
    for u, v in E:
        d[u] += 1
        d[v] += 1
    return d


def adjsets(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


def e_minus(n, E, S):
    """# edges of G with both ends outside S."""
    return sum(1 for u, v in E if u not in S and v not in S)


def M1(n, E):
    A = adjsets(n, E)
    return min(e_minus(n, E, A[v]) for v in range(n))


def M2(n, E, cap=1 << 17):
    """Exact min over independent sets I of e(G-I) = |E| - max_I sum_{v in I} d(v).
    Brute force over subsets for n <= 22, else greedy/local upper estimate."""
    d = degrees(n, E)
    A = adjsets(n, E)
    m = len(E)
    if (1 << n) <= cap:
        best = 0
        for S in range(1 << n):
            ok = True
            tot = 0
            bits = S
            vs = []
            while bits:
                b = bits & -bits
                v = b.bit_length() - 1
                vs.append(v)
                bits ^= b
            for i, v in enumerate(vs):
                if A[v] & set(vs[:i]):
                    ok = False
                    break
                tot += d[v]
            if ok and tot > best:
                best = tot
        return m - best, best
    # fallback: maximum-weight independent set by simple branch and bound
    order = sorted(range(n), key=lambda v: -d[v])
    best = [0]

    def rec(avail, cur):
        if not avail:
            best[0] = max(best[0], cur)
            return
        bound = cur + sum(d[v] for v in avail)
        if bound <= best[0]:
            return
        v = max(avail, key=lambda x: d[x])
        rec(avail - A[v] - {v}, cur + d[v])       # take v
        rec(avail - {v}, cur)                      # skip v
    rec(set(range(n)), 0)
    return m - best[0], best[0]


def M3(n, E):
    A = adjsets(n, E)
    best = None
    for s in range(n):
        lay = {s: 0}
        frontier = [s]
        while frontier:
            nf = []
            for u in frontier:
                for w in A[u]:
                    if w not in lay:
                        lay[w] = lay[u] + 1
                        nf.append(w)
            frontier = nf
        if len(lay) < n:
            continue                      # disconnected: skip
        mono = sum(1 for u, v in E if lay[u] == lay[v])
        best = mono if best is None else min(best, mono)
    return best


def M4(n, E):
    d = degrees(n, E)
    return F(len(E)) - F(sum(x * x for x in d), n)


def M5(n, E):
    d = degrees(n, E)
    return F((n - max(d)) ** 2, 4)


def row(name, n, E, bip=None, do_bip=True):
    assert C.is_triangle_free(n, E), name
    m = len(E)
    d = degrees(n, E)
    tgt = F(n * n, 25)
    m1 = M1(n, E)
    m2, wt = M2(n, E)
    m3 = M3(n, E)
    m4 = M4(n, E)
    m5 = M5(n, E)
    b = C.bip_bruteforce_fast(n, E) if (do_bip and n <= 22) else bip
    print(f"{name}: N={n} |E|={m} Delta={max(d)} delta={min(d)}   N^2/25 = {tgt} = {float(tgt):.4f}")
    print(f"    bip = {b}"
          f"    M1 min_v e(G-N(v)) = {m1} {'OK' if m1<=tgt else 'BREAKS'}"
          f"    M2 min_I e(G-I) = {m2} {'OK' if m2<=tgt else 'BREAKS'}")
    print(f"    M3 BFS-layer = {m3} {'OK' if m3 is not None and m3<=tgt else 'BREAKS'}"
          f"    M4 |E|-sum d^2/N = {m4} = {float(m4):.4f} {'OK' if m4<=tgt else 'BREAKS'}"
          f"    M5 (N-Delta)^2/4 = {m5} {'OK' if m5<=tgt else 'BREAKS'}")
    if b is not None:
        print(f"    ratios vs bip: M1 {F(m1,b) if b else '-'}  M2 {F(m2,b) if b else '-'}"
              f"  M3 {F(m3,b) if b else '-'}")
    print(f"    M2/N^2 = {F(m2, n*n)} = {float(F(m2,n*n)):.6f}   (mechanism-2 ceiling)")
    return dict(name=name, n=n, m=m, bip=b, M1=m1, M2=m2, M3=m3, M4=m4, M5=m5)


def main():
    print("=" * 78)
    print("(c) covering mechanisms, exact values.  'BREAKS' = exceeds N^2/25.")
    print("=" * 78)
    rows = []
    for t in range(1, 5):
        N, E = C.blowup(5, C.C5()[1], [t] * 5)
        rows.append(row(f"C5[{t}]", N, E, bip=t * t, do_bip=(N <= 20)))
    rows.append(row("Petersen", *nx_to_pair(nx.petersen_graph())))
    rows.append(row("Clebsch(folded 5-cube)", *clebsch()))
    rows.append(row("Grotzsch", *grotzsch()))
    for k in (2, 3, 4, 5, 6):
        rows.append(row(f"Andrasfai({k})", *andrasfai(k)))
    rows.append(row("Kneser(7,3)", *kneser(7, 3)))
    n, E = hoffman_singleton()
    rows.append(row("Hoffman-Singleton", n, E, bip=50, do_bip=False))
    for g6 in ["K?ABBBwerwBw", "K?BD@g]Qvo^?", "L??ED@_~?~^_Fw", "M?AE@bH{AYN_LgBs?"]:
        n, E = C.graph6_to_edges(g6)
        rows.append(row(f"extremal N={n} ({g6})", n, E))

    print()
    print("=" * 78)
    print("worst mechanism-2 ratio  min_I e(G-I) / N^2  (mechanism ceiling)")
    print("=" * 78)
    worst = max(rows, key=lambda r: F(r['M2'], r['n'] ** 2))
    print(f"    worst = {worst['name']}: {F(worst['M2'], worst['n']**2)}"
          f" = {float(F(worst['M2'], worst['n']**2)):.6f}   vs 1/25 = 0.04")


if __name__ == "__main__":
    main()
