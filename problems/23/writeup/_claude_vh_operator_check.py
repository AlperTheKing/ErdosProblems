r"""Operator-identity + VH-validity + reroute-necessity checks (EXACT). 2026-07-08.

On two-lane (rho(K2)>N stress graph) + blow-ups + census:
 (A) Gamma = 1^T K2 1  (K2(v,w)=sum_e p_e(v)p_e(w))  == sum_v T[v]  == sum_e ell^2   [identity triple]
 (B) reroute-necessity: does max_v T[v] EXCEED N while Gamma<=N^2 ?  (=> geodesic routing infeasible pointwise;
     VH transportation feasibility genuinely needs re-routing away from hubs)
 (C) VH-VALIDITY: is the transportation-Hall  max_S ( sum_{e in S} ell^2 - N|V(S)| )  <= 0 on this REAL graph?
     If VH FAILS on a real (non-deficient) graph while Gamma<=N^2 holds, VH is STRICTLY STRONGER than the
     conjecture (a bad target). If VH holds with slack, it's a valid but possibly-hard target.
 (D) lambda_max(K2) vs N (spectral route liveness).
Run from problems/23/writeup: python _claude_vh_operator_check.py
"""
from fractions import Fraction as F
from itertools import combinations
import subprocess
from _h import Bconn, dec, maxcut_all, gmin, GENG
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import residuals, geos_paths
from _verify_two_lane import build_two_lane


def support_vertices(adj, side, e):
    Vs = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        Vs.update(P)
    return frozenset(Vs)


def full_check(name, n, adj, side):
    if not Bconn(n, adj, side):
        return None
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    M, ell, p, T = cd['M'], cd['ell'], cd['p'], cd['T']
    if not M:
        return None
    Gamma = sum(ell[e] ** 2 for e in M)
    sumT = sum(T)
    # 1^T K2 1 = sum_{v,w} sum_e p_e(v)p_e(w) = sum_e (sum_v p_e(v))^2 = sum_e ell(e)^2  (since sum_v p_e=ell)
    oneK2one = sum((sum(p[e][v] for v in range(n))) ** 2 for e in M)
    id_ok = (Gamma == sumT == oneK2one)
    maxT = max(T)
    hub = maxT > F(n)
    # VH exact over all subsets if few atoms
    Ve = {e: support_vertices(adj, side, e) for e in M}
    vh_min = None; binding = None
    atoms = list(M)
    if len(atoms) <= 22:
        for r in range(1, len(atoms) + 1):
            for S in combinations(atoms, r):
                dem = sum(ell[e] ** 2 for e in S)
                Vs = set()
                for e in S:
                    Vs |= Ve[e]
                slack = F(n) * len(Vs) - dem
                if vh_min is None or slack < vh_min:
                    vh_min = slack; binding = (r, len(Vs), dem)
        vh_exhaustive = True
    else:
        vh_exhaustive = False
        vh_min = F(n) * len({v for e in atoms for v in Ve[e]}) - Gamma  # S=all only
        binding = (len(atoms), '(all)', Gamma)
    return dict(name=name, n=n, m=len(M), Gamma=Gamma, Nsq=n * n, id_ok=id_ok,
                maxT=maxT, hub=hub, vh_min=vh_min, binding=binding, vh_exhaustive=vh_exhaustive,
                maxell=max(ell.values()))


def blowup(n0, E0, side0, q):
    n = n0 * q
    E = set()
    for (u, v) in E0:
        for i in range(q):
            for j in range(q):
                a = u * q + i; b = v * q + j; E.add((min(a, b), max(a, b)))
    side = [0] * n
    for v in range(n0):
        for i in range(q):
            side[v * q + i] = side0[v]
    adj = adj_from_edges(n, sorted(E))
    return n, adj, side


def main():
    print("VH operator/validity/reroute checks (EXACT)")
    print("=" * 100)
    rows = []
    for L in (8, 12, 16):
        n, E, side, bad = build_two_lane(L)
        adj = adj_from_edges(n, E)
        r = full_check('twolane L=%d' % L, n, adj, side)
        if r: rows.append(r)
        # blow-ups
        for q in (2, 3):
            n0, E0, side0 = n, E, side
            nn, adjq, sideq = blowup(n0, E0, side0, q)
            if nn <= 80:
                r = full_check('twolane L=%d x%d' % (L, q), nn, adjq, sideq)
                if r: rows.append(r)
    for r in rows:
        print("  %-18s N=%2d m=%2d Gamma=%4d N^2=%4d G<=N^2:%s | id:%s maxT=%5s hub(>N):%s | VH_min=%5s bind=%s %s"
              % (r['name'], r['n'], r['m'], r['Gamma'], r['Nsq'], r['Gamma'] <= r['Nsq'],
                 r['id_ok'], str(r['maxT']), r['hub'], str(r['vh_min']), r['binding'],
                 '' if r['vh_exhaustive'] else '(S=all only)'))
    print()
    idbad = [r for r in rows if not r['id_ok']]
    print("  IDENTITY Gamma=sumT=1^T K2 1: %s" % ("ALL PASS" if not idbad else "FAIL %s" % idbad))
    hubs = [r for r in rows if r['hub']]
    print("  REROUTE-NECESSITY: %d/%d graphs have a T-hub max_v T[v] > N (geodesic routing infeasible pointwise, "
          "yet Gamma<=N^2) -> VH needs genuine rerouting" % (len(hubs), len(rows)))
    for r in hubs[:6]:
        print("     hub: %s maxT=%s > N=%d  Gamma=%d<=N^2=%d" % (r['name'], r['maxT'], r['n'], r['Gamma'], r['Nsq']))
    vhfail = [r for r in rows if r['vh_min'] is not None and r['vh_min'] < 0]
    print("  VH-VALIDITY on real graphs: %d/%d have VH violation (vh_min<0). "
          "If >0, VH is STRICTLY STRONGER than the conjecture (bad target)." % (len(vhfail), len(rows)))
    if vhfail:
        for r in vhfail[:6]:
            print("     *** VH FAILS on REAL graph: %s vh_min=%s binding=%s (Gamma=%d<=N^2=%d) => VH too strong!"
                  % (r['name'], r['vh_min'], r['binding'], r['Gamma'], r['Nsq']))
    # also a census sweep for VH validity + hub
    print()
    print("  CENSUS N<=10 Gamma-min: VH-violations and T-hubs (both should be tracked)")
    cvh = 0; chub = 0; ccage = 0; worst = None
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            r = full_check('cen%d' % nn, n, adj, best[0])
            if r is None:
                continue
            ccage += 1
            if r['hub']:
                chub += 1
            if r['vh_min'] is not None and r['vh_min'] < 0:
                cvh += 1
            if worst is None or (r['vh_min'] is not None and r['vh_min'] < worst[1]):
                worst = (r['name'], r['vh_min'])
        print("    census N=%d done: cages=%d VH-violations=%d T-hubs=%d" % (nn, ccage, cvh, chub), flush=True)
    print("  CENSUS TOTAL: cages=%d VH-violations=%d T-hubs=%d worst VH-slack=%s" % (ccage, cvh, chub, worst))


if __name__ == '__main__':
    main()
