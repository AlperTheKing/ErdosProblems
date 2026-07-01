"""Gate a replacement-exit rule for rare-stage residual defects.

After rare stage0, let e be a residual exit in a component and f a longer
crossing bad edge in the same component that e does not witness.  The tested
rule is:

    there exists a residual exit e' witnessed by f such that either
      outside(e') = outside(e), or inside(e') = inside(f), or
      e' = (inside(e), outside(f)) as an oriented side-door.

Here inside/outside are with respect to the completed seed+moat switch S.

This is meant as a geometric handle for the two-terminal residual theorem:
missed rows should be recoverable either through the same outside side-door or
through an exit based at the missed terminal.
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


def oriented(edge, mask):
    a, b = edge
    ain = (mask >> a) & 1
    bin_ = (mask >> b) & 1
    if ain and not bin_:
        return a, b
    if bin_ and not ain:
        return b, a
    return None, None


def gate(st, det, mask):
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
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", {}

    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    e_io = {e: oriented(e, mask) for e in rem}
    f_io = {f: oriented(f, mask) for f in F1}

    stats = Counter()
    examples = []
    for cl, cr in components(F1, rem, adj1):
        for e in sorted(cr):
            e_in, e_out = e_io[e]
            for f in sorted(cl):
                if e in adj1.get(f, set()):
                    continue
                f_in, _f_out = f_io[f]
                candidates = tuple(sorted(adj1.get(f, set()) & set(cr)))
                same_out = tuple(c for c in candidates if e_io[c][1] == e_out)
                same_terminal = tuple(c for c in candidates if e_io[c][0] == f_in)
                corner = tuple(c for c in candidates if e_io[c] == (e_in, f_io[f][1]))
                stats["missing"] += 1
                if same_out:
                    stats["same_out"] += 1
                if same_terminal:
                    stats["same_terminal"] += 1
                if corner:
                    stats["corner"] += 1
                if same_out or same_terminal or corner:
                    stats["ok"] += 1
                else:
                    examples.append(
                        dict(
                            e=e,
                            e_io=e_io[e],
                            f=f,
                            f_io=f_io[f],
                            component=(tuple(sorted(cl)), tuple(sorted(cr))),
                            candidates=tuple((c, e_io[c]) for c in candidates),
                        )
                    )
    if examples:
        return False, "replacement_fail", {"stats": dict(stats), "first": examples[0]}
    return True, "ok", {"stats": dict(stats)}


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
        ok, status, info = gate(st, det, mask)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["stats"].update(info.get("stats", {}))
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
    args = parser.parse_args()

    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "stats": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add)
            if first is not None:
                break
        if first is not None:
            break
    if first is None and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_allmax("H2-allmax", n, edges, acc, first, args.max_add)
    if first is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add)
            if first is not None:
                break

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()

