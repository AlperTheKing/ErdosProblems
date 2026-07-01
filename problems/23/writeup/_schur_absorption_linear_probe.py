"""Probe stronger affine Schur row-sum bounds.

The absorption-Hall gate only asks rho(X) >= 0 when a(X) <= A-a(X).
This diagnostic tests the stronger candidate

    rho(X) >= A - 2 a(X)

for the same non-majority subsets.
"""

from itertools import combinations

from _schur_absorption_margin_probe import consider as _unused_consider
from _schur_absorption_margin_probe import adj_from_edges, gfam
from _schur_absorption_hall_gate import schur_on_O
from _bdef_construct import Cn, mycielski
from _h import Bconn
from _hardy_gate import BETA, build_H, maxcut_ls
from _satzmu_conn import struct_for_side


def test_one(name, n, adj, side):
    if not Bconn(n, adj, side):
        return []
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return []
    N = n
    O = [v for v in range(n) if T[v] > N]
    if not O:
        return []
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    if S is None:
        return []
    a = [T[o] - N for o in O]
    rho = [sum(S[i]) for i in range(len(O))]
    A = sum(a)
    out = []
    for r in range(1, len(O) + 1):
        for X in combinations(range(len(O)), r):
            ax = sum(a[i] for i in X)
            if ax > A - ax:
                continue
            rhox = sum(rho[i] for i in X)
            margin = rhox - (A - 2 * ax)
            out.append((margin, name, n, "".join(map(str, side)), tuple(O[i] for i in X), str(ax), str(A), [str(x) for x in a], [str(x) for x in rho]))
    return out


def main():
    # The known nontrivial guardrail is the fastest informative target.
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = adj_from_edges(m2N, m2E)
    side = maxcut_ls(m2N, adj)
    rows = test_one("MycGrotzsch_N23", m2N, adj, side)
    rows.sort(key=lambda z: z[0])
    print("MycGrotzsch_N23 affine margins")
    for rec in rows[:12]:
        print(rec)


if __name__ == "__main__":
    main()
