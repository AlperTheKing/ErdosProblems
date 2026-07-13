#!/usr/bin/env python3
"""AGENT fiberhunter -- Script A (v2): fully independent exact reverification of the two
t=5 zero-vector engine hits (#298 R49, #264 R50) + NEW exact measurements.

KEY STRUCTURAL FACT USED (proved here, exact-checked): profile-consistency of a row
selection is FACTORED -- the only inter-atom constraints are
   (ii) star surjection: the 5 incident atoms' first-steps must cover {y1..y4},
   (iii) coverage matching: 4 DISTINCT nonincident atoms with selected rows containing
         {x0,y_i}, v-free,
and everything else is per-atom local (clean row exists; nonincident rows avoid v;
no row uses a forbidden/latent-designated edge).  Hence "is there a profile-consistent
selection with edge-set U latent?" is decidable by two bipartite matchings --
no search.  This turns the engine's per-edge SAT gates into polynomial checks and
gives a complete, solver-free capture decision:

  capture at atom g  <=>  some minimal latent witness U (union of simple paths from
  x0 to g's endpoints, avoiding v, |U| <= 9) keeps the factored CSP feasible with
  U u {vx0} forbidden.

Outputs per hit: axioms, classifier, fibers/SC, supersaturation audit, per-edge
latent-feasibility map, capture verdict (exact), min |S_omega| (exact B&B).
Integer arithmetic only; own code end-to-end.
"""

from __future__ import annotations

import json
import sys
import time
from itertools import combinations
from pathlib import Path

BASE = Path(r"E:\Projects\ErdosProblems\tmp\fanout\r42_graph_specific_exclusion")
OUT = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\fiberhunter")

HITS = {
    "298": BASE / "t5_classifier_v_l9_r9_1000.json",
    "264": BASE / "t5_live_x_classifier_v_l9_r9_5000.json",
}
GRAPH6 = {
    "298": "Q??????wE_[?EGs?D_@A?C_B???",
    "264": "Q??????wE_Bws?s?DCD??@?@???",
}


def e(u, v):
    return (u, v) if u < v else (v, u)


def g6_decode(s):
    vals = [ord(c) - 63 for c in s]
    assert all(0 <= x < 64 for x in vals)
    n = vals[0]
    assert n < 63
    bits = []
    for x in vals[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


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


class Circuit:
    def __init__(self, n, support, shore, chosen, rows_of, owner, x0):
        self.n, self.support, self.shore = n, support, shore
        self.chosen, self.rows_of, self.owner, self.x0 = chosen, rows_of, owner, x0
        self.adj = [set() for _ in range(n)]
        for a, b in support:
            self.adj[a].add(b)
            self.adj[b].add(a)
        self.ys = sorted(self.adj[owner] - {x0})
        self.vx0 = e(owner, x0)
        self.incident = [p for p in chosen if owner in p]
        self.noninc = [p for p in chosen if owner not in p]

    def clean_rows(self, p, forbid):
        out = []
        for r in self.rows_of[p]:
            re_ = row_edges(r)
            if re_ & forbid:
                continue
            if self.owner not in p and self.owner in r:
                continue
            out.append((r, re_))
        return out

    def feasible(self, forbid_extra=frozenset()):
        """Exact factored feasibility of a profile-consistent selection with
        forbid_extra (plus vx0) latent."""
        forbid = frozenset(forbid_extra) | {self.vx0}
        cands = {}
        for p in self.chosen:
            cr = self.clean_rows(p, forbid)
            if not cr:
                return False
            cands[p] = cr
        # star surjection: distinct incident atoms for the 4 y-first-steps
        stepadj = []
        for y in self.ys:
            row = []
            for k, p in enumerate(self.incident):
                if any(e(self.owner, y) in re_ for _, re_ in cands[p]):
                    row.append(k)
            stepadj.append(row)
        cnt, _ = max_matching(4, stepadj)
        if cnt < 4:
            return False
        # coverage matching: 4 distinct nonincident atoms
        covadj = []
        for y in self.ys:
            row = []
            for k, p in enumerate(self.noninc):
                if any(self.x0 in r and y in r for r, _ in cands[p]):
                    row.append(k)
            covadj.append(row)
        cnt, _ = max_matching(4, covadj)
        return cnt == 4

    def build_selection(self, forbid_extra=frozenset()):
        """Construct an explicit profile-consistent selection (for audit)."""
        forbid = frozenset(forbid_extra) | {self.vx0}
        cands = {p: self.clean_rows(p, forbid) for p in self.chosen}
        if any(not c for c in cands.values()):
            return None
        stepadj = []
        for y in self.ys:
            stepadj.append([k for k, p in enumerate(self.incident)
                            if any(e(self.owner, y) in re_ for _, re_ in cands[p])])
        c1, m1 = max_matching(4, stepadj)
        covadj = []
        for y in self.ys:
            covadj.append([k for k, p in enumerate(self.noninc)
                           if any(self.x0 in r and y in r for r, _ in cands[p])])
        c2, m2 = max_matching(4, covadj)
        if c1 < 4 or c2 < 4:
            return None
        sel = {}
        for yi, ki in m1.items():
            p = self.incident[ki]
            y = self.ys[yi]
            sel[p] = next(r for r, re_ in cands[p] if e(self.owner, y) in re_)
        for yi, ki in m2.items():
            p = self.noninc[ki]
            y = self.ys[yi]
            sel[p] = next(r for r, _ in cands[p] if self.x0 in r and y in r)
        for p in self.chosen:
            if p not in sel:
                sel[p] = cands[p][0][0]
        return sel


def simple_paths_from(adj, src, avoid, maxlen):
    """All simple paths starting at src, avoiding vertex set `avoid`, length<=maxlen.
    Yields (endvertex, edgeset, vertextuple)."""
    out = []

    def rec(path, edges):
        cur = path[-1]
        if len(path) > 1:
            out.append((cur, frozenset(edges), tuple(path)))
        if len(edges) == maxlen:
            return
        for nx in adj[cur]:
            if nx in avoid or nx in path:
                continue
            rec(path + [nx], edges + [e(cur, nx)])

    rec([src], [])
    return out


def analyze(tag, path):
    t_start = time.time()
    rep = {"hit": tag}
    src = json.loads(path.read_text(encoding="utf-8"))
    hit = src["hit"]
    n = src["left"] + src["right"]
    n2, edges = g6_decode(GRAPH6[tag])
    assert n2 == n == 18
    support = sorted(e(*x) for x in edges)
    assert support == sorted(e(*x) for x in hit["supportEdges"])
    assert len(support) == 24
    shore = ["L"] * src["left"] + ["R"] * src["right"]
    assert all(shore[a] != shore[b] for a, b in support)
    adj = [set() for _ in range(n)]
    for a, b in support:
        adj[a].add(b)
        adj[b].add(a)
    assert all(d >= 0 for d in bfs(adj, 0, n))

    dist = [bfs(adj, s, n) for s in range(n)]
    avail = {}
    for a, b in combinations(range(n), 2):
        if shore[a] == shore[b] and dist[a][b] == 4:
            avail[(a, b)] = sorted(four_paths(adj, a, b))
    rep["atomsAvailable"] = len(avail)

    chosen = []
    for rec_ in hit["selectedAtoms"]:
        key = e(rec_["u"], rec_["v"])
        assert key in avail
        assert sorted(map(tuple, rec_["rows"])) == list(map(tuple, avail[key])), "row DB mismatch"
        chosen.append(key)
    assert len(chosen) == len(set(chosen)) == 25
    rows_of = {p: avail[p] for p in chosen}
    fp = {p: frozenset().union(*(row_edges(r) for r in rows_of[p])) for p in chosen}

    gadj = [set(adj[z]) for z in range(n)]
    for a, b in chosen:
        gadj[a].add(b)
        gadj[b].add(a)
    tri = sum(1 for a, b, c in combinations(range(n), 3) if b in gadj[a] and c in gadj[a] and c in gadj[b])
    assert tri == 0
    rep["triangles"] = 0

    eid = {ed: k for k, ed in enumerate(support)}
    mu = [0] * 24
    for p in chosen:
        for ed in fp[p]:
            mu[eid[ed]] += 1
    assert min(mu) >= 2
    rep["muMin"] = min(mu)

    for out_i in range(25):
        rest = [p for k, p in enumerate(chosen) if k != out_i]
        cnt, _ = max_matching(len(rest), [[eid[ed] for ed in fp[p]] for p in rest])
        assert cnt == 24
    rep["deletionSdr"] = "24x25 all perfect"

    owners = {ed: {p for p in chosen if ed in fp[p]} for ed in support}
    worst = []
    for k in (1, 2, 3):
        wk = None
        for sub in combinations(support, k):
            t = set()
            for ed in sub:
                t |= owners[ed]
            slack = len(t) - (k + 1)
            assert slack >= 0, ("supersaturation FAIL", sub)
            if wk is None or slack < wk[0]:
                wk = (slack, sub, len(t))
        worst.append({"k": k, "minOwners": wk[2], "tight": ["%d-%d" % ed for ed in wk[1]], "slack": wk[0]})
    rep["supersaturation"] = worst

    owner = 0
    x0 = hit["selectionMeta"]["localClassifiers"][str(owner)]["activeNeighbour"]
    C = Circuit(n, support, shore, chosen, rows_of, owner, x0)
    ys = C.ys
    rep["owner"], rep["x0"], rep["ys"] = owner, x0, ys

    # classifier
    e_forced = sum(1 for p in C.noninc if all(owner in r for r in rows_of[p]))
    stepadj = []
    for y in ys:
        stepadj.append([k for k, p in enumerate(C.incident)
                        if any((r[1] if r[0] == owner else r[-2]) == y for r in rows_of[p])])
    empty = sum(1 for p in C.incident
                if not ({r[1] if r[0] == owner else r[-2] for r in rows_of[p]} & set(ys)))
    sr, _ = max_matching(4, stepadj)
    covadj = []
    for y in ys:
        covadj.append([k for k, p in enumerate(C.noninc)
                       if any(owner not in r and x0 in r and y in r for r in rows_of[p])])
    cr, _ = max_matching(4, covadj)
    vec = [e_forced, empty, 4 - sr, 4 - cr]
    assert vec == [0, 0, 0, 0], vec
    rep["classifier"] = vec

    # fibers + SC
    fibers = {}
    c_sets = {}
    for y in ys:
        wit = []
        for p in chosen:
            for r in rows_of[p]:
                if x0 in r and y in r and C.vx0 not in row_edges(r):
                    assert owner not in r, ("cooccur", r)
                    px, py = r.index(x0), r.index(y)
                    assert abs(px - py) == 2, ("dist2", r)
                    wit.append((p, r, r[(px + py) // 2]))
        assert wit
        c_i = sorted((adj[x0] & adj[y]) - {owner})
        c_sets[y] = c_i
        xsets = [frozenset(ed for ed in row_edges(r) if x0 in ed) for _, r, _ in wit]
        inter = frozenset.intersection(*xsets)
        fibers[y] = {"witnesses": len(wit), "middles": sorted({q for _, _, q in wit}),
                     "C": c_i, "forced": sorted("%d-%d" % ed for ed in inter)}
    rep["fibers"] = {str(y): fibers[y] for y in ys}
    tails = sorted(z for z in adj[x0] if z != owner)
    sc = {str(z): [y for y in ys if c_sets[y] == [z]] for z in tails}
    rep["scHolds"] = all(v for v in sc.values())
    rep["scCertificate"] = sc

    # base feasibility + replay
    assert C.feasible(), "base profile infeasible?!"
    sel = C.build_selection()
    assert sel is not None
    used = frozenset().union(*(row_edges(r) for r in sel.values()))
    assert C.vx0 not in used
    rep["exampleSelectionLatent"] = sorted("%d-%d" % ed for ed in set(support) - used)

    # per-edge latent feasibility (exact, factored)
    latent_ok = []
    for ed in support:
        if ed == C.vx0:
            latent_ok.append(("%d-%d" % ed, True))
            continue
        latent_ok.append(("%d-%d" % ed, C.feasible({ed})))
    rep["latentFeasible"] = {k: v for k, v in latent_ok}
    x0_edges = [e(x0, z) for z in tails]
    blanket = all(not rep["latentFeasible"]["%d-%d" % ed] for ed in x0_edges)
    rep["tailBlanketProved"] = blanket

    # capture decision (exact): minimal witnesses
    # incident: simple paths x0 -> b (avoid owner) with all edges latent-designated
    cap_witness = None
    paths = simple_paths_from(adj, x0, {owner}, 9)
    n_checked = 0
    bset = {p[0] if p[1] == owner else p[1] for p in C.incident}
    for endv, eset, pt in paths:
        if endv in bset and len(pt) >= 4:  # length >= 3 edges
            n_checked += 1
            if C.feasible(eset):
                cap_witness = ("incident", pt)
                break
    if cap_witness is None:
        # remote: pairs of simple paths from x0 to both endpoints of a nonincident atom
        by_end = {}
        for endv, eset, pt in paths:
            by_end.setdefault(endv, []).append((eset, pt))
        for p in C.noninc:
            a, b = p
            for eset_a, pt_a in by_end.get(a, []):
                for eset_b, pt_b in by_end.get(b, []):
                    u = eset_a | eset_b
                    if len(u) > 9:
                        continue
                    n_checked += 1
                    if C.feasible(u):
                        cap_witness = ("remote", p, pt_a, pt_b)
                        break
                if cap_witness:
                    break
            if cap_witness:
                break
    rep["captureWitness"] = cap_witness
    rep["captureFeasible"] = cap_witness is not None
    rep["captureChecksTried"] = n_checked
    assert cap_witness is None, ("CAPTURE FOUND", cap_witness)

    # min |S_omega| exact B&B (fail-first ordering, greedy warm start)
    forbid = frozenset({C.vx0})
    cands = {p: C.clean_rows(p, forbid) for p in chosen}
    order = sorted(chosen, key=lambda p: len(cands[p]))
    greedy_used = frozenset().union(*(row_edges(r) for r in sel.values()))
    best = [len(greedy_used)]

    # NOTE: min over ALL selections (star/coverage enforced at leaves)
    def rec_min(i, used, cover, star):
        if len(used) >= best[0]:
            return
        if i == len(order):
            if len(star) == 4 and all(cover.values()):
                best[0] = len(used)
            return
        p = order[i]
        for r, re_ in cands[p]:
            cov2, star2 = cover, star
            if owner in p:
                st = re_ & {e(owner, y) for y in ys}
                if st:
                    star2 = star | st
            else:
                hits_y = [y for y in ys if x0 in r and y in r]
                if hits_y:
                    cov2 = dict(cover)
                    for y in hits_y:
                        cov2[y] = True
            rec_min(i + 1, used | re_, cov2, star2)

    rec_min(0, frozenset(), {y: False for y in ys}, frozenset())
    rep["minSelectedSupport"] = best[0]
    rep["maxLatentAnySelection"] = 24 - best[0]
    rep["cycleRank"] = 24 - n + 1
    rep["elapsedSec"] = round(time.time() - t_start, 1)
    return rep


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    for tag, path in HITS.items():
        r = analyze(tag, path)
        reports.append(r)
        print("== hit %s ==" % tag)
        print(" axioms OK: 24 edges, 25/%d atoms, tri=0, mu>=%d, SDR ok" % (r["atomsAvailable"], r["muMin"]))
        print(" classifier %s owner=%d x0=%d" % (r["classifier"], r["owner"], r["x0"]))
        for y, f in sorted(r["fibers"].items()):
            print("  y=%s |W|=%d middles=%s C=%s forced=%s" % (y, f["witnesses"], f["middles"], f["C"], f["forced"]))
        print(" SC certificate: %s (holds=%s)" % (r["scCertificate"], r["scHolds"]))
        print(" supersaturation slacks k=1,2,3: %s (tight ex: %s)" %
              ([w["slack"] for w in r["supersaturation"]], r["supersaturation"][0]["tight"]))
        print(" latent-feasible edges: %s" % sorted(k for k, v in r["latentFeasible"].items() if v))
        print(" tail blanket proved (all x0-edges latent-infeasible): %s" % r["tailBlanketProved"])
        print(" capture: feasible=%s (witness checks tried: %d)" % (r["captureFeasible"], r["captureChecksTried"]))
        print(" min|S_omega|=%d  max latent=%d  rank=%d  (%.1fs)" %
              (r["minSelectedSupport"], r["maxLatentAnySelection"], r["cycleRank"], r["elapsedSec"]))
        print()
    out = OUT / "fh_hits_report.json"
    out.write_text(json.dumps({"schema": "fiberhunter-hits-v2", "reports": reports}, indent=1, sort_keys=True),
                   encoding="utf-8")
    print("written:", out)


if __name__ == "__main__":
    main()
