"""Classify OC-PMS attachment signatures in uniform equality-atom blowups."""

from collections import Counter, deque
from fractions import Fraction as F

from _satzmu_conn import struct_for_side
from _codex_ocpms_petersen_blow import blow


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


def classify(t):
    n, E, side = blow([t] * 10)
    st = struct_for_side(n, [set() for _ in range(n)], side)
    # struct_for_side expects adjacency, not edge list.
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    st = struct_for_side(n, adj, side)
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    B = [e for e in E if side[e[0]] != side[e[1]]]
    sig_counter = Counter()
    contrib_counter = Counter()
    rows = 0
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
                sigs = tuple(
                    sorted(
                        [
                            endpoint_signature(d0, d4, L, gu),
                            endpoint_signature(d0, d4, L, gv),
                        ],
                        key=str,
                    )
                )
                cg = F(1, len(cyc[g])) * sum(
                    len(Pset & set(Q)) for Q in cyc[g]
                )
                if cg:
                    sig_counter[sigs] += 1
                    contrib_counter[(sigs, cg)] += 1
    print("t", t, "n", n, "m", len(M), "over_rows", rows)
    print("signatures")
    for k, v in sig_counter.most_common(20):
        print(v, k)
    print("contribs")
    for k, v in contrib_counter.most_common(20):
        print(v, k)


def main():
    for t in [1, 2, 3]:
        classify(t)


if __name__ == "__main__":
    main()

