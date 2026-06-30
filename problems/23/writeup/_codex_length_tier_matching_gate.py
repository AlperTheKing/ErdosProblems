"""Gate a two-stage length-tier matching pattern.

For each completed seed+moat switch, test whether the witness SDR can be
constructed by:

1. matching all minimum-length crossing bad edges into minimum-lambda exits;
2. matching every remaining exit using the non-minimum crossing bad edges.

This is a diagnostic strengthening of the Hall/SDR lemma.  It is exact but not
a proof artifact.
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


def max_matching(left, adj):
    match_r = {}

    def dfs(u, seen):
        for v in adj.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or dfs(match_r[v], seen):
                match_r[v] = u
                return True
        return False

    for u in left:
        dfs(u, set())
    return match_r


def enumerate_matchings(left, adj, cap):
    left = tuple(left)
    out = []

    def rec(i, used, pairs):
        if len(out) >= cap:
            return
        if i == len(left):
            out.append(dict(pairs))
            return
        u = left[i]
        for v in sorted(adj.get(u, ())):
            if v in used:
                continue
            used.add(v)
            pairs[u] = v
            rec(i + 1, used, pairs)
            pairs.pop(u)
            used.remove(v)

    rec(0, set(), {})
    return out


def stage1_extends(E_edges, F1, witnesses, used_e):
    E_rem = tuple(e for e in E_edges if e not in used_e)
    adj1 = {e: {f for f in F1 if f in witnesses[e]} for e in E_rem}
    match1 = max_matching(E_rem, adj1)
    return len(match1) == len(E_rem), len(E_rem), len(match1)


def tier_gate(st, det, all_stage0=False, enum_cap=100000):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    min_len = min(ell[f] for f in F_edges)
    min_lam = min(lamb[e] for e in E_edges)
    F0 = tuple(f for f in F_edges if ell[f] == min_len)
    E0 = tuple(e for e in E_edges if lamb[e] == min_lam)
    F1 = tuple(f for f in F_edges if ell[f] > min_len)

    adj0 = {f: {e for e in E0 if f in witnesses[e]} for f in F0}
    match0 = max_matching(F0, adj0)
    if len(match0) < len(F0):
        return False, "stage0", dict(min_len=min_len, min_lam=min_lam, F0=len(F0), E0=len(E0), matched=len(match0))

    checked_stage0 = 1
    if all_stage0:
        all_m = enumerate_matchings(F0, adj0, enum_cap)
        if len(all_m) >= enum_cap:
            return False, "stage0_enum_cap", dict(min_len=min_len, min_lam=min_lam, F0=len(F0), E0=len(E0), cap=enum_cap)
        checked_stage0 = len(all_m)
        for m0 in all_m:
            ok, e_rem_size, matched = stage1_extends(E_edges, F1, witnesses, set(m0.values()))
            if not ok:
                return False, "stage1_all", dict(min_len=min_len, min_lam=min_lam, F1=len(F1), E_rem=e_rem_size, matched=matched, checked_stage0=checked_stage0)
        E_rem = tuple(e for e in E_edges if e not in set(match0))
    else:
        ok, e_rem_size, matched = stage1_extends(E_edges, F1, witnesses, set(match0))
        E_rem = tuple(e for e in E_edges if e not in set(match0))
        if not ok:
            return False, "stage1", dict(min_len=min_len, min_lam=min_lam, F1=len(F1), E_rem=e_rem_size, matched=matched)

    psi_from_tiers = sum(ell[f] * ell[f] for f in F_edges) - sum(lamb[e] * lamb[e] for e in E_edges)
    return True, "ok", dict(
        min_len=min_len,
        min_lam=min_lam,
        F0=len(F0),
        E0=len(E0),
        F1=len(F1),
        E_rem=len(E_rem),
        psi=psi_from_tiers,
        checked_stage0=checked_stage0,
    )


def scan_cut(name, n, adj, side, acc, first, max_add, all_stage0, enum_cap):
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
        ok, status, info = tier_gate(st, det, all_stage0=all_stage0, enum_cap=enum_cap)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["info"][tuple(sorted(info.items()))] += 1
        if not ok and first is None:
            first = dict(name=name, n=n, side="".join(map(str, side)), v=v, R=str(rv), S=tuple(i for i in range(n) if (mask >> i) & 1), status=status, info=info)
    return first


def scan_graph_allmax(name, n, edges, acc, first, max_add, all_stage0, enum_cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add, all_stage0, enum_cap)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--all-stage0", action="store_true")
    parser.add_argument("--enum-cap", type=int, default=100000)
    args = parser.parse_args()

    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "info": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_graph_allmax("cen%d" % nn, n, edges, acc, first, args.max_add, args.all_stage0, args.enum_cap)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_graph_allmax("H2-allmax", n, edges, acc, first, args.max_add, args.all_stage0, args.enum_cap)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add, args.all_stage0, args.enum_cap)

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("info:")
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(v, dict(k))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
