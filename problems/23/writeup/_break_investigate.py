"""Investigate the break-hunt 'failure': vblow_H?AFBo]_t2 N=18 side=011111111111000000 v=2 Lmax=7.

Questions:
 (Q1) Is this side an ACTUAL maximum cut?  (maxcut_ls_many may return non-global optima.)
 (Q2) If it is a max cut, does the FULL construction gate (search ALL lengths/orientations/pref/suff,
      take first neutral B-connected Gamma-decreasing) cover v=2?  i.e. is the failure only of the
      *L_max-specific* selector, or of the whole construction?
 (Q3) What does the L_max switch at v=2 look like (neutral? bconn? why does it fail)?
 (Q4) Confirm on the CANONICAL blowup cut (base[v//t]) that v's that ARE R<0 are L_max-covered.

Exact Fraction.
"""
from fractions import Fraction as F
from _h import dec, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


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


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def cutval(n, adj, side):
    return sum(1 for v in range(n) for w in adj[v] if w > v and side[v] != side[w])


def all_len_switches(v, M, ell, cyc):
    bylen = {}
    for f in M:
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(ell[f], []).append(list(Q))
    res = {}
    for L, rows in bylen.items():
        out = set()
        for orient in (0, 1):
            pref = set(); suff = set()
            for Q in rows:
                q = Q if orient == 0 else Q[::-1]
                i = q.index(v)
                pref.update(q[:i + 1])
                suff.update(q[i:])
            out.add(frozenset(pref)); out.add(frozenset(suff))
        res[L] = out
    return res


def analyze(name, n, adj, side):
    print("\n===", name, "side=", ''.join(map(str, side)))
    print("  cutval =", cutval(n, adj, side))
    # global max cut value
    gmax = max(cutval(n, adj, s) for s in maxcut_all(n, adj))
    print("  GLOBAL max cut value =", gmax, " -> this side is", "MAX" if cutval(n, adj, side) == gmax else "NOT MAX")
    if not Bconn(n, adj, side):
        print("  B not connected -> skip"); return
    st = struct_for_side(n, adj, side)
    if st is None:
        print("  struct None"); return
    M, ell, T, mu, cyc = st
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    neg = [v for v in range(n) if R[v] < 0]
    print("  R<0 vertices:", neg)
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        sw = all_len_switches(v, M, ell, cyc)
        Ls = sorted(sw.keys())
        Lmax = max(Ls)
        # which lengths give a neutral+bconn+drop switch?
        winning = []
        lmax_neu = lmax_bc = lmax_drop = False
        for L in Ls:
            for Sset in sw[L]:
                if v not in Sset or len(Sset) in (0, n):
                    continue
                neu = boundary_delta(n, adj, side, Sset) == 0
                if L == Lmax and neu:
                    lmax_neu = True
                if not neu:
                    continue
                bc = Bconn(n, adj, flip(side, Sset))
                if L == Lmax and bc:
                    lmax_bc = True
                if not bc:
                    continue
                g2 = gamma_of(n, adj, flip(side, Sset))
                if g2 is not None and g2 < gamma0:
                    if L not in winning:
                        winning.append(L)
                    if L == Lmax:
                        lmax_drop = True
        print("    v=%d R=%s lens-through-v=%s Lmax=%d | winning-lengths=%s | Lmax neutral=%s bconn=%s drop=%s"
              % (v, R[v], Ls, Lmax, sorted(winning), lmax_neu, lmax_bc, lmax_drop))


def main():
    hN, hE = dec("H?AFBo]")
    nn, EE = vertex_blowup(hN, hE, 2)
    adj = [set() for _ in range(nn)]
    for x, y in EE:
        adj[x].add(y); adj[y].add(x)
    # the break-hunt side
    s1 = [int(c) for c in "011111111111000000"]
    analyze("break-hunt cut", nn, adj, s1)
    # the canonical blowup cut used by the construction gate
    base = [int(c) for c in "111110000"]
    s2 = [base[v // 2] for v in range(nn)]
    analyze("canonical blowup cut (construction-gate)", nn, adj, s2)


if __name__ == "__main__":
    main()
