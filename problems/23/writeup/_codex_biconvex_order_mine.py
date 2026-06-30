"""Mine consecutive exit orders for selected completed seed+moat switches."""

import itertools
import subprocess
from fractions import Fraction as F

from _h import GENG, Bconn, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _codex_k2t_switch_probe import adj_from_edges


def first_order(items, sets):
    items = tuple(items)
    for perm in itertools.permutations(items):
        pos = {x: i for i, x in enumerate(perm)}
        ok = True
        for s in sets:
            if not s:
                continue
            idx = sorted(pos[x] for x in s)
            if idx[-1] - idx[0] + 1 != len(idx):
                ok = False
                break
        if ok:
            return perm
    return None


def edge_parts(edge, smask):
    a, b = edge
    ain = (smask >> a) & 1
    bin_ = (smask >> b) & 1
    if ain and not bin_:
        return a, b
    if bin_ and not ain:
        return b, a
    return None, None


def process(name, n, edges, limit):
    adj = adj_from_edges(n, edges)
    out = []
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
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                continue
            seed, moat, drop = sm
            smask = 0
            for x in set(seed) | set(moat):
                smask |= 1 << x
            res = witness_structure(n, adj, side, st, set(seed) | set(moat))
            if res is None:
                continue
            crossM, bdyB, wit = res
            by_f = {f: set() for f in crossM}
            by_e = {e: set() for e in bdyB}
            for f, e in wit:
                by_f[f].add(e)
                by_e[e].add(f)
            eorder = first_order(bdyB, list(by_f.values()))
            forder = first_order(crossM, list(by_e.values()))
            if eorder is None or forder is None:
                continue
            out.append(
                dict(
                    graph=name,
                    n=n,
                    side="".join(map(str, side)),
                    v=v,
                    R=str(rv),
                    seed=tuple(sorted(seed)),
                    moat=tuple(sorted(moat)),
                    S=tuple(sorted(set(seed) | set(moat))),
                    drop=drop,
                    exit_order=[
                        dict(edge=e, inside=edge_parts(e, smask)[0], outside=edge_parts(e, smask)[1], witnesses=tuple(sorted(by_e[e], key=str)))
                        for e in eorder
                    ],
                    bad_order=[
                        dict(edge=f, ell=ell[f], exits=tuple(eorder.index(e) for e in by_f[f]))
                        for f in forder
                    ],
                )
            )
            if len(out) >= limit:
                return out
    return out


def main():
    examples = []
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            examples.extend(process("cen%d:%s" % (nn, g6), n, edges, 4 - len(examples)))
            if len(examples) >= 4:
                break
        if len(examples) >= 4:
            break
    hN, hE = dec("H?AFBo]")
    n, edges = vertex_blowup(hN, hE, 2)
    examples.extend(process("Hblow2", n, edges, 12))
    for idx, ex in enumerate(examples[:12], 1):
        print("=" * 80)
        print("EX", idx, "graph", ex["graph"], "n", ex["n"], "side", ex["side"], "v", ex["v"], "R", ex["R"], "drop", ex["drop"])
        print("seed", ex["seed"], "moat", ex["moat"], "S", ex["S"])
        print("exit_order:")
        for k, row in enumerate(ex["exit_order"]):
            print(" ", k, row)
        print("bad_order:")
        for k, row in enumerate(ex["bad_order"]):
            print(" ", k, row)


if __name__ == "__main__":
    main()
