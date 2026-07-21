#!/usr/bin/env python3
"""Symbolic re-derivation of the r=4 hive row system.

Reproduces hive4.build_hive4 line for line but with the boundary values B kept
as formal linear combinations of (l1..l4, m1..m4, n1..n4).  Prints every row as
  normal . h <= rhs(l,m,n)
grouped by normal.  This makes the 'width lemma' a symbolic identity rather than
a sampled one: for each direction d the two opposite groups are listed and the
min of the rhs's is read off directly.
"""
VARS = ["l1", "l2", "l3", "l4", "m1", "m2", "m3", "m4", "n1", "n2", "n3", "n4"]
Z = tuple([0] * 12)

def vec(**kw):
    v = [0] * 12
    for k, c in kw.items():
        v[VARS.index(k)] += c
    return tuple(v)

def add(a, b):
    return tuple(x + y for x, y in zip(a, b))

def neg(a):
    return tuple(-x for x in a)

def fmt(v):
    ts = []
    for c, name in zip(v, VARS):
        if c == 0: continue
        s = ("+" if c > 0 else "-")
        m = "" if abs(c) == 1 else str(abs(c))
        ts.append("%s%s%s" % (s, m, name))
    return "".join(ts) if ts else "0"

r = 4
INTERIOR4 = [(1, 1), (1, 2), (2, 1)]
idx = {v: i for i, v in enumerate(INTERIOR4)}

L = [vec(l1=1), vec(l2=1), vec(l3=1), vec(l4=1)]
M = [vec(m1=1), vec(m2=1), vec(m3=1), vec(m4=1)]
N = [vec(n1=1), vec(n2=1), vec(n3=1), vec(n4=1)]

def ps(P, k):
    out = Z
    for i in range(k):
        out = add(out, P[i])
    return out

B = {}
for y in range(r + 1):
    B[(0, y)] = ps(L, y)
for x in range(r + 1):
    B[(x, r - x)] = add(ps(L, 4), ps(M, x))
for x in range(r + 1):
    B[(x, 0)] = ps(N, x)
B[(0, 0)] = Z

rows = []
def addrow(plus, minus):
    co = [0, 0, 0]
    const = Z
    for v in plus:
        if v in idx: co[idx[v]] -= 1
        else: const = add(const, neg(B[v]))
    for v in minus:
        if v in idx: co[idx[v]] += 1
        else: const = add(const, B[v])
    if co == [0, 0, 0]:
        rows.append(("CHECK", const))
        return
    rows.append((tuple(co), neg(const)))

for x in range(r + 1):
    for y in range(r + 1):
        if x + y <= r - 2:
            addrow([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)])
        if y >= 1 and x + y <= r - 1:
            addrow([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)])
        if x >= 1 and x + y <= r - 1:
            addrow([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)])

from collections import defaultdict
g = defaultdict(list)
for co, rhs in rows:
    g[co].append(rhs)
print("total rows:", len(rows), " distinct normals:", len(g))
for co in sorted(g):
    print(co, "->", [fmt(v) for v in g[co]])

print()
print("=== slab widths  w(d) = min{rhs: +d} + min{rhs: -d}  (as sets of sums) ===")
DIRS = {"e1": (1,0,0), "e2": (0,1,0), "e3": (0,0,1),
        "e2-e1": (-1,1,0), "e3-e1": (-1,0,1), "e3-e2": (0,-1,1)}
for name, d in DIRS.items():
    nd = tuple(-x for x in d)
    plus = g.get(d, []); minus = g.get(nd, [])
    sums = sorted({fmt(add(a, b)) for a in plus for b in minus})
    print("%-6s : +d rhs %s ; -d rhs %s ; pairwise sums %s"
          % (name, [fmt(v) for v in plus], [fmt(v) for v in minus], sums))
