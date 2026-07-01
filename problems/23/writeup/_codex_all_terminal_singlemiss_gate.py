"""Scope gate for component-local single-miss on all terminal-shadow switches.

This tests whether the residual component-local single-miss theorem is a
formal consequence of neutral terminal-shadow structure alone, or whether it
depends on the selected seed+moat / minimality construction.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components


def check(st, det):
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
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    if not F1:
        return True, "skip_no_F1", {}
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", {"F0": len(F0), "E0": len(E0)}
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    for cl, cr in components(F1, rem, adj1):
        if len(cl) != len(cr):
            return False, "unbalanced_component", {"L": len(cl), "R": len(cr), "cl": cl, "cr": cr}
        for f in cl:
            misses = tuple(e for e in cr if e not in adj1.get(f, set()))
            if len(misses) > 1:
                return False, "row_multi_miss", {"f": f, "misses": misses, "cl": cl, "cr": cr}
        for e in cr:
            deg = sum(1 for f in cl if e in adj1.get(f, set()))
            if 0 < deg < 2 and deg < len(cl):
                return False, "col_one_witness", {"e": e, "deg": deg, "cl": cl, "cr": cr}
    return True, "ok", {}


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None:
                continue
            ok, status, info = check(st, det)
            acc["switches"] += 1
            acc["status"][status] += 1
            if not ok and acc["first"] is None:
                acc["first"] = {
                    "name": name,
                    "n": n,
                    "side": "".join(map(str, side)),
                    "S": tuple(i for i in range(n) if (mask >> i) & 1),
                    "status": status,
                    "info": info,
                }
                return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=9)
    args = ap.parse_args()
    acc = {"switches": 0, "status": Counter(), "first": None}
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["switches"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N=%d switches=%d first=%s" % (nn, acc["switches"] - before, bool(acc["first"])), flush=True)
        if acc["first"] is not None:
            break
    print("switches:", acc["switches"])
    print("status:", dict(acc["status"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
