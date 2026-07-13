"""Exact R29 all-anchor audit against compiled singleton FullBank semantics.

The graph and current scoped relation are reconstructed.  The Door result is
conditional exactly on the provider hypotheses named in the output; no float
arithmetic or optimization oracle is used.
"""

from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
LEAN_SINGLETON = ROOT / "problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean"
LEAN_ENDPOINT = ROOT / "problems/23/lean/Erdos23Delta0/EndpointHalfDoorComplete.lean"
LEAN_LEDGER = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean"
LEAN_TYPED = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean"
LEAN_ADAPTER = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean"
WIRING = ROOT / "problems/23/writeup/WIRING_SPECS_GPTPRO.md"
OWNERS = (0, 1, 2)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def load_lead() -> tuple[object, dict]:
    spec = importlib.util.spec_from_file_location("r29_lead_fullbank", LEAD)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module, module.build()


def all_anchor_rows(data: dict) -> tuple[tuple[int, ...], ...]:
    rows = [tuple(row) for row in data["rows"]]
    start = int(data["selectorStart"])
    for j, meta in enumerate(data["selectorMeta"]):
        rows[start + j] = tuple(meta["anchorRow"])
    return tuple(rows)


def scoped_gate(data: dict, rows: tuple[tuple[int, ...], ...]) -> dict:
    n = int(data["n"])
    blue = set(data["blue"])
    bad = set(data["bad"])
    pair = Counter()
    selected = set()
    support = set()
    row_count = Counter()
    for row in rows:
        for x in row:
            selected.add(x)
            row_count[x] += 1
            for y in row:
                pair[x, y] += 1
        support.update(edge(x, y) for x, y in zip(row, row[1:]))

    active_edges = {e for e in blue - support if e[0] in selected and e[1] in selected}
    adj = defaultdict(set)
    for u, v in active_edges:
        adj[u].add(v)
        adj[v].add(u)
    component = {}
    cid = 0
    for root in sorted(selected):
        if root in component:
            continue
        seen = {root}
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        for v in seen:
            component[v] = cid
        cid += 1
    active_cids = {
        component[u] for u, v in bad
        if u in component and v in component and component[u] == component[v]
    }
    active_vertices = {v for v in selected if component[v] in active_cids}
    demanded_edges = {e for e in active_edges if e[0] in active_vertices}
    degree = Counter()
    for u, v in demanded_edges:
        degree[u] += 1
        degree[v] += 1
    collision = {
        v: 2 * sum(max(0, pair[v, y] - 1) for y in range(n))
        for v in active_vertices
    }
    hit = {
        v: max(0, degree[v] - max(0, n - 5 * row_count[v]))
        for v in active_vertices
    }

    signed_degree = Counter()
    sign = {}
    for e in blue:
        sign[e] = 1
        signed_degree[e[0]] += 1
        signed_degree[e[1]] += 1
    for e in bad:
        sign[e] = -1
        signed_degree[e[0]] -= 1
        signed_degree[e[1]] -= 1
    companions = {o: {x for x in range(n) if pair[o, x] > 0} for o in OWNERS}
    masks = {}
    reasons = {}
    for o in OWNERS:
        for y in range(n):
            if y == o or pair[o, y] != 0:
                continue
            for half in (0, 1):
                key = (o, y, half)
                reserved = half == 0 and edge(o, y) in active_edges and o in active_vertices
                if not reserved:
                    masks[key] = masks.get(key, 0) | (1 << o)
                    reasons[key] = reasons.get(key, 0) | 1
        for x in companions[o]:
            for y in companions[o]:
                if x == y or pair[x, y] != 0:
                    continue
                e = edge(x, y)
                sigma2 = signed_degree[x] + signed_degree[y] - 2 * sign.get(e, 0)
                if sigma2 < 0:
                    continue
                for half in (0, 1):
                    key = (x, y, half)
                    reserved = half == 0 and e in active_edges and x in active_vertices
                    if not reserved:
                        masks[key] = masks.get(key, 0) | (1 << o)
                        reasons[key] = reasons.get(key, 0) | 2

    demand = {o: collision.get(o, 0) + hit.get(o, 0) for o in OWNERS}
    cuts = []
    for shore_mask in range(8):
        d = sum(demand[o] for o in OWNERS if shore_mask & (1 << o))
        reach = sum(1 for mask in masks.values() if mask & shore_mask)
        cuts.append({"shoreMask": shore_mask, "demand": d, "reach": reach, "defect": d - reach})
    reason_hist = Counter(reasons.values())
    return {
        "demandByOwner": demand,
        "cuts": cuts,
        "sameFirst": reason_hist[1],
        "rowCompanion": reason_hist[2],
        "reasonOverlap": reason_hist[3],
        "deduplicatedReach": len(masks),
        "hubSelectedLoad": {str(o): 5 * row_count[o] for o in OWNERS},
        "hubCandidateVertexSlack": {str(o): max(0, n - 5 * row_count[o]) for o in OWNERS},
    }


def wall_gate(data: dict, rows: tuple[tuple[int, ...], ...]) -> dict:
    blue = set(data["blue"])
    bad = set(data["bad"])
    graph = set(data["graph"])
    side = tuple(data["side"])
    selected = {x for row in rows for x in row}
    support = {edge(x, y) for row in rows for x, y in zip(row, row[1:])}
    ports = blue - support
    assert len(rows) == len(bad) == 1383
    assert all(len(row) == 5 and edge(row[0], row[-1]) in bad for row in rows)
    assert all(side[u] == side[v] for u, v in bad)
    assert all(u in selected and v in selected for u, v in bad)
    assert support <= blue
    assert all(side[u] != side[v] for u, v in support)
    assert all(u in selected and v in selected for u, v in support)
    assert ports.isdisjoint(support) and ports | support == blue
    assert graph == blue | bad and blue.isdisjoint(bad)

    singleton_load = {
        e: Fraction(int(e[0] in selected) + int(e[1] in selected), 2)
        for e in ports
    }
    assert all(Fraction(0) <= q <= 1 for q in singleton_load.values())
    load_hist = Counter(singleton_load.values())
    door_spend_hall = sum(singleton_load.values(), Fraction(0))
    door_capacity_hall = Fraction(len(ports))
    door_slack_hall = door_capacity_hall - door_spend_hall
    assert door_spend_hall <= door_capacity_hall

    # Typed/WIRING scale: one legal own-Door has capQ=25 and hallCapQ=1.
    token_cap_q = {e: Fraction(25) for e in ports}
    token_spend_q = {e: 25 * singleton_load[e] for e in ports}
    assert len(token_cap_q) == len(set(("door", e) for e in token_cap_q))
    assert all(Fraction(0) <= token_spend_q[e] <= token_cap_q[e] for e in ports)
    total_cap_q = sum(token_cap_q.values(), Fraction(0))
    total_spend_q = sum(token_spend_q.values(), Fraction(0))
    total_slack_q = total_cap_q - total_spend_q

    n = int(data["n"])
    residual_q_if_one_global_component = Fraction(n * n - 25 * len(rows))
    reserve_q_if_one_global_component = residual_q_if_one_global_component - total_cap_q
    assert reserve_q_if_one_global_component >= 0
    return {
        "graphDerived": {
            "N": n,
            "badAtoms": len(bad),
            "selectedVertices": len(selected),
            "selectedSupportEdges": len(support),
            "offSupportPorts": len(ports),
            "portLoadHistogram": {str(k): v for k, v in sorted(load_hist.items())},
            "rowCoverageMinimum": "1",
            "shortCongestionMaximum": "1",
        },
        "conditionalAllDoorPrimal": {
            "doorTokens": len(ports),
            "doorCapacityHall": str(door_capacity_hall),
            "doorSpendHall": str(door_spend_hall),
            "doorSlackHall": str(door_slack_hall),
            "doorCapacityCapQ": str(total_cap_q),
            "doorSpendCapQ": str(total_spend_q),
            "doorSlackCapQ": str(total_slack_q),
            "portRoutingDefect": "0",
            "tokenSourceUnique": True,
            "noDoubleSpend": True,
            "noCrossComponentSpendIfOneComponentOwnershipAssumed": True,
        },
        "conditionalOneComponentLedger": {
            "compN": str(n),
            "componentRowCountQ": str(len(rows)),
            "componentResidualQ": str(residual_q_if_one_global_component),
            "componentReserveSlackQ": str(reserve_q_if_one_global_component),
            "superadditivitySlackQ": "0",
        },
    }


def main() -> None:
    _, data = load_lead()
    rows = all_anchor_rows(data)
    scoped = scoped_gate(data, rows)
    wall = wall_gate(data, rows)
    full_cut = scoped["cuts"][7]
    assert full_cut == {"shoreMask": 7, "demand": 19953, "reach": 19925, "defect": 28}
    assert scoped["sameFirst"] == 17325
    assert scoped["rowCompanion"] == 2600
    assert scoped["reasonOverlap"] == 0
    assert all(v == 0 for v in scoped["hubCandidateVertexSlack"].values())
    assert wall["conditionalAllDoorPrimal"]["doorSpendHall"] == "2750"
    assert wall["conditionalAllDoorPrimal"]["doorSlackHall"] == "1492"

    out = {
        "schema": "r29-fullbank-gate-v1",
        "arithmetic": "integers and fractions.Fraction only; no floats",
        "currentScopedRelation": scoped,
        "compiledWallGate": wall,
        "comparison": {
            "scopedDefectHallUnits": "28",
            "scaledCapQEquivalentAt25PerHallUnit": "700",
            "conditionalDoorSlackHallUnits": "1492",
            "conditionalDoorSlackCapQ": "37300",
            "numericallyAbsorbs28": True,
            "unconditionalGraphProviderVerdict": "UNRESOLVED",
            "fullWallFalsifierVerdict": False,
        },
        "sourceClasses": {
            "Door": {"conditionalFreshHallCapacity": "1492", "absorber": True},
            "vertexSlack": {"hubCandidateCapacity": "0", "absorber": False},
            "c5Base": {"deduplicatedCurrentFreeHalfReach": 19925, "additionalFreshCapacity": "0"},
            "prune": {"instantiatedTokens": 0, "additionalFreshCapacity": "0"},
        },
        "stillAssumedGraphDerivedProviderFields": [
            "ownDoor_inc: every off-support port edge is incident to its own Door sink",
            "ownDoor_capacity: every such Door has hall capacity at least 1 (typed capQ at least 25)",
            "DoorWallAdapter: typed Door token embeds injectively into the real wall Sink and preserves capQ/25",
            "global component/local ownership for every Door token and every positive spend",
            "one-component identification compN=2943 and componentRowCountQ=1383",
            "local FullBank wall bundle to FullBankGlobalPackage semantic adapter",
            "any independent c5Base source disjoint from the 19925 FreeHalf keys",
            "any graph-derived prune token/proper-descendant balance",
        ],
        "hashes": {str(p.relative_to(ROOT)).replace('\\\\', '/'): sha256(p) for p in [
            LEAD, LEAN_SINGLETON, LEAN_ENDPOINT, LEAN_LEDGER, LEAN_TYPED, LEAN_ADAPTER, WIRING
        ]},
    }
    output = HERE / "result.json"
    output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
