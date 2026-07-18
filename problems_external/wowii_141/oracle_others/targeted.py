"""Targeted family sweeps for WOWII conjectures (beyond atlas n<=7).

Families:
  A. all nonisomorphic trees n=8..12 (full conjecture set)
  B. all nonisomorphic trees n=13..15 (cheap set w/ tree shortcuts)
  C. sparse random connected graphs n=8..12 (217 focus + cheap set)
  D. dense random graphs n=11..12 (291 focus)
  E. random bipartite + C5 blowups n<=13 (314 focus + cheap set)
"""

import sys
import math
import random
import itertools
from fractions import Fraction

import networkx as nx

from wowii_oracle import (nx_to_adj, graph_key, compute_inv, check_conjectures,
                          popcount, bits, indep_num_mask, residue_of,
                          hh_zero_step, num_triangles_at, total_dom_number,
                          minimal_tds_cards, connected_mask, has_c4_subgraph,
                          count_induced_c4, bfs_ecc, Ls_of, sweep_graphs)

VIOL = []


def report(name, g6, detail):
    VIOL.append((name, g6, detail))
    print(f"VIOLATION conj{name}: {g6} :: {detail}", flush=True)


# ---------------- tree-specific fast checks (n=13..15) ----------------------

def max_linear_forest_edges_tree(G):
    """Max edges of a spanning linear forest of a tree (deg<=2 subgraph)."""
    root = next(iter(G.nodes()))
    # iterative post-order
    parent = {root: None}
    order = [root]
    for u in order:
        for w in G.neighbors(u):
            if w not in parent:
                parent[w] = u
                order.append(w)
    dp0 = {}
    dp1 = {}  # dp1: v reserves one slot for parent edge
    for v in reversed(order):
        ch = [w for w in G.neighbors(v) if parent.get(w) == v]
        base = sum(dp0[c] for c in ch)
        gains = sorted((1 + dp1[c] - dp0[c] for c in ch), reverse=True)
        g0 = base + sum(g for g in gains[:2] if g > 0)
        g1 = base + sum(g for g in gains[:1] if g > 0)
        dp0[v] = g0
        dp1[v] = g1
    return dp0[root]


def check_tree_cheap(G):
    """Cheap exact checks for a tree (n can be 13..15)."""
    n, adj = nx_to_adj(G)
    g6 = graph_key(G)
    deg = [popcount(adj[v]) for v in range(n)]
    leaves = sum(1 for d in deg if d == 1)
    # tree facts: b = forest = treeSize = n ; ipath = diam+1 ; l(v)=deg(v)
    ecc = [max(bfs_ecc(adj, n, v)) for v in range(n)]
    diam, rad = max(ecc), min(ecc)
    sum_ecc = sum(ecc)
    l_avg = Fraction(sum(deg), n)   # neighborhoods independent in a tree
    maxL = max(deg)
    memo = {}
    alpha = indep_num_mask(adj, (1 << n) - 1, memo)
    res = residue_of(deg)
    Ls = leaves if n >= 3 else 2
    bG = n
    forest = n
    treeS = n
    ipath = diam + 1
    ham = (leaves == 2) if n >= 3 else True  # tree has ham path iff path graph
    pcn = n - max_linear_forest_edges_tree(G)
    avg_ecc = Fraction(sum_ecc, n)

    # 2
    if 2 * (l_avg - 1) > Ls:
        report("2", g6, f"l_avg={l_avg}, Ls={Ls}")
    # 19
    if math.floor(Fraction(sum_ecc, n) + maxL) > bG:
        report("19", g6, f"avg_ecc={avg_ecc}, maxL={maxL}, b={bG}")
    # 40
    if -((pcn + bG + 1) // -2) > forest:
        report("40", g6, f"pcn={pcn}, b={bG}, forest={forest}")
    # 59
    if res * bG > forest ** 2:
        report("59", g6, f"residue={res}, b={bG}, forest={forest}")
    # 61
    if res + (-(diam // -3)) > forest:
        report("61", g6, f"residue={res}, diam={diam}, forest={forest}")
    # 100 (complement of a tree with n>=4 is connected unless star; check)
    full = (1 << n) - 1
    cadj = [full & ~adj[v] & ~(1 << v) for v in range(n)]
    if connected_mask(cadj, full):
        S = sum(popcount(cadj[v]) ** 2 for v in range(n))
        rhs = 4 * (alpha - 1) - 2 * maxL
        if rhs >= 0 and S <= rhs * rhs:
            report("100", g6, f"alpha={alpha}, maxL={maxL}, complL2sq={S}")
    # 103
    if avg_ecc == 1:
        if bG < alpha:
            report("103", g6, f"b={bG}, avg_ecc=1, alpha={alpha}")
    else:
        lnv = math.log(avg_ecc.numerator) - math.log(avg_ecc.denominator)
        if bG - alpha < lnv - 1e-9:
            report("103", g6, f"b={bG}, alpha={alpha}, avg_ecc={avg_ecc}")
    # 109
    if (res + 2 * bG) // 3 < alpha:
        report("109", g6, f"alpha={alpha}, residue={res}, b={bG}")
    # 133 (tree is C4-subgraph-free -> exponent 1)
    fl = l_avg.numerator // l_avg.denominator
    if rad + fl > ipath:
        report("133", g6, f"rad={rad}, floor_l={fl}, path={ipath}")
    # 160 (tree: no C4 -> RHS=maxL; maxT=0 anyway)
    if maxL > Ls:
        report("160", g6, f"maxL={maxL}, maxT=0, c4ind=0, Ls={Ls}")
    # 194
    if alpha <= 1 + l_avg and not ham:
        report("194", g6, f"alpha={alpha}, l_avg={l_avg}, ham=False")
    # 198a
    if bG <= 2 + avg_ecc and not ham:
        report("198a", g6, f"b={bG}, avg_ecc={avg_ecc}, ham=False")
    # 200
    c = 1 + l_avg
    ceilc = -((-c.numerator) // c.denominator)
    if treeS == ceilc and not ham:
        report("200", g6, f"tree={treeS}, ceil(1+l_avg)={ceilc}, ham=False")
    # 217
    ind = 1 if res == 2 else 0
    if Ls <= 4 * ind + 2 and not ham:
        report("217", g6, f"Ls={Ls}, residue={res}, ham=False")
    # 291: trivially true for triangle-free (freqMin = n >= gamma_t); skip
    # 314: hyp needs ipath<=4 i.e. diam<=3
    if diam <= 3 and ipath <= 4:
        cards = minimal_tds_cards(n, adj)
        if len(cards) > 1:
            report("314", g6, f"ipath={ipath}, minimalTDScards={sorted(cards)}")
    # 322: tree n>=5 always has a vertex with 2 indep neighbors -> hyp false


# ------------------------------ families ------------------------------------

def run_trees_full(nmin=8, nmax=12):
    cnt = 0
    for n in range(nmin, nmax + 1):
        for G in nx.nonisomorphic_trees(n):
            cnt += 1
            nn, adj = nx_to_adj(G)
            iv = compute_inv(nn, adj, graph_key(G), heavy=True)
            for name, det in check_conjectures(iv):
                report(name, iv.g6, det)
    print(f"[trees {nmin}-{nmax} full] {cnt} trees", flush=True)


def run_trees_cheap(nmin=13, nmax=15):
    cnt = 0
    for n in range(nmin, nmax + 1):
        for G in nx.nonisomorphic_trees(n):
            cnt += 1
            check_tree_cheap(G)
    print(f"[trees {nmin}-{nmax} cheap] {cnt} trees", flush=True)


def run_sparse(count_per_n=400, seed=2171):
    """Sparse connected graphs, 217-focused but full cheap set."""
    rng = random.Random(seed)
    cheap = {"2", "19", "59", "61", "100", "103", "109", "133", "291",
             "314", "322", "217", "160"}
    cnt = 0
    for n in range(8, 13):
        made = 0
        tries = 0
        while made < count_per_n and tries < count_per_n * 80:
            tries += 1
            m = n - 1 + rng.randint(0, 4)
            G = nx.gnm_random_graph(n, m, seed=rng.randrange(1 << 30))
            if not nx.is_connected(G):
                continue
            made += 1
            cnt += 1
            nn, adj = nx_to_adj(G)
            iv = compute_inv(nn, adj, graph_key(G), heavy=False)
            # 217 needs ham: hypothesis first
            ind = 1 if iv.residue == 2 else 0
            need_ham = (iv.Ls <= 4 * ind + 2) or (iv.alpha <= 1 + iv.l_avg) \
                or (iv.b <= 2 + iv.avg_ecc)
            if need_ham:
                from wowii_oracle import ham_ends, path_cover_number
                ends = ham_ends(nn, adj)
                iv.ham = ends[(1 << nn) - 1] != 0
                iv.pcn = path_cover_number(nn, adj, ends)
                for name, det in check_conjectures(iv):
                    report(name, iv.g6, det)
            else:
                for name, det in check_conjectures(iv, which=cheap):
                    report(name, iv.g6, det)
    print(f"[sparse 217-focus] {cnt} graphs", flush=True)


def run_dense_291(count_per_n=1000, seed=2911):
    rng = random.Random(seed)
    cnt = 0
    for n in (11, 12):
        made = 0
        tries = 0
        while made < count_per_n and tries < count_per_n * 40:
            tries += 1
            p = rng.choice([0.45, 0.55, 0.65, 0.75, 0.85])
            G = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
            if not nx.is_connected(G):
                continue
            made += 1
            cnt += 1
            nn, adj = nx_to_adj(G)
            g6 = graph_key(G)
            gt = total_dom_number(nn, adj)
            deg = [popcount(adj[v]) for v in range(nn)]
            k = hh_zero_step(deg)
            tri = [num_triangles_at(adj, v) for v in range(nn)]
            mn = min(tri)
            freq = sum(1 for t in tri if t == mn)
            if gt is not None and gt > k + freq:
                report("291", g6, f"gamma_t={gt}, k={k}, freqMinTri={freq}")
    print(f"[dense 291-focus] {cnt} graphs", flush=True)


def run_bip_314(count=1200, seed=3141):
    rng = random.Random(seed)
    cnt = 0
    graphs = []
    while len(graphs) < count:
        a = rng.randint(2, 7)
        b = rng.randint(2, 7)
        if a + b > 13:
            continue
        p = rng.choice([0.4, 0.55, 0.7, 0.85, 1.0])
        G = nx.bipartite.random_graph(a, b, p, seed=rng.randrange(1 << 30))
        if nx.is_connected(G):
            graphs.append(G)
    # C5 blowups, all size vectors summing <= 13
    for total in range(5, 14):
        for sizes in itertools.combinations_with_replacement(range(1, 10), 5):
            if sum(sizes) != total:
                continue
            for perm in set(itertools.permutations(sizes)):
                G = nx.Graph()
                groups = []
                nid = 0
                for s in perm:
                    groups.append(list(range(nid, nid + s)))
                    nid += s
                for i in range(5):
                    for u in groups[i]:
                        for v in groups[(i + 1) % 5]:
                            G.add_edge(u, v)
                graphs.append(G)
                break  # one representative per multiset is enough up to symmetry-ish
    seen = set()
    for G in graphs:
        g6 = graph_key(nx.convert_node_labels_to_integers(G))
        if g6 in seen:
            continue
        seen.add(g6)
        cnt += 1
        n, adj = nx_to_adj(G)
        tri = [num_triangles_at(adj, v) for v in range(n)]
        if any(tri):
            continue
        # induced path size via subset scan (only needed when triangle-free)
        from wowii_oracle import compute_subset_maxima
        bmax, fmax, tmax, ipath = compute_subset_maxima(n, adj)
        if ipath > 4:
            continue
        cards = minimal_tds_cards(n, adj)
        if len(cards) > 1:
            report("314", g6, f"ipath={ipath}, minimalTDScards={sorted(cards)}")
    print(f"[bip/C5blowup 314-focus] {cnt} triangle-free candidates scanned",
          flush=True)


def main():
    which = sys.argv[1]
    if which == "treesfull":
        run_trees_full()
    elif which == "treescheap":
        run_trees_cheap(13, 14)
    elif which == "sparse":
        run_sparse()
    elif which == "dense291":
        run_dense_291()
    elif which == "bip314":
        run_bip_314()
    if VIOL:
        with open("violations_targeted.txt", "a") as f:
            for name, g6, det in VIOL:
                f.write(f"{name}\t{g6}\t{det}\n")
    print(f"TOTAL VIOLATIONS: {len(VIOL)}")


if __name__ == "__main__":
    main()
