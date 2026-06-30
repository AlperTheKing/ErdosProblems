"""Gate side-clean component conditions SC1 and SC4.

For each selected seed+moat switch, take the rare first-tier matching
F0 -> E0 and residual components C=(L,R_C) of G1=(F1,R).  For each component,
build the component terminal-prefix shadow W_C and test the proposed boundary
decomposition:

    delta_M(W_C) = L dotcup Z_C
    delta_B(W_C) = R_C dotcup mu(Z_C)

with Z_C subset F0.  The script tests both raw prefix shadows and B-closed
shadows inside S, because the exact geometric formulation is still being
scouted.

It also gates SC4: every residual non-universal side exit has at least two
F1-neighbors unless the component is K_{1,1}.
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
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary, mask_tuple
from _codex_blueclosed_hull_gate import blue_close_inside_s


def decompose(st, det):
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
    mu = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if mu is None:
        return None
    rem = tuple(e for e in E if e not in set(mu.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    return F0, F1, E0, rem, witnesses, mu, adj1


def shadow_mask(mask_s, prefixes, L, R):
    out = 0
    for f in L:
        for e in R:
            for pmask in prefixes[f].get(e, ()):
                out |= pmask
    return out


def check_sc1(n, adj, side, mask_s, F0, mu, L, R, mask_w):
    bdu, mdu = edge_boundary(n, adj, side, mask_w)
    L = set(L)
    R = set(R)
    F0 = set(F0)
    mu_img = {f: e for f, e in mu.items()}

    extra_m = mdu - L
    extra_b = bdu - R
    if not extra_m <= F0:
        return False, "M_extra_not_F0", {
            "W": mask_tuple(n, mask_w),
            "L": tuple(sorted(L)),
            "R": tuple(sorted(R)),
            "deltaM": tuple(sorted(mdu)),
            "deltaB": tuple(sorted(bdu)),
            "extraM": tuple(sorted(extra_m)),
            "extraB": tuple(sorted(extra_b)),
        }
    expected_b = {mu_img[f] for f in extra_m}
    if extra_b != expected_b:
        return False, "B_extra_not_muZ", {
            "W": mask_tuple(n, mask_w),
            "L": tuple(sorted(L)),
            "R": tuple(sorted(R)),
            "Z": tuple(sorted(extra_m)),
            "expectedB": tuple(sorted(expected_b)),
            "extraB": tuple(sorted(extra_b)),
            "deltaM": tuple(sorted(mdu)),
            "deltaB": tuple(sorted(bdu)),
        }
    return True, "ok", {"Zsize": len(extra_m), "Wsize": mask_w.bit_count()}


def check_sc4(L, R, adj1):
    if len(L) == 1 and len(R) == 1:
        return True, "ok", {}
    bad = []
    for e in R:
        neigh = {f for f in L if e in adj1.get(f, set())}
        if neigh != set(L) and len(neigh) < 2:
            bad.append((e, tuple(sorted(neigh))))
    if bad:
        return False, "SC4", {"bad": tuple(bad), "L": tuple(sorted(L)), "R": tuple(sorted(R))}
    return True, "ok", {}


def gate_switch(n, adj, side, st, mask_s):
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        return False, "terminal", {}
    dec = decompose(st, det)
    if dec is None:
        return False, "stage0", {}
    F0, F1, _E0, rem, witnesses, mu, adj1 = dec
    cyc = st[4]
    prefixes = {f: crossing_prefixes(mask_s, f, cyc[f]) for f in det["cross_m"]}
    sig = []
    for L, R in components(F1, rem, adj1):
        ok4, st4, info4 = check_sc4(L, R, adj1)
        if not ok4:
            return False, st4, info4

        raw = shadow_mask(mask_s, prefixes, L, R)
        ok_raw, st_raw, info_raw = check_sc1(n, adj, side, mask_s, F0, mu, L, R, raw)
        closed = blue_close_inside_s(n, adj, side, mask_s, raw)
        ok_closed, st_closed, info_closed = check_sc1(n, adj, side, mask_s, F0, mu, L, R, closed)
        if not ok_raw and not ok_closed:
            info_raw["closed_status"] = st_closed
            info_raw["closed_info"] = info_closed
            return False, "SC1", info_raw
        sig.append((len(L), len(R), "raw" if ok_raw else "closed", info_raw if ok_raw else info_closed))
    return True, "ok", {"components": tuple(sig)}


def scan_cut(name, n, adj, side, acc, first, max_add):
    if not Bconn(n, adj, side):
        return first
    st = struct_for_side(n, adj, side)
    if st is None:
        return first
    Rv = residuals(n, adj, side)
    if Rv is None:
        return first
    for v, rv in enumerate(Rv):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["no_switch"] += 1
            continue
        _seed, mask, _psi = got
        ok, status, info = gate_switch(n, adj, side, st, mask)
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
                S=mask_tuple(n, mask),
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
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    acc = {"tested": 0, "no_switch": 0, "status": Counter(), "info": Counter()}
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

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"])
    print("status:", dict(acc["status"]))
    print("info:")
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0]))[: args.top]:
        print(v, k)
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
