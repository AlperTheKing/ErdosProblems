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

STAGE 1: verify R[u] >= 0 (the PROVEN residual-sign lemma) exactly on census Gamma-min + even-cycle+chord N>=18.
STAGE 2: whole-cage support-restricted Hall feasibility (max-flow; GENEROUS pooled door 25*sigma) -- necessary-condition all-subset Hall.
STAGE 3: K2-support component decomposition. Verifies (a) K2-closure, (b) split identity R_full(X)=R_local(X)+(N-|VX|)*T_sum(X),
  (c) failure-mode-1 test R_local(X)>=0 vs Demand(X). FINDING (census N<=11 + even-chord N=18-30, 71894 components):
  closure+identity EXACT everywhere; R_local<0 occurs but ONLY at Demand(X)=0 components => the clean lemma
  R_local(X)<0 => Demand(X)=0 (failure mode 1 harmless); and Demand(X)<=R_full(X) on EVERY component (0 uncovered).
KEY IDENTITY (K2-closure): sum_{u in V_X} T(u) = sum_{e in X} ell(e)^2 = Gamma_X (component's exact contribution to Gamma).
  => R_full(X) = N*Gamma_X - sum_{e in X} ell(e)*edge_dot(e), edge_dot(e)=sum_w p_e(w)T(w). The GERSH aggregation at component level.
EXACT rational (Fraction). Gamma-min scope. Coverage stated (C_18 lesson: incl N>=18). Run from problems/23/writeup.
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


def stage2_support_hall(n, adj, side, cd):
    """STAGE 2 (corrected): whole-cage support-restricted Hall. Route each bad edge's FULL surplus ell^2-25 to a
    shared DOOR sink (cap 25*sigma, sigma=#cutedges-m, all atoms eligible) + vertex banks cap=R[v] (edge e -> v iff
    v notin V_e, the support restriction = failure mode 2). Max-flow feasibility (LP). Returns (feasible, detail)."""
    M, ell, p, R = cd['M'], cd['ell'], cd['p'], cd['R']
    cut_edges = sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])
    sigma = cut_edges - len(M)
    door_cap = F(25) * sigma
    edges = [(e, F(ell[e] ** 2 - 25)) for e in M if ell[e] ** 2 - 25 > 0]
    if not edges:
        return True, 'no surplus'
    if not HAVE_SCIPY:
        return None, 'no scipy'
    Ve = {e: set(v for v in range(n) if p[e][v] > 0) for e, _ in edges}
    # sinks: index 0 = door; index 1+v = vertex v (cap R[v]). var q(e, sink).
    var = []
    for ei, (e, rem) in enumerate(edges):
        var.append((ei, 'door'))
        for v in range(n):
            if v not in Ve[e] and R[v] > 0:
                var.append((ei, v))
    idx = {kv: i for i, kv in enumerate(var)}
    nv = len(var)
    A_eq = np.zeros((len(edges), nv)); b_eq = np.zeros(len(edges))
    for ei, (e, rem) in enumerate(edges):
        b_eq[ei] = float(rem)
        for kv, i in idx.items():
            if kv[0] == ei:
                A_eq[ei, i] = 1.0
    # capacity rows: door + each vertex
    sinks = ['door'] + [v for v in range(n)]
    A_ub = np.zeros((len(sinks), nv)); b_ub = np.zeros(len(sinks))
    b_ub[0] = float(door_cap)
    for si, s in enumerate(sinks):
        cap = door_cap if s == 'door' else R[s]
        b_ub[si] = float(cap)
        for kv, i in idx.items():
            if kv[1] == s:
                A_ub[si, i] = 1.0
    res = linprog(c=np.zeros(nv), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method='highs')
    return bool(res.success), ('feasible' if res.success else ('INFEASIBLE sigma=%d door=%s surplus=%s maxell=%d'
                               % (sigma, door_cap, sum(r for _, r in edges), max(ell.values()))))


def k2_components(n, cd):
    """K2-support component decomposition: atoms (bad edges) union-merged when their supports V_e overlap.
    Returns list of dicts {atoms:[e...], VX:set, T_sum:F}. By construction each component is K2-CLOSED (every atom
    whose support touches V_X is in the component), so (K2*T)(u)=(K2_X*T)(u) for u in V_X -- verified in stage3."""
    M, p = cd['M'], cd['p']
    Ve = {e: frozenset(v for v in range(n) if p[e][v] > 0) for e in M}
    parent = {e: e for e in M}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)
    for i in range(len(M)):
        for j in range(i + 1, len(M)):
            if Ve[M[i]] & Ve[M[j]]:
                union(M[i], M[j])
    groups = {}
    for e in M:
        groups.setdefault(find(e), []).append(e)
    comps = []
    for atoms in groups.values():
        VX = set()
        for e in atoms:
            VX |= Ve[e]
        comps.append(dict(atoms=atoms, VX=VX, T_sum=sum(cd['T'][u] for u in VX)))
    return comps


def stage3_component_gate(n, sigma, cd):
    """STAGE 3 (per-K2-component). For each component X, EXACT checks:
      * K2-CLOSURE self-check: (K2_X*T)(u) == K2T[u] for u in V_X (all atoms touching u are inside X);
      * IDENTITY: R_full(X) = R_local(X) + (N-|V_X|)*T_sum(X) [validates the decomposition split];
      * FAILURE-MODE-1: R_local(X) >= 0 ?  (R_local<0 harmless iff Demand(X)=0);
      * COVERAGE (ALL components, not just R_local<0): Demand(X) <= R_full(X)  [residual alone -- FALSE in general,
        e.g. C_7: R_full=0, Demand=24; the door is essential] and Demand(X) <= 25*sigma + R_full(X) [generous
        whole-graph door pooled -- necessary-condition, matches STAGE 2].  sigma = whole-graph cutedges - m.
    Demand(X)=sum_{e in X}(ell^2-25); ell>=5 in triangle-free graphs so ell^2-25>=0 always."""
    M, ell, p, T, K2T, R = cd['M'], cd['ell'], cd['p'], cd['T'], cd['K2T'], cd['R']
    edge_dot = {e: sum(p[e][w] * T[w] for w in range(n)) for e in M}
    door = F(25) * sigma
    comps = k2_components(n, cd)
    closure_ok = True; identity_ok = True
    rlocal_min = None; rneg = 0; worst = None
    dangerous = 0; danger_ex = None
    unc_Rfull = 0; unc_door = 0; unc_door_ex = None
    for X in comps:
        VX = X['VX']; nV = len(VX); atomsX = set(X['atoms'])
        for u in VX:
            k2x = sum(p[e][u] * edge_dot[e] for e in atomsX)
            if k2x != K2T[u]:
                closure_ok = False
        R_full = sum(R[u] for u in VX)
        R_local = sum(F(nV) * T[u] - K2T[u] for u in VX)
        ambient = F(n - nV) * X['T_sum']
        if R_full != R_local + ambient:
            identity_ok = False
        Demand = sum(ell[e] ** 2 - 25 for e in atomsX)  # ell>=5 => each term >=0
        if Demand > R_full:
            unc_Rfull += 1
        if Demand > door + R_full:  # generous whole-graph door + residual; a FAIL here is a real necessary-condition breach
            unc_door += 1
            if unc_door_ex is None:
                unc_door_ex = dict(nV=nV, natoms=len(atomsX), Demand=str(Demand), R_full=str(R_full),
                                   door=str(door), maxell=max(ell[e] for e in atomsX))
        if R_local < 0:
            rneg += 1
            if Demand > 0:
                dangerous += 1
                if danger_ex is None:
                    danger_ex = dict(nV=nV, natoms=len(atomsX), R_local=str(R_local), R_full=str(R_full),
                                     Demand=str(Demand), maxell=max(ell[e] for e in atomsX))
        if rlocal_min is None or R_local < rlocal_min:
            rlocal_min = R_local
            worst = dict(nV=nV, natoms=len(atomsX), R_local=str(R_local), R_full=str(R_full),
                         Demand=str(Demand), maxell=max(ell[e] for e in atomsX))
    return dict(ncomp=len(comps), closure_ok=closure_ok, identity_ok=identity_ok,
                rlocal_min=rlocal_min, rlocal_neg=rneg, worst=worst,
                dangerous=dangerous, danger_ex=danger_ex,
                unc_Rfull=unc_Rfull, unc_door=unc_door, unc_door_ex=unc_door_ex)


def check_stage3(name, n, adj, side, acc3):
    if not Bconn(n, adj, side):
        return
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    cut_edges = sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])
    sigma = cut_edges - len(cd['M'])
    r = stage3_component_gate(n, sigma, cd)
    acc3['cages'] += 1
    acc3['ncomp'] += r['ncomp']
    if not r['closure_ok']:
        acc3['closure_fail'] += 1
        if acc3['clex'] is None:
            acc3['clex'] = (name, n)
    if not r['identity_ok']:
        acc3['identity_fail'] += 1
        if acc3['idex'] is None:
            acc3['idex'] = (name, n)
    if r['rlocal_neg']:
        acc3['rlocal_neg_cages'] += 1
        if acc3['rlex'] is None or (r['rlocal_min'] is not None and r['rlocal_min'] < F(acc3['rlex'][2])):
            acc3['rlex'] = (name, n, str(r['rlocal_min']), r['worst'])
    if r['dangerous']:
        acc3['dangerous_cages'] += 1
        acc3['dangerous_comps'] += r['dangerous']
        if acc3['dgex'] is None:
            acc3['dgex'] = (name, n, r['danger_ex'])
    acc3['unc_Rfull'] += r['unc_Rfull']
    if r['unc_door']:
        acc3['unc_door'] += r['unc_door']
        if acc3['unc_door_ex'] is None:
            acc3['unc_door_ex'] = (name, n, r['unc_door_ex'])


def check_stage2(name, n, adj, side, acc2):
    if not Bconn(n, adj, side):
        return
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    acc2['cages'] += 1
    feas, detail = stage2_support_hall(n, adj, side, cd)
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
    print("STAGE 2: support-restricted Hall, WHOLE-CAGE POOLED door (route full surplus ell^2-25 to shared door sink"
          " cap 25*sigma [sigma=cutedges-m, all atoms eligible] + vertex banks R[v], edge->v iff v notin V_e; scipy=%s)."
          "\n  NOTE: pooled door is GENEROUS (per-cage door is smaller); a pass is a NECESSARY-condition all-subset-Hall"
          " check, NOT the tight per-cage theorem. STAGE 3 tightens to per-K2-component doors." % HAVE_SCIPY)
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
    print()
    print("STAGE 3: K2-support component decomposition -- closure self-check + identity R_full=R_local+(N-|VX|)*T_sum")
    print("  + FAILURE-MODE-1 test R_local(X)>=0 (the 'wrong split' mode; NOT implied by R[u]>=0). Graph-computable, exact.")
    acc3 = dict(cages=0, ncomp=0, closure_fail=0, identity_fail=0, rlocal_neg_cages=0, clex=None, idex=None, rlex=None,
                dangerous_cages=0, dangerous_comps=0, dgex=None, unc_Rfull=0, unc_door=0, unc_door_ex=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            check_stage3('cen%d' % nn, n, adj, best[0], acc3)
        print("  census N=%d: cages %d, comps %d, R_local<0 cages %d, DANGEROUS(R_local<0&Demand>0) %d, unc-by-Rfull(door-needed) %d, unc-by-door+Rfull %d"
              % (nn, acc3['cages'], acc3['ncomp'], acc3['rlocal_neg_cages'], acc3['dangerous_comps'], acc3['unc_Rfull'], acc3['unc_door']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            check_stage3('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc3)
    print("  TOTAL: cages %d, components %d | closure_fail %d | identity_fail %d | R_local<0 cages %d"
          % (acc3['cages'], acc3['ncomp'], acc3['closure_fail'], acc3['identity_fail'], acc3['rlocal_neg_cages']))
    print("  DANGEROUS (R_local<0 AND Demand>0): %d | comps needing the DOOR (Demand>R_full, residual alone insufficient): %d | comps UNCOVERED even by 25*sigma+R_full: %d"
          % (acc3['dangerous_comps'], acc3['unc_Rfull'], acc3['unc_door']))
    if acc3['clex']:
        print("  *** K2-CLOSURE FAILED (decomposition bug): %s ***" % (acc3['clex'],))
    if acc3['idex']:
        print("  *** IDENTITY FAILED (split bug): %s ***" % (acc3['idex'],))
    if acc3['rlex']:
        print("  R_local<0 worst (harmless if Demand=0): %s" % (acc3['rlex'],))
    if acc3['dgex']:
        print("  *** DANGEROUS example (R_local<0 at positive-demand comp): %s ***" % (acc3['dgex'],))
    if acc3['unc_door_ex']:
        print("  *** UNCOVERED even by door+residual (necessary-condition breach candidate): %s ***" % (acc3['unc_door_ex'],))
    ok3 = acc3['closure_fail'] == 0 and acc3['identity_fail'] == 0
    print("STAGE-3 VERDICT: %s" % (
        ("decomposition VALID (closure+identity exact). Failure mode 1: R_local<0 on %d cages but 0 DANGEROUS (R_local<0 => Demand=0, harmless). "
         "COVERAGE: residual R_full ALONE is insufficient on %d components (the DOOR is essential, e.g. C_7: R_full=0<24=Demand); "
         "with the generous pooled door 25*sigma+R_full, %d components remain uncovered. %s"
         % (acc3['rlocal_neg_cages'], acc3['unc_Rfull'], acc3['unc_door'],
            "So per-component Demand<=25*sigma+R_full holds everywhere (necessary-condition; door+residual bank suffices) -- consistent with STAGE 2." if acc3['dangerous_comps'] == 0 and acc3['unc_door'] == 0 else
            "DANGEROUS/uncovered components exist -- examine (decisive-obstruction candidate)."))
        if ok3 else
        "DECOMPOSITION BUG (closure_fail=%d identity_fail=%d) -- fix before trusting" % (acc3['closure_fail'], acc3['identity_fail'])))


if __name__ == '__main__':
    main()
