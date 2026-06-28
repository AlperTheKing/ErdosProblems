"""Exact test of component-support ROWSUM strengthening.

Candidate strengthening:
  For each support-overlap component C of bad edges and each f in C,
      sum_{g in C} O_fg <= | union_{g in C} supp(p_g) |.

Since different support-overlap components have disjoint vertex supports, this
would imply ROWSUM-O. This script only tests the statement exactly.
"""
from collections import defaultdict, deque
from fractions import Fraction as F
import subprocess

from _h import GENG, dec, loads


def blowup_edges(n, edges, t):
    ee = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                ee.append((a * t + i, b * t + j))
    return n * t, ee


def pfs(info):
    out = []
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = defaultdict(int)
        for path in paths:
            for v in path:
                cnt[v] += 1
        out.append({v: F(c, den) for v, c in cnt.items()})
    return out


def dot(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(av * b.get(v, F(0)) for v, av in a.items())


def comps(adj):
    n = len(adj)
    seen = [False] * n
    out = []
    for s in range(n):
        if seen[s]:
            continue
        q = deque([s])
        seen[s] = True
        c = []
        while q:
            u = q.popleft()
            c.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
        out.append(c)
    return out


def check_info(label, info):
    pp = pfs(info)
    m = len(pp)
    if m == 0:
        return None
    O = [[dot(pp[i], pp[j]) for j in range(m)] for i in range(m)]
    adj = [set() for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            if O[i][j] > 0:
                adj[i].add(j)
                adj[j].add(i)
    worst = None
    for comp in comps(adj):
        support = set()
        for j in comp:
            support.update(pp[j])
        cap = F(len(support))
        for i in comp:
            row = sum(O[i][j] for j in comp)
            gap = row - cap
            if worst is None or gap > worst[0]:
                worst = (gap, row, cap, info["M"][i], [info["M"][j] for j in comp], len(support))
    return worst


def run_named():
    cases = [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("J???E?pNu\\?", 2),
    ]
    for g6, t in cases:
        n, e = dec(g6)
        if t != 1:
            n, e = blowup_edges(n, e, t)
        info = loads(n, e)
        w = check_info(f"{g6}[{t}]", info)
        print(f"{g6}[{t}] N={n} worst_gap={w[0]} row={w[1]} cap={w[2]} f={w[3]} support_size={w[5]}")


def run_census(nmax=11, stride=1):
    worst = None
    count = 0
    bad = 0
    for n in range(5, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()[::stride]
        for g6 in out:
            nn, e = dec(g6)
            info = loads(nn, e)
            if info is None:
                continue
            count += 1
            w = check_info(g6, info)
            if w is None:
                continue
            if w[0] > 0:
                bad += 1
            if worst is None or w[0] > worst[0]:
                worst = (w[0], g6, nn, w)
        print(f"N={n} done", flush=True)
    print(f"census count={count} bad={bad} worst={worst}")


if __name__ == "__main__":
    run_named()
    run_census(10)
