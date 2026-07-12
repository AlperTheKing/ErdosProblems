#!/usr/bin/env python3
"""Diagnostics on the verified falsifier: owner census, per-(owner,active) profile +
capture map, switch-demand (maxcut layer) sweep, selected-multiplicity stats.
All exact integer arithmetic."""

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


def main():
    data = json.loads((OUT / "fh_FALSIFIER.json").read_text(encoding="utf-8"))
    support = sorted(e(*x) for x in data["edges"])
    chosen = sorted(e(*p) for p in data["atoms"])
    n, n1 = 18, 9
    adj = [set() for _ in range(n)]
    for a, b in support:
        adj[a].add(b)
        adj[b].add(a)
    badj = [set() for _ in range(n)]
    for a, b in chosen:
        badj[a].add(b)
        badj[b].add(a)
    dist = [bfs(adj, s, n) for s in range(n)]
    rows_of = {p: sorted(four_paths(adj, *p)) for p in chosen}

    print("=== owner census ===")
    for z in range(n):
        print("  z=%2d dM=%d dB=%d %s" % (z, len(adj[z]), len(badj[z]),
              "PROFILE-SHAPED" if len(adj[z]) == 5 and len(badj[z]) == 5 else ""))

    def classifier(owner, x0):
        ys = sorted(adj[owner] - {x0})
        if len(adj[owner]) != 5 or len(badj[owner]) != 5:
            return None
        incident = [p for p in chosen if owner in p]
        noninc = [p for p in chosen if owner not in p]
        e_forced = sum(1 for p in noninc if all(owner in r for r in rows_of[p]))
        stepsets = {}
        empty = 0
        for p in incident:
            s = {r[1] if r[0] == owner else r[-2] for r in rows_of[p]} & set(ys)
            stepsets[p] = s
            if not s:
                empty += 1
        sr, _ = max_matching(4, [[k for k, p in enumerate(incident) if y in stepsets[p]] for y in ys])
        cr, _ = max_matching(4, [[k for k, p in enumerate(noninc)
                                  if any(owner not in r and x0 in r and y in r for r in rows_of[p])]
                                 for y in ys])
        return [e_forced, empty, 4 - sr, 4 - cr]

    def capture(owner, x0):
        vx0 = e(owner, x0)
        ys = sorted(adj[owner] - {x0})
        incident = [p for p in chosen if owner in p]
        noninc = [p for p in chosen if owner not in p]

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

        def feasible(extra):
            forbid = frozenset(extra) | {vx0}
            cands = {}
            for p in chosen:
                cr_ = clean_rows(p, forbid)
                if not cr_:
                    return False
                cands[p] = cr_
            c1, _ = max_matching(4, [[k for k, p in enumerate(incident)
                                      if any(e(owner, y) in re_ for _, re_ in cands[p])] for y in ys])
            if c1 < 4:
                return False
            c2, _ = max_matching(4, [[k for k, p in enumerate(noninc)
                                      if any(x0 in r and y in r for r, _ in cands[p])] for y in ys])
            return c2 == 4

        if not feasible(frozenset()):
            return "profile-unrealizable"
        paths = []

        def rec(path, edges_):
            cur = path[-1]
            if len(path) > 1:
                paths.append((cur, frozenset(edges_), tuple(path)))
            if len(edges_) == 9:
                return
            for nx in adj[cur]:
                if nx == owner or nx in path:
                    continue
                rec(path + [nx], edges_ + [e(cur, nx)])

        rec([x0], [])
        bset = {p[0] if p[1] == owner else p[1] for p in incident}
        for endv, eset, pt in paths:
            if endv in bset and len(pt) >= 4 and feasible(eset):
                return ("ACTIVE-incident", pt)
        by_end = {}
        for endv, eset, pt in paths:
            by_end.setdefault(endv, []).append((eset, pt))
        for p in noninc:
            for ea, pa in by_end.get(p[0], []):
                for eb, pb in by_end.get(p[1], []):
                    u = ea | eb
                    if len(u) <= 9 and feasible(u):
                        return ("ACTIVE-remote", p, pa, pb)
        return "scope-vacuous"

    print("=== per-(owner,active) profile + capture map ===")
    for z in range(n):
        if len(adj[z]) == 5 and len(badj[z]) == 5:
            for x0 in sorted(adj[z]):
                vec = classifier(z, x0)
                cap = capture(z, x0) if vec == [0, 0, 0, 0] else "-"
                print("  owner %d active %d classifier %s capture %s" % (z, x0, vec, cap))

    print("=== switch demand sweep (R47 layer): kappa = badCross - blueCross ===")
    maxk, argmax, poscnt = -10**9, None, 0
    for mask in range(1 << n):
        kb = sum(((mask >> a) ^ (mask >> b)) & 1 for a, b in chosen)
        ks = sum(((mask >> a) ^ (mask >> b)) & 1 for a, b in support)
        k = kb - ks
        if k > 0:
            poscnt += 1
        if k > maxk:
            maxk, argmax = k, mask
    print("  max kappa = %d at S = %s ; positive switches: %d" %
          (maxk, sorted(z for z in range(n) if (argmax >> z) & 1), poscnt))
    print("  (displayed cut maximum iff max kappa <= 0; hits had 20/21)")

    sel = {tuple(sorted((int(k.strip('()').split(',')[0]), int(k.strip('()').split(',')[1])))): tuple(v)
           for k, v in data["rows"].items()}
    used = {}
    for p, r in sel.items():
        for ed in row_edges(r):
            used[ed] = used.get(ed, 0) + 1
    print("=== selected multiplicities (capture selection) ===")
    print("  |S|=%d; top: %s" % (len(used), sorted(used.items(), key=lambda kv: -kv[1])[:6]))


if __name__ == "__main__":
    main()
