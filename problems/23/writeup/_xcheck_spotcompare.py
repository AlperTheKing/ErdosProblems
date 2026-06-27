"""Spot-check: compare my independent impl vs census_GPI on specific graphs.
Compares Gamma, K, and max_v T_uniform exactly."""
import sys
from fractions import Fraction
import _xcheck_indep as IND
from census_GPI import dec, maxcut_all, gmin, geos

def census_gpi_maxT(g6):
    """Replicate the T_uniform computation USING census_GPI primitives only."""
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    cuts = maxcut_all(n, adj)
    g = gmin(n, adj, cuts)
    if g is None:
        return None
    side, Gamma, M, ell = g
    T = [Fraction(0)] * n
    for f in M:
        Ps = geos(adj, side, f[0], f[1])
        nf = len(Ps)
        share = Fraction(ell[f], nf)
        for P in Ps:
            for v in P:
                T[v] += share
    maxT = max(T) if T else Fraction(0)
    K = n + (n*n - Gamma)
    return dict(n=n, Gamma=Gamma, K=Fraction(K), maxT=maxT)

# three graphs to spot-check: pick the tight C5 (N=5), the n=8 witness, and a random N=10 graph
import subprocess
TESTS = []
# C5 = first tight at N=5
out5 = subprocess.run([IND.GENG,'-tc','5'],capture_output=True,text=True).stdout.split()
for g6 in out5:
    n,E = IND.g6_decode(g6)
    r = IND.check_graph(n,E)
    if r and r['slack']==0:
        TESTS.append(g6); break
# the n=8 witness
TESTS.append('G?`F`w')
# a representative N=10 graph (take the 1000th connected tri-free with a connected-B cut)
out10 = subprocess.run([IND.GENG,'-tc','10'],capture_output=True,text=True).stdout.split()
TESTS.append(out10[1000])

print("g6 | mine(Gamma,K,maxT) | census_GPI(Gamma,K,maxT) | MATCH?")
all_match = True
for g6 in TESTS:
    n,E = IND.g6_decode(g6)
    mine = IND.check_graph(n,E)
    cg = census_gpi_maxT(g6)
    if mine is None or cg is None:
        print(f"{g6}: mine={mine is not None}, census={cg is not None} -- skip")
        continue
    m = (mine['Gamma'], mine['K'], mine['maxT'])
    c = (cg['Gamma'], cg['K'], cg['maxT'])
    match = (m == c)
    all_match = all_match and match
    print(f"{g6} | mine={m} | census={c} | MATCH={match}")
print("ALL THREE MATCH:", all_match)
