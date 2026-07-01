r"""Probe a stronger componentwise matching form of CRFE.

The current live CRFE target is the cardinal statement

    |H_K| >= |Z_K|

for every reduced set Z and every chosen fan component K.  This script tests
the stronger SDR statement: the bipartite incidence graph

    e in Z_K  --  g in H_K     iff     e in D_U(g)

has a matching saturating Z_K.

If this holds on the same battery as _nl_leaf_broad_probe.py, the proof
target can be sharpened from cardinal expansion to an explicit componentwise
door-to-row injection.  If it fails, the printed witness is the next geometry
to understand.
"""

import argparse
import itertools
import subprocess

from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _rfc_gate import blue_closure_in_S, delta_B_M
from _nl_leaf_gate import chosen_initial_paths, graph_components, inner_endpoint
from _nl_leaf_broad_probe import all_reduced_sets


def component_records(Uset, door_paths, Z, H):
    fan_vertices = set()
    fan_edges = set()
    door_inner = {}

    for g in H:
        for e in set(door_paths[g]) & Z:
            door_inner[e] = inner_endpoint(e, Uset)
            P = door_paths[g][e]
            fan_vertices.update(P)
            for i in range(len(P) - 1):
                u, v = P[i], P[i + 1]
                fan_edges.add((u, v) if u < v else (v, u))

    records = []
    for comp in graph_components(fan_vertices, fan_edges):
        ZK = {e for e in Z if door_inner.get(e) in comp}
        if not ZK:
            continue
        HK = {g for g in H if (set(door_paths[g]) & ZK)}
        records.append((comp, ZK, HK))
    return records


def hall_failure(ZK, HK, door_paths):
    zlist = sorted(ZK)
    hlist = sorted(HK)
    h_index = {g: i for i, g in enumerate(hlist)}
    neigh = []
    for e in zlist:
        mask = 0
        for g in hlist:
            if e in door_paths[g]:
                mask |= 1 << h_index[g]
        neigh.append(mask)

    for smask in range(1, 1 << len(zlist)):
        nmask = 0
        for i, nm in enumerate(neigh):
            if (smask >> i) & 1:
                nmask |= nm
        if nmask.bit_count() < smask.bit_count():
            badZ = [zlist[i] for i in range(len(zlist)) if (smask >> i) & 1]
            badH = [hlist[i] for i in range(len(hlist)) if (nmask >> i) & 1]
            return badZ, badH
    return None


def test_switch(name, n, adj, side, st, Sset, acc, max_cross=9, max_z=16):
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, _bdyB, wit = res
    if not crossM:
        return
    _M, _ell, _T, _mu, cyc = st
    WitS = {f: set() for f in crossM}
    PrefS = {}
    for (f, e), pref in wit.items():
        WitS[f].add(e)
        PrefS[(f, e)] = pref

    acc["switches"] += 1
    Cl = list(crossM)
    if len(Cl) > max_cross:
        acc["toobig"] += 1
        return

    for rX in range(1, len(Cl) + 1):
        for X0 in itertools.combinations(Cl, rX):
            X = set(X0)
            Y = set()
            U0 = set()
            for f in X:
                Y |= WitS[f]
                for e in WitS[f]:
                    U0 |= PrefS[(f, e)]
            U = blue_closure_in_S(n, adj, side, Sset, U0)
            dB, dM = delta_B_M(n, adj, side, U)
            Bplus = dB - Y
            Mplus = dM - X
            if not Bplus:
                continue

            door_paths = {g: chosen_initial_paths(cyc, U, g, Bplus) for g in Mplus}
            rz = all_reduced_sets(Bplus, door_paths, max_z=max_z)
            acc["XU"] += 1
            if rz == "TOOBIG":
                acc["XU_toobig"] += 1
                continue

            for Z, H in rz:
                acc["reduced"] += 1
                for comp, ZK, HK in component_records(U, door_paths, Z, H):
                    acc["components"] += 1
                    margin = len(HK) - len(ZK)
                    acc["min_margin"] = min(acc["min_margin"], margin)
                    bad = hall_failure(ZK, HK, door_paths)
                    if bad is not None:
                        acc["matching_fail"] += 1
                        if acc["ex"] is None:
                            badZ, badH = bad
                            acc["ex"] = {
                                "name": name,
                                "n": n,
                                "side": "".join(map(str, side)),
                                "X": sorted(X),
                                "Z": sorted(Z),
                                "H": sorted(H),
                                "ZK": sorted(ZK),
                                "HK": sorted(HK),
                                "component": sorted(comp),
                                "badZ": badZ,
                                "badH": badH,
                                "margin": margin,
                            }
                        return


def process(name, n, E, acc, max_cross=9, max_z=16):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y)
        adj[y].add(x)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        if not M:
            continue
        N = F(n)
        K2 = build_K2(n, M, cyc)
        R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v in range(n):
            if R[v] >= 0:
                continue
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                continue
            A, moat, _drop = sm
            test_switch(name, n, adj, side, st, set(A) | set(moat), acc,
                        max_cross=max_cross, max_z=max_z)


def process_h3_hard(acc, max_cross, max_z):
    from _codex_length_tier_matching_gate import h_blowup
    from _codex_k2t_switch_probe import adj_from_edges

    n, edges, _side = h_blowup(3)
    adj = adj_from_edges(n, edges)
    side = [int(c) for c in "111111111111111100000000000"]
    st = struct_for_side(n, adj, side)
    Sset = {
        3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
        13, 14, 15, 18, 21, 22, 23, 24, 25, 26,
    }
    test_switch("H3-hard", n, adj, side, st, Sset, acc,
                max_cross=max_cross, max_z=max_z)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-cross", type=int, default=9)
    parser.add_argument("--max-z", type=int, default=16)
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--h3-hard", action="store_true")
    args = parser.parse_args()

    acc = dict(
        switches=0,
        XU=0,
        XU_toobig=0,
        toobig=0,
        reduced=0,
        components=0,
        min_margin=10**9,
        matching_fail=0,
        ex=None,
    )

    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            process("cen%d" % nn, n, E, acc,
                    max_cross=args.max_cross, max_z=args.max_z)
        print("census N=%d: switches=%d XU=%d reduced=%d components=%d fail=%d" %
              (nn, acc["switches"], acc["XU"], acc["reduced"], acc["components"], acc["matching_fail"]),
              flush=True)

    hN, hE = dec("H?AFBo]")
    nn, EE = vertex_blowup(hN, hE, 2)
    process("Hblow2", nn, EE, acc, max_cross=args.max_cross, max_z=args.max_z)
    print("after Hblow2: switches=%d XU=%d reduced=%d components=%d fail=%d" %
          (acc["switches"], acc["XU"], acc["reduced"], acc["components"], acc["matching_fail"]),
          flush=True)

    if args.h_inherited:
        from _codex_length_tier_matching_gate import h_blowup
        from _codex_k2t_switch_probe import adj_from_edges

        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            adj = adj_from_edges(n, edges)
            st = struct_for_side(n, adj, side)
            if st is not None:
                M, ell, T, cyc = st[0], st[1], st[2], st[4]
                if M:
                    N = F(n)
                    K2 = build_K2(n, M, cyc)
                    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
                    gamma0 = sum(ell[f] ** 2 for f in M)
                    for v in range(n):
                        if R[v] >= 0:
                            continue
                        sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
                        if sm is None:
                            continue
                        A, moat, _drop = sm
                        test_switch("H%d-inherited" % t, n, adj, side, st, set(A) | set(moat), acc,
                                    max_cross=args.max_cross, max_z=args.max_z)
            print("after H%d-inherited: switches=%d XU=%d reduced=%d components=%d fail=%d" %
                  (t, acc["switches"], acc["XU"], acc["reduced"], acc["components"], acc["matching_fail"]),
                  flush=True)

    if args.h3_hard:
        process_h3_hard(acc, args.max_cross, args.max_z)
        print("after H3-hard: switches=%d XU=%d reduced=%d components=%d fail=%d" %
              (acc["switches"], acc["XU"], acc["reduced"], acc["components"], acc["matching_fail"]),
              flush=True)

    print("=" * 72)
    print("switches:", acc["switches"], "XU:", acc["XU"],
          "too-big switches:", acc["toobig"], "too-big Z:", acc["XU_toobig"])
    print("all reduced Z:", acc["reduced"],
          "fan components:", acc["components"],
          "min |H_K|-|Z_K|:", acc["min_margin"] if acc["components"] else "NA",
          "component matching failures:", acc["matching_fail"])
    print("example:", acc["ex"] or "")
    if acc["matching_fail"] == 0:
        print("VERDICT: componentwise door-row matching found no falsifier")
    else:
        print("VERDICT: componentwise door-row matching failed")


if __name__ == "__main__":
    main()
