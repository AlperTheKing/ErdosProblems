"""Exact fixed-row all-subset Slack-CAGE profiler.

This is a guardrail for larger named graphs where checking every row against
every subset is too expensive.  It chooses the row with smallest full-set
Slack-CAGE/GERSH margin in a true connected gamma-minimum maximum cut, then
checks that one row against every U subset V exactly.

For a fixed row Q, D_Q(U) is accumulated by adding each row atom contribution
to every supermask of its vertex set.  All quantities are scaled to integers
by lcm(25, all |cyc[g]|), so no floating point is used.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import math
from array import array
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski
    from _codex_mycgrotzsch_exact_maxcut_c5lift import (
        enumerate_maxcuts_gray,
        gamma_for_side,
        side_list,
        side_string,
    )
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def fmt_int_scaled(x: int, scale: int) -> str:
    f = F(x, scale)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def graph_by_name(name: str):
    if name == "Grotzsch":
        return mycielski(5, Cn(5))
    if name == "MycGrotzsch":
        return mycielski(*mycielski(5, Cn(5)))
    if name.startswith("g6:"):
        return dec(name[3:])
    raise ValueError(f"unknown graph name: {name}")


def gamma_min_sides(n, edges):
    adj = adj_of(n, edges)
    if n <= 23:
        best, max_sides = enumerate_maxcuts_gray(n, edges)
        connected = []
        gammas = []
        for side_int in max_sides:
            side = side_list(n, side_int)
            if not Bconn(n, adj, side):
                continue
            gamma = gamma_for_side(n, adj, side)
            if gamma is None:
                continue
            connected.append(side_int)
            gammas.append(gamma)
        min_gamma = min(gammas) if gammas else None
        gmin = [s for s, g in zip(connected, gammas) if g == min_gamma]
        return best, min_gamma, [side_list(n, s) for s in gmin], [side_string(n, s) for s in gmin]

    _adj, cuts = gmins(n, edges)
    best = None
    min_gamma = None
    out = []
    out_s = []
    for side_s in cuts:
        side = [int(c) for c in side_s]
        gamma = gamma_for_side(n, adj, side)
        if gamma is None:
            continue
        if min_gamma is None or gamma < min_gamma:
            min_gamma = gamma
            out = [side]
            out_s = ["".join(map(str, side))]
        elif gamma == min_gamma:
            out.append(side)
            out_s.append("".join(map(str, side)))
    return best, min_gamma, out, out_s


def iter_supermasks(pmask: int, allmask: int):
    free = allmask ^ pmask
    sub = free
    while True:
        yield pmask | sub
        if sub == 0:
            break
        sub = (sub - 1) & free


def build_cut_data(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    if not M_raw:
        return None
    M = [norm(g) for g in M_raw]
    ell = {norm(g): ell_raw[g] for g in M_raw}
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    E = {norm(e) for e in edges}
    Mset = set(M)
    B = E - Mset
    return M, ell, cyc, E, B, Mset


def full_vertex_tw(n, M, cyc):
    tw = [F(0) for _ in range(n)]
    for g in M:
        den = len(cyc[g])
        mass = F(1, den)
        for P in cyc[g]:
            for v in P:
                tw[v] += mass
    return tw


def choose_worst_full_row(n, M, cyc):
    tw = full_vertex_tw(n, M, cyc)
    eta = F(n * n, 25) - len(M)
    ceiling = F(n) + eta
    best = None
    for f in M:
        for Q in cyc[f]:
            lhs = sum((tw[v] for v in Q), F(0))
            margin = ceiling - lhs
            rec = (margin, f, tuple(Q), lhs, ceiling)
            if best is None or rec < best:
                best = rec
    return best


def row_mask(P):
    out = 0
    for v in P:
        out |= 1 << v
    return out


def build_sigma_array(n, B, Mset):
    subset_count = 1 << n
    weights = [[] for _ in range(n)]
    total = [0] * n
    for u, v in B:
        weights[u].append((v, 1))
        weights[v].append((u, 1))
        total[u] += 1
        total[v] += 1
    for u, v in Mset:
        weights[u].append((v, -1))
        weights[v].append((u, -1))
        total[u] -= 1
        total[v] -= 1

    sigma = array("h", [0]) * subset_count
    for mask in range(1, subset_count):
        lb = mask & -mask
        v = lb.bit_length() - 1
        prev = mask ^ lb
        inside = 0
        for u, w in weights[v]:
            if (prev >> u) & 1:
                inside += w
        sigma[mask] = sigma[prev] + total[v] - 2 * inside
    return sigma


def profile_fixed_row(n, M, cyc, B, Mset, Q):
    scale = 25
    for g in M:
        scale = math.lcm(scale, len(cyc[g]))

    subset_count = 1 << n
    allmask = subset_count - 1
    demand = array("q", [0]) * subset_count
    qset = set(Q)
    atoms_used = 0
    additions = 0

    for g in M:
        den = len(cyc[g])
        for P in cyc[g]:
            inter = len(qset.intersection(P))
            if inter == 0:
                continue
            coeff = inter * (scale // den)
            pmask = row_mask(P)
            atoms_used += 1
            for umask in iter_supermasks(pmask, allmask):
                demand[umask] += coeff
                additions += 1

    sigma = build_sigma_array(n, B, Mset)
    eta_int = (n * n - 25 * len(M)) * (scale // 25)

    best = None
    best_empty = None
    best_full = None
    best_proper = None
    best_counted = None
    for mask in range(subset_count):
        rhs = (mask.bit_count() + sigma[mask]) * scale + eta_int
        margin = rhs - demand[mask]
        rec = (margin, mask, demand[mask], rhs, mask.bit_count(), int(sigma[mask]))
        if best is None or margin < best[0]:
            best = rec
        if mask == 0:
            best_empty = rec
        elif mask == allmask:
            best_full = rec
        elif best_proper is None or margin < best_proper[0]:
            best_proper = rec
        if demand[mask] > 0 and (best_counted is None or margin < best_counted[0]):
            best_counted = rec

    return {
        "scale": scale,
        "atoms_used": atoms_used,
        "additions": additions,
        "best": best,
        "empty": best_empty,
        "full": best_full,
        "proper": best_proper,
        "counted": best_counted,
    }


def mask_tuple(mask: int, n: int):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def print_rec(label, rec, n, scale):
    margin, mask, lhs, rhs, size, sigma = rec
    print(label + ":")
    print("  margin:", fmt_int_scaled(margin, scale))
    print("  U:", mask_tuple(mask, n))
    print("  lhs:", fmt_int_scaled(lhs, scale))
    print("  rhs:", fmt_int_scaled(rhs, scale))
    print("  size:", size)
    print("  sigma:", sigma)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="MycGrotzsch")
    ap.add_argument("--side-index", type=int, default=0)
    ap.add_argument("--row-index", type=int, default=None)
    args = ap.parse_args()

    n, edges = graph_by_name(args.graph)
    maxcut_value, min_gamma, sides, side_strings = gamma_min_sides(n, edges)
    if not sides:
        raise SystemExit("no connected gamma-min maximum cut found")
    side = sides[args.side_index]
    data = build_cut_data(n, edges, side)
    if data is None:
        raise SystemExit("selected side has no row data")
    M, ell, cyc, _E, B, Mset = data

    rows = [(f, tuple(Q)) for f in M for Q in cyc[f]]
    if args.row_index is None:
        full_margin, f, Q, full_lhs, full_rhs = choose_worst_full_row(n, M, cyc)
    else:
        f, Q = rows[args.row_index]
        tw = full_vertex_tw(n, M, cyc)
        eta = F(n * n, 25) - len(M)
        full_rhs = F(n) + eta
        full_lhs = sum((tw[v] for v in Q), F(0))
        full_margin = full_rhs - full_lhs

    print("=== fixed-row Slack-CAGE all-subset profiler ===")
    print("graph:", args.graph)
    print("n:", n)
    print("edges:", len(edges))
    print("maxcut_value:", maxcut_value)
    print("min_gamma_connected_maxcuts:", min_gamma)
    print("gamma_min_connected_sides:", len(sides))
    print("side:", side_strings[args.side_index])
    print("m:", len(M))
    print("rows:", len(rows))
    print("chosen_f:", f)
    print("chosen_Q:", Q)
    print("chosen_ell:", ell[f])
    print("full_lhs:", full_lhs)
    print("full_rhs:", full_rhs)
    print("full_margin:", full_margin)

    result = profile_fixed_row(n, M, cyc, B, Mset, Q)
    scale = result["scale"]
    print("scale:", scale)
    print("atoms_used:", result["atoms_used"])
    print("supermask_additions:", result["additions"])
    print_rec("min_all", result["best"], n, scale)
    print_rec("min_empty", result["empty"], n, scale)
    print_rec("min_full", result["full"], n, scale)
    print_rec("min_proper", result["proper"], n, scale)
    if result["counted"] is not None:
        print_rec("min_counted", result["counted"], n, scale)
    print("VERDICT:", "HOLDS" if result["best"][0] >= 0 else "FAILS")


if __name__ == "__main__":
    main()
