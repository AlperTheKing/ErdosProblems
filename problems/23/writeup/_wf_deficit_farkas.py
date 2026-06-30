"""GATE: GPT-Pro's CLOSING deficit-aware (LOAD-based) uniform Farkas certificate for Erdos #23, L=5.

Prior SIZE-based generator cone was INFEASIBLE (glued C5|C7 row unreachable). Fix = LOAD-based
generators: add the five product-slacks (h_i h_{i+1} - q), i=0..4, alongside dGamma(U) (gamma-min,
neutral connected switches) and (delta_B(W)-delta_M(W)) (max-cut).

Target (per L=5 row): 25*M(P) = 5*(N^2-Gamma) - 25*sum_i(T[x_i]-N) - S^2 + 25*q   (exact Fraction)
  with h_i=T[x_i]/N, S=sum h_i, q=min_{i mod5} h_i h_{i+1}, Gamma=sum_v T[v].
Goal ineq M(P)>=0.  Certificate: 25*M = sum alpha_U dGamma(U) + sum beta_W (dB(W)-dM(W))
                                       + sum_i lambda_i (h_i h_{i+1} - q),  all coeffs UNIFORM >=0.

Generators are POSITION-INDEXED (same formula slot across all rows). Solve uniform conic-membership
LP exists lambda>=0 with G lambda = b on ALL rows; then VERIFY exactly in Fraction.

Run from E:/Projects/ErdosProblems/problems/23/writeup with: python _wf_deficit_farkas.py
"""
from fractions import Fraction as F
from collections import deque
import itertools
import numpy as np
from scipy.optimize import linprog

from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

INF = 10**9

# ----------------------------------------------------------------------------
# Gamma on a (possibly flipped) side via struct_for_side; None if invalid.
# ----------------------------------------------------------------------------
def gamma_of(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    # require every bad edge has a blue geodesic (struct returns None otherwise) -> ok
    return sum(T)

def deltas(n, adj, side, W):
    """delta_B(W)=#cut(blue) edges with exactly one endpoint in W; delta_M(W)=#bad(same-side) edges
       with exactly one endpoint in W.  W a set of vertices."""
    dB = 0; dM = 0
    for u in range(n):
        for v in adj[u]:
            if v <= u: continue
            inW = (u in W) ^ (v in W)
            if not inW: continue
            if side[u] != side[v]: dB += 1
            else: dM += 1
    return dB, dM

# ----------------------------------------------------------------------------
# Build all L=5 rows over gamma-min connected-B global-max cuts.
# Each row: target b (Fraction) and the position-indexed generator vector (list of Fractions).
# ----------------------------------------------------------------------------
# Generator layout (uniform / position-indexed):
#  A. dGamma single on-path vertex x_j flip, neutral+connected   : 5 slots (j=0..4)
#  B. dGamma pair {x_j,x_k} flip, neutral+connected              : 10 slots (j<k)
#  C. dGamma pair {x_j, off-path blue-neighbor m_j} flip         : 5 slots (j=0..4) [first blue nbr off path]
#  D. (dB-dM) single path vertex x_j                             : 5 slots
#  E. (dB-dM) path interval [j..k] (contiguous along P)          : 10 slots (j<k)  -- intervals incl j..k
#  F. (dB-dM) layer set Lambda_i (B-distance-i layer from x0)    : up to 5 slots (i=0..4)
#  G. product-slack (h_i h_{i+1} - q)                            : 5 slots (i=0..4)  <-- LOAD-based fix
GEN_LABELS = []
for j in range(5): GEN_LABELS.append(("A.dGam.v%d" % j))
for j in range(5):
    for k in range(j+1,5): GEN_LABELS.append(("B.dGam.pair%d%d" % (j,k)))
for j in range(5): GEN_LABELS.append(("C.dGam.mate%d" % j))
for j in range(5): GEN_LABELS.append(("D.dBdM.v%d" % j))
for j in range(5):
    for k in range(j+1,5): GEN_LABELS.append(("E.dBdM.int%d-%d" % (j,k)))
for i in range(5): GEN_LABELS.append(("F.dBdM.layer%d" % i))
for i in range(5): GEN_LABELS.append(("G.prodslack%d" % i))
NGEN = len(GEN_LABELS)

def layers_from(adj, side, src, n):
    """B-distance layers (blue BFS) from src."""
    d = {src: 0}; q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u]+1; q.append(v)
    lay = {}
    for v, dd in d.items(): lay.setdefault(dd, set()).add(v)
    return lay

def flip(side, S):
    s2 = side[:]
    for v in S: s2[v] ^= 1
    return s2

def build_rows_for_cut(n, adj, side, name):
    """For one gamma-min connected-B cut, emit one row per (bad edge f with ell_f=5, geodesic P)."""
    st = struct_for_side(n, adj, side)
    if st is None: return []
    M, ell, T, mu, cyc = st
    N = F(n)
    Gamma = sum(T)
    Gamma0 = Gamma
    rows = []
    for f in M:
        if ell[f] != 5: continue
        for P in cyc[f]:
            if len(P) != 5: continue
            x = P  # x0..x4
            # loads / h / S / q
            h = [T[x[i]]/N for i in range(5)]
            S = sum(h)
            prods = [h[i]*h[(i+1) % 5] for i in range(5)]
            q = min(prods)
            # target 25*M
            b = 5*(N*N - Gamma) - 25*sum(T[x[i]] - N for i in range(5)) - S*S + 25*q
            # ---- generator vector ----
            g = [F(0)] * NGEN
            idx = 0
            # A. single on-path vertex flips
            for j in range(5):
                v = x[j]
                s2 = flip(side, [v])
                if Bconn(n, adj, s2):
                    dB, dM = deltas(n, adj, side, {v})
                    if dB == dM:  # neutral
                        g1 = gamma_of(n, adj, s2)
                        if g1 is not None:
                            g[idx] = g1 - Gamma0
                idx += 1
            # B. pair {x_j,x_k}
            for j in range(5):
                for k in range(j+1,5):
                    Wset = {x[j], x[k]}
                    s2 = flip(side, Wset)
                    if Bconn(n, adj, s2):
                        dB, dM = deltas(n, adj, side, Wset)
                        if dB == dM:
                            g1 = gamma_of(n, adj, s2)
                            if g1 is not None:
                                g[idx] = g1 - Gamma0
                    idx += 1
            # C. pair {x_j, first off-path blue neighbor m_j}
            Pset = set(x)
            for j in range(5):
                v = x[j]
                mate = None
                for w in sorted(adj[v]):
                    if side[w] != side[v] and w not in Pset:
                        mate = w; break
                if mate is not None:
                    Wset = {v, mate}
                    s2 = flip(side, Wset)
                    if Bconn(n, adj, s2):
                        dB, dM = deltas(n, adj, side, Wset)
                        if dB == dM:
                            g1 = gamma_of(n, adj, s2)
                            if g1 is not None:
                                g[idx] = g1 - Gamma0
                idx += 1
            # D. (dB-dM) single path vertex
            for j in range(5):
                dB, dM = deltas(n, adj, side, {x[j]})
                g[idx] = F(dB - dM); idx += 1
            # E. (dB-dM) contiguous interval [j..k] along P
            for j in range(5):
                for k in range(j+1,5):
                    Wset = set(x[j:k+1])
                    dB, dM = deltas(n, adj, side, Wset)
                    g[idx] = F(dB - dM); idx += 1
            # F. (dB-dM) layer sets Lambda_i (blue BFS layers from x0)
            lay = layers_from(adj, side, x[0], n)
            for i in range(5):
                Wset = lay.get(i, set())
                if Wset:
                    dB, dM = deltas(n, adj, side, Wset)
                    g[idx] = F(dB - dM)
                idx += 1
            # G. product-slacks (h_i h_{i+1} - q)
            for i in range(5):
                g[idx] = prods[i] - q; idx += 1
            assert idx == NGEN
            rows.append(dict(name=name, f=f, P=tuple(x), b=b, g=g, N=n,
                             Gamma=Gamma0, S=S, q=q, h=h))
    return rows

def collect_rows(name, n, E):
    adj, cuts = gmins(n, E)
    rows = []
    for side in cuts:
        rows += build_rows_for_cut(n, adj, side, name)
    return rows

# ----------------------------------------------------------------------------
# Witness families
# ----------------------------------------------------------------------------
def odd_blowup(m, sizes):
    nn = sum(sizes); start = [0]*m
    for i in range(1, m): start[i] = start[i-1] + sizes[i-1]
    adj = [set() for _ in range(nn)]; E = []
    for i in range(m):
        j = (i+1) % m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                u = start[i]+a; v = start[j]+b; E.append((u, v))
    return nn, E

def families():
    fams = []
    import subprocess
    from _h import GENG
    # census N<=10 triangle-free connected
    for nn in range(5, 11):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); fams.append(("cen%s" % g6, n, E))
    # theta-witnesses (small g6 from the writeup state)
    for g6 in ["G?Fw", "G?bFw", "G?rFw", "H?AFBo]"]:
        try:
            n, E = dec(g6); fams.append(("thw-%s" % g6, n, E))
        except Exception:
            pass
    # uniform C5[t], t=1..3
    for t in (1, 2, 3):
        n, E = odd_blowup(5, [t]*5); fams.append(("C5[%d]" % t, n, E))
    # nonuniform C5
    for sizes in [(2,1,2,1,2), (3,2,3,2,3), (2,1,2,1,3)]:
        n, E = odd_blowup(5, list(sizes)); fams.append(("C5%s" % (sizes,), n, E))
    # glued C5|C7 (the prior Farkas KILLER) -- bridge edge x0(C5)-y0(C7)
    n5, E5 = 5, Cn(5); n7, E7 = 7, Cn(7)
    n, E = union_disjoint((n5, E5), (n7, E7)); E = E + [(0, n5)]  # bridge
    fams.append(("glue_C5|C7", n, E))
    # also a glued C5|C7 with no bridge (disjoint) as control
    n, E = union_disjoint((n5, E5), (n7, E7)); fams.append(("disj_C5+C7", n, E))
    # C7|Grotzsch (Grotzsch = mycielski(C5))
    grN, grE = mycielski(5, Cn(5))
    n, E = union_disjoint((7, Cn(7)), (grN, grE)); E = E + [(0, 7)]
    fams.append(("glue_C7|Grotzsch", n, E))
    return fams

# ----------------------------------------------------------------------------
# Solve uniform conic-membership LP, then exact verify.
# ----------------------------------------------------------------------------
def solve(rows):
    R = len(rows)
    A = np.array([[float(rows[r]['g'][c]) for c in range(NGEN)] for r in range(R)], float)
    b = np.array([float(rows[r]['b']) for r in range(R)], float)
    # feasibility: exists lambda>=0 with A lambda = b. Minimize 0 s.t. equality + bounds.
    # Use phase-1: min sum of artificials.  Simpler: linprog with equality and a tiny obj.
    c = np.zeros(NGEN)
    res = linprog(c, A_eq=A, b_eq=b, bounds=[(0, None)]*NGEN, method="highs")
    return res, A, b

def exact_verify(rows, lam):
    """lam: list of Fractions. Check A lam == b exactly on every row."""
    bad = []
    for r, row in enumerate(rows):
        lhs = sum(row['g'][c]*lam[c] for c in range(NGEN))
        if lhs != row['b']:
            bad.append((r, row['name'], float(lhs - row['b'])))
    return bad

def rationalize(x, maxden=10000):
    return F(x).limit_denominator(maxden)

def main():
    print("Collecting L=5 rows over gamma-min connected-B global-max cuts...", flush=True)
    rows = []
    for (name, n, E) in families():
        try:
            rs = collect_rows(name, n, E)
        except Exception as ex:
            print("  [skip %s: %s]" % (name, ex)); rs = []
        if rs:
            print("  %-22s -> %d L=5 rows (N=%d)" % (name, len(rs), n), flush=True)
        rows += rs
    print("TOTAL L=5 rows: %d ; generators: %d" % (len(rows), NGEN), flush=True)
    if not rows:
        print("NO ROWS"); return

    # dedup identical (b,g) rows to shrink LP
    seen = {}; ded = []
    for row in rows:
        key = (row['b'], tuple(row['g']))
        if key not in seen:
            seen[key] = 1; ded.append(row)
    print("Distinct (b,g) rows: %d" % len(ded), flush=True)

    res, A, b = solve(ded)
    print("\nLP status:", res.message, "| success:", res.success, flush=True)
    if not res.success:
        # INFEASIBLE: extract Farkas dual missing-generator direction.
        # min 0 infeasible => find y with y^T A <= 0 (componentwise, since lambda>=0) and y^T b > 0.
        # Solve: max y^T b s.t. A^T y <= 0, -1<=y<=1 (bounded).
        R = A.shape[0]
        cc = -b  # maximize b^T y == minimize -b^T y
        Aub = A.T  # (NGEN x R): A^T y <= 0
        bub = np.zeros(NGEN)
        res2 = linprog(cc, A_ub=Aub, b_ub=bub, bounds=[(-1, 1)]*R, method="highs")
        y = res2.x if res2.success else None
        print("Farkas dual (max b^T y s.t. A^T y<=0, |y|<=1):", res2.message,
              "obj=", -res2.fun if res2.success else None, flush=True)
        if y is not None:
            # which rows carry the certificate of infeasibility
            heavy = sorted(range(R), key=lambda r: -abs(y[r]))[:8]
            print("  dominant rows in Farkas direction (idx,name,y,b):")
            for r in heavy:
                print("    r=%d %-18s y=%+.4f b=%.4f" % (r, ded[r]['name'], y[r], ded[r]['b']))
            # generator-side residual A^T y : the 'missing generator' directions = most-negative slacks (none can absorb)
            resid = A.T.dot(y)
            print("  A^T y (should be <=0 for valid Farkas); min/max:", resid.min(), resid.max())
            # report whether glued rows are the obstruction
            gl = [r for r in range(R) if 'glue' in ded[r]['name']]
            if gl:
                print("  glued-row y values:", [(ded[r]['name'], round(float(y[r]),4)) for r in gl])
        print("\nRESULT: cone INFEASIBLE even with LOAD-based product-slacks.")
        return res, ded, A, b, None

    # FEASIBLE (float). Rationalize and verify exactly.
    lam_f = res.x
    lam = [rationalize(v) for v in lam_f]
    bad = exact_verify(ded, lam)
    if not bad:
        support = [(GEN_LABELS[c], lam[c]) for c in range(NGEN) if lam[c] != 0]
        print("\nEXACT-VERIFIED uniform certificate. Support (%d generators):" % len(support))
        for lab, v in support:
            print("    %-18s = %s (%.4f)" % (lab, v, float(v)))
        # classify families exercised
        print("RESULT: cone FEASIBLE, EXACT certificate found.")
        return res, ded, A, b, lam
    else:
        print("\nFloat-LP feasible but rationalized lambda FAILS exact check on %d rows (first 5):" % len(bad))
        for r, nm, d in bad[:5]:
            print("    r=%d %-18s resid=%.3e" % (r, nm, d))
        print("RESULT: float-feasible, exact-verification FAILED (rationalization mismatch).")
        return res, ded, A, b, None

if __name__ == "__main__":
    main()
