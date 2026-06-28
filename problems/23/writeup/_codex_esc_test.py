"""Exact tests for GPT-Pro's EDGE-SHADOW-CAP candidate.

For a gamma-min connected-B maximum cut and a B-edge e=uv, define

    r_e(f) = Pr_{P in P_f}[P meets {u,v}]
           = p_f(u) + p_f(v) - tau_f(uv).

Candidate inequalities:

    ESC:  sum_f ell(f) r_e(f) <= N              for every B-edge e.
    PESC: sum_f r_e(f) p_f(x) <= 1             for every B-edge e and vertex x.

This script is read-only: it does not certify anything, just finds exact failures.
"""
from fractions import Fraction as F
import subprocess

from _h import dec, GENG
from _angleD_O1 import gmin_sides
from _satzmu_conn import struct_for_side


def p_and_tau_for_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    pdata = {}
    for f in M:
        Ps = cyc[f]
        k = len(Ps)
        p = [F(0) for _ in range(n)]
        tau = {}
        for P in Ps:
            for v in P:
                p[v] += F(1, k)
            for i in range(len(P) - 1):
                e = (min(P[i], P[i + 1]), max(P[i], P[i + 1]))
                tau[e] = tau.get(e, F(0)) + F(1, k)
        # The bad edge f is in the closed odd cycle with probability 1.
        tau[(min(f), max(f))] = tau.get((min(f), max(f)), F(0)) + F(1)
        pdata[f] = (p, tau)
    return M, ell, T, mu, cyc, pdata


def test_side(n, adj, side):
    st = p_and_tau_for_side(n, adj, side)
    if st is None:
        return []
    M, ell, T, mu, cyc, pdata = st
    Bedges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    fails = []
    for e in Bedges:
        esc = F(0)
        pesc = [F(0) for _ in range(n)]
        for f in M:
            p, tau = pdata[f]
            te = tau.get(e, F(0))
            re = p[e[0]] + p[e[1]] - te
            if re < 0:
                fails.append(("NEG_RE", e, f, re))
            esc += ell[f] * re
            for x in range(n):
                pesc[x] += re * p[x]
        if esc > n:
            fails.append(("ESC", e, esc, F(n), T[e[0]], T[e[1]], mu.get(e, F(0))))
        for x, val in enumerate(pesc):
            if val > 1:
                fails.append(("PESC", e, x, val, mu.get(e, F(0))))
                break
    return fails


def run_census(max_n=11, stop_first=True):
    total_sides = 0
    total_edges = 0
    first = None
    for nn in range(7, max_n + 1):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        nfails = 0
        nsides = 0
        nedges = 0
        for g6 in outg:
            n, E = dec(g6)
            adj, sides = gmin_sides(n, E)
            for side in sides:
                nsides += 1
                total_sides += 1
                nedges += sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
                total_edges += nedges
                fs = test_side(n, adj, side)
                if fs:
                    nfails += len(fs)
                    if first is None:
                        first = (g6, side, fs[:5])
                    if stop_first:
                        print(f"N={nn} FIRST_FAIL graph={g6} side={''.join(map(str, side))}")
                        for f in fs[:10]:
                            print(" ", f)
                        return False
        print(f"N={nn}: sides={nsides} B-edge-probes={nedges} failures={nfails}", flush=True)
    print(f"TOTAL sides={total_sides} B-edge-probes={total_edges} first={first}")
    return first is None


if __name__ == "__main__":
    run_census()
