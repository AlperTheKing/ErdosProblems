r"""EXACT gate for GPT-Pro's Route-B pair-door proof (gap #1, 2026-07-07, GAP1_ROUTEB_PAIRDOOR_PROOF_GPTPRO.md).

On the stretched nested type-B L/(L+2) cores (build from _l5forcing_gate) with the canonical pair-door
terminal-shadow U={s,u,a1}={0,1,5}, verify EXACTLY (integer BFS on cut edges) the checkable claims of GPT-Pro's
proof:
 (a) §9.2 no-cross from max-cutness: |deltaB(U)|=2 (=born0,born1), |deltaM(U)|=2, deltaM(U)={f0,f1}={oldLo,oldHi}.
 (b) PairDoorConvex(B, U, born0,born1): dist_HU(u0,u1) <= 2+dist_HW(w0,w1) AND dist_HW <= 2+dist_HU (cut-graph
     distances within U and within W=V\U).  [convexity BEFORE switch]
 (c) PairDoorConvex(B^U, U, oldLo,oldHi): same two inequalities for the switched cut with doors {f0,f1}. [AFTER]
 (d) induced cut-graph invariance: cut edges within U identical in B and B^U; cut edges within W identical.
 (e) metric stability: for every STABLE bad edge e (in M, not crossing U), ell_B(e) = ell_{B^U}(e).
 (f) sides connected: induced graph G[U] connected and G[V\U] connected.
 (g) strict drop: Gamma(B)-Gamma(B^U) = ell(f0)^2+ell(f1)^2 - ell'(born0)^2 - ell'(born1)^2 >= 4L+4 > 0.
ell(e) = bdist_restr(adj,side,e)+1 (odd-cycle length). All checks EXACT. Run from problems/23/writeup.
NOTE: battery pass = annotation of the L-uniform CAP residuals (#1,#2,#3 of the closure list), NOT a proof of the
GENERAL CAP_PairDoorConvexity lemma (all cages) nor the §9.8 token-bank decomposition -- those remain GPT-Pro's.
"""
from collections import deque
from _l5forcing_gate import build, edge


def cut_bfs(adj, side, S, a, b):
    """shortest-path distance (in edges) a->b using ONLY cut edges with BOTH endpoints in S. -1 if unreachable."""
    if a == b:
        return 0
    if a not in S or b not in S:
        return -1
    d = {a: 0}
    q = deque([a])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v in S and side[u] != side[v] and v not in d:
                d[v] = d[u] + 1
                if v == b:
                    return d[v]
                q.append(v)
    return d.get(b, -1)


def graph_bfs_connected(adj, S):
    """is the induced graph G[S] connected (all graph edges within S)?"""
    S = list(S)
    if not S:
        return True
    seen = {S[0]}
    q = deque([S[0]])
    Sset = set(S)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v in Sset and v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == len(Sset)


def ell_of(adj, side, e):
    """odd-cycle length of bad edge e under `side` = (cut-distance in edges)+1. -1 if no cut-path."""
    a, b = e
    d = {a: 0}
    q = deque([a])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u] + 1
                q.append(v)
    db = d.get(b, -1)
    return db + 1 if db >= 0 else -1


def cutedges_within(adj, side, S):
    out = set()
    for u in S:
        for v in adj[u]:
            if v in S and u < v and side[u] != side[v]:
                out.add((u, v))
    return out


def door_endpoints(door, U):
    """return (uEnd in U, wEnd in W) for a crossing edge door."""
    a, b = door
    return (a, b) if a in U else (b, a)


def convex_check(adj, side, U, doors):
    """PairDoorConvex: dist_HU(u0,u1)<=2+dist_HW(w0,w1) and dist_HW<=2+dist_HU. Returns (ok, detail)."""
    S = set(range(len(adj)))
    W = S - U
    d0, d1 = doors
    u0, w0 = door_endpoints(d0, U)
    u1, w1 = door_endpoints(d1, U)
    dU = cut_bfs(adj, side, U, u0, u1)
    dW = cut_bfs(adj, side, W, w0, w1)
    # unreachable within a side => that induced distance is +inf; convexity inequality with inf on the LHS fails.
    INF = 10 ** 9
    dUv = INF if dU < 0 else dU
    dWv = INF if dW < 0 else dW
    c1 = dUv <= 2 + dWv
    c2 = dWv <= 2 + dUv
    return (c1 and c2), dict(u0=u0, u1=u1, w0=w0, w1=w1, dU=dU, dW=dW, c1=c1, c2=c2)


def analyze(L):
    n, E, side, f0, f1, adj, bip = build(L)
    if not bip:
        return dict(L=L, ok=False, why="blue not bipartite")
    U = {0, 1, 5}  # s,u,a1
    fe0, fe1 = edge(*f0), edge(*f1)
    # classify crossing edges
    deltaB = []  # cut edges crossing U (become bad) = born0,born1
    deltaM = []  # bad edges crossing U (become cut) = oldLo,oldHi
    for a, b in E:
        cross = (a in U) ^ (b in U)
        if not cross:
            continue
        e = edge(a, b)
        if side[a] != side[b]:
            deltaB.append(e)
        else:
            deltaM.append(e)
    res = dict(L=L, n=n, U=sorted(U), deltaB=sorted(deltaB), deltaM=sorted(deltaM))
    # (a) no-cross exact
    res['a_deltaB2'] = (len(deltaB) == 2)
    res['a_deltaM2'] = (len(deltaM) == 2)
    res['a_deltaM_is_f0f1'] = (set(deltaM) == {fe0, fe1})
    if len(deltaB) != 2:
        res['ok'] = False
        res['why'] = "deltaB != 2"
        return res
    born0, born1 = deltaB
    # ell before
    ellB = {}
    M = [edge(a, b) for a, b in E if side[a] == side[b]]
    for e in M:
        ellB[e] = ell_of(adj, side, e)
    res['ell_f0'] = ellB.get(fe0, -1)
    res['ell_f1'] = ellB.get(fe1, -1)
    res['a_ellf0_L'] = (ellB.get(fe0) == L)
    res['a_ellf1_Lp2'] = (ellB.get(fe1) == L + 2)
    # (b) convexity before
    okB, detB = convex_check(adj, side, U, (born0, born1))
    res['b_convB'] = okB
    res['b_detB'] = detB
    # switch
    side_U = [side[i] ^ (1 if i in U else 0) for i in range(n)]
    # ell after
    ellU = {}
    M_U = [edge(a, b) for a, b in E if side_U[a] == side_U[b]]
    for e in M_U:
        ellU[e] = ell_of(adj, side_U, e)
    res['born_ells'] = sorted(ellU.get(e, -1) for e in deltaB)
    res['g_born_le_L'] = all(ellU.get(e, 10 ** 9) <= L for e in deltaB)
    # deltaB(B^U) should be {f0,f1}
    deltaB_U = []
    for a, b in E:
        if ((a in U) ^ (b in U)) and side_U[a] != side_U[b]:
            deltaB_U.append(edge(a, b))
    res['c_deltaBU_is_f0f1'] = (set(deltaB_U) == {fe0, fe1})
    # (c) convexity after (doors = f0,f1)
    okC, detC = convex_check(adj, side_U, U, (fe0, fe1))
    res['c_convBU'] = okC
    res['c_detC'] = detC
    # (d) induced cut-graph invariance
    W = set(range(n)) - U
    res['d_UU_inv'] = (cutedges_within(adj, side, U) == cutedges_within(adj, side_U, U))
    res['d_WW_inv'] = (cutedges_within(adj, side, W) == cutedges_within(adj, side_U, W))
    # (e) metric stability on stable bad edges
    stable = [e for e in M if e not in {fe0, fe1}]  # bad, not crossing (f0,f1 are the only crossing bad edges)
    changed = []
    for e in stable:
        if ellU.get(e, None) != ellB.get(e, None):
            changed.append((e, ellB.get(e), ellU.get(e)))
    res['e_stable_changed'] = changed
    res['e_metric_stable'] = (len(changed) == 0)
    # (f) sides connected
    res['f_GU_conn'] = graph_bfs_connected(adj, U)
    res['f_GW_conn'] = graph_bfs_connected(adj, W)
    # (g) strict drop
    gB = sum(ellB[e] ** 2 for e in M)
    gBU = sum(ellU[e] ** 2 for e in M_U)
    res['gamma_B'] = gB
    res['gamma_BU'] = gBU
    res['drop'] = gB - gBU
    res['g_drop_ge_4Lp4'] = (gB - gBU >= 4 * L + 4)
    res['g_drop_eq_4Lp4'] = (gB - gBU == 4 * L + 4)
    # overall
    checks = ['a_deltaB2', 'a_deltaM2', 'a_deltaM_is_f0f1', 'a_ellf0_L', 'a_ellf1_Lp2',
              'b_convB', 'c_deltaBU_is_f0f1', 'c_convBU', 'd_UU_inv', 'd_WW_inv',
              'e_metric_stable', 'f_GU_conn', 'f_GW_conn', 'g_born_le_L', 'g_drop_ge_4Lp4']
    res['ok'] = all(res[c] for c in checks)
    res['failed'] = [c for c in checks if not res[c]]
    return res


def main():
    print("Route-B pair-door convexity/no-cross/metric-stability gate (U={s,u,a1}):")
    allok = True
    for L in [5, 7, 9, 11, 13, 15]:
        r = analyze(L)
        if not r.get('ok'):
            allok = False
        print("L=%2d n=%2d ok=%s | ellf0=%s ellf1=%s born_ells=%s drop=%s(4L+4=%d,eq=%s) | convB=%s convBU=%s | "
              "deltaM=f0f1:%s deltaBU=f0f1:%s | induced UU/WW:%s/%s | metric_stable:%s (chg=%s) | sides UU/WW:%s/%s"
              % (L, r.get('n', -1), r.get('ok'),
                 r.get('ell_f0'), r.get('ell_f1'), r.get('born_ells'), r.get('drop'), 4 * L + 4,
                 r.get('g_drop_eq_4Lp4'), r.get('b_convB'), r.get('c_convBU'),
                 r.get('a_deltaM_is_f0f1'), r.get('c_deltaBU_is_f0f1'), r.get('d_UU_inv'), r.get('d_WW_inv'),
                 r.get('e_metric_stable'), r.get('e_stable_changed'), r.get('f_GU_conn'), r.get('f_GW_conn')))
        if r.get('failed'):
            print("      FAILED CHECKS: %s | convB detail=%s | convBU detail=%s" %
                  (r['failed'], r.get('b_detB'), r.get('c_detC')))
    print()
    print("VERDICT: Route-B pair-door structural claims %s on stretched L=5..15" %
          ("ALL PASS (a-g) => L-uniform CAP residuals #1,#2,#3 battery-validated (NOT the general proof)"
           if allok else "FAIL at some L => residual convexity/connectivity blocker exposed"))


if __name__ == '__main__':
    main()
