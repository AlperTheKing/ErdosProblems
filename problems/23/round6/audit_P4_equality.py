"""audit_P4_equality — classify the equality configurations (25*ARCBOUND = q^2) found by
audit_P4_exhaust.cpp, and test P4.md's claim that EVERY one is a balanced C5 blow-up.
"""
import sys
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import adj_matrix, normalise, arcbound, psi_bruteforce


def collapse_twins(supp, adj, wt):
    """quotient the support-induced graph by the twin relation (same neighbourhood inside supp)."""
    nbr = {u: frozenset(v for v in supp if v != u and adj[u][v]) for u in supp}
    classes = {}
    for u in supp:
        classes.setdefault(nbr[u], []).append(u)
    keys = list(classes)
    cw = [sum(wt[u] for u in classes[k]) for k in keys]
    # quotient adjacency
    qadj = [[False] * len(keys) for _ in keys]
    for a in range(len(keys)):
        for b in range(len(keys)):
            if a != b:
                qadj[a][b] = adj[classes[keys[a]][0]][classes[keys[b]][0]]
    return keys, classes, cw, qadj


def is_C5(qadj):
    n = len(qadj)
    if n != 5:
        return False
    deg = [sum(r) for r in qadj]
    if deg != [2] * 5:
        return False
    # connected 2-regular on 5 vertices == C5
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in range(5):
            if qadj[u][v] and v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == 5


def classify(path, m):
    adj = adj_matrix(m)
    stats = {}
    notC5 = []
    n = 0
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        w = [int(t) for t in line.split(",")]
        n += 1
        q = sum(w)
        x = normalise(w)
        ab = arcbound(x, adj, m)
        assert ab == F(1, 25), f"claimed equality but ARCBOUND={ab}"
        supp = [i for i in range(m) if w[i]]
        keys, classes, cw, qadj = collapse_twins(supp, adj, w)
        ok = is_C5(qadj) and len(set(cw)) == 1
        stats[len(supp)] = stats.get(len(supp), 0) + 1
        if not ok:
            notC5.append((w, cw, len(keys)))
    print(f"{path}: {n} equality configs; atoms histogram {dict(sorted(stats.items()))}")
    if notC5:
        print(f"  *** {len(notC5)} are NOT balanced C5 blow-ups, e.g. {notC5[0]}")
    else:
        print("  all are balanced C5 blow-ups after twin collapse (P4's classification CONFIRMED)")
    return n, stats, notC5


if __name__ == "__main__":
    for path, m in [("audit_P4_eq_g11_q15.txt", 11), ("audit_P4_eq_g18_q10.txt", 18),
                    ("audit_P4_eq_g17_q10.txt", 17)]:
        try:
            classify(path, m)
        except FileNotFoundError:
            print(f"{path}: missing")
