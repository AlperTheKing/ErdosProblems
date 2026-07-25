"""Q2_ledger.py -- EXACT integer ledger for the two calibration objects of the
Q2 discharging task:

  (1) C5[n]  (the extremal blow-up)              n = 1..6
  (2) W_b    = P4-blowup with parts (b+1,b,b,b+1) at its locally-maximal cut

Everything is exact integer / Fraction arithmetic.

Key structural lemma used (proved, not assumed):
    In a blow-up H[a] the mono-count of a cut, and the switching gain
        Delta(S) = -sum_{u in S} sigma(u) - 2 e_M(S) + 2 e_B(S)
    are MULTILINEAR in the counts s_i = |S cap part i| (parts are independent
    sets, so no s_i^2 term ever appears).  A multilinear function on a box
    attains its maximum at a corner.  Hence
      * maxcut(H[a]) is attained by a part-respecting cut, and
      * a part-respecting cut is a MAXIMUM cut  iff  Delta(S) <= 0 for the
        2^h part-subsets S.
    Both facts are used to certify maximality for all n / all b at once.
"""
from fractions import Fraction as Fr
from itertools import product

# ---------------------------------------------------------------- blow-up core

class Pattern:
    def __init__(self, h, edges, name):
        self.h = h
        self.edges = sorted(tuple(sorted(e)) for e in edges)
        self.name = name
        self.adj = [set() for _ in range(h)]
        for i, j in self.edges:
            self.adj[i].add(j)
            self.adj[j].add(i)

    def nedges(self, a):
        return sum(a[i] * a[j] for i, j in self.edges)

    def mono(self, a, col):
        return sum(a[i] * a[j] for i, j in self.edges if col[i] == col[j])

    def sigma(self, a, col):
        """sigma_i = d_B - d_M for a vertex of part i."""
        out = []
        for i in range(self.h):
            db = sum(a[j] for j in self.adj[i] if col[j] != col[i])
            dm = sum(a[j] for j in self.adj[i] if col[j] == col[i])
            out.append(db - dm)
        return out

    def degrees(self, a):
        return [sum(a[j] for j in self.adj[i]) for i in range(self.h)]

    def delta(self, a, col, s):
        """switching gain for S with s_i vertices from part i (exact)."""
        sig = self.sigma(a, col)
        val = -sum(s[i] * sig[i] for i in range(self.h))
        for i, j in self.edges:
            if col[i] == col[j]:
                val -= 2 * s[i] * s[j]
            else:
                val += 2 * s[i] * s[j]
        return val

    def bip(self, a):
        """min over part-respecting cuts (= true bip, by multilinearity)."""
        best = None
        for col in product((0, 1), repeat=self.h):
            m = self.mono(a, col)
            if best is None or m < best[0]:
                best = (m, col)
        return best

    def all_min_cuts(self, a):
        m0 = self.bip(a)[0]
        return [col for col in product((0, 1), repeat=self.h)
                if self.mono(a, col) == m0]

    def is_max_cut(self, a, col):
        """exact: check all 2^h corners."""
        bad = []
        for s_mask in product((0, 1), repeat=self.h):
            s = [a[i] if s_mask[i] else 0 for i in range(self.h)]
            d = self.delta(a, col, s)
            if d > 0:
                bad.append((s_mask, d))
        return (len(bad) == 0), bad

    def min_improving_switch(self, a, col):
        """exact brute force over all integer s in the box; returns
        (min |S| with Delta>0, argmin s, Delta)  or None."""
        best = None
        ranges = [range(ai + 1) for ai in a]
        for s in product(*ranges):
            d = self.delta(a, col, list(s))
            if d > 0:
                k = sum(s)
                if best is None or k < best[0]:
                    best = (k, s, d)
        return best


C5 = Pattern(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)], "C5")
P4 = Pattern(4, [(0, 1), (1, 2), (2, 3)], "P4")

# ---------------------------------------------------------------- charge model
# mu(v) = N - (25/2) d_M(v)   =>   sum_v mu(v) = N^2 - 25|M|


def charge_report(pat, a, col, label):
    h = pat.h
    N = sum(a)
    E = pat.nedges(a)
    M = pat.mono(a, col)
    B = E - M
    sig = pat.sigma(a, col)
    deg = pat.degrees(a)
    dM = [(deg[i] - sig[i]) // 2 if (deg[i] - sig[i]) % 2 == 0 else Fr(deg[i] - sig[i], 2)
          for i in range(h)]
    mu = [Fr(N) - Fr(25, 2) * dM[i] for i in range(h)]
    tot = sum(a[i] * mu[i] for i in range(h))
    assert tot == Fr(N * N - 25 * M), (tot, N * N - 25 * M)
    lines = []
    lines.append(f"  {label}: N={N} |E|={E} |M|={M} |B|={B}  25|M|={25*M} N^2={N*N} "
                 f"25|M|-N^2={25*M-N*N}")
    for i in range(h):
        lines.append(f"    part{i} size={a[i]:4d} d={deg[i]:4d} sigma={sig[i]:5d} "
                     f"d_M={dM[i]} mu={mu[i]}")
    return lines, dict(N=N, E=E, M=M, B=B, sigma=sig, deg=deg, dM=dM, mu=mu, tot=tot)


def switchstar_check(pat, a, col):
    """switch-star bound sigma(v) >= sum_{t in T}(2 - sigma(t)) over T subset N_B(v).
    Best T = all B-neighbours with sigma <= 1.  Report slack per part."""
    sig = pat.sigma(a, col)
    out = []
    for i in range(pat.h):
        rhs = 0
        for j in pat.adj[i]:
            if col[j] != col[i] and sig[j] <= 1:
                rhs += a[j] * (2 - sig[j])
        out.append((sig[i], rhs, sig[i] - rhs))
    return out


def star_plus_T(pat, a, col):
    """family (*)  S = N(v) u T,  T independent in H[a], T disjoint from N(v).
       Enumerates T as a sub-blow-up: t_j vertices from part j, j not in N(i),
       {j : t_j>0} independent in H.  Returns the most violated / tightest
       instance:  slack = -Delta(S)  (>=0 required at a max cut)."""
    h = pat.h
    res = []
    for i in range(h):
        Nv = sorted(pat.adj[i])
        cand = [j for j in range(h) if j not in pat.adj[i]]
        # choose an independent subset of cand
        best = None
        for mask in product((0, 1), repeat=len(cand)):
            sel = [cand[k] for k in range(len(cand)) if mask[k]]
            ok = True
            for x in range(len(sel)):
                for y in range(x + 1, len(sel)):
                    if sel[y] in pat.adj[sel[x]]:
                        ok = False
            if not ok:
                continue
            for tmul in product(*[range(0, a[j] + 1) for j in sel]):
                s = [0] * h
                for j in Nv:
                    s[j] = a[j]
                for k, j in enumerate(sel):
                    s[j] = tmul[k]
                d = pat.delta(a, col, s)
                if best is None or d > best[0]:
                    best = (d, tuple(s))
        res.append((i, best))
    return res


def hdr(t):
    return "\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78


def main():
    L = []
    # ---------------------------------------------------------- 1. C5[n]
    L.append(hdr("1.  C5[n]  ledger, n = 1..6   (target: 25|M| = N^2 exactly)"))
    for n in range(1, 7):
        a = [n] * 5
        m0, col0 = C5.bip(a)
        mincuts = C5.all_min_cuts(a)
        L.append(f"\n C5[{n}]: bip = {m0}   (N^2/25 = {(5*n)**2}/25 = {(5*n)**2//25})"
                 f"   #part-cuts attaining it = {len(mincuts)}")
        for col in mincuts:
            ok, bad = C5.is_max_cut(a, col)
            lines, D = charge_report(C5, a, col, f"cut {''.join(map(str,col))}")
            L += lines
            L.append(f"    maximum-cut certificate (all 2^5 corners): {'PASS' if ok else 'FAIL '+str(bad)}")
            ss = switchstar_check(C5, a, col)
            L.append("    switch-star  sigma(v) >= sum_T (2-sigma):  " +
                     " | ".join(f"p{i}: {s} >= {r} slack {sl}" for i, (s, r, sl) in enumerate(ss)))
            st = star_plus_T(C5, a, col)
            L.append("    family (*) S=N(v)uT   max Delta (must be <=0, =0 means TIGHT):")
            for i, best in st:
                L.append(f"       v in part{i}: max Delta = {best[0]}  at s={best[1]}")
            break  # one representative cut is enough (others are rotations)

    # ---------------------------------------------------------- 2. W_b
    L.append(hdr("2.  W_b = P4[b+1,b,b,b+1]  ledger, b = 1..12"))
    for b in range(1, 13):
        a = [b + 1, b, b, b + 1]
        N = sum(a)
        m0, col0 = P4.bip(a)
        L.append(f"\n W_{b}: N={N} parts={a}  bip={m0} (P4 is bipartite)")
        # enumerate ALL part-cuts, find the locally maximal ones
        for col in product((0, 1), repeat=4):
            if col[0] == 1:
                continue  # fix part0 on side 0 (complement symmetry)
            M = P4.mono(a, col)
            sig = P4.sigma(a, col)
            if min(sig) < 0:
                continue
            ok, bad = P4.is_max_cut(a, col)
            tag = "MAXIMUM" if ok else "local-only"
            L.append(f"   cut {''.join(map(str,col))}: |M|={M} sigma={sig} 25|M|-N^2={25*M-N*N} [{tag}]")
            if not ok and 25 * M > N * N:
                lines, D = charge_report(P4, a, col, "  ->")
                L += lines
                ss = switchstar_check(P4, a, col)
                L.append("      switch-star slacks: " +
                         " | ".join(f"p{i}: {s}>={r} slack {sl}" for i, (s, r, sl) in enumerate(ss)))
                if b <= 24:
                    mis = P4.min_improving_switch(a, col)
                    L.append(f"      MIN IMPROVING SWITCH: |S|={mis[0]} s={mis[1]} Delta={mis[2]} "
                             f"ratio |S|/N = {Fr(mis[0],N)} = {float(Fr(mis[0],N)):.4f}")
                st = star_plus_T(P4, a, col)
                L.append("      family (*) S=N(v)uT  max Delta (>0 means (*) REFUTES this cut):")
                for i, best in st:
                    L.append(f"         v in part{i}: max Delta = {best[0]} at s={best[1]}")
    print("\n".join(L))


if __name__ == "__main__":
    main()
