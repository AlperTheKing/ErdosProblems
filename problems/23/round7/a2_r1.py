"""AUDIT pass 2 -- R1 (Grotzsch / neighbourhood-union family) and E3 (uniqueness).

Everything exact.  Independent of Q1_*.py and audit_Q1_*.py.
"""
from fractions import Fraction as F
from itertools import combinations
from a2_core import (g6_decode, g6_encode, adj_masks, is_triangle_free, bip, bip2,
                     blowup_value, expand_blowup, nbhd_union_sets, family_value,
                     count_C5_subgraphs, induced_C5_vertexsets, compositions, cycle)

G6 = 'J?BD@g]Qvo?'
n, E = g6_decode(G6)
A = adj_masks(n, E)
print(f'== A. decode {G6}: n={n} |E|={len(E)} trianglefree={is_triangle_free(n,E)}')
print('   edges  :', E)
print('   degrees:', sorted(bin(A[v]).count("1") for v in range(n)))
print('   g6 round trip:', g6_encode(n, E), g6_encode(n, E) == G6)


# ---- B. isomorphism to the Mycielskian M(C5) -----------------------------
def mycielski(nn, EE):
    """M(H): vertices 0..nn-1 = shadows u_i, nn..2nn-1 = originals v_i, 2nn = apex.
    Here I use the report's claimed labelling: 0..4 shadows, 5..9 the C5, 10 apex."""
    m = 2 * nn + 1
    F_ = []
    for (u, v) in EE:
        F_.append((nn + u, nn + v))          # original copy
        F_.append((u, nn + v))               # shadow-original
        F_.append((v, nn + u))
    for i in range(nn):
        F_.append((i, 2 * nn))               # shadow-apex
    return m, sorted(tuple(sorted(e)) for e in F_)


def iso(n1, E1, n2, E2):
    """backtracking isomorphism search, degree-pruned. returns a mapping or None."""
    if n1 != n2 or len(E1) != len(E2):
        return None
    A1, A2 = adj_masks(n1, E1), adj_masks(n2, E2)
    d1 = [bin(A1[v]).count('1') for v in range(n1)]
    d2 = [bin(A2[v]).count('1') for v in range(n2)]
    if sorted(d1) != sorted(d2):
        return None
    order = sorted(range(n1), key=lambda v: -d1[v])
    mp = {}
    used = set()

    def rec(k):
        if k == n1:
            return True
        u = order[k]
        for w in range(n2):
            if w in used or d2[w] != d1[u]:
                continue
            ok = True
            for j in range(k):
                uu = order[j]
                if (((A1[u] >> uu) & 1) != ((A2[w] >> mp[uu]) & 1)):
                    ok = False
                    break
            if ok:
                mp[u] = w
                used.add(w)
                if rec(k + 1):
                    return True
                used.discard(w)
                del mp[u]
        return False
    return dict(mp) if rec(0) else None


nc, Ec = cycle(5)
mn, mE = mycielski(nc, Ec)
mp = iso(n, E, mn, mE)
print(f'== B. isomorphic to M(C5)? {mp is not None};  mapping={mp}')
print('     identity mapping works?', sorted(tuple(sorted(e)) for e in E) == mE)

# ---- C. bip, three ways, and the neighbourhood-union family --------------
b1, b2 = bip(n, E), bip2(n, E)
# third, totally naive: brute force over all 2^n assignments with an explicit list
b3 = min(sum(1 for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1)) for S in range(1 << n))
sets = nbhd_union_sets(n, E)
fam = family_value(n, E, [1] * n, sets)
single = min(sum(1 for (u, v) in E if ((A[w] >> u) & 1) == ((A[w] >> v) & 1)) for w in range(n))
print(f'== C. bip = {b1} / {b2} / {b3}   (agree: {b1==b2==b3})')
print(f'     #distinct neighbourhood-union sets = {len(sets)}')
print(f'     min over the union family = {fam};  min over single N(v) = {single}')
print(f'     25*fam = {25*fam} vs n^2 = {n*n}  -> certificate FAILS: {25*fam > n*n}')
print(f'     25*bip = {25*b1} vs n^2 = {n*n}   -> conjecture OK: {25*b1 <= n*n}')
print(f'     exact: bip/n^2 = {F(b1,n*n)} = 1/25 - {F(1,25)-F(b1,n*n)};'
      f'  fam/n^2 = {F(fam,n*n)} = 1/25 + {F(fam,n*n)-F(1,25)}')

# widened families
pairs = min(sum(1 for (u, v) in E if (((A[p] | A[q]) >> u) & 1) == (((A[p] | A[q]) >> v) & 1))
            for p in range(n) for q in range(n))
sym = min(sum(1 for (u, v) in E if (((A[p] ^ A[q]) >> u) & 1) == (((A[p] ^ A[q]) >> v) & 1))
          for p in range(n) for q in range(n) if p != q)
closed = [A[v] | (1 << v) for v in range(n)]
cl = min(sum(1 for (u, v) in E if ((c >> u) & 1) == ((c >> v) & 1)) for c in closed)
print(f'     pairs {pairs}   symmetric-differences {sym}   closed nbhds {cl}')

# ---- D. BFS-layer scope claim -------------------------------------------
def bfs_odd(nn, AA, root):
    dist = [-1] * nn
    dist[root] = 0
    frontier = [root]
    while frontier:
        nxt = []
        for x in frontier:
            for y in range(nn):
                if (AA[x] >> y) & 1 and dist[y] < 0:
                    dist[y] = dist[x] + 1
                    nxt.append(y)
        frontier = nxt
    S = 0
    for v in range(nn):
        if dist[v] > 0 and dist[v] % 2 == 1:
            S |= 1 << v
    return S


bfsvals = []
setset = set(sets)
notin = 0
for r in range(n):
    S = bfs_odd(n, A, r)
    bfsvals.append(sum(1 for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1)))
    if S not in setset:
        notin += 1
print(f'== D. Grotzsch odd-BFS-layer cut values by root: {bfsvals}  min={min(bfsvals)}')
print(f'     #roots whose odd-layer set is NOT a neighbourhood union: {notin}')

# ---- E. the 17-vertex blow-up -------------------------------------------
a17 = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
bb = blowup_value(n, E, a17)
ff = family_value(n, E, a17, sets)
NN, EE = expand_blowup(n, E, a17)
bexp = bip(NN, EE)
print(f'== E. a=(1^5,2^6) W={sum(a17)}: base-1 bip={bb}  explicit {NN}-vertex blow-up bip={bexp} '
      f'(agree: {bb==bexp}) |E(blowup)|={len(EE)} trianglefree={is_triangle_free(NN,EE)}')
print(f'     family value = {ff};  ratio fam/bip = {F(ff,bb)};  overshoot 25*fam/W^2 = {F(25*ff,sum(a17)**2)}')
print(f'     bip/W^2 = {F(bb,289)} = 1/25 - {F(1,25)-F(bb,289)};  fam/W^2 = {F(ff,289)} = 1/25 + {F(ff,289)-F(1,25)}')

# ---- F. E3: uniqueness of the blow-up maximiser --------------------------
ind5 = induced_C5_vertexsets(n, E)
print(f'== F. induced C5 subsets of Grotzsch: {len(ind5)}')
maxers = []
for S in ind5:
    a = [0] * n
    for v in S:
        a[v] = 5
    q = blowup_value(n, E, a)
    if 25 * q == 25 * 25:
        maxers.append((S, q))
print(f'     of these, #{len(maxers)} give 25*bip = W^2 at W=25 (weight 5 on each of the five)')
print('     first five:', maxers[:5])
claim = [5, 5, 0, 0, 0, 5, 5, 0, 0, 5, 0]
print(f'     pass-1 falsifier a={claim}: bip={blowup_value(n,E,claim)}  '
      f'25*bip={25*blowup_value(n,E,claim)}  W^2={sum(claim)**2}')
print(f'     support of that vector = {[i for i,v in enumerate(claim) if v]}, '
      f'induced C5? {tuple(i for i,v in enumerate(claim) if v) in set(ind5)}')
print(f'     Q1.md claims the ONLY maximiser is (0,0,0,0,0,t,t,t,t,t,0); '
      f'is (5,6,7,8,9) an induced C5? {(5,6,7,8,9) in set(ind5)}')

# exhaustive count of maximisers at small W (exact, zero weights allowed)
for W in (5, 10):
    cnt = 0
    ex = None
    for a in compositions(n, W):
        q = blowup_value(n, E, list(a))
        if 25 * q == W * W:
            cnt += 1
            if ex is None:
                ex = a
        assert 25 * q <= W * W, ('COUNTEREXAMPLE', a, q)
    print(f'     W={W}: #maximisers (25*bip == W^2) = {cnt}, e.g. {ex}')
