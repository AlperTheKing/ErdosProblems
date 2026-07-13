"""Exact R29 common-blue Hall gate at ResidualSourceTokenization scale."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REBUILD = ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py"
OWNERS = (0, 1, 2)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    hall = load_module(REBUILD, "r29_owner_hall_micro")
    incidence = hall.load_untrusted_incidence()
    (
        _rows,
        pair,
        _load,
        _support,
        active_edges,
        active_vertices,
        _active_demand_edges,
        collision,
        hit_need,
    ) = hall.rebuild_scope(incidence)

    # ResidualSourceTokenization uses two microcopies per collision debit and
    # 25 microcopies per endpoint-need slot. Collision already counts halves.
    demand = {
        owner: collision.get(owner, 0) + 25 * hit_need.get(owner, 0)
        for owner in OWNERS
    }
    assert demand == {0: 6675, 1: 6675, 2: 6675}

    masks, _reasons, _companions = hall.owner_sources(
        incidence, pair, active_edges, active_vertices
    )
    old_masks = dict(masks)

    blue_adj = defaultdict(set)
    signed_degree = Counter()
    edge_sign = {}
    for x, y in incidence["blue"]:
        blue_adj[x].add(y)
        blue_adj[y].add(x)
        edge_sign[hall.norm(x, y)] = 1
        signed_degree[x] += 1
        signed_degree[y] += 1
    for x, y in incidence["bad"]:
        edge_sign[hall.norm(x, y)] = -1
        signed_degree[x] -= 1
        signed_degree[y] -= 1

    common_blue_arcs = set()
    for owner in OWNERS:
        for x in sorted(blue_adj[owner]):
            for y in sorted(blue_adj[owner]):
                if x == y or pair[x, y] != 0:
                    continue
                source_edge = hall.norm(x, y)
                sigma = (
                    signed_degree[x]
                    + signed_degree[y]
                    - 2 * edge_sign.get(source_edge, 0)
                )
                if sigma < 2:
                    continue
                for half in (0, 1):
                    reserved = (
                        half == 0
                        and source_edge in active_edges
                        and x in active_vertices
                    )
                    if reserved:
                        continue
                    source = (x, y, half)
                    masks[source] = masks.get(source, 0) | (1 << owner)
                    common_blue_arcs.add((owner, source))

    cuts = []
    for shore_mask in range(8):
        shore_demand = sum(
            demand[o] for o in OWNERS if shore_mask & (1 << o)
        )
        reach = sum(mask & shore_mask != 0 for mask in masks.values())
        cuts.append(
            {
                "shoreMask": shore_mask,
                "demand": shore_demand,
                "reach": reach,
                "margin": reach - shore_demand,
            }
        )
    assert min(cut["margin"] for cut in cuts) == 0

    by_mask = {
        mask: sorted(source for source, source_mask in masks.items()
                     if source_mask == mask)
        for mask in range(1, 8)
    }
    assert {mask: len(by_mask[mask]) for mask in range(1, 8)} == {
        1: 5775,
        2: 5879,
        3: 4,
        4: 5879,
        5: 4,
        6: 0,
        7: 2600,
    }

    shared = by_mask[7]
    allocation = {
        0: by_mask[1] + shared[:900],
        1: by_mask[2] + shared[900:1696],
        2: by_mask[4] + shared[1696:2492],
    }
    assert {o: len(allocation[o]) for o in OWNERS} == demand
    flat = [(o, source) for o in OWNERS for source in allocation[o]]
    assert len({source for _, source in flat}) == len(flat) == 20025
    assert all(masks[source] & (1 << owner) for owner, source in flat)

    checked_new = 0
    for owner, (x, y, half) in flat:
        source = (x, y, half)
        if old_masks.get(source, 0) & (1 << owner):
            continue
        assert (owner, source) in common_blue_arcs
        assert x != y and pair[x, y] == 0
        assert owner in blue_adj[x] and owner in blue_adj[y]
        source_edge = hall.norm(x, y)
        sigma = (
            signed_degree[x]
            + signed_degree[y]
            - 2 * edge_sign.get(source_edge, 0)
        )
        assert sigma >= 2
        assert not (
            half == 0 and source_edge in active_edges and x in active_vertices
        )
        checked_new += 1

    allocation_payload = {
        "schema": "ResidualSourceTokenization-scale owner allocation",
        "demand": demand,
        "ownerSources": {
            str(owner): [list(source) for source in allocation[owner]]
            for owner in OWNERS
        },
    }
    raw = json.dumps(
        allocation_payload, sort_keys=True, separators=(",", ":")
    ).encode()
    result = {
        "verdict": "PASS_COMMON_BLUE_MICRO_SCALE",
        "demandByOwner": demand,
        "totalDemand": sum(demand.values()),
        "sourceCount": len(masks),
        "newCommonBlueKeys": len(set(masks) - set(old_masks)),
        "checkedNewAssignmentArcs": checked_new,
        "maskHistogram": {
            str(mask): len(by_mask[mask]) for mask in range(1, 8)
        },
        "cuts": cuts,
        "allocationSha256": hashlib.sha256(raw).hexdigest(),
    }
    Path(__file__).with_name("r29_common_blue_micro_result.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    Path(__file__).with_name("r29_common_blue_micro_allocation.json").write_bytes(
        raw + b"\n"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
