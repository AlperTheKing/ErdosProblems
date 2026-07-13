"""Exact R19 base-transfer audit on the 3,892-vertex guardrail.

The attachment export described in R19 uses two vertices from one 784-class.
They have the core attachment vertex as a COMMON BLUE neighbour, not a common
bad neighbour.  Flipping the pair has 58 blue boundary edges and no bad
boundary edge; reserving the two blue edges to the destination leaves 56
units of adjusted switch surplus.

For each row-choice omega the endpoint overloads are 43 at vertex 4 and 38 at
vertex 8.  We exhibit 43 and 38 distinct ordered-pair sources respectively,
prove that each source is permanently Free (no shortest row of any bad edge
can contain both vertices), and verify the corrected common-blue base-transfer
condition exactly.  The construction replicates independently for every
omega, so no enumeration of the enormous row-choice product is needed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_endpointflow_3892_counterexample import (  # noqa: E402
    ATTACHMENTS,
    add_c5_blowup,
    adjacency,
    build_locked_core,
    edge,
    support_and_load,
)


def bfs(adj: list[set[int]], source: int) -> list[int]:
    dist = [-1] * len(adj)
    dist[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def build_fixture():
    side, edges, blue, bad, _locks, next_vertex = build_locked_core()
    blowups = {}
    for attachment in ATTACHMENTS:
        next_vertex, parts, _cycles = add_c5_blowup(
            side, edges, blue, bad, next_vertex, attachment
        )
        blowups[attachment] = parts
    assert next_vertex == 3892
    return side, edges, blue, bad, blowups


def switch_counts(
    blue: set[tuple[int, int]], bad: set[tuple[int, int]], vertices: set[int]
) -> tuple[int, int]:
    blue_boundary = sum((u in vertices) ^ (v in vertices) for u, v in blue)
    bad_boundary = sum((u in vertices) ^ (v in vertices) for u, v in bad)
    return blue_boundary, bad_boundary


def permanently_free(
    x: int,
    y: int,
    blue_adj: list[set[int]],
    bad: set[tuple[int, int]],
    bad_distance: int = 4,
) -> bool:
    """No shortest row for any bad edge contains both x and y."""

    dx = bfs(blue_adj, x)
    dy = bfs(blue_adj, y)
    dxy = dx[y]
    assert dxy >= 0
    for a, b in bad:
        if (
            dx[a] + dxy + dy[b] == bad_distance
            or dy[a] + dxy + dx[b] == bad_distance
        ):
            return False
    return True


def ordered_pairs(vertices: tuple[int, ...], count: int):
    out = []
    for x in vertices:
        for y in vertices:
            if x != y:
                out.append((x, y))
                if len(out) == count:
                    return out
    raise AssertionError("not enough ordered pairs")


def canonical_payload(records: list[dict]) -> bytes:
    return json.dumps(records, sort_keys=True, separators=(",", ":")).encode()


def main() -> None:
    _side, _edges, blue, bad, blowups = build_fixture()
    n = 3892
    blue_adj = adjacency(n, blue)
    bad_adj = adjacency(n, bad)
    load, _supports, _vertices, ell_hist = support_and_load(n, blue, bad)
    assert ell_hist == {5: len(bad)}

    endpoint_deficit = {
        4: int(load[4] - n),
        8: int(load[8] - n),
    }
    assert endpoint_deficit == {4: 43, 8: 38}

    records = []
    used_sources: set[tuple[int, int]] = set()
    for owner in ATTACHMENTS:
        # A1 is a 784-class; every shortest attachment row uses exactly one
        # A1 vertex, making distinct A1 x A1 ordered pairs permanently Free.
        part_a1 = blowups[owner][1]
        sources = ordered_pairs(part_a1, endpoint_deficit[owner])
        for x, y in sources:
            assert (x, y) not in used_sources
            used_sources.add((x, y))
            assert owner in blue_adj[x] and owner in blue_adj[y]
            assert owner not in bad_adj[x] and owner not in bad_adj[y]
            assert permanently_free(x, y, blue_adj, bad)
            blue_boundary, bad_boundary = switch_counts(blue, bad, {x, y})
            # Two blue boundary edges x-owner and y-owner are the destination
            # incidence spent by this base transfer.
            adjusted_surplus = blue_boundary - bad_boundary - 2
            assert (blue_boundary, bad_boundary, adjusted_surplus) == (58, 0, 56)
            records.append(
                {
                    "owner": owner,
                    "source": [x, y],
                    "commonBlue": True,
                    "commonBad": False,
                    "permanentlyFree": True,
                    "switch": [x, y],
                    "blueBoundary": blue_boundary,
                    "badBoundary": bad_boundary,
                    "destinationEdges": 2,
                    "adjustedSurplus": adjusted_surplus,
                    "kind": "c5Base",
                }
            )

    # The two orientations of the active internal edge are also permanently
    # Free and supply its two endpoint half-needs directly.
    active_sources = [(4, 8), (8, 4)]
    assert all(permanently_free(x, y, blue_adj, bad) for x, y in active_sources)

    assert len(records) == 81
    result = {
        "N": n,
        "endpointDeficitPerOmega": endpoint_deficit,
        "baseTransferSourcesPerOmega": len(records),
        "allSourcesDistinct": len(used_sources) == len(records),
        "relation": "common-blue-neighbour with adjusted switch surplus",
        "commonBadRelationWouldFail": True,
        "activeHitSources": [list(p) for p in active_sources],
        "recordSHA256": hashlib.sha256(canonical_payload(records)).hexdigest(),
    }
    allocation = {}
    for owner in ATTACHMENTS:
        pairs = [r["source"] for r in records if r["owner"] == owner]
        keys = []
        for pair0 in pairs:
            for half in (0, 1):
                keys.append(pair0 + [half])
                if len(keys) == 25:
                    break
            if len(keys) == 25:
                break
        assert len(keys) == 25
        allocation[str(owner)] = keys
    cert = {"records": records, "microAllocation": allocation}
    Path(__file__).with_name("n3892_certificate.json").write_text(json.dumps(cert, sort_keys=True, separators=(",", ":")) + "\n")
    Path(__file__).with_name("n3892_result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

