"""Census: for how many triangle-free graphs does ANY fixed cut certificate survive?

By THEOREM R8-2 (rigidity) the support of a working fixed certificate -- under
the arithmetic mean, any weighted geometric mean, any power mean, or the Gibbs
free-energy aggregator at any beta -- must consist of RAINBOW-1 cuts: cuts whose
monochromatic edge set meets every induced C5 of H exactly once.  Write R(H) for
that set.  Then the best conceivable fixed certificate is  min_{S in R} m_S, so

    a fixed certificate exists for H   <=>   max_a min_{S in R(H)} m_S(a) <= 1/25
                                             (a on the simplex).

This script reads graph6 on stdin, and for each connected triangle-free graph
containing an induced C5 decides:

    DEAD-0   R(H) = empty                        (no admissible cut at all)
    DEAD-*   a weighting a with min_{S in R} m_S(a) > (sum a)^2/25 is found
             (verified exactly in integer arithmetic)
    ALIVE    neither

The star test (THEOREM R8-4) is used as the primary exact kill: if some vertex v
meets every S in R -- i.e. every rainbow-1 cut has a monochromatic edge at v --
put weight 1/2 on v and spread 1/2 over N(v) by the optimal fractional strategy;
since N(v) is independent (triangle-freeness) the support induces a star and
    min_{S in R} m_S = (1/4) * max_l min_S l(D_S) = 1/(4 tau*)   with tau* <= |R|.
So |R| <= 6 plus "v meets every S in R" already gives 1/24 > 1/25.
"""

import sys
from fractions import Fraction
from itertools import combinations


def g6_decode(s):
    s = s.strip()
    if not s:
        return None
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for d in data[1:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    E, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                E.append((i, j))
            idx += 1
    return n, E


def analyse(n, E):
    m = len(E)
    eidx = {e: i for i, e in enumerate(E)}
    adj = [[False] * n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = True
    # triangle-free?
    for (u, v) in E:
        for w in range(n):
            if adj[u][w] and adj[v][w]:
                return None
    # induced C5s as edge bitmasks
    pmasks = []
    for S in combinations(range(n), 5):
        if any(sum(1 for u in S if adj[v][u]) != 2 for v in S):
            continue
        seen, st = {S[0]}, [S[0]]
        while st:
            v = st.pop()
            for u in S:
                if adj[v][u] and u not in seen:
                    seen.add(u)
                    st.append(u)
        if len(seen) != 5:
            continue
        msk = 0
        for (u, v) in combinations(S, 2):
            if adj[u][v]:
                msk |= 1 << eidx[(u, v)]
        pmasks.append(msk)
    if not pmasks:
        return None                      # no induced C5: rigidity test empty
    # rainbow-1 cuts
    R = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        mono = 0
        for i, (u, v) in enumerate(E):
            if side[u] == side[v]:
                mono |= 1 << i
        if all(bin(mono & p).count("1") == 1 for p in pmasks):
            R.append(mono)
    return pmasks, R


def frac_cover(sets, ground):
    """Exact fractional cover number of a hypergraph via its (small) LP,
    computed as the integral optimum when it coincides, else by LP.
    Here we only need an UPPER bound, so return the integral cover number."""
    best = len(ground) + 1
    gs = sorted(ground)
    for r in range(1, len(gs) + 1):
        for C in combinations(gs, r):
            cs = set(C)
            if all(cs & S for S in sets):
                return r
        if r >= best:
            break
    return best


def star_kill(n, E, R):
    """Return (v, tau_upper) if the star obstruction applies, else None."""
    inc = [[] for _ in range(n)]
    for i, (u, v) in enumerate(E):
        inc[u].append((i, v))
        inc[v].append((i, u))
    for v in range(n):
        Ds = []
        ok = True
        for mono in R:
            D = set(w for (i, w) in inc[v] if (mono >> i) & 1)
            if not D:
                ok = False
                break
            Ds.append(D)
        if not ok:
            continue
        ground = set().union(*Ds)
        tau = frac_cover(Ds, ground)
        if Fraction(1, 4 * tau) > Fraction(1, 25):
            return v, tau
    return None


if __name__ == "__main__":
    counts = {}
    alive_examples = []
    dead0 = deadstar = alive = total = 0
    for line in sys.stdin:
        dec = g6_decode(line)
        if dec is None:
            continue
        n, E = dec
        res = analyse(n, E)
        if res is None:
            continue
        pmasks, R = res
        total += 1
        deg = [sum(1 for e in E if v in e) for v in range(n)]
        if not R:
            dead0 += 1
            key = "DEAD-0"
        else:
            sk = star_kill(n, E, R)
            if sk:
                deadstar += 1
                key = "DEAD-star"
            else:
                alive += 1
                key = "ALIVE"
                if len(alive_examples) < 40:
                    alive_examples.append((line.strip(), n, len(E),
                                           len(R), min(deg), max(deg)))
        counts[(n, key)] = counts.get((n, key), 0) + 1
    print(f"graphs with an induced C5 : {total}")
    print(f"  DEAD-0    (R = empty)   : {dead0}")
    print(f"  DEAD-star (star kill)   : {deadstar}")
    print(f"  ALIVE                   : {alive}")
    for k in sorted(counts):
        print(f"    n={k[0]:2d} {k[1]:10s} {counts[k]}")
    print("\nALIVE examples (g6, n, |E|, |R|, delta, Delta):")
    for e in alive_examples:
        print("   ", e)
