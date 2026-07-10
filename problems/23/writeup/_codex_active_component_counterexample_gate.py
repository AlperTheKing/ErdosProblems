"""Exact active-component half-block gate on the two endpoint-flow falsifiers.

The endpoint-flow counterexamples overload the endpoints of one internal
off-support blue edge.  The canonical block cover first collapses every
inactive component of the internal off-support graph.  An internal component
is active exactly when it contains both endpoints of a selected bad atom; only
active components are singletonized.

This script recomputes the selected core and full shortest-geodesic supports,
constructs that owner partition, and evaluates every off-support blue-edge
load exactly in ``Fraction`` arithmetic.  A successful record means all
positive off-support load lies on core-boundary restriction exits, each with
load 1/2; it does not assert that the repository currently exports the
corresponding typed Door incidence.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction

from _codex_endpointflow_3892_counterexample import (
    ATTACHMENTS,
    add_c5_blowup,
    build_locked_core,
    support_and_load,
)
from _codex_ies_3164_counterexample import CORE_BAD, build_graph


Edge = tuple[int, int]


class DSU:
    def __init__(self, vertices: set[int]) -> None:
        self.parent = {v: v for v in vertices}

    def find(self, x: int) -> int:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        x, y = self.find(x), self.find(y)
        if x != y:
            self.parent[max(x, y)] = min(x, y)


def build_3892() -> tuple[int, set[Edge], set[Edge]]:
    side, edges, blue, bad, _lock_paths, next_vertex = build_locked_core()
    for attachment in ATTACHMENTS:
        next_vertex, _parts, _cycles = add_c5_blowup(
            side, edges, blue, bad, next_vertex, attachment
        )
    assert next_vertex == 3892
    return next_vertex, blue, bad


def build_3164() -> tuple[int, set[Edge], set[Edge]]:
    data = build_graph()
    assert data["n"] == 3164
    return data["n"], data["blue"], data["bad"]


def owner_partition_record(
    name: str, n: int, blue: set[Edge], bad: set[Edge]
) -> dict[str, object]:
    _load, supports, vertices, ell_hist = support_and_load(n, blue, bad)
    assert ell_hist == {5: len(bad)}

    core = set().union(*(vertices[a] for a in CORE_BAD))
    short = set().union(*(supports[a] for a in CORE_BAD))
    internal = {
        e for e in blue if e[0] in core and e[1] in core and e not in short
    }

    dsu = DSU(core)
    for u, v in internal:
        dsu.union(u, v)
    component = {v: dsu.find(v) for v in core}
    active_components = {
        component[u] for u, v in CORE_BAD if component[u] == component[v]
    }

    def owner(v: int) -> tuple[str, int]:
        c = component[v]
        return ("vertex", v) if c in active_components else ("component", c)

    assert all(owner(u) != owner(v) for u, v in CORE_BAD)

    offsupport = blue - short
    loads: dict[Edge, Fraction] = {}
    boundary: list[Edge] = []
    internal_positive: list[Edge] = []
    for e in offsupport:
        u, v = e
        u_in, v_in = u in core, v in core
        if u_in and v_in:
            loads[e] = Fraction(0) if owner(u) == owner(v) else Fraction(1)
            if loads[e] > 0:
                internal_positive.append(e)
        elif u_in or v_in:
            loads[e] = Fraction(1, 2)
            boundary.append(e)
        else:
            loads[e] = Fraction(0)

    positive = {e: q for e, q in loads.items() if q > 0}
    assert not internal_positive
    assert set(positive) == set(boundary)
    assert all(q == Fraction(1, 2) for q in positive.values())

    payload = "".join(f"{u} {v} {loads[(u, v)]}\n" for u, v in sorted(loads))
    return {
        "name": name,
        "N": n,
        "selectedAtoms": len(CORE_BAD),
        "coreVertices": len(core),
        "shortEdges": len(short),
        "internalOffSupport": [list(e) for e in sorted(internal)],
        "offSupportComponents": len(set(component.values())),
        "activeComponents": sorted(active_components),
        "positiveInternalLoads": [list(e) for e in sorted(internal_positive)],
        "boundaryDoorLoads": len(boundary),
        "maxBoundaryLoad": str(max(positive.values(), default=Fraction(0))),
        "loadTableSHA256": hashlib.sha256(payload.encode("ascii")).hexdigest(),
    }


def main() -> None:
    records = []
    for name, builder in (("ies3164", build_3164), ("endpoint3892", build_3892)):
        n, blue, bad = builder()
        records.append(owner_partition_record(name, n, blue, bad))
    print(json.dumps({"records": records}, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
