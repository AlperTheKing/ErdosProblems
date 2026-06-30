"""FOCUSED exact probe of the (LB) failure site found by _lb_counterhunt.py:
   graph = vertex t=2 blowup of H?AFBo], cut side = 101111111111000000, v=2, R=-4, mixed lens (5,7).

Settle EXACTLY:
 (1) is this side a genuine MAX cut of the blowup graph?  (maxcut value == best)
 (2) connected-B?
 (3) independently recompute T, K2, R -> confirm R[2] == -4 (Fraction)
 (4) does the LENGTH-BUNDLE family contain a neutral B-conn Gamma-DECREASING switch through v=2?  (enumerate)
 (5) does ANY neutral B-connected switch decrease Gamma?  Brute over:
     (a) all connected B-geodesic-based vertex subsets the length-bundle family yields (already in 4),
     (b) ALL subsets containing v=2 of size <= 6 with delta_B=delta_M (neutral) and B-conn-after, recompute Gamma.
   If (5) finds a Gamma-drop -> the length-bundle SELECTOR is incomplete (LB-spirit survives, family too narrow).
   If (5) finds NONE -> this cut admits NO neutral Gamma-decreasing switch at v=2: the descent contradiction
     for gamma-min cannot be derived at this vertex via neutral switches. BUT: is this cut gamma-min?  Report Gamma
     vs the gamma-min Gamma of the graph (if NOT gamma-min, no contradiction is REQUIRED -- it's off the LB hypothesis
     only in spirit; the LB statement as written still quantifies over all max cuts, so a true 'no switch' is a BREAK).

Exact Fraction.  Run: python _lb_site_probe.py
"""
import itertools
from fractions import Fraction as F
from _h import dec, Bconn, maxcut_all, bdist_restr, geos
from _satzmu_conn import struct_for_side
from _csmspec import build_K2


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def cut_value(n, adj, side):
    return sum(1 for u in range(n) for w in adj[u] if w > u and side[u] != side[w])


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def boundary_delta(n, adj, side, Sset):
    dB = dM = 0
    for u in Sset:
        for w in adj[u]:
            if w in Sset:
                continue
            if side[u] != side[w]:
                dB += 1
            else:
                dM += 1
    return dB - dM


def lenbundle_switches(v, M, ell, cyc):
    bylen = {}
    for f in M:
        L = ell[f]
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(L, []).append(list(Q))
    out = set()
    for L, rows in bylen.items():
        for orient in (0, 1):
            pref = set(); suff = set()
            for Q in rows:
                q = Q if orient == 0 else Q[::-1]
                i = q.index(v)
                pref.update(q[:i + 1])
                suff.update(q[i:])
            out.add(frozenset(pref))
            out.add(frozenset(suff))
    return out


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


def main():
    hN, hE = dec("H?AFBo]")
    n, E = vertex_blowup(hN, hE, 2)
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    side = [int(c) for c in "101111111111000000"]
    assert len(side) == n, (len(side), n)

    # (1) max cut?
    val = cut_value(n, adj, side)
    best = max(cut_value(n, adj, s) for s in maxcut_all(n, adj))
    print("(1) cut value = %d ; graph maxcut value = %d ; IS-MAX-CUT = %s" % (val, best, val == best))

    # (2) connected-B?
    bc = Bconn(n, adj, side)
    print("(2) B-connected = %s" % bc)

    # (3) recompute T, K2, R
    st = struct_for_side(n, adj, side)
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    neg = [v for v in range(n) if R[v] < 0]
    gamma0 = sum(ell[f] ** 2 for f in M)
    print("(3) N=%d |M|=%d Gamma0=%d ; lens=%s" % (n, len(M), gamma0, sorted(set(ell.values()))))
    print("    R = %s" % [int(R[v]) if R[v].denominator == 1 else str(R[v]) for v in range(n)])
    print("    neg vertices = %s ; R[2] = %s" % (neg, R[2]))

    # (4) length-bundle family through v=2
    v = 2
    fam = lenbundle_switches(v, M, ell, cyc)
    print("(4) length-bundle switches through v=%d: %d candidates" % (v, len(fam)))
    found_lb = None
    for Sset in fam:
        if v not in Sset or len(Sset) == 0 or len(Sset) == n:
            continue
        if boundary_delta(n, adj, side, Sset) != 0:
            continue
        s2 = flip(side, Sset)
        g2 = gamma_of(n, adj, s2)
        if g2 is not None and g2 < gamma0:
            found_lb = (sorted(Sset), int(gamma0 - g2))
            break
    print("    length-bundle neutral B-conn Gamma-DROP switch: %s" % (found_lb if found_lb else "NONE"))

    # (5) ANY neutral B-conn Gamma-decreasing switch through v=2, brute |S|<=6
    print("(5) brute search: neutral B-conn Gamma-decreasing switch through v=2, |S|<=6 ...")
    others = [u for u in range(n) if u != v]
    found_any = None
    checked = 0
    for k in range(0, 6):  # size = 1 + k
        for combo in itertools.combinations(others, k):
            Sset = frozenset((v,) + combo)
            checked += 1
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, list(Sset))
            if not Bconn(n, adj, s2):
                continue
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                found_any = (sorted(Sset), int(gamma0 - g2))
                break
        if found_any:
            break
    print("    checked %d subsets; ANY neutral B-conn Gamma-DROP switch (|S|<=6): %s"
          % (checked, found_any if found_any else "NONE"))

    # (6) is this cut gamma-min for the graph? (compare against min Gamma over all connected-B max cuts)
    gmins = []
    for s in maxcut_all(n, adj):
        g = gamma_of(n, adj, s)
        if g is not None:
            gmins.append(g)
    gm = min(gmins) if gmins else None
    print("(6) this cut Gamma=%d ; min Gamma over all connected-B max cuts = %s ; this-cut-is-gamma-min = %s"
          % (gamma0, gm, gamma0 == gm))

    # verdict logic
    print("=" * 64)
    if found_any:
        print("RESULT: length-bundle family MISSED a valid neutral Gamma-drop switch -> SELECTOR too narrow, "
              "(LB)-SPIRIT survives (descent witness exists, just not length-bundle).  drop=%s S=%s"
              % (found_any[1], found_any[0]))
    elif found_lb:
        print("RESULT: length-bundle switch DOES cover this site (hunt's break must be re-examined).  drop=%s"
              % (found_lb[1],))
    else:
        print("RESULT: NO neutral B-conn Gamma-decreasing switch through v=2 with |S|<=6 EXISTS at this R<0 site. "
              "If gamma-min=%s this is a TRUE (LB) BREAK." % (gamma0 == gm,))


if __name__ == "__main__":
    main()
