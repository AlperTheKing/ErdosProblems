"""Gate the directional rare-monotonicity obstruction.

Broad near-witness persistence is false.  The only finite RM direction that
matters for TH-rare is:

    root e is unmatched in E0,
    matched u is reachable from e in the F0-E0 alternating graph,
    c(u) > c(e), where c(x)=|Wit(x) cap F1|.

Such a pair would give a stage-0 rare-cost-decreasing alternating exchange.
For a minimum-cost stage-0 matching it should never occur.  This gate counts
all reachable matched exits and fails on the first dangerous one.
"""

import argparse
import subprocess
from collections import Counter, deque

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_stage0_all_min_gate import enumerate_min_matchings
from _codex_th_corridor_gate import vertices_of_mask


def alternating_reachable(F0, witnesses, matching, root):
    q = deque([("e", root)])
    seen_e = {root}
    seen_f = set()
    while q:
        typ, obj = q.popleft()
        if typ == "e":
            for f in F0:
                if f in witnesses[obj] and f not in seen_f:
                    seen_f.add(f)
                    q.append(("f", f))
        else:
            e = matching.get(obj)
            if e is not None and e not in seen_e:
                seen_e.add(e)
                q.append(("e", e))
    return seen_e, seen_f


def matching_list(F0, E0, witnesses, deg_f1, all_min, cap):
    if not all_min:
        m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
        return ([m0] if m0 is not None else None), "ok" if m0 is not None else "stage0"
    matchings, status, _best_cost, _count = enumerate_min_matchings(F0, E0, witnesses, deg_f1, cap)
    return matchings, status


def gate_for_matching(F0, E0, F1, witnesses, deg_f1, matching):
    stats = Counter()
    matched = set(matching.values())
    for root in sorted(set(E0) - matched):
        seen_e, seen_f = alternating_reachable(F0, witnesses, matching, root)
        stats["unmatched_roots"] += 1
        stats["reachable_exits"] += len(seen_e)
        stats["reachable_f0"] += len(seen_f)
        for u in sorted(seen_e & matched):
            stats["reachable_matched"] += 1
            if deg_f1[u] <= deg_f1[root]:
                stats["skip_nondangerous_cost"] += 1
                continue
            rows = tuple(sorted(f for f in F1 if f in witnesses[root] and f not in witnesses[u]))
            return False, "dangerous_reachable", {
                "root": root,
                "matched": u,
                "c_root": deg_f1[root],
                "c_matched": deg_f1[u],
                "rows_witness_root_not_matched": rows,
                "alt_f0": tuple(sorted(seen_f)),
            }, stats
    return True, "ok", {}, stats


def check(st, det, all_min, cap):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {"stats": {}}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb.values())
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F0 or not F1:
        return True, "skip_degenerate", {"stats": {}}
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    matchings, mstatus = matching_list(F0, E0, witnesses, deg_f1, all_min, cap)
    if mstatus != "ok":
        return True, mstatus, {"stats": {}}

    stats = Counter()
    for idx, m0 in enumerate(matchings):
        ok, status, info, st_stats = gate_for_matching(F0, E0, F1, witnesses, deg_f1, m0)
        stats["matchings"] += 1
        stats.update(st_stats)
        if not ok:
            info["matching_index"] = idx
            info["stage0"] = tuple(sorted(m0.items()))
            return False, status, {"stats": dict(stats), "failure": info}
    return True, "ok", {"stats": dict(stats)}


def scan_selected_cut(name, n, adj, side, acc, max_add, all_min, cap):
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
            acc["no_switch"] += 1
            continue
        _seed, mask, _psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        ok, status, info = check(st, det, all_min, cap)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["stats"].update(info.get("stats", {}))
        if not ok and acc["first"] is None:
            acc["first"] = {
                "name": name,
                "n": n,
                "side": "".join(map(str, side)),
                "v": v,
                "S": vertices_of_mask(n, mask),
                "status": status,
                "info": info,
            }
            return


def scan_selected_allmax(name, n, edges, acc, max_add, all_min, cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_selected_cut(name, n, adj, side, acc, max_add, all_min, cap)
        if acc["first"] is not None:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--all-min", action="store_true")
    ap.add_argument("--cap", type=int, default=100000)
    args = ap.parse_args()
    acc = {
        "tested": 0,
        "no_switch": 0,
        "bad_terminal": 0,
        "status": Counter(),
        "stats": Counter(),
        "first": None,
    }
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_selected_allmax("cen%d" % nn, n, edges, acc, args.max_add, args.all_min, args.cap)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if acc["first"] is None and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_selected_allmax("H2-allmax", n, edges, acc, args.max_add, args.all_min, args.cap)
    if acc["first"] is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            scan_selected_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add, args.all_min, args.cap)
            if acc["first"] is not None:
                break
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
