"""Gate a two-terminal swap form of rare-exit residual defects.

After canonical rare-exit stage0, every non-universal residual exit e has
missing longer bad edges with one S-inside endpoint tau.  This gate tests the
stronger form: in each residual component, all pairs (inside(e), tau(e)) use
at most two terminal vertices, and tau(e) != inside(e).  Thus defects are
oriented across a two-terminal pair.
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


def inside(edge_pair, mask):
    a, b = edge_pair
    if (mask >> a) & 1 and not ((mask >> b) & 1):
        return a
    if (mask >> b) & 1 and not ((mask >> a) & 1):
        return b
    return None


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
    f_term = {f: inside(f, mask) for f in F1}
    e_term = {e: inside(e, mask) for e in rem}
    sigs = []
    for cl, cr in components(F1, rem, adj1):
        pairs = []
        for e in sorted(cr):
            missing = tuple(f for f in cl if e not in adj1.get(f, set()))
            if not missing:
                continue
            terms = tuple(sorted(set(f_term[f] for f in missing)))
            if len(terms) != 1:
                return False, "mixed_missing_terminal", {"e": e, "missing": missing, "terms": terms}
            pair = (e_term[e], terms[0], len(missing))
            if pair[0] == pair[1]:
                return False, "loop_pair", {"pair": pair, "e": e, "missing": missing}
            pairs.append(pair)
        verts = sorted(set(x for a, b, _s in pairs for x in (a, b)))
        if len(verts) > 2:
            return False, "more_than_two_vertices", {"pairs": tuple(pairs), "verts": tuple(verts), "cl": tuple(sorted(cl)), "cr": tuple(sorted(cr))}
        sigs.append(tuple(sorted(pairs)))
    return True, "ok", {"components": tuple(sorted(sigs))}


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--top", type=int, default=50)
    args = ap.parse_args()
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
