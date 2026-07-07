r"""AMBIENT SHADOW gate for gap#1's true wall (GPT-Pro 2026-07-08): PositiveSlackHallPrefix_FullBank / AmbientShadowLoadBound.

GPT-Pro reduced the full-bank absorption wall to a per-vertex charge/capacity inequality and gave a GRAPH-COMPUTABLE
diagnostic cap: cap(v) = N - T(v), where T(v) = sum_{e in M} ell(e)*p_e(v) is the vertex load (loads() T[v]), so
sum_v cap(v) = N^2 - Gamma = reserveResidual. Each bad edge e has surplus rem(e) = ell(e)^2 - 25, spread over the
N-|V_e| AMBIENT vertices off its geodesic support V_e. The wall's per-vertex form:
   for every vertex v:  sum_{e: v notin V_e} rem(e)/(N-|V_e|)  <=  cap(v)      (UNIFORM charge)
and the STRONGER max-flow feasibility (a nonuniform flow may fit even if uniform overcharges):
   exists q(e,v)>=0, q(e,v)=0 if v in V_e, sum_{v notin V_e} q(e,v) = rem(e), sum_e q(e,v) <= cap(v).
GPT-Pro: "cap=N-T(v) is a STRONG DIAGNOSTIC gate, not the official cap_i(v) unless rowDB AmbientCap dominates it."
C_18 calibration: rem=56 door-deficit=31 spread 31/9 over 9 outside vertices; cap=18 there => passes.

EXACT rational (Fraction). COVERAGE stated explicitly (the C_18 lesson: a battery over too-small N is an artifact --
this gate covers census N<=11 AND the even-cycle+chord family N=18,22,26,30, where the single-row long-annulus escapes
live). PASS across families with N>=18 = strong support that the natural cap=N-T(v) absorbs the surpluses. A vertex
with load>cap (uniform) that ALSO fails the LP feasibility = the decisive obstruction (cap=N-T(v) insufficient). Run
from problems/23/writeup.  Usage: python _claude_ambient_shadow_gate.py
"""
from fractions import Fraction as F
from collections import deque
from itertools import combinations
import sys
from _h import dec, maxcut_all, loads, Bconn, GENG
from _codex_k2t_switch_probe import adj_from_edges

# DOOR PRECHARGE: each bad edge first draws one 25-door-token (crude per-cage 25*sigma proxy); ambient pays the rest.
# rem(a) = max(0, surplus - DOOR_PRECHARGE). DOOR_PRECHARGE=0 -> ambient-only (strongest); =25 -> door+ambient.
DOOR_PRECHARGE = 25

try:
    from scipy.optimize import linprog
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


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


def cut_data(n, adj, side):
    """From a max cut (side), compute M (bad edges), ell, V_e (geodesic support), T[v] load, cap[v]=n-T[v]."""
    M = [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] == side[b]]
    ell = {}; Ve = {}; T = [F(0)] * n
    Tlist = [F(0) for _ in range(n)]
    ok = True
    for f in M:
        Ps = geos_paths(adj, side, f[0], f[1])
        if not Ps:
            ok = False; break
        L = len(Ps[0])  # odd-cycle length ell = (#edges in shortest cut path)+1 = #vertices in the path
        ell[f] = L
        supp = set()
        for P in Ps:
            supp.update(P)
        Ve[f] = supp
        nf = len(Ps)
        share = F(L, nf)
        for P in Ps:
            for v in P:
                Tlist[v] += share
    if not ok:
        return None
    cap = [F(n) - Tlist[v] for v in range(n)]
    return dict(M=M, ell=ell, Ve=Ve, T=Tlist, cap=cap)


def uniform_check(n, cd):
    """load(v) = sum_{e: v notin V_e} rem(e)/(n-|V_e|); pass iff load(v) <= cap(v) all v. Returns (ok, worst, zeroamb)."""
    load = [F(0)] * n
    loadl = [F(0) for _ in range(n)]
    zeroamb = []
    for e in cd['M']:
        rem = max(0, cd['ell'][e] ** 2 - 25 - DOOR_PRECHARGE)
        if rem <= 0:
            continue
        amb = n - len(cd['Ve'][e])
        if amb <= 0:
            zeroamb.append((e, rem)); continue
        share = F(rem, amb)
        for v in range(n):
            if v not in cd['Ve'][e]:
                loadl[v] += share
    worst = None
    ok = True
    for v in range(n):
        if loadl[v] > cd['cap'][v]:
            ok = False
            slack = loadl[v] - cd['cap'][v]
            if worst is None or slack > worst[1]:
                worst = (v, slack, float(loadl[v]), float(cd['cap'][v]))
    return ok, worst, zeroamb, loadl


def lp_feasible(n, cd):
    """Max-flow/transportation feasibility: route each bad edge's rem to ambient vertices within cap. Exact-ish via LP."""
    if not HAVE_SCIPY:
        return None
    edges = [e for e in cd['M'] if max(0, cd['ell'][e] ** 2 - 25 - DOOR_PRECHARGE) > 0]
    if not edges:
        return True
    # variables q(e,v) for v notin V_e. Minimize 0 s.t. sum_v q=rem(e) (eq), sum_e q<=cap(v) (ub), q>=0.
    var = []
    for ei, e in enumerate(edges):
        for v in range(n):
            if v not in cd['Ve'][e]:
                var.append((ei, v))
    idx = {kv: i for i, kv in enumerate(var)}
    if not var:
        return False  # some edge has no ambient room
    import numpy as np
    nv = len(var)
    # equality: per edge sum = rem
    A_eq = np.zeros((len(edges), nv)); b_eq = np.zeros(len(edges))
    for ei, e in enumerate(edges):
        rem = max(0, cd['ell'][e] ** 2 - 25 - DOOR_PRECHARGE)
        b_eq[ei] = float(rem)
        has = False
        for v in range(n):
            if (ei, v) in idx:
                A_eq[ei, idx[(ei, v)]] = 1.0; has = True
        if not has:
            return False
    # inequality: per vertex sum <= cap
    A_ub = np.zeros((n, nv)); b_ub = np.zeros(n)
    for v in range(n):
        b_ub[v] = float(cd['cap'][v])
        for ei, e in enumerate(edges):
            if (ei, v) in idx:
                A_ub[v, idx[(ei, v)]] = 1.0
    res = linprog(c=np.zeros(nv), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method='highs')
    return bool(res.success)


def analyze(name, n, adj, side):
    if not Bconn(n, adj, side):
        return None
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return None
    cd = cut_data(n, adj, side)
    if cd is None:
        return None
    uok, worst, zeroamb, loadl = uniform_check(n, cd)
    res = dict(name=name, n=n, m=len(cd['M']), maxell=max(cd['ell'].values()) if cd['ell'] else 0,
               uniform_ok=uok, worst=worst, zeroamb=zeroamb)
    if not uok or zeroamb:
        res['lp'] = lp_feasible(n, cd)
    else:
        res['lp'] = True
    return res


def even_cycle_chord(n, chord):
    E = [(i, (i + 1) % n) for i in range(n)] + [chord]
    adj = adj_from_edges(n, E)
    side = [i % 2 for i in range(n)]
    return n, adj, side


def run_census(maxn, acc):
    import subprocess
    for nn in range(5, maxn + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = adj_from_edges(n, E)
            for side in maxcut_all(n, adj):
                r = analyze('cen%d' % nn, n, adj, side)
                if r:
                    acc.append(r)
        print('  census N=%d done (rows so far %d, uniform_fail %d, lp_fail %d)'
              % (nn, len(acc), sum(1 for r in acc if not r['uniform_ok']), sum(1 for r in acc if r['lp'] is False)), flush=True)


def summarize(label, acc):
    ufail = [r for r in acc if not r['uniform_ok']]
    lpfail = [r for r in acc if r['lp'] is False]
    za = [r for r in acc if r['zeroamb']]
    print('=' * 70)
    print('AMBIENT SHADOW GATE (cap=N-T(v)):', label)
    print('  rows: %d | max ell seen: %d' % (len(acc), max((r['maxell'] for r in acc), default=0)))
    print('  UNIFORM charge fails: %d | zero-ambient-room edges: %d | LP-feasibility FAILS: %d'
          % (len(ufail), len(za), len(lpfail)))
    if ufail[:3]:
        for r in ufail[:3]:
            print('   uniform-overcharge %s N=%d maxell=%d worst_v=%s lp=%s' % (r['name'], r['n'], r['maxell'], r['worst'], r['lp']))
    if lpfail:
        for r in lpfail[:5]:
            print('   *** LP-INFEASIBLE %s N=%d maxell=%d zeroamb=%s ***' % (r['name'], r['n'], r['maxell'], r['zeroamb']))
    ok = len(lpfail) == 0
    print('VERDICT: %s' % ('cap=N-T(v) ABSORBS all surpluses (LP-feasible everywhere) -- strong support for PositiveSlackHallPrefix_FullBank with the natural cap'
                           if ok else 'LP-INFEASIBLE on %d rows -- cap=N-T(v) insufficient (decisive: natural cap does NOT absorb; needs a smarter rowDB tau OR the wall is problematic)' % len(lpfail)))
    return ok


def main():
    print('scipy available:', HAVE_SCIPY)
    acc = []
    run_census(11, acc)
    summarize('CENSUS N<=11', acc)
    print()
    # even-cycle + chord family (N>=18): the single-row long-annulus escapes (C_18 generalization)
    acc2 = []
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            r = analyze('C%d+chord(0,%d)' % (n, gap), *even_cycle_chord(n, (0, gap)))
            if r:
                acc2.append(r)
    summarize('EVEN-CYCLE+CHORD N=18,22,26,30 (single-row long annuli, incl C_18-type)', acc2)


if __name__ == '__main__':
    main()
