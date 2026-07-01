"""Scope gate for laminar missed-exit structure on all terminal-shadow switches."""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_selected_interval_hall_gate import laminar_leaf_count, laminar_leaves


def check(st, det, require_f1=False):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {}
    if require_f1:
        min_len = min(ell[f] for f in F)
        if not any(ell[f] > min_len for f in F):
            return True, "skip_no_F1", {}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in E if f in witnesses[e]} for f in F}
    miss_sets = [set(E) - exits_of_f[f] for f in F]
    leaves = laminar_leaf_count(miss_sets)
    if leaves is None:
        return False, "not_laminar", {"F": F, "E": E, "miss": tuple(tuple(sorted(s)) for s in miss_sets)}
    if leaves > 2:
        return False, "too_many_leaves", {"leaves": leaves, "miss": tuple(tuple(sorted(s)) for s in miss_sets)}
    leaf_sets = laminar_leaves(miss_sets) or []
    leaf_union = set().union(*leaf_sets) if leaf_sets else set()
    for e in set(E) - leaf_union:
        if witnesses[e] != set(F):
            return False, "middle_nonuniversal", {"e": e, "wit": tuple(sorted(witnesses[e])), "leaves": tuple(tuple(sorted(s)) for s in leaf_sets)}
    for ms in miss_sets:
        union_form = set()
        for leaf in leaf_sets:
            if leaf <= ms:
                union_form |= leaf
        if union_form != ms:
            return False, "not_leaf_union", {"miss": tuple(sorted(ms)), "leaves": tuple(tuple(sorted(s)) for s in leaf_sets)}
    return True, "ok", {"leaves": leaves}


def scan_graph(name, n, edges, acc, require_f1):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None:
                continue
            ok, status, info = check(st, det, require_f1=require_f1)
            acc["switches"] += 1
            acc["status"][status] += 1
            if status == "ok":
                acc["leaf_hist"][info["leaves"]] += 1
            if not ok and acc["first"] is None:
                acc["first"] = {
                    "name": name,
                    "n": n,
                    "side": "".join(map(str, side)),
                    "S": tuple(i for i in range(n) if (mask >> i) & 1),
                    "status": status,
                    "info": info,
                }
                return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--require-f1", action="store_true")
    args = ap.parse_args()
    acc = {"switches": 0, "status": Counter(), "leaf_hist": Counter(), "first": None}
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["switches"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc, args.require_f1)
            if acc["first"] is not None:
                break
        print("N=%d switches=%d first=%s" % (nn, acc["switches"] - before, bool(acc["first"])), flush=True)
        if acc["first"] is not None:
            break
    print("switches:", acc["switches"])
    print("status:", dict(acc["status"]))
    print("leaf_hist:", dict(acc["leaf_hist"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
