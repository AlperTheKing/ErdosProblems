"""Gate the class quotient behind rare-exit residual Hall.

After rare-exit stage0, group remaining exits by their identical neighbor set
inside each residual F1 component.  The complement-degree residual is
equivalent to two quotient conditions:

  * every longer edge is absent from exits in total multiplicity at most one;
  * every exit class has enough longer-edge neighbors that a singleton exit
    has at least two witnesses unless the component is K_{1,1}.

This script records those class profiles exactly on the current selected
seed+moat battery.
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
from _codex_rare_exit_complement_gate import components


def class_profile(cl, cr, adj):
    cl = tuple(sorted(cl))
    cr = tuple(sorted(cr))
    n = len(cl)
    if len(cr) != n:
        return False, "unbalanced", {"L": len(cl), "R": len(cr)}

    classes = Counter()
    for e in cr:
        neigh = tuple(f for f in cl if e in adj.get(f, set()))
        classes[neigh] += 1

    row_missing = {}
    for f in cl:
        row_missing[f] = sum(count for neigh, count in classes.items() if f not in neigh)

    class_missing = {neigh: n - len(neigh) for neigh in classes}
    max_class_missing = max(0, n - 2)

    if row_missing and max(row_missing.values()) > 1:
        return False, "row_missing", {
            "n": n,
            "classes": tuple(sorted((neigh, count) for neigh, count in classes.items())),
            "row_missing": row_missing,
            "class_missing": class_missing,
        }
    if class_missing and max(class_missing.values()) > max_class_missing:
        return False, "class_missing", {
            "n": n,
            "classes": tuple(sorted((neigh, count) for neigh, count in classes.items())),
            "row_missing": row_missing,
            "class_missing": class_missing,
        }

    signature = tuple(sorted(
        (len(neigh), n - len(neigh), count)
        for neigh, count in classes.items()
    ))
    return True, "ok", {
        "n": n,
        "class_signature": signature,
        "row_missing_values": tuple(sorted(Counter(row_missing.values()).items())),
    }


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
        ok, status, info = class_profile(cl, cr, adj1)
        if not ok:
            info["cl"] = cl
            info["cr"] = cr
            return False, status, info
        sig.append((info["n"], info["class_signature"], info["row_missing_values"]))
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
    parser.add_argument("--top", type=int, default=40)
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
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0]))[:args.top]:
        print(v, k)
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
