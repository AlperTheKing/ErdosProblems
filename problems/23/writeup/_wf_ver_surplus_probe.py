"""Probe the ratio-max witness nu[5,1,1,1,5] (N=13) and the claimant's cited witness cenJ????A?oB~?."""
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
import _wf_ver_surplus as W

def report(name, n, E):
    adj, cuts = gmins(n, E)
    for idx, s in enumerate(cuts):
        st = struct_for_side(n, adj, s)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        N = F(n); beta = len(M); Gamma = sum(F(ell[f])**2 for f in M)
        V2 = sum((t - N)**2 for t in T)
        sumTTmN = sum(t*(t - N) for t in T)
        badset = set((min(a, b), max(a, b)) for (a, b) in M)
        TVcut = F(0); TVbad = F(0)
        for u in range(n):
            for v in adj[u]:
                if v <= u:
                    continue
                d = abs(T[u] - T[v])
                if s[u] != s[v]:
                    TVcut += d
                else:
                    TVbad += d
        denom = Gamma * (F(n*n, 25) - beta)
        central_lhs = V2 + N*(Gamma - N*N) + F(n, 5)*(TVcut - TVbad)
        rhs = Gamma * (F(n*n, 25) - beta)
        margin = rhs - central_lhs
        ratio = (V2 / denom) if denom != 0 else None
        print("%s cut#%d: N=%d beta=%d Gamma=%s V2=%s TVcut=%s TVbad=%s" % (
            name, idx, n, beta, Gamma, V2, TVcut, TVbad))
        print("   denom(=Gamma*(N2/25-beta))=%s  ratio V2/denom=%s (%.6f)" % (
            denom, ratio, float(ratio) if ratio is not None else float('nan')))
        print("   CENTRAL margin = %s (%.6f)  -> %s" % (
            margin, float(margin), "HOLDS" if margin >= 0 else "VIOLATION"))
        print("   T = %s" % [str(t) for t in T])

# the ratio-max witness from my gate
n, E = W.blowup([5, 1, 1, 1, 5])
report("nu[5,1,1,1,5]", n, E)
# the claimant's cited witness
n2, E2 = dec("J????A?oB~?")
report("cenJ????A?oB~?", n2, E2)
