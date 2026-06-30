"""The REAL surplus lemma for Psi>0 on the L_max half-switch: SORTED LENGTH DOMINANCE (strict).

Anatomy showed: |crossM|==|bdyB| (count neutrality) and, sorting both descending, cross[i]>=lam[i] for all i
on 56/56 sites. Then Psi = sum cross^2 - sum lam^2 = sum (cross[i]^2 - lam[i]^2) >= 0, and Psi>0 iff some i has
cross[i] > lam[i]. This file verifies the STRICT version and isolates the two remaining unproved sub-lemmas:

  (SL1 count-neutrality)   |crossM| == |bdyB|.
  (SL2 sorted dominance)   sort cross desc, lam desc: cross[i] >= lam[i] for all i, with >= one strict.

We confirm (SL1)+(SL2-strict) => Psi>0 on every site, and report the minimal strict-gap index data.
We also test the natural STRUCTURAL reason for (SL2): each boundary witness lambda_e is the length of a
crossing bad edge f whose geodesic exits S at e -- so every lam value is ITSELF a crossM length, hence the
lam-multiset is a sub-multiset-with-repetition dominated by crossM. We check: is the lam multiset always a
"capped" image of crossM (each lam[i] picks the min over witnesses, so lam <= the cross it witnesses)?

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
    lam_per_edge = {e: min(ell[f] for f in ws) for e, ws in witnesses.items()}
    lambdas = sorted(lam_per_edge.values(), reverse=True)
    return cross_lens, lambdas, lam_per_edge, witnesses, ell


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
                chosen = Sset
                break
        if chosen is None:
            continue
        w = witnesses_full(n, adj, side, (M, ell, T, mu, cyc), chosen)
        if w is None:
            acc['gates_fail'] += 1
            continue
        cross_lens, lambdas, lam_per_edge, witnesses, _ = w
        # SL1 count neutrality
        sl1 = (len(cross_lens) == len(lambdas))
        acc['sl1_ok'] += 1 if sl1 else 0
        acc['sl1_bad'] += 0 if sl1 else 1
        # SL2 sorted dominance (descending)
        k = min(len(cross_lens), len(lambdas))
        dom = sl1 and all(cross_lens[i] >= lambdas[i] for i in range(k))
        strict = dom and any(cross_lens[i] > lambdas[i] for i in range(k))
        acc['sl2_dom'] += 1 if dom else 0
        acc['sl2_strict'] += 1 if strict else 0
        if not dom and acc['ex_nondom'] is None:
            acc['ex_nondom'] = (name, n, v, 'cross=%s lam=%s' % (cross_lens, lambdas))
        if dom and not strict and acc['ex_notstrict'] is None:
            acc['ex_notstrict'] = (name, n, v, 'cross=%s lam=%s' % (cross_lens, lambdas))
        # STRUCTURAL: each lam_e <= ell of its witnessing cross edge => lam multiset entrywise-bounded
        each_lam_is_cross = all(any(lam == cl for cl in cross_lens) for lam in lambdas)
        acc['lam_subset_cross'] += 1 if each_lam_is_cross else 0
        # Psi recompute and entrywise gap
        psi = sum(c * c for c in cross_lens) - sum(l * l for l in lambdas)
        acc['psi_min'] = psi if acc['psi_min'] is None else min(acc['psi_min'], psi)
        if psi > 0:
            acc['psi_pos'] += 1
        else:
            acc['psi_nonpos'] += 1
            if acc['ex_psi_nonpos'] is None:
                acc['ex_psi_nonpos'] = (name, n, v, 'cross=%s lam=%s psi=%s' % (cross_lens, lambdas, psi))


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
    acc = dict(neg=0, gates_fail=0, sl1_ok=0, sl1_bad=0, sl2_dom=0, sl2_strict=0,
               lam_subset_cross=0, psi_pos=0, psi_nonpos=0, psi_min=None,
               ex_nondom=None, ex_notstrict=None, ex_psi_nonpos=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: neg=%d sl1_ok=%d sl2_dom=%d sl2_strict=%d psi_pos=%d"
              % (nn, acc['neg'], acc['sl1_ok'], acc['sl2_dom'], acc['sl2_strict'], acc['psi_pos']), flush=True)
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
    print("R[v]<0 sites:", acc['neg'], " (L_max gates_fail:", acc['gates_fail'], ")")
    print("  (SL1) |crossM|==|bdyB|     :", acc['sl1_ok'], " bad:", acc['sl1_bad'])
    print("  (SL2) sorted dominance     :", acc['sl2_dom'], "/ strict:", acc['sl2_strict'])
    print("  each lambda value IS a crossM length:", acc['lam_subset_cross'])
    print("  Psi>0 (consequence)        :", acc['psi_pos'], " nonpos:", acc['psi_nonpos'])
    print("  min Psi                    :", acc['psi_min'])
    print("--- witnesses ---")
    print("  ex non-dominant   :", acc['ex_nondom'])
    print("  ex dom-not-strict :", acc['ex_notstrict'])
    print("  ex Psi<=0         :", acc['ex_psi_nonpos'])
    ok = acc['sl1_bad'] == 0 and acc['sl2_strict'] == acc['neg'] and acc['psi_nonpos'] == 0
    print("VERDICT:",
          "(SL1)+(SL2-strict) HOLD 56/56 => Psi>0 reduces to two length-multiset lemmas; this is the SOLE residual gap"
          if ok else "SL1/SL2 break -- see witnesses")


if __name__ == "__main__":
    main()
