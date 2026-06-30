"""Gate a complement-degree sufficient condition for rare-exit residual Hall.

After the rare-exit F0->E0 matching, each residual component between longer
bad edges F1 and remaining exits should be balanced and satisfy:

  * every left vertex misses at most one right vertex;
  * every right vertex is missed by at most n-2 left vertices in its component.

For a balanced n x n component this implies strict proper Hall:
if |Y|>=2 then every left vertex sees Y; if |Y|=1 the second condition gives
at least two neighbors.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import (
    best_seed_moat_mask,
    h_blowup,
    residuals,
)
from _codex_balanced_stage0_gate import min_cost_stage0


def components(left, right, adj):
    unseen_l = set(left)
    unseen_r = set(right)
    out = []
    while unseen_l or unseen_r:
        if unseen_l:
            start = ("L", next(iter(unseen_l)))
            unseen_l.remove(start[1])
        else:
            start = ("R", next(iter(unseen_r)))
            unseen_r.remove(start[1])
        q = [start]
        cl = set()
        cr = set()
        while q:
            side, node = q.pop()
            if side == "L":
                cl.add(node)
                for e in right:
                    if e in adj.get(node, set()) and e in unseen_r:
                        unseen_r.remove(e)
                        q.append(("R", e))
            else:
                cr.add(node)
                for f in left:
                    if node in adj.get(f, set()) and f in unseen_l:
                        unseen_l.remove(f)
                        q.append(("L", f))
        out.append((tuple(sorted(cl)), tuple(sorted(cr))))
    return out


def check_component(cl, cr, adj):
    n = len(cl)
    if len(cr) != n:
        return False, "unbalanced", {"L": len(cl), "R": len(cr)}
    row_miss = {f: sum(1 for e in cr if e not in adj.get(f, set())) for f in cl}
    col_miss = {e: sum(1 for f in cl if e not in adj.get(f, set())) for e in cr}
    if row_miss and max(row_miss.values()) > 1:
        return False, "row_miss", {"n": n, "row_miss": row_miss, "col_miss": col_miss}
    if col_miss and max(col_miss.values()) > max(0, n - 2):
        return False, "col_miss", {"n": n, "row_miss": row_miss, "col_miss": col_miss}
    return True, "ok", {"n": n, "edges": sum(1 for f in cl for e in cr if e in adj.get(f, set()))}


def gate(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    min_len = min(ell[f] for f in F_edges)
    min_lam = min(lamb[e] for e in E_edges)
    F0 = tuple(f for f in F_edges if ell[f] == min_len)
    F1 = tuple(f for f in F_edges if ell[f] > min_len)
    E0 = tuple(e for e in E_edges if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", {}
    rem = tuple(e for e in E_edges if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    sig = []
    for cl, cr in components(F1, rem, adj1):
        ok, status, info = check_component(cl, cr, adj1)
        if not ok:
            info["cl"] = cl
            info["cr"] = cr
            return False, status, info
        sig.append((info["n"], info["edges"]))
    return True, "ok", {"components": tuple(sorted(sig))}


def scan_cut(name, n, adj, side, acc, first, max_add):
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
        ok, status, info = gate(st, det)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["info"][repr(info)] += 1
        if not ok and first is None:
            first = dict(name=name, n=n, side="".join(map(str, side)), v=v, R=str(rv), S=tuple(i for i in range(n) if (mask >> i) & 1), status=status, info=info)
    return first


def scan_allmax(name, n, edges, acc, first, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    args = parser.parse_args()

    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "info": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_allmax("H2-allmax", n, edges, acc, first, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add)

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("info:")
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(v, k)
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
