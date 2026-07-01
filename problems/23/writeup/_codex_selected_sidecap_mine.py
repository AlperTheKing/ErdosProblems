"""Mine Hall margins on laminar missed-exit side caps for selected switches."""

import subprocess
import itertools
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def mask_of(vertices):
    out = 0
    for v in vertices:
        out |= 1 << v
    return out


def canonical_bipartite(rows, cols, edges):
    rows = tuple(rows)
    cols = tuple(cols)
    best = None
    for rp in itertools.permutations(rows):
        for cp in itertools.permutations(cols):
            bits = tuple(1 if (r, c) in edges else 0 for r in rp for c in cp)
            if best is None or bits < best:
                best = bits
    return (len(rows), len(cols), best)


def inside_endpoint(edge, smask):
    a, b = edge
    ain = (smask >> a) & 1
    bin_ = (smask >> b) & 1
    if ain and not bin_:
        return a
    if bin_ and not ain:
        return b
    return None


def mine_switch(name, n, adj, side, st, v, seed, moat, acc, examples):
    scalar = acc["scalar"]
    det = terminal_shadow_details(n, adj, side, st, mask_of(set(seed) | set(moat)))
    if det is None:
        scalar["bad_terminal"] += 1
        return
    Fset = tuple(sorted(det["cross_m"]))
    Eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in Eset if f in witnesses[e]} for f in Fset}
    smask = mask_of(set(seed) | set(moat))
    miss_nodes = sorted({tuple(sorted(set(Eset) - exits_of_f[f])) for f in Fset if set(Eset) - exits_of_f[f]}, key=lambda z: (len(z), z))
    scalar["switches"] += 1
    if not miss_nodes:
        scalar["no_cap"] += 1
    for zt in miss_nodes:
        Z = set(zt)
        A = {f for f in Fset if Z <= (set(Eset) - exits_of_f[f])}
        margin = len(Eset) - len(Z) - len(A)
        scalar["caps"] += 1
        acc["margin"][margin] += 1
        touch = set(Fset) - A
        cap_neighbors = {e: {f for f in Fset if e in exits_of_f[f]} for e in Z}
        cap_inside = tuple(sorted({inside_endpoint(e, smask) for e in Z}))
        touch_inside = tuple(sorted({inside_endpoint(f, smask) for f in touch}))
        cap_edges = {(e, f) for e, fs in cap_neighbors.items() for f in fs}
        acc["matrix_signature"][canonical_bipartite(sorted(Z), sorted(touch), cap_edges)] += 1
        complete_cap = all(ns == touch for ns in cap_neighbors.values())
        min_cap_deg = min((len(ns) for ns in cap_neighbors.values()), default=0)
        max_cap_deg = max((len(ns) for ns in cap_neighbors.values()), default=0)
        ell = st[1]
        touch_lengths = tuple(sorted(ell[f] for f in touch))
        z_lambdas = []
        for e in Z:
            z_lambdas.append(min(ell[f] for f in witnesses[e]))
        z_lambdas = tuple(sorted(z_lambdas))
        strict_touch = sum(1 for f in touch if ell[f] > min(ell[g] for g in touch))
        acc["signature"][(len(Eset), len(Z), len(A), margin)] += 1
        acc["len_signature"][(len(Z), margin, touch_lengths, z_lambdas, strict_touch)] += 1
        acc["block_signature"][(len(Z), len(touch), margin, complete_cap, min_cap_deg, max_cap_deg)] += 1
        acc["inside_signature"][(len(Z), len(touch), margin, cap_inside, touch_inside)] += 1
        if not complete_cap:
            scalar["noncomplete_cap"] += 1
            if not examples["noncomplete"]:
                examples["noncomplete"].append((name, n, "".join(map(str, side)), v, zt, tuple(sorted(touch)), {e: tuple(sorted(ns)) for e, ns in cap_neighbors.items()}))
        cap_hall_min = None
        cap_strict_min = None
        zlist = list(Z)
        for r in range(1, len(zlist) + 1):
            for sub in itertools.combinations(zlist, r):
                nbr = set().union(*(cap_neighbors[e] for e in sub))
                gap = len(nbr) - len(sub)
                cap_hall_min = gap if cap_hall_min is None else min(cap_hall_min, gap)
                if len(sub) < len(zlist):
                    cap_strict_min = gap if cap_strict_min is None else min(cap_strict_min, gap)
        acc["cap_hall_min"][cap_hall_min] += 1
        acc["cap_proper_hall_min"][cap_strict_min if cap_strict_min is not None else 999] += 1
        if cap_hall_min < 1:
            scalar["cap_hall_surplus_fail"] += 1
            if not examples["cap_hall_fail"]:
                examples["cap_hall_fail"].append((name, n, "".join(map(str, side)), v, zt, {e: tuple(sorted(ns)) for e, ns in cap_neighbors.items()}, cap_hall_min))
        if margin < 0:
            scalar["fail"] += 1
            if not examples["fail"]:
                examples["fail"].append((name, n, "".join(map(str, side)), v, tuple(sorted(seed)), tuple(sorted(moat)), Eset, Fset, zt, tuple(sorted(A)), margin))
        if margin == 0 and len(examples["tight"]) < 12:
            examples["tight"].append((name, n, "".join(map(str, side)), v, len(Eset), len(Z), len(A), zt, tuple(sorted(A))))
        if margin == 1 and len(examples["margin1"]) < 12:
            examples["margin1"].append((name, n, "".join(map(str, side)), v, tuple(sorted(seed)), tuple(sorted(moat)), len(Eset), zt, tuple(sorted(A)), touch_lengths, z_lambdas, strict_touch))


def process_graph(name, n, edges, acc, examples):
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
            acc["scalar"]["neg"] += 1
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                acc["scalar"]["no_seedmoat"] += 1
                continue
            seed, moat, _drop = sm
            mine_switch(name, n, adj, side, st, v, seed, moat, acc, examples)


def main():
    acc = {
        "scalar": Counter(),
        "margin": Counter(),
        "signature": Counter(),
        "len_signature": Counter(),
        "block_signature": Counter(),
        "cap_hall_min": Counter(),
        "cap_proper_hall_min": Counter(),
        "matrix_signature": Counter(),
        "inside_signature": Counter(),
    }
    examples = {"tight": [], "margin1": [], "fail": [], "noncomplete": [], "cap_hall_fail": []}

    def wrap_process(name, n, edges):
        process_graph(name, n, edges, acc, examples)

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            wrap_process(f"cen{nn}:{g6}", n, edges)
    hn, he = dec("H?AFBo]")
    n, edges = vertex_blowup(hn, he, 2)
    wrap_process("H?AFBo]x2", n, edges)

    scalar = acc["scalar"]
    print("neg", scalar["neg"], "switches", scalar["switches"], "caps", scalar["caps"], "no_cap", scalar["no_cap"], "fail", scalar["fail"])
    print("margin", sorted(acc["margin"].items()))
    print("top signatures")
    for sig, cnt in acc["signature"].most_common(20):
        print(" ", sig, cnt)
    print("top length signatures")
    for sig, cnt in acc["len_signature"].most_common(20):
        print(" ", sig, cnt)
    print("top block signatures")
    for sig, cnt in acc["block_signature"].most_common(20):
        print(" ", sig, cnt)
    print("tight examples")
    for ex in examples["tight"]:
        print(" ", ex)
    print("margin1 examples")
    for ex in examples["margin1"]:
        print(" ", ex)
    print("fail examples", examples["fail"])
    print("noncomplete", scalar["noncomplete_cap"], examples["noncomplete"])
    print("cap_hall_min", sorted(acc["cap_hall_min"].items()))
    print("cap_proper_hall_min", sorted(acc["cap_proper_hall_min"].items()))
    print("cap_hall_surplus_fail", scalar["cap_hall_surplus_fail"], examples["cap_hall_fail"])
    print("matrix signatures")
    for sig, cnt in acc["matrix_signature"].most_common(20):
        print(" ", sig, cnt)
    print("inside signatures")
    for sig, cnt in acc["inside_signature"].most_common(20):
        print(" ", sig, cnt)


if __name__ == "__main__":
    main()
