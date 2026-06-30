"""Gate the two-level terminal-shadow completion inequality.

For harmonic unit overload potentials phi, form nested threshold shadows

    A = {phi >= high},   B = {phi >= low},   A subset B.

For shadows with negative energy q = 1_A^T H 1_B < 0, brute-force all
completions W with A subset W subset B (when the annulus is small enough) and
search for a neutral, B-connected, terminal-shadow-safe completion with

    Psi(W) >= -q.

This is an exact diagnostic for Claude/GPT-Pro's two-level bridge.  It is not
intended as an efficient general solver yet.
"""

import argparse
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski
from _h import Bconn, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import solve_exact, submatrix
from _codex_double_coarea_gate import qform, indicator
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi


def harmonic_unit_phis(H, n, T):
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return []
    H_UU = submatrix(H, U, U)
    H_UO = submatrix(H, U, O)
    out = []
    for oi, o in enumerate(O):
        rhs = [-H_UO[i][oi] for i in range(len(U))]
        sol = solve_exact(H_UU, [rhs])
        if sol is None:
            continue
        phi = [F(0)] * n
        phi[o] = F(1)
        for ui, u in enumerate(U):
            phi[u] = sol[0][ui]
        out.append((O, o, phi))
    return out


def mask_from_vertices(vertices):
    mask = 0
    for v in vertices:
        mask |= 1 << v
    return mask


def negative_shadows(H, phi):
    vals = sorted({x for x in phi if x > 0})
    sets = []
    n = len(phi)
    for val in vals:
        verts = [i for i, x in enumerate(phi) if x >= val]
        sets.append((val, mask_from_vertices(verts), indicator(n, verts)))
    shadows = []
    for hi, high_mask, high_vec in sets:
        for lo, low_mask, low_vec in sets:
            if hi < lo:
                continue
            # high threshold gives the smaller A; low threshold gives larger B.
            if high_mask & ~low_mask:
                continue
            q = qform(H, high_vec, low_vec)
            if q < 0:
                shadows.append((hi, lo, high_mask, low_mask, q))
    return shadows


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def best_completion(n, adj, side, st, A, B, max_free):
    free = [i for i in range(n) if ((B >> i) & 1) and not ((A >> i) & 1)]
    if len(free) > max_free:
        return None, "too_large", len(free)
    best = None
    for sub in range(1 << len(free)):
        W = A
        for j, v in enumerate(free):
            if (sub >> j) & 1:
                W |= 1 << v
        if boundary_delta(n, adj, side, W) != 0:
            continue
        if not Bconn(n, adj, flip_side(side, W)):
            continue
        psi = terminal_shadow_psi(n, adj, side, st, W)
        if psi is None:
            continue
        cand = (psi, -W.bit_count(), W)
        if best is None or cand > best:
            best = cand
    if best is None:
        return None, "none", len(free)
    psi, _negsize, W = best
    return (psi, W, len(free)), "ok", len(free)


def scan_cut(name, n, adj, side, acc, max_free):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, cyc = st
    if not M:
        return
    H = build_H(n, M, ell, T, cyc, BETA)
    for O, o, phi in harmonic_unit_phis(H, n, T):
        acc["phis"] += 1
        for hi, lo, A, B, q in negative_shadows(H, phi):
            acc["neg_shadows"] += 1
            comp, status, free_size = best_completion(n, adj, side, st, A, B, max_free)
            if status == "too_large":
                acc["skipped_large"] += 1
                if acc["first_large"] is None:
                    acc["first_large"] = (name, n, "".join(map(str, side)), O, o, str(hi), str(lo), free_size)
                continue
            if comp is None:
                acc["fail"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        O,
                        o,
                        str(hi),
                        str(lo),
                        str(q),
                        "no completion",
                        mask_tuple(n, A),
                        mask_tuple(n, B),
                        free_size,
                    )
                continue
            psi, W, _free = comp
            if psi < -q:
                acc["fail"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        O,
                        o,
                        str(hi),
                        str(lo),
                        str(q),
                        str(psi),
                        mask_tuple(n, A),
                        mask_tuple(n, B),
                        mask_tuple(n, W),
                        free_size,
                    )
            else:
                acc["pass"] += 1
                margin = psi + q
                if acc["min_margin"] is None or margin < acc["min_margin"]:
                    acc["min_margin"] = margin
                    acc["min_margin_ex"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        O,
                        o,
                        str(hi),
                        str(lo),
                        str(q),
                        str(psi),
                        mask_tuple(n, W),
                        free_size,
                    )


def scan_allmax(name, n, edges, acc, max_free):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_free)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-free", type=int, default=18)
    args = parser.parse_args()

    acc = {
        "phis": 0,
        "neg_shadows": 0,
        "pass": 0,
        "fail": 0,
        "skipped_large": 0,
        "first_fail": None,
        "first_large": None,
        "min_margin": None,
        "min_margin_ex": None,
    }

    # H?AFBo] base and blowups.
    n, edges = dec("H?AFBo]")
    side = [int(c) for c in "111110000"]
    scan_cut("H?AFBo]", n, adj_from_edges(n, edges), side, acc, args.max_free)
    for t in (2, 3):
        nn, ee, ss = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, nn, adj_from_edges(nn, ee), ss, acc, args.max_free)

    # Mycielskian guardrail local-search cut.
    gr_n, gr_e = mycielski(5, Cn(5))
    m2_n, m2_e = mycielski(gr_n, gr_e)
    adj = adj_from_edges(m2_n, m2_e)
    side = maxcut_ls(m2_n, adj)
    scan_cut("MycGrotzsch_N23", m2_n, adj, side, acc, args.max_free)

    # Small all-max examples where previous selectors failed.
    for g6 in ("H?AFBo]", "I??CF@wFo"):
        nn, ee = dec(g6)
        scan_allmax(g6, nn, ee, acc, args.max_free)

    print("harmonic phis:", acc["phis"])
    print("negative shadows:", acc["neg_shadows"])
    print("pass:", acc["pass"])
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("skipped large:", acc["skipped_large"], acc["first_large"] or "")
    print("min margin:", acc["min_margin"], acc["min_margin_ex"] or "")
    verdict = acc["fail"] == 0
    print("VERDICT:", "TS bridge passes checked shadows" if verdict else "FAIL")


if __name__ == "__main__":
    main()
