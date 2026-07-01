"""Exact residual Hall gate after the stage-0 rare matching.

The older residual gate used a sufficient complement-degree condition:
balanced components, row_miss <= 1, and col_miss <= n-2.  The hard H3 side
shows that row_miss <= 1 is too strong.  This diagnostic checks the actual
Hall condition on each residual F1/E component for the selected stage-0
matching.
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


def exact_hall_failure(cl, cr, adj, max_enum=22):
    """Return a deficient left subset, or None if Hall holds.

    This is exact for component size <= max_enum.  Larger components are marked
    as too_large by the caller instead of silently passing.
    """
    left = tuple(sorted(cl))
    if len(left) > max_enum:
        return "too_large"
    right = tuple(sorted(cr))
    n = len(left)
    neigh = []
    for f in left:
        mask = 0
        for i, e in enumerate(right):
            if e in adj.get(f, set()):
                mask |= 1 << i
        neigh.append(mask)
    for smask in range(1, 1 << n):
        nmask = 0
        size = 0
        for i in range(n):
            if (smask >> i) & 1:
                size += 1
                nmask |= neigh[i]
        if nmask.bit_count() < size:
            return {
                "left_subset": tuple(left[i] for i in range(n) if (smask >> i) & 1),
                "neighbor_subset": tuple(right[i] for i in range(len(right)) if (nmask >> i) & 1),
                "left_size": size,
                "neighbor_size": nmask.bit_count(),
            }
    return None


def gate(st, det, max_enum):
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
    sig = []
    for cl, cr in components(F1, rem, adj1):
        stats["components"] += 1
        stats[("size", len(cl), len(cr))] += 1
        row_miss = {f: sum(1 for e in cr if e not in adj1.get(f, set())) for f in cl}
        stats[("max_row_miss", max(row_miss.values()) if row_miss else 0)] += 1
        fail = exact_hall_failure(cl, cr, adj1, max_enum=max_enum)
        if fail == "too_large":
            return True, "too_large", {"component": (tuple(sorted(cl)), tuple(sorted(cr)))}
        if fail is not None:
            return False, "hall_fail", {
                "component": (tuple(sorted(cl)), tuple(sorted(cr))),
                "failure": fail,
                "stage0": tuple(sorted(m0.items())),
            }
        edges = sum(1 for f in cl for e in cr if e in adj1.get(f, set()))
        sig.append((len(cl), len(cr), edges, max(row_miss.values()) if row_miss else 0))
    return True, "ok", {"stats": dict(stats), "signature": tuple(sorted(sig))}


def scan_cut(name, n, adj, side, acc, max_add, max_enum):
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
        ok, status, info = gate(st, det, max_enum)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["stats"].update(info.get("stats", {}))
        if not ok and acc["first"] is None:
            acc["first"] = {
                "name": name,
                "n": n,
                "side": "".join(map(str, side)),
                "v": v,
                "S": tuple(i for i in range(n) if (mask >> i) & 1),
                "status": status,
                "info": info,
            }


def scan_allmax(name, n, edges, acc, max_add, max_enum):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add, max_enum)
        if acc["first"] is not None:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--h3-hard", action="store_true")
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--max-enum", type=int, default=22)
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
            scan_allmax("cen%d" % nn, n, edges, acc, args.max_add, args.max_enum)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if acc["first"] is None and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, args.max_add, args.max_enum)
    if acc["first"] is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add, args.max_enum)
            if acc["first"] is not None:
                break
    if acc["first"] is None and args.h3_hard:
        n, edges, _side = h_blowup(3)
        side = [int(c) for c in "111111111111111100000000000"]
        scan_cut("H3-hard", n, adj_from_edges(n, edges), side, acc, args.max_add, args.max_enum)
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
