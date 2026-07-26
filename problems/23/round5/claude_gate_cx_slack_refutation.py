"""ROOT-AGENT GATE (Claude): Codex refutes MY R3-C37/R3-C46 slack claim. Check it.

I claimed (R3-C37, and again in R3-C46/C47) that the non-C5-colourable half of the Gamma_11 split
carries roughly 17% slack -- max 25*psi/q^2 about 0.826 -- and that this made the residual target
NON-SHARP, which was the whole selling point.

Codex (TICK-CX-192/197) says the non-colourable side is still SHARP, with an explicit family: on the
minimal non-colourable support S = {0,1,2,4,5,6,8,9} with induced C5 C = {0,1,4,5,8}, put weight M on
C and weight 1 on S - C = {2,6,9}. Then

        bip(Gamma_11[a(M)]) = M^2 + 1,   sum a = 5M + 3,
        25 * bip / (sum a)^2 = 25(M^2+1)/(5M+3)^2  ->  1   as M -> infinity,

with 25000025/25030009 at M = 1000. If true, no uniform positive epsilon exists on the
non-colourable full-support region and my 17% figure was an artefact of testing only small q.

My measurements ran q <= 15, where M is at most 3 -- so I would never have seen this. Checked here in
exact integer arithmetic over all 1024 cuts.
"""
from fractions import Fraction as F


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)

S = {0, 1, 2, 4, 5, 6, 8, 9}
C = {0, 1, 4, 5, 8}
rest = sorted(S - C)
print(f"support S = {sorted(S)} (size {len(S)}), pentagon C = {sorted(C)}, S-C = {rest}")
print(f"C induces a 5-cycle: "
      f"{all(len(A[v] & C) == 2 for v in C)}")


def colourable(sup):
    sup = sorted(sup)
    c = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for t in range(5 if i else 1):
            if all((c[w] - t) % 5 in (1, 4) for w in A[v] if w in c):
                c[v] = t
                if rec(i + 1):
                    return True
                c.pop(v)
        return False

    return rec(0)


print(f"S is NOT C5-colourable: {not colourable(S)}   (so it is in my 'hard half')")

print(f"\n{'M':>6s} {'sum a':>8s} {'bip':>12s} {'M^2+1':>12s} {'match':>6s} "
      f"{'25*bip/(sum a)^2':>22s}")
prev = None
for M in (1, 2, 3, 5, 10, 50, 200, 1000):
    a = [0] * n
    for v in C:
        a[v] = M
    for v in rest:
        a[v] = 1
    q = sum(a)
    best = None
    for mm in range(1 << (n - 1)):
        Sb = (mm << 1) | 1
        s = sum(a[u] * a[v] for (u, v) in E if ((Sb >> u) & 1) == ((Sb >> v) & 1))
        if best is None or s < best:
            best = s
    ratio = F(25 * best, q * q)
    print(f"{M:6d} {q:8d} {best:12d} {M*M+1:12d} {str(best == M*M+1):>6s} "
          f"{str(ratio):>22s} = {float(ratio):.8f}")
    prev = ratio

print(f"\nlimit of 25(M^2+1)/(5M+3)^2 as M -> infinity: {25/25:.6f}")
print("If bip = M^2+1 holds and the ratio climbs toward 1, my 17% slack claim is REFUTED and the")
print("non-colourable half is as sharp as the colourable half. My q <= 15 scans reached only M = 3.")
