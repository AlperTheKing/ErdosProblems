"""Endpoint-side diagnostics for rare-exit two-star residual examples.

This is proof-scouting scaffolding.  It prints the terminal endpoint of every
longer crossing bad edge, the inner endpoint of every remaining exit, and the
residual witness matrix after the canonical rare-exit stage0 matching.
"""

import argparse
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import edge, terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components


def in_out(edge_pair, mask):
    a, b = edge_pair
    ina = (mask >> a) & 1
    inb = (mask >> b) & 1
    if ina and not inb:
        return a, b
    if inb and not ina:
        return b, a
    return None, None


def exit_counts_for_f(st, mask, f):
    _M, _ell, _T, _mu, cyc = st
    inside, _outside = in_out(f, mask)
    counts = {}
    for path0 in cyc[f]:
        path = list(path0)
        if path[0] != inside:
            path = list(reversed(path))
        bits = [(mask >> x) & 1 for x in path]
        r = 0
        while r + 1 < len(bits) and bits[r + 1] == 1:
            r += 1
        if r < len(path) - 1:
            e = edge(path[r], path[r + 1])
            counts[e] = counts.get(e, 0) + 1
    return counts


def describe(st, det, mask):
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
        return []
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}

    out = []
    for cl, cr in components(F1, rem, adj1):
        edges = sum(1 for f in cl for e in cr if e in adj1.get(f, set()))
        if edges == len(cl) * len(cr):
            continue
        cr = tuple(sorted(cr))
        cl = tuple(sorted(cl))
        item = {
            "F0": F0,
            "F1": cl,
            "E0": E0,
            "stage0": tuple(sorted(m0.items())),
            "rem": cr,
            "f_terms": tuple((f, ell[f], in_out(f, mask), exit_counts_for_f(st, mask, f)) for f in cl),
            "e_terms": tuple((e, lamb[e], in_out(e, mask), tuple(sorted(witnesses[e]))) for e in cr),
            "missing": tuple(
                (e, tuple(f for f in cl if e not in adj1.get(f, set())))
                for e in cr
            ),
        }
        out.append(item)
    return out


def scan_cut(name, n, adj, side, max_add, examples, limit):
    if len(examples) >= limit or not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if len(examples) >= limit:
            return
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            continue
        _seed, mask, psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            continue
        details = describe(st, det, mask)
        if details:
            examples.append(
                dict(
                    name=name,
                    n=n,
                    side="".join(map(str, side)),
                    v=v,
                    R=str(rv),
                    S=tuple(i for i in range(n) if (mask >> i) & 1),
                    psi=psi,
                    details=details,
                )
            )


def scan_allmax(name, n, edges, max_add, examples, limit):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, max_add, examples, limit)
        if len(examples) >= limit:
            return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    examples = []
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, args.max_add, examples, args.limit)
            if len(examples) >= args.limit:
                break
        if len(examples) >= args.limit:
            break
    if args.h2_allmax and len(examples) < args.limit:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, args.max_add, examples, args.limit)
    for t in range(2, args.h_inherited + 1):
        if len(examples) >= args.limit:
            break
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, args.max_add, examples, args.limit)

    print("examples:", len(examples))
    for ex in examples:
        print("=" * 72)
        print({k: ex[k] for k in ("name", "n", "side", "v", "R", "S", "psi")})
        for detail in ex["details"]:
            print("F0", detail["F0"])
            print("E0", detail["E0"])
            print("stage0", detail["stage0"])
            print("remaining exits", detail["rem"])
            print("F1 terms")
            for row in detail["f_terms"]:
                print(" ", row)
            print("exit terms")
            for row in detail["e_terms"]:
                print(" ", row)
            print("missing")
            for row in detail["missing"]:
                print(" ", row)


if __name__ == "__main__":
    main()
