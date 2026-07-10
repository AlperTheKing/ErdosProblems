"""Exact gate for the half-singleton vertex-slack FullBank certificate.

For each K2 support component X in a connected-B Gamma-minimal maximum cut:

* C is the union of shortest-geodesic vertices of X;
* F is the union of shortest-geodesic blue edges of X;
* O is every blue edge incident with C but not in F.

The compiled Lean constructor `Ell5SingletonVertexSlack` puts weight 1/2 on
each singleton core cut and routes half of every edge in O to each incident
core endpoint.  Its only numeric obligation is

    deg_O(v) / 2 <= max(0, N - T(v))       for every v in C.

This script recomputes that inequality exactly with Fraction.  Failure is not
a FullBankHall falsifier: Door/C5Base/Prune may still absorb the remainder. It
is precisely the boundary between the vertex-slack-only branch and the real
mixed-bank wall.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _claude_residual_hall_gate import (
    even_cycle_chord,
    geos_paths,
    k2_components,
    residuals,
)
from _codex_k2t_switch_probe import adj_from_edges
from _h import Bconn, GENG, dec, gmin, maxcut_all


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def subset_record(n, adj, side, cd, atoms):
    C = set()
    Fshort = set()
    for a, b in atoms:
        paths = geos_paths(adj, side, a, b)
        assert paths
        for path in paths:
            C.update(path)
            Fshort.update(norm_edge(path[i], path[i + 1])
                          for i in range(len(path) - 1))

    cut_edges = {
        (u, v)
        for u in range(n)
        for v in adj[u]
        if u < v and side[u] != side[v]
    }
    outside = {
        e for e in cut_edges
        if (e[0] in C or e[1] in C) and e not in Fshort
    }
    internal = {e for e in outside if e[0] in C and e[1] in C}
    boundary = outside - internal

    failures = []
    mixed_failures = []
    min_margin = None
    min_mixed_margin = None
    for v in sorted(C):
        degree = sum(1 for e in outside if v in e)
        internal_degree = sum(1 for e in internal if v in e)
        cap = max(F(0), F(n) - cd["T"][v])
        load = F(degree, 2)
        mixed_load = F(internal_degree, 2)
        margin = cap - load
        mixed_margin = cap - mixed_load
        if min_margin is None or margin < min_margin:
            min_margin = margin
        if min_mixed_margin is None or mixed_margin < min_mixed_margin:
            min_mixed_margin = mixed_margin
        if margin < 0:
            failures.append({
                "v": v,
                "degreeO": degree,
                "load": str(load),
                "T": str(cd["T"][v]),
                "cap": str(cap),
                "margin": str(margin),
            })
        if mixed_margin < 0:
            mixed_failures.append({
                "v": v,
                "internalDegree": internal_degree,
                "load": str(mixed_load),
                "T": str(cd["T"][v]),
                "cap": str(cap),
                "margin": str(mixed_margin),
            })

    return {
        "nAtoms": len(atoms),
        "nCore": len(C),
        "nShort": len(Fshort),
        "nOutside": len(outside),
        "nInternal": len(internal),
        "nBoundaryDoor": len(boundary),
        "maxEll": max(cd["ell"][e] for e in atoms),
        "demand": str(sum(cd["ell"][e] ** 2 - 25 for e in atoms)),
        "minMargin": str(min_margin if min_margin is not None else F(0)),
        "minMixedMargin": str(min_mixed_margin if min_mixed_margin is not None else F(0)),
        "failures": failures,
        "mixedFailures": mixed_failures,
    }


def component_records(n, adj, side, cd, comp):
    """Enumerate all support-deficient atom subsets of one K2 component.

    The census components are small. A defensive 22-atom cap prevents an
    accidental exponential run on a future structured input; such a case is
    reported separately instead of silently sampled.
    """
    atoms = list(comp["atoms"])
    if len(atoms) > 22:
        return [], {"skippedAtoms": len(atoms)}
    rows = []
    for mask in range(1, 1 << len(atoms)):
        subset = [atoms[i] for i in range(len(atoms)) if (mask >> i) & 1]
        rec = subset_record(n, adj, side, cd, subset)
        if rec["nAtoms"] > rec["nShort"]:
            rows.append(rec)
    return rows, None


def analyze_graph(record):
    name, n, edges, fixed_side = record
    adj = adj_from_edges(n, edges)
    side = fixed_side
    if side is None:
        best = gmin(n, adj, maxcut_all(n, adj))
        if best is None:
            return None
        side = best[0]
    if not Bconn(n, adj, side):
        return None
    cd = residuals(n, adj, side)
    if cd is None or not cd["M"]:
        return None
    deficient = []
    skipped = []
    for X in k2_components(n, cd):
        rows, skip = component_records(n, adj, side, cd, X)
        deficient.extend(rows)
        if skip is not None:
            skipped.append(skip)
    return {"name": name, "n": n, "deficient": deficient,
            "skipped": skipped}


def census_records(maxn):
    out = []
    for n in range(5, maxn + 1):
        g6s = subprocess.run(
            [GENG, "-tc", str(n)], capture_output=True, text=True, check=True
        ).stdout.split()
        for i, g6 in enumerate(g6s):
            nn, edges = dec(g6)
            out.append((f"cen{n}:{i}:{g6}", nn, edges, None))
    return out


def structured_records():
    out = []
    for n in (18, 22, 26, 30):
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            edges = [(u, v) for u in range(nn) for v in adj[u] if u < v]
            out.append((f"C{n}+chord(0,{gap})", nn, edges, side))

    # Canonical 24-vertex bare-SSE counterexample.
    left = [0, 1, 2]
    right = [3, 4, 5]
    u, w, v = 6, 7, 8
    aL = [9, 10, 11]
    zL = [12, 13, 14]
    mid = [15, 16, 17]
    zR = [18, 19, 20]
    aR = [21, 22, 23]
    edges24 = set()
    for x in left:
        edges24.add(norm_edge(x, u))
    edges24.update((norm_edge(u, w), norm_edge(w, v)))
    for y in right:
        edges24.add(norm_edge(v, y))
    for A, B in ((left, right), (left, aL), (aL, zL), (zL, mid),
                 (mid, zR), (zR, aR), (aR, right)):
        edges24.update(norm_edge(x, y) for x in A for y in B)
    side24 = [0] * 24
    for x in [u, v] + aL + mid + aR:
        side24[x] = 1
    out.append(("canonical24", 24, sorted(edges24), side24))

    # One extra blue edge from the overloaded waist w to an existing middle
    # vertex. It creates no triangle and no new shortest row, while displayed
    # bad count stays nine. This is the minimal vertex-slack-only stress: the
    # new off-support edge loads w by 1/2 but N-T(w)=0. Its own Door token is
    # therefore genuinely needed.
    stressed24 = set(edges24)
    stressed24.add(norm_edge(w, mid[0]))
    out.append(("canonical24+waistDoor", 24, sorted(stressed24), side24))

    # The independently exact-gated 359-vertex lock realization.
    from _codex_wall_r5_359_gate import edges as edges359, side as side359
    out.append(("canonical359", 359, sorted(edges359), list(side359)))
    return out


def verify_stressed24(record):
    """Independent exact/integer gate for the waist-Door stress instance."""
    import numpy as np

    name, n, edges, side = record
    assert name == "canonical24+waistDoor" and n == 24
    adj = adj_from_edges(n, edges)
    triangle_free = all(not (adj[u] & adj[v]) for u, v in edges)

    # Exhaust all cuts with vertex zero fixed, in bounded-memory chunks.
    count_states = 1 << (n - 1)
    chunk = 1 << 20
    best = -1
    multiplicity = 0
    for start in range(0, count_states, chunk):
        stop = min(start + chunk, count_states)
        masks = np.arange(start, stop, dtype=np.uint32)
        value = np.zeros(stop - start, dtype=np.int16)
        for u, v in edges:
            if u == 0:
                value += ((masks >> np.uint32(v - 1)) & 1).astype(np.int16)
            else:
                value += (((masks >> np.uint32(u - 1)) ^
                           (masks >> np.uint32(v - 1))) & 1).astype(np.int16)
        local = int(value.max())
        if local > best:
            best = local
            multiplicity = int(np.count_nonzero(value == local))
        elif local == best:
            multiplicity += int(np.count_nonzero(value == local))

    cd = residuals(n, adj, side)
    assert cd is not None
    comps = k2_components(n, cd)
    assert len(comps) == 1
    rec = subset_record(n, adj, side, cd, list(cd["M"]))
    return {
        "triangleFree": triangle_free,
        "edges": len(edges),
        "maxCut": best,
        "maxCutsModComplement": multiplicity,
        "displayedBad": len(edges) - sum(side[u] != side[v] for u, v in edges),
        "rows": len(cd["M"]),
        "allEll5": all(L == 5 for L in cd["ell"].values()),
        "short": rec["nShort"],
        "outside": rec["nOutside"],
        "vertexSlackFailures": rec["failures"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxn", type=int, default=10)
    ap.add_argument("--workers", type=int, default=32)
    args = ap.parse_args()

    structured = structured_records()
    stress = next(r for r in structured if r[0] == "canonical24+waistDoor")
    print("stressed24Exact=", verify_stressed24(stress))
    records = census_records(args.maxn) + structured
    total_graphs = deficient_sets = passed = failed = skipped = 0
    vertex_only_failed = 0
    first_failure = None
    min_margin = None

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, records, chunksize=16):
            if result is None:
                continue
            total_graphs += 1
            skipped += len(result["skipped"])
            for comp in result["deficient"]:
                deficient_sets += 1
                margin = F(comp["minMixedMargin"])
                if min_margin is None or margin < min_margin:
                    min_margin = margin
                if comp["failures"]:
                    vertex_only_failed += 1
                if comp["mixedFailures"]:
                    failed += 1
                    if first_failure is None:
                        first_failure = {
                            "graph": result["name"],
                            "n": result["n"],
                            "component": comp,
                        }
                else:
                    passed += 1

    print("SINGLETON VERTEX-SLACK EXACT GATE")
    print(f"graphs={total_graphs} deficientSets={deficient_sets} "
          f"skippedLargeComponents={skipped}")
    print(f"mixedPass={passed} mixedFail={failed} "
          f"vertexOnlyFail={vertex_only_failed} minMixedMargin={min_margin}")
    print(f"firstFailure={first_failure}")
    print("Interpretation: fail means mixed Door/C5Base/Prune bank is required; "
          "it is not a FullBankHall falsifier.")


if __name__ == "__main__":
    main()
