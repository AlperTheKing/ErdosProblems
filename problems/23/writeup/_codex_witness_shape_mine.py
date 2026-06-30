"""Mine witness-graph shapes for completed seed+moat K2T switches.

This is a diagnostic script for the terminal-shadow Hall proof.  It selects the
same completed switches as _codex_sidedoor_prefix_hull_gate.py and records
small graph invariants of the witness relation C=delta_M(S) -- E=delta_B(S).
"""

import argparse
import itertools
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, T, _mu, cyc = st
    if not M:
        return None
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


def best_seed_moat_mask(n, adj, side, st, v, max_add):
    gamma0 = gamma_of(n, adj, side)
    _M, ell, _T, _mu, cyc = st
    best = None
    for seed in length_bundle_half_switches(ell, cyc, v):
        if not ((seed >> v) & 1):
            continue
        cand = best_moat_completion(n, adj, side, st, seed, max_add)
        if cand is None:
            continue
        added, _negpsi, mask, psi = cand
        gamma2 = gamma_of(n, adj, flip_side(side, mask))
        if gamma2 is None or gamma2 >= gamma0:
            continue
        key = (added, -psi, mask)
        if best is None or key < best[0]:
            best = (key, seed, mask, psi)
    return None if best is None else best[1:]


def min_hall_slack(det, cap):
    C = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if len(E) > cap:
        return None, ("skipped", len(E))
    wit_of_f = {f: set() for f in C}
    for e, fs in det["witnesses"].items():
        for f in fs:
            wit_of_f.setdefault(f, set()).add(e)

    min_proper = None
    arg = None
    for bits in range(1, (1 << len(E)) - 1):
        Y = {E[i] for i in range(len(E)) if (bits >> i) & 1}
        X = {f for f in C if wit_of_f[f] <= Y}
        slack = len(Y) - len(X)
        if min_proper is None or slack < min_proper:
            min_proper = slack
            arg = (len(Y), len(X), tuple(sorted(len(wit_of_f[f]) for f in X)))
    return min_proper, arg


def shape_key(st, det, hall_cap):
    _M, ell, _T, _mu, _cyc = st
    C = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    wit_of_f = {f: set() for f in C}
    deg_e = {e: 0 for e in E}
    for e, fs0 in det["witnesses"].items():
        fs = set(fs0)
        deg_e[e] = len(fs)
        for f in fs:
            wit_of_f.setdefault(f, set()).add(e)
    bad_lengths = tuple(sorted(ell[f] for f in C))
    f_degrees = tuple(sorted(len(wit_of_f[f]) for f in C))
    e_degrees = tuple(sorted(deg_e[e] for e in E))
    lambdas = tuple(sorted(min(ell[f] for f in det["witnesses"][e]) for e in E))
    strict_exits = sum(1 for e in E if any(ell[f] > min(ell[g] for g in det["witnesses"][e]) for f in det["witnesses"][e]))
    min_slack, slack_arg = min_hall_slack(det, hall_cap)
    return (len(C), bad_lengths, f_degrees, e_degrees, lambdas, strict_exits, min_slack, slack_arg)


def scan_cut(name, n, adj, side, acc, max_add, examples, hall_cap):
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
        seed, mask, psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        key = shape_key(st, det, hall_cap)
        acc["shapes"][key] += 1
        acc["moat"][(mask & ~seed).bit_count()] += 1
        if key not in examples:
            examples[key] = (name, n, "".join(map(str, side)), v, str(rv), tuple(i for i in range(n) if (mask >> i) & 1), psi)


def scan_graph_allmax(name, n, edges, acc, max_add, examples, hall_cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add, examples, hall_cap)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--hall-cap", type=int, default=14)
    args = parser.parse_args()

    acc = {"shapes": Counter(), "moat": Counter(), "no_switch": 0, "bad_terminal": 0}
    examples = {}

    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph_allmax("cen%d" % nn, n, edges, acc, args.max_add, examples, args.hall_cap)

    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_graph_allmax("H?AFBo][2]-allmax", n, edges, acc, args.max_add, examples, args.hall_cap)

    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add, examples, args.hall_cap)

    print("shapes:", len(acc["shapes"]))
    print("moat:", dict(sorted(acc["moat"].items())))
    print("no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    for idx, (key, count) in enumerate(acc["shapes"].most_common(args.top), 1):
        size, lens, fdeg, edeg, lambdas, strict_exits, min_slack, slack_arg = key
        print("-" * 72)
        print("rank", idx, "count", count)
        print("size", size, "lens", lens)
        print("fdeg", fdeg, "edeg", edeg)
        print("lambdas", lambdas, "strict_exits", strict_exits)
        print("min_proper_slack", min_slack, "arg", slack_arg)
        print("example", examples[key])


if __name__ == "__main__":
    main()
