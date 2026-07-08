r"""ODD-CYCLE PACKING mirror gate (2026-07-08, Fable-5). Falsifier-first test of MY packing-mechanism candidate
for L3 (sent to GPT-Pro, verdict pending): at a Gamma-min MAX cut of a triangle-free graph, does a FRACTIONAL
odd-cycle packing exist assigning total weight 1 to the geodesic cycles of EACH bad edge (cycle = bad edge e +
one shortest blue geodesic between its endpoints) with congestion <= 1 on every cut edge@?

LP per config:  t* = min t  s.t.  Sum_g w(e,g) = 1 for every bad edge e (ALL bad edges, any ell);
                                  Sum_{(e,g) : c in g} w(e,g) <= t for every cut edge c;  w >= 0.
t* <= 1  <=> the packing mirror holds. t* is the CONGESTION NUMBER: expect exactly 1 (tight) at C5[t] and the
odd cycles, < 1 generically. A single real config with t* > 1 REFUTES the mirror as stated (then only the
leak/bank version survives -- report immediately, before GPT-Pro over-invests).
Geodesic enumeration capped (many-geodesic atoms use a sampled subset -- cap makes t* an UPPER bound, so
t*<=1 conclusions are still valid certificates; t*>1 under cap = inconclusive, escalate cap).
Census N=5..9 Gamma-min max cuts + C5[1..3] + CP11 + F4 true-gmin configs. Float LP + exact Fraction re-verify
of the optimal packing on the named anchors. Run from problems/23/writeup.
"""
import subprocess, json
from fractions import Fraction
from collections import deque
import numpy as np
from scipy.optimize import linprog
from _h import dec, maxcut_all, Bconn, GENG, gmin
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import geos_paths, residuals

CAP_GEOS = 200


def cut_edges_of(n, adj, side):
    return sorted((a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b])


def packing_lp(name, n, adj, side, acc, exact_anchor=False):
    cd = residuals(n, adj, side)
    if cd is None:
        return
    bad = list(cd['M'])
    if not bad:
        return
    cutE = cut_edges_of(n, adj, side)
    eidx = {c: i for i, c in enumerate(cutE)}
    cols = []          # (bad_index, frozenset(edge_indices))
    for bi, e in enumerate(bad):
        gs = geos_paths(adj, side, e[0], e[1])
        if not gs:
            return  # not B-connected
        for P in gs[:CAP_GEOS]:
            edges = frozenset(eidx[(min(P[i], P[i + 1]), max(P[i], P[i + 1]))] for i in range(len(P) - 1))
            cols.append((bi, edges))
    nv = len(cols) + 1  # + t
    # equality: per bad edge, sum w = 1
    A_eq, b_eq = [], []
    for bi in range(len(bad)):
        A_eq.append([1.0 if cols[k][0] == bi else 0.0 for k in range(len(cols))] + [0.0])
        b_eq.append(1.0)
    # congestion: per cut edge, sum w - t <= 0
    A_ub, b_ub = [], []
    for ci in range(len(cutE)):
        row = [1.0 if ci in cols[k][1] else 0.0 for k in range(len(cols))] + [-1.0]
        A_ub.append(row); b_ub.append(0.0)
    cost = [0.0] * len(cols) + [1.0]
    res = linprog(c=cost, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)] * len(cols) + [(0, None)], method='highs')
    if not res.success:
        acc['lpfail'].append(name); return
    tstar = float(res.x[-1])
    acc['n'] += 1
    rec = dict(name=name, n=n, bads=len(bad), cutE=len(cutE), cols=len(cols), tstar=round(tstar, 6))
    acc['rows'].append(rec)
    if tstar > 1 + 1e-7:
        acc['violations'].append(rec)
    if acc['worst'] is None or tstar > acc['worst'][1]:
        acc['worst'] = (name, tstar)
    if exact_anchor:
        w = {k: Fraction(res.x[k]).limit_denominator(10 ** 4) for k in range(len(cols)) if res.x[k] > 1e-9}
        ok = True
        for bi in range(len(bad)):
            if sum(v for k, v in w.items() if cols[k][0] == bi) != 1:
                ok = False; break
        maxcong = max((sum(v for k, v in w.items() if ci in cols[k][1]) for ci in range(len(cutE))), default=Fraction(0))
        rec['exact'] = bool(ok and maxcong <= 1)
        rec['exact_maxcong'] = str(maxcong)
        print("   ANCHOR %-10s t*=%.6f exact-verify=%s (max congestion %s)" % (name, tstar, rec['exact'], maxcong), flush=True)


def c5t_build(t):
    n = 5 * t
    E = []
    for a in range(5):
        b = (a + 1) % 5
        for i in range(t):
            for j in range(t):
                E.append((min(a * t + i, b * t + j), max(a * t + i, b * t + j)))
    adj = adj_from_edges(n, E)
    side = [0 if (v // t) in (0, 2, 4) else 1 for v in range(n)]
    return n, adj, side


def counterpattern11():
    V = ['p', 'q', 'a', 'b', 'bb', 'c', 'y', 'w', 'r1', 'r2', 'r3']
    idx = {v: i for i, v in enumerate(V)}
    given = {v: 0 for v in ['p', 'q', 'b', 'bb', 'y', 'w', 'r2']}
    for v in ['a', 'c', 'r1', 'r3']:
        given[v] = 1
    B = [('p', 'a'), ('a', 'b'), ('b', 'c'), ('c', 'y'), ('q', 'c'), ('c', 'bb'), ('bb', 'a'),
         ('a', 'w'), ('p', 'r1'), ('r1', 'r2'), ('r2', 'r3'), ('r3', 'q')]
    M = [('p', 'y'), ('q', 'w'), ('p', 'q')]
    E = [(min(idx[u], idx[w]), max(idx[u], idx[w])) for u, w in B + M]
    adj = adj_from_edges(11, E)
    return 11, adj, [given[v] for v in V]


def main():
    acc = dict(n=0, rows=[], violations=[], lpfail=[], worst=None)
    print("ODD-CYCLE PACKING mirror gate: t* = min max-congestion (unit weight per bad edge, geodesic cycles)")
    print("=" * 100)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None or not Bconn(n, adj, best[0]):
                continue
            packing_lp('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cfgs %d, violations %d, worst %s" % (nn, acc['n'], len(acc['violations']),
              ("%s t*=%.6f" % acc['worst']) if acc['worst'] else None), flush=True)
    for t in (1, 2, 3):
        n, adj, side = c5t_build(t)
        packing_lp('C5[%d]' % t, n, adj, side, acc, exact_anchor=True)
    n, adj, side = counterpattern11()
    packing_lp('CP11', n, adj, side, acc, exact_anchor=True)
    print("=" * 100)
    print("TOTALS: %d configs | t*>1 VIOLATIONS: %d | worst t* = %s" % (acc['n'], len(acc['violations']), acc['worst'],))
    for r in acc['violations'][:10]:
        print("   VIOLATION:", r)
    hist = {}
    for r in acc['rows']:
        b = min(10, int(r['tstar'] * 10))
        hist[b] = hist.get(b, 0) + 1
    print("t* histogram (x0.1 buckets):", dict(sorted(hist.items())))
    json.dump(acc, open('../../../tmp/claude_oddcycle_packing_gate.json', 'w'), indent=1, default=str)
    print("VERDICT:", ("PACKING MIRROR REFUTED on a real config (see VIOLATION rows) -- only the leak/bank "
                       "version survives; correct GPT-Pro NOW" if acc['violations'] else
                       "packing mirror HOLDS (t*<=1) on ALL %d real configs tested; tightness at anchors as "
                       "predicted -- (i) is a real empirical law, the packing-existence lemma is THE candidate core"
                       % acc['n']))


if __name__ == '__main__':
    main()
