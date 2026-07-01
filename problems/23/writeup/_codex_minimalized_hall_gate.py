"""Gate Hall structure after inclusion-minimalizing selected descent switches.

For each R[v]<0 selected seed+moat switch S, shrink inside S to a smallest
neutral terminal-shadow Gamma-decreasing subset U containing v when such a
proper subset exists.  Then re-run the selected interval/Hall structural checks
on U:

  * missed-exit sets are laminar with at most two leaves,
  * middle exits are universal and misses are unions of leaves,
  * every consecutive interval satisfies the interval-hull side-door inequality.

This tests whether Claude's neutral-minimality route can be made literal by
changing the selector to a minimalized switch.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import boundary_delta, flip, gamma_of
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_selected_interval_hall_gate import (
    first_convex_order,
    laminar_leaf_count,
    laminar_leaves,
)
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s
from _codex_selected_minimality_gate import mask_of, vertices_of, smaller_descent


def minimalize(n, adj, side, st, gamma0, smask, v):
    while True:
        got = smaller_descent(n, adj, side, st, gamma0, smask, v)
        if got is None:
            return smask
        smask = got[0]


def check_switch(name, n, adj, side, st, v, smask, acc):
    M, _ell, _T, _mu, cyc = st
    det = terminal_shadow_details(n, adj, side, st, smask)
    if det is None:
        acc["bad_terminal"] += 1
        return ("bad_terminal", name, n, "".join(map(str, side)), v, vertices_of(smask, n))
    Fset = tuple(sorted(det["cross_m"]))
    Eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in Eset if f in witnesses[e]} for f in Fset}
    miss_sets = [set(Eset) - exits_of_f[f] for f in Fset]
    leaves = laminar_leaf_count(miss_sets)
    acc["switches"] += 1
    if leaves is None:
        acc["miss_not_laminar"] += 1
        return ("miss_not_laminar", name, n, "".join(map(str, side)), v, vertices_of(smask, n), Fset, Eset)
    acc["leaf_hist"][leaves] += 1
    if leaves > 2:
        acc["too_many_leaves"] += 1
        return ("too_many_leaves", name, n, "".join(map(str, side)), v, leaves)
    leaf_sets = laminar_leaves(miss_sets) or []
    leaf_union = set().union(*leaf_sets) if leaf_sets else set()
    for e in set(Eset) - leaf_union:
        if witnesses[e] != set(Fset):
            acc["nonuniversal_middle"] += 1
            return ("nonuniversal_middle", name, n, "".join(map(str, side)), v, e)
    for ms in miss_sets:
        union_form = set()
        for leaf in leaf_sets:
            if leaf <= ms:
                union_form |= leaf
        if union_form != ms:
            acc["non_leaf_union_miss"] += 1
            return ("non_leaf_union_miss", name, n, "".join(map(str, side)), v, tuple(sorted(ms)))

    order = first_convex_order(Eset, [exits_of_f[f] for f in Fset])
    if order is None:
        acc["no_order"] += 1
        return ("no_order", name, n, "".join(map(str, side)), v)

    prefixes = {f: crossing_prefixes(smask, f, cyc[f]) for f in Fset}
    for i in range(len(order)):
        for j in range(i, len(order)):
            Y = set(order[i : j + 1])
            X = {f for f in Fset if exits_of_f[f] <= Y}
            if not X:
                continue
            umask = 0
            for f in X:
                for e in exits_of_f[f]:
                    for pmask in prefixes[f].get(e, ()):
                        umask |= pmask
            umask = blue_close_inside_s(n, adj, side, smask, umask)
            bdu, mdu = edge_boundary(n, adj, side, umask)
            slack = len(mdu - X) - len(bdu - Y)
            acc["intervals"] += 1
            acc["slack"][slack] += 1
            if slack < 0:
                acc["interval_fail"] += 1
                return (
                    "interval_fail",
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    vertices_of(smask, n),
                    tuple(order),
                    tuple(sorted(Y)),
                    tuple(sorted(X)),
                    tuple(sorted(bdu - Y)),
                    tuple(sorted(mdu - X)),
                    slack,
                )
    return None


def scan_cut(name, n, adj, side, acc, first, max_add):
    if not Bconn(n, adj, side):
        return first
    st = struct_for_side(n, adj, side)
    if st is None:
        return first
    M, ell, T, _mu, cyc = st
    if not M:
        return first
    K2 = build_K2(n, M, cyc)
    R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=max_add)
        if got is None:
            acc["no_seedmoat"] += 1
            continue
        seed, moat, _drop = got
        smask0 = mask_of(set(seed) | set(moat))
        smask = minimalize(n, adj, side, st, gamma0, smask0, v)
        if smask != smask0:
            acc["shrunk"] += 1
        acc["neg"] += 1
        fail = check_switch(name, n, adj, side, st, v, smask, acc)
        if fail is not None and first is None:
            first = fail
    return first


def scan_allmax(name, n, edges, acc, first, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    args = parser.parse_args()

    acc = Counter()
    acc["leaf_hist"] = Counter()
    acc["slack"] = Counter()
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add)
            if first is not None:
                break
        if first is not None:
            break
    if first is None and args.h2_allmax:
        n, edges = vertex_blowup(*dec("H?AFBo]"), 2)
        first = scan_allmax("H?AFBo]x2", n, edges, acc, first, args.max_add)

    print("neg:", acc["neg"], "switches:", acc["switches"], "shrunk:", acc["shrunk"], "no_seedmoat:", acc["no_seedmoat"])
    print("bad_terminal:", acc["bad_terminal"], "miss_not_laminar:", acc["miss_not_laminar"], "too_many_leaves:", acc["too_many_leaves"])
    print("nonuniversal_middle:", acc["nonuniversal_middle"], "non_leaf_union_miss:", acc["non_leaf_union_miss"], "no_order:", acc["no_order"])
    print("leaf_hist:", sorted(acc["leaf_hist"].items()))
    print("intervals:", acc["intervals"], "interval_fail:", acc["interval_fail"])
    print("slack:", sorted(acc["slack"].items()))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
