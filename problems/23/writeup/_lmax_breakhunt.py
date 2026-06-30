"""BREAK HUNT: try hard to find an R[v]<0 site where the L_max half-switch fails one of
neutrality / B-connected-after / SL1(count) / SL2(strict dominance) / Psi>0.

R<0 needs a NON-gamma-min max cut with MIXED bad-edge lengths. We generate many such cuts:
  - larger odd-blowups of C5/C7 with asymmetric sizes (forces length-7 and length-5 bad edges together),
  - vertex blowups of small mixed-length graphs at t=2,3,4,
  - random triangle-free N=11..16 graphs scanned over ALL max cuts (not just gamma-min),
  - glued C5/C7 islands at several sizes.
For every R[v]<0 vertex, we test the L_max half-switch directly and accumulate any FAILURE with full data.

Exact Fraction.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
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


def witnesses_full(n, adj, side, st, Sset):
    M, ell, _T, _mu, cyc = st
    mask = 0
    for u in Sset:
        mask |= (1 << u)
    bdy_b = set(); cross_m = []
    for u in range(n):
        inu = (mask >> u) & 1
        for v in adj[u]:
            if v <= u:
                continue
            if inu == ((mask >> v) & 1):
                continue
            if side[u] == side[v]:
                cross_m.append(edge(u, v))
            else:
                bdy_b.add(edge(u, v))
    witnesses = {e: [] for e in bdy_b}
    for f in cross_m:
        u, v = f
        tau = u if ((mask >> u) & 1) else v
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            if path[0] != tau:
                return None
            bits = [(mask >> x) & 1 for x in path]
            if bits[0] != 1 or bits[-1] != 0:
                return None
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            if any(bits[j] for j in range(r + 1, len(bits))):
                return None
            if r > len(path) - 2:
                return None
            exit_edge = edge(path[r], path[r + 1])
            if exit_edge not in witnesses:
                return None
            witnesses[exit_edge].append(f)
    if any(not ws for ws in witnesses.values()):
        return None
    cross_lens = sorted((ell[f] for f in cross_m), reverse=True)
    lambdas = sorted((min(ell[f] for f in ws) for ws in witnesses.values()), reverse=True)
    return cross_lens, lambdas


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
    acc['cuts'] += 1
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        Lmax, switches = lmax_switches(v, M, ell, cyc)
        # collect neutral+bconn L_max switches
        nb = []
        any_neutral = False
        for Sset in switches:
            if v not in Sset or len(Sset) in (0, n):
                continue
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            any_neutral = True
            if Bconn(n, adj, flip(side, Sset)):
                nb.append(Sset)
        if not any_neutral:
            acc['fail_neutral'] += 1
            if acc['ex'] is None:
                acc['ex'] = ('NEUTRAL', name, n, ''.join(map(str, side)), v, 'Lmax=%d' % Lmax)
            continue
        if not nb:
            acc['fail_bconn'] += 1
            if acc['ex'] is None:
                acc['ex'] = ('BCONN', name, n, ''.join(map(str, side)), v, 'Lmax=%d' % Lmax)
            continue
        # among neutral+bconn L_max switches, require at least one with Psi>0 via SL1+SL2
        win = False
        for Sset in nb:
            s2 = flip(side, Sset)
            g2 = gamma_of(n, adj, s2)
            if g2 is None or g2 >= gamma0:
                continue
            w = witnesses_full(n, adj, side, (M, ell, T, mu, cyc), Sset)
            if w is None:
                continue
            cross_lens, lambdas = w
            if len(cross_lens) != len(lambdas):
                continue
            k = len(cross_lens)
            if all(cross_lens[i] >= lambdas[i] for i in range(k)) and any(cross_lens[i] > lambdas[i] for i in range(k)):
                psi = sum(c * c for c in cross_lens) - sum(l * l for l in lambdas)
                if psi == gamma0 - g2 and psi > 0:
                    win = True
                    break
        if win:
            acc['ok'] += 1
        else:
            acc['fail_psi'] += 1
            if acc['ex'] is None:
                acc['ex'] = ('PSI/SL', name, n, ''.join(map(str, side)), v, 'Lmax=%d' % Lmax)


def gfam_allmax(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj)
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def maxcut_ls_many(n, adj, seeds=120):
    rng = random.Random(11); best = -1; outs = set()
    cand = []
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        cand.append((val, tuple(s)))
        if val > best:
            best = val
    for val, s in cand:
        if val == best:
            outs.add(s)
    return [list(s) for s in outs]


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def main():
    acc = dict(cuts=0, neg=0, ok=0, fail_neutral=0, fail_bconn=0, fail_psi=0, ex=None)
    # asymmetric odd-blowups (C5 + C7), forcing mixed lengths
    blow_sizes = [
        (5, [3,1,3,1,2]), (5, [4,1,4,1,3]), (5, [3,2,1,3,2]), (5, [4,2,4,2,1]),
        (5, [3,1,4,1,3]), (5, [2,3,2,3,1]), (7, [2,1,2,1,2,1,2]), (7, [3,1,2,1,3,1,2]),
        (5, [5,1,5,1,4]), (5, [4,4,1,4,4]),
    ]
    for base_n, sizes in blow_sizes:
        nn, EE = odd_blowup(base_n, list(sizes))
        if nn <= 28:
            gfam_allmax("blow_%d_%s" % (base_n, sizes), nn, EE, acc)
    print("after asym blowups: cuts=%d neg=%d ok=%d fails(neu/bc/psi)=%d/%d/%d %s"
          % (acc['cuts'], acc['neg'], acc['ok'], acc['fail_neutral'], acc['fail_bconn'], acc['fail_psi'], acc['ex'] or ''), flush=True)
    # vertex blowups of mixed-length census graphs (those with both C5 and C7 geodesics)
    seeds = ["H?AFBo]", "GCrb`o", "G?qabo", "H?qa`bs"]
    for g6 in seeds:
        try:
            hN, hE = dec(g6)
        except Exception:
            continue
        for t in (2, 3, 4):
            nn, EE = vertex_blowup(hN, hE, t)
            if nn > 30:
                continue
            adj = [set() for _ in range(nn)]
            for x, y in EE:
                adj[x].add(y); adj[y].add(x)
            for side in maxcut_ls_many(nn, adj):
                test_cut("vblow_%s_t%d" % (g6, t), nn, adj, side, acc)
    print("after vertex blowups: cuts=%d neg=%d ok=%d fails(neu/bc/psi)=%d/%d/%d %s"
          % (acc['cuts'], acc['neg'], acc['ok'], acc['fail_neutral'], acc['fail_bconn'], acc['fail_psi'], acc['ex'] or ''), flush=True)
    # glued islands at several sizes
    for (a_n, a_E, b) in [((5, Cn(5)), None, mycielski(7, Cn(7))),
                          ((7, Cn(7)), None, mycielski(5, Cn(5)))]:
        nn, EE = union_disjoint(a_n, b); nn, EE = add_edges((nn, EE), [(0, a_n[0])])
        gfam_allmax("isl", nn, EE, acc)
    # random triangle-free N=11..16 over ALL max cuts
    rng = random.Random(2024); made = 0; tries = 0
    while made < 400 and tries < 200000:
        tries += 1
        nn = rng.choice([11, 12, 13, 14, 15, 16]); p = rng.uniform(0.12, 0.30)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        if nn <= 13:
            gfam_allmax("rand%d" % made, nn, EE, acc)
        else:
            for side in maxcut_ls_many(nn, adj):
                test_cut("rand%d" % made, nn, adj, side, acc)
    print("=" * 72)
    print("R<0 cuts:", acc['cuts'], " R<0 vertices:", acc['neg'], " (random graphs:", made, ")")
    print("OK (Lmax neutral+bconn+SL1+SL2-strict+Psi==drop>0):", acc['ok'])
    print("FAIL neutral:", acc['fail_neutral'], " FAIL bconn:", acc['fail_bconn'], " FAIL psi/SL:", acc['fail_psi'])
    print("first failure:", acc['ex'] or 'NONE')
    ok = acc['fail_neutral'] == 0 and acc['fail_bconn'] == 0 and acc['fail_psi'] == 0
    print("VERDICT:", "NO BREAK FOUND -- L_max assembly survives extended break-hunt; gap confined to SL1+SL2" if ok
          else "BREAK FOUND -- see first failure")


if __name__ == "__main__":
    main()
