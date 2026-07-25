"""Global-ish maximiser for  beta(H) = max_{w>=0, sum w = D}  bip(H[w]) / D^2 .

Calibration requirement: any H containing a 5-cycle satisfies beta(H) >= 1/25, so the
optimiser MUST return 25*bip/D^2 >= 1 on every such H. The plain random-start hill climb
fails that test (Petersen -> 0.77), so we use:
  * structured starts: weight D/5 on each vertex of each 5-cycle of H (the conjectured
    extremal configuration), plus D/(2k+1) on each odd cycle found, plus uniform, plus random;
  * multi-unit transfer moves (step sizes 1,2,4,...) so the climb can leave plateaus;
  * a refinement ladder D = 25 -> 50 -> 100 -> 200 -> 400 restarted from the rescaled winner.
All arithmetic on the acceptance path is exact integer.
"""
import numpy as np, random
from beta import Template


def odd_cycles(n, edges, length, cap=250, seed=0):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    out, seen = [], set()
    def rec(start, path, used):
        if len(out) >= cap:
            return
        if len(path) == length:
            if start in adj[path[-1]]:
                key = frozenset(path)
                if key not in seen:
                    seen.add(key); out.append(list(path))
            return
        for x in adj[path[-1]]:
            if x > start and not (used >> x) & 1:
                path.append(x); rec(start, path, used | (1 << x)); path.pop()
    for s in range(n):
        rec(s, [s], 1 << s)
        if len(out) >= cap:
            break
    return out


def climb(t, w, steps=(8, 4, 2, 1), maxit=4000):
    n = t.n
    w = np.asarray(w, dtype=np.float64).copy()
    cur = t.bip(w)[0]
    mv = np.array([(i, j) for i in range(n) for j in range(n) if i != j])
    nmv = len(mv)
    deltas = []
    for q in steps:
        d = np.zeros((nmv, n))
        d[np.arange(nmv), mv[:, 0]] = -q
        d[np.arange(nmv), mv[:, 1]] += q
        deltas.append(d)
    D = np.vstack(deltas)
    for _ in range(maxit):
        cand = w[None, :] + D
        ok = cand.min(axis=1) >= 0
        vals = np.where(ok, t.bip_batch(cand), -1.0)
        k = int(np.argmax(vals))
        if vals[k] > cur:
            cur = int(round(vals[k])); w = cand[k]
        else:
            break
    return cur, w


def starts_for(t, D, seed=0, nrand=30, cap_cycles=200):
    n, E = t.n, t.edges
    rng = random.Random(seed)
    S = []
    base = np.full(n, D // n, float); base[: D - int(base.sum())] += 1
    S.append(base)
    for L in (5, 7, 9):
        if L > n:
            break
        for cyc in odd_cycles(n, E, L, cap=cap_cycles, seed=seed):
            w = np.zeros(n); q, r = divmod(D, L)
            for idx, v in enumerate(cyc):
                w[v] = q + (1 if idx < r else 0)
            S.append(w)
    for _ in range(nrand):
        k = rng.randint(2, n)
        sup = rng.sample(range(n), k)
        w = np.zeros(n)
        for _ in range(D):
            w[sup[rng.randrange(k)]] += 1
        S.append(w)
    return S


def beta_max(t, ladder=(25, 50, 100, 200), seed=0, keep=6, nrand=30, cap_cycles=200):
    """returns (best_ratio, D, w, bip)"""
    D0 = ladder[0]
    pool = []
    for w0 in starts_for(t, D0, seed=seed, nrand=nrand, cap_cycles=cap_cycles):
        v, w = climb(t, w0)
        pool.append((v, w))
    pool.sort(key=lambda z: -z[0])
    pool = pool[:keep]
    best = (25.0 * pool[0][0] / D0 ** 2, D0, [int(x) for x in pool[0][1]], pool[0][0])
    cur = [w for _, w in pool]
    for D in ladder[1:]:
        nxt = []
        for w in cur:
            s = np.floor(np.asarray(w) * D / np.sum(w))
            s[int(np.argmax(s))] += D - s.sum()
            if s.min() < 0:
                continue
            v, w2 = climb(t, s)
            nxt.append((v, w2))
        if not nxt:
            break
        nxt.sort(key=lambda z: -z[0])
        nxt = nxt[:keep]
        r = 25.0 * nxt[0][0] / D ** 2
        if r > best[0]:
            best = (r, D, [int(x) for x in nxt[0][1]], nxt[0][0])
        cur = [w for _, w in nxt]
    return best
