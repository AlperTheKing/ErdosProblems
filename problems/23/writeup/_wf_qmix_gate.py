"""DECISIVE closing gate: full L=5 uniform Farkas cone WITH GPT-Pro's mixed five-shadow
   generator Q_mix added.  Old 45-gen cone was EXACT-INFEASIBLE (dual y=(-1,1/2,1/2)).
   Q_mix(canonical bluedist shadow) breaks that dual (y.Q_mix=125/42>0).

   Test: with Q_mix column(s) appended, is the UNIFORM cone  exists lambda>=0, G lambda = b
   now FEASIBLE?  If float-feasible -> extract rational certificate -> EXACT-verify on all rows.

   Q_mix(phi) = Gamma - 25*min_i(n_i*w_{i+1}),  n_i=#{phi=i}, w_i=(1/N)sum_{phi(v)=i}T(v).
   Canonical shadow: phi(v) = bluedist(x0, v) mod 5  (satisfies phi(x_i)=i on the blue geodesic).
   All generators have PROVEN sign: dGamma>=0 (gamma-min), dB-dM>=0 (max-cut),
   product-slack>=0 (def q), Q_mix>=0 (AM-GM, non-circular).  A feasible exact certificate
   => 25*M(P)>=0 => F>=C_L/25 => PATH-GAMMA (ell=5) PROVEN.
"""
import sys, subprocess
from collections import deque
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog

from _wf_deficit_farkas import (build_rows_for_cut, GEN_LABELS, NGEN,
                                 odd_blowup, families)
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def bluedist(n, adj, side, src):
    d = {src: 0}; dq = deque([src])
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u]+1; dq.append(v)
    return d

def qmix_canonical(n, adj, side, T, Gamma, P):
    """Canonical blue-distance five-shadow Q_mix; None if shadow invalid (shouldn't for connected-B)."""
    d = bluedist(n, adj, side, P[0])
    if any(v not in d for v in range(n)): return None
    phi = [d[v] % 5 for v in range(n)]
    for i in range(5):
        if phi[P[i]] != i: return None
    N = F(n); ncnt = [0]*5; wsum = [F(0)]*5
    for v in range(n):
        c = phi[v]; ncnt[c] += 1; wsum[c] += T[v]
    w = [wsum[i]/N for i in range(5)]
    mn = min(F(ncnt[i])*w[(i+1) % 5] for i in range(5))
    return Gamma - 25*mn

EXT_LABELS = GEN_LABELS + ["H.Qmix.bluedist"]
NEXT = len(EXT_LABELS)

def collect_ext(name, n, E):
    adj, cuts = gmins(n, E)
    rows = []
    for side in cuts:
        base = build_rows_for_cut(n, adj, side, name)
        if not base: continue
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st
        Gamma = sum(T)
        for r in base:
            Q = qmix_canonical(n, adj, side, T, Gamma, r['P'])
            if Q is None: Q = F(0)
            r['g'] = list(r['g']) + [Q]
            rows.append(r)
    return rows

def solve(rows):
    R = len(rows)
    A = np.array([[float(rows[r]['g'][c]) for c in range(NEXT)] for r in range(R)], float)
    b = np.array([float(rows[r]['b']) for r in range(R)], float)
    res = linprog(np.zeros(NEXT), A_eq=A, b_eq=b, bounds=[(0, None)]*NEXT, method="highs")
    return res

def exact_verify(rows, lam):
    bad = []
    for r, row in enumerate(rows):
        lhs = sum(row['g'][c]*lam[c] for c in range(NEXT))
        if lhs != row['b']:
            bad.append((r, row['name'], str(row['P']), str(lhs - row['b'])))
    return bad

def rationalize(x, maxden=100000):
    return F(x).limit_denominator(maxden)

def main():
    fams = families()
    # extend census to N=11
    for nn in [11]:
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); fams.append(("cen11-%s" % g6, n, E))
    rows = []
    for (name, n, E) in fams:
        rows += collect_ext(name, n, E)
    print("collected %d L=5 rows; generators = %d (45 + Q_mix)" % (len(rows), NEXT))
    sys.stdout.flush()
    res = solve(rows)
    print("LP status:", res.message, "| success:", res.success)
    if not res.success:
        print(">>> STILL INFEASIBLE with Q_mix (float). Route-A single-canonical Q_mix insufficient.")
        return
    # rationalize and exact-verify
    lam = [rationalize(res.x[c]) for c in range(NEXT)]
    bad = exact_verify(rows, lam)
    support = [(EXT_LABELS[c], str(lam[c])) for c in range(NEXT) if lam[c] != 0]
    print("float support:", [(EXT_LABELS[c], round(res.x[c],4)) for c in range(NEXT) if res.x[c] > 1e-9])
    print("rational support:", support)
    if not bad:
        print(">>> EXACT CERTIFICATE FOUND & VERIFIED on all %d rows. ell=5 PATH-GAMMA PROVEN." % len(rows))
    else:
        print(">>> rationalized lambda fails exact on %d rows (float-only); need exact LP / better rationalization." % len(bad))
        for v in bad[:5]: print("    ", v)

if __name__ == "__main__":
    main()
