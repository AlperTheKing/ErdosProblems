"""AUDIT pass 2 -- protocol step 2: run the R1 scheme (and the single-neighbourhood
sub-family, and the BFS-layer family) against the ten recorded witnesses of
round5/claude_witness_regression.py, exactly, and check tightness on C5[n].

Own weighted max-cut: subset DP over W[S] = sum_{u<v in S, u~v} w_u w_v, exact integers.
Own union-of-neighbourhood closure.  No floating point on any acceptance path.
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, r'E:\Projects\ErdosProblems\problems\23\round5')
from claude_witness_regression import WITNESSES, gamma, arcbound, mono as regr_mono  # noqa

from a2_core import blowup_value, expand_blowup, bip, nbhd_union_sets, cycle


def true_min_int(m, adj, w):
    """exact min over ALL cuts of sum_{uv mono} w_u w_v, integer weights."""
    full = (1 << m) - 1
    nbr = [[u for u in range(m) if adj[v][u]] for v in range(m)]
    Wt = [0] * (1 << m)
    for S in range(1, 1 << m):
        v = (S & -S).bit_length() - 1
        T = S ^ (1 << v)
        s = 0
        for u in nbr[v]:
            if (T >> u) & 1:
                s += w[u]
        Wt[S] = Wt[T] + w[v] * s
    best = None
    for S in range(1 << (m - 1)):
        t = Wt[S] + Wt[full ^ S]
        if best is None or t < best:
            best = t
    return best, Wt, full


def union_sets(m, adj):
    """all distinct unions of neighbourhoods, over every index set I."""
    nb = [sum(1 << u for u in range(m) if adj[v][u]) for v in range(m)]
    cur = {0}
    for v in range(m):
        cur |= {S | nb[v] for S in cur}
    return cur, nb


def odd_layer_sets(m, adj):
    out = set()
    for r in range(m):
        dist = [-1] * m
        dist[r] = 0
        q = [r]
        for x in q:
            for y in range(m):
                if adj[x][y] and dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        out.add(sum(1 << v for v in range(m) if dist[v] > 0 and dist[v] % 2))
    return out


print('== protocol step 2: the ten recorded witnesses ==')
print(f'{"witness":28s} {"m":>3s} {"true min (all cuts)":>20s} {"arcbound":>10s} '
      f'{"R1 union family":>16s} {"single N(v)":>12s} {"odd BFS":>10s}  verdict')
bad_R1 = []
for wname, m, w, why in WITNESSES:
    adj = gamma(m)
    q = sum(w)
    tm, Wt, full = true_min_int(m, adj, w)
    us, nb = union_sets(m, adj)
    fam = min(Wt[S] + Wt[full ^ S] for S in us)
    sgl = min(Wt[nb[v]] + Wt[full ^ nb[v]] for v in range(m))
    ols = odd_layer_sets(m, adj)
    bfs = min(Wt[S] + Wt[full ^ S] for S in ols)
    x = [F(wi, q) for wi in w]
    ab = arcbound(m, adj, x)
    tf = F(tm, q * q)
    ff = F(fam, q * q)
    sf = F(sgl, q * q)
    bf = F(bfs, q * q)
    ok = ff <= F(1, 25)
    if not ok:
        bad_R1.append(wname)
    print(f'{wname:28s} {m:3d} {str(tf):>20s} {str(ab):>10s} {str(ff):>16s} {str(sf):>12s} '
          f'{str(bf):>10s}  R1 {"OK" if ok else "*** EXCEEDS 1/25 ***"}'
          f'{"  single EXCEEDS" if sf > F(1,25) else ""}'
          f'{"  bfs EXCEEDS" if bf > F(1,25) else ""}'
          f'{"  [arcbound != true min]" if ab != tf else ""}')
print(f'\nR1 family fails on: {bad_R1 if bad_R1 else "NONE of the ten witnesses"}')

print('\n== tightness of R1 on C5[n] (exact, all integer weightings) ==')
n5, E5 = cycle(5)
sets5 = nbhd_union_sets(n5, E5)
worst = None
allmatch = True
from a2_core import compositions
for W in range(1, 13):
    for a in compositions(5, W):
        b = blowup_value(n5, E5, list(a))
        f = min(sum(a[u] * a[v] for (u, v) in E5 if ((S >> u) & 1) == ((S >> v) & 1))
                for S in sets5)
        if f != b:
            allmatch = False
            print('   MISMATCH', a, b, f)
        r = F(25 * b, W * W)
        if worst is None or r > worst[0]:
            worst = (r, W, a)
print(f'   R1 == bip for every integer weighting of C5 with sum <= 12 : {allmatch}')
print(f'   max 25*bip/W^2 over those = {worst[0]} at W={worst[1]}, a={worst[2]}')
for W in (5, 10, 15, 20):
    a = [W // 5] * 5
    print(f'   uniform W={W}: 25*bip/W^2 = {F(25*blowup_value(n5,E5,a), W*W)}')

print('\n== tightness of Q1-C (bip <= floor((N-Delta-1)^2/4)) on C5[n] ==')
for t in range(1, 6):
    NN, EE = expand_blowup(5, E5, [t] * 5)
    D = 2 * t
    print(f'   C5[{t}]: N={NN} Delta={D} bip={t*t} Q1-C bound={((NN-D-1)**2)//4}  '
          f'tight={t*t==((NN-D-1)**2)//4}   hypothesis Delta>=3N/5-1 holds? {D >= 3*NN/5-1}')
