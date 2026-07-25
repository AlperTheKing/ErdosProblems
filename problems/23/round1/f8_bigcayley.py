"""
f8_bigcayley.py -- wide net over large Cayley graphs with sum-free connection sets.

Cay(A,S) is triangle-free  <=>  S is sum-free (S cap (S+S) = empty).
Groups: Z_n (n<=90), Z_a x Z_b (ab<=90), dihedral D_n (order 2n<=90, product-free S).
Connection sets: random maximal sum-free / product-free sets (greedy from a random order),
plus the canonical "C5-type" set  {g : g mod 5 in {2,3}}  when 5 | |A|.

Any cut found gives a RIGOROUS upper bound on bip, so a ratio <= 1/25 rejects the graph.
"""
import sys, random, itertools
from f8_core import g6_encode, is_triangle_free, edges_of

rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
MAXORD = int(sys.argv[2]) if len(sys.argv) > 2 else 90
SAMPLES = int(sys.argv[3]) if len(sys.argv) > 3 else 60


def cayley(elems, op, inv, S):
    idx = {g: i for i, g in enumerate(elems)}
    n = len(elems)
    adj = [0] * n
    for g in elems:
        for s in S:
            h = op(g, s)
            i, j = idx[g], idx[h]
            if i != j:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return n, adj


def random_maximal_sumfree(elems, op, inv, e):
    order = [g for g in elems if g != e]
    rnd.shuffle(order)
    S = []
    for x in order:
        if x == e:
            continue
        cand = S + [x]
        ok = True
        for a in cand:
            for b in cand:
                if op(a, b) in cand:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            S.append(x)
    # symmetrise for an undirected Cayley graph
    S = sorted(set(S) | set(inv(x) for x in S))
    return S


GROUPS = []
for n in range(5, MAXORD + 1):
    GROUPS.append((f"Z{n}", list(range(n)), (lambda n: (lambda a, b: (a + b) % n))(n),
                   (lambda n: (lambda a: (-a) % n))(n), 0))
for a in range(2, 10):
    for b in range(a, MAXORD // a + 1):
        if 5 <= a * b <= MAXORD and a > 1:
            E = [(i, j) for i in range(a) for j in range(b)]
            GROUPS.append((f"Z{a}xZ{b}", E,
                           (lambda a, b: (lambda x, y: ((x[0] + y[0]) % a, (x[1] + y[1]) % b)))(a, b),
                           (lambda a, b: (lambda x: ((-x[0]) % a, (-x[1]) % b)))(a, b), (0, 0)))
for n in range(3, MAXORD // 2 + 1):
    E = [(r, s) for r in range(n) for s in (0, 1)]     # (rotation r, reflection flag s)
    def mkop(n):
        def op(x, y):
            r1, s1 = x; r2, s2 = y
            if s1 == 0:
                return ((r1 + r2) % n, s2)
            return ((r1 - r2) % n, 1 - s2)
        return op
    def mkinv(n):
        def inv(x):
            r, s = x
            return ((-r) % n, 0) if s == 0 else (r, 1)
        return inv
    GROUPS.append((f"D{n}", E, mkop(n), mkinv(n), (0, 0)))

best = []
for name, elems, op, inv, e in GROUPS:
    N = len(elems)
    if N > MAXORD:
        continue
    seen = set()
    for _ in range(SAMPLES):
        S = random_maximal_sumfree(elems, op, inv, e)
        if not S or tuple(S) in seen:
            continue
        seen.add(tuple(S))
        n, adj = cayley(elems, op, inv, S)
        if not is_triangle_free(n, adj):
            continue
        m = len(edges_of(n, adj))
        if m <= 2 * n * n / 25.0:          # bip <= m/2 kills it outright
            continue
        best.append((g6_encode(n, adj), f"{name}|d={2*len(S)//2}", n, m))
print(f"# {len(best)} dense triangle-free Cayley graphs to screen", file=sys.stderr)
with open('f8_cayley.g6', 'w') as f, open('f8_cayley_names.txt', 'w') as g:
    for s, nm, n, m in best:
        f.write(s + "\n")
        g.write(f"{s}\t{nm}\n")
print(len(best))
