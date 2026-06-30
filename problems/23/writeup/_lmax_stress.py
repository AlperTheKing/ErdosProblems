"""STRESS the weakest link of the (LB) proof assembly.

The proof of (LB) claims: R[v]<0 => the L_max (longest enclosing) length-bundle half-switch through v
is neutral (delta_B=delta_M), B-connected after, and has Psi>0 (so Gamma drops). This file isolates the
L_max half-switch specifically and tests each of those three properties, AND records at WHICH length L the
witness actually lives (to verify the selector is L_max, not a shorter bundle).

For every R[v]<0 site we record, per length L (descending), for both orientations and pref/suff:
  - neutral?  (boundary_delta == 0)
  - B-connected after?
  - Gamma strictly drops?  (exact Fraction recompute)
We then answer: (Q1) is the WINNING length always L_max?  (Q2) is the L_max switch ALWAYS neutral?
(Q3) is the L_max switch ALWAYS B-connected-after?  (Q4) does L_max ALWAYS drop Gamma (square-surplus)?

Exact Fraction.  Same battery as _construction_gate.py.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _wf_deficit_farkas import odd_blowup


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


def bundles_by_len(v, M, ell, cyc):
    """Return {L: [ (pref_frozenset, suff_frozenset) for each orientation ]}."""
    bylen = {}
    for f in M:
        L = ell[f]
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(L, []).append(list(Q))
    out = {}
    for L, rows in bylen.items():
        switches = []
        for orient in (0, 1):
            pref = set(); suff = set()
            for Q in rows:
                q = Q if orient == 0 else Q[::-1]
                i = q.index(v)
                pref.update(q[:i + 1])
                suff.update(q[i:])
            switches.append((frozenset(pref), frozenset(suff)))
        out[L] = switches
    return out


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    neg = [v for v in range(n) if R[v] < 0]
    if not neg:
        return
    gamma0 = sum(ell[f] ** 2 for f in M)
    lens_present = sorted(set(ell[f] for f in M))
    mixed = len(lens_present) > 1
    for v in neg:
        acc['neg'] += 1
        bylen = bundles_by_len(v, M, ell, cyc)
        if not bylen:
            acc['no_bundle'] += 1
            continue
        Lmax = max(bylen.keys())
        Lmin = min(bylen.keys())
        # --- analyze L_max switches specifically ---
        lmax_any_neutral = False
        lmax_any_neutral_bconn = False
        lmax_any_winner = False    # neutral + bconn + gamma drops
        for (pref, suff) in bylen[Lmax]:
            for Sset in (pref, suff):
                if v not in Sset or len(Sset) in (0, n):
                    continue
                neu = boundary_delta(n, adj, side, Sset) == 0
                if not neu:
                    continue
                lmax_any_neutral = True
                s2 = flip(side, Sset)
                bc = Bconn(n, adj, s2)
                if not bc:
                    continue
                lmax_any_neutral_bconn = True
                g2 = gamma_of(n, adj, s2)
                if g2 is not None and g2 < gamma0:
                    lmax_any_winner = True
        # --- find the actual winning length(s): smallest-size winner per length ---
        winning_lengths = []
        for L in sorted(bylen.keys()):
            for (pref, suff) in bylen[L]:
                for Sset in (pref, suff):
                    if v not in Sset or len(Sset) in (0, n):
                        continue
                    if boundary_delta(n, adj, side, Sset) != 0:
                        continue
                    s2 = flip(side, Sset)
                    if not Bconn(n, adj, s2):
                        continue
                    g2 = gamma_of(n, adj, s2)
                    if g2 is not None and g2 < gamma0:
                        winning_lengths.append(L)
                        break
                else:
                    continue
                break
        winning_lengths = sorted(set(winning_lengths))
        # bookkeeping
        if lmax_any_neutral:
            acc['lmax_neutral'] += 1
        else:
            acc['lmax_not_neutral'] += 1
            if acc['ex_not_neutral'] is None:
                acc['ex_not_neutral'] = (name, n, ''.join(map(str, side)), v, str(R[v]), 'Lmax=%d lens=%s' % (Lmax, lens_present))
        if lmax_any_neutral_bconn:
            acc['lmax_bconn'] += 1
        else:
            acc['lmax_not_bconn'] += 1
            if lmax_any_neutral and acc['ex_not_bconn'] is None:
                acc['ex_not_bconn'] = (name, n, ''.join(map(str, side)), v, str(R[v]), 'Lmax=%d' % Lmax)
        if lmax_any_winner:
            acc['lmax_winner'] += 1
        else:
            acc['lmax_not_winner'] += 1
            if acc['ex_not_winner'] is None:
                acc['ex_not_winner'] = (name, n, ''.join(map(str, side)), v, str(R[v]),
                                        'Lmax=%d lens=%s winningL=%s' % (Lmax, lens_present, winning_lengths))
        if not winning_lengths:
            acc['no_winner_anyL'] += 1
            if acc['ex_no_winner'] is None:
                acc['ex_no_winner'] = (name, n, ''.join(map(str, side)), v, str(R[v]))
        else:
            # is the winning length L_max?
            if Lmax in winning_lengths:
                acc['lmax_is_a_winner'] += 1
            if winning_lengths == [Lmax]:
                acc['only_lmax_wins'] += 1
            # does any STRICTLY shorter length also win?
            if any(L < Lmax for L in winning_lengths):
                acc['shorter_also_wins'] += 1
            # record which-length-wins relative to Lmax
            key = tuple('+' if L == Lmax else ('lt' if L < Lmax else 'gt') for L in winning_lengths)
            acc['winL_pattern'][key] = acc['winL_pattern'].get(key, 0) + 1
        acc['mixed'] += 1 if mixed else 0


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
    acc = dict(neg=0, no_bundle=0, mixed=0,
               lmax_neutral=0, lmax_not_neutral=0,
               lmax_bconn=0, lmax_not_bconn=0,
               lmax_winner=0, lmax_not_winner=0,
               lmax_is_a_winner=0, only_lmax_wins=0, shorter_also_wins=0,
               no_winner_anyL=0, winL_pattern={},
               ex_not_neutral=None, ex_not_bconn=None, ex_not_winner=None, ex_no_winner=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: neg=%d lmax_winner=%d lmax_not_winner=%d only_lmax_wins=%d shorter_also_wins=%d"
              % (nn, acc['neg'], acc['lmax_winner'], acc['lmax_not_winner'], acc['only_lmax_wins'], acc['shorter_also_wins']), flush=True)
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
    print("total R[v]<0 sites:", acc['neg'], " (of which mixed-length cuts:", acc['mixed'], ")")
    print("--- L_max half-switch properties ---")
    print("  L_max NEUTRAL (some pref/suff orient):", acc['lmax_neutral'], " NOT-neutral:", acc['lmax_not_neutral'])
    print("  L_max neutral+BCONN-after          :", acc['lmax_bconn'], " not-bconn:", acc['lmax_not_bconn'])
    print("  L_max WINNER (neu+bconn+Gamma drop):", acc['lmax_winner'], " NOT-winner:", acc['lmax_not_winner'])
    print("--- selector question: which length wins? ---")
    print("  L_max is among winning lengths     :", acc['lmax_is_a_winner'])
    print("  ONLY L_max wins (no shorter)       :", acc['only_lmax_wins'])
    print("  a STRICTLY shorter length also wins:", acc['shorter_also_wins'])
    print("  NO length wins at all (true fail)  :", acc['no_winner_anyL'])
    print("  winning-length pattern (rel Lmax)  :", dict(sorted(acc['winL_pattern'].items(), key=lambda kv: -kv[1])))
    print("--- counterexamples to the strong (L_max) claims ---")
    print("  ex L_max NOT neutral :", acc['ex_not_neutral'])
    print("  ex L_max neutral NOT bconn:", acc['ex_not_bconn'])
    print("  ex L_max NOT winner  :", acc['ex_not_winner'])
    print("  ex NO length wins    :", acc['ex_no_winner'])
    strong_ok = (acc['lmax_not_winner'] == 0)
    print("VERDICT:", "L_MAX HALF-SWITCH IS ALWAYS THE WITNESS (strong selector holds)" if strong_ok
          else "L_MAX HALF-SWITCH IS NOT ALWAYS THE WITNESS -- selector is a shorter bundle in some sites")


if __name__ == "__main__":
    main()
