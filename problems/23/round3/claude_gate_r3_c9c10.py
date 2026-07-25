"""ROOT-AGENT GATE (Claude): independent re-derivation of the round-3 agent-appended claims
R3-C6 (independent-set covering family) and R3-C8 (density band), plus the numeric side of my own
R3-C9 / R3-C10.  Own graph constructions, own maximum-cut, exact integers.
"""
from fractions import Fraction as F
from itertools import combinations


def mk(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return n, adj, sorted({(min(u, v), max(u, v)) for u, v in E})


def circ(m, S):
    return mk(m, [(v, (v + s) % m) for v in range(m) for s in S if v != (v + s) % m])


def andrasfai(k):
    m = 3 * k - 1
    return circ(m, [s for s in range(1, m) if s % 3 == 1])


def blowup(base, t):
    n, adj, E = base
    EE = [(t * u + i, t * v + j) for (u, v) in E for i in range(t) for j in range(t)]
    return mk(n * t, EE)


def clebsch():
    V = list(range(16))
    S = {1, 2, 4, 8, 15}
    return mk(16, [(u, v) for u in V for v in V if u < v and (u ^ v) in S])


def bip_exact(n, adj, E):
    best = len(E)
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        c = sum(1 for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        best = min(best, c)
    return best


def maximal_independent_sets(n, adj):
    out = []
    for r in range(1, n + 1):
        for S in combinations(range(n), r):
            if all(v not in adj[u] for u, v in combinations(S, 2)):
                out.append(S)
    return out


def e_minus(E, I):
    Is = set(I)
    return sum(1 for (u, v) in E if u not in Is and v not in Is)


GS = [('C5', circ(5, [1])), ('C5[2]', blowup(circ(5, [1]), 2)), ('C5[3]', blowup(circ(5, [1]), 3)),
      ('And(3)=Wagner', andrasfai(3)), ('And(4)', andrasfai(4)), ('And(5)', andrasfai(5)),
      ('Clebsch', clebsch()), ('Petersen', mk(10, [(i, (i + 1) % 5) for i in range(5)] +
                                              [(i, 5 + i) for i in range(5)] +
                                              [(5 + i, 5 + (i + 2) % 5) for i in range(5)])),
      ('C13', circ(13, [1])), ('C15', circ(15, [1])), ('C19', circ(19, [1]))]

print("independent re-derivation of the agent-appended R3-C6 and R3-C8\n")
print(f"{'graph':14s} {'N':>3s} {'|E|':>4s} {'bip':>4s} {'M2=min_I e(G-I)':>16s} {'N^2/25':>8s} "
      f"{'M2>N^2/25?':>11s} {'|E|-4|E|^2/N^2':>15s} {'chain ok':>9s}")
for name, (n, adj, E) in GS:
    b = bip_exact(n, adj, E)
    M2 = min(e_minus(E, I) for I in maximal_independent_sets(n, adj))
    M1 = min(e_minus(E, sorted(adj[v])) for v in range(n))      # neighbourhood cuts only
    avg = F(len(E)) - F(sum(len(adj[u]) ** 2 for u in range(n)), n)
    cs = F(len(E)) - F(4 * len(E) ** 2, n * n)
    tgt = F(n * n, 25)
    chain_ok = (b <= M2 <= M1 <= avg <= cs)
    print(f"{name:14s} {n:3d} {len(E):4d} {b:4d} {M2:16d} {str(tgt):>8s} "
          f"{str(M2 > tgt):>11s} {str(cs):>15s} {str(chain_ok):>9s}")
    assert b <= M2 and b <= tgt, name
    assert b <= M1 <= avg <= cs, (name, b, M1, avg, cs)

print("\nchain  bip <= min_v e(G-N(v)) <= |E| - (1/N)sum d^2 <= |E| - 4|E|^2/N^2   holds everywhere")
print("roots of 4x^2 - x + 1/25 = 0 with x = |E|/N^2:", F(1, 20), "and", F(1, 5),
      "-> proved for |E| <= N^2/20 and for |E| >= N^2/5")
x = F(2, 25)
print("posted sparse endpoint 2/25: x - 4x^2 =", x - 4 * x * x, "=", float(x - 4 * x * x),
      "> 1/25, so the posted endpoint is indeed wrong;  C13/C15/C19 above are explicit witnesses")
print("\nWagner falsifier of the independent-set family, by hand: N=8, |E|=12, alpha=3, every")
print("independent 3-set is a neighbourhood, so M2 = 12 - 3*3 = 3 > 64/25 = 2.56.  CONFIRMED")
