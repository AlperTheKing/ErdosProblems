"""Numerical scout for PSC-50.

Candidate certificate:
  lambda + |M| + Xi(h)/50 <= N + N^2/25

where lambda is the Perron root of O=P^T P, x is a nonnegative top
eigenvector with |x|_2=1, Phi(v)=sum_f x_f p_f(v),
h(v)=N Phi(v)^2/lambda, and
Xi(h)=sum_{uv in B}|h_u-h_v|-sum_{uv in M}|h_u-h_v|.

This script is only a fast scout.  The acceptance gate must be exact/algebraic
or interval-certified; this code uses floating eigensolvers.
"""

import argparse
import math
import subprocess
from fractions import Fraction as F

import numpy as np

from _h import Bconn, GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _wf_lrsbreak_0 import build_k_lane, cpmax, trifree


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def blowup(parts):
    m = len(parts)
    off = [0] * (m + 1)
    for i in range(m):
        off[i + 1] = off[i] + parts[i]
    n = off[m]
    edges = []
    for i in range(m):
        j = (i + 1) % m
        for a in range(off[i], off[i + 1]):
            for b in range(off[j], off[j + 1]):
                edges.append((min(a, b), max(a, b)))
    return n, sorted(set(edges))




def build_two_lane(L):
    a = lambda i: (L + 1) + i
    b = lambda i: (L + 1) + (L + 1) + i
    n = 3 * (L + 1)
    edges = set()
    for i in range(L):
        edges.add((i, i + 1))
    for i in range(L + 1):
        edges.add((min(i, a(i)), max(i, a(i))))
        edges.add((min(i, b(i)), max(i, b(i))))
    for i in range(L):
        for u in (a(i), b(i)):
            for v in (a(i + 1), b(i + 1)):
                edges.add((min(u, v), max(u, v)))
    bad = [(0, L - 2), (0, L), (2, L - 2), (2, L)]
    for e in bad:
        edges.add((min(e), max(e)))
    side = [0] * n
    for i in range(L + 1):
        side[i] = i % 2
        side[a(i)] = 1 - (i % 2)
        side[b(i)] = 1 - (i % 2)
    return n, sorted(edges), side, bad


def greedy_chords(L, k, gap):
    base_n, base_edges, _, _ = build_k_lane(L, k, [])
    adj = adj_of(base_n, base_edges)
    chords = []
    cand = [(a, b) for a in range(L + 1) for b in range(a + gap, L + 1) if (a % 2) == (b % 2)]
    for a, b in cand:
        if b in adj[a] or (adj[a] & adj[b]):
            continue
        adj[a].add(b)
        adj[b].add(a)
        chords.append((a, b))
    return chords

def p_matrix(n, M, cyc):
    fs = list(M)
    P = np.zeros((n, len(fs)), dtype=np.float64)
    for j, f in enumerate(fs):
        paths = cyc[f]
        k = len(paths)
        for path in paths:
            for v in path:
                P[v, j] += 1.0 / k
    return fs, P


def psc50_case(name, n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    fs, P = p_matrix(n, M, cyc)
    O = P.T @ P
    vals, vecs = np.linalg.eigh(O)
    lam = float(vals[-1])
    x = np.array(vecs[:, -1], dtype=np.float64)
    # Pick the Perron orientation on the top component; connected positive O
    # cases are nonnegative up to sign.  For reducible top multiplicity, this is
    # only a scout and Claude should exact-test componentwise.
    if np.sum(x) < 0:
        x = -x
    x = np.maximum(x, 0.0)
    norm = float(np.linalg.norm(x))
    if norm == 0.0:
        return None
    x = x / norm
    Phi = P @ x
    lam_ray = float(Phi @ Phi)
    if abs(lam_ray - lam) > 1e-6 * max(1.0, abs(lam)):
        lam = lam_ray
    h = (n / lam) * (Phi * Phi)
    B_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    M_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    Xi = sum(abs(h[u] - h[v]) for u, v in B_edges) - sum(abs(h[u] - h[v]) for u, v in M_edges)
    rhs = n + n * n / 25.0
    margin = rhs - len(M) - lam - Xi / 50.0
    sbc_margin = rhs - len(M) - lam
    return {
        "name": name,
        "N": n,
        "m": len(M),
        "lambda": lam,
        "Xi": Xi,
        "margin": margin,
        "sbc_margin": sbc_margin,
        "h_min": float(np.min(h)),
        "h_max": float(np.max(h)),
        "sum_h": float(np.sum(h)),
    }


def add_case(acc, name, n, edges, side):
    adj = adj_of(n, edges)
    rec = psc50_case(name, n, adj, side)
    if rec is None:
        return
    acc.append(rec)
    if rec["margin"] < -1e-7:
        print("VIOLATION", rec, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    acc = []

    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        add_case(acc, f"two-lane-L{L}", n, edges, side)

    for L, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _ = build_k_lane(L, k, bad)
        adj = adj_of(n, edges)
        assert trifree(n, adj)
        opt, bound, optimal = cpmax(n, edges, 120)
        cut = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        if optimal and cut == opt == bound:
            add_case(acc, f"klane-L{L}-k{k}-g{gap}", n, edges, side)

    if not args.fast:
        for n0 in range(7, 11):
            graphs = subprocess.run([GENG, "-tc", str(n0)], capture_output=True, text=True, check=True).stdout.split()
            for g6 in graphs:
                n, edges = dec(g6)
                adj, cuts = gmins(n, edges)
                for side in cuts:
                    rec = psc50_case(f"cen-{g6}", n, adj, side)
                    if rec is not None:
                        acc.append(rec)
            print(f"census N={n0} done; cases={len(acc)}", flush=True)

        for cyc in (5, 7, 9):
            for t in range(1, 5):
                n, edges = blowup([t] * cyc)
                if n > 28:
                    continue
                adj, cuts = gmins(n, edges)
                for side in cuts[:1]:
                    rec = psc50_case(f"C{cyc}[{t}]", n, adj, side)
                    if rec is not None:
                        acc.append(rec)

        for name, (n, edges) in [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("Myc(Grotzsch)", mycielski(*mycielski(5, Cn(5)))),
            ("M(C7)", mycielski(7, Cn(7))),
        ]:
            adj, cuts = gmins(n, edges)
            for side in cuts[:2]:
                rec = psc50_case(name, n, adj, side)
                if rec is not None:
                    acc.append(rec)

    acc.sort(key=lambda r: r["margin"])
    print("=== PSC-50 scout ===")
    print(f"cases={len(acc)} violations={sum(1 for r in acc if r['margin'] < -1e-7)}")
    for rec in acc[:12]:
        print(
            "%s N=%d m=%d margin=%.9g sbc=%.9g Xi=%.9g lambda=%.9g h=[%.4g,%.4g] sumh=%.9g"
            % (
                rec["name"],
                rec["N"],
                rec["m"],
                rec["margin"],
                rec["sbc_margin"],
                rec["Xi"],
                rec["lambda"],
                rec["h_min"],
                rec["h_max"],
                rec["sum_h"],
            )
        )


if __name__ == "__main__":
    main()
