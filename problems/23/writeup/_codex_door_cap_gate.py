"""Exact diagnostic gate for the Door-Cap normal form.

This is a proof-scouting gate for completed terminal-shadow switches.  It
reuses the same selected seed+moat switches and rare stage-0 residual
components as the TH-corridor gates, but tests the sharper door-cap predicates:

  A. forced-door length equivalence:
       f witnesses e iff eps_f(e)=0, and non-witness finite eps_f(e) >= 2.
  B. exit cap path obstruction:
       for fixed residual exit e, no e-avoiding co-witness path connects two
       e-missing rows with different inside terminals while all internal rows
       witness e.
  C. row cap path obstruction:
       for fixed residual row f, no co-witness path connects two f-missed
       exits with all internal exits witnessed by f.
  D. cyclic cap obstruction:
       no directed cap cycle of length >= 3 with f_i !~ e_i and f_i ~ e_{i+1}.
  E. TT3 defect-terminal obstruction:
       after A-D, the residual complement should use at most two inside
       terminals in each component.  If a component needs three or more,
       report whether an unused minimum-tier defect exit has a reachable
       stage-0 mate with strictly larger rare cost.
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
from _codex_rare_exit_complement_gate import components


INF = 10**9


def edge(u, v):
    return (u, v) if u < v else (v, u)


def vertices_of_mask(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def in_out(pair, mask):
    a, b = pair
    ina = (mask >> a) & 1
    inb = (mask >> b) & 1
    if ina and not inb:
        return a, b
    if inb and not ina:
        return b, a
    return None, None


def blue_dist_restricted(n, adj, side, mask, src, dst, inside):
    """B-distance inside S or outside S; INF if disconnected."""
    if src is None or dst is None:
        return INF
    if ((mask >> src) & 1) != inside or ((mask >> dst) & 1) != inside:
        return INF
    q = deque([(src, 0)])
    seen = {src}
    while q:
        u, d = q.popleft()
        if u == dst:
            return d
        for v in adj[u]:
            if v in seen:
                continue
            if ((mask >> v) & 1) != inside:
                continue
            if side[u] == side[v]:
                continue
            seen.add(v)
            q.append((v, d + 1))
    return INF


def forced_excess(n, adj, side, mask, ell, f, e):
    tau, sigma = in_out(f, mask)
    x, y = in_out(e, mask)
    if tau is None or x is None:
        return INF, INF
    din = blue_dist_restricted(n, adj, side, mask, tau, x, 1)
    dout = blue_dist_restricted(n, adj, side, mask, y, sigma, 0)
    if din >= INF or dout >= INF:
        return INF, INF
    lam = din + 1 + dout
    return lam, lam - (ell[f] - 1)


def row_graph_path(cl, cr, adj1, start, goal, allowed_internal):
    """Shortest row path start--...--goal through co-witness exits in cr."""
    exit_to_rows = {e: [f for f in cl if e in adj1.get(f, set())] for e in cr}
    q = deque([start])
    prev = {start: None}
    prev_exit = {}
    while q:
        f = q.popleft()
        if f == goal:
            break
        if f != start and f not in allowed_internal:
            continue
        for e in cr:
            if e not in adj1.get(f, set()):
                continue
            for g in exit_to_rows[e]:
                if g in prev:
                    continue
                if g != goal and g not in allowed_internal:
                    continue
                prev[g] = f
                prev_exit[g] = e
                q.append(g)
    if goal not in prev:
        return None
    rows = []
    exits = []
    cur = goal
    while cur is not None:
        rows.append(cur)
        if cur in prev_exit:
            exits.append(prev_exit[cur])
        cur = prev[cur]
    rows.reverse()
    exits.reverse()
    return rows, exits


def exit_cap_path_falsifier(cl, cr, adj1, mask):
    terminals = {f: in_out(f, mask)[0] for f in cl}
    for e in cr:
        seen = {f for f in cl if e in adj1.get(f, set())}
        missing = [f for f in cl if f not in seen]
        for i, f0 in enumerate(missing):
            for f1 in missing[i + 1 :]:
                if terminals[f0] == terminals[f1]:
                    continue
                got = row_graph_path(cl, [h for h in cr if h != e], adj1, f0, f1, seen)
                if got is not None:
                    rows, exits = got
                    return {
                        "exit": e,
                        "rows": tuple(rows),
                        "hinge_exits": tuple(exits),
                        "terminals": (terminals[f0], terminals[f1]),
                    }
    return None


def shortest_exit_path(cr, adj1, f, e0, ek):
    """Shortest exit co-witness path with internal exits witnessed by f."""
    crs = tuple(cr)
    j_adj = {e: set() for e in crs}
    hinge = {}
    for a in crs:
        for b in crs:
            if a >= b:
                continue
            gs = sorted(g for g, es in adj1.items() if a in es and b in es)
            if gs:
                j_adj[a].add(b)
                j_adj[b].add(a)
                hinge[(a, b)] = gs[0]
                hinge[(b, a)] = gs[0]
    q = deque([e0])
    prev = {e0: None}
    while q:
        e = q.popleft()
        if e == ek:
            break
        for nb in sorted(j_adj[e]):
            if nb not in prev:
                prev[nb] = e
                q.append(nb)
    if ek not in prev:
        return None
    path = []
    cur = ek
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    if any(x not in adj1[f] for x in path[1:-1]):
        return None
    hs = tuple(hinge[(path[i - 1], path[i])] for i in range(1, len(path)))
    return tuple(path), hs


def row_cap_path_falsifier(cl, cr, adj1):
    for f in cl:
        misses = [e for e in cr if e not in adj1.get(f, set())]
        for i, e0 in enumerate(misses):
            for ek in misses[i + 1 :]:
                got = shortest_exit_path(cr, adj1, f, e0, ek)
                if got is not None:
                    path, hinges = got
                    return {"row": f, "exit_path": path, "hinge_rows": hinges}
    return None


def cyclic_cap_falsifier(cl, cr, adj1):
    """Find a directed cap cycle e_i -> e_{i+1} of length at least 3."""
    arcs = {e: [] for e in cr}
    for e in cr:
        for f in cl:
            if e in adj1.get(f, set()):
                continue
            for ep in cr:
                if ep != e and ep in adj1.get(f, set()):
                    arcs[e].append((ep, f))

    for start in cr:
        stack = [(start, [], [], {start})]
        while stack:
            cur, exits, rows, seen = stack.pop()
            for nb, f in arcs[cur]:
                if nb == start:
                    if len(exits) + 1 >= 3:
                        return {
                            "exits": tuple(exits + [cur]),
                            "rows": tuple(rows + [f]),
                        }
                    continue
                if nb in seen:
                    continue
                if len(seen) >= len(cr):
                    continue
                stack.append((nb, exits + [cur], rows + [f], seen | {nb}))
    return None


def reachable_matched_exits(F0, E0, witnesses, m0, start):
    """Alternating closure exits reachable from an unmatched minimum exit."""
    used = set(m0.values())
    q = deque([("e", start)])
    seen = {("e", start)}
    matched = set()
    while q:
        typ, obj = q.popleft()
        if typ == "e":
            e = obj
            if e in used:
                matched.add(e)
            for h in F0:
                if e not in witnesses.get(h, set()):
                    continue
                if m0.get(h) == e:
                    continue
                node = ("f", h)
                if node not in seen:
                    seen.add(node)
                    q.append(node)
        else:
            h = obj
            e = m0.get(h)
            if e is None:
                continue
            node = ("e", e)
            if node not in seen:
                seen.add(node)
                q.append(node)
    return matched


def tt3_defect_falsifier(cl, cr, adj1, mask, F0, E0, witnesses_by_f, m0, deg_f1):
    """Flag a residual component whose defect digraph uses >=3 terminals."""
    defects = []
    terminal_vertices = set()
    for e in cr:
        missing = [f for f in cl if e not in adj1.get(f, set())]
        if not missing:
            continue
        miss_terms = {in_out(f, mask)[0] for f in missing}
        if len(miss_terms) != 1:
            return {
                "kind": "TT1_not_normalized",
                "exit": e,
                "missing": tuple(missing),
                "missing_terminals": tuple(sorted(miss_terms)),
            }
        inside, _outside = in_out(e, mask)
        tau = next(iter(miss_terms))
        defects.append((e, inside, tau, tuple(sorted(missing))))
        terminal_vertices.add(inside)
        terminal_vertices.add(tau)

    if len(terminal_vertices) <= 2:
        return None

    strict = []
    used = set(m0.values())
    e0 = set(E0)
    for e, _inside, _tau, _missing in defects:
        if e not in e0 or e in used:
            continue
        for u in reachable_matched_exits(F0, E0, witnesses_by_f, m0, e):
            if deg_f1.get(u, 0) > deg_f1.get(e, 0):
                strict.append((e, u, deg_f1.get(e, 0), deg_f1.get(u, 0)))
    return {
        "kind": "TT3_three_terminal",
        "terminals": tuple(sorted(terminal_vertices)),
        "defects": tuple(defects),
        "strict_reachable_exchanges": tuple(sorted(strict)),
    }


def check_forced_excess(n, adj, side, mask, st, det):
    _M, ell, _T, _mu, _cyc = st
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    inf_nonwit = 0
    finite_nonwit = 0
    for f in det["cross_m"]:
        for e in det["bdy_b"]:
            _lam, eps = forced_excess(n, adj, side, mask, ell, f, e)
            wit = f in witnesses[e]
            if wit and eps != 0:
                return False, {"f": f, "e": e, "witness": True, "epsilon": eps}
            if not wit:
                if eps >= INF:
                    inf_nonwit += 1
                else:
                    finite_nonwit += 1
                    if eps < 2:
                        return False, {"f": f, "e": e, "witness": False, "epsilon": eps}
    return True, {"inf_nonwit": inf_nonwit, "finite_nonwit": finite_nonwit}


def check_one_matching(st, det, mask, m0, info):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    witnesses_by_f = {f: {e for e in E if f in witnesses[e]} for f in F}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb[e] for e in E)
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}

    stats = Counter()
    stats[("forced_inf_nonwit", info["inf_nonwit"])] += 1
    stats[("forced_finite_nonwit", info["finite_nonwit"])] += 1
    for cl, cr in components(F1, rem, adj1):
        cl = tuple(cl)
        cr = tuple(cr)
        stats[("component", len(cl), len(cr))] += 1
        got = exit_cap_path_falsifier(cl, cr, adj1, mask)
        if got is not None:
            got["component"] = (cl, cr)
            got["stage0"] = tuple(sorted(m0.items()))
            return False, "B_exit_cap_path", got
        got = row_cap_path_falsifier(cl, cr, adj1)
        if got is not None:
            got["component"] = (cl, cr)
            got["stage0"] = tuple(sorted(m0.items()))
            return False, "C_row_cap_path", got
        got = cyclic_cap_falsifier(cl, cr, adj1)
        if got is not None:
            got["component"] = (cl, cr)
            got["stage0"] = tuple(sorted(m0.items()))
            return False, "D_cyclic_cap", got
        got = tt3_defect_falsifier(cl, cr, adj1, mask, F0, E0, witnesses_by_f, m0, deg_f1)
        if got is not None:
            got["component"] = (cl, cr)
            got["stage0"] = tuple(sorted(m0.items()))
            return False, "E_TT3_defect", got
    return True, "ok", {"stats": tuple(sorted(stats.items(), key=lambda kv: repr(kv[0])))}


def check(st, det, n, adj, side, mask, all_stage0=False, cap=100000):
    ok, info = check_forced_excess(n, adj, side, mask, st, det)
    if not ok:
        return False, "A_forced_excess", info

    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb[e] for e in E)
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return True, "skip_no_F1", info
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    if all_stage0:
        matchings, status, best_cost, count = enumerate_min_matchings(F0, E0, witnesses, deg_f1, cap)
        if status != "ok":
            return True, "too_many_stage0", {"F0": len(F0), "E0": len(E0), "best_cost": best_cost, "count": count}
    else:
        m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
        if m0 is None:
            return False, "stage0", {}
        matchings = [m0]

    combo = Counter()
    for m0 in matchings:
        ok, status, got = check_one_matching(st, det, mask, m0, info)
        if not ok:
            return ok, status, got
        combo.update(dict(got["stats"]))
    return True, "ok", {"stage0_count": len(matchings), "stats": tuple(sorted(combo.items(), key=lambda kv: repr(kv[0])))}


def scan_cut(name, n, adj, side, acc, first, max_add, all_stage0, cap):
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
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        ok, status, info = check(st, det, n, adj, side, mask, all_stage0, cap)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["info"][repr(info)] += 1
        if not ok and first is None:
            first = dict(
                name=name,
                n=n,
                side="".join(map(str, side)),
                v=v,
                R=str(rv),
                S=vertices_of_mask(n, mask),
                status=status,
                info=info,
            )
    return first


def scan_allmax(name, n, edges, acc, first, max_add, all_stage0, cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add, all_stage0, cap)
    return first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--all-stage0", action="store_true")
    ap.add_argument("--cap", type=int, default=100000)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "info": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add, args.all_stage0, args.cap)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_allmax("H2-allmax", n, edges, acc, first, args.max_add, args.all_stage0, args.cap)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add, args.all_stage0, args.cap)

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("info:")
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0]))[: args.top]:
        print(v, k)
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
