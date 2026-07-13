"""Exact real-cage search for the R38 saturated neutral square rotor.

The canonical cage starts with the blue square x-m0-y-m1-x and one anchored
bad atom whose complete row family contains a-x-mi-y-b.  For each middle and
each retained vertex z in {a,x,y,b}, an anchored background C5 row adds a
second co-occurrence.  The program reconstructs the complete shortest-row
database, enumerates every row tuple, solves the production five-pattern
coherent collision matching exactly, and tests neutral rotor exposure.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
FULLBANK = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
for path in (P5, FULLBANK):
    sys.path.insert(0, str(path))

import p5_core as p5  # noqa: E402
from fullbank_core import (  # noqa: E402
    coherent_collision_match,
    collision_owners,
    project_masks,
)


A, X, M0, Y, B, M1 = range(6)
CORE = (A, X, M0, Y, B, M1)
RETAINED = (A, X, Y, B)
MIDDLES = (M0, M1)


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def merge_relations(*relations: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            out[source] = out.get(source, 0) | mask
    return out


def build_cage() -> dict:
    """Build the minimal anchored multiplicity-two background template."""
    next_vertex = 6
    rows = [(A, X, M0, Y, B)]
    bad = [edge(A, B)]
    labels = ["producer"]
    gadgets = []

    for middle in MIDDLES:
        for z in RETAINED:
            p, u, q = range(next_vertex, next_vertex + 3)
            next_vertex += 3
            if (middle in (M0, M1)) == (z in (A, B)):
                row = (p, middle, u, z, q)
            else:
                # Opposite-shore pairs are adjacent in the square and hence
                # must be consecutive in every induced shortest row.
                row = (p, middle, z, u, q)
            rows.append(row)
            bad.append(edge(p, q))
            labels.append(f"background_m{middle}_z{z}")
            gadgets.append({"middle": middle, "z": z, "fresh": [p, u, q]})

    blue = {edge(x, y) for row in rows for x, y in zip(row, row[1:])}
    blue.update({edge(X, M1), edge(M1, Y)})
    # One extra internally disjoint a-b geodesic is a cut lock for the central
    # bad atom.  It removes the unique +1 recut of the raw background template.
    lock = tuple(range(next_vertex, next_vertex + 3))
    next_vertex += 3
    lock_row = (A, lock[0], lock[1], lock[2], B)
    blue.update(edge(x, y) for x, y in zip(lock_row, lock_row[1:]))
    gadgets.append({"middle": A, "z": B, "fresh": list(lock)})
    return {
        "n": next_vertex,
        "blue": blue,
        "bad": set(bad),
        "displayedRows": tuple(rows),
        "labels": tuple(labels),
        "gadgets": gadgets,
        "lockRows": (lock_row,),
        "sideZero": {A, M0, B, M1, *(u for g in gadgets for u in [g["fresh"][1]])},
    }


def adjacency(n: int, edges) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    return adj


def connected(n: int, edges) -> bool:
    adj = adjacency(n, edges)
    seen = {0}
    todo = [0]
    while todo:
        x = todo.pop()
        for y in adj[x] - seen:
            seen.add(y)
            todo.append(y)
    return len(seen) == n


def triangle_free(n: int, edges) -> bool:
    adj = adjacency(n, edges)
    return not any(adj[x] & adj[y] for x, y in edges)


def shortest_rows(n: int, blue, start: int, finish: int) -> tuple[tuple[int, ...], ...]:
    adj = adjacency(n, blue)
    dist = [-1] * n
    dist[start] = 0
    todo = deque([start])
    while todo:
        x = todo.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                todo.append(y)
    if dist[finish] != 4:
        return ()
    rows = []

    def visit(path: tuple[int, ...]) -> None:
        x = path[-1]
        if len(path) == 5:
            if x == finish:
                rows.append(path)
            return
        for y in sorted(adj[x]):
            if y not in path and dist[y] == dist[x] + 1:
                visit((*path, y))

    visit((start,))
    return tuple(sorted(rows))


def maxcut_by_core_dp(cage: dict) -> dict:
    """Exact max-cut by enumerating six core bits and independent gadgets."""
    n = cage["n"]
    all_edges = cage["blue"] | cage["bad"]
    fresh = set(range(n)) - set(CORE)
    # Fresh sets of distinct gadgets are disjoint and have no cross edges.
    gadget_sets = [set(g["fresh"]) for g in cage["gadgets"]]
    assert sum(map(len, gadget_sets)) == len(fresh)
    assert not any(gadget_sets[i] & gadget_sets[j]
                   for i in range(len(gadget_sets)) for j in range(i))
    core_edges = {e for e in all_edges if e[0] in CORE and e[1] in CORE}
    best = -1
    best_core = None
    table = []
    for core_mask in range(1 << len(CORE)):
        side = {v: (core_mask >> CORE.index(v)) & 1 for v in CORE}
        value = sum(side[x] != side[y] for x, y in core_edges)
        local_values = []
        for vertices in gadget_sets:
            incident = {e for e in all_edges if e[0] in vertices or e[1] in vertices}
            local_best = -1
            for local_mask in range(1 << len(vertices)):
                local_side = dict(side)
                for i, v in enumerate(sorted(vertices)):
                    local_side[v] = (local_mask >> i) & 1
                local_best = max(local_best, sum(local_side[x] != local_side[y] for x, y in incident))
            value += local_best
            local_values.append(local_best)
        table.append(value)
        if value > best:
            best, best_core = value, core_mask
    displayed = len(cage["blue"])
    return {
        "exactMaxcut": best,
        "displayedCut": displayed,
        "isMaximum": best == displayed,
        "coreAssignments": 1 << len(CORE),
        "localAssignmentsPerGadget": 8,
        "bestCoreMask": best_core,
        "valueHistogram": dict(sorted(Counter(table).items())),
    }


def matching(ctx, state) -> dict:
    owners = collision_owners(state)
    masks = p5.relation_masks(ctx, state)
    raw = project_masks(state, masks["five"], owners)
    result = coherent_collision_match(ctx, state, owners, raw, ())
    used = {source for source, _ in result.assignment}
    return {
        "owners": owners,
        "raw": raw,
        "result": result,
        "used": used,
        "demand": result.demand,
        "matched": result.matched,
        "defect": result.defect,
        "coherenceLabels": len(result.base_labels),
        "searchNodes": result.search_nodes,
    }


def attachment_audit(ctx, state, match) -> dict:
    active = adjacency(ctx.n, state.demanded_active_edges)
    support = adjacency(ctx.n, state.support)
    probes = []
    generated = set()
    all_weak = True
    classes = []
    owner_index = {owner: i for i, owner in enumerate(match["owners"])}
    for owner in sorted(state.active_vertices):
        xs = sorted(active[owner])
        ys = sorted(support[owner])
        local = []
        for x in xs:
            for y in ys:
                if x == y:
                    continue
                sigma = ctx.sigma_pair[x][y]
                count = state.pair[x][y]
                local.append((x, y, count, sigma))
                all_weak &= count == 0 and sigma in (0, 1)
                if count == 0 and sigma >= 2 and owner in owner_index:
                    bit = 1 << owner_index[owner]
                    for half in (0, 1):
                        sid = p5.source_id(ctx.n, x, y, half)
                        if match["raw"].get(sid, 0) & bit:
                            generated.add(sid)
        if local:
            x_tight = bool(xs) and all(p5.sigma_value(ctx, 1 << x) == 0 for x in xs)
            y_tight = bool(ys) and all(p5.sigma_value(ctx, 1 << y) == 0 for y in ys)
            classes.append({
                "owner": owner,
                "X": xs,
                "Y": ys,
                "XSingletonCutTight": x_tight,
                "YSingletonCutTight": y_tight,
            })
        probes.extend(local)
    necessary = (not probes or not all_weak or all(
        c["XSingletonCutTight"] or c["YSingletonCutTight"] for c in classes
    ))
    unused = sorted(generated - match["used"])
    return {
        "probeCount": len(probes),
        "allWeak": bool(probes) and all_weak,
        "singletonCutTightNecessaryCondition": necessary,
        "classes": classes,
        "productionGeneratedSources": sorted(generated),
        "unusedProductionGeneratedSources": unused,
    }


def transition_escape(ctx, old, target, old_middle: int, target_match) -> dict:
    created = set()
    singleton_z = []
    for z in RETAINED:
        if old.pair[old_middle][z] == 1:
            singleton_z.append(z)
            for sx, sy in ((old_middle, z), (z, old_middle)):
                for half in (0, 1):
                    created.add(p5.source_id(ctx.n, sx, sy, half))
    singleton_row = old.row_count[old_middle] == 1
    if singleton_row:
        for half in (0, 1):
            created.add(p5.source_id(ctx.n, old_middle, old_middle, half))
    eligible = sorted(source for source in created if source in target_match["raw"])
    unused = sorted(set(eligible) - target_match["used"])
    return {
        "oldMiddle": old_middle,
        "singletonRetainedVertices": singleton_z,
        "rowCountOne": singleton_row,
        "rawNewFreeCount": 4 * len(singleton_z) + 2 * int(singleton_row),
        "eligibleTargetSources": eligible,
        "unusedEligibleTargetSources": unused,
    }


def canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "manifest.json")
    parser.add_argument("--tuple-bound", type=int, default=2_000_000)
    args = parser.parse_args()

    cage = build_cage()
    n = cage["n"]
    all_edges = cage["blue"] | cage["bad"]
    structural = {
        "n": n,
        "edges": len(all_edges),
        "blueEdges": len(cage["blue"]),
        "badEdges": len(cage["bad"]),
        "triangleFree": triangle_free(n, all_edges),
        "blueConnected": connected(n, cage["blue"]),
        "maxcut": maxcut_by_core_dp(cage),
    }
    assert structural["triangleFree"] and structural["blueConnected"]
    assert structural["maxcut"]["isMaximum"]

    bads = tuple(sorted(cage["bad"]))
    families = tuple(shortest_rows(n, cage["blue"], *bad) for bad in bads)
    assert all(families)
    family_sizes = tuple(map(len, families))
    tuple_count = math.prod(family_sizes)
    if tuple_count > args.tuple_bound:
        raise RuntimeError(f"tuple count {tuple_count} exceeds bound {args.tuple_bound}")
    producer_atom = bads.index(edge(A, B))
    q0 = (A, X, M0, Y, B)
    q1 = (A, X, M1, Y, B)
    producer_rows = families[producer_atom]
    assert q0 in producer_rows and q1 in producer_rows

    ctx = p5.make_graph_context(n, cage["blue"], cage["bad"])
    records = []
    minimum = None
    for choice in itertools.product(*(range(size) for size in family_sizes)):
        rows = tuple(families[i][choice[i]] for i in range(len(bads)))
        state = p5.reconstruct_state(ctx, rows)
        solved = matching(ctx, state)
        audit = attachment_audit(ctx, state, solved)
        middle = rows[producer_atom][2] if rows[producer_atom] in (q0, q1) else None
        saturation = None
        if middle in MIDDLES:
            saturation = {
                "middle": middle,
                "rowCount": state.row_count[middle],
                "pairCounts": {str(z): state.pair[middle][z] for z in RETAINED},
                "multiplicitySaturated": (
                    state.row_count[middle] >= 2
                    and all(state.pair[middle][z] >= 2 for z in RETAINED)
                ),
            }
        record = {
            "choice": list(choice),
            "producerMiddle": middle,
            "defect": solved["defect"],
            "demand": solved["demand"],
            "matched": solved["matched"],
            "coherenceLabels": solved["coherenceLabels"],
            "matchingSearchNodes": solved["searchNodes"],
            "matchingAssignment": [[s, o] for s, o in solved["result"].assignment],
            "support": [list(e) for e in sorted(state.support)],
            "activeEdges": [list(e) for e in sorted(state.demanded_active_edges)],
            "saturation": saturation,
            "attachment": audit,
            "_state": state,
            "_matching": solved,
        }
        records.append(record)
        minimum = solved["defect"] if minimum is None else min(minimum, solved["defect"])

    minimal_indices = [i for i, r in enumerate(records) if r["defect"] == minimum]
    transitions = []
    for i in minimal_indices:
        left = records[i]
        if left["producerMiddle"] not in MIDDLES:
            continue
        for j in minimal_indices:
            right = records[j]
            if right["producerMiddle"] not in MIDDLES or left["producerMiddle"] == right["producerMiddle"]:
                continue
            diffs = [k for k, (a, b) in enumerate(zip(left["choice"], right["choice"])) if a != b]
            if diffs != [producer_atom]:
                continue
            old_middle = left["producerMiddle"]
            new_middle = right["producerMiddle"]
            old_state = left["_state"]
            target_state = right["_state"]
            support_retained = all(
                edge(old_middle, z) in target_state.support for z in (X, Y)
            )
            active_inverse = all(
                edge(old_middle, z) in target_state.demanded_active_edges for z in (X, Y)
            )
            escape = transition_escape(ctx, old_state, target_state, old_middle, right["_matching"])
            transitions.append({
                "from": i,
                "to": j,
                "oldMiddle": old_middle,
                "newMiddle": new_middle,
                "oldMultiplicitySaturated": left["saturation"]["multiplicitySaturated"],
                "oldSquareEdgesRetainedInTargetSupport": support_retained,
                "inverseMiddleHasRequiredActiveSquareEdges": active_inverse,
                "escape": escape,
            })

    rotor_edges = [t for t in transitions if t["oldMultiplicitySaturated"]]
    inverse_pairs = []
    by_pair = {(t["from"], t["to"]): t for t in rotor_edges}
    for key, transition in by_pair.items():
        reverse = by_pair.get((key[1], key[0]))
        if reverse and key[0] < key[1]:
            inverse_pairs.append({
                "states": list(key),
                "bothMultiplicitySaturated": True,
                "bothInverseActive": (
                    transition["inverseMiddleHasRequiredActiveSquareEdges"]
                    and reverse["inverseMiddleHasRequiredActiveSquareEdges"]
                ),
                "exposure": (
                    len(records[key[0]]["attachment"]["unusedProductionGeneratedSources"])
                    + len(records[key[1]]["attachment"]["unusedProductionGeneratedSources"])
                    + len(transition["escape"]["unusedEligibleTargetSources"])
                    + len(reverse["escape"]["unusedEligibleTargetSources"])
                ),
            })

    serial_records = []
    for record in records:
        serial_records.append({k: v for k, v in record.items() if not k.startswith("_")})
    exact_support_lemma = {
        "statement": (
            "If Q contains the blue edge m-x and n_omega(m,x)>=2, then after replacing Q, "
            "another selected shortest row still contains m,x. Because m-x is blue and rows are shortest, "
            "m,x are consecutive there; hence m-x remains selected support and cannot be an active edge."
        ),
        "checkedTransitions": len(rotor_edges),
        "failures": sum(not t["oldSquareEdgesRetainedInTargetSupport"] for t in rotor_edges),
    }
    witness = next((p for p in inverse_pairs if p["bothInverseActive"] and p["exposure"] == 0 and minimum > 0), None)
    prune_summary = {
        "allWeakStates": sum(r["attachment"]["allWeak"] for r in records),
        "allWeakSingletonCutTightFailures": sum(
            r["attachment"]["allWeak"]
            and not r["attachment"]["singletonCutTightNecessaryCondition"]
            for r in records
        ),
        "multiplicitySaturatedStates": sum(
            bool(r["saturation"] and r["saturation"]["multiplicitySaturated"])
            for r in records
        ),
        "multiplicitySaturatedWithAttachmentClass": sum(
            bool(
                r["saturation"] and r["saturation"]["multiplicitySaturated"]
                and r["attachment"]["classes"]
            )
            for r in records
        ),
        "cutTightClassAndMultiplicitySaturation": sum(
            bool(
                r["saturation"] and r["saturation"]["multiplicitySaturated"]
                and any(
                    c["XSingletonCutTight"] or c["YSingletonCutTight"]
                    for c in r["attachment"]["classes"]
                )
            )
            for r in records
        ),
    }
    payload = {
        "schema": "R41_REAL_SATURATED_NEUTRAL_SQUARE_ROTOR_V1",
        "arithmetic": "Python integers, finite sets, exhaustive finite products",
        "workers": 1,
        "productionRelation": ["P1", "P3", "commonBlue_sigma_ge_2", "strictP4", "P5"],
        "weakSigma01CountedAsExposure": False,
        "structural": structural,
        "coreLabels": {"a": A, "x": X, "m0": M0, "y": Y, "b": B, "m1": M1},
        "blue": [list(e) for e in sorted(cage["blue"])],
        "bad": [list(e) for e in bads],
        "completeFamilies": [[list(row) for row in family] for family in families],
        "familySizes": list(family_sizes),
        "tupleCount": tuple_count,
        "tuplesEnumerated": len(records),
        "canonicalCoherentOptimalMatchingsSolved": len(records),
        "minimumDefect": minimum,
        "defectMinimalTupleIndices": minimal_indices,
        "states": serial_records,
        "neutralProducerTransitions": transitions,
        "saturatedInversePairs": inverse_pairs,
        "singletonCutTightPrune": prune_summary,
        "supportRetentionLemma": exact_support_lemma,
        "exposureZeroWitness": witness,
        "verdict": "EXPOSURE_ZERO_WITNESS" if witness else "BOUNDED_ZERO_FAILURE_MANIFEST",
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "verdict": payload["verdict"],
        "n": n,
        "familySizes": family_sizes,
        "tuples": tuple_count,
        "minimumDefect": minimum,
        "transitions": len(transitions),
        "saturatedInversePairs": len(inverse_pairs),
        "supportLemmaFailures": exact_support_lemma["failures"],
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
