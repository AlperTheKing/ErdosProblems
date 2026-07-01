"""Gate inclusion-minimality of selected seed+moat descent switches.

Claude's latest suggested route is that strict cap expansion may follow from
neutral-minimality: deleting a deficient side cap would yield a smaller neutral
Gamma-decreasing switch.  Before using that argument, this gate checks whether
the selected switches returned by find_seedmoat are already inclusion-minimal
among proper subsets containing the negative-residual vertex and satisfying:

  * neutral boundary_delta == 0,
  * terminal-shadow validity,
  * B-connected after flip and Gamma decreases.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import boundary_delta, flip, gamma_of
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def mask_of(vertices):
    out = 0
    for v in vertices:
        out |= 1 << v
    return out


def vertices_of(mask, n):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def smaller_descent(n, adj, side, st, gamma0, smask, v):
    sverts = [i for i in range(n) if (smask >> i) & 1]
    others = [x for x in sverts if x != v]
    # Enumerate by increasing size so the first witness is a true smaller one.
    for k in range(0, len(others)):
        for sub in itertools.combinations(others, k):
            umask = (1 << v)
            for x in sub:
                umask |= 1 << x
            if umask == smask:
                continue
            U = set(vertices_of(umask, n))
            if boundary_delta(n, adj, side, U) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, umask)
            if det is None:
                continue
            g2 = gamma_of(n, adj, flip(side, U))
            if g2 is not None and g2 < gamma0:
                return umask, gamma0 - g2, det["psi"]
    return None


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
            acc["no_switch"] += 1
            continue
        seed, moat, drop = got
        smask = mask_of(set(seed) | set(moat))
        acc["tested"] += 1
        acc["size"][len(seed) + len(moat)] += 1
        witness = smaller_descent(n, adj, side, st, gamma0, smask, v)
        if witness is None:
            acc["minimal"] += 1
        else:
            acc["nonminimal"] += 1
            if first is None:
                umask, udrop, upsi = witness
                first = dict(
                    name=name,
                    n=n,
                    side="".join(map(str, side)),
                    v=v,
                    R=str(rv),
                    S=vertices_of(smask, n),
                    S_drop=str(drop),
                    U=vertices_of(umask, n),
                    U_drop=str(udrop),
                    U_psi=upsi,
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
    acc = {"tested": 0, "minimal": 0, "nonminimal": 0, "no_switch": 0, "size": Counter()}
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
    print("tested:", acc["tested"], "minimal:", acc["minimal"], "nonminimal:", acc["nonminimal"], "no_switch:", acc["no_switch"])
    print("size:", sorted(acc["size"].items()))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
