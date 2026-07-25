"""Best blow-up constructions:  LB(N) = max over triangle-free H (|V(H)|=h<=HMAX,
maximal) and integer weights t with sum(t)=N of bip(H[t]) (Lemma A, exact integers).

Combined with the PROVED upper bound a(N) <= N^2/25 for N <= 40 (Theorem 3 in
F1.md) this pins a(N) exactly whenever LB(N) = floor(N^2/25).
"""
import subprocess, os, sys
import numpy as np
from f1_bip import g6_decode

GENG = os.environ.get("GENG", r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe")
rng = np.random.default_rng(7)


def maximal_trianglefree(h):
    out = subprocess.run([GENG, "-tcq", str(h)], capture_output=True, text=True).stdout
    res = []
    for line in out.split():
        n, E = g6_decode(line)
        adj = [0] * n
        for u, v in E:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        ok = all((adj[i] >> j) & 1 or (adj[i] & adj[j])
                 for i in range(n) for j in range(i + 1, n))
        if ok:
            res.append((line, n, E))
    return res


def make_M(h, E):
    S = np.arange(1 << (h - 1), dtype=np.int64) * 2 + 1
    bits = np.array([[(int(s) >> v) & 1 for v in range(h)] for s in S], dtype=np.int8)
    M = np.array([[1 if bits[k][u] == bits[k][v] else 0 for (u, v) in E]
                  for k in range(len(S))], dtype=np.int64)
    return M


def best_for(h, E, M, N, tries=8):
    ei = np.array([e[0] for e in E]); ej = np.array([e[1] for e in E])

    def val(t):
        p = t[ei] * t[ej]
        return int((M @ p).min())

    best = -1; bestt = None
    for r in range(tries):
        if N < h:
            return -1, None
        t = np.full(h, N // h, dtype=np.int64)
        for k in range(N - t.sum()):
            t[(k if r == 0 else int(rng.integers(h))) % h] += 1
        if r > 0:
            for _ in range(h):
                i = int(rng.integers(h)); j = int(rng.integers(h))
                if t[i] > 1:
                    t[i] -= 1; t[j] += 1
        cur = val(t)
        improved = True
        while improved:
            improved = False
            for i in range(h):
                for j in range(h):
                    if i == j or t[i] <= 0:
                        continue
                    t[i] -= 1; t[j] += 1
                    v = val(t)
                    if v > cur:
                        cur = v; improved = True
                    else:
                        t[i] += 1; t[j] -= 1
        if cur > best:
            best, bestt = cur, t.copy()
    return best, bestt


def main():
    HMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    graphs = []
    for h in range(5, HMAX + 1):
        for (g6, n, E) in maximal_trianglefree(h):
            graphs.append((g6, h, E, make_M(h, E)))
    extra = ["K?ABBBwerwBw", "K?BD@g]Qvo^?", "L??FFB_~?~^_Fw", "L?`DAboU`w@{hS",
             "L?`DE`gl@YJODg", "M?AE@bH{AYN_LgBs?"]
    for g6 in extra:
        h, E = g6_decode(g6)
        if h > HMAX:
            graphs.append((g6, h, E, make_M(h, E)))
    print(f"{len(graphs)} candidate type-graphs", flush=True)
    print(" N  floor(N^2/25)   LB(N)  match?  best H (g6)  weights")
    for N in range(5, NMAX + 1):
        tgt = N * N // 25
        best = -1; rec = None
        for (g6, h, E, M) in graphs:
            if h > N:
                continue
            v, t = best_for(h, E, M, N)
            if v > best:
                best, rec = v, (g6, list(map(int, t)))
        flag = "EXACT" if best == tgt else ("gap %d" % (tgt - best))
        print(f"{N:3d}  {tgt:6d}      {best:5d}  {flag:8s} {rec[0]:20s} {rec[1]}", flush=True)


if __name__ == "__main__":
    main()
