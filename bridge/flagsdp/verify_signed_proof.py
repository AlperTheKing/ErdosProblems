#!/usr/bin/env python3
"""AUDIT GPT's signed-graph proof of Erdos #23 Step-2 (chat 6a3b5aba).
Checks the two load-bearing pieces:
 (A) CYCLE-DEGREE INEQUALITY (6): for every odd cycle C (length ell) in a triangle-free graph G on N
     vertices,  sum_{v in C} d_G(v) <= N(ell-1)/2.  [the new combinatorial lemma, used in BOTH proofs]
     Also confirm EQUALITY on C5 inside C5[n] (GPT's tight claim).
 (B) CD <=> MIN-SIGNATURE: for a MAXIMUM cut (X,Y), the bad set M = monochromatic edges is a
     minimum-cardinality signature of the signed graph (G,M): |M| <= |M XOR delta_G(S)| for ALL S.
     (delta_G(S) = edges of G crossing S; M XOR delta is the signature after switching S.)
 (C) K_{2,3} counterexample (Section 2): N=13, |M|=4, all d_B=4, CD holds, congestion-one fails.
"""
import sys, itertools
from collections import deque
import flag_engine as fe

def adjset(N, A):
    return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def odd_cycles(N, adj, maxlen=9):
    """Yield vertex sets of all odd cycles (as ordered tuples, dedup by frozenset+rotation-free) up to maxlen.
    Simple DFS; small N only."""
    seen = set(); out = []
    def dfs(start, u, path, pathset):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                key = frozenset(path)
                if key not in seen:
                    seen.add(key); out.append(list(path))
            elif w not in pathset and w > start and len(path) < maxlen:
                path.append(w); pathset.add(w); dfs(start, w, path, pathset); path.pop(); pathset.discard(w)
    for s in range(N):
        dfs(s, s, [s], {s})
    return out

def checkA(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    worst = -1; viol = 0; cnt = 0
    for (n, A) in states:
        adj = adjset(n, A)
        deg = [len(adj[u]) for u in range(n)]
        for C in odd_cycles(n, adj):
            ell = len(C); s = sum(deg[v] for v in C); rhs = n * (ell - 1) / 2
            cnt += 1
            if s > rhs + 1e-9:
                viol += 1
            worst = max(worst, s - rhs)
    print(f"N={N}: {len(states)} graphs, {cnt} odd cycles. (6) violations: {viol}; max(LHS-RHS)={worst:.1f} (<=0 OK)", flush=True)
    return viol

def c5n(n):
    """C5[n] blow-up: parts P0..P4 (Pi adjacent Pi+-1). N=5n."""
    N = 5 * n; A = [0] * N
    part = lambda v: v // n
    for u in range(N):
        for v in range(u + 1, N):
            if (part(u) - part(v)) % 5 in (1, 4):
                A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

def checkA_tight(n):
    N, A = c5n(n); adj = adjset(N, A); deg = [len(adj[u]) for u in range(N)]
    # a C5 = one vertex per part 0..4
    C = [i * n for i in range(5)]
    # verify it's a 5-cycle
    ok = all((C[(i + 1) % 5] in adj[C[i]]) for i in range(5))
    s = sum(deg[v] for v in C); rhs = N * 4 / 2
    print(f"C5[{n}] (N={N}): a C5 has sum d(v)={s}, N(ell-1)/2={rhs}, EQUALITY: {s == rhs} (is5cyc={ok})", flush=True)

def maxcut_side(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N - 1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; bs = side
    return best, bs

def checkB(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    fails = 0
    for (n, A) in states:
        adj = adjset(n, A); E = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not E:
            continue
        mc, side = maxcut_side(n, adj)
        M = [(u, v) for (u, v) in E if side[u] == side[v]]
        m = len(M)
        # min signature: min over all S of |M XOR delta_G(S)|
        best = m
        for mask in range(1 << (n - 1)):
            S = [(mask >> u) & 1 for u in range(n)]
            cross = sum(1 for (u, v) in E if S[u] != S[v])      # |delta_G(S)|
            # |M XOR delta|: edges in exactly one of M, delta
            sz = 0
            for (u, v) in E:
                inM = (side[u] == side[v]); inD = (S[u] != S[v])
                if inM != inD:
                    sz += 1
            best = min(best, sz)
        if best < m:
            fails += 1
    print(f"N={N}: CD <=> min-signature check over {len(states)} graphs: max-cut M is min signature FAILS: {fails}", flush=True)
    return fails

if __name__ == "__main__":
    print("=== AUDIT GPT signed-graph proof ===", flush=True)
    print("--- (A) cycle-degree inequality (6) ---", flush=True)
    vA = sum(checkA(N) for N in [5, 6, 7, 8])
    for n in [1, 2, 3]:
        checkA_tight(n)
    print("--- (B) CD <=> min-signature (max-cut M is a minimum signature) ---", flush=True)
    vB = sum(checkB(N) for N in [5, 6, 7, 8])
    print(f"SUMMARY: (6) violations={vA}; min-signature failures={vB}", flush=True)
    print("DONE", flush=True)
