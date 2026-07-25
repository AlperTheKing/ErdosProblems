"""Decode the known small extremal graphs and test whether they are BLOW-UPS
(i.e. whether their twin-quotient is small).  If yes, the whole large-N search can be
carried out inside the exactly-solvable class 'blow-up of a small triangle-free H'."""
import sys
from itertools import combinations
from h5_core import from_g6, edges_from_adj, maxcut_exhaustive, is_triangle_free, g6

CANDS = ["K?ABBBwerwBw", "K?BD@g]Qvo^?", "L?`DAboUdIF_Bo", "K?ABA`ocdQBo",
         "L??ED@_~?~^_Fw", "L??EDB_~?~^_Fw", "L??EFB_~FwB{Fw", "L??FFB_~?~^_Fw",
         "L?`DAboU`w@{hS"]


def twin_classes(n, adj):
    """Non-adjacent twins: u ~= v iff N(u) == N(v).  Returns list of classes."""
    seen, classes = [None] * n, []
    for v in range(n):
        placed = False
        for c in classes:
            u = c[0]
            if adj[u] == adj[v]:
                c.append(v)
                placed = True
                break
        if not placed:
            classes.append([v])
    return classes


def quotient(n, adj, classes):
    h = len(classes)
    rep = [c[0] for c in classes]
    w = [len(c) for c in classes]
    qadj = [0] * h
    for i in range(h):
        for j in range(i + 1, h):
            if (adj[rep[i]] >> rep[j]) & 1:
                qadj[i] |= 1 << j
                qadj[j] |= 1 << i
    return h, qadj, w


def main():
    for s in CANDS:
        n, adj = from_g6(s)
        m = len(edges_from_adj(n, adj))
        mc, _ = maxcut_exhaustive(n, adj)
        cls = twin_classes(n, adj)
        h, qadj, w = quotient(n, adj, cls)
        degs = sorted(bin(a).count("1") for a in adj)
        print(f"{s}: N={n} m={m} maxcut={mc} bip={m-mc} trifree={is_triangle_free(n,adj)}")
        print(f"   twin-quotient h={h} weights={w} qg6={g6(h,qadj) if h<=62 else ''}")
        print(f"   degrees={degs}")
        # is the quotient itself C5?
        if h == 5:
            qe = edges_from_adj(h, qadj)
            print(f"   quotient edges={qe}")
        print()


if __name__ == "__main__":
    main()
