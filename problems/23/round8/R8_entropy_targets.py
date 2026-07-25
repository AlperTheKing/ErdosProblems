"""The rainbow-1 / averaging-certificate test on the graphs that matter.

For each target H:
  * R(H) = set of rainbow-1 cuts (mono set meets every induced C5 exactly once)
  * whether the mono sets of R(H) partition E(H)
  * class-degree c(v) = number of distinct classes met by the edges at v
  * THEOREM R8-4 (star kill): if some v has c(v) = |R| = 5 then
        max_a min_{S in R} m_S(a) >= 1/20 > 1/25
    and no averaging certificate (arithmetic / geometric / power mean / Gibbs
    free energy at any beta) can certify max_x psi(H,x) <= 1/25.
Everything is exact: bitmasks over edges and integer weights.
"""

import numpy as np
from fractions import Fraction
from itertools import combinations


def nrm(E):
    return sorted(set((min(u, v), max(u, v)) for u, v in E))


def andrasfai(k):
    p = 3 * k - 1
    return p, nrm([(v, (v + s) % p) for v in range(p)
                   for s in range(1, p) if s % 3 == 1])


def mycielski(n, E):
    """M(G): 0..n-1 original, n..2n-1 shadows, 2n apex."""
    F = list(E)
    for u, v in E:
        F.append((n + u, v))
        F.append((n + v, u))
    for u in range(n):
        F.append((n + u, 2 * n))
    return 2 * n + 1, nrm(F)


def cyc(n):
    return n, nrm([(i, (i + 1) % n) for i in range(n)])


def petersen():
    E = []
    for i in range(5):
        E += [(i, (i + 1) % 5), (i, 5 + i), (5 + i, 5 + (i + 2) % 5)]
    return 10, nrm(E)


def blowup(n, E, a):
    st, idx = [], 0
    for i in range(n):
        st.append(idx)
        idx += a[i]
    F = [(st[u] + p, st[v] + q) for (u, v) in E
         for p in range(a[u]) for q in range(a[v])]
    return idx, nrm(F)


def clebsch():
    E = [(u, v) for u in range(16) for v in range(u + 1, 16)
         if bin(u ^ v).count("1") in (1, 4)]
    return 16, nrm(E)


def g6(s):
    d = [ord(c) - 63 for c in s.strip()]
    n = d[0]
    bits = []
    for x in d[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    E, i = [], 0
    for j in range(1, n):
        for u in range(j):
            if bits[i]:
                E.append((u, j))
            i += 1
    return n, nrm(E)


def analyse(name, n, E, show=True):
    m = len(E)
    assert m <= 63, f"{name}: too many edges for uint64"
    eidx = {e: i for i, e in enumerate(E)}
    adj = np.zeros((n, n), dtype=bool)
    for u, v in E:
        adj[u, v] = adj[v, u] = True
    tf = all(not (adj[u] & adj[v]).any() for u, v in E)
    # induced C5s
    pmask = []
    for S in combinations(range(n), 5):
        sub = adj[np.ix_(S, S)]
        if sub.sum() != 10 or (sub.sum(1) != 2).any():
            continue
        seen, st = {S[0]}, [S[0]]
        while st:
            v = st.pop()
            for u in S:
                if adj[v, u] and u not in seen:
                    seen.add(u)
                    st.append(u)
        if len(seen) != 5:
            continue
        msk = 0
        for (u, v) in combinations(S, 2):
            if adj[u, v]:
                msk |= 1 << eidx[(u, v)]
        pmask.append(msk)
    if not pmask:
        if show:
            print(f"{name:22s} n={n:3d} |E|={m:3d} tf={tf}  no induced C5")
        return None
    P = np.array(pmask, dtype=np.uint64)
    # all cuts as mono masks, vectorised
    cuts = np.arange(1 << (n - 1), dtype=np.uint64)
    mono = np.zeros(cuts.shape, dtype=np.uint64)
    for i, (u, v) in enumerate(E):
        bu = (cuts >> np.uint64(u)) & np.uint64(1) if u < n - 1 else np.uint64(0)
        bv = (cuts >> np.uint64(v)) & np.uint64(1) if v < n - 1 else np.uint64(0)
        mono |= np.uint64(1 << i) * ((bu ^ bv) ^ np.uint64(1))
    ok = np.ones(cuts.shape, dtype=bool)
    for p in P:
        ok &= (np.bitwise_count(mono & p) == 1)
    R = [int(x) for x in mono[ok]]
    Runiq = sorted(set(R))
    # partition test + class degrees
    cover = [0] * m
    for msk in Runiq:
        for i in range(m):
            if (msk >> i) & 1:
                cover[i] += 1
    is_part = all(c == 1 for c in cover)
    cdeg = []
    for v in range(n):
        inc = [i for i, e in enumerate(E) if v in e]
        cdeg.append(sum(1 for msk in Runiq if any((msk >> i) & 1 for i in inc)))
    kill = (len(Runiq) > 0 and max(cdeg) == len(Runiq) and len(Runiq) <= 6)
    deg = [int(adj[v].sum()) for v in range(n)]
    if show:
        verdict = ("NO rainbow-1 cut -> averaging DEAD" if not Runiq else
                   ("star kill -> averaging DEAD" if kill else "survives"))
        print(f"{name:22s} n={n:3d} |E|={m:3d} tf={tf} #indC5={len(pmask):5d} "
              f"|R|={len(Runiq):4d} part={str(is_part):5s} "
              f"deg=[{min(deg)},{max(deg)}] cdeg_max={max(cdeg) if cdeg else 0}"
              f"  {verdict}")
    return Runiq, is_part, cdeg, E, n


def star_witness(name, res):
    """Exhibit and verify the exact killing weighting for a star kill."""
    Runiq, is_part, cdeg, E, n = res
    v = int(np.argmax(cdeg))
    k = len(Runiq)
    chosen = {}
    for j, msk in enumerate(Runiq):
        for i, e in enumerate(E):
            if (msk >> i) & 1 and v in e:
                chosen[j] = e[0] + e[1] - v
                break
    a = [0] * n
    a[v] = k                      # weight k on the centre
    for j in chosen:
        a[chosen[j]] += 1         # weight 1 on one leaf per class
    q = sum(a)
    vals = [sum(a[u] * a[w] for i, (u, w) in enumerate(E) if (msk >> i) & 1)
            for msk in Runiq]
    print(f"    witness a = {a} (centre v={v}, sum a = {q})")
    print(f"    m_S(a) over the {k} admissible cuts: {vals}")
    print(f"    min = {min(vals)} = {Fraction(min(vals), q*q)} (sum a)^2 "
          f"vs 1/25 -> {'KILL' if Fraction(min(vals), q*q) > Fraction(1,25) else 'no kill'}")
    return a, vals


if __name__ == "__main__":
    C5 = cyc(5)
    targets = [("C5", cyc(5)), ("C7", cyc(7)),
               ("C5[2]", blowup(5, C5[1], [2] * 5)),
               ("C5[3]", blowup(5, C5[1], [3] * 5)),
               ("C5[2,1,2,1,2]", blowup(5, C5[1], [2, 1, 2, 1, 2])),
               ("Petersen", petersen()),
               ("And(3)=Wagner", andrasfai(3)),
               ("And(4)", andrasfai(4)),
               ("And(5)", andrasfai(5)),
               ("And(6)", andrasfai(6)),
               ("Grotzsch=M(C5)", mycielski(*cyc(5))),
               ("M(C7)", mycielski(*cyc(7))),
               ("Clebsch", clebsch()),
               ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?")),
               ]
    for name, (n, E) in targets:
        res = analyse(name, n, E)
        if res and res[0] and max(res[2]) == len(res[0]) and len(res[0]) <= 6:
            star_witness(name, res)
