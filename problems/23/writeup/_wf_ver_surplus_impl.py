"""Implication check: does CENTRAL (c=5) imply LOAD-PSC and Erdos?
We verify, on the core battery:
 (I1) identity  V2+N(Gamma-N^2) == sum_v T(T-N)            [makes central c=5 == LOAD-PSC-5 form]
 (I2) TVcut-TVbad >= 0 everywhere (max-cut/cut-deficit)    [so c=5 LHS >= c=25 LHS; central-5 => central-25]
 (I3) LOAD-PSC-25 form  sum_v T(T-N)+(N/25)(TVcut-TVbad) <= Gamma(N^2/25-beta) holds (implied by central-5)
 (I4) Erdos: from LOAD-PSC, beta <= N^2/25. We confirm sum_v T(T-N) >= 0  (=> Gamma>=N*Gamma? no);
      Actually Erdos derivation: at c, since TVcut-TVbad>=0, LHS_c >= sum_v T(T-N) when (N/c)(TVcut-TVbad)>=0.
      And sum_v T(T-N) = sumT^2 - N*Gamma. By Cauchy-Schwarz sumT^2 >= (sumT)^2/N = Gamma^2/N.
      So Gamma^2/N - N*Gamma <= sum_v T(T-N) <= LHS_c <= Gamma(N^2/25-beta).
      => Gamma/N - N <= N^2/25 - beta  => beta <= N^2/25 - Gamma/N + N. Since Gamma>=25*beta (ell>=5),
      Gamma/N >= 25 beta/N. Need to confirm the standard chain numerically: that central=>Erdos beta<=N^2/25.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords
from _bdef_construct import mycielski, Cn, union_disjoint
import _wf_ver_surplus as W

acc = {'n': 0, 'i1_fail': 0, 'xineg': 0, 'xineg_ex': [],
       'lp25_viol': 0, 'erdos_viol': 0, 'erdos_min_slack': (F(10**30), '')}

def chk(name, n, adj, side):
    from _h import Bconn
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n); beta = len(M); Gamma = sum(F(ell[f])**2 for f in M)
    V2 = sum((t - N)**2 for t in T)
    sumTTmN = sum(t*(t - N) for t in T)
    if V2 + N*(Gamma - N*N) != sumTTmN:
        acc['i1_fail'] += 1
    TVcut = F(0); TVbad = F(0)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            d = abs(T[u] - T[v])
            if side[u] != side[v]:
                TVcut += d
            else:
                TVbad += d
    xi = TVcut - TVbad
    if xi < 0:
        acc['xineg'] += 1
        if len(acc['xineg_ex']) < 5:
            acc['xineg_ex'].append((name, str(xi)))
    rhs = Gamma * (F(n*n, 25) - beta)
    lp25 = sumTTmN + F(n, 25)*xi
    if lp25 > rhs:
        acc['lp25_viol'] += 1
    # Erdos slack: N^2/25 - beta  (should be >= 0)
    erd = F(n*n, 25) - beta
    if erd < 0:
        acc['erdos_viol'] += 1
    if erd < acc['erdos_min_slack'][0]:
        acc['erdos_min_slack'] = (erd, name)
    acc['n'] += 1

for L in range(8, 21):
    n, E, side, _ = build_two_lane(L)
    chk("two-lane-L%d" % L, n, W.adj_of(n, E), side)
for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
    bad = greedy_chords(Ll, k, gap)
    n, E, side, bad = build_k_lane(Ll, k, bad)
    chk("klane-L%dk%d" % (Ll, k), n, W.adj_of(n, E), side)
for nn in range(7, 12):
    outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
    for g6 in outg:
        n, E = dec(g6)
        adj, cuts = gmins(n, E)
        for s in cuts:
            chk("cen" + g6, n, adj, s)
for cyc in (5, 7, 9):
    for t in range(1, 6):
        n, E = W.blowup([t] * cyc)
        if n > 26:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:1] if cuts else []):
            chk("C%d_t%d" % (cyc, t), n, adj, s)
for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],
              [1,6,2,2,6],[4,1,4,1,4],[2,3,1,3,2],[1,1,5,1,1],[5,1,1,1,5]]:
    n, E = W.blowup(parts)
    if n > 26:
        continue
    adj, cuts = gmins(n, E)
    for s in (cuts[:1] if cuts else []):
        chk("nu%s" % parts, n, adj, s)
grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])

def bridge(b1, b2, u, v):
    nn, E = union_disjoint(b1, b2); n1 = b1[0]
    return nn, E + [(u, n1 + v)]

for name, (nn, E) in [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg),
                      ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9))),
                      ("bridge(C7,Grotzsch)", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
                      ("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), 0, 0))]:
    adj, cuts = gmins(nn, E)
    for s in cuts[:3]:
        chk(name, nn, adj, s)

print("IMPL configs=%d" % acc['n'])
print("(I1) identity fail = %d" % acc['i1_fail'])
print("(I2) Xi=TVcut-TVbad < 0 count = %d  examples=%s" % (acc['xineg'], acc['xineg_ex']))
print("(I3) LOAD-PSC-25 violations (should be 0 if central-5 holds & Xi>=0) = %d" % acc['lp25_viol'])
print("(I4) Erdos beta>N^2/25 violations = %d ; min (N^2/25 - beta) = %s at %s" % (
    acc['erdos_viol'], acc['erdos_min_slack'][0], acc['erdos_min_slack'][1]))
