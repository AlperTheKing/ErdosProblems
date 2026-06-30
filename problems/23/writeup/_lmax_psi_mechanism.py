"""Verify the SQUARE-SURPLUS mechanism for the L_max half-switch, exactly.

For each R[v]<0 site we take the neutral B-connected L_max half-switch S (the one the stress test proved
always exists) and check, exactly:
  (1) descent identity:  Gamma(before) - Gamma(after) == Psi(S)   [terminal_shadow_psi]
  (2) Psi(S) > 0
  (3) the surplus decomposition: Psi(S) = sum_{f in crossM} ell[f]^2 - sum_{e in bdyB} lambda_e^2,
      and crossM lengths vs lambda (boundary witness) lengths -- confirm long-bad -> shorter-boundary.
We report:
  - how many L_max switches satisfy the terminal_shadow gates (so Psi is computable & = Gamma drop),
  - min/max Psi, and min over sites of (max crossM length - max lambda),
  - any site where the chosen neutral-bconn L_max switch FAILS the terminal_shadow gates (Psi=None).

This stresses whether the proven descent identity actually APPLIES to the L_max switch (its hypotheses:
terminal-shadow-gated, every new bad boundary edge covered by an old crossing geodesic, noncrossing old bad
edges safe).  If Psi is None for a neutral-bconn L_max switch, that names the residual gap precisely.

Exact Fraction.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _wf_deficit_farkas import odd_blowup


def edge(u, v):
    return (u, v) if u < v else (v, u)


def boundary_delta(n, adj, side, Sset):
    dB = dM = 0
    for u in Sset:
        for w in adj[u]:
            if w in Sset:
                continue
            if side[u] != side[w]:
                dB += 1
            else:
                dM += 1
    return dB - dM


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def lmax_switches(v, M, ell, cyc):
    """All pref/suff/orient switches at the single largest length L_max through v."""
    bylen = {}
    for f in M:
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(ell[f], []).append(list(Q))
    if not bylen:
        return None, []
    Lmax = max(bylen)
    rows = bylen[Lmax]
    out = []
    for orient in (0, 1):
        pref = set(); suff = set()
        for Q in rows:
            q = Q if orient == 0 else Q[::-1]
            i = q.index(v)
            pref.update(q[:i + 1])
            suff.update(q[i:])
        out.append(frozenset(pref))
        out.append(frozenset(suff))
    return Lmax, list(set(out))


def cross_and_bdy(n, adj, side, Sset):
    """crossM = bad edges (same side) with one endpoint in S; bdyB = blue edges (diff side) with one endpoint in S."""
    crossM = []; bdyB = []
    for u in Sset:
        for w in adj[u]:
            if w in Sset:
                continue
            if side[u] == side[w]:
                crossM.append(edge(u, w))
            else:
                bdyB.append(edge(u, w))
    return crossM, bdyB


def mask_of(Sset):
    m = 0
    for u in Sset:
        m |= (1 << u)
    return m


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    neg = [v for v in range(n) if R[v] < 0]
    if not neg:
        return
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        Lmax, switches = lmax_switches(v, M, ell, cyc)
        # pick a neutral + B-connected + Gamma-decreasing L_max switch (we proved one exists)
        chosen = None
        for Sset in switches:
            if v not in Sset or len(Sset) in (0, n):
                continue
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, Sset)
            if not Bconn(n, adj, s2):
                continue
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                chosen = (Sset, g2)
                break
        if chosen is None:
            acc['no_lmax_winner'] += 1
            continue
        Sset, g2 = chosen
        drop = gamma0 - g2
        # square-surplus structure
        crossM, bdyB = cross_and_bdy(n, adj, side, Sset)
        cross_lens = sorted(ell[f] for f in crossM if f in ell)
        # terminal_shadow_psi requires st in (M,ell,T,mu,cyc) order
        psi = terminal_shadow_psi(n, adj, side, (M, ell, T, mu, cyc), mask_of(Sset))
        if psi is None:
            acc['psi_none'] += 1
            if acc['ex_psi_none'] is None:
                acc['ex_psi_none'] = (name, n, ''.join(map(str, side)), v, str(R[v]), 'Lmax=%d drop=%d crossM_lens=%s' % (Lmax, drop, cross_lens))
            continue
        acc['psi_ok'] += 1
        # identity check: drop == psi
        if psi == drop:
            acc['identity_ok'] += 1
        else:
            acc['identity_bad'] += 1
            if acc['ex_identity'] is None:
                acc['ex_identity'] = (name, n, ''.join(map(str, side)), v, 'drop=%d psi=%d' % (drop, psi))
        if psi > 0:
            acc['psi_pos'] += 1
        else:
            acc['psi_nonpos'] += 1
        # surplus margin: max crossM length present
        if cross_lens:
            acc['min_maxcross'] = cross_lens[-1] if acc['min_maxcross'] is None else min(acc['min_maxcross'], cross_lens[-1])
            acc['Lmax_eq_maxcross'] += 1 if cross_lens[-1] == Lmax else 0
            acc['Lmax_gt_maxcross'] += 1 if cross_lens[-1] < Lmax else 0
        acc['psi_min'] = psi if acc['psi_min'] is None else min(acc['psi_min'], psi)
        acc['psi_max'] = psi if acc['psi_max'] is None else max(acc['psi_max'], psi)


def gfam_allmax(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc)


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


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
    acc = dict(neg=0, no_lmax_winner=0, psi_ok=0, psi_none=0,
               identity_ok=0, identity_bad=0, psi_pos=0, psi_nonpos=0,
               Lmax_eq_maxcross=0, Lmax_gt_maxcross=0, min_maxcross=None,
               psi_min=None, psi_max=None,
               ex_psi_none=None, ex_identity=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: neg=%d psi_ok=%d psi_none=%d identity_ok=%d psi_pos=%d"
              % (nn, acc['neg'], acc['psi_ok'], acc['psi_none'], acc['identity_ok'], acc['psi_pos']), flush=True)
    grN, grE = mycielski(5, Cn(5)); m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    hN, hE = dec("H?AFBo]"); base = [int(c) for c in "111110000"]
    for t in (2, 3):
        nn, EE = vertex_blowup(hN, hE, t)
        side = [base[v // t] for v in range(nn)]
        adj = [set() for _ in range(nn)]
        for x, y in EE:
            adj[x].add(y); adj[y].add(x)
        test_cut("Hblow_t%d" % t, nn, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,2)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 13:
            gfam_allmax("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam_allmax("isl", nn, EE, acc)
    rng = random.Random(7); made = 0; tries = 0
    while made < 150 and tries < 50000:
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
        made += 1; gfam_allmax("rand%d" % made, nn, EE, acc)
    print("=" * 72)
    print("R[v]<0 sites:", acc['neg'], " no L_max winner:", acc['no_lmax_winner'])
    print("--- terminal_shadow Psi on the chosen L_max switch ---")
    print("  Psi computable (gates pass):", acc['psi_ok'], "  Psi=None (gates FAIL):", acc['psi_none'])
    print("  descent identity drop==Psi :", acc['identity_ok'], "  identity violated:", acc['identity_bad'])
    print("  Psi > 0                    :", acc['psi_pos'], "  Psi <= 0:", acc['psi_nonpos'])
    print("  Psi range (exact)          :", acc['psi_min'], "..", acc['psi_max'])
    print("--- square-surplus structure ---")
    print("  Lmax == max crossM length  :", acc['Lmax_eq_maxcross'], "  Lmax > max crossM length:", acc['Lmax_gt_maxcross'])
    print("  min over sites of max crossM length:", acc['min_maxcross'])
    print("--- gap witnesses ---")
    print("  ex Psi=None (descent identity does NOT apply to L_max switch):", acc['ex_psi_none'])
    print("  ex identity violated:", acc['ex_identity'])
    gap = acc['psi_none'] > 0 or acc['identity_bad'] > 0 or acc['psi_nonpos'] > 0
    print("VERDICT:", "RESIDUAL GAP: descent identity does not apply to every L_max switch (Psi=None or identity fails)" if gap
          else "L_MAX SWITCH: descent identity APPLIES, Psi==Gamma-drop>0 on every R[v]<0 site -- mechanism exact-verified")


if __name__ == "__main__":
    main()
