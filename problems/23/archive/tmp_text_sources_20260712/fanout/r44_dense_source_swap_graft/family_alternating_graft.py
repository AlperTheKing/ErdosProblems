"""Exact search for an active, collision-loaded R39 family-alternating rotor.

The N29 R42 source-swap cage is retained only as a stricter two-state control.
This driver instead starts from the exact R39 square with rows A_m,A_v,B_x,B_y.
Every central detour is audited under the corrected R37 profile: one entering
edge is active/off-support and the other was already selected support.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R42_SOURCE = ROOT / "tmp" / "fanout" / "r42_source_swap_hunt" / "source_swap_hunt.py"
_spec = importlib.util.spec_from_file_location("r42_control", R42_SOURCE)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load R42 control")
r42 = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = r42
_spec.loader.exec_module(r42)
p5 = r42.p5
fullbank = r42.fullbank


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class GraftSpec:
    pin_mask: int
    traffic_mode: str
    traffic_multiplicity: int
    lock_mode: str


@dataclass(frozen=True)
class Cage:
    n: int
    names: tuple[str, ...]
    blue: frozenset[tuple[int, int]]
    bad: frozenset[tuple[int, int]]
    side_zero: frozenset[int]
    core: dict[str, int]
    named_rows: dict[str, tuple[int, ...]]
    spec: GraftSpec


def build_cage(spec: GraftSpec) -> Cage:
    """Build the R39 square, selectable active pin, and symmetric traffic."""
    names: list[str] = []
    lookup: dict[str, int] = {}
    side_zero: set[int] = set()

    def add(name: str, zero: bool) -> int:
        if name in lookup:
            raise AssertionError(name)
        value = len(names)
        lookup[name] = value
        names.append(name)
        if zero:
            side_zero.add(value)
        return value

    a = add("a", False)
    x = add("x", True)
    m = add("m", False)
    y = add("y", True)
    b = add("b", False)
    p = add("p", True)
    v = add("v", False)
    q = add("q", True)
    core = {"a": a, "x": x, "m": m, "y": y, "b": b, "p": p, "v": v, "q": q}
    blue = {edge(a, x), edge(x, m), edge(m, y), edge(y, b), edge(p, m), edge(x, v), edge(v, q), edge(y, v)}
    bad = {edge(a, b), edge(p, q)}
    named_rows = {
        "A_m": (a, x, m, y, b),
        "A_v": (a, x, v, y, b),
        "B_x": (p, m, x, v, q),
        "B_y": (p, m, y, v, q),
    }

    def background(tag: str, anchor: int, anchor_zero: bool) -> None:
        h = add(f"bg_h_{tag}", not anchor_zero)
        i = add(f"bg_i_{tag}", not anchor_zero)
        j = add(f"bg_j_{tag}", anchor_zero)
        k = add(f"bg_k_{tag}", not anchor_zero)
        blue.update((edge(h, anchor), edge(anchor, i), edge(i, j), edge(j, k)))
        bad.add(edge(h, k))

    # A selected C5 row for s--t and a disjoint selected-background family make
    # every interior of the six-edge spine selected while leaving the spine off-support.
    s = add("s", False)
    g1 = add("g1", True)
    g2 = add("g2", False)
    g3 = add("g3", True)
    t = add("t", False)
    blue.update((edge(s, g1), edge(g1, g2), edge(g2, g3), edge(g3, t)))
    bad.add(edge(s, t))
    u1 = add("u1", True)
    u2 = add("u2", False)
    c = add("c", True)
    u3 = add("u3", False)
    u4 = add("u4", True)
    blue.update((edge(s, u1), edge(u1, u2), edge(u2, c), edge(c, u3), edge(u3, u4), edge(u4, t)))
    for tag, anchor, zero in (("u1", u1, True), ("u2", u2, False), ("c", c, True), ("u3", u3, False), ("u4", u4, True)):
        background(tag, anchor, zero)

    pin_data = (("x", x, True), ("y", y, True), ("m", m, False), ("v", v, False))
    for index, (tag, owner, owner_zero) in enumerate(pin_data):
        if not spec.pin_mask & (1 << index):
            continue
        if owner_zero:
            bridge = add(f"pin_{tag}", False)
            blue.update((edge(owner, bridge), edge(bridge, c)))
            background(f"pin_{tag}", bridge, False)
        else:
            # A direct c-m and c-v pair creates the spurious B_c row
            # p-m-c-v-q.  Use symmetric selected length-three branches instead.
            first = add(f"pin_{tag}_1", True)
            second = add(f"pin_{tag}_2", False)
            blue.update((edge(owner, first), edge(first, second), edge(second, c)))
            background(f"pin_{tag}_1", first, True)
            background(f"pin_{tag}_2", second, False)

    if spec.traffic_mode not in {"diagonal", "shared"}:
        raise ValueError(f"unknown traffic mode {spec.traffic_mode}")
    if spec.lock_mode not in {"none", "traffic_l6"}:
        raise ValueError(f"unknown lock mode {spec.lock_mode}")
    if spec.traffic_multiplicity < 1:
        raise ValueError("traffic multiplicity must be positive")
    for owner_tag in ("x", "y", "m", "v"):
        owner = core[owner_tag]
        owner_zero = owner in side_zero
        shared_r: int | None = None
        if spec.traffic_mode == "shared":
            shared_r = add(f"tr_{owner_tag}", owner_zero)
        for index in range(spec.traffic_multiplicity):
            h = add(f"th_{owner_tag}_{index}", not owner_zero)
            u = add(f"tu_{owner_tag}_{index}", not owner_zero)
            r = shared_r if shared_r is not None else add(f"tr_{owner_tag}_{index}", owner_zero)
            k = add(f"tk_{owner_tag}_{index}", not owner_zero)
            blue.update((edge(h, owner), edge(owner, u), edge(u, r), edge(r, k)))
            bad.add(edge(h, k))
            if spec.lock_mode == "traffic_l6":
                lock = [add(f"tl_{owner_tag}_{index}_{step}", owner_zero if (step % 2) == 0 else (not owner_zero)) for step in range(5)]
                blue.update(edge(left, right) for left, right in zip((h, *lock), (*lock, k)))
    return Cage(len(names), tuple(names), frozenset(blue), frozenset(bad), frozenset(side_zero), core, named_rows, spec)


def structural_gate(cage: Cage) -> dict:
    all_edges = cage.blue | cage.bad
    displayed = sum((u in cage.side_zero) != (v in cage.side_zero) for u, v in all_edges)
    maximum = r42.maxcut_exact(cage.n, all_edges)
    return {
        "n": cage.n,
        "edgeCount": len(all_edges),
        "blueEdges": len(cage.blue),
        "badEdges": len(cage.bad),
        "triangleFree": r42.triangle_free(cage.n, all_edges),
        "blueConnected": r42.is_connected(cage.n, cage.blue),
        "displayedCut": displayed,
        "blueCrossesDisplayedCut": all((u in cage.side_zero) != (v in cage.side_zero) for u, v in cage.blue),
        "badMonochromaticInDisplayedCut": all((u in cage.side_zero) == (v in cage.side_zero) for u, v in cage.bad),
        "maxCut": maximum,
        "displayedCutIsMaximum": maximum["exactMaxCut"] == displayed,
    }


def row_database(cage: Cage) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[tuple[int, ...], ...], ...]]:
    bads = tuple(sorted(cage.bad))
    return bads, tuple(r42.shortest_rows(cage.n, cage.blue, *bad) for bad in bads)


def solve_production(ctx: p5.GraphContext, state: p5.TupleState) -> dict:
    return r42.solve_production(ctx, state)


def state_record(ctx: p5.GraphContext, rows: tuple[tuple[int, ...], ...], choice: tuple[int, ...]) -> dict:
    state = p5.reconstruct_state(ctx, rows)
    solved = solve_production(ctx, state)
    return {"choice": choice, "rows": rows, "defect": solved["defect"], "demand": solved["demand"], "matched": solved["matched"], "_state": state, "_solved": solved}


def source_status(solved: dict, source: int) -> str:
    if source in solved["used"]:
        return "MATCHED"
    return "COMPONENT_OR_BASE_BLOCKED" if source not in solved["finalRelation"] else "UNUSED_ELIGIBLE"


def common_blue_probes(n: int, ctx: p5.GraphContext, state: p5.TupleState, solved: dict) -> set[int]:
    out: set[int] = set()
    active = r42.adjacency(n, state.demanded_active_edges)
    support = r42.adjacency(n, state.support)
    owner_index = {owner: index for index, owner in enumerate(solved["owners"])}
    for owner in state.active_vertices:
        if owner not in owner_index:
            continue
        bit = 1 << owner_index[owner]
        for left in active[owner]:
            for right in support[owner]:
                if left == right or state.pair[left][right] != 0 or ctx.sigma_pair[left][right] < 2:
                    continue
                for first, second in ((left, right), (right, left)):
                    for half in (0, 1):
                        source = p5.source_id(n, first, second, half)
                        if not p5._reserved(state, first, second, half) and solved["masks"]["p2"].get(source, 0) & bit:
                            out.add(source)
    return out


def detour(cage: Cage, ctx: p5.GraphContext, source: dict, target: dict) -> dict | None:
    changes = [i for i, (left, right) in enumerate(zip(source["rows"], target["rows"])) if left != right]
    if len(changes) != 1:
        return None
    index = changes[0]
    old_row, new_row = source["rows"][index], target["rows"][index]
    positions = [i for i, (left, right) in enumerate(zip(old_row, new_row)) if left != right]
    if positions != [2] or old_row[0] != new_row[0] or old_row[1] != new_row[1] or old_row[3] != new_row[3] or old_row[4] != new_row[4]:
        return None
    old, new = source["_state"], target["_state"]
    old_middle, new_middle = old_row[2], new_row[2]
    ends = (old_row[1], old_row[3])
    entering = {edge(ends[0], new_middle), edge(new_middle, ends[1])}
    leaving = {edge(ends[0], old_middle), edge(old_middle, ends[1])}
    active_entering = entering & old.demanded_active_edges
    supported_entering = entering & old.support
    if not active_entering:
        return None
    newly_freed: set[int] = set()
    for z in ends:
        if old.pair[old_middle][z] > 0 and new.pair[old_middle][z] == 0:
            for left, right in ((old_middle, z), (z, old_middle)):
                for half in (0, 1):
                    newly_freed.add(p5.source_id(cage.n, left, right, half))
    statuses = {key: source_status(target["_solved"], key) for key in newly_freed}
    used = target["_solved"]["used"]
    probes = common_blue_probes(cage.n, ctx, new, target["_solved"])
    outside = set(target["_solved"]["masks"]["p4"]) & set(target["_solved"]["finalRelation"]) - used
    quiescent = set(target["_solved"]["masks"]["p5"]) & set(target["_solved"]["finalRelation"]) - used
    turnover = {key for key, status in statuses.items() if status == "UNUSED_ELIGIBLE"}
    endpoint = (probes - used) - turnover
    outside -= turnover | endpoint
    quiescent -= turnover | endpoint | outside
    union = turnover | endpoint | outside | quiescent
    genuine_new = entering - old.support
    unique_old = leaving - new.support
    support_delta = len(new.support) - len(old.support)
    if support_delta != len(genuine_new) - len(unique_old):
        raise AssertionError("support identity failed")
    return {
        "from": list(source["choice"]), "to": list(target["choice"]), "rowIndex": index,
        "oldMiddle": old_middle, "newMiddle": new_middle,
        "enteringActiveEdges": [list(value) for value in sorted(active_entering)],
        "enteringSupportedEdges": [list(value) for value in sorted(supported_entering)],
        "oneNewOneSupported": len(active_entering) == 1 and len(supported_entering) == 1,
        "supportDelta": support_delta, "genuinelyNewSupportEdges": len(genuine_new), "uniqueOldSupportEdges": len(unique_old),
        "newlyFreedKeys": [list(p5.decode_source(cage.n, key)) for key in sorted(newly_freed)],
        "targetStatus": [{"source": list(p5.decode_source(cage.n, key)), "status": statuses[key]} for key in sorted(statuses)],
        "exposure": {"turnover": len(turnover), "endpointSameSideCommonBlue": len(endpoint), "outsideP4": len(outside), "quiescentP5": len(quiescent), "total": len(union)},
        "turnoverAllMatchedOrBlocked": not turnover,
    }


def tarjan(nodes: Iterable[tuple[int, ...]], arcs: dict[tuple[int, ...], set[tuple[int, ...]]]) -> list[list[tuple[int, ...]]]:
    index = 0
    order: dict[tuple[int, ...], int] = {}
    low: dict[tuple[int, ...], int] = {}
    stack: list[tuple[int, ...]] = []
    live: set[tuple[int, ...]] = set()
    result: list[list[tuple[int, ...]]] = []
    def visit(node: tuple[int, ...]) -> None:
        nonlocal index
        order[node] = low[node] = index
        index += 1
        stack.append(node)
        live.add(node)
        for nxt in sorted(arcs[node]):
            if nxt not in order:
                visit(nxt)
                low[node] = min(low[node], low[nxt])
            elif nxt in live:
                low[node] = min(low[node], order[nxt])
        if low[node] == order[node]:
            component: list[tuple[int, ...]] = []
            while True:
                nxt = stack.pop()
                live.remove(nxt)
                component.append(nxt)
                if nxt == node:
                    break
            result.append(sorted(component))
    for node in sorted(nodes):
        if node not in order:
            visit(node)
    return result


def evaluate(spec: GraftSpec, tuple_cap: int) -> dict:
    cage = build_cage(spec)
    structural = structural_gate(cage)
    bads, families = row_database(cage)
    family_sizes = tuple(len(family) for family in families)
    row_db = {"bads": [list(bad) for bad in bads], "familySizes": list(family_sizes), "completeFamilies": [[[v for v in row] for row in family] for family in families]}
    named_present = {name: row in {item for family in families for item in family} for name, row in cage.named_rows.items()}
    record = {"spec": {"pinMask": spec.pin_mask, "trafficMode": spec.traffic_mode, "trafficMultiplicity": spec.traffic_multiplicity, "lockMode": spec.lock_mode}, "structural": structural, "rowDatabase": row_db, "rotorRowsPreserved": named_present}
    if not (structural["triangleFree"] and structural["blueConnected"] and structural["displayedCutIsMaximum"] and structural["blueCrossesDisplayedCut"] and structural["badMonochromaticInDisplayedCut"]):
        record["gate"] = "STRUCTURAL_REJECT"
        return record
    if spec.pin_mask != 15:
        record["gate"] = "ACTIVE_PIN_REJECT"
        return record
    if not all(families):
        record["gate"] = "SHORTEST_ROW_REJECT"
        return record
    tuple_count = math.prod(family_sizes)
    record["tupleCount"] = tuple_count
    if tuple_count > tuple_cap:
        record["gate"] = "TUPLE_CAP_REJECT"
        return record
    ctx = p5.make_graph_context(cage.n, cage.blue, cage.bad)
    states: dict[tuple[int, ...], dict] = {}
    for choice in itertools.product(*(range(size) for size in family_sizes)):
        rows = tuple(families[i][choice[i]] for i in range(len(bads)))
        states[choice] = state_record(ctx, rows, choice)
    minimum = min(state["defect"] for state in states.values())
    arcs = {choice: set() for choice in states}
    detours: list[dict] = []
    for choice, source in states.items():
        for index, size in enumerate(family_sizes):
            for alternative in range(size):
                if alternative == choice[index]:
                    continue
                target_choice = (*choice[:index], alternative, *choice[index + 1:])
                target = states[target_choice]
                if target["defect"] != source["defect"]:
                    continue
                step = detour(cage, ctx, source, target)
                if step is not None:
                    arcs[choice].add(target_choice)
                    detours.append(step)
    row_label = {row: name for name, row in cage.named_rows.items()}
    central = (bads.index(edge(cage.core["a"], cage.core["b"])), bads.index(edge(cage.core["p"], cage.core["q"])))
    desired = {"A_m/B_x", "A_m/B_y", "A_v/B_y", "A_v/B_x"}
    rotor_sccs = []
    hits = []
    for component in tarjan(states, arcs):
        labels = {f"{row_label.get(states[node]['rows'][central[0]], '?')}/{row_label.get(states[node]['rows'][central[1]], '?')}" for node in component}
        if not desired <= labels:
            continue
        members = set(component)
        internal = [step for step in detours if tuple(step["from"]) in members and tuple(step["to"]) in members and step["rowIndex"] in central]
        outgoing = sorted({target for node in members for target in arcs[node] if target not in members})
        level = states[component[0]]["defect"]
        lower = sum(state["defect"] < level for state in states.values())
        exposure = Counter()
        for step in internal:
            exposure.update(step["exposure"])
        active = all(set(cage.core[key] for key in ("x", "y", "m", "v")) <= states[node]["_state"].active_vertices for node in component)
        exact_profile = bool(internal) and all(step["oneNewOneSupported"] for step in internal)
        sink = not outgoing
        hit = level > 0 and level == minimum and sink and active and exact_profile and exposure["total"] == 0 and lower == 0
        item = {"members": [list(node) for node in component], "defect": level, "labels": sorted(labels), "activePin": active, "oneNewOneSupported": exact_profile, "outgoingEqualDefectDetours": [list(node) for node in outgoing], "internalDetours": internal, "exposure": {key: exposure[key] for key in ("turnover", "endpointSameSideCommonBlue", "outsideP4", "quiescentP5", "total")}, "selectorTradeLowerTupleCount": lower, "sink": sink, "hit": hit}
        rotor_sccs.append(item)
        if hit:
            hits.append(item)
    min_states = [state for state in states.values() if state["defect"] == minimum]
    owner_collisions = {key: [state["_state"].collision.get(cage.core[key], 0) for state in min_states] for key in ("x", "y", "m", "v")}
    record.update({"gate": "FULL_GRAPH_EVALUATED", "labels": list(cage.names), "blue": [list(value) for value in sorted(cage.blue)], "bad": [list(value) for value in bads], "minimumCanonicalCollisionDefect": minimum, "minimalStateCount": len(min_states), "trafficCollisionAtMinimum": {key: {"min": min(values), "max": max(values)} for key, values in owner_collisions.items()}, "supportDeltaHistogram": dict(sorted(Counter(step["supportDelta"] for step in detours).items())), "rotorSccs": rotor_sccs, "hitSccs": hits})
    return record


def evaluate_worker(args: tuple[GraftSpec, int]) -> dict:
    return evaluate(*args)


def graph_phase(workers: int, traffic_max: int, tuple_cap: int) -> dict:
    specs = []
    for pin in range(16):
        for mode in ("diagonal", "shared"):
            upper = traffic_max if mode == "diagonal" else min(traffic_max, 2)
            for multiplicity in range(1, upper + 1):
                for lock in ("none", "traffic_l6"):
                    specs.append(GraftSpec(pin, mode, multiplicity, lock))
    args = [(spec, tuple_cap) for spec in specs]
    if workers == 1:
        records = [evaluate_worker(arg) for arg in args]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            records = list(pool.map(evaluate_worker, args))
    counter = Counter(record["gate"] for record in records)
    hits = [hit for record in records for hit in record.get("hitSccs", [])]
    full = [record for record in records if record["gate"] == "FULL_GRAPH_EVALUATED"]
    return {"space": {"pinMasks": list(range(16)), "trafficModes": ["diagonal", "shared"], "trafficMultiplicity": {"diagonal": [1, traffic_max], "shared": [1, min(traffic_max, 2)]}, "lockModes": ["none", "traffic_l6"], "candidateCount": len(specs), "rowTupleCap": tuple_cap, "workers": workers}, "counts": dict(sorted(counter.items())), "records": records, "hitCount": len(hits), "verdict": "GRAPH_HIT" if hits else "BOUNDED_NO_GRAPH_HIT", "nonConclusion": "This is a finite exact graft search, not a proof outside the enumerated traffic/pin/lock family."}


def build_manifest(workers: int, traffic_max: int, tuple_cap: int) -> dict:
    if not 1 <= workers <= 16:
        raise ValueError("workers must be in 1..16")
    if not 1 <= traffic_max <= 3:
        raise ValueError("traffic-max must be in 1..3")
    if tuple_cap < 4:
        raise ValueError("tuple cap too small")
    payload = {"schema": "R44_FAMILY_ALTERNATING_GRAFT_V1", "arithmetic": "Python integers, finite sets, complete shortest-row enumeration, exact integer bucket-elimination maxcut", "workers": workers, "control": {"r42N29": "c15f16a047885e61675b4797713f9a96af68d91ddb47f62bab9b8f2a0a4842f5", "role": "strict support-constant two-state control only"}, "productionContract": {"relations": ["P1", "P2/common-blue sigma>=2", "P3", "strict-P4", "P5"], "coherence": "BaseKeyComponentCoherent", "exposure": ["newly-freed turnover", "endpoint same-side/common-blue", "outside P4", "quiescent P5"], "detourProfile": "one entering active/off-support edge plus one already-supported entering edge"}, "inputs": {"family_alternating_graft.py": sha_file(HERE / "family_alternating_graft.py"), "r42_source_swap_hunt.py": sha_file(R42_SOURCE), "p5_core.py": sha_file(ROOT / "tmp" / "fanout" / "p5_n12_census" / "p5_core.py"), "fullbank_core.py": sha_file(ROOT / "tmp" / "fanout" / "r32_n12_fullbank" / "fullbank_core.py")}, "maxCutEngineSelfCheck": r42.maxcut_engine_self_check(), "graph": graph_phase(workers, traffic_max, tuple_cap)}
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--traffic-max", type=int, default=2)
    parser.add_argument("--row-tuple-cap", type=int, default=200000)
    parser.add_argument("--output", type=Path, default=HERE / "manifest.json")
    args = parser.parse_args(argv)
    payload = build_manifest(args.workers, args.traffic_max, args.row_tuple_cap)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({"canonicalPayloadSha256": payload["canonicalPayloadSha256"], "graphHits": payload["graph"]["hitCount"], "graphVerdict": payload["graph"]["verdict"], "graphGateCounts": payload["graph"]["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())