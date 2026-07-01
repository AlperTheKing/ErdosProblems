"""Classify residual row misses after rare stage0.

This is proof-scouting scaffolding.  It records, for every selected K2T
descent switch, which remaining exits a longer crossing bad edge fails to
witness, split by lambda tier and by the S-side endpoint of the exit.
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


def in_out(edge_pair, mask):
    a, b = edge_pair
    ina = (mask >> a) & 1
    inb = (mask >> b) & 1
    if ina and not inb:
        return a, b
    if inb and not ina:
        return b, a
    return None, None


def scan_switch(st, det, mask, acc, examples, limit):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb[e] for e in E)
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        acc["stage0_fail"] += 1
        return
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    for f in F1:
        f_in, _ = in_out(f, mask)
        misses = tuple(e for e in rem if f not in witnesses[e])
        if not misses:
            acc["row_miss_count"][0] += 1
            continue
        acc["row_miss_count"][len(misses)] += 1
        by_tier = Counter("min" if lamb[e] == min_lam else "long" for e in misses)
        by_inside = Counter(in_out(e, mask)[0] for e in misses)
        acc["tier_sig"][tuple(sorted(by_tier.items()))] += 1
        acc["inside_count"][len(by_inside)] += 1
        acc["pair_sig"][tuple(sorted((f_in, in_out(e, mask)[0], lamb[e], ell[f]) for e in misses))] += 1
        if len(examples) < limit:
            examples.append((f, ell[f], f_in, tuple((e, lamb[e], in_out(e, mask)[0], tuple(sorted(witnesses[e]))) for e in misses)))
    for cl, cr in components(F1, rem, adj1):
        for f in cl:
            f_in, _ = in_out(f, mask)
            misses = tuple(e for e in cr if e not in adj1.get(f, set()))
            acc["component_row_miss_count"][len(misses)] += 1
            if misses:
                by_tier = Counter("min" if lamb[e] == min_lam else "long" for e in misses)
                by_inside = Counter(in_out(e, mask)[0] for e in misses)
                acc["component_tier_sig"][tuple(sorted(by_tier.items()))] += 1
                acc["component_inside_count"][len(by_inside)] += 1
                acc["component_pair_sig"][tuple(sorted((f_in, in_out(e, mask)[0], lamb[e], ell[f]) for e in misses))] += 1


def scan_cut(name, n, adj, side, acc, examples, limit, max_add):
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
        acc["switches"] += 1
        scan_switch(st, det, mask, acc, examples, limit)


def scan_allmax(name, n, edges, acc, examples, limit, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, examples, limit, max_add)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--examples", type=int, default=20)
    args = ap.parse_args()

    acc = {
        "switches": 0,
        "no_switch": 0,
        "bad_terminal": 0,
        "stage0_fail": 0,
        "row_miss_count": Counter(),
        "tier_sig": Counter(),
        "inside_count": Counter(),
        "pair_sig": Counter(),
        "component_row_miss_count": Counter(),
        "component_tier_sig": Counter(),
        "component_inside_count": Counter(),
        "component_pair_sig": Counter(),
    }
    examples = []
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, acc, examples, args.examples, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, examples, args.examples, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, examples, args.examples, args.max_add)

    print("switches", acc["switches"], "no_switch", acc["no_switch"], "bad_terminal", acc["bad_terminal"], "stage0_fail", acc["stage0_fail"])
    print("row_miss_count", dict(acc["row_miss_count"]))
    print("tier_sig")
    for k, v in sorted(acc["tier_sig"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(v, k)
    print("inside_count", dict(acc["inside_count"]))
    print("top pair_sig")
    for k, v in sorted(acc["pair_sig"].items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        print(v, k)
    print("examples")
    for ex in examples:
        print(ex)
    print("component_row_miss_count", dict(acc["component_row_miss_count"]))
    print("component_tier_sig")
    for k, v in sorted(acc["component_tier_sig"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(v, k)
    print("component_inside_count", dict(acc["component_inside_count"]))
    print("component top pair_sig")
    for k, v in sorted(acc["component_pair_sig"].items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        print(v, k)


if __name__ == "__main__":
    main()
