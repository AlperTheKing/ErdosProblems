"""Exact gate for the two-level nested-threshold coarea identity.

For a symmetric matrix H and a vector 0 <= phi <= 1, let levels be the
distinct positive values of phi.  Put

    A_t = {v : phi[v] >= t},    B_s = {v : phi[v] > s}.

The exact finite nested form is

    phi^T H phi
      = 2 * sum_{b<a} d_b d_a  1_{A_a}^T H 1_{B_b}
        + sum_a d_a^2          1_{A_a}^T H 1_{B_a},

where d_a = level[a]-level[a-1] and the representative threshold for each
interval is its upper endpoint.  This is just the square integral split over
the triangle s <= t; all sets are nested.

This script gates the identity on harmonic overload unit potentials
phi_O=e_o, phi_U=-H_UU^{-1}H_UO e_o for selected cuts.
"""

from fractions import Fraction as F

from _h import Bconn, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import solve_exact, submatrix
from _bdef_construct import Cn, mycielski
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges


def qform(H, x, y=None):
    if y is None:
        y = x
    n = len(H)
    return sum(x[i] * H[i][j] * y[j] for i in range(n) for j in range(n))


def indicator(n, vertices):
    s = set(vertices)
    return [F(1) if i in s else F(0) for i in range(n)]


def double_coarea_value(H, phi):
    vals = sorted({x for x in phi if x > 0})
    prev = F(0)
    layers = []
    n = len(phi)
    for val in vals:
        d = val - prev
        verts = [i for i, x in enumerate(phi) if x >= val]
        layers.append((d, indicator(n, verts)))
        prev = val

    total = F(0)
    for a, (da, Aa) in enumerate(layers):
        total += da * da * qform(H, Aa)
        for b in range(a):
            db, Bb = layers[b]
            total += 2 * da * db * qform(H, Aa, Bb)
    return total


def harmonic_unit_phis(H, n, T):
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return []
    H_UU = submatrix(H, U, U)
    H_UO = submatrix(H, U, O)
    phis = []
    for oi, o in enumerate(O):
        rhs = [-H_UO[i][oi] for i in range(len(U))]
        sol = solve_exact(H_UU, [rhs])
        if sol is None:
            continue
        phi = [F(0)] * n
        phi[o] = F(1)
        for ui, u in enumerate(U):
            phi[u] = sol[0][ui]
        phis.append((O, o, phi))
    return phis


def scan_cut(name, n, adj, side, acc):
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
        left = qform(H, phi)
        right = double_coarea_value(H, phi)
        if left != right:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), O, o, str(left), str(right))
        if min(phi) < 0 or max(phi) > 1:
            acc["range_fail"] += 1
            if acc["first_range_fail"] is None:
                acc["first_range_fail"] = (
                    name,
                    n,
                    "".join(map(str, side)),
                    O,
                    o,
                    str(min(phi)),
                    str(max(phi)),
                )


def scan_graph_allmax(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def main():
    acc = dict(phis=0, fail=0, first_fail=None, range_fail=0, first_range_fail=None)

    # Base H?AFBo] and blowups, where switch witnesses live.
    n, edges = dec("H?AFBo]")
    side = [int(c) for c in "111110000"]
    scan_cut("H?AFBo]", n, adj_from_edges(n, edges), side, acc)
    for t in (2, 3):
        nn, ee, ss = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, nn, adj_from_edges(nn, ee), ss, acc)

    # Mycielskian guardrail local-search max cut.
    gr_n, gr_e = mycielski(5, Cn(5))
    m2_n, m2_e = mycielski(gr_n, gr_e)
    adj = adj_from_edges(m2_n, m2_e)
    side = maxcut_ls(m2_n, adj)
    scan_cut("MycGrotzsch_N23", m2_n, adj, side, acc)

    # Small all-max census spot check.
    for g6 in ["H?AFBo]", "I??CF@wFo"]:
        nn, ee = dec(g6)
        scan_graph_allmax(g6, nn, ee, acc)

    print("harmonic unit phis:", acc["phis"])
    print("double-coarea failures:", acc["fail"], acc["first_fail"] or "")
    print("range failures:", acc["range_fail"], acc["first_range_fail"] or "")
    verdict = acc["fail"] == 0
    print("VERDICT:", "double-coarea identity holds exactly" if verdict else "FAIL")


if __name__ == "__main__":
    main()
