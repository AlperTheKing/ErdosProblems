r"""F5 ABSTRACT INCIDENCE LIFT (2026-07-08, Fable-5). GPT-Pro reply 4 family 5: search minimal 4-uniform
Hall-deficient cores (|R| = |F|+1 distinct 4-subsets, every proper subset Hall-OK, no private edge) and attempt
the P4 LIFT: realize each abstract support edge c as a concrete cut edge u_c-v_c and each row as a 5-vertex path
x-c1-c2-c3-c4-y (consecutive edges share exactly one endpoint), bad edge x-y on top. The lift is a CSP: per-row
edge ORDERING (4!/2 = 12 up to reversal) + orientation, with global endpoint unification (union-find), simplicity
(no loops, no parallel edges, per-row 5 distinct vertices), then 2-colorability of the cut graph (sides) and
triangle-freeness of the total graph.

OUTCOMES: (a) some core LIFTS -> emit the graph (falsifier candidate: feed through the family pipeline, likely
dies at max-cutness -- WHERE it dies is the data); (b) NO core lifts at |F| = 6 (exhaustive) -> candidate
structural lemma 'minimal Hall-deficient ell=5 support skeletons are not P4-realizable' = a combinatorial heart
for L3 (the |S|<=5 base case is compiled, so violators need |S|>=6, i.e. |F|>=5; |F|=6,|S|=7 is the smallest
regime). Exhaustive |F|=6; sampled |F|=7. Run from problems/23/writeup.
"""
import json
from itertools import combinations, permutations


def minimal_cores(nF):
    """All R (sets of |F|+1 distinct 4-subsets of [nF]) with union = [nF], every proper subset Hall-OK,
    and no private edge. Returns list of tuples of frozensets."""
    edges = list(range(nF))
    quads = [frozenset(q) for q in combinations(edges, 4)]
    out = []
    target = nF + 1
    for R in combinations(quads, target):
        U = frozenset().union(*R)
        if len(U) != nF:
            continue
        # Hall for proper subsets: |T| <= |union(T)| for all T subset R, |T| < |R|
        ok = True
        for t in range(2, target):
            for T in combinations(R, t):
                if len(frozenset().union(*T)) < t:
                    ok = False; break
            if not ok:
                break
        if not ok:
            continue
        # no private edge: every row's edges appear in some other row
        for i, r in enumerate(R):
            others = frozenset().union(*(R[j] for j in range(target) if j != i))
            if not r <= others:
                ok = False; break
        if ok:
            out.append(R)
    return out


class UF:
    def __init__(self, n):
        self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        self.p[ra] = rb
    def snapshot(self):
        return list(self.p)
    def restore(self, s):
        self.p = list(s)


def try_lift(R, nF):
    """DFS over per-row (ordering, orientation) with endpoint unification. Slots: edge c has 2*c, 2*c+1.
    A row ordering (c1..c4) with orientations o1..o4 in {0,1}: path visits
    slot(c1, o1) - slot(c1, 1-o1)=slot(c2,o2) - ... ; unify consecutive shared endpoints.
    Returns (vertex-count, edges, rows_as_paths) or None."""
    nslots = 2 * nF
    rows = [sorted(r) for r in R]
    orders = {}
    for i, r in enumerate(rows):
        os_ = []
        seen = set()
        for perm in permutations(r):
            if (perm[3], perm[2], perm[1], perm[0]) in seen:
                continue
            seen.add(perm)
            os_.append(perm)
        orders[i] = os_
    sol = []

    def simple_ok(uf):
        # per-edge distinct endpoints; no two edges with identical endpoint pair
        pairs = set()
        for c in range(nF):
            a, b = uf.find(2 * c), uf.find(2 * c + 1)
            if a == b:
                return False
            key = (min(a, b), max(a, b))
            if key in pairs:
                return False
            pairs.add(key)
        return True

    def row_path_ok(uf, assignment):
        # each assigned row: 5 distinct vertices
        for (i, perm, ors) in assignment:
            vs = []
            for k in range(4):
                c, o = perm[k], ors[k]
                if k == 0:
                    vs.append(uf.find(2 * c + o))
                vs.append(uf.find(2 * c + (1 - o)))
            if len(set(vs)) != 5:
                return False
        return True

    def dfs(i, uf, assignment):
        if i == len(rows):
            if simple_ok(uf) and row_path_ok(uf, assignment):
                sol.append((uf.snapshot(), list(assignment)))
                return True
            return False
        for perm in orders[i]:
            for ors in (tuple((b >> k) & 1 for k in range(4)) for b in range(16)):
                snap = uf.snapshot()
                # unify consecutive endpoints: right-slot of ck = left-slot of c(k+1)
                for k in range(3):
                    c1, o1 = perm[k], ors[k]
                    c2, o2 = perm[k + 1], ors[k + 1]
                    uf.union(2 * c1 + (1 - o1), 2 * c2 + o2)
                if simple_ok(uf) and row_path_ok(uf, assignment + [(i, perm, ors)]):
                    if dfs(i + 1, uf, assignment + [(i, perm, ors)]):
                        return True
                uf.restore(snap)
        return False

    uf = UF(nslots)
    if dfs(0, uf, []):
        return sol[0]
    return None


def realize(R, nF, lift):
    """Build the concrete graph from a successful lift; check bipartite cut sides + triangle-free."""
    p, assignment = lift
    uf = UF(len(p)); uf.p = list(p)
    verts = sorted(set(uf.find(x) for x in range(2 * nF)))
    vid = {v: i for i, v in enumerate(verts)}
    cutE = []
    for c in range(nF):
        a, b = vid[uf.find(2 * c)], vid[uf.find(2 * c + 1)]
        cutE.append((min(a, b), max(a, b)))
    badE = []
    for (i, perm, ors) in assignment:
        x = vid[uf.find(2 * perm[0] + ors[0])]
        y = vid[uf.find(2 * perm[3] + (1 - ors[3]))]
        badE.append((min(x, y), max(x, y)))
    n = len(verts)
    # 2-color the cut graph
    adjC = [[] for _ in range(n)]
    for a, b in cutE:
        adjC[a].append(b); adjC[b].append(a)
    side = [-1] * n
    from collections import deque
    for s in range(n):
        if side[s] >= 0:
            continue
        side[s] = 0; Q = deque([s])
        while Q:
            u = Q.popleft()
            for w in adjC[u]:
                if side[w] < 0:
                    side[w] = 1 - side[u]; Q.append(w)
                elif side[w] == side[u]:
                    return None, 'cut graph has odd cycle (not 2-colorable)'
    # bad edges must be monochromatic (path length 4 even => automatic, verify)
    for a, b in badE:
        if side[a] != side[b]:
            return None, 'bad edge bichromatic (parity broken)'
    edges = sorted(set(cutE) | set(badE))
    if len(edges) != len(cutE) + len(badE):
        return None, 'bad edge coincides with cut edge'
    adjA = [set() for _ in range(n)]
    for a, b in edges:
        if b in adjA[a]:
            return None, 'parallel'
        adjA[a].add(b); adjA[b].add(a)
    for a in range(n):
        for b in adjA[a]:
            if b > a and (adjA[a] & adjA[b]):
                return None, 'TRIANGLE'
    return dict(n=n, cutE=cutE, badE=badE, side=side), 'ok'


def main():
    print("F5 incidence lift: minimal 4-uniform Hall-deficient cores -> P4 realizability")
    print("=" * 90)
    for nF in (5, 6):
        cores = minimal_cores(nF)
        print("|F|=%d: %d minimal Hall-deficient cores (|R|=%d)" % (nF, len(cores), nF + 1), flush=True)
        lifted = 0
        realized = []
        fails = {}
        for R in cores:
            lift = try_lift(R, nF)
            if lift is None:
                fails['no-lift'] = fails.get('no-lift', 0) + 1
                continue
            lifted += 1
            g, msg = realize(R, nF, lift)
            if g is None:
                fails[msg] = fails.get(msg, 0) + 1
            else:
                realized.append((R, g))
        print("   lifted (path-consistent): %d | realized (simple+bipartite+tri-free): %d | fails: %s"
              % (lifted, len(realized), fails), flush=True)
        for R, g in realized[:5]:
            print("   REALIZED core %s -> n=%d graph; sides ok; FEED TO PIPELINE:" % ([sorted(r) for r in R], g['n']))
            print("     cutE=%s badE=%s" % (g['cutE'], g['badE']))
        if realized:
            json.dump([{'core': [sorted(r) for r in R], 'graph': g} for R, g in realized],
                      open('../../../tmp/claude_f5_realized.json', 'w'), indent=1)
    print("=" * 90)
    print("VERDICT: realized cores exist -> run pipeline on tmp/claude_f5_realized.json; "
          "none realized -> 'Hall-deficient skeletons not P4-realizable (small |F|)' = L3 lemma candidate")


if __name__ == '__main__':
    main()
