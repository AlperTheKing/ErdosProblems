"""Gate whether cap door-owner SDRs can avoid the seed-through-v rows.

The door-owner/encloser certificate says each cap K has:
  * an SDR K -> touch(K), and
  * at least one seed-through-v row in touch(K) as a genuine extra.

This diagnostic first tests the too-strong separation:
  K has an SDR into touch(K) \\ SeedV(K).

It also tests the actually relevant encloser form:
  there exists rho in touch(K) cap SeedV such that K has an SDR into
  touch(K) \\ {rho}.
"""

from collections import Counter

from _doorowner_gate import process, bipartite_match
from _doorowner_gate import dec, GENG, vertex_blowup
from _doorowner_gate import Bconn, maxcut_all, struct_for_side, build_K2
from _doorowner_gate import find_seedmoat, witness_structure, minimalize, mask_of, vertices_of, laminar_leaves
from fractions import Fraction as F
import subprocess


def gate_switch(name, n, adj, side, st, smask, acc, v):
    M, ell, T, mu, cyc = st
    res = witness_structure(n, adj, side, st, set(vertices_of(smask, n)))
    if res is None:
        acc["no_wit"] += 1
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
    if not leaves:
        acc["no_cap_switch"] += 1
        return
    seedrows = set()
    for f in crossM:
        verts = set()
        for p in cyc[f]:
            verts |= set(p)
        if v in verts:
            seedrows.add(f)
    acc["switches"] += 1
    for cap in leaves:
        K = set(cap)
        touch = [f for f in crossM if exits[f] & K]
        touch_seed = [f for f in touch if f in seedrows]
        touch_nonseed = [f for f in touch if f not in seedrows]
        adj_all = {e: [f for f in touch if e in exits[f]] for e in K}
        adj_nonseed = {e: [f for f in touch_nonseed if e in exits[f]] for e in K}
        m_all = bipartite_match(list(K), adj_all)
        m_nonseed = bipartite_match(list(K), adj_nonseed)
        excludable_seed = []
        for rho in touch_seed:
            adj_minus_rho = {e: [f for f in touch if f != rho and e in exits[f]] for e in K}
            if bipartite_match(list(K), adj_minus_rho) == len(K):
                excludable_seed.append(rho)
        acc["caps"] += 1
        acc["sig"][(len(K), len(touch), len(touch_seed), m_nonseed, len(excludable_seed))] += 1
        if m_all != len(K):
            acc["all_fail"] += 1
        if m_nonseed != len(K):
            acc["avoid_fail"] += 1
        if not excludable_seed:
            acc["no_excludable_seed"] += 1
            if acc["first"] is None:
                acc["first"] = {
                    "name": name,
                    "n": n,
                    "side": "".join(map(str, side)),
                    "v": v,
                    "S": vertices_of(smask, n),
                    "K": tuple(sorted(K)),
                    "touch": tuple(sorted(touch)),
                    "touch_seed": tuple(sorted(touch_seed)),
                    "touch_lens": tuple(sorted(ell[f] for f in touch)),
                    "m_nonseed": m_nonseed,
                    "adj_nonseed": {e: tuple(sorted(adj_nonseed[e])) for e in sorted(K)},
                }


def process2(name, n, edges, acc, max_add=1):
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
            got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=max_add)
            if got is None:
                continue
            seed, moat, _drop = got
            smask0 = mask_of(set(seed) | set(moat))
            smask = minimalize(n, adj, side, st, gamma0, smask0, v)
            gate_switch(name, n, adj, side, st, smask, acc, v)


def main():
    acc = {
        "switches": 0,
        "caps": 0,
        "no_wit": 0,
        "no_cap_switch": 0,
        "all_fail": 0,
        "avoid_fail": 0,
        "no_excludable_seed": 0,
        "sig": Counter(),
        "first": None,
    }
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            process2("cen%d" % nn, n, E, acc)
    n, E = vertex_blowup(*dec("H?AFBo]"), 2)
    process2("H2x", n, E, acc)
    print("switches:", acc["switches"], "caps:", acc["caps"])
    print("all_fail:", acc["all_fail"], "avoid_all_seed_fail:", acc["avoid_fail"], "no_excludable_seed:", acc["no_excludable_seed"])
    print("signatures:", sorted(acc["sig"].items()))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["no_excludable_seed"] == 0 and acc["caps"] else "FAIL")


if __name__ == "__main__":
    main()
