"""Gate GPT-Pro's high-tier endpoint-contact atom (HT).

HT is a proposed local replacement for the long-lambda side of the
no-two-hole residual corridor proof:

  f in F1, p not witnessed by f, q witnessed by f,
  g in F1 witnesses both p and q, lambda(p)>L0,
  and p-g-q is the first hinge from p to an f-seen exit

should imply that some terminal f-row through q and terminal g-row through p
have both an inside-S and outside-S contact.  Then the splice lemma gives a
shorter B-geodesic.

This file only gates HT.  It does not assert the full no-two-hole theorem.
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
from _codex_th_corridor_gate import in_out, path_exit, vertices_of_mask


def oriented_parts(path0, mask, tau, e):
    got = path_exit(path0, mask, tau)
    if got is None:
        return None
    ex, path = got
    if ex != e:
        return None
    x, y = in_out(e, mask)
    if x is None:
        return None
    try:
        ix = path.index(x)
        iy = path.index(y)
    except ValueError:
        return None
    if iy != ix + 1:
        return None
    inside = frozenset(path[: ix + 1])
    outside = frozenset(path[iy:])
    return inside, outside, tuple(path)


def terminal_parts_for_exit(cyc, h, mask, e):
    tau, _sig = in_out(h, mask)
    if tau is None:
        return []
    out = []
    for path0 in cyc[h]:
        parts = oriented_parts(path0, mask, tau, e)
        if parts is not None:
            out.append(parts)
    return out


def distance_to_seen(cr, adj1, f, start):
    seen_exits = {e for e in cr if e in adj1[f]}
    if start in seen_exits:
        return 0
    j_adj = {e: set() for e in cr}
    for a in cr:
        for b in cr:
            if a >= b:
                continue
            if any(a in es and b in es for es in adj1.values()):
                j_adj[a].add(b)
                j_adj[b].add(a)
    q = deque([(start, 0)])
    seen = {start}
    while q:
        e, d = q.popleft()
        for nb in j_adj[e]:
            if nb in seen:
                continue
            if nb in seen_exits:
                return d + 1
            seen.add(nb)
            q.append((nb, d + 1))
    return None


def has_two_contact(st, mask, f, q, g, p):
    _M, _ell, _T, _mu, cyc = st
    fparts = terminal_parts_for_exit(cyc, f, mask, q)
    gparts = terminal_parts_for_exit(cyc, g, mask, p)
    for fin, fout, fpath in fparts:
        for gin, gout, gpath in gparts:
            if fin & gin and fout & gout:
                return True, {
                    "f_path": fpath,
                    "g_path": gpath,
                    "inside_contact": tuple(sorted(fin & gin)),
                    "outside_contact": tuple(sorted(fout & gout)),
                }
    return False, {"f_paths": len(fparts), "g_paths": len(gparts)}


def check(st, det, mask):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb.values())
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return True, "skip_no_F1", {}
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", {}
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}

    stats = Counter()
    for cl, cr0 in components(F1, rem, adj1):
        cr = tuple(sorted(cr0))
        for f in sorted(cl):
            for p in cr:
                if p in adj1[f] or lamb[p] <= min_lam:
                    continue
                d_seen = distance_to_seen(cr, adj1, f, p)
                if d_seen != 1:
                    stats[("high_miss_not_adjacent", d_seen)] += 1
                    continue
                for q in cr:
                    if q == p or q not in adj1[f]:
                        continue
                    gs = sorted(g for g in cl if p in adj1[g] and q in adj1[g])
                    if not gs:
                        continue
                    stats["ht_cases"] += 1
                    if not any(has_two_contact(st, mask, f, q, g, p)[0] for g in gs):
                        g = gs[0]
                        ok, info = has_two_contact(st, mask, f, q, g, p)
                        return False, "ht_no_two_contact", {
                            "f": f,
                            "p": p,
                            "q": q,
                            "g_candidates": tuple(gs),
                            "lambda_p": lamb[p],
                            "L0": min_lam,
                            "info": info,
                            "cr": cr,
                            "adj_f": tuple(sorted(adj1[f])),
                        }
                    stats["ht_ok"] += 1
    return True, "ok", {"stats": dict(stats)}


def scan_cut(name, n, adj, side, acc, max_add):
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
        ok, status, info = check(st, det, mask)
        acc["tested"] += 1
        acc["status"][status] += 1
        if status == "ok":
            acc["stats"].update(info["stats"])
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


def scan_allmax(name, n, edges, acc, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add)
        if acc["first"] is not None:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--max-add", type=int, default=1)
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
            scan_allmax("cen%d" % nn, n, edges, acc, args.max_add)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if acc["first"] is None and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, args.max_add)
    if acc["first"] is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add)
            if acc["first"] is not None:
                break
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
