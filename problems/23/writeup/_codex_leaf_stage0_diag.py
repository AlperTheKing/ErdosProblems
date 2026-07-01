"""Diagnose how rare stage0 consumes laminar missed-exit leaves.

For selected seed+moat switches, record each laminar leaf K of the global
miss-set family and how it intersects the residual graph after the min-cost
stage0 matching.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
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
        return None
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in E if f in witnesses[e]} for f in F}
    leaves = laminar_leaves([set(E) - exits_of_f[f] for f in F])
    if leaves is None:
        return None
    min_len = min(ell[f] for f in F)
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_lam = min(lamb.values())
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return None
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return None
    used = set(m0.values())
    rem = tuple(e for e in E if e not in used)
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    comps = list(components(F1, rem, adj1))

    rows = []
    for leaf in leaves:
        leaf = set(leaf)
        miss_f1 = tuple(f for f in F1 if leaf <= (set(E) - exits_of_f[f]))
        touch_f1 = tuple(f for f in F1 if exits_of_f[f] & leaf)
        leaf_used = leaf & used
        leaf_rem = leaf & set(rem)
        comp_intersections = []
        for cl, cr in comps:
            hit = tuple(sorted(set(cr) & leaf_rem))
            if hit:
                miss_in_comp = tuple(f for f in cl if leaf <= (set(E) - exits_of_f[f]))
                comp_intersections.append((len(cl), len(cr), len(hit), len(miss_in_comp), hit))
        rows.append(
            dict(
                size=len(leaf),
                used=len(leaf_used),
                rem=len(leaf_rem),
                min_lam=sum(1 for e in leaf if lamb[e] == min_lam),
                long_lam=sum(1 for e in leaf if lamb[e] > min_lam),
                miss_f1=len(miss_f1),
                touch_f1=len(touch_f1),
                comps=tuple((a, b, h, m) for a, b, h, m, _hit in comp_intersections),
            )
        )
    return rows


def scan_cut(name, n, adj, side, acc, examples, max_add):
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
        rows = check(st, det)
        if rows is None:
            acc["skip"] += 1
            continue
        acc["switches"] += 1
        for r in rows:
            key = (r["size"], r["used"], r["rem"], r["min_lam"], r["long_lam"], r["miss_f1"], r["touch_f1"], r["comps"])
            acc["leaf_sig"][key] += 1
            for comp in r["comps"]:
                acc["comp_sig"][comp] += 1
        if len(examples) < 12:
            examples.append((name, "".join(map(str, side)), v, rows))


def scan_allmax(name, n, edges, acc, examples, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, examples, max_add)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--max-add", type=int, default=1)
    args = ap.parse_args()

    acc = {"switches": 0, "no_switch": 0, "bad_terminal": 0, "skip": 0, "leaf_sig": Counter(), "comp_sig": Counter()}
    examples = []
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d:%s" % (nn, g6), n, edges, acc, examples, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, examples, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, examples, args.max_add)

    print("switches", acc["switches"], "no_switch", acc["no_switch"], "bad_terminal", acc["bad_terminal"], "skip", acc["skip"])
    print("leaf_sig")
    for k, v in sorted(acc["leaf_sig"].items(), key=lambda kv: (-kv[1], kv[0]))[:40]:
        print(v, k)
    print("comp_sig")
    for k, v in sorted(acc["comp_sig"].items(), key=lambda kv: (-kv[1], kv[0]))[:40]:
        print(v, k)
    print("examples")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
