"""SELECTOR TEST for the square-surplus mechanism of (LB).

CLAIM under test (the longer-enclosing-bundle selector):
For every connected-B MAXIMUM cut and every vertex v with residual R[v] < 0,
let  L_max(v) = max over bad edges f with ell[f]>0 whose shortest geodesic
passes through v of ell[f].  Build the L_max(v) length-bundle prefix/suffix
half-switch S through v (union of Q[:idx(v)+1] over all shortest geodesics Q
of bad edges f with ell[f]=L_max through v, and the suffix likewise; both
orientations).  Then there is such an S that is

   * cut-neutral (delta_B = delta_M),
   * B-connected after flipping,
   * terminal-shadow valid (every crossing geodesic exits a prefix-cut at v
     through a single blue boundary edge; old-cut Psi is well defined),

and whose Psi(S) = sum_{f in crossM} ell[f]^2 - sum_{e in bdyB} lambda_e^2
satisfies the SQUARE-SURPLUS structure:

   (i)  every crossing bad edge f in crossM has ell[f] = L_max,
   (ii) every boundary blue lambda_e is STRICTLY < L_max,
   (iii) Psi(S) >= L_max^2 - L2^2 > 0, where L2 = max lambda over bdyB
        (the next length down), so Gamma drops by exactly Psi(S) > 0.

This is the descent witness that contradicts gamma-min, closing (LB).

EXACT Fraction throughout. Reuses shared gates (terminal_shadow_psi,
closed_half_switches, struct_for_side, build_K2) WITHOUT modifying them.
Independent re-derivation of L_max selection + decomposition here.

Run: python _psi_surplus_gate.py
"""

import argparse
import random
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _wf_deficit_farkas import odd_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi, edge


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def lmax_bundle_masks(cyc, ell, v):
    """All prefix/suffix masks of the L_max(v) length-bundle through v.

    L_max(v) = max bad-edge length over geodesics through v.
    Returns (Lmax, [masks]).  Each mask is a prefix or suffix union (per
    orientation) over ALL shortest geodesics Q of bad edges f with
    ell[f]=Lmax that contain v.
    """
    lengths_through_v = set()
    for f, paths in cyc.items():
        for Q in paths:
            if v in Q:
                lengths_through_v.add(ell[f])
                break
    if not lengths_through_v:
        return None, []
    Lmax = max(lengths_through_v)
    masks = set()
    for rev in (False, True):
        pref = 0
        suff = 0
        any_hit = False
        for f, paths0 in cyc.items():
            if ell[f] != Lmax:
                continue
            for Q0 in paths0:
                Q = list(reversed(Q0)) if rev else list(Q0)
                if v not in Q:
                    continue
                any_hit = True
                i = Q.index(v)
                for x in Q[: i + 1]:
                    pref |= 1 << x
                for x in Q[i:]:
                    suff |= 1 << x
        if any_hit:
            masks.add(pref)
            masks.add(suff)
    return Lmax, list(masks)


def decompose(n, adj, side, st, mask):
    """Return (crossM_lengths, bdyB_lambdas, psi) for a terminal-shadow-valid
    switch, or None if not valid. Re-derives from the gate's logic to expose
    the per-edge length breakdown."""
    M, ell, _T, _mu, cyc = st
    bdy_b = set()
    cross_m = []
    for u in range(n):
        inu = (mask >> u) & 1
        for w in adj[u]:
            if w <= u:
                continue
            if inu == ((mask >> w) & 1):
                continue
            if side[u] == side[w]:
                cross_m.append(edge(u, w))
            else:
                bdy_b.add(edge(u, w))
    psi = terminal_shadow_psi(n, adj, side, st, mask)
    if psi is None:
        return None
    # re-derive witnesses to extract per-boundary lambda
    witnesses = {e: [] for e in bdy_b}
    for f in cross_m:
        u, w = f
        tau = u if ((mask >> u) & 1) else w
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            bits = [(mask >> x) & 1 for x in path]
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            exit_edge = edge(path[r], path[r + 1])
            witnesses[exit_edge].append(f)
    crossM_lengths = [ell[f] for f in cross_m]
    bdyB_lambdas = [min(ell[f] for f in ws) for ws in witnesses.values() if ws]
    return crossM_lengths, bdyB_lambdas, psi


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, _T, _mu, cyc = st
    if not M:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    gamma0 = sum(ell[f] * ell[f] for f in M)
    cut_has_neg = False
    for v, r in enumerate(R):
        if r >= 0:
            continue
        cut_has_neg = True
        acc["neg"] += 1
        Lmax, masks = lmax_bundle_masks(cyc, ell, v)
        if Lmax is None:
            acc["fail_struct"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = ("no-bundle", name, n, "".join(map(str, side)), v, str(r))
            continue
        # Try the L_max bundle half-switches; require neutral + Bconn + terminal valid +
        # square-surplus structure (crossM all == Lmax, bdyB lambdas < Lmax, Psi>0, Gamma drops by Psi)
        chosen = None
        for mask in masks:
            if not ((mask >> v) & 1):
                continue
            if mask == 0 or mask == (1 << n) - 1:
                continue
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            if not Bconn(n, adj, flip_side(side, mask)):
                continue
            dd = decompose(n, adj, side, st, mask)
            if dd is None:
                continue
            crossL, bdyLam, psi = dd
            if psi <= 0:
                continue
            # verify Gamma actually drops by exactly psi
            g2 = gamma_of(n, adj, flip_side(side, mask))
            if g2 is None or (gamma0 - g2) != psi:
                acc["psi_mismatch"] += 1
                continue
            chosen = (mask, crossL, bdyLam, psi)
            break
        if chosen is None:
            acc["fail_lmax"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = ("lmax-bundle", name, n, "".join(map(str, side)), v, str(r), Lmax)
            continue
        mask, crossL, bdyLam, psi = chosen
        # SQUARE-SURPLUS structural checks
        cross_all_lmax = all(L == Lmax for L in crossL)
        bdy_strict = all(lam < Lmax for lam in bdyLam) if bdyLam else True
        L2 = max(bdyLam) if bdyLam else 0
        surplus_bound = Lmax * Lmax - L2 * L2
        acc["covered"] += 1
        acc["psi_hist"][psi] = acc["psi_hist"].get(psi, 0) + 1
        acc["lmax_hist"][Lmax] = acc["lmax_hist"].get(Lmax, 0) + 1
        if not cross_all_lmax:
            acc["cross_not_lmax"] += 1
            if acc["first_struct"] is None:
                acc["first_struct"] = ("crossNotLmax", name, n, v, Lmax, crossL)
        if not bdy_strict:
            acc["bdy_not_strict"] += 1
            if acc["first_struct"] is None:
                acc["first_struct"] = ("bdyNotStrict", name, n, v, Lmax, bdyLam)
        # the per-witness lower bound Psi >= Lmax^2 - L2^2 should hold whenever
        # crossM all Lmax and there is exactly the surplus geometry
        if psi < surplus_bound:
            acc["below_surplus"] += 1
            if acc["first_surplus"] is None:
                acc["first_surplus"] = ("belowSurplus", name, n, v, Lmax, L2, str(psi), surplus_bound)
    if cut_has_neg:
        acc["bad_cuts"] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def maxcut_ls(n, adj, seeds=120):
    best = None
    bv = -1
    rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]
        imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1
                    imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val
            best = s[:]
    return best


def new_acc():
    return dict(
        bad_cuts=0, neg=0, covered=0,
        fail_struct=0, fail_lmax=0, psi_mismatch=0,
        cross_not_lmax=0, bdy_not_strict=0, below_surplus=0,
        psi_hist={}, lmax_hist={},
        first_fail=None, first_struct=None, first_surplus=None,
    )


def report(acc, tag):
    print("[%s] bad_cuts=%d neg=%d covered=%d fail_lmax=%d fail_struct=%d psi_mismatch=%d"
          % (tag, acc["bad_cuts"], acc["neg"], acc["covered"], acc["fail_lmax"], acc["fail_struct"], acc["psi_mismatch"]),
          flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--random", type=int, default=150)
    args = parser.parse_args()
    acc = new_acc()

    for n in range(5, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        report(acc, "census N=%d" % n)

    # Mycielski-of-Grotzsch N=23
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = adj_from_edges(m2N, m2E)
    side = maxcut_ls(m2N, adj)
    scan_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    report(acc, "after Myc23")

    # H?AFBo] blowups
    hN, hE = dec("H?AFBo]")
    base = [int(c) for c in "111110000"]
    for t in (2, 3):
        EE = []
        for (u, w) in hE:
            for a in range(t):
                for b in range(t):
                    EE.append((u * t + a, w * t + b))
        nn = hN * t
        s = [base[v // t] for v in range(nn)]
        adj = adj_from_edges(nn, EE)
        scan_cut("Hblow_t%d" % t, nn, adj, s, acc)
    report(acc, "after Hblowups")

    # overloaded odd blowups (all max cuts when small)
    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (2, 2, 2, 2, 2)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 13:
            scan_graph("blow%s" % (sizes,), nn, EE, acc)
    # glued island
    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15)
    nn, EE = add_edges((nn, EE), [(0, 5)])
    scan_graph("isl", nn, EE, acc)
    report(acc, "after blowups+island")

    # randoms
    rng = random.Random(7)
    made = 0
    tries = 0
    while made < args.random and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.32)
        EE = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = adj_from_edges(nn, EE)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        scan_graph("rand%d" % made, nn, EE, acc)
    report(acc, "after randoms (%d)" % made)

    print("=" * 72)
    print("bad cuts (some R[v]<0):", acc["bad_cuts"])
    print("negative-residual vertices:", acc["neg"])
    print("COVERED by L_max-bundle square-surplus switch:", acc["covered"])
    print("L_max-bundle FAILURES (no valid surplus switch):", acc["fail_lmax"], acc["first_fail"] or "")
    print("struct failures (no bundle):", acc["fail_struct"])
    print("psi/gamma mismatches skipped:", acc["psi_mismatch"])
    print("-" * 40)
    print("crossM NOT all L_max:", acc["cross_not_lmax"], acc["first_struct"] or "")
    print("bdyB lambda NOT strictly < L_max:", acc["bdy_not_strict"])
    print("Psi BELOW (L_max^2 - L2^2) surplus bound:", acc["below_surplus"], acc["first_surplus"] or "")
    print("L_max histogram:", dict(sorted(acc["lmax_hist"].items())))
    print("Psi histogram:", dict(sorted(acc["psi_hist"].items())))
    ok = (acc["fail_lmax"] == 0 and acc["fail_struct"] == 0 and
          acc["cross_not_lmax"] == 0 and acc["bdy_not_strict"] == 0 and acc["below_surplus"] == 0)
    print("VERDICT:", "SQUARE-SURPLUS SELECTOR HOLDS: every R[v]<0 has an L_max-bundle half-switch with "
          "crossM all length L_max, bdyB lambdas strictly shorter, Psi >= L_max^2 - L2^2 > 0 = exact Gamma drop"
          if ok else "FAIL (see counters above)")


if __name__ == "__main__":
    main()
