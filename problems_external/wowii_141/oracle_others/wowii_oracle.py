"""FC-faithful invariant oracle for WOWII conjectures
2, 19, 40, 59, 61, 100, 103, 109, 133, 160, 194, 198a, 200, 217, 291, 314, 322.

Definitions implemented EXACTLY as in the formal-conjectures Lean sources
(formal-conjectures-w143 @ FormalConjecturesForMathlib/Combinatorics/SimpleGraph/*):

- indepNeighborsCard G v = indepNum of G.induce N(v)                [Independence.lean]
- averageIndepNeighbors  = (sum_v l(v)) / n   (exact Fraction)      [Independence.lean]
- b G  = largest induced bipartite subgraph ORDER                   [Induced.lean]
- largestInducedForestSize = max |S| with G[S] acyclic              [Induced.lean]
- largestInducedTreeSize   = max |S| with G[S] a tree (nonempty)    [LargestInducedTree.lean]
- path G = largest induced path ORDER (isInducedPath lists)         [VertexDistance.lean]
- largestInducedPathSize (conj 314 local def) = same quantity
  (induced tree with all degrees <= 2)                              [GraphConjecture314.lean]
- Ls G = max #leaves over spanning trees (= n - gamma_c for n>=3;
  = 2 for K2)                                                       [SpanningTree.lean]
- residue G = Havel-Hakimi residue, exact algorithm of Residue.lean
- havelHakimiZeroStep = least i>=0 with 0 in s_i or s_i = []        [GraphConjecture291.lean]
- numTrianglesAtVertex v = # 3-cliques containing v                 [Degrees.lean]
- freqMinTriangles = # vertices attaining min_v T(v)                [GraphConjecture291.lean]
- degreeL2Norm G = sqrt(sum deg^2)                                  [Degrees.lean]
- countInducedC4 = number of INDUCED 4-cycles                       [VertexDistance.lean]
- conj133 hasC4 = exists 4-cycle SUBGRAPH (chords allowed)          [GraphConjecture133.lean]
- averageEccentricity = (sum ecc)/n (exact Fraction)                [Eccentricity.lean]
- totalDominationNumber = min |S|, every v has neighbor in S        [Domination.lean]
- IsWellTotallyDominated: all minimal (w.r.t. subset) total
  dominating sets have equal card                                   [WellTotallyDominated.lean]
- pathCoverNumber = min #parts partitioning V, each part carrying
  a (not nec. induced) Hamiltonian path of its induced subgraph     [PathCover.lean]
"""

import sys
import math
import random
import itertools
from fractions import Fraction

import networkx as nx


# ---------------------------------------------------------------- bit helpers

def popcount(x):
    return bin(x).count("1")


def bits(mask):
    v = 0
    while mask:
        if mask & 1:
            yield v
        mask >>= 1
        v += 1


def nx_to_adj(G):
    nodes = sorted(G.nodes())
    idx = {u: i for i, u in enumerate(nodes)}
    n = len(nodes)
    adj = [0] * n
    for u, v in G.edges():
        adj[idx[u]] |= 1 << idx[v]
        adj[idx[v]] |= 1 << idx[u]
    return n, adj


# ------------------------------------------------------------ mask primitives

def connected_mask(adj, mask):
    """Is the induced subgraph on mask connected (and nonempty)?"""
    if mask == 0:
        return False
    start = mask & (-mask)
    seen = start
    frontier = start
    while frontier:
        nxt = 0
        for v in bits(frontier):
            nxt |= adj[v] & mask
        nxt &= ~seen
        seen |= nxt
        frontier = nxt
    return seen == mask


def edges_in(adj, mask):
    e = 0
    for v in bits(mask):
        e += popcount(adj[v] & mask)
    return e // 2


def n_components(adj, mask):
    comps = 0
    rem = mask
    while rem:
        comps += 1
        start = rem & (-rem)
        seen = start
        frontier = start
        while frontier:
            nxt = 0
            for v in bits(frontier):
                nxt |= adj[v] & rem
            nxt &= ~seen
            seen |= nxt
            frontier = nxt
        rem &= ~seen
    return comps


def is_bipartite_mask(adj, mask):
    color = {}
    rem = mask
    while rem:
        s = rem & (-rem)
        v0 = s.bit_length() - 1
        color[v0] = 0
        stack = [v0]
        while stack:
            v = stack.pop()
            for w in bits(adj[v] & mask):
                if w in color:
                    if color[w] == color[v]:
                        return False
                else:
                    color[w] = 1 - color[v]
                    stack.append(w)
        rem &= ~sum(1 << v for v in color) & mask if False else rem
        # remove colored vertices from rem
        colored = 0
        for v in color:
            colored |= 1 << v
        rem = mask & ~colored
    return True


def indep_num_mask(adj, mask, memo):
    """Independence number of induced subgraph on mask."""
    if mask == 0:
        return 0
    if mask in memo:
        return memo[mask]
    # pick vertex of max degree within mask for better branching
    v = mask.bit_length() - 1
    best = 0
    for u in bits(mask):
        d = popcount(adj[u] & mask)
        if d > best:
            best = d
            v = u
    if best == 0:  # all isolated
        r = popcount(mask)
        memo[mask] = r
        return r
    without = indep_num_mask(adj, mask & ~(1 << v), memo)
    with_v = 1 + indep_num_mask(adj, mask & ~(1 << v) & ~adj[v], memo)
    r = max(without, with_v)
    memo[mask] = r
    return r


# ------------------------------------------------------------------ invariants

def bfs_ecc(adj, n, src):
    dist = [-1] * n
    dist[src] = 0
    frontier = [src]
    d = 0
    while frontier:
        d += 1
        nxt = []
        for v in frontier:
            for w in bits(adj[v]):
                if dist[w] < 0:
                    dist[w] = d
                    nxt.append(w)
        frontier = nxt
    return dist


def compute_subset_maxima(n, adj):
    """One pass over all masks: (b, forest, tree, inducedpath) maxima."""
    max_bip = 0
    max_forest = 0
    max_tree = 0
    max_path = 0
    for mask in range(1, 1 << n):
        k = popcount(mask)
        if k <= max_bip and k <= max_forest and k <= max_tree and k <= max_path:
            continue
        e = edges_in(adj, mask)
        # forest iff e == k - #components
        if k > max_forest or k > max_tree or k > max_path:
            c = n_components(adj, mask)
            if e == k - c:
                if k > max_forest:
                    max_forest = k
                if c == 1:
                    if k > max_tree:
                        max_tree = k
                    if k > max_path:
                        maxdeg = max(popcount(adj[v] & mask) for v in bits(mask))
                        if maxdeg <= 2:
                            max_path = k
        if k > max_bip and is_bipartite_mask(adj, mask):
            max_bip = k
    return max_bip, max_forest, max_tree, max_path


def havel_hakimi_step(s):
    """Exact Lean havelHakimiStep: s sorted descending."""
    if not s:
        return []
    d, rest = s[0], s[1:]
    to_dec, remaining = rest[:d], rest[d:]
    dec = [max(x - 1, 0) for x in to_dec]  # Nat subtraction
    out = dec + remaining
    out.sort(reverse=True)
    return out


def residue_of(degs):
    """Exact Lean residueAux on descending-sorted degree list."""
    s = sorted(degs, reverse=True)
    while True:
        if not s:
            return 0
        if s[0] == 0:
            return len(s)
        s = havel_hakimi_step(s)


def hh_zero_step(degs):
    """Least i >= 0 such that iterate i contains 0 or is empty."""
    s = sorted(degs, reverse=True)
    i = 0
    while True:
        if (not s) or (0 in s):
            return i
        s = havel_hakimi_step(s)
        i += 1


def gamma_connected_dom(n, adj):
    """Minimum connected dominating set size (G assumed connected, n>=1)."""
    full = (1 << n) - 1
    best = n
    for mask in range(1, 1 << n):
        k = popcount(mask)
        if k >= best:
            continue
        # dominating: every v not in mask has neighbor in mask
        dom = mask
        for v in bits(mask):
            dom |= adj[v]
        if dom != full:
            continue
        if connected_mask(adj, mask):
            best = k
    return best


def Ls_of(n, adj):
    """Max leaves over spanning trees. Requires connected G."""
    if n == 1:
        return 0
    if n == 2:
        return 2
    return n - gamma_connected_dom(n, adj)


def total_dom_number(n, adj):
    full = (1 << n) - 1
    best = None
    for mask in range(1, 1 << n):
        if best is not None and popcount(mask) >= best:
            continue
        ok = True
        for v in range(n):
            if adj[v] & mask == 0:
                ok = False
                break
        if ok:
            best = popcount(mask)
    return best  # None if no TDS (isolated vertex)


def is_tds(n, adj, mask):
    for v in range(n):
        if adj[v] & mask == 0:
            return False
    return True


def minimal_tds_cards(n, adj):
    """Cards of all minimal total dominating sets."""
    cards = set()
    for mask in range(1, 1 << n):
        if not is_tds(n, adj, mask):
            continue
        minimal = True
        m = mask
        while m:
            v = m & (-m)
            if is_tds(n, adj, mask & ~v):
                minimal = False
                break
            m &= ~v
        if minimal:
            cards.add(popcount(mask))
    return cards


def ham_ends(n, adj):
    """ends[mask] = bitmask of v: exists Ham path of induced-vertex-set mask
    (path in G using exactly the vertices of mask) ending at v."""
    size = 1 << n
    ends = [0] * size
    for v in range(n):
        ends[1 << v] = 1 << v
    for mask in range(1, size):
        e = ends[mask]
        if e == 0:
            continue
        for v in bits(e):
            for w in bits(adj[v] & ~mask):
                ends[mask | (1 << w)] |= 1 << w
    return ends


def path_cover_number(n, adj, ends):
    """Min #parts partitioning V into parts each having a spanning path."""
    full = (1 << n) - 1
    feasible = [ends[m] != 0 for m in range(1 << n)]
    INF = n + 1
    dp = [INF] * (1 << n)
    dp[0] = 0
    for mask in range(1, 1 << n):
        low = mask & (-mask)
        # iterate submasks of mask containing low
        sub = mask
        best = INF
        while sub:
            if sub & low and feasible[sub]:
                cand = dp[mask ^ sub] + 1
                if cand < best:
                    best = cand
            sub = (sub - 1) & mask
        dp[mask] = best
    return dp[full]


def num_triangles_at(adj, v):
    nb = adj[v]
    t = 0
    for u in bits(nb):
        t += popcount(adj[u] & nb)
    return t // 2


def has_c4_subgraph(n, adj):
    """Exists 4 distinct vertices a,b,c,d with ab,bc,cd,da edges (chords ok):
    equivalent to two distinct vertices with >= 2 common neighbors."""
    for a in range(n):
        for c in range(a + 1, n):
            if popcount(adj[a] & adj[c] & ~(1 << a) & ~(1 << c)) >= 2:
                return True
    return False


def count_induced_c4(n, adj):
    cnt = 0
    for q in itertools.combinations(range(n), 4):
        qmask = 0
        for x in q:
            qmask |= 1 << x
        degs = [popcount(adj[x] & qmask) for x in q]
        if degs == [2, 2, 2, 2]:
            # 2-regular on 4 vertices -> C4 (connected check redundant)
            cnt += 1
    return cnt


# --------------------------------------------------------------- full invariant

class Inv:
    __slots__ = ("n", "adj", "g6", "alpha", "lloc", "l_avg", "maxL", "b",
                 "forest", "tree", "ipath", "ecc", "diam", "rad", "avg_ecc",
                 "sum_ecc", "Ls", "residue", "hh_k", "freq_min_tri",
                 "gamma_t", "wtd_cards", "ham", "pcn", "tri_free",
                 "c4sub", "c4ind", "deg", "compl_l2sq")


def compute_inv(n, adj, g6, heavy=True):
    iv = Inv()
    iv.n = n
    iv.adj = adj
    iv.g6 = g6
    memo = {}
    full = (1 << n) - 1
    iv.alpha = indep_num_mask(adj, full, memo)
    iv.lloc = [indep_num_mask(adj, adj[v], memo) for v in range(n)]
    iv.l_avg = Fraction(sum(iv.lloc), n)
    iv.maxL = max(iv.lloc)
    iv.b, iv.forest, iv.tree, iv.ipath = compute_subset_maxima(n, adj)
    iv.ecc = []
    for v in range(n):
        dist = bfs_ecc(adj, n, v)
        iv.ecc.append(max(dist))
    iv.diam = max(iv.ecc)
    iv.rad = min(iv.ecc)
    iv.sum_ecc = sum(iv.ecc)
    iv.avg_ecc = Fraction(iv.sum_ecc, n)
    iv.deg = [popcount(adj[v]) for v in range(n)]
    iv.residue = residue_of(iv.deg)
    iv.hh_k = hh_zero_step(iv.deg)
    tri = [num_triangles_at(adj, v) for v in range(n)]
    mn = min(tri)
    iv.freq_min_tri = sum(1 for t in tri if t == mn)
    iv.tri_free = all(t == 0 for t in tri)
    iv.c4sub = has_c4_subgraph(n, adj)
    iv.c4ind = count_induced_c4(n, adj)
    cadj = [full & ~adj[v] & ~(1 << v) for v in range(n)]
    iv.compl_l2sq = sum(popcount(cadj[v]) ** 2 for v in range(n))
    iv.Ls = Ls_of(n, adj)
    iv.gamma_t = total_dom_number(n, adj)
    iv.wtd_cards = minimal_tds_cards(n, adj)
    if heavy:
        ends = ham_ends(n, adj)
        iv.ham = ends[full] != 0
        iv.pcn = path_cover_number(n, adj, ends)
    else:
        iv.ham = None
        iv.pcn = None
    return iv


def compl_connected(n, adj):
    full = (1 << n) - 1
    cadj = [full & ~adj[v] & ~(1 << v) for v in range(n)]
    return connected_mask(cadj, full)


# --------------------------------------------------------------- conjectures

def check_conjectures(iv, which=None):
    """Returns list of (conj_name, detail) violations. G must be connected, n>=2."""
    out = []
    n = iv.n

    def on(name):
        return which is None or name in which

    # 2: 2*(l_avg - 1) <= Ls
    if on("2"):
        if 2 * (iv.l_avg - 1) > iv.Ls:
            out.append(("2", f"l_avg={iv.l_avg}, Ls={iv.Ls}"))

    # 19: floor(sum_ecc/n + maxL) <= b
    if on("19"):
        lhs = Fraction(iv.sum_ecc, n) + iv.maxL
        if math.floor(lhs) > iv.b:
            out.append(("19", f"avg_ecc={iv.avg_ecc}, maxL={iv.maxL}, b={iv.b}"))

    # 40: ceil((pcn + b + 1)/2) <= forest
    if on("40") and iv.pcn is not None:
        lhs = -((iv.pcn + iv.b + 1) // -2)
        if lhs > iv.forest:
            out.append(("40", f"pcn={iv.pcn}, b={iv.b}, forest={iv.forest}"))

    # 59: ceil(sqrt(residue*b)) <= forest   <=>  violation iff residue*b > forest^2
    if on("59"):
        if iv.residue * iv.b > iv.forest ** 2:
            out.append(("59", f"residue={iv.residue}, b={iv.b}, forest={iv.forest}"))

    # 61: residue + ceil(diam/3) <= forest
    if on("61"):
        if iv.residue + (-(iv.diam // -3)) > iv.forest:
            out.append(("61", f"residue={iv.residue}, diam={iv.diam}, forest={iv.forest}"))

    # 100: (needs Gc connected) alpha <= ceil((maxL + 0.5*sqrt(compl_l2sq))/2)
    # violation iff alpha > ceil(x) iff x <= alpha-1
    # x = maxL/2 + sqrt(S)/4 <= alpha-1  <=>  sqrt(S) <= 4(alpha-1) - 2maxL
    if on("100") and compl_connected(n, iv.adj):
        rhs = 4 * (iv.alpha - 1) - 2 * iv.maxL
        if rhs >= 0 and iv.compl_l2sq <= rhs * rhs:
            out.append(("100", f"alpha={iv.alpha}, maxL={iv.maxL}, "
                               f"complL2sq={iv.compl_l2sq}"))

    # 103: alpha <= floor(b - ln(avg_ecc)); violation iff b - ln(avg_ecc) < alpha
    if on("103"):
        if iv.avg_ecc == 1:
            if iv.b < iv.alpha:
                out.append(("103", f"b={iv.b}, avg_ecc=1, alpha={iv.alpha}"))
        else:
            lnval = math.log(iv.avg_ecc.numerator) - math.log(iv.avg_ecc.denominator)
            gap = iv.b - iv.alpha  # integer >= ?
            if gap < lnval - 1e-9:
                out.append(("103", f"b={iv.b}, alpha={iv.alpha}, avg_ecc={iv.avg_ecc}, "
                                   f"ln={lnval:.6f}"))
            elif abs(gap - lnval) <= 1e-9:
                out.append(("103-NEARTIE", f"b={iv.b}, alpha={iv.alpha}, "
                                           f"avg_ecc={iv.avg_ecc}"))

    # 109: alpha <= floor((residue + 2b)/3)
    if on("109"):
        if (iv.residue + 2 * iv.b) // 3 < iv.alpha:
            out.append(("109", f"alpha={iv.alpha}, residue={iv.residue}, b={iv.b}"))

    # 133: rad + floor(l_avg)^cC4 <= path ; cC4 = 0 if C4-subgraph else 1
    if on("133"):
        fl = iv.l_avg.numerator // iv.l_avg.denominator
        term = 1 if iv.c4sub else fl  # x^0 = 1 when has C4; x^1 = x when C4-free
        if iv.rad + term > iv.ipath:
            out.append(("133", f"rad={iv.rad}, floor_l={fl}, c4sub={iv.c4sub}, "
                               f"path={iv.ipath}"))

    # 160: maxL + maxT*c4ind <= Ls
    if on("160"):
        maxT = max(num_triangles_at(iv.adj, v) for v in range(n))
        if iv.maxL + maxT * iv.c4ind > iv.Ls:
            out.append(("160", f"maxL={iv.maxL}, maxT={maxT}, c4ind={iv.c4ind}, "
                               f"Ls={iv.Ls}"))

    # 194: alpha <= 1 + l_avg -> ham path
    if on("194") and iv.ham is not None:
        if iv.alpha <= 1 + iv.l_avg and not iv.ham:
            out.append(("194", f"alpha={iv.alpha}, l_avg={iv.l_avg}, ham=False"))

    # 198a: b <= 2 + avg_ecc -> ham path
    if on("198a") and iv.ham is not None:
        if iv.b <= 2 + iv.avg_ecc and not iv.ham:
            out.append(("198a", f"b={iv.b}, avg_ecc={iv.avg_ecc}, ham=False"))

    # 200: tree == ceil(1 + l_avg) -> ham path
    if on("200") and iv.ham is not None:
        c = 1 + iv.l_avg
        ceilc = -((-c.numerator) // c.denominator)
        if iv.tree == ceilc and not iv.ham:
            out.append(("200", f"tree={iv.tree}, ceil(1+l_avg)={ceilc}, ham=False"))

    # 217: Ls <= 4*[residue=2] + 2 -> ham path
    if on("217") and iv.ham is not None:
        ind = 1 if iv.residue == 2 else 0
        if iv.Ls <= 4 * ind + 2 and not iv.ham:
            out.append(("217", f"Ls={iv.Ls}, residue={iv.residue}, ham=False"))

    # 291: n>2: gamma_t <= hh_k + freq_min_tri
    if on("291") and n > 2:
        if iv.gamma_t is not None and iv.gamma_t > iv.hh_k + iv.freq_min_tri:
            out.append(("291", f"gamma_t={iv.gamma_t}, k={iv.hh_k}, "
                               f"freqMinTri={iv.freq_min_tri}"))

    # 314: triangle-free & inducedPath <= 4 -> WTD
    if on("314"):
        if iv.tri_free and iv.ipath <= 4 and len(iv.wtd_cards) > 1:
            out.append(("314", f"ipath={iv.ipath}, minimalTDScards={sorted(iv.wtd_cards)}"))

    # 322: n>=5 & all l(v)<=1 -> WTD
    if on("322") and n >= 5:
        if all(x <= 1 for x in iv.lloc) and len(iv.wtd_cards) > 1:
            out.append(("322", f"lloc={iv.lloc}, minimalTDScards={sorted(iv.wtd_cards)}"))

    return out


# ------------------------------------------------------------------- sweeps

def graph_key(G):
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def sweep_graphs(graphs, which=None, heavy=True, label=""):
    violations = []
    count = 0
    for G in graphs:
        n = G.number_of_nodes()
        if n < 2 or not nx.is_connected(G):
            continue
        count += 1
        n_, adj = nx_to_adj(G)
        g6 = graph_key(G)
        iv = compute_inv(n_, adj, g6, heavy=heavy)
        for name, detail in check_conjectures(iv, which=which):
            violations.append((name, g6, detail))
            print(f"VIOLATION conj{name}: {g6} :: {detail}", flush=True)
    print(f"[{label}] swept {count} connected graphs; "
          f"{len(violations)} violations", flush=True)
    return violations, count


def atlas_graphs():
    for G in nx.graph_atlas_g():
        if G.number_of_nodes() >= 2 and nx.is_connected(G):
            yield G


def random_graphs(n, count, seed):
    rng = random.Random(seed)
    out = []
    tries = 0
    while len(out) < count and tries < count * 60:
        tries += 1
        p = rng.choice([0.12, 0.18, 0.25, 0.33, 0.4, 0.5, 0.6, 0.75, 0.85])
        G = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
        if nx.is_connected(G):
            out.append(G)
    return out


def structured_graphs(max_n=12):
    gs = []
    for n in range(3, max_n + 1):
        gs.append(nx.cycle_graph(n))
        gs.append(nx.path_graph(n))
        gs.append(nx.star_graph(n - 1))
        gs.append(nx.complete_graph(n))
        gs.append(nx.wheel_graph(n))
    for a in range(1, 7):
        for bb in range(a, 7):
            if a + bb <= max_n:
                gs.append(nx.complete_bipartite_graph(a, bb))
    # complete multipartite
    for parts in [(1, 1, 2), (1, 2, 2), (2, 2, 2), (1, 1, 3), (2, 2, 3),
                  (3, 3, 3), (1, 2, 3), (2, 3, 4), (1, 1, 1, 2), (2, 2, 2, 2),
                  (1, 2, 2, 3), (3, 3, 4), (2, 4, 4), (1, 4, 4), (2, 2, 4)]:
        if sum(parts) <= max_n:
            gs.append(nx.complete_multipartite_graph(*parts))
    # trees: spiders / double brooms
    for legs in [(2, 2, 2), (1, 2, 3), (3, 3, 3), (2, 2, 2, 2), (1, 1, 2, 2),
                 (2, 3, 3), (1, 1, 1, 1), (2, 2, 3, 3)]:
        G = nx.Graph()
        G.add_node(0)
        nid = 1
        for L in legs:
            prev = 0
            for _ in range(L):
                G.add_edge(prev, nid)
                prev = nid
                nid += 1
        if G.number_of_nodes() <= max_n:
            gs.append(G)
    # double brooms: path with a leaves on one end, b on other
    for plen in range(2, 7):
        for a in range(1, 4):
            for bb in range(1, 4):
                G = nx.path_graph(plen)
                nid = plen
                for _ in range(a):
                    G.add_edge(0, nid); nid += 1
                for _ in range(bb):
                    G.add_edge(plen - 1, nid); nid += 1
                if G.number_of_nodes() <= max_n:
                    gs.append(G)
    # coronas H o K1
    for H in [nx.complete_graph(3), nx.complete_graph(4), nx.cycle_graph(4),
              nx.cycle_graph(5), nx.path_graph(4), nx.complete_graph(5),
              nx.complete_bipartite_graph(2, 3)]:
        G = H.copy()
        m = G.number_of_nodes()
        for v in list(G.nodes()):
            G.add_edge(v, m + v)
        if G.number_of_nodes() <= max_n:
            gs.append(G)
    # named
    gs.append(nx.petersen_graph())
    gs.append(nx.hypercube_graph(3))
    gs.append(nx.octahedral_graph())
    gs.append(nx.cubical_graph())
    gs.append(nx.circular_ladder_graph(4))
    gs.append(nx.circular_ladder_graph(5))
    gs.append(nx.moebius_kantor_graph() if max_n >= 16 else nx.petersen_graph())
    # C5 blowups (triangle-free, for 314)
    for sizes in [(1, 1, 1, 1, 2), (1, 1, 1, 2, 2), (1, 1, 2, 1, 2),
                  (2, 2, 2, 2, 2), (1, 2, 1, 2, 2), (1, 1, 1, 1, 3),
                  (2, 1, 3, 1, 2), (1, 3, 1, 3, 1), (2, 2, 1, 2, 2)]:
        if sum(sizes) <= max_n:
            G = nx.Graph()
            groups = []
            nid = 0
            for s in sizes:
                groups.append(list(range(nid, nid + s)))
                nid += s
            for i in range(5):
                for u in groups[i]:
                    for v in groups[(i + 1) % 5]:
                        G.add_edge(u, v)
            gs.append(G)
    # crown graphs K_{m,m} minus perfect matching (triangle-free)
    for m in range(3, 7):
        if 2 * m <= max_n:
            G = nx.complete_bipartite_graph(m, m)
            for i in range(m):
                G.remove_edge(i, m + i)
            gs.append(G)
    # relabel all to int and dedupe by graph6
    seen = set()
    out = []
    for G in gs:
        G = nx.convert_node_labels_to_integers(G)
        if G.number_of_nodes() < 2 or not nx.is_connected(G):
            continue
        k = graph_key(G)
        if k not in seen:
            seen.add(k)
            out.append(G)
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "atlas"
    all_viol = []
    if mode == "atlas":
        v, c = sweep_graphs(atlas_graphs(), label="atlas n2-7")
        all_viol += v
    elif mode == "structured":
        v, c = sweep_graphs(structured_graphs(max_n=12), label="structured<=12")
        all_viol += v
    elif mode == "random":
        n = int(sys.argv[2])
        count = int(sys.argv[3])
        seed = int(sys.argv[4]) if len(sys.argv) > 4 else 12345
        heavy = n <= 12
        v, c = sweep_graphs(random_graphs(n, count, seed), heavy=heavy,
                            label=f"random n={n} x{count}")
        all_viol += v
    if all_viol:
        with open("violations.txt", "a") as f:
            for name, g6, det in all_viol:
                f.write(f"{name}\t{g6}\t{det}\n")
    print(f"TOTAL VIOLATIONS: {len(all_viol)}")


if __name__ == "__main__":
    main()
