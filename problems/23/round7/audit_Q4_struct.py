"""AUDIT of the structural claims of Q4.md section 3 / section 1.4:
  S1  the 29 cuts in the Gamma_8 certificate are exactly the inclusion-minimal monochromatic sets
      among all 2^7 = 128 cuts (and 135 of 2^9 = 512 for Petersen);
  S2  only 12 of the 29 are arcs of the circle;
  S3  the cut S = {1,3,5,7} has monochromatic edges {04,15,26,37} and is the second-heaviest cut
      of the certificate by multiplier mass;
  S4  the domination lemma is sound as stated (a listed cut's mono set contains no other's).
"""
import pickle
from fractions import Fraction as F
from itertools import combinations


def gamma_graph(n):
    third = F(1, 3)
    return [[(i != j and min(F((i - j) % n, n), F((j - i) % n, n)) > third) for j in range(n)]
            for i in range(n)]


def petersen():
    V = sorted(combinations(range(5), 2))
    return [[(i != j and not (set(V[i]) & set(V[j]))) for j in range(len(V))] for i in range(len(V))]


def analyse(path, adj, name):
    C = pickle.load(open(path, "rb"))
    n = len(adj)
    E = [tuple(sorted(e)) for e in C['E']]
    mine = [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i][j]]
    assert sorted(E) == mine

    monosets, sidesets = {}, {}
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        ms = frozenset(k for k, (u, v) in enumerate(E) if side[u] == side[v])
        if ms not in monosets:
            monosets[ms] = mask
            sidesets[ms] = frozenset(v for v in range(n) if side[v] == 1)
    minimal = [ms for ms in monosets if not any(o < ms for o in monosets)]
    listed = [frozenset(mo) for _, mo in C['cuts']]
    print(f"{name}: {len(monosets)} distinct mono-sets from {1<<(n-1)} cuts; "
          f"{len(minimal)} inclusion-minimal; certificate lists {len(listed)}")
    print(f"  listed == inclusion-minimal ?  {set(listed) == set(minimal)}")

    # arcs
    def is_arc(S):
        S = set(S)
        for T in (S, set(range(n)) - S):
            if not T:
                return True
            for start in range(n):
                if all(((start + t) % n in T) for t in range(len(T))):
                    return True
        return False

    mass = {}
    for (Sidx, m), v in C['nu'].items():
        mass[Sidx] = mass.get(Sidx, F(0)) + v
    order = sorted(mass, key=lambda s: -mass[s])
    if name.startswith("Gamma_8"):
        arcs = [i for i, ms in enumerate(listed) if is_arc(sidesets[ms])]
        print(f"  arcs among the listed cuts: {len(arcs)} of {len(listed)}")
    print("  heaviest cuts by multiplier mass (rank, side set, mono edges, mass):")
    for r, s in enumerate(order[:4]):
        ms = listed[s]
        print(f"    #{r+1}: side={sorted(sidesets[ms])}  mono={[E[k] for k in sorted(ms)]}  "
              f"mass={float(mass[s]):.6f}")
    tot = sum(mass.values())
    print(f"  total multiplier mass nu(1,..,1) = {tot} "
          f"(must be 25*n^2 = {25*n*n} since sum_S nu_S = 25 L^2)")
    # S4 antichain check
    print(f"  listed family is an antichain: "
          f"{not any(a < b for a in listed for b in listed)}")


analyse("Q4_cert_g8_d1.pkl", gamma_graph(8), "Gamma_8")
print()
analyse("Q4_cert_gpetersen_d1.pkl", petersen(), "Petersen")
