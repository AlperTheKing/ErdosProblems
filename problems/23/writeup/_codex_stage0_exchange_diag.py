"""Inspect rare stage0 matching around sparse residual defects.

This diagnostic prints F0-E0 witness neighborhoods and deg_F1 costs for cases
where the residual witness graph after stage0 is not complete.  It is meant to
guide the exchange proof in the two-terminal residual theorem.
"""

import argparse
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components


def inside(edge_pair, mask):
    a, b = edge_pair
    if (mask >> a) & 1 and not ((mask >> b) & 1):
        return a
    if (mask >> b) & 1 and not ((mask >> a) & 1):
        return b
    return None


def sparse_details(st, det, mask):
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
    used = set(m0.values())
    rem = tuple(e for e in E if e not in used)
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    f_term = {f: inside(f, mask) for f in F1}

    out = []
    for cl, cr in components(F1, rem, adj1):
        cl = tuple(sorted(cl))
        cr = tuple(sorted(cr))
        if sum(1 for f in cl for e in cr if e in adj1.get(f, set())) == len(cl) * len(cr):
            continue
        out.append(
            dict(
                F0=F0,
                F1=F1,
                E0=E0,
                deg_f1=tuple(sorted((e, deg_f1[e]) for e in E0)),
                stage0=tuple(sorted(m0.items())),
                used=tuple(sorted(used)),
                unused_E0=tuple(sorted(e for e in E0 if e not in used)),
                F0_neigh=tuple(sorted((e, tuple(f for f in F0 if f in witnesses[e])) for e in E0)),
                component=(cl, cr),
                missing=tuple(
                    (e, inside(e, mask), tuple(f for f in cl if e not in adj1.get(f, set())), tuple(sorted(set(f_term[f] for f in cl if e not in adj1.get(f, set())))))
                    for e in cr
                    if any(e not in adj1.get(f, set()) for f in cl)
                ),
            )
        )
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
        details = sparse_details(st, det, mask)
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()

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
        for d in ex["details"]:
            print("F0", d["F0"])
            print("F1", d["F1"])
            print("E0", d["E0"])
            print("deg_f1", d["deg_f1"])
            print("stage0", d["stage0"])
            print("used", d["used"])
            print("unused_E0", d["unused_E0"])
            print("F0_neigh")
            for row in d["F0_neigh"]:
                print(" ", row)
            print("component", d["component"])
            print("missing", d["missing"])


if __name__ == "__main__":
    main()
