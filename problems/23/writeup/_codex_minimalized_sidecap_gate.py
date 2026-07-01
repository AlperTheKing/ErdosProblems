"""Gate strict side-cap expansion for minimalized selected switches."""

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


def minimalize(n, adj, side, st, gamma0, smask, v):
    while True:
        got = smaller_descent(n, adj, side, st, gamma0, smask, v)
        if got is None:
            return smask
        smask = got[0]


def cap_expansion(det):
    fset = tuple(sorted(det["cross_m"]))
    eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in fset}
    miss_sets = [set(eset) - exits_of_f[f] for f in fset]
    leaves = laminar_leaves(miss_sets) or []
    out = []
    for cap in leaves:
        cap = list(cap)
        best = None
        best_sub = None
        best_nbr = None
        for r in range(1, len(cap) + 1):
            for sub in itertools.combinations(cap, r):
                y = set(sub)
                nbr = {f for f in fset if exits_of_f[f] & y}
                gap = len(nbr) - len(y)
                if best is None or gap < best:
                    best = gap
                    best_sub = tuple(sorted(y))
                    best_nbr = tuple(sorted(nbr))
        out.append((tuple(sorted(cap)), best, best_sub, best_nbr))
    return out


def scan_cut(name, n, adj, side, acc, first, max_add):
    if not Bconn(n, adj, side):
        return first
    st = struct_for_side(n, adj, side)
    if st is None:
        return first
    M, ell, T, _mu, cyc = st
    if not M:
        return first
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
        if smask != smask0:
            acc["shrunk"] += 1
        det = terminal_shadow_details(n, adj, side, st, smask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        acc["switches"] += 1
        caps = cap_expansion(det)
        if not caps:
            acc["no_cap"] += 1
        for cap, gap, sub, nbr in caps:
            acc["caps"] += 1
            acc["gap"][gap] += 1
            if gap < 1 and first is None:
                first = dict(
                    name=name,
                    n=n,
                    side="".join(map(str, side)),
                    v=v,
                    R=str(rv),
                    S=tuple(i for i in range(n) if (smask >> i) & 1),
                    cap=cap,
                    gap=gap,
                    subset=sub,
                    witnesses=nbr,
                )
    return first


def scan_allmax(name, n, edges, acc, first, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    args = parser.parse_args()
    acc = Counter()
    acc["gap"] = Counter()
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add)
            if first is not None:
                break
        if first is not None:
            break
    if first is None and args.h2_allmax:
        n, edges = vertex_blowup(*dec("H?AFBo]"), 2)
        first = scan_allmax("H?AFBo]x2", n, edges, acc, first, args.max_add)

    print("switches:", acc["switches"], "shrunk:", acc["shrunk"], "caps:", acc["caps"], "no_cap:", acc["no_cap"])
    print("bad_terminal:", acc["bad_terminal"], "no_seedmoat:", acc["no_seedmoat"])
    print("gap:", sorted(acc["gap"].items()))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
