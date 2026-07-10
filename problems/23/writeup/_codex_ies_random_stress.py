"""Exact random falsifier stress for Internal Endpoint Slack.

For an atom subset X in one K2 support component, let C(X) and F(X) be
the vertices and blue edges on shortest blue geodesics of X.  Let I(X) be
the blue edges outside F(X) with both endpoints in C(X).  The tested claim is

    deg_I(X)(v) / 2 <= max(0, N - T(v))  for every v in C(X).

All numeric work uses Fraction.  Random graphs are deterministic connected
triangle-free graphs with a C5 backbone.  Maximum cuts and the Gamma-minimal
connected-B refinement are exhaustive.  Uniform blow-ups are tested only when
their full vertex-level cut search fits ``--exact-n``.

This is a bounded falsifier, not a proof artifact.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from itertools import combinations


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def adjacency(n: int, edges) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_triangle_free(adj: list[set[int]], edges) -> bool:
    return all(not (adj[u] & adj[v]) for u, v in edges)


def bfs(adj: list[set[int]], start: int, allowed=None):
    """Distances and exact shortest-path counts from start."""
    n = len(adj)
    dist = [-1] * n
    ways = [0] * n
    dist[start] = 0
    ways[start] = 1
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if allowed is not None and not allowed(u, v):
                continue
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                ways[v] = ways[u]
                q.append(v)
            elif dist[v] == dist[u] + 1:
                ways[v] += ways[u]
    return dist, ways


def blue_connected(n: int, adj: list[set[int]], side: tuple[int, ...]) -> bool:
    dist, _ = bfs(adj, 0, lambda u, v: side[u] != side[v])
    return all(d >= 0 for d in dist)


def gamma_value(n: int, adj: list[set[int]], side: tuple[int, ...]):
    if not blue_connected(n, adj, side):
        return None
    gamma = 0
    bad = []
    for u in range(n):
        for v in adj[u]:
            if u < v and side[u] == side[v]:
                dist, _ = bfs(adj, u, lambda a, b: side[a] != side[b])
                if dist[v] < 0:
                    return None
                ell = dist[v] + 1
                gamma += ell * ell
                bad.append((u, v))
    return (gamma, tuple(bad)) if bad else None


def exact_gamma_min_cuts(n: int, edges, adj: list[set[int]]):
    """Exhaust all cuts modulo complement, then apply connected-B/Gamma-min."""
    edges = tuple(edges)
    best_cut = -1
    maximum = []
    for mask in range(1 << (n - 1)):
        side = (0,) + tuple((mask >> (v - 1)) & 1 for v in range(1, n))
        value = sum(side[u] != side[v] for u, v in edges)
        if value > best_cut:
            best_cut = value
            maximum = [side]
        elif value == best_cut:
            maximum.append(side)

    best_gamma = None
    selected = []
    for side in maximum:
        got = gamma_value(n, adj, side)
        if got is None:
            continue
        gamma, bad = got
        if best_gamma is None or gamma < best_gamma:
            best_gamma = gamma
            selected = [(side, bad)]
        elif gamma == best_gamma:
            selected.append((side, bad))
    return best_cut, len(maximum), best_gamma, selected


def row_data(n: int, adj: list[set[int]], side, bad):
    """Compute p_e, T, and shortest vertex/edge supports without path listing."""
    blue_edges = {
        (u, v)
        for u in range(n)
        for v in adj[u]
        if u < v and side[u] != side[v]
    }
    rows = {}
    for atom in bad:
        s, t = atom
        ds, ws = bfs(adj, s, lambda u, v: side[u] != side[v])
        dt, wt = bfs(adj, t, lambda u, v: side[u] != side[v])
        length = ds[t]
        total = ws[t]
        assert length >= 0 and total > 0
        vertices = frozenset(
            v for v in range(n) if ds[v] >= 0 and ds[v] + dt[v] == length
        )
        support_edges = frozenset(
            e
            for e in blue_edges
            if ds[e[0]] + 1 + dt[e[1]] == length
            or ds[e[1]] + 1 + dt[e[0]] == length
        )
        p = tuple(
            F(ws[v] * wt[v], total) if v in vertices else F(0)
            for v in range(n)
        )
        rows[atom] = {
            "ell": length + 1,
            "p": p,
            "vertices": vertices,
            "edges": support_edges,
            "pathCount": total,
        }
    T = tuple(
        sum((F(rows[a]["ell"]) * rows[a]["p"][v] for a in bad), F(0))
        for v in range(n)
    )
    return blue_edges, rows, T


def support_components(bad, rows):
    parent = {a: a for a in bad}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, a in enumerate(bad):
        for b in bad[i + 1 :]:
            if rows[a]["vertices"] & rows[b]["vertices"]:
                union(a, b)
    groups = {}
    for a in bad:
        groups.setdefault(find(a), []).append(a)
    return [tuple(sorted(group)) for group in groups.values()]


def frac(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def subset_check(n, blue_edges, rows, T, atoms):
    core = set().union(*(rows[a]["vertices"] for a in atoms))
    short = set().union(*(rows[a]["edges"] for a in atoms))
    internal = sorted(
        e for e in blue_edges if e not in short and e[0] in core and e[1] in core
    )
    deficient = len(atoms) > len(short)
    minimum = None
    failure = None
    for v in sorted(core):
        degree = sum(v in e for e in internal)
        load = F(degree, 2)
        cap = max(F(0), F(n) - T[v])
        margin = cap - load
        if minimum is None or margin < minimum:
            minimum = margin
        if margin < 0 and failure is None:
            failure = {
                "vertex": v,
                "internalDegree": degree,
                "load": frac(load),
                "T": frac(T[v]),
                "capacity": frac(cap),
                "margin": frac(margin),
            }
    return minimum if minimum is not None else F(0), deficient, failure, {
        "atoms": [list(a) for a in atoms],
        "core": sorted(core),
        "shortEdges": [list(e) for e in sorted(short)],
        "internalEdges": [list(e) for e in internal],
    }


def analyze_cut(name, kind, n, edges, side, bad, cut_meta, subset_cap):
    adj = adjacency(n, edges)
    blue_edges, rows, T = row_data(n, adj, side, bad)
    counts = Counter(
        cuts=1,
        components=0,
        subsets=0,
        subsetsWithInternalEdges=0,
        deficientSets=0,
        deficientSetsWithInternalEdges=0,
        verticesChecked=0,
        failures=0,
        failuresDeficient=0,
        failuresNondeficient=0,
        skippedComponents=0,
    )
    minimum = None
    deficient_internal_minimum = None
    witness = None
    for component in support_components(list(bad), rows):
        counts["components"] += 1
        if len(component) > subset_cap:
            counts["skippedComponents"] += 1
            continue
        for mask in range(1, 1 << len(component)):
            atoms = tuple(component[i] for i in range(len(component)) if (mask >> i) & 1)
            margin, deficient, failure, detail = subset_check(
                n, blue_edges, rows, T, atoms
            )
            counts["subsets"] += 1
            counts["verticesChecked"] += len(detail["core"])
            counts["deficientSets"] += int(deficient)
            has_internal = bool(detail["internalEdges"])
            counts["subsetsWithInternalEdges"] += int(has_internal)
            counts["deficientSetsWithInternalEdges"] += int(
                deficient and has_internal
            )
            if minimum is None or margin < minimum:
                minimum = margin
            if deficient and has_internal and (
                deficient_internal_minimum is None
                or margin < deficient_internal_minimum
            ):
                deficient_internal_minimum = margin
            if failure is not None:
                counts["failures"] += 1
                counts[
                    "failuresDeficient" if deficient else "failuresNondeficient"
                ] += 1
                if witness is None:
                    witness = {
                        "graph": name,
                        "kind": kind,
                        "n": n,
                        "edges": [list(e) for e in edges],
                        "triangleFree": is_triangle_free(adj, edges),
                        "side": list(side),
                        "badEdges": [list(e) for e in bad],
                        "cutCertification": cut_meta,
                        "rowData": {
                            str(a): {
                                "ell": rows[a]["ell"],
                                "pathCount": rows[a]["pathCount"],
                                "vertices": sorted(rows[a]["vertices"]),
                                "edges": [list(e) for e in sorted(rows[a]["edges"])],
                                "p": [frac(x) for x in rows[a]["p"]],
                            }
                            for a in bad
                        },
                        "T": [frac(x) for x in T],
                        "subset": detail,
                        "deficient": deficient,
                        "failure": failure,
                    }
    return counts, minimum, deficient_internal_minimum, witness


def analyze_record(record, exact_n, subset_cap):
    name, kind, n, edges = record
    edges = tuple(sorted(set(edge(u, v) for u, v in edges)))
    adj = adjacency(n, edges)
    out = {
        "counts": Counter(records=1, triangleFree=0, exactRecords=0,
                          noEligibleCut=0),
        "minimum": None,
        "deficientInternalMinimum": None,
        "witness": None,
    }
    if not is_triangle_free(adj, edges):
        return out
    out["counts"]["triangleFree"] = 1
    if n > exact_n:
        out["counts"]["tooLargeForExactCut"] = 1
        return out
    best, maximum_count, gamma, cuts = exact_gamma_min_cuts(n, edges, adj)
    out["counts"]["exactRecords"] = 1
    if not cuts:
        out["counts"]["noEligibleCut"] = 1
        return out
    for cut_index, (side, bad) in enumerate(cuts):
        meta = {
            "method": "exhaustive-mod-complement",
            "maxCut": best,
            "maximumCuts": maximum_count,
            "gamma": gamma,
            "gammaMinConnectedBCuts": len(cuts),
            "cutIndex": cut_index,
        }
        counts, minimum, deficient_internal_minimum, witness = analyze_cut(
            name, kind, n, edges, side, bad, meta, subset_cap
        )
        out["counts"].update(counts)
        if minimum is not None and (out["minimum"] is None or minimum < out["minimum"]):
            out["minimum"] = minimum
        if deficient_internal_minimum is not None and (
            out["deficientInternalMinimum"] is None
            or deficient_internal_minimum < out["deficientInternalMinimum"]
        ):
            out["deficientInternalMinimum"] = deficient_internal_minimum
        if out["witness"] is None and witness is not None:
            out["witness"] = witness
    return out


def random_triangle_free(seed: int, n: int, density: float):
    """Connected triangle-free graph with a randomized induced C5 backbone."""
    rng = random.Random(seed)
    order = list(range(n))
    rng.shuffle(order)
    chosen = set()
    for i in range(5):
        chosen.add(edge(order[i], order[(i + 1) % 5]))
    adj = adjacency(n, chosen)
    for i in range(5, n):
        u = order[i]
        v = rng.choice(order[:i])
        chosen.add(edge(u, v))
        adj[u].add(v)
        adj[v].add(u)
    candidates = [e for e in combinations(range(n), 2) if e not in chosen]
    rng.shuffle(candidates)
    for u, v in candidates:
        if rng.random() < density and not (adj[u] & adj[v]):
            chosen.add((u, v))
            adj[u].add(v)
            adj[v].add(u)
    assert is_triangle_free(adj, chosen)
    return tuple(sorted(chosen))


def blowup(n: int, edges, factor: int):
    lifted = []
    for u, v in edges:
        lifted.extend(
            (u * factor + i, v * factor + j)
            for i in range(factor)
            for j in range(factor)
        )
    return n * factor, tuple(sorted(lifted))


def make_records(trials, seed, ns, densities, blowup_every, factors, exact_n):
    records = []
    for i in range(trials):
        rng = random.Random(seed + i)
        n = rng.choice(ns)
        density = rng.choice(densities)
        edges = random_triangle_free(seed + i, n, density)
        records.append((f"random:{seed + i}:n{n}:p{density}", "random", n, edges))
        if blowup_every > 0 and i % blowup_every == 0:
            for factor in factors:
                nn, lifted = blowup(n, edges, factor)
                if nn <= exact_n:
                    records.append((
                        f"random-blowup:{seed + i}:n{n}:t{factor}",
                        "random-blowup", nn, lifted,
                    ))
    for cycle_n, factor in ((5, 2), (5, 3), (7, 2)):
        edges = tuple(edge(i, (i + 1) % cycle_n) for i in range(cycle_n))
        nn, lifted = blowup(cycle_n, edges, factor)
        if nn <= exact_n:
            records.append((f"C{cycle_n}-blowup-t{factor}", "cycle-blowup", nn, lifted))
    return records


def merge(total, result):
    total["counts"].update(result["counts"])
    minimum = result["minimum"]
    if minimum is not None and (total["minimum"] is None or minimum < total["minimum"]):
        total["minimum"] = minimum
    deficient_internal_minimum = result["deficientInternalMinimum"]
    if deficient_internal_minimum is not None and (
        total["deficientInternalMinimum"] is None
        or deficient_internal_minimum < total["deficientInternalMinimum"]
    ):
        total["deficientInternalMinimum"] = deficient_internal_minimum
    if total["witness"] is None and result["witness"] is not None:
        total["witness"] = result["witness"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=192)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=20260710)
    ap.add_argument("--ns", default="5,6,7,8,9,10,11,12")
    ap.add_argument("--densities", default="0.12,0.2,0.3,0.42,0.56")
    ap.add_argument("--blowup-every", type=int, default=6)
    ap.add_argument("--blowup-factors", default="2")
    ap.add_argument("--exact-n", type=int, default=15)
    ap.add_argument("--subset-cap", type=int, default=18)
    args = ap.parse_args()
    if not 1 <= args.workers <= 32:
        ap.error("--workers must be in 1..32")
    ns = [int(x) for x in args.ns.split(",") if x]
    densities = [float(x) for x in args.densities.split(",") if x]
    factors = [int(x) for x in args.blowup_factors.split(",") if x]
    if min(ns) < 5 or max(ns) > args.exact_n:
        ap.error("all --ns must be between 5 and --exact-n")
    records = make_records(
        args.trials, args.seed, ns, densities, args.blowup_every,
        factors, args.exact_n,
    )
    total = {
        "counts": Counter(),
        "minimum": None,
        "deficientInternalMinimum": None,
        "witness": None,
    }
    print("command=", " ".join([sys.executable] + sys.argv), flush=True)
    print(f"scheduledRecords={len(records)} workers={args.workers}", flush=True)
    work = [(record, args.exact_n, args.subset_cap) for record in records]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i, result in enumerate(pool.map(_work, work, chunksize=1), 1):
            merge(total, result)
            if i % 50 == 0:
                print(
                    f"done={i} cuts={total['counts']['cuts']} "
                    f"subsets={total['counts']['subsets']} "
                    f"failures={total['counts']['failures']}",
                    flush=True,
                )
    counts = dict(sorted(total["counts"].items()))
    print("INTERNAL ENDPOINT SLACK EXACT RANDOM STRESS")
    print("totals=", json.dumps(counts, sort_keys=True))
    print("minMargin=", "none" if total["minimum"] is None else frac(total["minimum"]))
    print(
        "minDeficientInternalMargin=",
        "none"
        if total["deficientInternalMinimum"] is None
        else frac(total["deficientInternalMinimum"]),
    )
    print("firstWitness=", json.dumps(total["witness"], sort_keys=True))
    print("VERDICT=", "FAIL" if total["witness"] is not None else "NO_FALSIFIER")


def _work(args):
    return analyze_record(*args)


if __name__ == "__main__":
    main()
