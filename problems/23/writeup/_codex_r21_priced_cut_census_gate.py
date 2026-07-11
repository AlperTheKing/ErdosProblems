"""Exact R21 priced-cut gate for the endpoint-half restricted dual.

For one connected triangle-free graph and its Gamma-minimal connected maximum
cut, this gate builds the concrete door-only wall used by
``_claude_rcc_dual_search.py``:

* ``S`` is the set of bad edges (all must have ell = 5);
* ``F`` is the union of every shortest blue geodesic edge supporting ``S``;
* ``O`` is the remaining blue-edge set;
* ``C`` is the union of the vertices of every shortest row supporting ``S``;
* the only bank sink has capacity ``sigma = |B| - |M|`` and is legal for all
  ports in ``O``.

The restricted dual enforces D1 only on the endpoint-half singleton cuts
``{x}``, where ``C`` is the full shortest-row vertex union.  Its canonical
almost-squeeze has theta({x}) = 1/2 and therefore exact port load

    L(uv) = (1[u in C] + 1[v in C]) / 2.

Discovery uses scipy/HiGHS.  Every reported mathematical verdict is then
recomputed with ``Fraction`` after a monotone rational repair of the candidate
dual.  For a strict restricted dual, the gate:

1. verifies restricted D1, D2, strictness, and weighted routing failure;
2. extracts an inclusion-minimal positive dual-scaled Hall shore;
3. enumerates every cut (canonicalized by excluding vertex 0);
4. compares ``max_X cutGap_d(X)`` with the exact scaled deficiency.

An ``allCutFailure`` record is an exact falsifier to the proposed R21
restricted-dual cut-extraction statement on this concrete real graph.  It is
not, by itself, a counterexample to Erdos #23.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _h import Bconn, GENG, dec, geos, gmin, maxcut_all  # noqa: E402


Edge = tuple[int, int]


def edge(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def separated(mask: int, e: Edge) -> bool:
    return bool(((mask >> e[0]) ^ (mask >> e[1])) & 1)


def triangle_free(n: int, adjacency: list[set[int]]) -> bool:
    return not any(
        adjacency[u] & adjacency[v]
        for u in range(n)
        for v in adjacency[u]
        if u < v
    )


def support_of_bad(adjacency: list[set[int]], side: list[int], e: Edge):
    edges: set[Edge] = set()
    vertices: set[int] = set()
    for row in geos(adjacency, side, e[0], e[1]):
        vertices.update(row)
        edges.update(edge(row[i], row[i + 1]) for i in range(len(row) - 1))
    return edges, vertices


def rationalize(value: float, denominator: int) -> Fraction:
    if abs(value) < 1e-10:
        return Fraction(0)
    return Fraction(float(value)).limit_denominator(denominator)


def singleton_gap(
    x: int,
    S: tuple[Edge, ...],
    F: tuple[Edge, ...],
    O: tuple[Edge, ...],
    alpha: dict[Edge, Fraction],
    beta: dict[Edge, Fraction],
    gamma: dict[Edge, Fraction],
) -> Fraction:
    lhs = sum((alpha[e] for e in S if x in e), Fraction(0))
    rhs = sum((beta[e] for e in F if x in e), Fraction(0))
    rhs += sum((gamma[e] for e in O if x in e), Fraction(0))
    return lhs - rhs


def exact_repair(
    C: tuple[int, ...],
    S: tuple[Edge, ...],
    F: tuple[Edge, ...],
    O: tuple[Edge, ...],
    sigma: int,
    values: np.ndarray,
    denominator: int,
):
    nS, nF, nO = len(S), len(F), len(O)
    alpha = {e: rationalize(values[i], denominator) for i, e in enumerate(S)}
    beta = {
        e: rationalize(values[nS + i], denominator)
        for i, e in enumerate(F)
    }
    gamma = {
        e: rationalize(values[nS + nF + i], denominator)
        for i, e in enumerate(O)
    }
    delta = rationalize(values[nS + nF + nO], denominator)

    # Monotone exact repair: increase only D1 right-hand variables.  Prefer a
    # support beta because it does not force a larger D2 sink price.
    for x in C:
        deficit = singleton_gap(x, S, F, O, alpha, beta, gamma)
        if deficit <= 0:
            continue
        support = next((e for e in F if x in e), None)
        if support is not None:
            beta[support] += deficit
            continue
        port = next((e for e in O if x in e), None)
        if port is None:
            return None
        gamma[port] += deficit

    delta = max([delta, Fraction(0), *gamma.values()])
    strict_gap = (
        sum(alpha.values(), Fraction(0))
        - sum(beta.values(), Fraction(0))
        - sigma * delta
    )
    if strict_gap <= 0:
        return None

    assert all(Fraction(0) <= a <= 1 for a in alpha.values())
    assert all(v >= 0 for v in [*beta.values(), *gamma.values(), delta])
    assert all(singleton_gap(x, S, F, O, alpha, beta, gamma) <= 0 for x in C)
    assert all(g <= delta for g in gamma.values())
    return alpha, beta, gamma, delta, strict_gap


def cut_gap(
    mask: int,
    S: tuple[Edge, ...],
    F: tuple[Edge, ...],
    O: tuple[Edge, ...],
    alpha: dict[Edge, Fraction],
    beta: dict[Edge, Fraction],
    gamma: dict[Edge, Fraction],
) -> Fraction:
    return (
        sum((alpha[e] for e in S if separated(mask, e)), Fraction(0))
        - sum((beta[e] for e in F if separated(mask, e)), Fraction(0))
        - sum((gamma[e] for e in O if separated(mask, e)), Fraction(0))
    )


def minimal_deficient_shore(
    O: tuple[Edge, ...],
    load: dict[Edge, Fraction],
    gamma: dict[Edge, Fraction],
    capacity: Fraction,
):
    weights = {p: load[p] * gamma[p] for p in O}
    shore = {p for p in O if weights[p] > 0}
    total = sum((weights[p] for p in shore), Fraction(0))
    if total <= capacity:
        return None
    for p in sorted(shore):
        if total - weights[p] > capacity:
            shore.remove(p)
            total -= weights[p]
    assert total > capacity
    assert all(total - weights[p] <= capacity for p in shore)
    return tuple(sorted(shore)), total - capacity, weights


def solve_one(payload):
    g6, denominator = payload
    n, graph_edges = dec(g6)
    adjacency = [set() for _ in range(n)]
    for u, v in graph_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    if not triangle_free(n, adjacency):
        return {"kind": "invalidGenerator", "g6": g6}

    cuts = maxcut_all(n, adjacency)
    best = gmin(n, adjacency, cuts)
    if best is None:
        return {"kind": "noEligibleCut", "g6": g6, "n": n}
    side, gamma_value, bad_edges, lengths = best
    if not Bconn(n, adjacency, side):
        return {"kind": "noEligibleCut", "g6": g6, "n": n}
    if any(lengths[e] != 5 for e in bad_edges):
        return {"kind": "notPureEll5", "g6": g6, "n": n}

    S = tuple(sorted(edge(*e) for e in bad_edges))
    Fset: set[Edge] = set()
    Cset: set[int] = set()
    for e in S:
        row_edges, row_vertices = support_of_bad(adjacency, side, e)
        Fset.update(row_edges)
        Cset.update(row_vertices)
    F = tuple(sorted(Fset))
    B = tuple(sorted(
        edge(u, v)
        for u, v in graph_edges
        if side[u] != side[v]
    ))
    O = tuple(e for e in B if e not in Fset)
    C = tuple(sorted(Cset))
    sigma = len(B) - len(S)
    if not O or sigma < 0:
        return {"kind": "noPorts", "g6": g6, "n": n}

    nS, nF, nO = len(S), len(F), len(O)
    nv = nS + nF + nO + 1
    objective = np.zeros(nv)
    objective[:nS] = -1.0
    objective[nS:nS + nF] = 1.0
    objective[-1] = float(sigma)
    rows = []
    rhs = []

    # D1 on the endpoint-half singleton family.
    for x in C:
        row = np.zeros(nv)
        for i, e in enumerate(S):
            if x in e:
                row[i] = 1.0
        for i, e in enumerate(F):
            if x in e:
                row[nS + i] = -1.0
        for i, e in enumerate(O):
            if x in e:
                row[nS + nF + i] = -1.0
        rows.append(row)
        rhs.append(0.0)

    # D2 for the unique sink, legal from every port.
    for i in range(nO):
        row = np.zeros(nv)
        row[nS + nF + i] = 1.0
        row[-1] = -1.0
        rows.append(row)
        rhs.append(0.0)

    result = linprog(
        c=objective,
        A_ub=np.asarray(rows),
        b_ub=np.asarray(rhs),
        bounds=[(0, 1)] * nS + [(0, None)] * (nF + nO + 1),
        method="highs",
    )
    if not result.success:
        return {"kind": "lpFailure", "g6": g6, "n": n, "status": result.message}
    if -result.fun <= 1e-8:
        return {
            "kind": "noStrictRestrictedDual",
            "g6": g6,
            "n": n,
            "floatObjective": float(-result.fun),
        }

    repaired = exact_repair(C, S, F, O, sigma, result.x, denominator)
    if repaired is None:
        return {
            "kind": "rationalizationFailure",
            "g6": g6,
            "n": n,
            "floatObjective": float(-result.fun),
        }
    alpha, beta, gamma, delta, strict_gap = repaired

    load = {
        p: Fraction(int(p[0] in C) + int(p[1] in C), 2)
        for p in O
    }
    weighted_load = sum((load[p] * gamma[p] for p in O), Fraction(0))
    scaled_capacity = sigma * delta
    if weighted_load <= scaled_capacity:
        return {
            "kind": "identityFailure",
            "g6": g6,
            "n": n,
            "strictGap": str(strict_gap),
            "weightedLoad": str(weighted_load),
            "scaledCapacity": str(scaled_capacity),
        }

    shore_result = minimal_deficient_shore(O, load, gamma, scaled_capacity)
    assert shore_result is not None
    shore, deficiency, weights = shore_result

    best_mask = 0
    best_gap = None
    for mask_without_zero in range(1 << (n - 1)):
        mask = mask_without_zero << 1
        gap = cut_gap(mask, S, F, O, alpha, beta, gamma)
        if best_gap is None or gap > best_gap:
            best_gap = gap
            best_mask = mask
    assert best_gap is not None

    atlas_gaps = []
    for x in C:
        mask = 1 << x
        atlas_gaps.append((cut_gap(mask, S, F, O, alpha, beta, gamma), mask))
    atlas_gap, atlas_mask = max(atlas_gaps)

    record = {
        "kind": "pricedCutPass" if deficiency <= best_gap else "allCutFailure",
        "g6": g6,
        "n": n,
        "sideMask": sum(bit << i for i, bit in enumerate(side)),
        "gammaValue": gamma_value,
        "S": [list(e) for e in S],
        "F": [list(e) for e in F],
        "O": [list(e) for e in O],
        "C": list(C),
        "sigma": sigma,
        "dual": {
            "alpha": {f"{e[0]},{e[1]}": str(alpha[e]) for e in S},
            "beta": {f"{e[0]},{e[1]}": str(beta[e]) for e in F},
            "gamma": {f"{e[0]},{e[1]}": str(gamma[e]) for e in O},
            "delta": str(delta),
            "strictGap": str(strict_gap),
        },
        "load": {f"{e[0]},{e[1]}": str(load[e]) for e in O},
        "minimalShore": [list(e) for e in shore],
        "scaledDeficiency": str(deficiency),
        "bestAllowedCutMask": best_mask,
        "bestAllowedCutGap": str(best_gap),
        "atlasCutMask": atlas_mask,
        "atlasCutGap": str(atlas_gap),
        "epsilon": str(deficiency - best_gap),
        "weightedLoadAllPorts": str(weighted_load),
        "scaledCapacity": str(scaled_capacity),
        "shoreWeights": {f"{e[0]},{e[1]}": str(weights[e]) for e in shore},
    }
    return record


def graph6_for_order(n: int) -> list[str]:
    result = subprocess.run(
        [GENG, "-tc", str(n)],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=9)
    parser.add_argument("--workers", type=int, default=61)
    parser.add_argument("--denominator", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, default=Path("../../../tmp/codex_r21_priced_cut_census.json"))
    parser.add_argument("--failure-limit", type=int, default=20)
    args = parser.parse_args()
    if not (1 <= args.workers <= 64):
        parser.error("--workers must be in [1,64]")

    payloads = []
    order_counts = {}
    for n in range(args.n_min, args.n_max + 1):
        graphs = graph6_for_order(n)
        order_counts[str(n)] = len(graphs)
        payloads.extend((g6, args.denominator) for g6 in graphs)

    counts = {}
    passes = []
    failures = []
    identity_failures = []
    rationalization_failures = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for record in pool.map(solve_one, payloads, chunksize=16):
            kind = record["kind"]
            counts[kind] = counts.get(kind, 0) + 1
            if kind == "pricedCutPass" and len(passes) < args.failure_limit:
                passes.append(record)
            elif kind == "allCutFailure" and len(failures) < args.failure_limit:
                failures.append(record)
            elif kind == "identityFailure":
                identity_failures.append(record)
            elif kind == "rationalizationFailure":
                rationalization_failures.append(record)

    summary = {
        "scope": {
            "nMin": args.n_min,
            "nMax": args.n_max,
            "workers": args.workers,
            "graphsByOrder": order_counts,
            "dualRestriction": "endpoint-half singleton cuts on C=union of all shortest-row vertices",
            "allCutSearch": "all vertex shores modulo complement",
        },
        "counts": counts,
        "firstPasses": passes,
        "firstAllCutFailures": failures,
        "identityFailures": identity_failures,
        "rationalizationFailures": rationalization_failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="ascii")
    print(json.dumps({"scope": summary["scope"], "counts": counts}, indent=2))
    print(f"OUTPUT {args.output.resolve()}")
    return 1 if failures or identity_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
