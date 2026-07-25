"""G9: exact analysis of the C5-blow-up witness family W_t = C5[7t,2t,7t,7t,2t].

Everything exact (Fraction / integers).

Facts used (accepted fact 1): bip(C5[a0..a4]) = min over cuts S of C5 of sum of monochromatic
a_u a_v.  For C5 a set F of edges is the monochromatic set of some cut iff |F| is odd, hence
    bip(C5[a]) = min_i a_i * a_{i+1}     (weights nonnegative, single edges cheapest).
This identity is re-verified against brute force in G9_verify2.py.
"""
from fractions import Fraction
from itertools import product

E5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]


def bip_blowup(a):
    """min over ODD subsets F of E5 of sum of a_u a_v.  Exact integer."""
    best = None
    for mask in range(32):
        if bin(mask).count("1") % 2 == 0:
            continue
        tot = 0
        for j, (u, v) in enumerate(E5):
            if (mask >> j) & 1:
                tot += a[u] * a[v]
        if best is None or tot < best:
            best = tot
    return best


def degrees(a):
    return [a[(i - 1) % 5] + a[(i + 1) % 5] for i in range(5)]


def report(a, label):
    N = sum(a)
    d = degrees(a)
    delta = min(d[i] for i in range(5) if a[i] > 0)
    b = bip_blowup(a)
    m = sum(a[u] * a[v] for u, v in E5)
    print(f"--- {label}: a={a} N={N} m={m} deg={d} delta={delta} "
          f"delta/N={Fraction(delta,N)} bip={b} N^2/25={Fraction(N*N,25)}")
    budget = Fraction(2 * N - 1, 25)
    drops = []
    for i in range(5):
        if a[i] == 0:
            continue
        a2 = list(a)
        a2[i] -= 1
        bi = bip_blowup(a2)
        drop = b - bi
        drops.append(drop)
        print(f"    part {i}: deg={d[i]} floor(d/2)={d[i]//2} bip(G-v)={bi} drop={drop} "
              f"drop==floor(d/2)? {drop == d[i]//2}  drop>budget({budget})? {drop > budget}")
    print(f"    min_v drop = {min(drops)}   budget (2N-1)/25 = {budget}  "
          f"single-vertex mechanism defeated? {min(drops) > budget}")
    return N, d, delta, b, m


def set_mechanism_check(a, verbose=False):
    """For every S given by (s_0..s_4) with 0<=s_i<=a_i, S nonempty, check whether the
    set-deletion mechanism can fire, i.e. whether  (E(S)-s)/2 <= (2Ns-s^2)/25 .
    E(S) = #edges meeting S = m - e(V\\S).
    Returns the list of firing S (empty list = mechanism fully defeated)."""
    N = sum(a)
    m = sum(a[u] * a[v] for u, v in E5)
    firing = []
    worst = None
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        eT = sum(rest[u] * rest[v] for u, v in E5)
        ES = m - eT
        lhs = Fraction(ES - ssz, 2)          # lower bound for cost(S)
        rhs = Fraction(2 * N * ssz - ssz * ssz, 25)
        margin = lhs - rhs
        if worst is None or margin < worst[0]:
            worst = (margin, s, ES, ssz)
        if lhs <= rhs:
            firing.append((s, ssz, ES, float(lhs), float(rhs)))
    return firing, worst


if __name__ == "__main__":
    print("=== calibration: balanced C5[t] ===")
    for t in range(1, 6):
        report([t] * 5, f"C5[{t}]")

    print()
    print("=== witness family W_t = C5[7t,2t,7t,7t,2t] ===")
    for t in range(1, 9):
        a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
        N, d, delta, b, m = report(a, f"W_{t}")
        assert delta * 25 == 4 * N, (delta, N)
        firing, worst = set_mechanism_check(a)
        print(f"    set-deletion mechanism: #firing S = {len(firing)}; "
              f"worst margin = {worst[0]} at s={worst[1]} (E(S)={worst[2]}, |S|={worst[3]})")
        if firing:
            print("      firing examples:", firing[:5])
