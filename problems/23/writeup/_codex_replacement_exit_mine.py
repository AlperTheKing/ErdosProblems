"""Mine replacement-exit shapes for rare-stage residual singleton holes.

This is a diagnostic companion to _codex_replacement_exit_gate.py.  It records
the exact shape of every residual miss (f,e) after the rare stage0 matching:
length tier, component size, and which of the three replacement identities hold.
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
from _codex_replacement_exit_gate import oriented


def mine_switch(st, det, mask, out, examples, limit):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb[e] for e in E)
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        out["stage0_fail"] += 1
        return

    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    e_io = {e: oriented(e, mask) for e in rem}
    f_io = {f: oriented(f, mask) for f in F1}

    for cl, cr in components(F1, rem, adj1):
        cl = tuple(sorted(cl))
        cr = tuple(sorted(cr))
        row_sets = tuple(sorted(tuple(sorted(cr.index(e) for e in adj1[f] & set(cr))) for f in cl))
        col_degs = tuple(sorted(sum(1 for f in cl if e in adj1[f]) for e in cr))
        comp_sig = (len(cl), len(cr), row_sets, col_degs)
        out[("component", comp_sig)] += 1
        for e in cr:
            e_in, e_out = e_io[e]
            e_tier = "min" if lamb[e] == min_lam else "long"
            for f in cl:
                if e in adj1[f]:
                    continue
                f_in, f_out = f_io[f]
                candidates = tuple(sorted(adj1[f] & set(cr)))
                same_out = tuple(c for c in candidates if e_io[c][1] == e_out)
                same_terminal = tuple(c for c in candidates if e_io[c][0] == f_in)
                corner = tuple(c for c in candidates if e_io[c] == (e_in, f_out))
                flags = "".join(
                    bit
                    for bit, ok in (
                        ("O", bool(same_out)),
                        ("T", bool(same_terminal)),
                        ("C", bool(corner)),
                    )
                    if ok
                )
                key = (
                    "ell",
                    ell[f],
                    "lam",
                    lamb[e],
                    "tier",
                    e_tier,
                    "comp",
                    (len(cl), len(cr)),
                    "seen",
                    len(candidates),
                    "flags",
                    flags,
                    "comp_sig",
                    comp_sig,
                )
                out[key] += 1
                if len(examples) < limit:
                    examples.append(
                        {
                            "f": f,
                            "ell": ell[f],
                            "e": e,
                            "lambda": lamb[e],
                            "e_io": e_io[e],
                            "f_io": f_io[f],
                            "component": (cl, cr),
                            "candidates": tuple((c, e_io[c]) for c in candidates),
                            "flags": flags,
                        }
                    )


def scan_cut(name, n, adj, side, acc, examples, limit, max_add):
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
        acc["tested"] += 1
        mine_switch(st, det, mask, acc["hist"], examples, limit)


def scan_allmax(name, n, edges, acc, examples, limit, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, examples, limit, max_add)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--examples", type=int, default=8)
    args = parser.parse_args()

    acc = {
        "tested": 0,
        "no_switch": 0,
        "bad_terminal": 0,
        "stage0_fail": 0,
        "hist": Counter(),
    }
    examples = []
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, acc, examples, args.examples, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, examples, args.examples, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, examples, args.examples, args.max_add)

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"], "stage0_fail:", acc["stage0_fail"])
    print("hist:")
    for key, count in acc["hist"].most_common():
        print(count, key)
    print("examples:")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
