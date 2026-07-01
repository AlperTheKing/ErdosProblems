"""Gate how laminar missed-exit leaves meet residual components after stage0."""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components
from _codex_selected_interval_hall_gate import laminar_leaves


def check(st, det):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {}
    min_len = min(ell[f] for f in F)
    if not any(ell[f] > min_len for f in F):
        return True, "skip_no_F1", {}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in E if f in witnesses[e]} for f in F}
    miss_sets = [set(E) - exits_of_f[f] for f in F]
    leaves = laminar_leaves(miss_sets)
    if leaves is None:
        return False, "not_laminar", {}

    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_lam = min(lamb.values())
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", {}
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    stats = Counter()
    for cl, cr in components(F1, rem, adj1):
        crs = set(cr)
        for leaf in leaves:
            k = len(crs & set(leaf))
            stats[("leaf_intersection", k)] += 1
            if k > 1:
                return False, "leaf_multi_in_component", {"leaf": tuple(sorted(leaf)), "cr": cr, "k": k, "leaves": tuple(tuple(sorted(x)) for x in leaves)}
        for f in cl:
            misses = tuple(e for e in cr if e not in adj1.get(f, set()))
            stats[("row_miss", len(misses))] += 1
            if len(misses) > 1:
                return False, "row_multi_miss", {"f": f, "misses": misses, "cr": cr}
    return True, "ok", {"stats": dict(stats), "leaves": len(leaves)}


def scan_graph(name, n, edges, acc):
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
            ok, status, info = check(st, det)
            acc["switches"] += 1
            acc["status"][status] += 1
            if status == "ok":
                acc["leaf_count"][info["leaves"]] += 1
                acc["stats"].update(info["stats"])
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


def scan_selected_cut(name, n, adj, side, acc, max_add):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["selected_no_switch"] += 1
            continue
        _seed, mask, _psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["selected_bad_terminal"] += 1
            continue
        ok, status, info = check(st, det)
        acc["selected"] += 1
        acc["selected_status"][status] += 1
        if status == "ok":
            acc["selected_leaf_count"][info["leaves"]] += 1
            acc["selected_stats"].update(info["stats"])
        if not ok and acc["first"] is None:
            acc["first"] = {
                "name": name,
                "n": n,
                "side": "".join(map(str, side)),
                "v": v,
                "S": tuple(i for i in range(n) if (mask >> i) & 1),
                "status": status,
                "info": info,
            }
            return


def scan_selected_allmax(name, n, edges, acc, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_selected_cut(name, n, adj, side, acc, max_add)
        if acc["first"] is not None:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--h2-selected", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--max-add", type=int, default=1)
    args = ap.parse_args()
    acc = {
        "switches": 0,
        "status": Counter(),
        "leaf_count": Counter(),
        "stats": Counter(),
        "selected": 0,
        "selected_no_switch": 0,
        "selected_bad_terminal": 0,
        "selected_status": Counter(),
        "selected_leaf_count": Counter(),
        "selected_stats": Counter(),
        "first": None,
    }
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["switches"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N=%d switches=%d first=%s" % (nn, acc["switches"] - before, bool(acc["first"])), flush=True)
        if acc["first"] is not None:
            break
    if acc["first"] is None and args.h2_selected:
        n, edges, _side = h_blowup(2)
        scan_selected_allmax("H2-allmax", n, edges, acc, args.max_add)
    if acc["first"] is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            scan_selected_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add)
            if acc["first"] is not None:
                break
    print("switches:", acc["switches"])
    print("status:", dict(acc["status"]))
    print("leaf_count:", dict(acc["leaf_count"]))
    print("stats:", dict(acc["stats"]))
    print("selected:", acc["selected"], "no_switch:", acc["selected_no_switch"], "bad_terminal:", acc["selected_bad_terminal"])
    print("selected_status:", dict(acc["selected_status"]))
    print("selected_leaf_count:", dict(acc["selected_leaf_count"]))
    print("selected_stats:", dict(acc["selected_stats"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
