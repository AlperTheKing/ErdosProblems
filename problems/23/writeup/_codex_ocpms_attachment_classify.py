"""Classify how bad edges contributing to overloaded OC-PMS rows attach.

This diagnostic is for the OC-PMS route.  The pure five-layer matrix model
only covers bad edges with endpoints in A0 and A4 of the row interval.  The
actual N=10 equality atom has additional bad edges sharing one row endpoint
but with the other endpoint outside the interval.  This script records the
endpoint distance signatures and row-capture contributions of every bad edge
in every overloaded census-N10 row.
"""

import subprocess
from collections import Counter, defaultdict, deque
from fractions import Fraction as F

from _h import dec, GENG, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side


def bdist(n, B, src):
    adj = [set() for _ in range(n)]
    for a, b in B:
        adj[a].add(b)
        adj[b].add(a)
    d = [None] * n
    d[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] is None:
                d[v] = d[u] + 1
                q.append(v)
    return d


def endpoint_signature(d0, d4, L, u):
    a = d0[u]
    b = d4[u]
    if a is None or b is None:
        return ("disc", a, b)
    if a + b == L - 1:
        return ("layer", a)
    return ("off", a, b, a + b - (L - 1))


def main():
    sig_counter = Counter()
    contrib_counter = Counter()
    examples = {}
    rows = 0

    for g6 in subprocess.run(
        [GENG, "-tc", "10"], capture_output=True, text=True
    ).stdout.split():
        n, E = dec(g6)
        adj = [set() for _ in range(n)]
        for a, b in E:
            adj[a].add(b)
            adj[b].add(a)
        try:
            _, cuts = gmins(n, E)
        except Exception:
            continue
        for side in cuts:
            if not Bconn(n, adj, side):
                continue
            st = struct_for_side(n, adj, side)
            if st is None:
                continue
            M, ell, T, cyc = st[0], st[1], st[2], st[4]
            B = [e for e in E if side[e[0]] != side[e[1]]]
            for f in M:
                L = ell[f]
                for P in cyc[f]:
                    if sum(T[v] for v in P) <= L * n:
                        continue
                    rows += 1
                    Pset = set(P)
                    d0 = bdist(n, B, P[0])
                    d4 = bdist(n, B, P[-1])
                    for g in M:
                        gu, gv = g
                        sigs = sorted(
                            [
                                endpoint_signature(d0, d4, L, gu),
                                endpoint_signature(d0, d4, L, gv),
                            ],
                            key=str,
                        )
                        cg = F(1, len(cyc[g])) * sum(
                            len(Pset & set(Q)) for Q in cyc[g]
                        )
                        kind = tuple(sigs)
                        sig_counter[kind] += 1
                        contrib_counter[(kind, cg)] += 1
                        examples.setdefault(
                            (kind, cg),
                            (
                                g6,
                                "".join(map(str, side)),
                                tuple(P),
                                f,
                                g,
                                tuple(sigs),
                                str(cg),
                                [tuple(Q) for Q in cyc[g]],
                            ),
                        )

    print("overloaded rows", rows)
    print("endpoint signature counts")
    for k, v in sig_counter.most_common():
        print(v, k)
    print("signature/contribution counts")
    for k, v in contrib_counter.most_common():
        print(v, k)
    print("examples")
    for k, rec in examples.items():
        print("EX", k, rec)


if __name__ == "__main__":
    main()

