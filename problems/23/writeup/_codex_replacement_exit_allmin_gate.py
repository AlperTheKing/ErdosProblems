"""All-minimum-stage0 gate for the replacement-exit rule.

This is the tie-break-independent version of _codex_replacement_exit_gate.py.
It enumerates every minimum-cost F0->E0 stage0 matching (up to a cap) and
checks the same replacement rule for each resulting residual graph.
"""

import argparse
from collections import Counter

import _codex_replacement_exit_gate as repl
from _codex_stage0_all_min_gate import enumerate_min_matchings


def gate_all_min(st, det, mask, cap):
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

    total_stats = Counter()
    for m0 in matchings:
        rem = tuple(e for e in E if e not in set(m0.values()))
        adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
        e_io = {e: repl.oriented(e, mask) for e in rem}
        f_io = {f: repl.oriented(f, mask) for f in F1}
        for cl, cr in repl.components(F1, rem, adj1):
            for e in sorted(cr):
                e_in, e_out = e_io[e]
                for f in sorted(cl):
                    if e in adj1.get(f, set()):
                        continue
                    f_in, f_out = f_io[f]
                    candidates = tuple(sorted(adj1.get(f, set()) & set(cr)))
                    same_out = tuple(c for c in candidates if e_io[c][1] == e_out)
                    same_terminal = tuple(c for c in candidates if e_io[c][0] == f_in)
                    corner = tuple(c for c in candidates if e_io[c] == (e_in, f_out))
                    total_stats["missing"] += 1
                    if same_out:
                        total_stats["same_out"] += 1
                    if same_terminal:
                        total_stats["same_terminal"] += 1
                    if corner:
                        total_stats["corner"] += 1
                    if same_out or same_terminal or corner:
                        total_stats["ok"] += 1
                    else:
                        return False, "replacement_fail", {
                            "matching": tuple(sorted(m0.items())),
                            "e": e,
                            "e_io": e_io[e],
                            "f": f,
                            "f_io": f_io[f],
                            "component": (tuple(sorted(cl)), tuple(sorted(cr))),
                            "candidates": tuple((c, e_io[c]) for c in candidates),
                            "stats": dict(total_stats),
                        }
    return True, "ok", {"stats": dict(total_stats), "matchings": len(matchings)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--cap", type=int, default=100000)
    args = parser.parse_args()

    # Monkey-patch the gate used by repl.scan_* to avoid duplicating the scan
    # boilerplate.
    def gate(st, det, mask):
        return gate_all_min(st, det, mask, args.cap)

    repl.gate = gate
    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "stats": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in repl.subprocess.run([repl.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = repl.dec(g6)
            first = repl.scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add)
            if first is not None:
                break
        if first is not None:
            break
    if first is None and args.h2_allmax:
        n, edges, _side = repl.h_blowup(2)
        first = repl.scan_allmax("H2-allmax", n, edges, acc, first, args.max_add)

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
