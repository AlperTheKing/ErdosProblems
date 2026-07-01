r"""Gate the exact mu(F0)-separation form of TH-rare.

For every minimum-cost stage0 matching (up to cap), and every F1 row f, look
at unmatched minimum exits E0 \ mu(F0) missed by f.  The global set may have
size > 1 in inherited blow-ups.  The TH-rare separation form predicts that
no two of these exits lie in the same residual co-witness component after
deleting mu(F0).
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_rare_exit_complement_gate import components
from _codex_stage0_all_min_gate import enumerate_min_matchings


def gate(st, det, cap):
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

    matchings, status, best_cost, count = enumerate_min_matchings(F0, E0, witnesses, deg_f1, cap)
    if status != "ok":
        return True, "too_many", {"F0": len(F0), "E0": len(E0), "best_cost": best_cost, "count": count}

    stats = Counter()
    for m0 in matchings:
        used = set(m0.values())
        rem = tuple(e for e in E if e not in used)
        adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
        comp_id_e = {}
        comp_id_f = {}
        for idx, (_cl, cr) in enumerate(components(F1, rem, adj1)):
            for g in _cl:
                comp_id_f[g] = idx
            for e in cr:
                comp_id_e[e] = idx
        for f in F1:
            fc = comp_id_f.get(f)
            missed_e0 = tuple(
                e for e in E0
                if e not in used
                and f not in witnesses[e]
                and comp_id_e.get(e) == fc
            )
            stats[("missed_e0_count", len(missed_e0))] += 1
            if len(missed_e0) < 2:
                continue
            stats["multi_global"] += 1
            by_comp = Counter(comp_id_e.get(e) for e in missed_e0)
            if any(v > 1 for v in by_comp.values()):
                return False, "same_component", {
                    "matching": tuple(sorted(m0.items())),
                    "F0": F0,
                    "F1": F1,
                    "E0": E0,
                    "best_cost": best_cost,
                    "count": count,
                    "f": f,
                    "missed_e0": missed_e0,
                    "by_comp": tuple(sorted(by_comp.items(), key=lambda kv: repr(kv[0]))),
                }
    return True, "ok", {"F0": len(F0), "E0": len(E0), "best_cost": best_cost, "count": count, "stats": tuple(sorted(stats.items(), key=lambda kv: repr(kv[0])))}


def scan_cut(name, n, adj, side, acc, first, max_add, cap):
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
        ok, status, info = gate(st, det, cap)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["info"][repr(info)] += 1
        if not ok and first is None:
            first = dict(name=name, n=n, side="".join(map(str, side)), v=v, R=str(rv), S=tuple(i for i in range(n) if (mask >> i) & 1), status=status, info=info)
    return first


def scan_allmax(name, n, edges, acc, first, max_add, cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add, cap)
    return first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--cap", type=int, default=100000)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "info": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add, args.cap)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_allmax("H2-allmax", n, edges, acc, first, args.max_add, args.cap)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add, args.cap)
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("info:")
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0]))[: args.top]:
        print(v, k)
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
