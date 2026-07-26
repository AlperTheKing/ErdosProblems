"""ROOT-AGENT (Claude): orbit structure of the non-C5-colourable supports of Gamma_11.

claude_noncolourable_split.py established the reduction: max_x psi(Gamma_11) <= 1/25 follows from
  (i)  C5-colourable supports -- PROVED, since the support then sits inside a complete C5 blow-up and
       Theorem B plus AM-GM give psi <= (sum x)^2/25; and
  (ii) NON-C5-colourable supports -- open, but only 45 of the 2047 subsets are of this kind, and the
       measured maximum there is 0.69..0.78 of the target rather than 1.

This prints the D_22 orbit structure of those 45, and the per-support maximum of psi over
FULL-SUPPORT weightings, which is the quantity the reduction actually needs.
"""
import numpy as np

n = 11
E = [(u, v) for u in range(n) for v in range(u + 1, n)
     if 3 * min((u - v) % n, (v - u) % n) > n]
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)


def colourable(mask):
    sup = [v for v in range(n) if (mask >> v) & 1]
    c = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for k in range(5 if i else 1):
            if all((c[w] - k) % 5 in (1, 4) for w in A[v] if w in c):
                c[v] = k
                if rec(i + 1):
                    return True
                c.pop(v)
        return False

    return rec(0)


nc = [m for m in range(1, 1 << n) if not colourable(m)]
ncset = set(nc)


def rot(m, k):
    return sum(((m >> v) & 1) << ((v + k) % n) for v in range(n))


def ref(m):
    return sum(((m >> v) & 1) << ((-v) % n) for v in range(n))


seen, orbs = set(), []
for m in nc:
    if m in seen:
        continue
    o = set()
    for k in range(n):
        o.add(rot(m, k))
        o.add(rot(ref(m), k))
    seen |= o
    orbs.append((m, len(o & ncset)))

print(f"Gamma_11: non-C5-colourable subsets = {len(nc)} of {(1 << n) - 1}")
print(f"D_22 orbits among them: {len(orbs)}")

ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])
ncuts = 1 << (n - 1)
M = np.zeros((ncuts, len(E)), dtype=np.int32)
mm = np.arange(ncuts, dtype=np.int64)
Sb = (mm << 1) | 1
for k, (u, v) in enumerate(E):
    M[:, k] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
MT = np.ascontiguousarray(M.T)


def compositions_pos(total, parts):
    """compositions with every part STRICTLY positive (full support)"""
    if parts == 1:
        if total >= 1:
            yield [total]
        return
    for first in range(1, total - parts + 2):
        for rest in compositions_pos(total - first, parts - 1):
            yield [first] + rest


for m, sz in orbs:
    sup = [v for v in range(n) if (m >> v) & 1]
    best = 0.0
    bestq = None
    for q in (len(sup), len(sup) + 2, len(sup) + 4, 12, 14):
        if q < len(sup):
            continue
        cnt = 0
        for part in compositions_pos(q, len(sup)):
            a = [0] * n
            for i, v in enumerate(sup):
                a[v] = part[i]
            arr = np.array([a], dtype=np.int32)
            pr = (arr[:, ue] * arr[:, ve]).astype(np.int32)
            val = 25 * int((pr @ MT).min()) / (q * q)
            if val > best:
                best, bestq = val, (q, list(a))
            cnt += 1
            if cnt > 40000:
                break
    print(f"  orbit rep {sup} (size {len(sup)}), orbit length {sz}: "
          f"max 25*psi/q^2 over FULL-SUPPORT weightings = {best:.6f}")
    if bestq:
        print(f"      attained at q = {bestq[0]}, a = {bestq[1]}")
print("\nEvery value strictly below 1 means the non-colourable half of the split carries a MARGIN,")
print("which is what makes it finitely checkable, unlike the sharp colourable half.")
