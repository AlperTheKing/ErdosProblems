"""Gate the high-tier endpoint contact atom.

For a completed terminal-shadow switch, choose the rare stage-0 matching,
form residual F1/exit components, and test every local first hinge of the
form

    f misses p, f witnesses q, g witnesses p and q, lambda(p) > L0,

where p,g,q is a first step on a shortest residual co-witness path from p
to Wit(f).  The HT atom requires terminal rows R_f(q), R_g(p) with both
inside and outside contact.

This is deliberately local: it does not assume row_miss <= 1.
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
from _codex_rare_exit_complement_gate import components
from _codex_th_corridor_gate import edge, paths_for_exit, vertices_of_mask
from _codex_stage0_all_min_gate import enumerate_min_matchings


def split_by_exit(path, exit_edge, mask):
    for i in range(len(path) - 1):
        if edge(path[i], path[i + 1]) != exit_edge:
            continue
        if ((mask >> path[i]) & 1) and not ((mask >> path[i + 1]) & 1):
            return set(path[: i + 1]), set(path[i + 1 :])
        return None
    return None


def contact_exists(st, mask, f, q_exit, g, p_exit):
    _M, _ell, _T, _mu, cyc = st
    f_paths = paths_for_exit(cyc, f, mask, q_exit)
    g_paths = paths_for_exit(cyc, g, mask, p_exit)
    if not f_paths or not g_paths:
        return False, {"f_paths": len(f_paths), "g_paths": len(g_paths)}

    f_splits = []
    for path in f_paths:
        got = split_by_exit(path, q_exit, mask)
        if got is not None:
            f_splits.append(got)
    g_splits = []
    for path in g_paths:
        got = split_by_exit(path, p_exit, mask)
        if got is not None:
            g_splits.append(got)
    if not f_splits or not g_splits:
        return False, {"f_splits": len(f_splits), "g_splits": len(g_splits)}

    for f_in, f_out in f_splits:
        for g_in, g_out in g_splits:
            if f_in & g_in and f_out & g_out:
                return True, {
                    "inside": tuple(sorted(f_in & g_in)),
                    "outside": tuple(sorted(f_out & g_out)),
                }
    return False, {
        "f_paths": len(f_paths),
        "g_paths": len(g_paths),
        "f_splits": len(f_splits),
        "g_splits": len(g_splits),
    }


def co_witness_graph(cr, adj1):
    cr = tuple(sorted(cr))
    j_adj = {e: set() for e in cr}
    hinges = {}
    for g, exits in adj1.items():
        es = sorted(e for e in exits if e in j_adj)
        for i, a in enumerate(es):
            for b in es[i + 1 :]:
                j_adj[a].add(b)
                j_adj[b].add(a)
                hinges.setdefault((a, b), []).append(g)
                hinges.setdefault((b, a), []).append(g)
    for key in list(hinges):
        hinges[key] = tuple(sorted(hinges[key]))
    return j_adj, hinges


def distances_to_targets(j_adj, targets):
    q = deque()
    dist = {}
    for t in targets:
        dist[t] = 0
        q.append(t)
    while q:
        e = q.popleft()
        for nb in sorted(j_adj[e]):
            if nb not in dist:
                dist[nb] = dist[e] + 1
                q.append(nb)
    return dist


def matching_list(F0, E0, witnesses, deg_f1, all_min, cap):
    if not all_min:
        m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
        return ([m0] if m0 is not None else None), "ok" if m0 is not None else "stage0"
    matchings, status, _best_cost, _count = enumerate_min_matchings(F0, E0, witnesses, deg_f1, cap)
    return matchings, status


def gate_for_matching(st, det, mask, m0):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb.values())
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return True, "skip_no_F1", {"stats": {}}
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}

    stats = Counter()
    for cl, cr in components(F1, rem, adj1):
        cr = tuple(sorted(cr))
        j_adj, hinges = co_witness_graph(cr, adj1)
        for f in sorted(cl):
            targets = set(adj1[f]) & set(cr)
            if not targets:
                return False, "component_row_no_target", {"f": f, "cr": cr}
            dist = distances_to_targets(j_adj, targets)
            for p in cr:
                if p in targets:
                    continue
                stats["missed_exit"] += 1
                if lamb[p] <= min_lam:
                    stats["missed_min_tier"] += 1
                    continue
                stats["missed_high_tier"] += 1
                if p not in dist:
                    return False, "no_residual_path_to_target", {"f": f, "p": p, "targets": tuple(sorted(targets)), "cr": cr}
                for q in sorted(j_adj[p]):
                    if q not in dist or dist[q] != dist[p] - 1:
                        continue
                    if q not in targets and dist[q] >= dist[p]:
                        continue
                    for g in hinges.get((p, q), ()):
                        if g not in cl:
                            continue
                        stats["ht_hinge"] += 1
                        ok, info = contact_exists(st, mask, f, q, g, p)
                        if not ok:
                            return False, "ht_no_contact", {
                                "f": f,
                                "g": g,
                                "p": p,
                                "q": q,
                                "lambda_p": lamb[p],
                                "L0": min_lam,
                                "dist_p": dist[p],
                                "targets": tuple(sorted(targets)),
                                "info": info,
                            }
                        stats["ht_contact"] += 1
    return True, "ok", {"stats": dict(stats)}


def check(st, det, mask, all_min, cap):
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
    if not F1:
        return True, "skip_no_F1", {"stats": {}}
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    matchings, status = matching_list(F0, E0, witnesses, deg_f1, all_min, cap)
    if status != "ok":
        return True, status, {"stats": {}}

    stats = Counter()
    for idx, m0 in enumerate(matchings):
        ok, st_status, info = gate_for_matching(st, det, mask, m0)
        stats["matchings"] += 1
        stats.update(info.get("stats", {}))
        if not ok:
            info["matching_index"] = idx
            info["stage0"] = tuple(sorted(m0.items()))
            return False, st_status, {"stats": dict(stats), "failure": info}
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
        ok, status, info = check(st, det, mask, all_min, cap)
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
