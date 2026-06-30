"""Structural mine for blue-closed extra graphs.

Checks whether the extra graph from the blue-closed hull lemma has laminar
neighborhoods or a consecutive-ones ordering.  These are candidate proof
handles for the Hall/matching atom.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details, max_bipartite_matching
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s


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


def is_laminar(sets):
    fam = [set(s) for s in sets if s]
    for i, a in enumerate(fam):
        for b in fam[i + 1 :]:
            inter = a & b
            if inter and not (a <= b or b <= a):
                return False
    return True


def consecutive_for_order(order, sets):
    pos = {x: i for i, x in enumerate(order)}
    for s in sets:
        if not s:
            continue
        idx = sorted(pos[x] for x in s)
        if idx[-1] - idx[0] + 1 != len(idx):
            return False
    return True


def has_consecutive_order(universe, sets, cap):
    universe = tuple(universe)
    if len(universe) > cap:
        return None
    for order in itertools.permutations(universe):
        if consecutive_for_order(order, sets):
            return True
    return False


def laminar_capacity(universe, sets):
    """Return (root_demand, min_margin, node_stats) for a laminar hypergraph.

    `sets` are right-neighborhood subsets of the left universe.  A hyperedge can
    cover one leaf in its set.  For laminar families, matching all leaves is
    equivalent to the root demand being zero under this bottom-up recursion:

      demand(leaf)=max(0, 1 - multiplicity(leaf)).
      demand(A)=max(0, sum demand(children of A) - multiplicity(A)).
    """
    universe = frozenset(universe)
    nodes = {universe}
    for x in universe:
        nodes.add(frozenset([x]))
    mult = Counter()
    for s in sets:
        fs = frozenset(s)
        if fs:
            nodes.add(fs)
            mult[fs] += 1
    nodes = list(nodes)
    parent = {}
    for a in nodes:
        if a == universe:
            continue
        candidates = [b for b in nodes if a < b]
        if not candidates:
            return None
        parent[a] = min(candidates, key=len)
    children = {a: [] for a in nodes}
    for a, p in parent.items():
        children[p].append(a)

    demand = {}
    margins = []

    def rec(a):
        if a in demand:
            return demand[a]
        child_need = 1 if len(a) == 1 else sum(rec(c) for c in children[a])
        margin = mult[a] - child_need
        margins.append((a, margin, mult[a], child_need))
        demand[a] = max(0, -margin)
        return demand[a]

    root_demand = rec(universe)
    min_margin = min(m for _a, m, _mu, _need in margins)
    return root_demand, min_margin, margins


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def scan_switch(n, adj, side, st, mask_s, acc, first, convex_cap):
    cyc = st[4]
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
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

        left_sets = []
        right_sets = {f: set() for f in extra_m}
        adj_left = {}
        for e in extra_b:
            nbrs = {f for f in witnesses.get(e, set()) if f in extra_m}
            adj_left[e] = nbrs
            left_sets.append(nbrs)
            for f in nbrs:
                right_sets[f].add(e)
        right_sets_list = list(right_sets.values())

        msize, _ = max_bipartite_matching(extra_b, extra_m, adj_left)
        if msize < len(extra_b):
            acc["matching_fail"] += 1
            if first is None:
                first = ("matching_fail", mask_tuple(n, mask_s), tuple(sorted(x_set)), extra_b, extra_m)

        acc["cases"] += 1
        left_lam = is_laminar(left_sets)
        right_lam = is_laminar(right_sets_list)
        acc["left_laminar"][left_lam] += 1
        acc["right_laminar"][right_lam] += 1
        left_conv = has_consecutive_order(extra_m, left_sets, convex_cap)
        right_conv = has_consecutive_order(extra_b, right_sets_list, convex_cap)
        cap_result = laminar_capacity(extra_b, right_sets_list) if right_lam else None
        if cap_result is None:
            acc["lamcap"][None] += 1
        else:
            root_demand, min_margin, _margins = cap_result
            acc["lamcap_root"][root_demand] += 1
            acc["lamcap_min_margin"][min_margin] += 1
        acc["left_convex"][left_conv] += 1
        acc["right_convex"][right_conv] += 1
        if (not left_lam or not right_lam) and first is None:
            first = ("nonlaminar", left_lam, right_lam, mask_tuple(n, mask_s), tuple(sorted(x_set)), extra_b, extra_m, left_sets, right_sets_list)
    return first


def scan_cut(n, adj, side, acc, max_add, first, convex_cap):
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
        first = scan_switch(n, adj, side, st, mask, acc, first, convex_cap)
    return first


def scan_graph_allmax(n, edges, acc, max_add, first, convex_cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(n, adj, side, acc, max_add, first, convex_cap)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--convex-cap", type=int, default=8)
    args = parser.parse_args()

    acc = {
        "switches": 0,
        "cases": 0,
        "matching_fail": 0,
        "no_switch": 0,
        "left_laminar": Counter(),
        "right_laminar": Counter(),
        "left_convex": Counter(),
        "right_convex": Counter(),
        "lamcap": Counter(),
        "lamcap_root": Counter(),
        "lamcap_min_margin": Counter(),
    }
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_graph_allmax(n, edges, acc, args.max_add, first, args.convex_cap)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_graph_allmax(n, edges, acc, args.max_add, first, args.convex_cap)

    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        first = scan_cut(n, adj_from_edges(n, edges), side, acc, args.max_add, first, args.convex_cap)

    print("switches:", acc["switches"])
    print("extra cases:", acc["cases"])
    print("matching_fail:", acc["matching_fail"], "no_switch:", acc["no_switch"])
    print("left_laminar:", dict(acc["left_laminar"]))
    print("right_laminar:", dict(acc["right_laminar"]))
    print("left_convex:", dict(acc["left_convex"]))
    print("right_convex:", dict(acc["right_convex"]))
    print("lamcap_root:", dict(sorted(acc["lamcap_root"].items())))
    print("lamcap_min_margin:", dict(sorted(acc["lamcap_min_margin"].items())))
    print("lamcap_none:", dict(acc["lamcap"]))
    print("first:", first or "")


if __name__ == "__main__":
    main()
