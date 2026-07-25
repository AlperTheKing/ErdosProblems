"""beta(H) for named triangle-free templates that are too large for the exhaustive geng sweep.
Every entry is checked for triangle-freeness first. A ratio > 1 would refute Erdos #23.
"""
import numpy as np, itertools, sys
from beta import Template, maximize

def andrasfai(k):
    n = 3 * k - 1
    S = {i % n for i in range(1, n, 3)}
    S |= {(-s) % n for s in S}
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) % n in S]
    return n, E

def circulant(n, S):
    S = {s % n for s in S} | {(-s) % n for s in S}
    return n, [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) % n in S]

def mycielski(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    N = 2 * n + 1
    EE = list(E)
    for i in range(n):
        for j in adj[i]:
            EE.append(tuple(sorted((i, n + j))))
    EE = sorted(set(EE))
    EE += [(n + i, 2 * n) for i in range(n)]
    return N, EE

def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]

def kneser(nn, kk):
    V = list(itertools.combinations(range(nn), kk))
    idx = {v: i for i, v in enumerate(V)}
    E = [(idx[a], idx[b]) for a, b in itertools.combinations(V, 2) if not set(a) & set(b)]
    return len(V), E

def clebsch():
    # folded 5-cube: vertices = even-weight subsets of F_2^5 ... use standard: V=F_2^4,
    # x~y iff x+y in {e1,e2,e3,e4, e1+e2+e3+e4}
    S = [1, 2, 4, 8, 15]
    E = [(x, y) for x in range(16) for y in range(x + 1, 16) if (x ^ y) in S]
    return 16, E

def is_tf(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    for u, v in E:
        if adj[u] & adj[v]:
            return False
    return True

GRAPHS = [
    ("C5", cycle(5)), ("C7", cycle(7)), ("C9", cycle(9)), ("C11", cycle(11)),
    ("Petersen=K(5,2)", kneser(5, 2)),
    ("And(3)=Wagner", andrasfai(3)), ("And(4)", andrasfai(4)),
    ("And(5)", andrasfai(5)), ("And(6)", andrasfai(6)),
    ("Grotzsch=M(C5)", mycielski(*cycle(5))),
    ("M(C7)", mycielski(*cycle(7))),
    ("Clebsch(16,5,0,2)", clebsch()),
    ("C13(1,5) R(3,5)", circulant(13, [1, 5])),
    ("C16(1,2,7)", circulant(16, [1, 2, 7])),
    ("C17(1,2,4,8)", circulant(17, [1, 2, 4, 8])),
    ("C18(1,5,8)", circulant(18, [1, 5, 8])),
    ("Mobius-Kantor C8(1,3)", circulant(8, [1, 3])),
]

if __name__ == "__main__":
    for name, (n, E) in GRAPHS:
        if not is_tf(n, E):
            print("%-22s n=%2d  SKIP (has a triangle)" % (name, n)); continue
        if n > 18:
            print("%-22s n=%2d  SKIP (too large for exhaustive cut enumeration)" % (name, n)); continue
        t = Template(n, E)
        best = (0.0, None, None)
        prev = None
        for D in (25, 50, 100):
            extra = []
            if prev is not None:
                s = np.round(np.array(prev, float) * D / sum(prev)); s[0] += D - s.sum()
                if s.min() >= 0: extra.append(s)
            b, w = maximize(t, D, restarts=25 if D < 100 else 10, seed=99 + D, starts_extra=extra)
            prev = w
            r = 25.0 * b / D ** 2
            if r > best[0]: best = (r, D, w)
        flag = "  <<< VIOLATION" if best[0] > 1 + 1e-12 else ""
        print("%-22s n=%2d |E|=%3d   max 25*bip/D^2 = %.6f  (D=%d, w=%s)%s"
              % (name, n, len(E), best[0], best[1], best[2], flag), flush=True)
