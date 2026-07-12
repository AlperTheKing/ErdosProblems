#!/usr/bin/env python3
"""VERIFY_3 adversarial re-verification of the falsifier_t6 report.

Everything here is written from scratch against the R44-R53 writeup
definitions.  The colleague's JSONs are used ONLY as data sources
(graph6 strings + which atoms were selected + their claimed numbers to
compare against).  All quantities are recomputed independently:
  - own graph6 decoder, own BFS distances, own all-shortest-4-path rows
  - own Hopcroft-Karp for deletion-SDRs and classifier matchings
  - own Gray-code exact brute force for min displayed-cut sigma
  - own Hall-style exact per-edge selection-forcing decision
Scope marker: this is verification arithmetic, not a proof of the wall.
"""

import json
import sys
from itertools import combinations

T6DIR = r"E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"

REPORT_T6_G6 = "T???????????z?t?Z??OwCwBc?Eg?@E?BG??"
REPORT_T5_G6 = "Q??????wE_Bws?s?DCD??@?@???"  # R50 archived hit #264 string


def fail(msg):
    print("VERIFY3-FAIL: " + msg)
    sys.exit(1)


def decode_graph6(s):
    data = [ord(c) - 63 for c in s]
    if any(d < 0 or d > 63 for d in data):
        fail("graph6 out of range")
    n = data[0]
    if n >= 63:
        fail("large graph6 not handled")
    bits = []
    for d in data[1:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    need = n * (n - 1) // 2
    if len(bits) < need:
        fail("graph6 too short")
    adj = [[0] * n for _ in range(n)]
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i][j] = adj[j][i] = 1
                edges.append((i, j))
            idx += 1
    return n, adj, edges


def bfs_dist(adj, n, src):
    dist = [-1] * n
    dist[src] = 0
    q = [src]
    while q:
        nq = []
        for u in q:
            for w in range(n):
                if adj[u][w] and dist[w] < 0:
                    dist[w] = dist[u] + 1
                    nq.append(w)
        q = nq
    return dist


def all_4_paths(adj, n, s, t):
    """All paths s-a-b-c-t of length 4 (vertices distinct)."""
    out = []
    for a in range(n):
        if not adj[s][a]:
            continue
        for b in range(n):
            if not adj[a][b] or b == s:
                continue
            for c in range(n):
                if adj[b][c] and adj[c][t] and c not in (s, a) and t not in (s, a, b):
                    out.append((s, a, b, c, t))
    return out


def hopcroft_karp(left_ids, right_ids, adj_map):
    """Max matching; adj_map: left -> iterable of rights.  Returns size."""
    INF = float("inf")
    pair_l = {u: None for u in left_ids}
    pair_r = {v: None for v in right_ids}
    while True:
        dist = {}
        q = []
        for u in left_ids:
            if pair_l[u] is None:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = INF
        found = False
        qi = 0
        while qi < len(q):
            u = q[qi]
            qi += 1
            for v in adj_map.get(u, ()):
                w = pair_r[v]
                if w is None:
                    found = True
                elif dist[w] == INF:
                    dist[w] = dist[u] + 1
                    q.append(w)
        if not found:
            break

        def dfs(u):
            for v in adj_map.get(u, ()):
                w = pair_r[v]
                if w is None or (dist[w] == dist[u] + 1 and dfs(w)):
                    pair_l[u] = v
                    pair_r[v] = u
                    return True
            dist[u] = INF
            return False

        for u in left_ids:
            if pair_l[u] is None:
                dfs(u)
    return sum(1 for u in left_ids if pair_l[u] is not None), pair_l


def row_edges(row):
    return {tuple(sorted((row[k], row[k + 1]))) for k in range(4)}


class Fixture:
    """Independent reconstruction of one engine hit."""

    def __init__(self, g6, left_n, right_n, t, sel_pairs):
        self.t = t
        self.left_n = left_n
        self.right_n = right_n
        n, adj, edges = decode_graph6(g6)
        if n != left_n + right_n:
            fail(f"order {n} != {left_n}+{right_n}")
        self.n, self.adj, self.edges = n, adj, sorted(edges)
        # bipartite w.r.t. the shore split?
        for (u, w) in self.edges:
            a, b = (u < left_n), (w < left_n)
            if a == b:
                fail(f"edge {u}-{w} inside a shore: not bipartite as labeled")
        # connected?
        if min(bfs_dist(adj, n, 0)) < 0:
            fail("not connected")
        # distances + available atoms in ENGINE enumeration order (L pairs lex, then R)
        self.dist = [bfs_dist(adj, n, v) for v in range(n)]
        self.avail = []
        for shore in (range(left_n), range(left_n, n)):
            vs = list(shore)
            for i, u in enumerate(vs):
                for w in vs[i + 1:]:
                    if self.dist[u][w] == 4:
                        self.avail.append((u, w))
        self.pair_index = {p: i for i, p in enumerate(self.avail)}
        # family
        self.family = []
        for (u, w) in sel_pairs:
            p = (min(u, w), max(u, w))
            if p not in self.pair_index:
                fail(f"selected atom {p} is not an exact-d4 same-shore pair")
            self.family.append(self.pair_index[p])
        self.family = sorted(self.family)
        # rows per family atom (recomputed)
        self.rows = {}
        for i in self.family:
            u, w = self.avail[i]
            rr = all_4_paths(adj, n, u, w)
            if not rr:
                fail(f"atom {self.avail[i]} has no 4-path but dist==4?")
            self.rows[i] = rr
        # footprints
        self.footprint = {
            i: sorted(set().union(*[row_edges(r) for r in self.rows[i]]))
            for i in self.family
        }

    def circuit_axioms(self):
        res = {}
        edge_set = set(self.edges)
        res["edgeCount"] = len(self.edges)
        # multiplicity >= 2 and union = all edges
        mult = {e: 0 for e in self.edges}
        for i in self.family:
            for e in self.footprint[i]:
                mult[e] += 1
        res["minMultiplicity"] = min(mult.values())
        res["unionIsAllEdges"] = all(m > 0 for m in mult.values())
        # full graph triangle-free (support edges + selected bad pairs)
        full = {e for e in edge_set} | {self.avail[i] for i in self.family}
        fadj = [[0] * self.n for _ in range(self.n)]
        for (u, w) in full:
            fadj[u][w] = fadj[w][u] = 1
        tri = 0
        for a in range(self.n):
            for b in range(a + 1, self.n):
                if not fadj[a][b]:
                    continue
                for c in range(b + 1, self.n):
                    if fadj[a][c] and fadj[b][c]:
                        tri += 1
        res["fullTriangleCount"] = tri
        # deletion-SDRs: for each atom, perfect SDR of the rest onto all edges
        edge_id = {e: k for k, e in enumerate(self.edges)}
        ok = True
        for ex in self.family:
            lefts = [i for i in self.family if i != ex]
            amap = {i: [edge_id[e] for e in self.footprint[i]] for i in lefts}
            size, _ = hopcroft_karp(lefts, list(range(len(self.edges))), amap)
            if size != len(self.edges):
                ok = False
                break
        res["deletionSdrAllPass"] = ok
        return res

    def incident(self, owner):
        return [i for i in self.family if owner in self.avail[i]]

    def nonincident(self, owner):
        return [i for i in self.family if owner not in self.avail[i]]

    def neighbours(self, v):
        return sorted(w for w in range(self.n) if self.adj[v][w])

    def steps(self, i, owner):
        st = set()
        for r in self.rows[i]:
            if r[0] == owner:
                st.add(r[1])
            elif r[4] == owner:
                st.add(r[3])
            else:
                fail("incident atom row without owner endpoint")
        return st

    def classifier(self, owner, active):
        t = self.t
        nbrs = self.neighbours(owner)
        inc = self.incident(owner)
        noninc = self.nonincident(owner)
        e_forced = sum(
            1 for i in noninc if all(owner in r for r in self.rows[i])
        )
        ys = [y for y in nbrs if y != active]
        i_step = 0
        amap = {}
        for i in inc:
            st = self.steps(i, owner) - {active}
            if not st:
                i_step += 1
            amap[i] = [y for y in ys if y in st]
        nu_step, _ = hopcroft_karp(ys, inc, {y: [i for i in inc if y in amap[i]] for y in ys})
        d_step = (t - 1) - nu_step
        cmap = {}
        for y in ys:
            opts = []
            for i in noninc:
                if any(owner not in r and active in r and y in r for r in self.rows[i]):
                    opts.append(i)
            cmap[y] = opts
        nu_cov, _ = hopcroft_karp(ys, noninc, cmap)
        d_cov = (t - 1) - nu_cov
        return (e_forced, i_step, d_step, d_cov)

    def witness_table(self, owner, active):
        """(atom, row) options covering each star pair, over family atoms."""
        nbrs = self.neighbours(owner)
        ys = [y for y in nbrs if y != active]
        table = {y: [] for y in ys}
        for i in self.nonincident(owner):
            for r in self.rows[i]:
                if owner in r:
                    continue
                if active in r:
                    for y in ys:
                        if y in r:
                            table[y].append((i, r))
        return table

    # ---- exact profile-consistency machinery (own derivation) ----
    def domains(self, owner, active, banned_edge=None):
        """Row domains under: one active edge (owner,active) unselected;
        non-incident rows avoid owner; optionally all rows avoid banned_edge."""
        act_e = tuple(sorted((owner, active)))
        dom = {}
        for i in self.family:
            opts = []
            inc = owner in self.avail[i]
            for r in self.rows[i]:
                es = row_edges(r)
                if act_e in es:
                    continue
                if (not inc) and (owner in r):
                    continue
                if banned_edge is not None and banned_edge in es:
                    continue
                opts.append(r)
            dom[i] = opts
        return dom

    def profile_feasible(self, owner, active, banned_edge=None):
        """Exact: does a profile-consistent selection exist (all rows chosen,
        r(owner)=t, active edge latent, all (owner,y) selected, all star
        pairs covered by distinct atoms) avoiding banned_edge everywhere?

        Feasibility <=> all domains nonempty AND a Y-saturating step matching
        AND a pair-saturating coverage matching (disjoint atom sets; all other
        atoms are unconstrained within their domain)."""
        t = self.t
        dom = self.domains(owner, active, banned_edge)
        if any(not dom[i] for i in self.family):
            return False
        nbrs = self.neighbours(owner)
        ys = [y for y in nbrs if y != active]
        inc = self.incident(owner)
        if len(inc) != t:
            fail("owner incident count != t")
        # step side: allowed first-steps from rows in domain
        smap = {}
        for y in ys:
            opts = []
            for i in inc:
                sts = set()
                for r in dom[i]:
                    sts.add(r[1] if r[0] == owner else r[3])
                if y in sts:
                    opts.append(i)
            smap[y] = opts
        nu, _ = hopcroft_karp(ys, inc, smap)
        if nu != t - 1:
            return False
        # coverage side
        noninc = self.nonincident(owner)
        cmap = {}
        for y in ys:
            opts = []
            for i in noninc:
                if any(active in r and y in r for r in dom[i]):
                    # rows in dom of nonincident already avoid owner
                    opts.append(i)
            cmap[y] = opts
        nu, _ = hopcroft_karp(ys, noninc, cmap)
        if nu != t - 1:
            return False
        return True

    def build_profile_tuple(self, owner, active):
        """Construct an explicit valid selection and re-verify it directly."""
        t = self.t
        dom = self.domains(owner, active)
        nbrs = self.neighbours(owner)
        ys = [y for y in nbrs if y != active]
        inc = self.incident(owner)
        noninc = self.nonincident(owner)
        smap = {}
        for y in ys:
            smap[y] = [
                i for i in inc
                if any((r[1] if r[0] == owner else r[3]) == y for r in dom[i])
            ]
        nu, pl = hopcroft_karp(ys, inc, smap)
        if nu != t - 1:
            return None
        choice = {}
        for y, i in pl.items():
            for r in dom[i]:
                if (r[1] if r[0] == owner else r[3]) == y:
                    choice[i] = r
                    break
        cmap = {}
        for y in ys:
            cmap[y] = [
                i for i in noninc
                if any(active in r and y in r for r in dom[i])
            ]
        nu, pl2 = hopcroft_karp(ys, noninc, cmap)
        if nu != t - 1:
            return None
        for y, i in pl2.items():
            for r in dom[i]:
                if active in r and y in r:
                    choice[i] = r
                    break
        for i in self.family:
            if i not in choice:
                choice[i] = dom[i][0]
        # direct re-verification
        sel_edges = set()
        for i, r in choice.items():
            sel_edges |= row_edges(r)
        act_e = tuple(sorted((owner, active)))
        assert act_e not in sel_edges, "active edge got selected"
        assert sum(1 for r in choice.values() if owner in r) == t
        for y in ys:
            assert tuple(sorted((owner, y))) in sel_edges
            assert any(
                owner not in r and active in r and y in r
                for i, r in choice.items() if owner not in self.avail[i]
            )
        latent = [e for e in self.edges if e not in sel_edges]
        return choice, sel_edges, latent

    def kappa_of_switch(self, switch):
        s = set(switch)
        bad = sum(1 for i in self.family
                  if (self.avail[i][0] in s) != (self.avail[i][1] in s))
        blue = sum(1 for (u, w) in self.edges if (u in s) != (w in s))
        return bad, blue, bad - blue

    def max_kappa_brute(self):
        """Exact max over all 2^(n-1) switches via Gray code."""
        n = self.n
        pairs = [self.avail[i] for i in self.family]
        blues = self.edges
        pin = [[] for _ in range(n)]   # (pair kind: +1 bad, -1 blue, idx)
        items = []
        for (u, w) in pairs:
            items.append((u, w, 1))
        for (u, w) in blues:
            items.append((u, w, -1))
        for k, (u, w, sgn) in enumerate(items):
            pin[u].append(k)
            pin[w].append(k)
        weight = [sgn for (_, _, sgn) in items]
        crossing = [0] * len(items)
        cur = 0
        best = 0
        best_switch = frozenset()
        cur_set = 0  # bitmask over vertices 1..n-1 (vertex 0 fixed out)
        # Gray over n-1 bits
        m = n - 1
        for g in range(1, 1 << m):
            flip = (g & -g).bit_length() - 1  # bit index flipped
            v = flip + 1
            for k in pin[v]:
                if crossing[k]:
                    cur -= weight[k]
                    crossing[k] = 0
                else:
                    cur += weight[k]
                    crossing[k] = 1
            cur_set ^= (1 << flip)
            if cur > best:
                best = cur
                best_switch = cur_set
        sw = sorted(i + 1 for i in range(m) if (best_switch >> i) & 1)
        return best, sw


def load_hit(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def section_t6_fixture():
    print("=" * 70)
    print("SECTION A: t=6 fixture (claim 3)")
    data = load_hit(T6DIR + r"\t6_cuttight_l12_r9_harvest.json")
    hit = data["hits"][0]
    g6 = hit["graph6"]
    print("graph6 matches report string:", g6 == REPORT_T6_G6)
    sel_pairs = [(a["u"], a["v"]) for a in hit["selectedAtoms"]]
    fx = Fixture(g6, 12, 9, 6, sel_pairs)
    print("order/edges:", fx.n, len(fx.edges), "(expect 21 / 35)")
    print("available atoms:", len(fx.avail), "(expect 41)  selected:", len(fx.family), "(expect 36)")
    # rows match theirs?
    theirs = {}
    for a in hit["selectedAtoms"]:
        p = (min(a["u"], a["v"]), max(a["u"], a["v"]))
        theirs[p] = {tuple(r) for r in a["rows"]}
    rows_match = all(
        {tuple(r) for r in fx.rows[i]} == theirs[fx.avail[i]] for i in fx.family
    )
    print("row DBs identical to artifact (recomputed):", rows_match)
    ax = fx.circuit_axioms()
    print("circuit axioms:", ax)
    inc0, inc1 = fx.incident(0), fx.incident(1)
    print("owner0 nbrs:", fx.neighbours(0), " deg:", len(fx.neighbours(0)))
    print("owner1 nbrs:", fx.neighbours(1), " deg:", len(fx.neighbours(1)))
    print("Inc(0):", len(inc0), " Inc(1):", len(inc1), "(expect 6/6)")
    # live atom {2,3} rooted rows through x=12,y=13
    la = fx.pair_index.get((2, 3))
    live_ok = la in fx.family and (2, 12, 0, 13, 3) in [tuple(r) for r in fx.rows[la]] \
        and (2, 12, 1, 13, 3) in [tuple(r) for r in fx.rows[la]]
    print("live middle-swap rows (2,12,0,13,3)/(2,12,1,13,3) present:", live_ok)
    owner, active = 0, 20
    vec = fx.classifier(owner, active)
    print("classifier vector at (0,20):", vec, "(expect (0,0,0,0))")
    print("deg(x0=20):", len(fx.neighbours(20)), " nbrs:", fx.neighbours(20), "(expect 3, {0,1,4})")
    # witness table
    wt = fx.witness_table(owner, active)
    print("--- witness table (atom index by engine order; rows) ---")
    for y in sorted(wt):
        opts = [(i, r) for (i, r) in wt[y]]
        print(f"pair {{20,{y}}}:")
        for i, r in opts:
            print(f"   atom {i} {fx.avail[i]}  row {r}  uses(1,20)={(1,20) in row_edges(r)}  uses(4,20)={(4,20) in row_edges(r)}")
    # one row covers at most one pair?
    max_pairs_per_row = 0
    for i in fx.nonincident(owner):
        for r in fx.rows[i]:
            if owner in r or active not in r:
                continue
            c = sum(1 for y in wt if y in r)
            max_pairs_per_row = max(max_pairs_per_row, c)
    print("max star pairs covered by a single row:", max_pairs_per_row, "(R48 parity claim: <=1)")
    # E1: some pair with ALL witnesses using (1,20)?
    e1_pairs = [y for y in wt if wt[y] and all((1, 20) in row_edges(r) for _, r in wt[y])]
    print("pairs whose EVERY witness uses (1,20):", e1_pairs)
    e2_all = [y for y in wt if wt[y] and all((4, 20) in row_edges(r) for _, r in wt[y])]
    print("pairs whose EVERY witness uses (4,20):", e2_all, "(expect none -> (4,20) not singleton-forced)")
    # fibers: which x0-neighbours appear as x0's row-neighbour across witnesses
    fibers = {}
    for y in wt:
        f = set()
        for i, r in wt[y]:
            k = r.index(20)
            if k > 0:
                f.add(r[k - 1])
            if k < 4:
                f.add(r[k + 1])
        fibers[y] = sorted(f - {0})
    print("fibers (x0 row-neighbours over witnesses):", fibers)
    # per-edge forcing landscape
    forced, latent_ok = [], []
    for e in fx.edges:
        if fx.profile_feasible(owner, active, banned_edge=e):
            latent_ok.append(e)
        else:
            forced.append(e)
    print("forced count:", len(forced), " latent-possible count:", len(latent_ok))
    print("latent-possible edges:", latent_ok)
    touch20 = [e for e in latent_ok if 20 in e and e != (0, 20)]
    print("latent-possible edges touching x0 (other than active (0,20)):", touch20)
    print("(1,20) forced:", (1, 20) in forced, "  (4,20) forced:", (4, 20) in forced)
    # existence of a full valid profile tuple + explicit construction
    print("profile-consistent selection exists:", fx.profile_feasible(owner, active))
    built = fx.build_profile_tuple(owner, active)
    print("explicit tuple constructed and re-verified:", built is not None)
    if built is not None:
        choice, sel_edges, latent = built
        # active component of x0 in latent graph minus owner
        ladj = {}
        for (u, w) in latent:
            ladj.setdefault(u, set()).add(w)
            ladj.setdefault(w, set()).add(u)
        comp = {active}
        stack = [active]
        while stack:
            u = stack.pop()
            for w in ladj.get(u, ()):
                if w != owner and w not in comp:
                    comp.add(w)
                    stack.append(w)
        print("tail of x0 in this tuple:", sorted(comp), "(expect {20})")
    # vacuity theorem check
    vac = ((1, 20) in forced) and ((4, 20) in forced) and fx.neighbours(20) == [0, 1, 4]
    print("VACUITY-CERTIFICATE HOLDS ((1,20),(4,20) forced + deg(x0)=3):", vac)
    # sigma brute + double-star kappa
    kmax, sw = fx.max_kappa_brute()
    print("max kappa over all switches (Gray 2^20):", kmax, " -> min sigma:", -kmax, "(expect -32)")
    sstar = sorted({0, 1} | set(fx.neighbours(0)) | set(fx.neighbours(1)))
    bad, blue, kap = fx.kappa_of_switch(sstar)
    print("S* =", sstar, " badCross:", bad, " blueCross(outward):", blue, " kappa:", kap,
          "(expect 22 / 12 / 10; cut-tight needs outward>=12)")
    return fx


def section_t5_264():
    print("=" * 70)
    print("SECTION B: t=5 hit #264 replay (claim 1)")
    data = load_hit(T6DIR + r"\t5_parity_l9_r9.json")
    hit = data["hits"][0]
    g6 = hit["graph6"]
    print("graph6 == report string:", g6 == REPORT_T5_G6)
    sel_pairs = [(a["u"], a["v"]) for a in hit["selectedAtoms"]]
    fx = Fixture(g6, 9, 9, 5, sel_pairs)
    print("order/edges:", fx.n, len(fx.edges), "(expect 18 / 24)")
    print("available atoms:", len(fx.avail), " selected:", len(fx.family), "(expect 25 selected)")
    ax = fx.circuit_axioms()
    print("circuit axioms:", ax)
    print("owner0 nbrs:", fx.neighbours(0), " Inc(0):", len(fx.incident(0)))
    print("owner1 nbrs:", fx.neighbours(1), " Inc(1):", len(fx.incident(1)))
    la = fx.pair_index.get((2, 3))
    live_ok = la in fx.family and (2, 9, 0, 10, 3) in [tuple(r) for r in fx.rows[la]] \
        and (2, 9, 1, 10, 3) in [tuple(r) for r in fx.rows[la]]
    print("live middle-swap rows (2,9,0,10,3)/(2,9,1,10,3) present:", live_ok)
    owner, active = 0, 9
    vec = fx.classifier(owner, active)
    print("classifier vector at (0,9):", vec, "(expect (0,0,0,0))")
    print("deg(x0=9):", len(fx.neighbours(9)), " nbrs:", fx.neighbours(9))
    wt = fx.witness_table(owner, active)
    for y in sorted(wt):
        print(f"pair {{9,{y}}} witnesses:")
        for i, r in wt[y]:
            print(f"   atom {i} {fx.avail[i]}  row {r}  uses(1,9)={(1,9) in row_edges(r)}  uses(2,9)={(2,9) in row_edges(r)}")
    all_use_19 = all(all((1, 9) in row_edges(r) for _, r in wt[y]) for y in wt if wt[y])
    print("every coverage witness of every pair uses edge (1,9):", all_use_19)
    w15 = wt.get(15, [])
    print("pair {9,15} witness count:", len(w15),
          " row:", w15[0][1] if len(w15) == 1 else [r for _, r in w15])
    # forcing of blanket edges by my per-edge machinery
    for e in [(1, 9), (2, 9)]:
        print(f"edge {e} selection-forced:", not fx.profile_feasible(owner, active, banned_edge=e))
    built = fx.build_profile_tuple(owner, active)
    print("explicit profile tuple constructed:", built is not None)
    if built is not None:
        choice, sel_edges, latent = built
        ladj = {}
        for (u, w) in latent:
            ladj.setdefault(u, set()).add(w)
            ladj.setdefault(w, set()).add(u)
        comp = {active}
        stack = [active]
        while stack:
            u = stack.pop()
            for w in ladj.get(u, ()):
                if w != owner and w not in comp:
                    comp.add(w)
                    stack.append(w)
        print("tail of x0=9:", sorted(comp), " active component:", sorted({owner} | comp))
        badcap = [fx.avail[i] for i in fx.family
                  if set(fx.avail[i]) <= comp or
                  (owner in fx.avail[i] and (set(fx.avail[i]) - {owner}) <= comp)]
        print("captured bads in this tuple:", badcap)
    kmax, sw = fx.max_kappa_brute()
    print("max kappa (Gray 2^17):", kmax, " -> min sigma:", -kmax, "(expect -21)")
    rep_sw = [4, 5, 6, 7, 8, 11, 14, 16]
    bad, blue, kap = fx.kappa_of_switch(rep_sw)
    print("report/R50 decisive switch", rep_sw, "-> badCross:", bad, " blueCross:", blue,
          " kappa:", kap, "(expect 23 / 2 / 21)")
    return fx


def section_bare13():
    print("=" * 70)
    print("SECTION C: t=6 bare 13+13 control (claim 5)")
    data = load_hit(T6DIR + r"\t6_diag_l13r13_bare.json")
    hit = data["hits"][0]
    sel_pairs = [(a["u"], a["v"]) for a in hit["selectedAtoms"]]
    fx = Fixture(hit["graph6"], 13, 13, 6, sel_pairs)
    print("order/edges:", fx.n, len(fx.edges), "(expect 26 / 35)")
    print("available:", len(fx.avail), " selected:", len(fx.family), "(expect 36)")
    ax = fx.circuit_axioms()
    print("circuit axioms:", ax)
    for owner in (0, 1):
        noninc = fx.nonincident(owner)
        e_forced = sum(1 for i in noninc if all(owner in r for r in fx.rows[i]))
        print(f"owner {owner}: nbrs {fx.neighbours(owner)} Inc {len(fx.incident(owner))} eForced {e_forced}")
        vecs = {}
        for active in fx.neighbours(owner):
            vecs[active] = fx.classifier(owner, active)
        print(f"   per-active vectors: {vecs}")
        print(f"   lexMin: {min(vecs.values())}")
    sstar = sorted({0, 1} | set(fx.neighbours(0)) | set(fx.neighbours(1)))
    bad, blue, kap = fx.kappa_of_switch(sstar)
    print("S*:", sstar, " badCross:", bad, " blueCross:", blue, " kappa:", kap, "(expect 25/8/17)")
    their_sw = [4, 6, 7, 8, 9, 10, 11, 12, 15, 18, 19, 22, 24, 25]
    bad, blue, kap = fx.kappa_of_switch(their_sw)
    print("their minSigmaSwitch kappa:", kap, "(expect 26 -> sigma -26)")
    if "--bare-brute" in sys.argv:
        kmax, sw = fx.max_kappa_brute()
        print("max kappa (Gray 2^25):", kmax, " -> min sigma:", -kmax, "(expect -26)")
    return fx


def section_near18():
    print("=" * 70)
    print("SECTION D: 18-vtx near-candidate kappa(S*) decomposition (claim 4 spot)")
    # R46 section 8 spec, verbatim: L={v,m,a,b0..b4} -> 0..6, R={x0..x4,y0..y4} -> 7..16
    n = 18 - 1  # 17 vertices actually: 7 left + 10 right
    left = {"v": 0, "m": 1, "a": 2}
    for j in range(5):
        left[f"b{j}"] = 3 + j
    right = {}
    for i in range(5):
        right[f"x{i}"] = 8 + i
    for j in range(5):
        right[f"y{j}"] = 13 + j
    # NOTE: R46 says 18-vtx: 8 left? L = {v,m,a,b0..b4} is 8 vertices? v,m,a + 5 b's = 8.
    # Recount: that is 8 left + 10 right = 18. Fix indices:
    left = {"v": 0, "m": 1, "a": 2}
    for j in range(5):
        left[f"b{j}"] = 3 + j  # 3..7
    right = {}
    for i in range(5):
        right[f"x{i}"] = 8 + i  # 8..12
    for j in range(5):
        right[f"y{j}"] = 13 + j  # 13..17
    edges = []
    for i in range(5):
        edges.append((left["v"], right[f"x{i}"]))
        edges.append((left["m"], right[f"x{i}"]))
    for i in range(4):
        edges.append((left["a"], right[f"x{i}"]))
    for j in range(5):
        edges.append((left["a"], right[f"y{j}"]))
        edges.append((left[f"b{j}"], right[f"y{j}"]))
    assert len(edges) == 24, len(edges)
    atoms = []
    for j in range(5):
        atoms.append((left["v"], left[f"b{j}"]))
        atoms.append((left["m"], left[f"b{j}"]))
    for i in range(5):
        for j in range(i + 1, 5):
            atoms.append((left[f"b{i}"], left[f"b{j}"]))
    for j in range(5):
        atoms.append((right["x4"], right[f"y{j}"]))
    assert len(atoms) == 25, len(atoms)
    sstar = {left["v"], left["m"]} | {right[f"x{i}"] for i in range(5)}
    bad = sum(1 for (u, w) in atoms if (u in sstar) != (w in sstar))
    blue = sum(1 for (u, w) in edges if (u in sstar) != (w in sstar))
    owner_bads = sum(1 for (u, w) in atoms
                     if (u in (0, 1) or w in (0, 1)) and ((u in sstar) != (w in sstar)))
    right_bads = bad - owner_bads
    print(f"kappa(S*) = badCross - blueCross = {bad} - {blue} = {bad - blue}")
    print(f"decomposition: ownerBads {owner_bads} + rightBad {right_bads} - outward {blue} = {owner_bads + right_bads - blue}")
    print("(report claims kappa(S*) = 10 + 5 - 4 = 11)")


if __name__ == "__main__":
    section_near18()
    fx6 = section_t6_fixture()
    fx5 = section_t5_264()
    fxb = section_bare13()
    print("=" * 70)
    print("verify3_main done")
