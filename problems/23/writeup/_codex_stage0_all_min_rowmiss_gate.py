"""Gate component-local row misses for all minimum-cost stage0 matchings.

This strengthens `_codex_stage0_all_min_gate.py`: instead of only checking the
two-terminal shape of residual missing pairs, it verifies the row-side target
directly for every minimum-cost matching of F0 into E0 (up to a cap):

    in each residual F1 component, every row misses at most one residual exit.

It is a proof-scouting diagnostic for the TH-rare flat-tie case.
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

    matchings, status, best_cost, count = enumerate_min_matchings(
        F0, E0, witnesses, deg_f1, cap
    )
    if status != "ok":
        return True, "too_many", {"F0": len(F0), "E0": len(E0), "best_cost": best_cost, "count": count}

    worst = 0
    for m0 in matchings:
        rem = tuple(e for e in E if e not in set(m0.values()))
        adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
        for cl, cr in components(F1, rem, adj1):
            for f in cl:
                miss = tuple(e for e in cr if e not in adj1.get(f, set()))
                worst = max(worst, len(miss))
                if len(miss) > 1:
                    return False, "row_miss", {
                        "matching": tuple(sorted(m0.items())),
                        "F0": F0,
                        "F1": F1,
                        "E0": E0,
                        "best_cost": best_cost,
                        "count": count,
                        "component": (tuple(sorted(cl)), tuple(sorted(cr))),
                        "f": f,
                        "miss": miss,
                    }
    return True, "ok", {"F0": len(F0), "E0": len(E0), "best_cost": best_cost, "count": count, "worst": worst}


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
            first = dict(
                name=name,
                n=n,
                side="".join(map(str, side)),
                v=v,
                R=str(rv),
                S=tuple(i for i in range(n) if (mask >> i) & 1),
                status=status,
                info=info,
            )
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
    ap.add_argument("--top", type=int, default=30)
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
