"""Mine extra-exit degrees in the blue-closed hull lemma.

For completed seed+moat switches, test whether the extra-exit witness graph

    delta_B(U)\Y  --  delta_M(U)\X

from the blue-closed bad-subset hull has right degree at most one.  The
multi-door fan obstruction has an extra bad edge opening several extra exits;
if the completed switches avoid this, BH2 reduces to coverage.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


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


def scan_switch(n, adj, side, st, mask_s, acc, first):
    cyc = st[4]
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        acc["bad_terminal"] += 1
        return first

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
        acc["extra_cases"] += 1
        right_deg = Counter()
        edge_count = 0
        left_covered = 0
        for e in extra_b:
            nbrs = [f for f in witnesses.get(e, set()) if f in extra_m]
            if nbrs:
                left_covered += 1
            for f in nbrs:
                edge_count += 1
                right_deg[f] += 1
        if edge_count == len(extra_b) * len(extra_m):
            acc["complete"] += 1
        else:
            acc["incomplete"] += 1
            if first is None:
                first = ("incomplete", mask_tuple(n, mask_s), tuple(sorted(x_set)), tuple(sorted(y_set)), mask_tuple(n, mask_u), extra_b, extra_m, edge_count)
        max_right = max(right_deg.values(), default=0)
        acc["max_right"][max_right] += 1
        if left_covered < len(extra_b):
            acc["uncovered"] += 1
            if first is None:
                first = ("uncovered", mask_tuple(n, mask_s), tuple(sorted(x_set)), tuple(sorted(y_set)), mask_tuple(n, mask_u), extra_b, extra_m)
        if max_right > 1:
            acc["multidoor"] += 1
            if first is None:
                first = ("multidoor", mask_tuple(n, mask_s), tuple(sorted(x_set)), tuple(sorted(y_set)), mask_tuple(n, mask_u), extra_b, extra_m, dict(right_deg))
    return first


def scan_cut(n, adj, side, acc, max_add, first):
    if not Bconn(n, adj, side):
        return first
    st = struct_for_side(n, adj, side)
    if st is None:
        return first
    R = residuals(n, adj, side)
    if R is None:
        return first
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["no_switch"] += 1
            continue
        _seed, mask, _psi = got
        acc["switches"] += 1
        first = scan_switch(n, adj, side, st, mask, acc, first)
    return first


def scan_graph_allmax(n, edges, acc, max_add, first):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(n, adj, side, acc, max_add, first)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    args = parser.parse_args()

    acc = {
        "switches": 0,
        "extra_cases": 0,
        "multidoor": 0,
        "uncovered": 0,
        "no_switch": 0,
        "bad_terminal": 0,
        "max_right": Counter(),
        "complete": 0,
        "incomplete": 0,
    }
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_graph_allmax(n, edges, acc, args.max_add, first)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_graph_allmax(n, edges, acc, args.max_add, first)

    print("switches:", acc["switches"])
    print("extra cases:", acc["extra_cases"])
    print("max right degree histogram:", dict(sorted(acc["max_right"].items())))
    print("complete extra graphs:", acc["complete"], "incomplete:", acc["incomplete"])
    print("multidoor cases:", acc["multidoor"])
    print("uncovered cases:", acc["uncovered"])
    print("no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("first:", first or "")
    print("VERDICT:", "PASS" if acc["multidoor"] == 0 and acc["uncovered"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
