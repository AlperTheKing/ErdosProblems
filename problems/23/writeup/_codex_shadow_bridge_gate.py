"""Exact pilot gate for the terminal-shadow bridge inequality.

For harmonic overload unit potentials phi, form nested threshold masks

    A_a = {v : phi[v] >= t_a},    B_b = {v : phi[v] >= t_b}, b <= a.

For each negative shadow energy 1_A^T H 1_B < 0, exhaustively search
completions W with A subset W subset B.  The pilot bridge target is

    max Psi(W) >= -1_A^T H 1_B

among completions that are cut-neutral, keep B connected after the flip,
and pass the terminal-shadow Psi verifier.

This is a finite gate, not a proof: large annuli are skipped unless the
--max-free threshold is raised.
"""

import argparse
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski
from _h import Bconn, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import submatrix, solve_exact
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi


def qform(H, x, y):
    n = len(H)
    return sum(x[i] * H[i][j] * y[j] for i in range(n) for j in range(n))


def indicator(n, mask):
    return [F((mask >> i) & 1) for i in range(n)]


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def masks_from_phi(phi):
    vals = sorted({x for x in phi if x > 0})
    masks = []
    for val in vals:
        mask = 0
        for i, x in enumerate(phi):
            if x >= val:
                mask |= 1 << i
        masks.append((val, mask))
    return masks


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


def iter_submasks(mask):
    sub = mask
    while True:
        yield sub
        if sub == 0:
            break
        sub = (sub - 1) & mask


def best_completion(n, adj, side, st, a_mask, b_mask, max_free):
    free = b_mask & ~a_mask
    free_bits = free.bit_count()
    if free_bits > max_free:
        return None, free_bits, "skip"

    best = None
    for sub in iter_submasks(free):
        mask = a_mask | sub
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        if not Bconn(n, adj, flip_side(side, mask)):
            continue
        psi = terminal_shadow_psi(n, adj, side, st, mask)
        if psi is None:
            continue
        cand = (psi, -mask.bit_count(), mask)
        if best is None or cand > best:
            best = cand
    return best, free_bits, "ok"


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
        masks = masks_from_phi(phi)
        for a, (ta, a_mask) in enumerate(masks):
            avec = indicator(n, a_mask)
            for b in range(a + 1):
                tb, b_mask = masks[b]
                e = qform(H, avec, indicator(n, b_mask))
                acc["pairs"] += 1
                if e >= 0:
                    continue
                acc["negative_pairs"] += 1
                best, free_bits, status = best_completion(n, adj, side, st, a_mask, b_mask, max_free)
                if status == "skip":
                    acc["skipped"] += 1
                    if acc["first_skip"] is None:
                        acc["first_skip"] = (name, n, "".join(map(str, side)), O, o, str(ta), str(tb), free_bits, str(e))
                    continue
                if best is None:
                    acc["fail"] += 1
                    if acc["first_fail"] is None:
                        acc["first_fail"] = (
                            name,
                            n,
                            "".join(map(str, side)),
                            O,
                            o,
                            str(ta),
                            str(tb),
                            str(e),
                            "no completion",
                        )
                    continue
                psi, _neg_size, mask = best
                margin = F(psi) + e
                acc["tested"] += 1
                if acc["min_margin"] is None or margin < acc["min_margin"][0]:
                    acc["min_margin"] = (
                        margin,
                        name,
                        n,
                        "".join(map(str, side)),
                        O,
                        o,
                        str(ta),
                        str(tb),
                        free_bits,
                        psi,
                        mask_tuple(n, mask),
                        str(e),
                    )
                if margin < 0:
                    acc["fail"] += 1
                    if acc["first_fail"] is None:
                        acc["first_fail"] = (
                            name,
                            n,
                            "".join(map(str, side)),
                            O,
                            o,
                            str(ta),
                            str(tb),
                            str(e),
                            psi,
                            mask_tuple(n, mask),
                            str(margin),
                        )


def scan_graph_allmax(name, n, edges, acc, max_free):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_free)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-free", type=int, default=20)
    parser.add_argument("--census", action="store_true")
    args = parser.parse_args()

    acc = dict(
        pairs=0,
        negative_pairs=0,
        tested=0,
        skipped=0,
        first_skip=None,
        fail=0,
        first_fail=None,
        min_margin=None,
    )

    n, edges = dec("H?AFBo]")
    scan_cut("H?AFBo]", n, adj_from_edges(n, edges), [int(c) for c in "111110000"], acc, args.max_free)
    for t in (2, 3):
        nn, ee, ss = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, nn, adj_from_edges(nn, ee), ss, acc, args.max_free)

    gr_n, gr_e = mycielski(5, Cn(5))
    m2_n, m2_e = mycielski(gr_n, gr_e)
    adj = adj_from_edges(m2_n, m2_e)
    scan_cut("MycGrotzsch_N23", m2_n, adj, maxcut_ls(m2_n, adj), acc, args.max_free)

    if args.census:
        for g6 in ["H?AFBo]", "I??CF@wFo"]:
            nn, ee = dec(g6)
            scan_graph_allmax(g6, nn, ee, acc, args.max_free)

    print("pairs:", acc["pairs"])
    print("negative pairs:", acc["negative_pairs"])
    print("tested:", acc["tested"])
    print("skipped:", acc["skipped"], acc["first_skip"] or "")
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("min margin:", acc["min_margin"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
