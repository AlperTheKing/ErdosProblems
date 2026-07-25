"""COUNTEREXAMPLE HUNT for Erdos #23 over all bounded-type triangle-free graphs.

By Lemma A (F1.md),  bip(H[t]) = min_{S subset V(H)} sum_{ij in E(H) uncut by S} t_i t_j
for every weight vector t of positive integers.  Every triangle-free graph whose
"twin quotient" has h vertices is such a blow-up.  Define

    beta(H) = sup_{t > 0} bip(H[t]) / (sum_i t_i)^2 .

The conjecture bip <= N^2/25 for all N is equivalent to beta(H) <= 1/25 for all
triangle-free H (Lemma B).  This script maximises beta(H) numerically over the
simplex (projected subgradient ascent, many restarts), then rounds to an integer
weight vector and RE-VERIFIES the value in exact integer arithmetic.

Any H,t with 25*bip(H[t]) > (sum t)^2 is an exact counterexample to Erdos #23.

Usage:  python beta_scan.py <hmin> <hmax>
Reads maximal triangle-free graphs from geng.
"""
import subprocess, sys, os
import numpy as np
from f1_bip import g6_decode, is_triangle_free

GENG = os.environ.get("GENG", r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe")
rng = np.random.default_rng(20260725)


def maximal_trianglefree(h):
    out = subprocess.run([GENG, "-tcq", str(h)], capture_output=True, text=True).stdout
    res = []
    for line in out.split():
        n, E = g6_decode(line)
        adj = [0] * n
        for u, v in E:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        ok = True
        for i in range(n):
            for j in range(i + 1, n):
                if not (adj[i] >> j) & 1 and (adj[i] & adj[j]) == 0:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            res.append((line, n, E))
    return res


def build(h, E):
    """M[s, e] = 1 iff edge e is uncut by subset s (bit-mask over V, 0 in S)."""
    ne = len(E)
    S = np.arange(1 << (h - 1), dtype=np.int64) * 2 + 1
    bits = np.zeros((1 << (h - 1), h), dtype=np.int8)
    for v in range(h):
        bits[:, v] = (S >> v) & 1
    M = np.zeros((1 << (h - 1), ne), dtype=np.float64)
    for k, (u, v) in enumerate(E):
        M[:, k] = (bits[:, u] == bits[:, v])
    return M


def exact_bip_blowup(h, E, t):
    """Exact integer min_S sum_{uncut} t_i t_j."""
    best = None
    for s in range(1 << (h - 1)):
        S = (s << 1) | 1
        tot = 0
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += t[u] * t[v]
        if best is None or tot < best:
            best = tot
    return best


def optimise(h, E, M, restarts=6, iters=700):
    ne = len(E)
    ei = np.array([e[0] for e in E])
    ej = np.array([e[1] for e in E])
    best_val, best_t = -1.0, None
    for r in range(restarts):
        t = np.ones(h) / h if r == 0 else rng.dirichlet(np.ones(h))
        step0 = 0.3 / h
        for it in range(iters):
            p = t[ei] * t[ej]
            vals = M @ p
            k = int(np.argmin(vals))
            row = M[k]
            g = np.zeros(h)
            np.add.at(g, ei, row * t[ej])
            np.add.at(g, ej, row * t[ei])
            step = step0 / (1 + it * 0.02)
            t = t + step * (g - g.mean())
            t = np.maximum(t, 0.0)
            s = t.sum()
            if s <= 0:
                t = np.ones(h) / h
            else:
                t /= s
        p = t[ei] * t[ej]
        v = float((M @ p).min())
        if v > best_val:
            best_val, best_t = v, t.copy()
    return best_val, best_t


def round_and_check(h, E, tvec, W):
    """Round the simplex point to integers summing to W; local integer polish."""
    raw = tvec * W
    t = np.maximum(np.floor(raw), 1).astype(int)
    while t.sum() < W:
        t[int(np.argmax(raw - t))] += 1
    while t.sum() > W:
        cand = [i for i in range(h) if t[i] > 1]
        if not cand:
            break
        t[min(cand, key=lambda i: raw[i] - t[i])] -= 1
    t = list(map(int, t))
    cur = exact_bip_blowup(h, E, t)
    improved = True
    while improved:
        improved = False
        for i in range(h):
            for j in range(h):
                if i == j or t[i] <= 1:
                    continue
                t[i] -= 1
                t[j] += 1
                v = exact_bip_blowup(h, E, t)
                if v > cur:
                    cur = v
                    improved = True
                else:
                    t[i] += 1
                    t[j] -= 1
    return cur, t


def main():
    hmin, hmax = int(sys.argv[1]), int(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    champs = []
    for h in range(hmin, hmax + 1):
        gs = maximal_trianglefree(h)
        bestratio, bestrec = -1, None
        over = []
        for (g6, n, E) in gs:
            M = build(h, E)
            v, t = optimise(h, E, M)
            ratio = v  # already normalised (sum t = 1)
            if ratio > 0.04 + 1e-9:
                over.append((g6, ratio, list(t)))
            if ratio > bestratio:
                bestratio, bestrec = ratio, (g6, E, t)
        if over:
            print("  !! graphs with continuous ratio > 1/25:", over)
        # exact re-verification of the champion of this h
        g6, E, t = bestrec
        val, tint = round_and_check(h, E, t, W)
        Wc = sum(tint)
        print(f"h={h:3d}  #maxtf={len(gs):5d}  best continuous beta={bestratio:.6f} "
              f"(1/25={1/25:.6f})  champion={g6}")
        print(f"        exact integer check: t={tint} sum={Wc} bip={val} "
              f"25*bip-(sum t)^2 = {25*val - Wc*Wc}  ratio={val/Wc**2:.6f}")
        champs.append((h, bestratio, g6, tint, val, Wc))
        sys.stdout.flush()
    print()
    print("SUMMARY (any positive '25*bip-(sum t)^2' would be a counterexample):")
    for (h, br, g6, tint, val, Wc) in champs:
        print(f"  h={h} beta_cont={br:.6f} exact 25*bip-(W)^2={25*val-Wc*Wc}")


if __name__ == "__main__":
    main()
