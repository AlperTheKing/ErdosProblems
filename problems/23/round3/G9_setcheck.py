"""G9: exact check that the SET-deletion mechanism cannot fire on the witness family
W_t = C5[7t,2t,7t,7t,2t].

Set-deletion bound (proved in the report):  for every nonempty S subset of V,
    bip(G) <= bip(G-S) + cost(S),   cost(S) = min over orderings of sum_i floor(b_i/2),
where b_i is the back-degree of the i-th re-inserted vertex.  Since sum_i b_i = E(S) :=
#edges meeting S and each floor loses at most 1/2,
    cost(S) >= (E(S) - |S|)/2 .
The mechanism FIRES on S (i.e. proves G is not a minimal counterexample) iff
    cost(S) <= (N^2 - (N-s)^2)/25 = (2Ns - s^2)/25 .
So the mechanism is DEFEATED if for every nonempty S :  (E(S) - s)/2 > (2Ns - s^2)/25.
Because all vertices in one part of a blow-up are twins, S is determined by (s_0..s_4).
E(S) = m - e(V\\S) = m - sum_i (a_i - s_i)(a_{i+1} - s_{i+1}).

Exact rational arithmetic throughout.
"""
from fractions import Fraction
from itertools import product
import sys

E5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]


def scan(a, use_exact_cost_for_small=True):
    N = sum(a)
    m = sum(a[u] * a[v] for u, v in E5)
    worst = None          # smallest margin with the crude bound
    bad = []              # S where the crude bound fails
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        eT = sum(rest[u] * rest[v] for u, v in E5)
        ES = m - eT
        lhs = Fraction(ES - ssz, 2)
        rhs = Fraction(2 * N * ssz - ssz * ssz, 25)
        marg = lhs - rhs
        if worst is None or marg < worst[0]:
            worst = (marg, s, ES, ssz)
        if marg <= 0:
            bad.append((s, ssz, ES, lhs, rhs))
    return worst, bad, N, m


def exact_cost_blowup(a, s):
    """Exact cost(S) = min over insertion orders of sum floor(b_i/2), for S given part-wise
    in a C5 blow-up.  DP over the state (c_0..c_4) = #already re-inserted per part.
    Only used for small instances."""
    from functools import lru_cache
    a = tuple(a); s = tuple(s)
    outside = tuple(a[i] - s[i] for i in range(5))

    @lru_cache(maxsize=None)
    def f(c):
        if all(c[i] == s[i] for i in range(5)):
            return 0
        best = None
        for i in range(5):
            if c[i] < s[i]:
                b = (outside[(i - 1) % 5] + c[(i - 1) % 5]) + (outside[(i + 1) % 5] + c[(i + 1) % 5])
                nc = list(c); nc[i] += 1
                val = b // 2 + f(tuple(nc))
                if best is None or val < best:
                    best = val
        return best
    return f((0, 0, 0, 0, 0))


if __name__ == "__main__":
    tmax = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for t in range(1, tmax + 1):
        a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
        worst, bad, N, m = scan(a)
        print(f"t={t} a={a} N={N} m={m}: crude-bound worst margin = {worst[0]} "
              f"at s={worst[1]} (E={worst[2]}, |S|={worst[3]});  #S where crude bound fails = {len(bad)}")
        # for the S where the crude bound fails, compute the exact cost
        nfire = 0
        for (s, ssz, ES, lhs, rhs) in bad:
            c = exact_cost_blowup(a, s)
            if Fraction(c) <= rhs:
                nfire += 1
                print(f"    *** MECHANISM FIRES: s={s} |S|={ssz} E={ES} exact cost={c} <= rhs={rhs}")
        print(f"    after exact cost evaluation on the {len(bad)} candidates: "
              f"#firing = {nfire}  -> mechanism {'FIRES' if nfire else 'DEFEATED'}")
