"""GPT-Pro closing diagnostic (route A): does the mixed five-shadow slack Q_mix(phi)
   break the exact Farkas dual y=(-1,1/2,1/2) on the minimal 3-row core?

   Q_mix(phi) = Gamma - 25 * min_i [ n_i(phi) * w_{i+1}(phi) ]      (cyclic i mod 5)
     n_i = #{v: phi(v)=i},  w_i = (1/N) * sum_{v: phi(v)=i} T(v),
     Sum n_i = N, Sum w_i = Gamma/N.  Nonneg by AM-GM; 0 at balanced C5 shadow.
   Five-shadow map phi: V->Z5 with phi(x_i)=i on the path P; enumerate all 5^(N-5) extensions.

   3-row core (from _wf_deficit_farkas, exact dual y=(-1,1/2,1/2)):
     R0 = cenECxo  N=6 P=(3,0,4,1,5)  b=34145/144
     R1 = cenF?bBo N=7 P=(4,0,5,1,6)  b=370
     R2 = cenF?bBo N=7 P=(0,4,6,1,5)  b=370
   Old generators all have y.G <= 0 while y.b > 0.  Q_mix repairs iff some column has y.Q_mix > 0.
   ALL exact Fraction.
"""
import itertools
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins

CORE = [("ECxo", 6, (3,0,4,1,5), F(34145,144)),
        ("F?bBo", 7, (4,0,5,1,6), F(370)),
        ("F?bBo", 7, (0,4,6,1,5), F(370))]

def find_row(g6, n, Ptarget, btarget):
    """Locate the gamma-min cut + bad edge whose geodesic == Ptarget; return (adj, side, T, Gamma)."""
    nn, E = dec(g6)
    assert nn == n, (g6, nn, n)
    adj, cuts = gmins(n, E)
    for side in cuts:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st
        N = F(n); Gamma = sum(T)
        for f in M:
            if ell[f] != 5: continue
            for P in cyc[f]:
                if tuple(P) != tuple(Ptarget): continue
                x = P
                h = [T[x[i]]/N for i in range(5)]
                S = sum(h); q = min(h[i]*h[(i+1)%5] for i in range(5))
                b = 5*(N*N-Gamma) - 25*sum(T[x[i]]-N for i in range(5)) - S*S + 25*q
                if b == btarget:
                    return adj, side, T, Gamma, tuple(x)
    return None

def bluedist(n, adj, side, src):
    from collections import deque
    d = {src: 0}; dq = deque([src])
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u]+1; dq.append(v)
    return d

def qmix_of_phi(n, T, Gamma, phi):
    N = F(n); ncnt = [0]*5; wsum = [F(0)]*5
    for v in range(n):
        c = phi[v]; ncnt[c] += 1; wsum[c] += T[v]
    w = [wsum[i]/N for i in range(5)]
    mn = min(F(ncnt[i])*w[(i+1)%5] for i in range(5))
    return Gamma - 25*mn

def canonical_qmix(n, adj, side, T, Gamma, path):
    """Canonical blue-distance shadow: phi(v) = bluedist(x0, v) mod 5 (gives phi(x_i)=i on geodesic)."""
    d = bluedist(n, adj, side, path[0])
    if any(v not in d for v in range(n)): return None  # disconnected blue (shouldn't happen, connected-B)
    phi = {v: d[v] % 5 for v in range(n)}
    # sanity: phi(x_i)=i
    for i in range(5):
        if phi[path[i]] != i: return ("BADSHADOW", phi)
    return qmix_of_phi(n, T, Gamma, phi)

def qmix_values(n, T, Gamma, path):
    """All Q_mix(phi) over phi: V->Z5 with phi(x_i)=i; return sorted distinct list (exact)."""
    N = F(n)
    fixed = {path[i]: i for i in range(5)}
    free = [v for v in range(n) if v not in fixed]
    vals = set()
    for assign in itertools.product(range(5), repeat=len(free)):
        phi = dict(fixed)
        for v, c in zip(free, assign): phi[v] = c
        ncnt = [0]*5
        wsum = [F(0)]*5
        for v in range(n):
            c = phi[v]; ncnt[c] += 1; wsum[c] += T[v]
        w = [wsum[i]/N for i in range(5)]
        mn = min(F(ncnt[i])*w[(i+1)%5] for i in range(5))
        Q = Gamma - 25*mn
        vals.add(Q)
    return sorted(vals)

def main():
    rows = []
    for (g6, n, P, b) in CORE:
        r = find_row(g6, n, P, b)
        if r is None:
            print("FAILED to locate row", g6, n, P, b); return
        adj, side, T, Gamma, x = r
        vals = qmix_values(n, T, Gamma, x)
        can = canonical_qmix(n, adj, side, T, Gamma, x)
        rows.append((g6, n, x, Gamma, vals, can))
        print("%s N=%d P=%s Gamma=%s  Q_mix: min=%s max=%s  canonical(bluedist)=%s  (#distinct=%d)"
              % (g6, n, x, str(Gamma), str(vals[0]), str(vals[-1]), str(can), len(vals)))
    # exact dual y = (-1, 1/2, 1/2); column = (Qmix(r0), Qmix(r1), Qmix(r2)) over INDEPENDENT phi
    y = [F(-1), F(1,2), F(1,2)]
    # best achievable y.Q over independent per-row choices:
    best = y[0]*rows[0][4][0] + y[1]*rows[1][4][-1] + y[2]*rows[2][4][-1]  # min row0, max row1, row2
    print("="*60)
    print("min Q_mix(row0) =", str(rows[0][4][0]), " (0 means balanced shadow exists)")
    print("max Q_mix(row1) =", str(rows[1][4][-1]))
    print("max Q_mix(row2) =", str(rows[2][4][-1]))
    print("BEST y.Q_mix (indep per-row) =", str(best), "=", float(best))
    if best > 0:
        print(">>> DUAL BROKEN (indep phi): a mixed-shadow column has y.Q_mix > 0.")
    else:
        print(">>> DUAL NOT BROKEN by Q_mix (indep).")
    # canonical single-rule (uniform) column:
    cans = [rows[r][5] for r in range(3)]
    if all(isinstance(c, F) for c in cans):
        yc = y[0]*cans[0] + y[1]*cans[1] + y[2]*cans[2]
        print("canonical blue-dist shadow column = (%s, %s, %s); y.Q_mix_canonical = %s = %s"
              % (str(cans[0]), str(cans[1]), str(cans[2]), str(yc), float(yc)))
        print(">>> CANONICAL UNIFORM RULE breaks dual" if yc > 0 else ">>> canonical rule does NOT break dual (need richer shadow family)")

if __name__ == "__main__":
    main()
