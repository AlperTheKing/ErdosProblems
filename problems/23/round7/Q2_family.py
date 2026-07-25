"""Q2_family.py -- MECHANISM CEILING for discharging schemes at a max cut.

A discharging scheme that only ever uses a family F of max-cut switching
inequalities can prove  25|M| <= N^2  only if

      c(F) := sup { |M|/N^2 : (H,cut,a) with all F-constraints satisfied }

equals 1/25.  Any (H,cut,a) with c > 1/25 is an EXACT witness killing every
scheme built from F.

Normalisation.  Weights a_i >= 0, sum a_i = 1 (so N = 1).  For a part-respecting
cut col of a blow-up H[a]:
    sigma_i = sum_{j~i, col_j != col_i} a_j - sum_{j~i, col_j == col_i} a_j
    M(a)    = sum_{ij in E, col_i == col_j} a_i a_j
    Delta_S(a) = -sum_i s_i sigma_i - 2 e_M(S) + 2 e_B(S),  0 <= s_i <= a_i
Delta is MULTILINEAR in s (parts are independent sets), so its max over the box
is at a corner s_i in {0, a_i}: checking part-subsets is exact and complete.

Families:
  LOCAL : only sigma_i >= 0            (all switch-star constraints are O(1/N)
                                        and hence vacuous after normalisation --
                                        this is exactly the "purely local" ceiling)
  STAR  : LOCAL + { S = N_H(i) u J : J independent in H, J cap N_H(i) = empty }
          (the family (*): switch a whole neighbourhood together with an
           independent set of second neighbours)
  ALL   : LOCAL + all 2^h part-subsets  ( <=> the cut really is maximum )
"""
import sys, subprocess, itertools, random
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import minimize, linprog

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def g6_decode(line):
    line = line.strip()
    if not line:
        return None
    bs = [ord(c) - 63 for c in line]
    n = bs[0]
    bits = []
    for b in bs[1:]:
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    adj = [[0] * n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i][j] = adj[j][i] = 1
            idx += 1
    return n, adj


def gen_patterns(h):
    out = []
    r = subprocess.run([GENG, "-t", "-c", str(h)], capture_output=True, text=True)
    for line in r.stdout.split():
        d = g6_decode(line)
        if d:
            out.append((line, d[0], d[1]))
    return out


def build(n, adj, col):
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i][j]]
    mono = [(i, j) for (i, j) in E if col[i] == col[j]]
    bi = [(i, j) for (i, j) in E if col[i] != col[j]]
    return E, mono, bi


def sigma_vec(n, adj, col, a):
    s = []
    for i in range(n):
        v = 0.0
        for j in range(n):
            if adj[i][j]:
                v += a[j] if col[j] != col[i] else -a[j]
        s.append(v)
    return np.array(s)


def delta_S(n, adj, col, a, S):
    """S = set of part indices, s_i = a_i for i in S."""
    sg = sigma_vec(n, adj, col, a)
    val = -sum(a[i] * sg[i] for i in S)
    for i in S:
        for j in S:
            if i < j and adj[i][j]:
                val += (-2 if col[i] == col[j] else 2) * a[i] * a[j]
    return val


def independent_subsets(n, adj, allowed):
    allowed = sorted(allowed)
    res = []
    for r in range(len(allowed) + 1):
        for J in itertools.combinations(allowed, r):
            ok = True
            for x in range(len(J)):
                for y in range(x + 1, len(J)):
                    if adj[J[x]][J[y]]:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                res.append(frozenset(J))
    return res


def family_sets(n, adj, kind):
    if kind == "LOCAL":
        return []
    if kind == "ALL":
        out = []
        for m in range(1, 1 << n):
            S = frozenset(i for i in range(n) if (m >> i) & 1)
            if len(S) < n:
                out.append(S)
        return out
    if kind == "STAR":
        out = set()
        for i in range(n):
            Nv = frozenset(j for j in range(n) if adj[i][j])
            rest = [j for j in range(n) if j not in Nv]
            for J in independent_subsets(n, adj, rest):
                S = Nv | J
                if 0 < len(S) < n:
                    out.add(S)
        return sorted(out, key=lambda s: (len(s), sorted(s)))
    raise ValueError(kind)


def solve(n, adj, col, sets, nstart=40, seed=0):
    """maximise M(a) s.t. sum a = 1, a>=0, sigma>=0, Delta_S<=0 for S in sets."""
    E, mono, bi = build(n, adj, col)
    if not mono:
        return 0.0, np.zeros(n)

    def negM(a):
        return -sum(a[i] * a[j] for (i, j) in mono)

    cons = [{"type": "eq", "fun": lambda a: a.sum() - 1.0}]
    for i in range(n):
        cons.append({"type": "ineq",
                     "fun": (lambda idx: (lambda a: sigma_vec(n, adj, col, a)[idx]))(i)})
    for S in sets:
        cons.append({"type": "ineq",
                     "fun": (lambda SS: (lambda a: -delta_S(n, adj, col, a, SS)))(S)})
    bnds = [(0.0, 1.0)] * n
    rng = random.Random(seed)
    best = (0.0, np.ones(n) / n)
    starts = [np.ones(n) / n]
    for _ in range(nstart):
        w = np.array([rng.random() ** 2 + 1e-3 for _ in range(n)])
        starts.append(w / w.sum())
    for x0 in starts:
        try:
            r = minimize(negM, x0, method="SLSQP", bounds=bnds, constraints=cons,
                         options={"maxiter": 400, "ftol": 1e-12})
        except Exception:
            continue
        if not r.success:
            continue
        a = np.clip(r.x, 0, None)
        if a.sum() <= 0:
            continue
        a = a / a.sum()
        # feasibility re-check with tolerance
        sg = sigma_vec(n, adj, col, a)
        if sg.min() < -1e-8:
            continue
        ok = True
        for S in sets:
            if delta_S(n, adj, col, a, S) > 1e-8:
                ok = False
                break
        if not ok:
            continue
        v = -negM(a)
        if v > best[0]:
            best = (v, a)
    return best


def main():
    hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    kinds = sys.argv[2].split(",") if len(sys.argv) > 2 else ["LOCAL", "STAR", "ALL"]
    TARGET = 1.0 / 25
    tops = {k: [] for k in kinds}
    for h in range(3, hmax + 1):
        pats = gen_patterns(h)
        print(f"# h={h}: {len(pats)} connected triangle-free patterns", flush=True)
        for (g6, n, adj) in pats:
            for cm in range(1 << (n - 1)):          # fix col[0]=0 (complement symmetry)
                col = [0] + [(cm >> i) & 1 for i in range(n - 1)]
                E, mono, bi = build(n, adj, col)
                if not mono:
                    continue
                for kind in kinds:
                    sets = family_sets(n, adj, kind)
                    v, a = solve(n, adj, col, sets, nstart=25, seed=hash((g6, cm)) & 0xffff)
                    if v > TARGET + 1e-9:
                        tops[kind].append((v, g6, n, tuple(col), tuple(np.round(a, 6))))
    for kind in kinds:
        L = sorted(tops[kind], reverse=True)[:12]
        print(f"\n### family {kind}: {len(tops[kind])} (H,cut) pairs exceed 1/25; top:")
        for v, g6, n, col, a in L:
            print(f"   M/N^2 = {v:.6f} (1/{1/v:.4f})  H={g6} n={n} cut={''.join(map(str,col))} a={a}")
        if not L:
            print("   NONE -- ceiling is <= 1/25 on every pattern tested")


if __name__ == "__main__":
    main()
