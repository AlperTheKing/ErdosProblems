r"""RESIDUAL R[u] machinery + support-restricted Hall gate for gap#1's final residual (GPT-Pro 2026-07-08).

gap#1 = PositiveSlackHallPrefix_FullBank (support-restricted Hall): PrefixDemand(i) <= 25*sigma + AmbientCap + C5Cap +
PruneCap. The PROVEN residual-sign lemma R[u] = N*T(u) - (K2*T)(u) >= 0 gives bank NONNEGATIVITY but NOT feasibility
(GPT-Pro's 3 failure modes: wrong split R_local<0; wrong location atom routes only to v notin V_a; double-spend).

Claude DERIVED + VALIDATED the K2 operator from K2T_INTERVAL_HALL_PROOF_TARGET.md's exact residual table:
  p_e(u) = (# shortest cut-geodesics of bad edge e through u) / (# geodesics of e)
  T(u)   = sum_e ell(e) * p_e(u)                         [ell(e) = odd-cycle length = #vertices in the shortest cut path]
  K2(u,w)= sum_e p_e(u) * p_e(w)                          [two-support operator]
  (K2*T)(u) = sum_w K2(u,w) * T(w)
  R[u]   = N*T(u) - (K2*T)(u)
This reproduces the table EXACTLY (10-vertex 5/7 model f0=(0,8) f1=(1,7): T={0:5,1:7,2:7,3:6,4:6,5:5/2,6:19/2,7:7,8:12,9:12},
(K2*T)(0)=41, R(0)=9). See validate_k2t_model().

STAGE 1 (this file): verify R[u] >= 0 (the PROVEN residual-sign lemma) exactly on census Gamma-min + even-cycle+chord N>=18.
A single R[u]<0 on a Gamma-min B-connected max cut would contradict the proven lemma (=> a bug or a scope error to surface).
STAGE 2 (next): the support-restricted Hall feasibility (LocalResidualDominance + AmbientResidualDominance) -- the actual residual.
EXACT rational (Fraction). Gamma-min scope. Coverage stated. Run from problems/23/writeup.
"""
from fractions import Fraction as F
from collections import deque
import subprocess, sys
from _h import dec, maxcut_all, Bconn, GENG, gmin
from _codex_k2t_switch_probe import adj_from_edges


def geos_paths(adj, side, s, t):
    dist = {s: 0}; pred = {s: []}; layer = [s]
    while layer:
        nxt = []
        for u in layer:
            for w in adj[u]:
                if side[u] != side[w]:
                    if w not in dist:
                        dist[w] = dist[u] + 1; pred[w] = [u]; nxt.append(w)
                    elif dist[w] == dist[u] + 1:
                        pred[w].append(u)
        layer = nxt
    if t not in dist:
        return []
    P = []
    def rec(v, acc):
        if v == s:
            P.append([s] + acc[::-1]); return
        for p in pred[v]:
            rec(p, acc + [v])
    rec(t, [])
    return P


def residuals(n, adj, side):
    """Return (M, ell, p, T, R) with p[e][v] geodesic-fraction, T[v], R[v]=N*T-K2*T. None if a bad edge has no cut-path."""
    M = [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] == side[b]]
    p = {}; ell = {}
    for e in M:
        Ps = geos_paths(adj, side, e[0], e[1])
        if not Ps:
            return None
        ell[e] = len(Ps[0])  # ell = #vertices in shortest cut path = odd-cycle length
        cnt = {}
        for P in Ps:
            for v in P:
                cnt[v] = cnt.get(v, 0) + 1
        nf = len(Ps)
        p[e] = {v: F(cnt.get(v, 0), nf) for v in range(n)}
    T = [sum(ell[e] * p[e][v] for e in M) for v in range(n)]
    # K2(u,w) = sum_e p_e(u) p_e(w); (K2*T)(u) = sum_w K2(u,w) T(w) = sum_e p_e(u) * (sum_w p_e(w) T(w))
    edge_dot = {e: sum(p[e][w] * T[w] for w in range(n)) for e in M}
    K2T = [sum(p[e][u] * edge_dot[e] for e in M) for u in range(n)]
    R = [F(n) * T[u] - K2T[u] for u in range(n)]
    return dict(M=M, ell=ell, p=p, T=T, K2T=K2T, R=R)


def validate_k2t_model():
    """Reproduce the K2T_INTERVAL_HALL_PROOF_TARGET.md exact table (10-vertex 5/7 model)."""
    n = 10
    # f0=(0,8): 0-5-9-3-8, 0-6-9-3-8, 0-5-9-4-8, 0-6-9-4-8 ; f1=(1,7): 1-6-9-3-8-2-7, 1-6-9-4-8-2-7 ; bad edges (0,8),(1,7)
    E = [(0, 5), (5, 9), (9, 3), (3, 8), (0, 6), (6, 9), (9, 4), (4, 8), (1, 6), (8, 2), (2, 7), (0, 8), (1, 7)]
    adj = adj_from_edges(n, E)
    # side: bipartite on the blue (non-bad) subgraph; bad edges (0,8),(1,7) same-side
    bad = {(0, 8), (1, 7)}
    blue = [set() for _ in range(n)]
    for a, b in E:
        if (min(a, b), max(a, b)) not in bad:
            blue[a].add(b); blue[b].add(a)
    side = [-1] * n; side[0] = 0; q = deque([0])
    while q:
        z = q.popleft()
        for w in blue[z]:
            if side[w] == -1:
                side[w] = 1 - side[z]; q.append(w)
    cd = residuals(n, adj, side)
    if cd is None:
        return False, "no geodesics"
    Tvals = {v: cd['T'][v] for v in range(n)}
    expect_T = {0: F(5), 1: F(7), 2: F(7), 3: F(6), 4: F(6), 5: F(5, 2), 6: F(19, 2), 7: F(7), 8: F(12), 9: F(12)}
    okT = Tvals == expect_T
    okK2T0 = cd['K2T'][0] == F(41)
    okR0 = cd['R'][0] == F(9)
    return (okT and okK2T0 and okR0), dict(T_match=okT, K2T0=str(cd['K2T'][0]), R0=str(cd['R'][0]), ell=cd['ell'])


def check_Rnonneg(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    acc['cages'] += 1
    neg = [(v, cd['R'][v]) for v in range(n) if cd['R'][v] < 0]
    if neg:
        acc['Rneg'] += 1
        if acc['ex'] is None:
            acc['ex'] = (name, n, neg[:3], cd['ell'])
    acc['maxell'] = max(acc['maxell'], max(cd['ell'].values()) if cd['ell'] else 0)


def even_cycle_chord(n, chord):
    E = [(i, (i + 1) % n) for i in range(n)] + [chord]
    return n, adj_from_edges(n, E), [i % 2 for i in range(n)]


try:
    from scipy.optimize import linprog
    import numpy as np
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

DOOR = 25  # one door token per bad edge (25*sigma proxy); ambient/R[v] pays the rest


def stage2_support_hall(n, cd):
    """STAGE 2: route each bad edge's rem = max(0, ell^2-25-DOOR) to vertex banks cap=R[v], ONLY to v notin V_e
    (support restriction = GPT-Pro failure mode 2). Max-flow feasibility (LP). Returns (feasible, detail)."""
    M, ell, p, R = cd['M'], cd['ell'], cd['p'], cd['R']
    edges = []
    for e in M:
        rem = ell[e] ** 2 - 25 - DOOR
        if rem > 0:
            edges.append((e, F(rem)))
    if not edges:
        return True, 'no long atoms'
    if not HAVE_SCIPY:
        return None, 'no scipy'
    Ve = {e: set(v for v in range(n) if p[e][v] > 0) for e, _ in edges}
    # variables q(e,v) for v notin V_e AND R[v] > 0
    var = []
    for ei, (e, rem) in enumerate(edges):
        for v in range(n):
            if v not in Ve[e] and R[v] > 0:
                var.append((ei, v))
    idx = {kv: i for i, kv in enumerate(var)}
    if not var:
        return False, 'atoms have no eligible ambient bank'
    nv = len(var)
    A_eq = np.zeros((len(edges), nv)); b_eq = np.zeros(len(edges))
    for ei, (e, rem) in enumerate(edges):
        b_eq[ei] = float(rem)
        has = False
        for v in range(n):
            if (ei, v) in idx:
                A_eq[ei, idx[(ei, v)]] = 1.0; has = True
        if not has:
            return False, ('edge %s (rem %s) has no ambient bank' % (e, rem))
    A_ub = np.zeros((n, nv)); b_ub = np.zeros(n)
    for v in range(n):
        b_ub[v] = float(R[v])
        for ei, (e, rem) in enumerate(edges):
            if (ei, v) in idx:
                A_ub[v, idx[(ei, v)]] = 1.0
    res = linprog(c=np.zeros(nv), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method='highs')
    return bool(res.success), ('feasible' if res.success else ('INFEASIBLE: %d long edges, maxell=%d' % (len(edges), max(ell.values()))))


def check_stage2(name, n, adj, side, acc2):
    if not Bconn(n, adj, side):
        return
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    acc2['cages'] += 1
    feas, detail = stage2_support_hall(n, cd)
    if feas is False:
        acc2['infeasible'] += 1
        if acc2['ex'] is None:
            acc2['ex'] = (name, n, detail, cd['ell'])


def main():
    ok, info = validate_k2t_model()
    print("K2 machinery self-validation vs K2T table:", "PASS" if ok else "FAIL", info)
    if not ok:
        print("ABORT: K2 formula does not reproduce the known table."); return
    print()
    acc = dict(cages=0, Rneg=0, ex=None, maxell=0)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            check_Rnonneg('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d done: Gamma-min cages %d, R[u]<0 cages %d" % (nn, acc['cages'], acc['Rneg']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            check_Rnonneg('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print()
    print("R[u] >= 0 CHECK (proven residual-sign lemma), Gamma-min scope, census N<=11 + even-cycle+chord N=18..30:")
    print("  cages checked: %d | max ell: %d | cages with some R[u]<0: %d" % (acc['cages'], acc['maxell'], acc['Rneg']))
    if acc['ex']:
        print("  *** R[u]<0 EXAMPLE: %s ***" % (acc['ex'],))
    print("VERDICT: %s" % ("R[u]>=0 holds on ALL %d Gamma-min cages (proven residual-sign lemma reproduced; K2 machinery validated) -- foundation for the support-restricted Hall gate"
                           % acc['cages'] if acc['Rneg'] == 0 else "R[u]<0 on %d cages -- SCOPE/BUG to investigate (contradicts the proven lemma)" % acc['Rneg']))
    print()
    print("STAGE 2: support-restricted Hall (route rem=max(0,ell^2-25-25) to vertex banks R[v], only v notin V_e; scipy=%s):" % HAVE_SCIPY)
    acc2 = dict(cages=0, infeasible=0, ex=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            check_stage2('cen%d' % nn, n, adj, best[0], acc2)
        print("  census N=%d: cages %d, INFEASIBLE %d" % (nn, acc2['cages'], acc2['infeasible']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            check_stage2('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc2)
    print("  cages checked: %d | support-restricted-Hall INFEASIBLE: %d" % (acc2['cages'], acc2['infeasible']))
    if acc2['ex']:
        print("  *** INFEASIBLE (support-restricted Hall fails -- decisive-obstruction candidate): %s ***" % (acc2['ex'],))
    print("STAGE-2 VERDICT: %s" % ("support-restricted Hall FEASIBLE on ALL %d Gamma-min cages (door+R[v]-ambient absorbs, respecting v notin V_e) -- strong support for PositiveSlackHallPrefix_FullBank"
                                  % acc2['cages'] if acc2['infeasible'] == 0 else "INFEASIBLE on %d Gamma-min cages -- failure mode 2 (wrong location) REALIZED; investigate (decisive-obstruction candidate)" % acc2['infeasible']))


if __name__ == '__main__':
    main()
