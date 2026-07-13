"""Independent exact replay of the first weak endpoint atom in R44."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
R40 = ROOT / "tmp" / "fanout" / "r40_strong_probe_census"
for path in (WRITEUP, P5, PHT, R40):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from strong_probe_census import matching_analysis  # noqa: E402
import p5_core as p5  # noqa: E402


G6 = "GCQb`o"
CHOICE = (1, 0)
ATOM = 0
REPLACEMENT = 0


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def triangle_free(n: int, edges: set[tuple[int, int]]) -> bool:
    adjacency = [set() for _ in range(n)]
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    return all(not (adjacency[x] & adjacency[y]) for x, y in edges)


def endpoint(ctx, old, new, m: int, z: int, owner: int, side: list[int]) -> dict:
    count = old.pair[m][z]
    sigma = ctx.sigma_pair[m][z]
    pair_edge = edge(m, z)
    unreserved = all(
        not p5._reserved(new, m, z, half) and not p5._reserved(new, z, m, half)
        for half in (0, 1)
    )
    common_blue = owner in ctx.blue_adj[m] and owner in ctx.blue_adj[z]
    return {
        "countOld": count,
        "countNew": new.pair[m][z],
        "sigma": sigma,
        "sameSide": side[m] == side[z],
        "noGraphEdge": pair_edge not in ctx.blue and pair_edge not in ctx.bad,
        "commonBlue": common_blue,
        "owner": owner,
        "unreservedBothOrientations": unreserved,
        "productionP2": count == 1 and common_blue and unreserved and sigma >= 2,
    }


def main() -> int:
    n, raw_edges = dec(G6)
    graph_edges = {edge(x, y) for x, y in raw_edges}
    info = loads(n, raw_edges)
    assert info is not None
    families = shortest_row_families(info)
    rows = rows_for_choice(families, CHOICE)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    old = p5.reconstruct_state(ctx, rows)
    new_choice = list(CHOICE)
    new_choice[ATOM] = REPLACEMENT
    new_rows = rows_for_choice(families, tuple(new_choice))
    new = p5.reconstruct_state(ctx, new_rows)
    a, x, m, y, b = rows[ATOM]
    v = new_rows[ATOM][2]
    defects = []
    for choice in itertools.product(*(range(len(family)) for family in families)):
        state = p5.reconstruct_state(ctx, rows_for_choice(families, choice))
        defects.append({"choice": list(choice), "defect": matching_analysis(ctx, state)["defect"]})
    left = endpoint(ctx, old, new, m, a, x, info["side"])
    right = endpoint(ctx, old, new, m, b, y, info["side"])
    displayed_cut = sum(info["side"][u] != info["side"][v] for u, v in graph_edges)
    exact_maxcut = max(
        sum(((mask >> u) & 1) != ((mask >> v) & 1) for u, v in graph_edges)
        for mask in range(1 << n)
    )
    payload = {
        "schema": "R44_N8_WEAK_ENDPOINT_WITNESS_V1",
        "g6": G6,
        "order": n,
        "triangleFree": triangle_free(n, graph_edges),
        "edgeCount": len(graph_edges),
        "displayedCut": displayed_cut,
        "exactMaxCut": exact_maxcut,
        "gamma": info["G"],
        "badEdges": [list(item) for item in info["M"]],
        "familySizes": [len(family) for family in families],
        "allTupleDefects": defects,
        "minimumDefect": min(item["defect"] for item in defects),
        "choice": list(CHOICE),
        "oldRow": list(rows[ATOM]),
        "newRow": list(new_rows[ATOM]),
        "xvOldActive": edge(x, v) in old.active_edges,
        "vyOldSupport": edge(v, y) in old.support,
        "supportConstant": len(old.support) == len(new.support),
        "middleMultiplicity": {"mx": old.pair[m][x], "my": old.pair[m][y]},
        "endpointAtX": left,
        "endpointAtY": right,
    }
    payload["canonicalSha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    (HERE / "n8_weak_endpoint_witness.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(payload, sort_keys=True))
    valid = (
        payload["triangleFree"]
        and payload["displayedCut"] == payload["exactMaxCut"]
        and payload["minimumDefect"] == 0
        and payload["xvOldActive"]
        and payload["vyOldSupport"]
        and payload["supportConstant"]
        and sorted(payload["middleMultiplicity"].values()) == [1, 2]
        and all(item["countOld"] == 1 and item["countNew"] == 0 for item in (left, right))
        and all(item["sameSide"] and item["noGraphEdge"] and item["commonBlue"] and item["unreservedBothOrientations"] for item in (left, right))
        and not left["productionP2"] and not right["productionP2"]
        and left["sigma"] == right["sigma"] == 1
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
