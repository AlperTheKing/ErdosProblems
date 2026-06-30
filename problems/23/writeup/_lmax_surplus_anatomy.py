"""Anatomy of Psi>0 for the L_max half-switch: WHY is the square-surplus positive in general?

Psi(S) = sum_{f in crossM} ell[f]^2  -  sum_{e in bdyB} lambda_e^2.
We proved Lmax == max crossM length on all 56 sites. For a clean general proof of Psi>0 we want a
COUNTING/LENGTH inequality. This file extracts, per L_max site, exactly:
  - |crossM|, multiset of crossM lengths,
  - |bdyB|,  multiset of lambda_e (boundary witness lengths),
  - per-orientation, whether |crossM| == |bdyB| (neutrality) AND whether each bdyB edge's lambda < its
    paired crossM contribution (so squares strictly help),
  - the KEY ratios:  does  Psi == sum(cross^2) - sum(lambda^2)  reduce to a pairing where every crossM
    edge of length L pairs to a boundary edge of length < L?
Then we test the STRUCTURAL surplus bound candidate:
  (*)  for the L_max switch, every lambda_e <= Lmax-2  AND |bdyB| <= |crossM|  => Psi >= Lmax^2-(Lmax-2)^2 = 4Lmax-4 > 0.
We check (*) exactly and report any site where it fails (naming the precise obstruction).

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


def lambda_witnesses(n, adj, side, st, Sset):
    """Replicate terminal_shadow_psi's witness computation: for each bdyB edge e, lambda_e = min ell[f]
       over crossing bad edges f whose terminal-prefix geodesic exits S at e. Returns (crossM_lens, bdyB_lambdas)
       or None if the terminal-shadow gates fail."""
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
    cross_lens = sorted(ell[f] for f in cross_m)
    lambdas = sorted(min(ell[f] for f in ws) for ws in witnesses.values())
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
        wl = lambda_witnesses(n, adj, side, (M, ell, T, mu, cyc), chosen)
        if wl is None:
            acc['gates_fail'] += 1
            continue
        cross_lens, lambdas = wl
        # neutrality in lambda-form: |crossM| == |bdyB|
        if len(cross_lens) == len(lambdas):
            acc['count_eq'] += 1
        else:
            acc['count_neq'] += 1
        # candidate (*): every lambda <= Lmax-2 and |bdyB| <= |crossM|
        maxlam = max(lambdas) if lambdas else 0
        cond_star = (maxlam <= Lmax - 2) and (len(lambdas) <= len(cross_lens))
        if cond_star:
            acc['star_ok'] += 1
        else:
            acc['star_fail'] += 1
            if acc['ex_star'] is None:
                acc['ex_star'] = (name, n, v, 'Lmax=%d maxlam=%d |cross|=%d |bdy|=%d cross=%s lam=%s'
                                  % (Lmax, maxlam, len(cross_lens), len(lambdas), cross_lens, lambdas))
        # strict: max lambda strictly < Lmax?
        if maxlam < Lmax:
            acc['maxlam_lt_Lmax'] += 1
        else:
            acc['maxlam_ge_Lmax'] += 1
            if acc['ex_lam_ge'] is None:
                acc['ex_lam_ge'] = (name, n, v, 'Lmax=%d maxlam=%d cross=%s lam=%s' % (Lmax, maxlam, cross_lens, lambdas))
        # record the actual margin Psi and the simple lower bound sum
        psi = sum(L * L for L in cross_lens) - sum(l * l for l in lambdas)
        acc['psi_min'] = psi if acc['psi_min'] is None else min(acc['psi_min'], psi)
        acc['maxlam_hist'][maxlam] = acc['maxlam_hist'].get(maxlam, 0) + 1
        # does every cross length >= every lambda? (sorted dominance)
        dom = all(cross_lens[i] >= lambdas[i] for i in range(min(len(cross_lens), len(lambdas)))) and len(cross_lens) >= len(lambdas)
        if dom:
            acc['sorted_dom'] += 1
        else:
            acc['sorted_nondom'] += 1
            if acc['ex_nondom'] is None:
                acc['ex_nondom'] = (name, n, v, 'cross=%s lam=%s' % (cross_lens, lambdas))


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
    acc = dict(neg=0, gates_fail=0, count_eq=0, count_neq=0, star_ok=0, star_fail=0,
               maxlam_lt_Lmax=0, maxlam_ge_Lmax=0, sorted_dom=0, sorted_nondom=0,
               psi_min=None, maxlam_hist={},
               ex_star=None, ex_lam_ge=None, ex_nondom=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: neg=%d star_ok=%d star_fail=%d maxlam_lt_Lmax=%d sorted_dom=%d"
              % (nn, acc['neg'], acc['star_ok'], acc['star_fail'], acc['maxlam_lt_Lmax'], acc['sorted_dom']), flush=True)
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
    print("--- neutrality / counting ---")
    print("  |crossM| == |bdyB| (count neutrality):", acc['count_eq'], " count_neq:", acc['count_neq'])
    print("--- surplus structure ---")
    print("  max lambda < Lmax (strict)           :", acc['maxlam_lt_Lmax'], " max lambda >= Lmax:", acc['maxlam_ge_Lmax'])
    print("  sorted dominance cross[i]>=lam[i]    :", acc['sorted_dom'], " non-dominant:", acc['sorted_nondom'])
    print("  candidate (*) maxlam<=Lmax-2 & |bdy|<=|cross|:", acc['star_ok'], " (*) fails:", acc['star_fail'])
    print("  min Psi (recomputed)                 :", acc['psi_min'])
    print("  max-lambda histogram                 :", dict(sorted(acc['maxlam_hist'].items())))
    print("--- gap witnesses ---")
    print("  ex (*) fails  :", acc['ex_star'])
    print("  ex maxlam>=Lmax:", acc['ex_lam_ge'])
    print("  ex non-dominant:", acc['ex_nondom'])
    print("VERDICT:",
          "SURPLUS via sorted-dominance |bdy|<=|cross| & maxlam<Lmax: Psi>0 reduces to a length-pairing inequality (general-proof target)"
          if acc['sorted_nondom'] == 0 and acc['maxlam_ge_Lmax'] == 0 else
          "SURPLUS structure breaks -- see ex_nondom / ex_lam_ge")


if __name__ == "__main__":
    main()
