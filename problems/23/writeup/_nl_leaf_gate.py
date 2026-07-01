"""Exact regression gate for the NL (no-naked-leaf) fan-branch atom.

This is deliberately downstream of `_rfc_gate.py`.

For each blue-closed prefix hull `(S, X, U)` it enumerates reduced deficient
extra-door sets `Z`.  For such a `Z`, it chooses one clean initial `U`-segment
of a shortest row for every door incidence `(g,e)`, builds the resulting fan
graph, and checks the exact leaf-branch tuple suggested by Claude:

  component K, row g, doors e0/e1, split vertex s, branch door set Z0,
  and a trapped row g' with empty != D(g') cap Z subset Z0.

If no reduced deficient `Z` exists, NL is vacuous on that battery instance.
That is the current hard-H3 situation; this script makes the leaf-branch
definition executable for future falsifiers instead of leaving it prose-only.
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
from _rfc_gate import blue_closure_in_S, delta_B_M, edge


def chosen_initial_paths(cyc, Uset, g, Bplus):
    """Map each extra door to one deterministic clean initial U-segment."""
    a, b = g
    if a in Uset and b not in Uset:
        a_g = a
    elif b in Uset and a not in Uset:
        a_g = b
    else:
        return {}

    out = {}
    for Q0 in cyc.get(g, []):
        Q = list(Q0)
        if Q[0] != a_g:
            Q = Q[::-1]
        if Q[0] != a_g:
            continue
        inU = [x in Uset for x in Q]
        if not inU[0]:
            continue
        r = 0
        while r + 1 < len(inU) and inU[r + 1]:
            r += 1
        if r + 1 >= len(Q):
            continue
        if any(inU[j] for j in range(r + 1, len(inU))):
            continue
        e = edge(Q[r], Q[r + 1])
        if e in Bplus:
            out.setdefault(e, set()).add(tuple(Q[: r + 1]))
    return {e: sorted(paths)[0] for e, paths in out.items()}


def graph_components(vertices, edges, banned=None, removed_edges=None):
    banned = set() if banned is None else set(banned)
    removed_edges = set() if removed_edges is None else set(removed_edges)
    vertices = set(vertices) - banned
    adj = {v: set() for v in vertices}
    for u, v in edges:
        if edge(u, v) in removed_edges:
            continue
        if u in vertices and v in vertices:
            adj[u].add(v)
            adj[v].add(u)
    comps = []
    seen = set()
    for v in sorted(vertices):
        if v in seen:
            continue
        stack = [v]
        seen.add(v)
        comp = set()
        while stack:
            x = stack.pop()
            comp.add(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(comp)
    return comps


def inner_endpoint(e, Uset):
    a, b = e
    if a in Uset and b not in Uset:
        return a
    if b in Uset and a not in Uset:
        return b
    return None


def longest_common_prefix_vertex(P0, P1):
    last = None
    for a, b in itertools.zip_longest(P0, P1, fillvalue=None):
        if a != b:
            break
        last = a
    return last


def reduced_deficient_sets(Bplus, door_paths, max_z):
    Bplus = list(Bplus)
    if len(Bplus) > max_z:
        return "TOOBIG"
    Ne = {e: set() for e in Bplus}
    door = {g: set(paths) for g, paths in door_paths.items()}
    for g, ds in door.items():
        for e in ds:
            if e in Ne:
                Ne[e].add(g)

    out = []
    for r in range(1, len(Bplus) + 1):
        for combo in itertools.combinations(Bplus, r):
            Z = set(combo)
            H = set()
            for e in Z:
                H |= Ne[e]
            if len(H) >= len(Z):
                continue
            if all(len(door[g] & Z) >= 2 for g in H):
                out.append((Z, H))
    return out


def nl_leaf_falsifier(Uset, Bplus, door_paths, Z, H):
    """Return a tuple witnessing failure of the executable NL branch check."""
    fan_vertices = set()
    fan_edges = set()
    door_inner = {}

    for g in H:
        for e in set(door_paths[g]) & Z:
            door_inner[e] = inner_endpoint(e, Uset)
            P = door_paths[g][e]
            fan_vertices.update(P)
            for i in range(len(P) - 1):
                fan_edges.add(edge(P[i], P[i + 1]))

    comps = graph_components(fan_vertices, fan_edges)
    for comp in comps:
        ZK = {e for e in Z if door_inner.get(e) in comp}
        if not ZK:
            continue
        HK = {g for g in H if (set(door_paths[g]) & ZK)}
        if len(ZK) <= len(HK):
            continue

        for g in sorted(HK):
            gdoors = sorted(set(door_paths[g]) & ZK)
            for e0, e1 in itertools.permutations(gdoors, 2):
                P0 = door_paths[g][e0]
                P1 = door_paths[g][e1]
                s = longest_common_prefix_vertex(P0, P1)
                if s is None or s == P0[-1] or s == P1[-1]:
                    continue
                i1 = P1.index(s)
                sibling_edges = {
                    edge(P1[i], P1[i + 1])
                    for i in range(i1, len(P1) - 1)
                }
                branch_comps = graph_components(
                    comp, fan_edges, banned={s}, removed_edges=sibling_edges
                )
                x0 = door_inner.get(e0)
                branch = next((c for c in branch_comps if x0 in c), set())
                if not branch:
                    continue
                Z0 = {e for e in ZK if door_inner.get(e) in branch}
                if not Z0 or e1 in Z0 or Z0 == ZK:
                    continue
                trapped = []
                for gp in HK - {g}:
                    dz = set(door_paths[gp]) & Z
                    if dz and dz <= Z0:
                        trapped.append(gp)
                if not trapped:
                    return {
                        "K_doors": sorted(ZK),
                        "K_rows": sorted(HK),
                        "g": g,
                        "e0": e0,
                        "e1": e1,
                        "split": s,
                        "removed_sibling_edges": sorted(sibling_edges),
                        "Z0": sorted(Z0),
                    }
    return None


def test_switch(name, n, adj, side, st, Sset, acc, max_cross=9, max_z=16):
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, _bdyB, wit = res
    if not crossM:
        return
    M, ell, T, mu, cyc = st
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
            door_paths = {
                g: chosen_initial_paths(cyc, U, g, Bplus)
                for g in Mplus
            }
            rd = reduced_deficient_sets(Bplus, door_paths, max_z=max_z)
            acc["XU"] += 1
            if rd == "TOOBIG":
                acc["XU_toobig"] += 1
                continue
            if not rd:
                continue
            acc["reduced_def"] += len(rd)
            for Z, H in rd:
                bad = nl_leaf_falsifier(U, Bplus, door_paths, Z, H)
                acc["leaf_checks"] += 1
                if bad is not None:
                    acc["nl_fail"] += 1
                    if acc["ex"] is None:
                        acc["ex"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "X": sorted(X),
                            "Z": sorted(Z),
                            "H": sorted(H),
                            "bad": bad,
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
    parser.add_argument("--max-cross", type=int, default=9)
    parser.add_argument("--max-z", type=int, default=16)
    parser.add_argument("--h3-hard", action="store_true")
    args = parser.parse_args()

    acc = dict(
        switches=0,
        XU=0,
        XU_toobig=0,
        toobig=0,
        reduced_def=0,
        leaf_checks=0,
        nl_fail=0,
        ex=None,
    )
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            process("cen%d" % nn, n, E, acc, max_cross=args.max_cross, max_z=args.max_z)
        print("census N=%d: switches=%d XU=%d reduced=%d nl_fail=%d" %
              (nn, acc["switches"], acc["XU"], acc["reduced_def"], acc["nl_fail"]), flush=True)

    hN, hE = dec("H?AFBo]")
    nn, EE = vertex_blowup(hN, hE, 2)
    process("Hblow2", nn, EE, acc, max_cross=args.max_cross, max_z=args.max_z)
    print("after Hblow2: switches=%d XU=%d reduced=%d nl_fail=%d" %
          (acc["switches"], acc["XU"], acc["reduced_def"], acc["nl_fail"]), flush=True)

    if args.h3_hard:
        process_h3_hard(acc, args.max_cross, args.max_z)
        print("after H3-hard: switches=%d XU=%d reduced=%d leaf_checks=%d nl_fail=%d" %
              (acc["switches"], acc["XU"], acc["reduced_def"], acc["leaf_checks"], acc["nl_fail"]), flush=True)

    print("=" * 60)
    print("switches:", acc["switches"], "XU:", acc["XU"],
          "too-big switches:", acc["toobig"], "too-big Z:", acc["XU_toobig"])
    print("reduced deficient cores:", acc["reduced_def"],
          "leaf checks:", acc["leaf_checks"], "NL failures:", acc["nl_fail"])
    print("example:", acc["ex"] or "")
    if acc["nl_fail"] == 0:
        print("VERDICT: no executable NL leaf-branch falsifier on this battery")
    else:
        print("VERDICT: NL leaf-branch check failed; inspect example")


if __name__ == "__main__":
    main()
