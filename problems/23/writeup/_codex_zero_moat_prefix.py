"""Zero-moat prefix-switch checker.

Tests the GPT-Pro proposed certificate for C-alltie:

If O nonempty, T(z)=0, zv is a cut edge, T(v)=N, and the positive-K
component C(v) misses O, then some switch S = prefix_through(v) union Z
where Z is a connected zero-load moat containing z should satisfy:
  * cut-loss Delta_beta(S)=0,
  * the switched cut graph B^S is connected,
  * Gamma^S < Gamma.

This checker intentionally scans connected maximum cuts, not only Gamma-min
cuts, because the premise is already absent on the verified Gamma-min gate.
"""
from __future__ import annotations

import argparse
import itertools
import multiprocessing as mp
import subprocess
from collections import deque
from fractions import Fraction as F

from _h import Bconn, GENG, bdist_restr, dec, geos, maxcut_all
from _satzmu_conn import kcomponents, struct_for_side


def build_adj(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def edge_sets(n, adj, side):
    B = set()
    M = set()
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            e = (u, v)
            if side[u] != side[v]:
                B.add(e)
            else:
                M.add(e)
    return B, M


def gamma_for_side(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    G = 0
    M = []
    for u in range(n):
        for v in adj[u]:
            if v <= u or side[u] != side[v]:
                continue
            d = bdist_restr(adj, side, u, v)
            if d < 0:
                return None
            M.append((u, v))
            G += (d + 1) ** 2
    if not M:
        return None
    return G


def flip_side(side, S):
    out = list(side)
    for v in S:
        out[v] ^= 1
    return out


def cut_loss(B, M, S):
    S = set(S)
    db = sum(1 for u, v in B if (u in S) ^ (v in S))
    dm = sum(1 for u, v in M if (u in S) ^ (v in S))
    return db - dm


def zero_b_component(n, adj, side, T, z):
    zero = {v for v in range(n) if T[v] == 0}
    if z not in zero:
        return set()
    seen = {z}
    q = deque([z])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w in zero and side[u] != side[w] and w not in seen:
                seen.add(w)
                q.append(w)
    return seen


def is_b_connected_subset(adj, side, S):
    S = set(S)
    if not S:
        return False
    start = next(iter(S))
    seen = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w in S and side[u] != side[w] and w not in seen:
                seen.add(w)
                q.append(w)
    return seen == S


def connected_zero_moats(adj, side, comp, z, forbidden=frozenset()):
    """All B-connected zero subsets of comp containing z, disjoint forbidden."""
    avail = sorted(set(comp) - set(forbidden))
    if z not in avail:
        return
    rest = [v for v in avail if v != z]
    # Small exact census checker: exhaustive subsets are fine for N<=11.
    for mask in range(1 << len(rest)):
        S = {z}
        for i, v in enumerate(rest):
            if (mask >> i) & 1:
                S.add(v)
        if is_b_connected_subset(adj, side, S):
            yield frozenset(S)


def candidates_for_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, ell, T, mu, cyc = st
    N = n
    O = {v for v in range(N) if T[v] > N}
    if not O:
        return []
    comps, find = kcomponents(n, cyc)
    out = []
    for z in range(n):
        if T[z] != 0:
            continue
        for v in adj[z]:
            if side[z] == side[v] or T[v] != N:
                continue
            Cv = comps[find(v)]
            if Cv & O:
                continue
            out.append((z, v, frozenset(Cv), frozenset(O)))
    return out


def find_certificate(n, adj, side, z, v, C, O):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    G0 = sum(L * L for L in ell.values())
    Bset, Mset = edge_sets(n, adj, side)
    zcomp = zero_b_component(n, adj, side, T, z)
    if not zcomp:
        return None

    for f in M:
        for P in cyc[f]:
            positions = [i for i, x in enumerate(P) if x == v]
            for i in positions:
                prefixes = [
                    frozenset(P[: i + 1]),
                    frozenset(P[i:]),
                ]
                for A in prefixes:
                    for Z in connected_zero_moats(adj, side, zcomp, z, forbidden=C):
                        S = frozenset(set(A) | set(Z))
                        if cut_loss(Bset, Mset, S) != 0:
                            continue
                        side2 = flip_side(side, S)
                        G2 = gamma_for_side(n, adj, side2)
                        if G2 is not None and G2 < G0:
                            return {
                                "z": z,
                                "v": v,
                                "f": f,
                                "path": tuple(P),
                                "prefix": tuple(sorted(A)),
                                "Z": tuple(sorted(Z)),
                                "S": tuple(sorted(S)),
                                "G0": G0,
                                "G2": G2,
                                "O": tuple(sorted(O)),
                                "C": tuple(sorted(C)),
                            }
    return None


def connected_maxcut_sides(n, adj):
    cuts = maxcut_all(n, adj)
    for side in cuts:
        if Bconn(n, adj, side):
            # Require at least one bad edge and finite B-distances.
            if gamma_for_side(n, adj, side) is not None:
                yield side


def scan_graph(g6, all_maxcuts=True):
    n, E = dec(g6)
    adj = build_adj(n, E)
    sides = connected_maxcut_sides(n, adj) if all_maxcuts else []
    total_premises = 0
    missing = []
    certs = []
    for side in sides:
        for z, v, C, O in candidates_for_side(n, adj, side):
            total_premises += 1
            cert = find_certificate(n, adj, side, z, v, C, O)
            if cert is None:
                missing.append((side, z, v, tuple(sorted(C)), tuple(sorted(O))))
                if len(missing) >= 3:
                    return total_premises, certs, missing
            else:
                certs.append(cert)
    return total_premises, certs, missing


def scan_graph_summary(g6):
    total, certs, missing = scan_graph(g6, all_maxcuts=True)
    return g6, total, len(certs), missing[0] if missing else None


def scan_census(nmin, nmax, limit=None, workers=1):
    for N in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
        if limit:
            g6s = g6s[:limit]
        graphs_with_premise = 0
        premise_count = 0
        cert_count = 0
        first_missing = None
        if workers > 1:
            ctx = mp.get_context("spawn")
            iterator = ctx.Pool(processes=workers).imap_unordered(scan_graph_summary, g6s, chunksize=8)
        else:
            iterator = map(scan_graph_summary, g6s)
        try:
            for g6, total, ncerts, first_graph_missing in iterator:
                if total:
                    graphs_with_premise += 1
                    premise_count += total
                    cert_count += ncerts
                if first_graph_missing is not None:
                    first_missing = (g6, first_graph_missing)
                    break
        finally:
            if workers > 1 and hasattr(iterator, "_pool"):
                iterator._pool.terminate()
                iterator._pool.join()
        print(
            f"N={N}: graphs_with_premise={graphs_with_premise} "
            f"premises={premise_count} certs={cert_count} "
            f"missing={first_missing}",
            flush=True,
        )
        if first_missing is not None:
            break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=9)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--graph6", action="append", default=[])
    args = ap.parse_args()

    if args.graph6:
        for g6 in args.graph6:
            total, certs, missing = scan_graph(g6)
            print(f"{g6}: premises={total} certs={len(certs)} missing={len(missing)}")
            if certs:
                print("  first_cert=", certs[0])
            if missing:
                print("  first_missing=", missing[0])
    else:
        scan_census(args.nmin, args.nmax, args.limit, args.workers)


if __name__ == "__main__":
    main()
