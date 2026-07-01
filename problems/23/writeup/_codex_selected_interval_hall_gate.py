r"""Selected seed+moat interval-Hall gate.

This is the narrow diagnostic for the current K2T finish line.  It checks only
the completed seed+moat switches selected by an R[v] < 0 vertex:

  * missed-exit sets Miss(f)=E\Wit(f) are pairwise laminar, with at most two
    inclusion-minimal nonempty leaves;
  * witness sets Wit(f) admit a consecutive exit order;
  * every consecutive exit interval satisfies the blue-closed interval-hull
    side-door inequality |delta_B(U)\Y| <= |delta_M(U)\X|.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s


def mask_of(vertices):
    mask = 0
    for v in vertices:
        mask |= 1 << v
    return mask


def consecutive_for_order(order, sets):
    pos = {x: i for i, x in enumerate(order)}
    for s in sets:
        if not s:
            continue
        idx = sorted(pos[x] for x in s)
        if idx[-1] - idx[0] + 1 != len(idx):
            return False
    return True


def first_convex_order(items, sets):
    items = tuple(items)
    for order in itertools.permutations(items):
        if consecutive_for_order(order, sets):
            return order
    return None


def laminar_pair(a, b):
    return a <= b or b <= a or a.isdisjoint(b)


def laminar_leaf_count(sets):
    nonempty = [set(s) for s in sets if s]
    if any(not laminar_pair(a, b) for i, a in enumerate(nonempty) for b in nonempty[i + 1 :]):
        return None
    leaves = []
    for s in nonempty:
        if not any(t < s for t in nonempty):
            if not any(t == s for t in leaves):
                leaves.append(s)
    return len(leaves)


def laminar_leaves(sets):
    nonempty = [set(s) for s in sets if s]
    if any(not laminar_pair(a, b) for i, a in enumerate(nonempty) for b in nonempty[i + 1 :]):
        return None
    leaves = []
    for s in nonempty:
        if not any(t < s for t in nonempty):
            if not any(t == s for t in leaves):
                leaves.append(s)
    return leaves


def check_selected_switch(name, n, adj, side, st, v, seed, moat, acc):
    M, ell, _T, _mu, cyc = st
    smask = mask_of(set(seed) | set(moat))
    det = terminal_shadow_details(n, adj, side, st, smask)
    if det is None:
        acc["bad_terminal"] += 1
        if acc["first"] is None:
            acc["first"] = ("bad_terminal", name, n, "".join(map(str, side)), v, tuple(sorted(seed)), tuple(sorted(moat)))
        return

    Fset = tuple(sorted(det["cross_m"]))
    Eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in Eset if f in witnesses[e]} for f in Fset}

    miss_sets = [set(Eset) - exits_of_f[f] for f in Fset]
    leaves = laminar_leaf_count(miss_sets)
    acc["switches"] += 1
    if leaves is None:
        acc["miss_not_laminar"] += 1
        if acc["first"] is None:
            acc["first"] = ("miss_not_laminar", name, n, "".join(map(str, side)), v, Fset, Eset, tuple(tuple(sorted(s)) for s in miss_sets))
        return
    acc["leaf_hist"][leaves] += 1
    if leaves > 2:
        acc["too_many_leaves"] += 1
        if acc["first"] is None:
            acc["first"] = ("too_many_leaves", name, n, "".join(map(str, side)), v, leaves, tuple(tuple(sorted(s)) for s in miss_sets))
        return
    leaf_sets = laminar_leaves(miss_sets) or []
    leaf_union = set().union(*leaf_sets) if leaf_sets else set()
    for e in set(Eset) - leaf_union:
        if witnesses[e] != set(Fset):
            acc["nonuniversal_middle"] += 1
            if acc["first"] is None:
                acc["first"] = ("nonuniversal_middle", name, n, "".join(map(str, side)), v, e, tuple(sorted(witnesses[e])), Fset, tuple(tuple(sorted(s)) for s in leaf_sets))
            return
    for ms in miss_sets:
        union_form = set()
        for leaf in leaf_sets:
            if leaf <= ms:
                union_form |= leaf
        if union_form != ms:
            acc["non_leaf_union_miss"] += 1
            if acc["first"] is None:
                acc["first"] = ("non_leaf_union_miss", name, n, "".join(map(str, side)), v, tuple(sorted(ms)), tuple(tuple(sorted(s)) for s in leaf_sets))
            return

    order = first_convex_order(Eset, [exits_of_f[f] for f in Fset])
    if order is None:
        acc["no_order"] += 1
        if acc["first"] is None:
            acc["first"] = ("no_order", name, n, "".join(map(str, side)), v, Fset, Eset, tuple(tuple(sorted(exits_of_f[f])) for f in Fset))
        return

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
                if acc["first"] is None:
                    acc["first"] = (
                        "interval_fail",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        tuple(sorted(set(seed) | set(moat))),
                        tuple(order),
                        tuple(sorted(Y)),
                        tuple(sorted(X)),
                        tuple(sorted(bdu - Y)),
                        tuple(sorted(mdu - X)),
                        slack,
                    )
                return


def process_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v, rv in enumerate(R):
            if rv >= 0:
                continue
            acc["neg"] += 1
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                acc["no_seedmoat"] += 1
                if acc["first"] is None:
                    acc["first"] = ("no_seedmoat", name, n, "".join(map(str, side)), v, str(rv))
                continue
            seed, moat, _drop = sm
            check_selected_switch(name, n, adj, side, st, v, seed, moat, acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--hblow", type=int, default=2)
    args = ap.parse_args()

    acc = Counter()
    acc["slack"] = Counter()
    acc["leaf_hist"] = Counter()
    acc["first"] = None

    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            process_graph(f"cen{nn}:{g6}", n, edges, acc)
            if acc["first"] is not None:
                break
        print(
            "N",
            nn,
            "neg",
            acc["neg"],
            "switches",
            acc["switches"],
            "intervals",
            acc["intervals"],
            "fail",
            acc["interval_fail"],
            "first",
            acc["first"],
            flush=True,
        )
        if acc["first"] is not None:
            break

    if acc["first"] is None and args.hblow:
        hn, he = dec("H?AFBo]")
        n, edges = vertex_blowup(hn, he, args.hblow)
        process_graph(f"H?AFBo]x{args.hblow}", n, edges, acc)

    print("=" * 60)
    print("neg:", acc["neg"], "selected switches:", acc["switches"], "no_seedmoat:", acc["no_seedmoat"])
    print("miss_not_laminar:", acc["miss_not_laminar"], "too_many_leaves:", acc["too_many_leaves"], "no_order:", acc["no_order"])
    print("nonuniversal_middle:", acc["nonuniversal_middle"], "non_leaf_union_miss:", acc["non_leaf_union_miss"])
    print("leaf_hist:", sorted(acc["leaf_hist"].items()))
    print("intervals:", acc["intervals"], "interval_fail:", acc["interval_fail"])
    print("slack:", sorted(acc["slack"].items()))
    print("first:", acc["first"])
    ok = (
        acc["first"] is None
        and acc["no_seedmoat"] == 0
        and acc["miss_not_laminar"] == 0
        and acc["too_many_leaves"] == 0
        and acc["no_order"] == 0
        and acc["interval_fail"] == 0
    )
    print("VERDICT:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
