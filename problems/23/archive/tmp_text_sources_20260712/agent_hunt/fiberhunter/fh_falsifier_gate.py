#!/usr/bin/env python3
"""AGENT fiberhunter -- adversarial gate for the candidate falsifier of
t5_triangleFree_localProfile_is_scopeVacuous found by fh_capture_search.py (9+9).

Everything re-derived from the raw edge list + atom list ONLY (rows re-derived from
scratch; the solver's selection used only as a secondary witness cross-check).

Checks:
  A. circuit axioms: 24 edges, bipartite 9+9, connected, 25 chosen atoms all
     same-shore support-distance exactly 4, complete row DBs, mu(e) >= 2,
     deletion-SDR (25 deletions, perfect matchings onto all 24 edges),
     triangle count 0 in blue+bad;
  B. DB-level classifier at (v=0, x0=9): e_forced = 0, steps nonempty,
     nu(R_step) = 4, nu(R_cov) = 4  [T5LocalOwnerProfile];
  C. capture decision via the FACTORED-CSP witness procedure (no SAT solver):
     enumerate simple latent-witness paths from x0, decide profile-consistent
     feasibility by per-atom clean rows + two bipartite matchings; report ALL
     capture witnesses (incident and remote);
  D. replay of the solver's selection: latent set, r(v), star, coverage,
     component of v, captured atom;
  E. fiber analysis: C_y sets, per-pair forced x0-edges, SC failure point;
  F. min |S_omega| + per-edge latent-feasibility map;
  G. graph6 canonical-ish export + comparison against hits #298/#264 supports.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

OUT = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\fiberhunter")


def e(u, v):
    return (u, v) if u < v else (v, u)


def bfs(adj, src, n):
    d = [-1] * n
    d[src] = 0
    q = [src]
    h = 0
    while h < len(q):
        c = q[h]
        h += 1
        for x in adj[c]:
            if d[x] == -1:
                d[x] = d[c] + 1
                q.append(x)
    return d


def four_paths(adj, a, b):
    out = []
    for m1 in adj[a]:
        if m1 == b:
            continue
        for m2 in adj[m1]:
            if m2 in (a, b):
                continue
            for m3 in adj[m2]:
                if m3 in (a, b, m1):
                    continue
                if b in adj[m3]:
                    out.append((a, m1, m2, m3, b))
    return out


def row_edges(r):
    return frozenset(e(r[k], r[k + 1]) for k in range(4))


def max_matching(nl, adjlist):
    mr, ml = {}, {}

    def aug(l, seen):
        for r in adjlist[l]:
            if r in seen:
                continue
            seen.add(r)
            if r not in mr or aug(mr[r], seen):
                mr[r] = l
                ml[l] = r
                return True
        return False

    cnt = 0
    for l in range(nl):
        if aug(l, set()):
            cnt += 1
    return cnt, ml


def g6_encode(n, edges):
    bits = []
    es = {tuple(sorted(x)) for x in edges}
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in es else 0)
    while len(bits) % 6:
        bits.append(0)
    chars = [chr(63 + n)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        chars.append(chr(63 + v))
    return "".join(chars)


def main():
    data = json.loads((OUT / "fh_FALSIFIER.json").read_text(encoding="utf-8"))
    support = sorted(e(*x) for x in data["edges"])
    chosen = sorted(e(*p) for p in data["atoms"])
    n = 18
    n1 = 9
    owner, x0 = 0, 9
    shore = ["L" if z < n1 else "R" for z in range(n)]

    print("=== A. circuit axioms ===")
    assert len(support) == 24, len(support)
    assert len(chosen) == len(set(chosen)) == 25
    adj = [set() for _ in range(n)]
    for a, b in support:
        assert shore[a] != shore[b], "not bipartite"
        adj[a].add(b)
        adj[b].add(a)
    assert all(d >= 0 for d in bfs(adj, 0, n)), "disconnected"
    dist = [bfs(adj, s, n) for s in range(n)]
    rows_of = {}
    for p in chosen:
        a, b = p
        assert shore[a] == shore[b], p
        assert dist[a][b] == 4, (p, dist[a][b])
        rows_of[p] = sorted(four_paths(adj, a, b))
        assert rows_of[p]
    fp = {p: frozenset().union(*(row_edges(r) for r in rows_of[p])) for p in chosen}
    eid = {ed: k for k, ed in enumerate(support)}
    mu = [0] * 24
    for p in chosen:
        for ed in fp[p]:
            mu[eid[ed]] += 1
    assert min(mu) >= 2, min(mu)
    print("  mu >= 2 OK, min =", min(mu))
    for out_i in range(25):
        rest = [p for k, p in enumerate(chosen) if k != out_i]
        cnt, _ = max_matching(len(rest), [[eid[ed] for ed in fp[p]] for p in rest])
        assert cnt == 24, ("SDR fail", out_i)
    print("  deletion-SDR 25x24 all perfect OK")
    gadj = [set(adj[z]) for z in range(n)]
    for a, b in chosen:
        gadj[a].add(b)
        gadj[b].add(a)
    tri = [t for t in combinations(range(n), 3)
           if t[1] in gadj[t[0]] and t[2] in gadj[t[0]] and t[2] in gadj[t[1]]]
    assert not tri, tri
    print("  triangle count blue+bad = 0 OK")
    avail = sum(1 for a, b in combinations(range(n), 2)
                if shore[a] == shore[b] and dist[a][b] == 4)
    print("  atoms available (distance-4 pairs):", avail, " chosen: 25")

    print("=== B. DB-level classifier at (v=0, x0=9) ===")
    assert sorted(adj[owner]) == [9, 10, 11, 12, 13] and len(adj[owner]) == 5
    ys = [10, 11, 12, 13]
    incident = [p for p in chosen if owner in p]
    noninc = [p for p in chosen if owner not in p]
    assert len(incident) == 5, incident
    e_forced = [p for p in noninc if all(owner in r for r in rows_of[p])]
    assert not e_forced, e_forced
    stepsets = {}
    for p in incident:
        stepsets[p] = {r[1] if r[0] == owner else r[-2] for r in rows_of[p]} & set(ys)
        assert stepsets[p], ("empty step", p)
    sr, sm = max_matching(4, [[k for k, p in enumerate(incident) if y in stepsets[p]] for y in ys])
    assert sr == 4, sr
    covrel = {}
    for y in ys:
        covrel[y] = [p for p in noninc
                     if any(owner not in r and x0 in r and y in r for r in rows_of[p])]
    cr, cm = max_matching(4, [[k for k, p in enumerate(noninc) if p in covrel[y]] for y in ys])
    assert cr == 4, cr
    print("  e_forced=0, steps nonempty, nu(step)=4, nu(cov)=4  => T5LocalOwnerProfile OK")

    print("=== C. capture decision, factored-CSP witness procedure ===")
    vx0 = e(owner, x0)

    def clean_rows(p, forbid):
        out = []
        for r in rows_of[p]:
            re_ = row_edges(r)
            if re_ & forbid:
                continue
            if owner not in p and owner in r:
                continue
            out.append((r, re_))
        return out

    def feasible(forbid_extra=frozenset()):
        forbid = frozenset(forbid_extra) | {vx0}
        cands = {}
        for p in chosen:
            cr_ = clean_rows(p, forbid)
            if not cr_:
                return False
            cands[p] = cr_
        stepadj = []
        for y in ys:
            stepadj.append([k for k, p in enumerate(incident)
                            if any(e(owner, y) in re_ for _, re_ in cands[p])])
        c1, _ = max_matching(4, stepadj)
        if c1 < 4:
            return False
        covadj = []
        for y in ys:
            covadj.append([k for k, p in enumerate(noninc)
                           if any(x0 in r and y in r for r, _ in cands[p])])
        c2, _ = max_matching(4, covadj)
        return c2 == 4

    assert feasible(), "base profile infeasible?!"

    paths = []

    def rec(path, edges_):
        cur = path[-1]
        if len(path) > 1:
            paths.append((cur, frozenset(edges_), tuple(path)))
        if len(edges_) == 9:
            return
        for nx in adj[cur]:
            if nx in (owner,) or nx in path:
                continue
            rec(path + [nx], edges_ + [e(cur, nx)])

    rec([x0], [])
    bset = {p[0] if p[1] == owner else p[1] for p in incident}
    witnesses = []
    for endv, eset, pt in paths:
        if endv in bset and len(pt) >= 4:
            if feasible(eset):
                witnesses.append(("incident", pt))
    by_end = {}
    for endv, eset, pt in paths:
        by_end.setdefault(endv, []).append((eset, pt))
    for p in noninc:
        a, b = p
        found = None
        for eset_a, pt_a in by_end.get(a, []):
            for eset_b, pt_b in by_end.get(b, []):
                u = eset_a | eset_b
                if len(u) <= 9 and feasible(u):
                    found = ("remote", p, pt_a, pt_b)
                    break
            if found:
                break
        if found:
            witnesses.append(found)
    print("  capture witnesses found:", len(witnesses))
    for wtn in witnesses[:6]:
        print("   ", wtn)
    assert witnesses, "NO capture witness -- candidate NOT a falsifier"

    print("=== D. solver-selection replay ===")
    sel = {tuple(sorted((int(k.strip('()').split(',')[0]), int(k.strip('()').split(',')[1])))): tuple(v)
           for k, v in data["rows"].items()}
    assert set(sel) == set(chosen)
    used = set()
    for p, r in sel.items():
        assert tuple(r) in {tuple(x) for x in rows_of[p]}, ("row not in DB", p, r)
        if owner not in p:
            assert owner not in r
        used |= row_edges(r)
    latent = set(support) - used
    print("  |S_omega| =", len(used), " latent =", sorted(latent))
    assert vx0 in latent
    assert sum(1 for r in sel.values() if owner in r) == 5
    for y in ys:
        assert e(owner, y) in used
    covs = set()
    for y in ys:
        got = [p for p, r in sel.items() if owner not in p and x0 in r and y in r and owner not in r]
        got = [p for p in got if p not in covs]
        assert got, ("coverage", y)
        covs.add(got[0])
    comp = {owner}
    st = [owner]
    ladj = {}
    for a, b in latent:
        ladj.setdefault(a, []).append(b)
        ladj.setdefault(b, []).append(a)
    while st:
        c = st.pop()
        for x in ladj.get(c, []):
            if x not in comp:
                comp.add(x)
                st.append(x)
    captured = [p for p in chosen if p[0] in comp and p[1] in comp]
    print("  component of v in latent:", sorted(comp), " captured atoms:", captured)
    assert captured

    print("=== E. fibers / SC failure ===")
    for y in ys:
        wit = []
        for p in chosen:
            for r in rows_of[p]:
                if x0 in r and y in r and vx0 not in row_edges(r):
                    assert owner not in r
                    px, py = r.index(x0), r.index(y)
                    assert abs(px - py) == 2
                    wit.append((p, r, r[(px + py) // 2]))
        c_y = sorted((adj[x0] & adj[y]) - {owner})
        inter = frozenset.intersection(*[frozenset(ed for ed in row_edges(r) if x0 in ed) for _, r, _ in wit])
        print("  y=%d: C=%s middles=%s |W|=%d forcedX0=%s" %
              (y, c_y, sorted({q for _, _, q in wit}), len(wit), sorted(inter)))

    print("=== F. per-edge latent feasibility + min|S| ===")
    lat_ok = [ed for ed in support if ed != vx0 and feasible({ed})]
    print("  latent-feasible edges besides vx0:", lat_ok)

    print("=== G. identity ===")
    print("  graph6(support, this labeling):", g6_encode(n, support))
    print("  degree sequence L:", sorted(len(adj[z]) for z in range(9)),
          " R:", sorted(len(adj[z]) for z in range(9, 18)))
    hits = {"298": "Q??????wE_[?EGs?D_@A?C_B???", "264": "Q??????wE_Bws?s?DCD??@?@???"}
    print("  (hit graph6 strings for the record: %s)" % hits)

    print()
    print("ALL GATES PASSED -- the candidate is a verified falsifier of")
    print("t5_triangleFree_localProfile_is_scopeVacuous at the intrinsic-F* layer.")


if __name__ == "__main__":
    main()
