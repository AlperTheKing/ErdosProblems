"""Dump one laminar-capacity tight blue-closed hull example.

This is a diagnostic, not a proof gate.  It reuses the structure miner and
prints the first extra-door case where the laminar capacity recursion has a
negative local margin, so the proof target can be inspected.
"""

from collections import Counter
from fractions import Fraction as F
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details, max_bipartite_matching
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s
from _codex_blueclosed_structure_mine import is_laminar, laminar_capacity


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, T, _mu, cyc = st
    if not M:
        return None
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


def best_seed_moat_mask(n, adj, side, st, v, max_add):
    gamma0 = gamma_of(n, adj, side)
    _M, ell, _T, _mu, cyc = st
    best = None
    for seed in length_bundle_half_switches(ell, cyc, v):
        if not ((seed >> v) & 1):
            continue
        cand = best_moat_completion(n, adj, side, st, seed, max_add)
        if cand is None:
            continue
        added, _negpsi, mask, psi = cand
        gamma2 = gamma_of(n, adj, flip_side(side, mask))
        if gamma2 is None or gamma2 >= gamma0:
            continue
        key = (added, -psi, mask)
        if best is None or key < best[0]:
            best = (key, seed, mask, psi)
    return None if best is None else best[1:]


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def inspect_switch(name, n, adj, side, st, mask_s):
    cyc = st[4]
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        return None
    cross = list(det["cross_m"])
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: set() for f in cross}
    for e, fs in witnesses.items():
        for f in fs:
            exits_of_f[f].add(e)
    prefixes = {f: crossing_prefixes(mask_s, f, cyc[f]) for f in cross}

    for bits in range(1, 1 << len(cross)):
        x_set = {cross[i] for i in range(len(cross)) if (bits >> i) & 1}
        y_set = set().union(*(exits_of_f[f] for f in x_set))
        mask_u = 0
        for f in x_set:
            for e in exits_of_f[f]:
                for pmask in prefixes[f].get(e, ()):
                    mask_u |= pmask
        mask_u = blue_close_inside_s(n, adj, side, mask_s, mask_u)
        bdu, mdu = edge_boundary(n, adj, side, mask_u)
        extra_b = tuple(sorted(bdu - y_set))
        extra_m = tuple(sorted(mdu - x_set))
        if not extra_b:
            continue
        right_sets = {f: set() for f in extra_m}
        adj_left = {}
        for e in extra_b:
            nbrs = {f for f in witnesses.get(e, set()) if f in extra_m}
            adj_left[e] = nbrs
            for f in nbrs:
                right_sets[f].add(e)
        rsets = list(right_sets.values())
        if not is_laminar(rsets):
            continue
        cap = laminar_capacity(extra_b, rsets)
        if cap is None:
            continue
        root_demand, min_margin, margins = cap
        if root_demand == 0 and any((margin == 0 and len(a) > 1 and set(a) != set(extra_b)) for a, margin, mult, need in margins):
            match_size, matching = max_bipartite_matching(extra_b, extra_m, adj_left)
            return dict(
                graph=name,
                n=n,
                side="".join(map(str, side)),
                S=mask_tuple(n, mask_s),
                X=tuple(sorted(x_set)),
                Y=tuple(sorted(y_set)),
                U=mask_tuple(n, mask_u),
                extra_b=extra_b,
                extra_m=extra_m,
                right_sets={f: tuple(sorted(s)) for f, s in right_sets.items()},
                matching_size=match_size,
                matching=matching,
                margins=[(tuple(sorted(a)), margin, mult, need) for a, margin, mult, need in margins],
            )
    return None


def scan_cut(name, n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    R = residuals(n, adj, side)
    if R is None:
        return None
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, 1)
        if got is None:
            continue
        _seed, mask, _psi = got
        found = inspect_switch(name, n, adj, side, st, mask)
        if found is not None:
            found["v"] = v
            found["R_v"] = rv
            return found
    return None


def main():
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            adj = adj_from_edges(n, edges)
            for side in maxcut_all(n, adj):
                found = scan_cut(g6, n, adj, side)
                if found:
                    print(found)
                    return
    n, edges, _inherited_side = h_blowup(2)
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        found = scan_cut("H2-allmax", n, adj, side)
        if found:
            print(found)
            return
    print("NO_EXAMPLE")


if __name__ == "__main__":
    main()
