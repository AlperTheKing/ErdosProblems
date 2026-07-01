"""Check the exact identity behind dirty-cap-defect accounting.

Claude's `_dcd_gate.py` tests the sufficient inequality

    DCD := missing_allowed + M_leak - B_leak >= 1.

This diagnostic verifies the algebraic correction:

    |N(K)| - |K| = DCD + (|delta_B(U_K)| - |delta_M(U_K)|)

on the selected minimalized cap battery.  Thus negative DCD can be paid by
ordinary max-cut slack of the prefix-union `U_K`.
"""

from collections import Counter
from fractions import Fraction as F
import subprocess

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure, deltas_of
from _codex_minimalized_sidecap_gate import minimalize
from _codex_selected_minimality_gate import mask_of
from _codex_selected_interval_hall_gate import laminar_leaves


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    return adj


def vertices(mask, n):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def inspect_switch(name, n, adj, side, st, smask, acc):
    res = witness_structure(n, adj, side, st, set(vertices(smask, n)))
    if res is None:
        acc["no_wit"] += 1
        return
    crossM, bdyB, wit = res
    C = set(crossM)
    E = set(bdyB)
    exits = {f: set() for f in crossM}
    pref = {}
    for (f, e), pv in wit.items():
        exits[f].add(e)
        pref[(f, e)] = pv
    leaves = laminar_leaves([set(E) - exits[f] for f in crossM]) or []
    if not leaves:
        acc["no_cap_switch"] += 1
        return
    acc["switches"] += 1
    for cap in leaves:
        K = set(cap)
        NK = {f for f in crossM if exits[f] & K}
        FK = {f for f in crossM if not (exits[f] & K)}
        U = set()
        for f in FK:
            for e in exits[f]:
                U |= pref[(f, e)]
        dB, dM = deltas_of(n, adj, side, U)
        EK = E - K
        B_good = dB & EK
        B_leak = dB - EK
        M_leak = dM - FK
        missing = EK - B_good
        dcd = len(missing) + len(M_leak) - len(B_leak)
        slack = len(dB) - len(dM)
        gap = len(NK) - len(K)
        acc["caps"] += 1
        acc["dcd"][dcd] += 1
        acc["slack"][slack] += 1
        acc["gap"][gap] += 1
        acc["pair"][(dcd, slack, gap)] += 1
        if FK - dM:
            acc["fk_not_boundary"] += 1
            if acc["first"] is None:
                acc["first"] = ("fk_not_boundary", name, "".join(map(str, side)), tuple(sorted(K)), tuple(sorted(FK - dM)))
        if gap != dcd + slack:
            acc["identity_fail"] += 1
            if acc["first"] is None:
                acc["first"] = ("identity_fail", name, "".join(map(str, side)), tuple(sorted(K)), gap, dcd, slack)


def scan_graph(name, n, edges, acc, max_add=1):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v, rv in enumerate(R):
            if rv >= 0:
                continue
            got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=max_add)
            if got is None:
                acc["no_seedmoat"] += 1
                continue
            seed, moat, _drop = got
            smask0 = mask_of(set(seed) | set(moat))
            smask = minimalize(n, adj, side, st, gamma0, smask0, v)
            inspect_switch(name, n, adj, side, st, smask, acc)


def main():
    acc = Counter()
    acc["dcd"] = Counter()
    acc["slack"] = Counter()
    acc["gap"] = Counter()
    acc["pair"] = Counter()
    acc["first"] = None
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph("cen%d:%s" % (nn, g6), n, edges, acc)
    n, edges = vertex_blowup(*dec("H?AFBo]"), 2)
    scan_graph("H?AFBo]x2", n, edges, acc)

    print("switches:", acc["switches"], "caps:", acc["caps"], "no_cap_switch:", acc["no_cap_switch"])
    print("identity_fail:", acc["identity_fail"], "fk_not_boundary:", acc["fk_not_boundary"], "first:", acc["first"] or "")
    print("dcd:", sorted(acc["dcd"].items()))
    print("slack:", sorted(acc["slack"].items()))
    print("gap:", sorted(acc["gap"].items()))
    print("triples:")
    for triple, count in sorted(acc["pair"].items()):
        print(" ", triple, count)
    print("VERDICT:", "PASS" if acc["identity_fail"] == 0 and acc["fk_not_boundary"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
