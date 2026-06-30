"""Gate interval prefix-hull side-door inequalities.

If witness sets are consecutive in an exit order, any Hall violator has a
violating consecutive exit interval.  This diagnostic asks whether consecutive
intervals already satisfy the blue-closed side-door inequality:

    |delta_B(U) \ Y| <= |delta_M(U) \ X|,

where X={f: Wit(f) subset Y} and U is the blue-closed prefix hull of X.
"""

import argparse
import itertools
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s


def consecutive_for_order(order, sets):
    pos = {x: i for i, x in enumerate(order)}
    for s in sets:
        if not s:
            continue
        idx = sorted(pos[x] for x in s)
        if idx[-1] - idx[0] + 1 != len(idx):
            return False
    return True


def first_convex_order(univ, sets, cap):
    univ = tuple(univ)
    if len(univ) > cap:
        return None
    for order in itertools.permutations(univ):
        if consecutive_for_order(order, sets):
            return order
    return None


def scan_graph(name, n, edges, acc, cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        cyc = st[4]
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or not det["cross_m"] or len(det["cross_m"]) != len(det["bdy_b"]):
                continue
            F = tuple(sorted(det["cross_m"]))
            E = tuple(sorted(det["bdy_b"]))
            witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
            exits_of_f = {f: {e for e in E if f in witnesses[e]} for f in F}
            fsets = [exits_of_f[f] for f in F]
            order = first_convex_order(E, fsets, cap)
            if order is None:
                acc["no_order"] += 1
                if acc["first"] is None:
                    acc["first"] = ("no_order", name, n, "".join(map(str, side)), tuple(i for i in range(n) if (mask >> i) & 1), F, E)
                continue
            prefixes = {f: crossing_prefixes(mask, f, cyc[f]) for f in F}
            acc["switches"] += 1
            for i in range(len(order)):
                for j in range(i, len(order)):
                    Y = set(order[i : j + 1])
                    X = {f for f in F if exits_of_f[f] <= Y}
                    if not X:
                        continue
                    mask_u = 0
                    for f in X:
                        for e in exits_of_f[f]:
                            for pmask in prefixes[f].get(e, ()):
                                mask_u |= pmask
                    mask_u = blue_close_inside_s(n, adj, side, mask, mask_u)
                    bdu, mdu = edge_boundary(n, adj, side, mask_u)
                    extra_b = bdu - Y
                    extra_m = mdu - X
                    slack = len(extra_m) - len(extra_b)
                    acc["intervals"] += 1
                    acc["slack"][slack] += 1
                    if slack < 0:
                        acc["fail"] += 1
                        if acc["first"] is None:
                            acc["first"] = (
                                "side_fail",
                                name,
                                n,
                                "".join(map(str, side)),
                                tuple(i for i in range(n) if (mask >> i) & 1),
                                tuple(order),
                                tuple(sorted(Y)),
                                tuple(sorted(X)),
                                tuple(sorted(extra_b)),
                                tuple(sorted(extra_m)),
                                slack,
                            )
                            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--cap", type=int, default=8)
    args = ap.parse_args()
    acc = {"switches": 0, "intervals": 0, "fail": 0, "no_order": 0, "slack": Counter(), "first": None}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc, args.cap)
            if acc["first"] is not None:
                break
        print("N", nn, "switches", acc["switches"], "intervals", acc["intervals"], "fail", acc["fail"], "no_order", acc["no_order"], flush=True)
        if acc["first"] is not None:
            break
    print("slack:", sorted(acc["slack"].items())[:20], "...", sorted(acc["slack"].items())[-10:])
    print("first:", acc["first"])
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
