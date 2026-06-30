"""Dump one rare-exit residual example for each sparse component signature.

This is diagnostic scaffolding for the terminal-shadow Hall proof.  It uses the
same completed seed+moat switch selector as the side-door gates, performs the
canonical shortest-tier stage0 matching, and prints residual components that
are not complete bipartite graphs.
"""

import argparse
import subprocess
from collections import defaultdict

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components


def sparse_components(st, det, mask):
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
        cr_sorted = tuple(sorted(cr))
        rows = tuple((f, "".join("1" if e in adj1.get(f, set()) else "." for e in cr_sorted)) for f in sorted(cl))
        row_terms = {}
        for f in sorted(cl):
            a, b = f
            if (mask >> a) & 1:
                row_terms[f] = a
            elif (mask >> b) & 1:
                row_terms[f] = b
            else:
                row_terms[f] = None
        classes = []
        for e in cr_sorted:
            neigh = tuple(f for f in sorted(cl) if e in adj1.get(f, set()))
            missing = tuple(f for f in sorted(cl) if f not in neigh)
            classes.append((e, neigh, missing))
        class_sig = tuple(sorted((len(neigh), len(missing)) for _e, neigh, missing in classes))
        out.append(
            dict(
                signature=(len(cl), len(cr), edges, class_sig),
                F0=F0,
                F1=F1,
                E0=E0,
                stage0=tuple(sorted(m0.items())),
                rem=cr_sorted,
                rows=rows,
                row_terms=tuple(sorted(row_terms.items())),
                classes=tuple(classes),
            )
        )
    return out


def scan_cut(name, n, adj, side, max_add, examples):
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
            continue
        _seed, mask, psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            continue
        for comp in sparse_components(st, det, mask):
            examples.setdefault(
                comp["signature"],
                dict(
                    name=name,
                    n=n,
                    side="".join(map(str, side)),
                    v=v,
                    R=str(rv),
                    S=tuple(i for i in range(n) if (mask >> i) & 1),
                    psi=psi,
                    comp=comp,
                ),
            )


def scan_allmax(name, n, edges, max_add, examples):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, max_add, examples)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    args = parser.parse_args()

    examples = {}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, args.max_add, examples)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, args.max_add, examples)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, args.max_add, examples)

    print("sparse signatures:", len(examples))
    for sig, ex in sorted(examples.items()):
        print("=" * 72)
        print("signature", sig)
        print("example", {k: ex[k] for k in ("name", "n", "side", "v", "R", "S", "psi")})
        comp = ex["comp"]
        print("F1", comp["F1"])
        print("F1 inside terminals", comp["row_terms"])
        print("remaining exits", comp["rem"])
        print("stage0", comp["stage0"])
        print("classes")
        for e, neigh, missing in comp["classes"]:
            print(" ", e, "neigh", neigh, "missing", missing)
        print("matrix")
        for f, row in comp["rows"]:
            print(" ", f, row)


if __name__ == "__main__":
    main()
