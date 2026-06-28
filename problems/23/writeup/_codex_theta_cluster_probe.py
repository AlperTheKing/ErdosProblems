"""Codex-only exact probe for bad-edge overlap / theta-star structure.

This is diagnostic only. It avoids numerical KKT optimization and computes:
  * exact O_fg overlap matrix,
  * support-overlap and strong-overlap components on bad edges,
  * theta-star neighborhoods around bad-edge endpoints,
  * how much of each ROWSUM-O row is captured by the best theta-star.

The output is meant to suggest exact-testable lemmas for Claude, not certify
the theorem.
"""
from __future__ import annotations

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


def exact_pfs(info):
    pfs = []
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = defaultdict(int)
        for path in paths:
            for v in path:
                cnt[v] += 1
        pfs.append({v: F(c, den) for v, c in cnt.items()})
    return pfs


def dot(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(av * b.get(v, F(0)) for v, av in a.items())


def components(m, adj):
    seen = [False] * m
    comps = []
    for s in range(m):
        if seen[s]:
            continue
        q = deque([s])
        seen[s] = True
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
        comps.append(sorted(comp))
    return comps


def theta_stars(info, O):
    """Return endpoint-indexed theta-star sets of bad edge indices.

    For an endpoint a, start with all bad edges incident to a. Add any edge h
    overlapping at least two incident star edges.
    """
    M = info["M"]
    by_endpoint = defaultdict(list)
    for i, (a, b) in enumerate(M):
        by_endpoint[a].append(i)
        by_endpoint[b].append(i)
    stars = {}
    for a, inc in by_endpoint.items():
        star = set(inc)
        for h in range(len(M)):
            if h in star:
                continue
            hits = sum(1 for g in inc if O[h][g] > 0)
            if hits >= 2:
                star.add(h)
        stars[a] = sorted(star)
    return stars


def analyze_info(label, info, verbose=False):
    M = info["M"]
    m = len(M)
    if m == 0:
        return None
    pfs = exact_pfs(info)
    O = [[dot(pfs[i], pfs[j]) for j in range(m)] for i in range(m)]
    rows = [sum(row) for row in O]
    support_adj = [set() for _ in range(m)]
    strong_adj = [set() for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            share_endpoint = bool(set(M[i]) & set(M[j]))
            if O[i][j] > 0:
                support_adj[i].add(j)
                support_adj[j].add(i)
            if share_endpoint or O[i][j] >= 1:
                strong_adj[i].add(j)
                strong_adj[j].add(i)
    supp_comps = components(m, support_adj)
    strong_comps = components(m, strong_adj)
    stars = theta_stars(info, O)

    worst = None
    for i in range(m):
        best_cap = F(0)
        best_star = None
        for a, star in stars.items():
            if i not in star:
                continue
            cap = sum(O[i][j] for j in star)
            if cap > best_cap:
                best_cap = cap
                best_star = a
        miss = rows[i] - best_cap
        if worst is None or miss > worst[0]:
            worst = (miss, i, best_star, rows[i], best_cap)

    if verbose:
        print(f"\n{label} N={info['n']} Gamma={info['G']} |M|={m}")
        print(f"  support comps sizes={[len(c) for c in supp_comps]} comps={[[M[i] for i in c] for c in supp_comps]}")
        print(f"  strong comps sizes={[len(c) for c in strong_comps]} comps={[[M[i] for i in c] for c in strong_comps]}")
        print(f"  theta stars={{{', '.join(str(a)+':'+str([M[i] for i in s]) for a,s in stars.items())}}}")
        print(f"  worst theta-star row miss={worst[0]} f={M[worst[1]]} row={worst[3]} cap={worst[4]} star={worst[2]}")
        for i in range(m):
            overlaps = [(M[j], O[i][j]) for j in range(m) if O[i][j]]
            print(f"    row {M[i]} rowsum={rows[i]} overlaps={overlaps}")

    return {
        "label": label,
        "n": info["n"],
        "m": m,
        "support_comp_sizes": sorted(len(c) for c in supp_comps),
        "strong_comp_sizes": sorted(len(c) for c in strong_comps),
        "worst_miss": worst[0],
        "worst_row": worst[3],
        "worst_cap": worst[4],
        "worst_edge": M[worst[1]],
    }


def run_named():
    labels = [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("J???E?pNu\\?", 2),
    ]
    for g6, t in labels:
        n, e = dec(g6)
        if t != 1:
            n, e = blowup_edges(n, e, t)
        info = loads(n, e)
        if info is None:
            print(f"{g6}[{t}] skipped")
            continue
        analyze_info(f"{g6}[{t}]", info, verbose=True)


def run_census(nmax=10, stride=1):
    print(f"\nCENSUS N<= {nmax} stride={stride}")
    acc = {
        "graphs": 0,
        "multi_support_comp": 0,
        "multi_strong_comp": 0,
        "theta_miss_pos": 0,
    }
    worst = None
    for n in range(5, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()[::stride]
        for g6 in out:
            nn, e = dec(g6)
            info = loads(nn, e)
            if info is None:
                continue
            r = analyze_info(g6, info)
            if r is None:
                continue
            acc["graphs"] += 1
            if len(r["support_comp_sizes"]) > 1:
                acc["multi_support_comp"] += 1
            if len(r["strong_comp_sizes"]) > 1:
                acc["multi_strong_comp"] += 1
            if r["worst_miss"] > 0:
                acc["theta_miss_pos"] += 1
            if worst is None or r["worst_miss"] > worst["worst_miss"]:
                worst = {"g6": g6, **r}
        print(f"  N={n} done", flush=True)
    print(f"  acc={acc}")
    if worst:
        print(
            "  worst theta miss:",
            worst["g6"],
            "N=", worst["n"],
            "miss=", worst["worst_miss"],
            "edge=", worst["worst_edge"],
            "row=", worst["worst_row"],
            "cap=", worst["worst_cap"],
        )


if __name__ == "__main__":
    run_named()
    run_census(10)
