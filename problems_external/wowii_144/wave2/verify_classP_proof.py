#!/usr/bin/env python3
"""Mechanical verification of every internal step of the class-P proof of
Lemma E  (e <= M(K) for pendant-forest graphs).

Class P: G = C_g (g >= 4) + pendant trees T_1..T_k, each attached to a cycle
position rho_j by exactly one edge.  mu_j = |T_j|, D_j = depth (max d(.,K)).

Proof steps checked on each sampled graph (exact arithmetic):
  (S0) exact metric formulas used in the proof
  (S1) same-tree case:      x*, c in same tree  ==>  mu_that_tree >= e + 1
  (S2) c in a tree (h_c>=1, different tree from x*) ==> D_{T_c} >= r + 1
  (S3) c on K:  e = hx + delta0 exactly (delta0 = d_K(m, q_c))
  (S4) c on K:  window = positions sigma with d_K(m,sigma) <= delta0 - 1 are
       all noncentral, the window is an honest arc (2*delta0 - 1 <= g - 1),
       and every window position sigma has a witness tree j with
       d_K(sigma, rho_j) >= r + 1 - D_j                       (TENT)
  (S5) per-tree coverage capacity <= max(0, g - 2r - 1 + 2 D_j) <= 2 D_j
  (S6) x*'s own tree covers NO window position
  (S7) counting: any cover of the window forces  sum D_j >= delta0  over the
       used trees (checked via the per-tree capacities: greedy max coverage)
  (S8) conclusion  M(K) >= e  via F = (Tx if any) + a minimal witness family,
       cross-checked against the exact M(K) of lemma_e_tests
Run: python verify_classP_proof.py   (seed 20260720)
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "wowii_141" / "oracle"))
sys.path.insert(0, str(ROOT.parent / "oracle"))

from invariants import (all_pairs_dist, ecc_of_set, eccentricities, girth,
                        graph_connected, nx_to_bitadj)
from lemma_e_tests import M_of_cycle

SEED = 20260720


def random_classP(rng):
    g = rng.randrange(4, 22)
    G = nx.cycle_graph(g)
    lbl = 0
    trees = []          # (root_pos, set_of_nodes)
    for _ in range(rng.randrange(0, 6)):
        pos = rng.randrange(g)
        size = rng.randrange(1, 8)
        nodes = []
        first = f"t{lbl}"; lbl += 1
        G.add_edge(pos, first)
        nodes.append(first)
        for _ in range(size - 1):
            parent = rng.choice(nodes)
            v = f"t{lbl}"; lbl += 1
            G.add_edge(parent, v)
            nodes.append(v)
        trees.append((pos, nodes))
    return g, G, trees


def main() -> None:
    rng = random.Random(SEED)
    fails = []
    checked = 0
    for trial in range(4000):
        g, G, trees = random_classP(rng)
        # distinct attachment positions may repeat -> merge trees with same pos?
        # (two trees at the same position are two components: still class P)
        # order: cycle positions 0..g-1 first, then tree nodes by name
        names = ([p for p in range(g)] +
                 sorted((u for u in G.nodes() if isinstance(u, str)), key=str))
        idx = {u: i for i, u in enumerate(names)}
        n = len(names)
        adj = [0] * n
        for u, v in G.edges():
            adj[idx[u]] |= 1 << idx[v]
            adj[idx[v]] |= 1 << idx[u]
        if not graph_connected(n, adj):
            continue
        gg = girth(n, adj)
        assert gg == g, (gg, g)
        dist = all_pairs_dist(n, adj)
        ecc_v = eccentricities(n, dist)
        r = min(ecc_v)
        cm = 0
        for v in range(n):
            if ecc_v[v] == r:
                cm |= 1 << v
        # e and a realizer
        e = 0; xs = None
        for v in range(n):
            d = min(dist[v][idx[k]] for k in range(g) ) # not dist to center!
        # recompute properly: distance to center set
        from invariants import dist_to_set
        for v in range(n):
            d = dist_to_set(dist, v, cm)
            if d > e:
                e = d; xs = v
        if e == 0:
            continue
        checked += 1
        kpos = [idx[k] for k in range(g)]        # cycle vertices 0..g-1
        in_k = set(kpos)

        # tree bookkeeping
        tree_of = {}
        tinfo = []                                # (root_pos, node_idx_set)
        for (pos, nodes) in trees:
            nset = {idx[v] for v in nodes}
            for v in nset:
                tree_of[v] = len(tinfo)
            tinfo.append((pos, nset))
        depth = [max(min(dist[v][k] for k in kpos) for v in nset)
                 for (_, nset) in tinfo]
        mu = [len(nset) for (_, nset) in tinfo]

        # x* data
        hx = min(dist[xs][k] for k in kpos)
        m_pos = min(range(g), key=lambda p: dist[xs][idx[p]])
        tx = tree_of.get(xs, None)

        # pick nearest center c
        cverts = [v for v in range(n) if cm >> v & 1]
        c = min(cverts, key=lambda v: dist[xs][v])
        assert dist[xs][c] == e
        hc = min(dist[c][k] for k in kpos)
        tc = tree_of.get(c, None)

        def dk(p, q):
            d0 = abs(p - q) % g
            return min(d0, g - d0)

        if tx is not None and tc is not None and tx == tc:
            if not mu[tx] >= e + 1:
                fails.append(("S1", trial)); continue
            continue
        if hc >= 1:
            if not depth[tc] >= r + 1:
                fails.append(("S2", trial, depth[tc], r)); continue
            if not mu[tc] >= e + 1:
                fails.append(("S2b", trial)); continue
            continue
        # c on K
        qc = min(range(g), key=lambda p: dist[c][idx[p]])
        assert idx[qc] == c
        delta0 = dk(m_pos, qc)
        if e != hx + delta0:
            fails.append(("S3", trial, e, hx, delta0)); continue
        if not (2 * delta0 - 1 <= g - 1):
            fails.append(("S4-arc", trial)); continue
        window = [p for p in range(g) if dk(m_pos, p) <= delta0 - 1]
        if len(window) != max(0, 2 * delta0 - 1):
            fails.append(("S4-len", trial)); continue
        used = []
        ok = True
        for sig in window:
            if ecc_v[idx[sig]] <= r:
                fails.append(("S4-noncentral", trial)); ok = False; break
            wits = [j for j in range(len(tinfo))
                    if dk(sig, tinfo[j][0]) >= r + 1 - depth[j]]
            if not wits:
                fails.append(("S4-tent", trial, sig)); ok = False; break
            if tx is not None and tx in wits:
                fails.append(("S6", trial, sig)); ok = False; break
            used.append(wits)
        if not ok:
            continue
        # S5: capacities
        for j in range(len(tinfo)):
            cov = sum(1 for sig in window
                      if dk(sig, tinfo[j][0]) >= r + 1 - depth[j])
            if cov > max(0, g - 2 * r - 1 + 2 * depth[j]):
                fails.append(("S5", trial, j, cov)); ok = False
        if not ok:
            continue
        # S7: minimal cover mass  (greedy over subsets is fine: few trees)
        best_mass = None
        kk = len(tinfo)
        for sub in range(1 << kk):
            js = [j for j in range(kk) if sub >> j & 1]
            if all(any(j in w for j in js) for w in used):
                mass = sum(depth[j] for j in js)
                if best_mass is None or mass < best_mass:
                    best_mass = mass
        if window and (best_mass is None or best_mass < delta0):
            fails.append(("S7", trial, best_mass, delta0)); continue
        # S8: conclusion vs exact M
        mk = M_of_cycle(n, adj, kpos)
        if mk < e:
            fails.append(("S8", trial, mk, e)); continue
    print("class-P graphs with e>=1 checked:", checked)
    print("failures:", len(fails))
    for f in fails[:20]:
        print("  ", f)


if __name__ == "__main__":
    main()
