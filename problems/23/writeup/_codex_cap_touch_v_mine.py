"""Mine path fractions p_f(v) for cap-touching rows.

Purpose: after complete-cap, surplus-touch is the remaining cap atom.  This
diagnostic checks whether cap-touching rows are exactly the rows whose shortest
geodesic bundles pass through the negative-residual vertex v, and records the
fractions p_f(v).
"""

import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _codex_minimalized_sidecap_gate import minimalize
from _codex_selected_minimality_gate import mask_of, vertices_of
from _codex_selected_interval_hall_gate import laminar_leaves


def pfv(cyc, f, v):
    paths = cyc[f]
    return F(sum(1 for p in paths if v in p), len(paths))


def scan_switch(name, n, adj, side, st, smask, v, acc, examples):
    M, ell, T, mu, cyc = st
    res = witness_structure(n, adj, side, st, set(vertices_of(smask, n)))
    if res is None:
        return
    crossM, bdyB, wit = res
    E = set(bdyB)
    if not crossM or not E:
        return
    exits = {f: set() for f in crossM}
    for f, e in wit:
        exits[f].add(e)
    miss_sets = [E - exits[f] for f in crossM]
    leaves = laminar_leaves(miss_sets) or []
    for cap in leaves:
        K = set(cap)
        touch = sorted(f for f in crossM if exits[f] & K)
        touch_p = tuple(sorted((ell[f], pfv(cyc, f, v)) for f in touch))
        n_zero = sum(1 for _l, p in touch_p if p == 0)
        n_one = sum(1 for _l, p in touch_p if p == 1)
        acc["caps"] += 1
        acc["touch_p_sig"][(len(K), len(touch), touch_p)] += 1
        acc["zero_count"][n_zero] += 1
        acc["one_count"][n_one] += 1
        acc["min_p"][min(p for _l, p in touch_p)] += 1
        if n_zero and len(examples["zero"]) < 5:
            examples["zero"].append((name, n, "".join(map(str, side)), v, vertices_of(smask, n), tuple(sorted(K)), touch_p))
        if len(examples["all"]) < 12:
            examples["all"].append((name, n, "".join(map(str, side)), v, tuple(sorted(K)), tuple(touch), touch_p))


def scan_graph(name, n, edges, acc, examples):
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v, rv in enumerate(R):
            if rv >= 0:
                continue
            got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if got is None:
                continue
            seed, moat, _drop = got
            smask0 = mask_of(set(seed) | set(moat))
            smask = minimalize(n, adj, side, st, gamma0, smask0, v)
            scan_switch(name, n, adj, side, st, smask, v, acc, examples)


def main():
    acc = {"caps": 0, "touch_p_sig": Counter(), "zero_count": Counter(), "one_count": Counter(), "min_p": Counter()}
    examples = {"zero": [], "all": []}
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            scan_graph("cen%d:%s" % (nn, g6), n, E, acc, examples)
    n, E = vertex_blowup(*dec("H?AFBo]"), 2)
    scan_graph("H2x", n, E, acc, examples)
    print("caps:", acc["caps"])
    print("zero_count:", sorted(acc["zero_count"].items()))
    print("one_count:", sorted(acc["one_count"].items()))
    print("min_p:", sorted((str(k), v) for k, v in acc["min_p"].items()))
    print("touch_p signatures top:")
    for sig, cnt in acc["touch_p_sig"].most_common(20):
        print(" ", sig, cnt)
    print("zero examples:", examples["zero"])
    print("examples:")
    for ex in examples["all"]:
        print(" ", ex)


if __name__ == "__main__":
    main()
