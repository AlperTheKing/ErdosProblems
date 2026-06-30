"""FOLLOW-UP to _hardy_pervertex.py.

Established EXACTLY (2409 gamma-min cuts incl N=23, C5[3] tight):
  (a)  T_v - N <= d(v)   holds 0-fail   <=>   H[v][v] = (N - T_v) + d(v) >= 0   for all v.
  (c)  plain Gershgorin H[v][v] >= sum_{w!=v}|H[v][w]|  fails exactly at the T_v>N vertices (= NOT elementary).

So per-vertex DIAGONAL NONNEGATIVITY holds but plain diagonal dominance does not.  The standard way to
upgrade is WEIGHTED (scaled) diagonal dominance: pick positive weights g_v with
    H[v][v] * g_v  >=  sum_{w!=v} |H[v][w]| * g_w        for all v.
If such g>0 exists for every cut, then D_g^{-1} H D_g... actually the clean statement: a symmetric matrix H
with H[v][v]>=0 is PSD if there EXISTS g>0 with  H[v][v] g_v >= sum_{w!=v} |H[v][w]| g_w  AND the off-diagonals
are <=0 (H is a symmetric Z-matrix => weighted diag dominant + nonneg diag => PSD M-matrix-like).  Lstar has
off-diag <=0, and D_{N-T} is diagonal, so H IS a symmetric Z-matrix.  For a symmetric Z-matrix, H PSD <=>
H is positive semidefinite <=> there is g>0 with row-sums (H g)_v >= 0 for all v (since H = M-matrix shifted).
Equivalently: H g >= 0 componentwise for some g>0  =>  H PSD (for symmetric Z-matrix this is sufficient).

CANONICAL CANDIDATE WEIGHT:  the all-ones vector g = 1.  Then (H * 1)_v = H[v][v] + sum_{w!=v} H[v][w]
= (N - T_v) + d(v) - d(v)  [Lstar row sums to 0]  = N - T_v.  This is < 0 at overloaded vertices => g=1 fails.

So we need a NON-trivial g>0.  Natural candidates from the geometry:
   g_v = 1                      (fails, = T_v<=N)
   g_v = T_v                    (load-weighted)
   g_v = something from cycles
We TEST EXACTLY whether the row-sum certificate H g >= 0 holds for these g, on the battery.  A g that works
0-fail would give an ELEMENTARY (no eigenvalue) proof of (H) via Z-matrix theory.

Also: measure the (a)-margin  m_v = d(v) - (T_v - N) = H[v][v]  to see tightness, and where it is smallest.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _hardy_gate import BETA, build_H


def matvec(H, g, n):
    return [sum(H[v][w] * g[w] for w in range(n)) for v in range(n)]


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)

    # min diagonal of H = min (a)-margin
    for v in range(n):
        m = H[v][v]
        if acc['min_diag'] is None or m < acc['min_diag']:
            acc['min_diag'] = m; acc['min_diag_ex'] = (name, n, v)

    # candidate row-sum certificates  H g >= 0  componentwise, g>0
    # g1 = ones
    g1 = [F(1)] * n
    r1 = matvec(H, g1, n)
    if any(x < 0 for x in r1):
        acc['g1_fail'] += 1
    # g2 = T_v (load)  (strictly positive on cut vertices; T_v>0 for any vertex on a bad cycle, but some
    #     vertices have T_v=0 -> not >0; replace 0 by a small positive 1 to keep g>0)
    g2 = [T[v] if T[v] > 0 else F(1) for v in range(n)]
    r2 = matvec(H, g2, n)
    if any(x < 0 for x in r2):
        acc['g2_fail'] += 1
        if acc['g2_ex'] is None:
            bad = [v for v in range(n) if r2[v] < 0][0]
            acc['g2_ex'] = (name, n, bad, str(r2[bad]))
    # g3 = degree-in-cycles weight = d(v) shifted positive: use H[v][v] if >0 else 1
    g3 = [H[v][v] if H[v][v] > 0 else F(1) for v in range(n)]
    r3 = matvec(H, g3, n)
    if any(x < 0 for x in r3):
        acc['g3_fail'] += 1
        if acc['g3_ex'] is None:
            bad = [v for v in range(n) if r3[v] < 0][0]
            acc['g3_ex'] = (name, n, bad, str(r3[bad]))
    # g4 = N - T_v + d(v) is H[v][v]; try g4 = T_v + 1 (uniform positive shift of load)
    g4 = [T[v] + 1 for v in range(n)]
    r4 = matvec(H, g4, n)
    if any(x < 0 for x in r4):
        acc['g4_fail'] += 1
        if acc['g4_ex'] is None:
            bad = [v for v in range(n) if r4[v] < 0][0]
            acc['g4_ex'] = (name, n, bad, str(r4[bad]))


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(cuts=0, g1_fail=0, g2_fail=0, g3_fail=0, g4_fail=0,
               g2_ex=None, g3_ex=None, g4_ex=None, min_diag=None, min_diag_ex=None)

    for sizes in [(2,1,2,1,2), (3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        gfam("C5blow%s" % (sizes,), nn, EE, acc)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d done: cuts=%d g1f=%d g2f=%d g3f=%d g4f=%d"
              % (nn, acc['cuts'], acc['g1_fail'], acc['g2_fail'], acc['g3_fail'], acc['g4_fail']), flush=True)
    for q in range(2, 12):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after chains+Grotzsch+Myc23: cuts=%d g1f=%d g2f=%d g3f=%d g4f=%d"
          % (acc['cuts'], acc['g1_fail'], acc['g2_fail'], acc['g3_fail'], acc['g4_fail']), flush=True)

    rng = random.Random(7); made = 0; tries = 0
    while made < 60 and tries < 30000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)

    print("=" * 64)
    print("total gamma-min cuts tested:", acc['cuts'], " (random N11/12:", made, ")")
    print("min diagonal H[v][v] (= min (a)-margin):", float(acc['min_diag']) if acc['min_diag'] is not None else None,
          "at", acc['min_diag_ex'])
    print("ROW-SUM Z-matrix certificate  H g >= 0 componentwise (g>0 => PSD):")
    print("  g = ones        : FAILURES =", acc['g1_fail'], "(expected: = #cuts with some T_v>N)")
    print("  g = T_v (load)  : FAILURES =", acc['g2_fail'], acc['g2_ex'] or '')
    print("  g = H[v][v]+    : FAILURES =", acc['g3_fail'], acc['g3_ex'] or '')
    print("  g = T_v + 1     : FAILURES =", acc['g4_fail'], acc['g4_ex'] or '')


if __name__ == "__main__":
    main()
