"""Diagnostic gate for the proposed NO RE-ENTRY LENS sublemma.

For completed seed+moat switches, enumerate cutoff pairs (t,Y), build the
right-closed trapped prefix hull U, and check whether rows of crossing bad
edges outside X can meet U in a non-terminal component without a shorter
trapped bad edge.

This is a falsification/diagnostic script, not a proof artifact.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, mask_tuple


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


def oriented_from_s(mask_s, f, path0):
    a, b = f
    a_in = (mask_s >> a) & 1
    b_in = (mask_s >> b) & 1
    if a_in == b_in:
        return None
    tau = a if a_in else b
    path = list(path0)
    if path[0] != tau:
        path = list(reversed(path))
    return path if path and path[0] == tau else None


def has_nonterminal_u_component(mask_u, path):
    in_u = [bool((mask_u >> x) & 1) for x in path]
    i = 0
    while i < len(in_u):
        if not in_u[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(in_u) and in_u[j + 1]:
            j += 1
        if i != 0:
            return True, (i, j)
        i = j + 1
    return False, None


def scan_completed_switch(n, adj, side, st, mask_s, acc, first, cap_et, deficient_only):
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        acc["not_terminal"] += 1
        return first
    M, ell, _T, _mu, cyc = st
    C = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    wit_of_f = {f: set() for f in C}
    for e, fs in witnesses.items():
        for f in fs:
            wit_of_f[f].add(e)
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    prefixes = {f: crossing_prefixes(mask_s, f, cyc[f]) for f in C}
    if any(v is None for v in prefixes.values()):
        acc["bad_prefix"] += 1
        return first

    thresholds = sorted({ell[f] + 1 for f in C} | {lamb[e] + 1 for e in E})
    for t in thresholds:
        et = tuple(sorted(e for e in E if lamb[e] < t))
        if len(et) > cap_et:
            acc["skipped"] += 1
            continue
        for bits in range(1 << len(et)):
            Y = {et[i] for i in range(len(et)) if (bits >> i) & 1}
            X = {f for f in C if ell[f] < t and wit_of_f[f] <= Y}
            if deficient_only and len(X) <= len(Y):
                continue
            acc["pairs"] += 1
            mask_u = 0
            for f in X:
                for e in wit_of_f[f]:
                    for pmask in prefixes[f].get(e, ()):
                        mask_u |= pmask
            shorter_trapped = {
                g for g in C if ell[g] < max(ell[f] for f in C) and wit_of_f[g] <= Y
            }
            for g in C:
                if g in X:
                    continue
                has_shorter = any(ell[h] < ell[g] and wit_of_f[h] <= Y for h in shorter_trapped)
                for path0 in cyc[g]:
                    path = oriented_from_s(mask_s, g, path0)
                    if path is None:
                        continue
                    bad, comp = has_nonterminal_u_component(mask_u, path)
                    if not bad:
                        continue
                    acc["nonterminal"] += 1
                    if not has_shorter:
                        acc["fail"] += 1
                        if first is None:
                            first = dict(
                                t=t,
                                Y=tuple(sorted(Y)),
                                X=tuple(sorted(X)),
                                U=mask_tuple(n, mask_u),
                                g=g,
                                ell_g=ell[g],
                                component=comp,
                                path=tuple(path),
                                switch=mask_tuple(n, mask_s),
                            )
                        return first
    return first


def scan_cut(n, adj, side, acc, max_add, first, cap_et, deficient_only):
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
        acc["switches"] += 1
        first = scan_completed_switch(n, adj, side, st, mask, acc, first, cap_et, deficient_only)
    return first


def scan_graph_allmax(n, edges, acc, max_add, first, cap_et, deficient_only):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(n, adj, side, acc, max_add, first, cap_et, deficient_only)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--cap-et", type=int, default=14)
    parser.add_argument("--deficient-only", action="store_true")
    args = parser.parse_args()

    acc = Counter()
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_graph_allmax(n, edges, acc, args.max_add, first, args.cap_et, args.deficient_only)
            if first:
                break
        if first:
            break
    if not first and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_graph_allmax(n, edges, acc, args.max_add, first, args.cap_et, args.deficient_only)
    if not first:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            first = scan_cut(n, adj_from_edges(n, edges), side, acc, args.max_add, first, args.cap_et, args.deficient_only)
            if first:
                break

    print("switches:", acc["switches"])
    print("pairs:", acc["pairs"], "skipped:", acc["skipped"])
    print("nonterminal:", acc["nonterminal"], "fail:", acc["fail"])
    print("other:", dict(acc))
    print("first:", first or "")
    print("VERDICT:", "PASS" if not first else "FAIL")


if __name__ == "__main__":
    main()
