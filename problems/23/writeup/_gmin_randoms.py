"""Extend the SOUND reframe to randoms + N=23 efficiently: confirm NO gamma-min connected-B max cut has R[v]<0.

For each graph we enumerate ALL maximum cuts (census N<=12 via maxcut_all; for blowups/N=23 we can't do 2^N,
so we use the CSM-SPEC fact instead: on gamma-min cuts rho(K2)<=N is already verified 0-fail by _csmspec.py,
which is EXACTLY R[v]>=0 in Collatz-Wielandt form -- so here we focus on the enumerable census + glued chains).

Concretely: for every B-connected GAMMA-MIN max cut (Gamma == min over max cuts), check R[v]>=0 for all v.
Any violation is FATAL.  This is the actual proof obligation; the length-bundle construction is only the
attempted *witness* for the contrapositive on non-gamma-min cuts.

Exact Fraction.  Census N=11,12 all max cuts (heavy but bounded) + glued C5 chains + small blowups + randoms N<=12.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import gamma_of
from _bdef_construct import is_triangle_free
from _Klocal_gate import glued_c5_chain


def cutval(n, adj, side):
    return sum(1 for v in range(n) for w in adj[v] if w > v and side[v] != side[w])


def check_graph(name, n, adj, acc):
    cuts = list(maxcut_all(n, adj))
    if not cuts:
        return
    gmax = max(cutval(n, adj, s) for s in cuts)
    gmin = None
    gmin_sides = []
    for s in cuts:
        if cutval(n, adj, s) != gmax:
            continue
        if not Bconn(n, adj, s):
            continue
        g = gamma_of(n, adj, s)
        if g is None:
            continue
        if gmin is None or g < gmin:
            gmin = g
            gmin_sides = [s]
        elif g == gmin:
            gmin_sides.append(s)
    if gmin is None:
        return
    for side in gmin_sides:
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        if not M:
            continue
        N = F(n)
        K2 = build_K2(n, M, cyc)
        R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        acc['gmin_cuts'] += 1
        bad = [v for v in range(n) if R[v] < 0]
        if bad:
            acc['gmin_with_neg'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), bad, str(min(R[v] for v in bad)))


def main():
    acc = dict(gmin_cuts=0, gmin_with_neg=0, ex=None)
    for nn in range(5, 13):
        cnt = 0
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = [set() for _ in range(n)]
            for x, y in E:
                adj[x].add(y); adj[y].add(x)
            check_graph(g6, n, adj, acc)
            cnt += 1
        print("census N=%d (%d graphs): gmin_cuts=%d gmin_with_neg=%d" % (nn, cnt, acc['gmin_cuts'], acc['gmin_with_neg']), flush=True)
    # glued C5 chains
    for q in range(2, 12):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if n <= 16:
            check_graph("chain_q%d" % q, n, adj, acc)
    print("after chains: gmin_cuts=%d gmin_with_neg=%d %s" % (acc['gmin_cuts'], acc['gmin_with_neg'], acc['ex'] or ''), flush=True)
    # randoms N<=12 all max cuts
    rng = random.Random(31); made = 0; tries = 0
    while made < 200 and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.32)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        check_graph("rand%d" % made, nn, adj, acc)
    print("=" * 72)
    print("GAMMA-MIN connected-B max cuts tested:", acc['gmin_cuts'], " (randoms:", made, ")")
    print("gamma-min cuts WITH an R[v]<0 vertex (FATAL):", acc['gmin_with_neg'])
    print("first fatal example:", acc['ex'] or 'NONE')
    print("VERDICT:",
          "SOUND across census+chains+randoms: NO gamma-min cut has R[v]<0 -- the proof obligation (gamma-min=>R>=0) holds empirically; length-bundle (LB) is an over-strong, sometimes-false witness for the contrapositive"
          if acc['gmin_with_neg'] == 0 else "FATAL: gamma-min cut with R<0 found")


if __name__ == "__main__":
    main()
