"""Classify the positive-Psi length-bundle switches covering R[v] < 0.

This is a diagnostic, not a proof gate.  It records the length signature of
the empirically decisive switches:

  * chosen bundle length L;
  * lengths of crossing old bad edges;
  * lambda prices of new boundary B-edges.

The goal is to see whether the surviving construction has a simpler normal
form than the raw terminal-shadow existential.
"""

import argparse
import random
import subprocess
from collections import Counter

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals


def edge(u, v):
    return (u, v) if u < v else (v, u)


def connected(adj):
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(adj)


def bundle_candidates(ell, cyc, v):
    out = []
    for L in sorted(set(ell.values())):
        for rev in (False, True):
            hits = []
            for f, paths0 in cyc.items():
                if ell[f] != L:
                    continue
                for path0 in paths0:
                    path = list(reversed(path0)) if rev else list(path0)
                    if v in path:
                        hits.append(path)
            if not hits:
                continue

            for sign in ("pref", "suff"):
                mask = 0
                for path in hits:
                    i = path.index(v)
                    interval = path[: i + 1] if sign == "pref" else path[i:]
                    for x in interval:
                        mask |= 1 << x
                out.append((L, rev, sign, mask, len(hits)))
    return out


def terminal_shadow_details(n, adj, side, st, mask):
    M, ell, _T, _mu, cyc = st
    bdy_b = set()
    cross_m = []
    for u in range(n):
        inu = (mask >> u) & 1
        for v in adj[u]:
            if v <= u:
                continue
            if inu == ((mask >> v) & 1):
                continue
            if side[u] == side[v]:
                cross_m.append(edge(u, v))
            else:
                bdy_b.add(edge(u, v))

    witnesses = {e: [] for e in bdy_b}
    for f in cross_m:
        u, v = f
        tau = u if ((mask >> u) & 1) else v
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            if path[0] != tau:
                return None
            bits = [(mask >> x) & 1 for x in path]
            if bits[0] != 1 or bits[-1] != 0:
                return None
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            if any(bits[j] for j in range(r + 1, len(bits))):
                return None
            if r > len(path) - 2:
                return None
            exit_edge = edge(path[r], path[r + 1])
            if exit_edge not in witnesses:
                return None
            witnesses[exit_edge].append(f)

    if any(not ws for ws in witnesses.values()):
        return None

    for h in M:
        if h in cross_m:
            continue
        safe = False
        for path in cyc[h]:
            if all(edge(path[i], path[i + 1]) not in bdy_b for i in range(len(path) - 1)):
                safe = True
                break
        if not safe:
            return None

    cross_lengths = tuple(sorted(ell[f] for f in cross_m))
    lambda_lengths = tuple(sorted(min(ell[f] for f in ws) for ws in witnesses.values()))
    psi = sum(x * x for x in cross_lengths) - sum(x * x for x in lambda_lengths)
    return dict(
        psi=psi,
        cross_lengths=cross_lengths,
        lambda_lengths=lambda_lengths,
        cross_m=tuple(sorted(cross_m)),
        bdy_b=tuple(sorted(bdy_b)),
        witnesses={e: tuple(sorted(ws)) for e, ws in witnesses.items()},
    )


def max_bipartite_matching(left, right, adj):
    """Return a maximum matching size from left to right."""
    match_r = {}

    def dfs(u, seen):
        for v in adj.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or dfs(match_r[v], seen):
                match_r[v] = u
                return True
        return False

    size = 0
    for u in left:
        if dfs(u, set()):
            size += 1
    return size, match_r


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    _M, ell, _T, _mu, cyc = st
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        acc["neg"] += 1
        best = None
        for L, rev, sign, mask, hits in bundle_candidates(ell, cyc, v):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            if not Bconn(n, adj, flip_side(side, mask)):
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or det["psi"] <= 0:
                continue
            cand = (mask.bit_count(), -det["psi"], L, rev, sign, mask, hits, det)
            if best is None or cand < best:
                best = cand
        if best is None:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(rv))
            continue
        size, negpsi, L, rev, sign, mask, hits, det = best
        psi = -negpsi
        cross = det["cross_lengths"]
        lambdas = det["lambda_lengths"]
        normal_all_cross_L = all(x == L for x in cross)
        normal_all_lambda_lt_L = all(x < L for x in lambdas)
        normal_majorizes = len(cross) == len(lambdas) and all(a >= b for a, b in zip(cross, lambdas))
        witness_adj = {f: [] for f in det["cross_m"]}
        for e, fs in det["witnesses"].items():
            for f in fs:
                witness_adj[f].append(e)
        match_size, matching = max_bipartite_matching(det["cross_m"], det["bdy_b"], witness_adj)
        perfect_witness_matching = match_size == len(det["cross_m"]) == len(det["bdy_b"])
        strict_matched = False
        if perfect_witness_matching:
            # matching maps boundary edge -> crossing bad edge
            for e, f in matching.items():
                if ell[f] > min(ell[g] for g in det["witnesses"][e]):
                    strict_matched = True
        acc["covered"] += 1
        acc["sig_hist"][(L, cross, lambdas)] += 1
        acc["normal_cross_L"][normal_all_cross_L] += 1
        acc["normal_lambda_lt_L"][normal_all_lambda_lt_L] += 1
        acc["normal_majorizes"][normal_majorizes] += 1
        acc["perfect_witness_matching"][perfect_witness_matching] += 1
        acc["strict_matched"][strict_matched] += 1
        if len(acc["examples"]) < acc["example_limit"]:
            acc["examples"].append(
                (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(rv),
                    L,
                    sign,
                    psi,
                    mask_tuple(n, mask),
                    cross,
                    lambdas,
                    hits,
                    perfect_witness_matching,
                    strict_matched,
                )
            )


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=0)
    parser.add_argument("--examples", type=int, default=20)
    args = parser.parse_args()

    acc = dict(
        neg=0,
        covered=0,
        fail=0,
        first_fail=None,
        sig_hist=Counter(),
        normal_cross_L=Counter(),
        normal_lambda_lt_L=Counter(),
        normal_majorizes=Counter(),
        perfect_witness_matching=Counter(),
        strict_matched=Counter(),
        examples=[],
        example_limit=args.examples,
    )

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print("census N=%d neg=%d covered=%d fail=%d" % (n, acc["neg"], acc["covered"], acc["fail"]), flush=True)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)
        print("H?AFBo][%d] neg=%d covered=%d fail=%d" % (t, acc["neg"], acc["covered"], acc["fail"]), flush=True)

    if args.random:
        rng = random.Random(774)
        made = 0
        tries = 0
        while made < args.random and tries < 100000:
            tries += 1
            n = rng.choice([11, 12])
            p = rng.uniform(0.16, 0.32)
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
            if not edges or not is_triangle_free(n, edges):
                continue
            adj = adj_from_edges(n, edges)
            if not connected(adj):
                continue
            made += 1
            scan_graph("rand%d" % made, n, edges, acc)
        print("random graphs scanned:", made, flush=True)

    print("=" * 72)
    print("neg:", acc["neg"])
    print("covered:", acc["covered"])
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("all crossing lengths equal L:", dict(acc["normal_cross_L"]))
    print("all lambda lengths < L:", dict(acc["normal_lambda_lt_L"]))
    print("sorted crossing lengths majorize lambdas:", dict(acc["normal_majorizes"]))
    print("perfect witness matching:", dict(acc["perfect_witness_matching"]))
    print("strict matched witness:", dict(acc["strict_matched"]))
    print("signature histogram:")
    for sig, count in acc["sig_hist"].most_common():
        print(" ", count, sig)
    print("examples:")
    for ex in acc["examples"]:
        print(" ", ex)


if __name__ == "__main__":
    main()
