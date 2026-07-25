"""beta(And(d)) for the Andrasfai graphs And(d) = Cay(Z_{3d-1}, {j : j = 1 mod 3}).

Motivation: Jin's theorem (delta > 10n/29 => chi <= 3) together with
Chen-Jin-Koh (delta > n/3 and chi <= 3 => G is homomorphic to some Andrasfai
graph) means that a counterexample to Erdos #23 with delta > 10n/29 would force
beta(And(d)) > 1/25 for some d.  Lemma A turns that into a finite max-min
problem per d.
"""
import numpy as np
from itertools import combinations

rng = np.random.default_rng(11)


def andrasfai(d):
    n = 3 * d - 1
    conn = set()
    for j in range(1, n):
        if j % 3 == 1:
            conn.add(j)
            conn.add((-j) % n)
    E = [(i, (i + j) % n) for i in range(n) for j in conn if (i + j) % n > i]
    E = sorted(set(tuple(sorted(e)) for e in E))
    return n, E


def trianglefree(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return all(not (adj[u] & adj[v]) for u, v in E)


def build(h, E):
    S = np.arange(1 << (h - 1), dtype=np.int64) * 2 + 1
    bits = np.zeros((1 << (h - 1), h), dtype=np.int8)
    for v in range(h):
        bits[:, v] = (S >> v) & 1
    M = np.zeros((1 << (h - 1), len(E)), dtype=np.float64)
    for k, (u, v) in enumerate(E):
        M[:, k] = (bits[:, u] == bits[:, v])
    return M


def optimise(h, E, M, restarts=10, iters=1500):
    ei = np.array([e[0] for e in E]); ej = np.array([e[1] for e in E])
    best, bt = -1.0, None
    for r in range(restarts):
        t = np.ones(h) / h if r == 0 else rng.dirichlet(np.ones(h))
        for it in range(iters):
            p = t[ei] * t[ej]
            vals = M @ p
            k = int(np.argmin(vals))
            row = M[k]
            g = np.zeros(h)
            np.add.at(g, ei, row * t[ej]); np.add.at(g, ej, row * t[ei])
            step = (0.3 / h) / (1 + it * 0.01)
            t = np.maximum(t + step * (g - g.mean()), 0.0)
            s = t.sum()
            t = t / s if s > 0 else np.ones(h) / h
        v = float((M @ (t[ei] * t[ej])).min())
        if v > best:
            best, bt = v, t.copy()
    return best, bt


def exact_int(h, E, t):
    best = None
    for s in range(1 << (h - 1)):
        S = (s << 1) | 1
        tot = sum(t[u] * t[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or tot < best:
            best = tot
    return best


for d in range(2, 7):
    n, E = andrasfai(d)
    assert trianglefree(n, E), d
    M = build(n, E)
    v, t = optimise(n, E, M)
    # balanced integer weights, W = 5n  (exact integer check)
    W = 5 * n
    tb = [5] * n
    print(f"And({d}): n={n} deg={2*len(E)//n} e={len(E)}  beta_num={v:.6f}  "
          f"(1/25={0.04})  balanced bip={exact_int(n, E, tb)} "
          f"25*bip-(W)^2={25*exact_int(n,E,tb)-W*W}  unit bip={exact_int(n,E,[1]*n)}"
          f" ratio_unit={exact_int(n,E,[1]*n)/n**2:.5f}")
