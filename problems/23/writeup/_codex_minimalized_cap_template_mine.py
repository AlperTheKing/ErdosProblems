"""Classify side-cap witness graphs after selected-switch minimalization.

This is a read-only diagnostic for the K2T Hall proof target.  It starts with
the same selected seed+moat switches as `_codex_minimalized_sidecap_gate.py`,
shrinks each to an inclusion-minimal neutral terminal-shadow Gamma-decreasing
subset containing the negative-residual vertex, and then classifies the
bipartite witness graph on each laminar side cap.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_selected_interval_hall_gate import laminar_leaves
from _codex_selected_minimality_gate import mask_of, smaller_descent


def vertices(mask, n):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def minimalize(n, adj, side, st, gamma0, smask, v):
    while True:
        got = smaller_descent(n, adj, side, st, gamma0, smask, v)
        if got is None:
            return smask
        smask = got[0]


def canonical_bipartite(rows, cols, edges):
    rows = tuple(rows)
    cols = tuple(cols)
    best = None
    for rp in itertools.permutations(rows):
        for cp in itertools.permutations(cols):
            bits = tuple(1 if (r, c) in edges else 0 for r in rp for c in cp)
            if best is None or bits < best:
                best = bits
    return len(rows), len(cols), best


def inside_endpoint(edge, smask):
    a, b = edge
    ain = (smask >> a) & 1
    bin_ = (smask >> b) & 1
    if ain and not bin_:
        return a
    if bin_ and not ain:
        return b
    return None


def cap_hall_min(cap, cap_neighbors):
    best = None
    cap = list(cap)
    for r in range(1, len(cap) + 1):
        for sub in itertools.combinations(cap, r):
            nbr = set().union(*(cap_neighbors[e] for e in sub))
            gap = len(nbr) - len(sub)
            best = gap if best is None else min(best, gap)
    return best


def inspect_cap(name, n, side, st, smask, cap, fset, exits_of_f, witnesses, acc, examples):
    touch = {f for f in fset if exits_of_f[f] & cap}
    cap_neighbors = {e: {f for f in touch if e in exits_of_f[f]} for e in cap}
    cap_edges = {(e, f) for e, fs in cap_neighbors.items() for f in fs}
    complete = all(fs == touch for fs in cap_neighbors.values())
    min_deg = min((len(fs) for fs in cap_neighbors.values()), default=0)
    max_deg = max((len(fs) for fs in cap_neighbors.values()), default=0)
    gap = cap_hall_min(cap, cap_neighbors)
    ell = st[1]
    touch_lengths = tuple(sorted(ell[f] for f in touch))
    lambdas = tuple(sorted(min(ell[f] for f in witnesses[e]) for e in cap))
    cap_inside = tuple(sorted({inside_endpoint(e, smask) for e in cap}))
    touch_inside = tuple(sorted({inside_endpoint(f, smask) for f in touch}))

    sig = (len(cap), len(touch), gap, complete, min_deg, max_deg, touch_lengths, lambdas)
    acc["cap_signature"][sig] += 1
    acc["matrix_signature"][canonical_bipartite(sorted(cap), sorted(touch), cap_edges)] += 1
    acc["inside_signature"][(len(cap), len(touch), gap, cap_inside, touch_inside)] += 1
    acc["gap"][gap] += 1
    acc["caps"] += 1
    if complete:
        acc["complete"] += 1
    else:
        acc["noncomplete"] += 1
        if len(examples["noncomplete"]) < 12:
            examples["noncomplete"].append(
                (
                    name,
                    n,
                    "".join(map(str, side)),
                    vertices(smask, n),
                    tuple(sorted(cap)),
                    tuple(sorted(touch)),
                    {e: tuple(sorted(cap_neighbors[e])) for e in sorted(cap)},
                )
            )


def scan_cut(name, n, adj, side, acc, examples, max_add):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, cyc = st
    if not M:
        return
    K2 = build_K2(n, M, cyc)
    R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        acc["neg"] += 1
        got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=max_add)
        if got is None:
            acc["no_seedmoat"] += 1
            continue
        seed, moat, _drop = got
        smask0 = mask_of(set(seed) | set(moat))
        smask = minimalize(n, adj, side, st, gamma0, smask0, v)
        if smask != smask0:
            acc["shrunk"] += 1
        det = terminal_shadow_details(n, adj, side, st, smask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        acc["switches"] += 1
        fset = tuple(sorted(det["cross_m"]))
        eset = tuple(sorted(det["bdy_b"]))
        witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
        exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in fset}
        miss_sets = [set(eset) - exits_of_f[f] for f in fset]
        leaves = laminar_leaves(miss_sets) or []
        if not leaves:
            acc["no_cap"] += 1
        for cap in leaves:
            inspect_cap(name, n, side, st, smask, cap, fset, exits_of_f, witnesses, acc, examples)


def scan_graph(name, n, edges, acc, examples, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, examples, max_add)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-add", type=int, default=1)
    ap.add_argument("--h2-allmax", action="store_true")
    args = ap.parse_args()

    acc = Counter()
    acc["gap"] = Counter()
    acc["cap_signature"] = Counter()
    acc["matrix_signature"] = Counter()
    acc["inside_signature"] = Counter()
    examples = {"noncomplete": []}

    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph("cen%d:%s" % (nn, g6), n, edges, acc, examples, args.max_add)
    if args.h2_allmax:
        n, edges = vertex_blowup(*dec("H?AFBo]"), 2)
        scan_graph("H?AFBo]x2", n, edges, acc, examples, args.max_add)

    print("neg:", acc["neg"], "switches:", acc["switches"], "shrunk:", acc["shrunk"])
    print("caps:", acc["caps"], "complete:", acc["complete"], "noncomplete:", acc["noncomplete"], "no_cap:", acc["no_cap"])
    print("bad_terminal:", acc["bad_terminal"], "no_seedmoat:", acc["no_seedmoat"])
    print("gap:", sorted(acc["gap"].items()))
    print("cap signatures:")
    for sig, cnt in acc["cap_signature"].most_common(30):
        print(" ", sig, cnt)
    print("matrix signatures:")
    for sig, cnt in acc["matrix_signature"].most_common(30):
        print(" ", sig, cnt)
    print("inside signatures:")
    for sig, cnt in acc["inside_signature"].most_common(30):
        print(" ", sig, cnt)
    print("noncomplete examples:")
    for ex in examples["noncomplete"]:
        print(" ", ex)


if __name__ == "__main__":
    main()
