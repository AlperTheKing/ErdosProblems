"""AUDIT of the Q4 DUAL certificate (Q4_dualcert_g11_d1.pkl): the claim

    c*(Gamma_11, multiplier degree 2) <= 25445007099/1021743686 = 24.9035... < 25 .

Independent re-derivation.  Own graph, own monomial enumeration, own multinomials, own moment
blocks, own PSD test (LDL^T factorisation re-multiplied), own min over ALL 2^10 cuts.

It also states, explicitly, WHICH primal the ray excludes: the pairing step
    sum_{S,m} nu_{S,m} zhat_S(m)  >=  sum_m (sum_S nu_{S,m}) * min_S zhat_S(m)
uses nu_{S,m} >= 0 COEFFICIENTWISE.  A multiplier that is nonnegative only on the orthant
(mode 'sosy' of Q4_sos.py, or any nu_S with a negative coefficient) is NOT excluded by this ray,
and the script measures how badly that step would fail: it reports min over m of min_S zhat_S(m)
and the number of (S,m) with zhat_S(m) < 0.
"""
import sys, pickle
from fractions import Fraction as F
from itertools import combinations
from math import factorial

sys.path.insert(0, ".")
from audit_Q4_primal import psd_verified          # my own re-multiplied LDL^T test


def gamma_graph(n):
    third = F(1, 3)
    return [[(i != j and min(F((i - j) % n, n), F((j - i) % n, n)) > third) for j in range(n)]
            for i in range(n)]


def monomials(n, deg):
    """all exponent vectors of length n summing to deg -- own enumeration by combinations"""
    out = []
    for c in combinations(range(deg + n - 1), n - 1):
        e, prev = [], -1
        for x in c:
            e.append(x - prev - 1)
            prev = x
        e.append(deg + n - 2 - prev)
        out.append(tuple(e))
    return out


def multinom(a):
    r = factorial(sum(a))
    for t in a:
        r //= factorial(t)
    return r


def main(path="Q4_dualcert_g11_d1.pkl"):
    C = pickle.load(open(path, "rb"))
    m, d, z = C['m'], C['d'], C['z']
    n = m
    fails = []

    def need(cond, msg):
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        if not cond:
            fails.append(msg)

    print(f"AUDIT {path}: pattern Gamma_{m}, multiplier degree {2*d}")
    adj = gamma_graph(n)
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i][j]]
    need(len(E) == 22 and all(sum(r) == 4 for r in adj),
         f"Gamma_11 rebuilt: {len(E)} edges, 4-regular")
    need(not any(adj[a][b] and adj[b][c] and adj[a][c] for a, b, c in combinations(range(n), 3)),
         "triangle-free")

    monsD, monsT = monomials(n, 2 * d), monomials(n, 2 * d + 2)
    need(len(monsT) == len(z) == 1001 and set(monsT) == set(z),
         f"z is indexed by exactly the {len(monsT)} degree-{2*d+2} exponents")
    need(all(isinstance(v, F) for v in z.values()), "all moments are exact Fractions (no float)")
    need(all(v >= 0 for v in z.values()), "all moments are >= 0")

    # moment blocks by parity class, PSD each (this is what makes <Z_b,Q_b> >= 0)
    groups = {}
    for b in monsT:
        groups.setdefault(tuple(t % 2 for t in b), []).append(b)
    nbad, sizes = 0, sorted({len(B) for B in groups.values()}, reverse=True)
    for p, B in groups.items():
        k = len(B)
        M = [[z[tuple((B[i][t] + B[j][t]) // 2 for t in range(n))] for j in range(k)]
             for i in range(k)]
        ok, info = psd_verified(M)
        if not ok:
            nbad += 1
            print(f"    block {p} size {k}: {info}")
    need(nbad == 0, f"all {len(groups)} moment blocks PSD (sizes {sizes}), factorisations re-multiplied")

    # num / den, recomputed
    num = sum(F(multinom(a)) * z[a] for a in monsT)
    den = F(0)
    negcount, worst = 0, None
    for mm in monsD:
        best = None
        for mask in range(1 << (n - 1)):
            side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
            s = F(0)
            for u, v in E:
                if side[u] == side[v]:
                    a = list(mm)
                    a[u] += 1
                    a[v] += 1
                    s += z[tuple(a)]
            if best is None or s < best:
                best = s
        if best < 0:
            negcount += 1
        if worst is None or best < worst:
            worst = best
        den += F(multinom(mm)) * best
    need(num == C['num'], f"num recomputed = {num}  (stored {C['num']})")
    need(den == C['den'], f"den recomputed = {den}  (stored {C['den']})")
    need(den > 0, f"den > 0 (required for the division to be a valid bound)")
    r = num / den
    need(r == C['ratio'], f"ratio recomputed = {r} (stored {C['ratio']})")
    need(r < 25, f"ratio = {r} = {float(r):.9f} < 25")

    print(f"  SCOPE: min over m of min_S zhat_S(m) = {worst} = {float(worst):.9f}; "
          f"{negcount} of {len(monsD)} monomials have a negative min.")
    print("  SCOPE: the ray bounds ONLY multipliers with NONNEGATIVE COEFFICIENTS "
          "(mode 'coef').  Orthant-nonnegative multipliers with a negative coefficient on a "
          "monomial m whose min_S zhat_S(m) < 0 are not bounded by this argument.")

    print("AUDIT VERDICT:", "dual ray arithmetically CONFIRMED" if not fails else
          f"BROKEN ({len(fails)} failed checks)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Q4_dualcert_g11_d1.pkl")
