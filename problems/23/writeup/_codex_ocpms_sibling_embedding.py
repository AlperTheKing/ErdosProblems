"""Check whether sibling PMS-5 overloaded rows are equality-atom supergraphs.

This is a structural diagnostic for the L=5-multi / PMS-5 branch.

Claim tested:
  Every overloaded row/cut of the sibling seed I?`FAo]]? is obtained from
  an overloaded row/cut of the equality seed I?BD@g]Qo by a spanning graph
  embedding whose image misses only blue edges of the sibling cut.

If true, the sibling atom may be handled by a monotonicity lemma:
adding blue edges to the equality atom cannot increase the row-overlap
quantity I(P), provided the bad set and distinguished row are preserved.
"""

from collections import deque
from fractions import Fraction as F

from _h import dec, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side


EQ = "I?BD@g]Qo"
SIB = "I?" + chr(96) + "FAo]]?"


def norm(e):
    a, b = e
    return (a, b) if a < b else (b, a)


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def bdist(n, B, src):
    adj = adj_from_edges(n, B)
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


def kcomp(n, M, cyc, seed):
    seen = set(seed)
    changed = True
    while changed:
        changed = False
        for g in M:
            rows = cyc[g]
            if any(seen & set(P) for P in rows):
                before = len(seen)
                for P in rows:
                    seen.update(P)
                changed |= len(seen) != before
    return seen


def overloaded_rows(g6):
    n, E = dec(g6)
    E = {norm(e) for e in E}
    adj = adj_from_edges(n, E)
    rows = []
    for side in gmins(n, E)[1]:
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        if not M:
            continue
        B = {e for e in E if side[e[0]] != side[e[1]]}
        for f in M:
            for P in cyc[f]:
                if sum(T[v] for v in P) <= ell[f] * n:
                    continue
                Pset = set(P)
                I = sum(
                    F(1, len(cyc[g])) * sum(len(Pset & set(Q)) for Q in cyc[g])
                    for g in M
                )
                rows.append(
                    dict(
                        g6=g6,
                        n=n,
                        E=E,
                        side="".join(map(str, side)),
                        side_bits=tuple(side),
                        B={norm(e) for e in B},
                        M={norm(e) for e in M},
                        f=norm(f),
                        P=tuple(P),
                        I=I,
                        C=kcomp(n, M, cyc, Pset),
                    )
                )
    return rows


def subgraph_embeddings(Ea, Eb):
    """All bijections phi with phi(Ea) subset Eb."""
    n = 10
    adjb = adj_from_edges(n, Eb)
    dega = [0] * n
    for a, b in Ea:
        dega[a] += 1
        dega[b] += 1
    cand = {i: [j for j in range(n) if len(adjb[j]) >= dega[i]] for i in range(n)}
    order = sorted(range(n), key=lambda i: (len(cand[i]), -dega[i]))
    out = []
    mp = {}
    used = set()

    def rec(k):
        if k == n:
            out.append(dict(mp))
            return
        i = order[k]
        for j in cand[i]:
            if j in used:
                continue
            ok = True
            for a, b in Ea:
                if i == a and b in mp and norm((j, mp[b])) not in Eb:
                    ok = False
                    break
                if i == b and a in mp and norm((j, mp[a])) not in Eb:
                    ok = False
                    break
            if not ok:
                continue
            mp[i] = j
            used.add(j)
            rec(k + 1)
            used.remove(j)
            del mp[i]

    rec(0)
    return out


def image_edges(edges, mp):
    return {norm((mp[a], mp[b])) for a, b in edges}


def image_path(P, mp):
    return tuple(mp[v] for v in P)


def side_image(side, mp):
    out = ["?"] * len(side)
    for i, b in enumerate(side):
        out[mp[i]] = b
    return "".join(out)


def main():
    eq_rows = overloaded_rows(EQ)
    sib_rows = overloaded_rows(SIB)
    eqE = eq_rows[0]["E"]
    sibE = sib_rows[0]["E"]
    embs = subgraph_embeddings(eqE, sibE)
    print("eq_rows", len(eq_rows), "sib_rows", len(sib_rows), "embeddings", len(embs))
    failures = []
    matches = []
    for sr in sib_rows:
        found = []
        for er in eq_rows:
            for mp in embs:
                if side_image(er["side"], mp) != sr["side"]:
                    continue
                mapped_P = image_path(er["P"], mp)
                if mapped_P != sr["P"] and tuple(reversed(mapped_P)) != sr["P"]:
                    continue
                if image_edges(er["M"], mp) != sr["M"]:
                    continue
                imgE = image_edges(er["E"], mp)
                extra = sr["E"] - imgE
                if not extra:
                    continue
                if not extra <= sr["B"]:
                    continue
                found.append((er, mp, extra))
        if not found:
            failures.append(sr)
        else:
            er, _mp, extra = found[0]
            matches.append((sr, er, extra))
    print("matched", len(matches), "failures", len(failures))
    for sr, er, extra in matches:
        print(
            "MATCH",
            "sib_side", sr["side"],
            "sib_P", sr["P"],
            "sib_I", sr["I"],
            "eq_side", er["side"],
            "eq_P", er["P"],
            "eq_I", er["I"],
            "extra_blue", sorted(extra),
        )
    for sr in failures:
        print("FAIL", sr["side"], sr["P"], sr["M"], sr["I"])
    print("VERDICT", "PASS" if not failures else "FAIL")


if __name__ == "__main__":
    main()
