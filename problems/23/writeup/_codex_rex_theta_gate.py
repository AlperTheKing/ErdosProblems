"""Gate the 5/7 theta form behind residual singleton misses.

For selected completed seed+moat switches at vertices with R[v]<0, run the
rare stage-0 matching and inspect every residual miss (f,e):

    f in F1 misses residual exit e in its residual component.

The proposed row-side rigid shape says such a miss is not arbitrary: the
missed row f is the long side of a 5/7 terminal theta.  This diagnostic checks
the path-level part:

    every missed f has ell(f)=7 and contains, in some shortest row P of f, a
    contiguous shortest row Q of some length-5 bad edge g.

It records both the strong version (g is a crossing stage-0 edge in F0 for the
same switch) and the weak version (g is any bad edge of the cut).
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


def is_contiguous_subpath(needle, haystack):
    needle = list(needle)
    haystack = list(haystack)
    k = len(needle)
    if k > len(haystack):
        return False
    rev = list(reversed(needle))
    for i in range(len(haystack) - k + 1):
        block = haystack[i : i + k]
        if block == needle or block == rev:
            return True
    return False


def contiguous_subpath_positions(needle, haystack):
    needle = list(needle)
    haystack = list(haystack)
    k = len(needle)
    if k > len(haystack):
        return []
    rev = list(reversed(needle))
    out = []
    for i in range(len(haystack) - k + 1):
        block = haystack[i : i + k]
        if block == needle or block == rev:
            out.append(i)
    return out


def embedded_short_rows(cyc, ell, f, short_edges):
    """Return witnesses (g,Q,P) with Q a contiguous subpath of P."""
    out = []
    for p in cyc[f]:
        for g in short_edges:
            for q in cyc[g]:
                for pos in contiguous_subpath_positions(q, p):
                    out.append((g, tuple(q), tuple(p), pos))
    return out


def scan_switch(st, det, mask, acc, first, example_limit):
    _M, ell, _T, _mu, cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return first

    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb[e] for e in E)
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return first
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        acc["stage0_fail"] += 1
        return first

    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    e_io = {e: oriented(e, mask) for e in rem}
    f_io = {f: oriented(f, mask) for f in F1}

    any_short = tuple(sorted(g for g in cyc if ell[g] == 5))
    f0_short = tuple(sorted(g for g in F0 if ell[g] == 5))

    for cl, cr in components(F1, rem, adj1):
        cl = tuple(sorted(cl))
        cr = tuple(sorted(cr))
        for e in cr:
            for f in cl:
                if e in adj1[f]:
                    continue
                acc["misses"] += 1
                acc[("ell", ell[f])] += 1
                strong = embedded_short_rows(cyc, ell, f, f0_short)
                weak = strong or embedded_short_rows(cyc, ell, f, any_short)
                if strong:
                    acc["strong_f0_theta"] += 1
                if weak:
                    acc["weak_any_theta"] += 1
                if weak and ell[f] == 7:
                    acc["ok"] += 1
                else:
                    if first is None:
                        first = {
                            "f": f,
                            "ell": ell[f],
                            "e": e,
                            "lambda": lamb[e],
                            "e_io": e_io[e],
                            "f_io": f_io[f],
                            "component": (cl, cr),
                            "F0": F0,
                            "F0_lengths": tuple((g, ell[g]) for g in F0),
                            "candidates": tuple(sorted(adj1[f] & set(cr))),
                            "strong": bool(strong),
                            "weak": bool(weak),
                        }
                    acc["fail"] += 1
                if len(acc["examples"]) < example_limit and weak:
                    g, q, p, pos = weak[0]
                    acc[("window_pos", pos)] += 1
                    acc["examples"].append(
                        {
                            "f": f,
                            "e": e,
                            "g": g,
                            "ell_f": ell[f],
                            "ell_g": ell[g],
                            "strong": bool(strong),
                            "pos": pos,
                            "q": q,
                            "p": p,
                        }
                    )
                elif weak:
                    _g, _q, _p, pos = weak[0]
                    acc[("window_pos", pos)] += 1
    return first


def scan_cut(name, n, adj, side, acc, first, max_add, example_limit):
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
        acc["tested"] += 1
        first = scan_switch(st, det, mask, acc, first, example_limit)
    return first


def scan_allmax(name, n, edges, acc, first, max_add, example_limit):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add, example_limit)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--examples", type=int, default=5)
    args = parser.parse_args()

    acc = Counter()
    acc["examples"] = []
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add, args.examples)
            if first is not None:
                break
        if first is not None:
            break
    if first is None and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_allmax("H2-allmax", n, edges, acc, first, args.max_add, args.examples)
    if first is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add, args.examples)
            if first is not None:
                break

    examples = acc.pop("examples")
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"], "stage0_fail:", acc["stage0_fail"])
    print("misses:", acc["misses"], "ok:", acc["ok"], "fail:", acc["fail"])
    print("strong_f0_theta:", acc["strong_f0_theta"], "weak_any_theta:", acc["weak_any_theta"])
    print("ell_hist:", {k[1]: v for k, v in acc.items() if isinstance(k, tuple) and k[0] == "ell"})
    print("window_pos_hist:", {k[1]: v for k, v in acc.items() if isinstance(k, tuple) and k[0] == "window_pos"})
    print("first:", first or "")
    print("examples:")
    for ex in examples:
        print(ex)
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
