"""Enumerate exact row tuples and live owner-profile transitions on t=4 hits."""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import product
from pathlib import Path

from enumerate_t4_support_graphs import decode_graph6, adjacency


def all_shortest_rows(n, edges, source, target):
    adj = adjacency(n, edges)
    ds = [-1] * n
    ds[source] = 0
    todo = deque([source])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if ds[v] < 0:
                ds[v] = ds[u] + 1
                todo.append(v)
    assert ds[target] == 4
    out = []

    def dfs(path):
        if len(path) == 5:
            if path[-1] == target:
                out.append(tuple(path))
            return
        u = path[-1]
        for v in sorted(adj[u]):
            if v in path or ds[v] != ds[u] + 1:
                continue
            dfs(path + (v,))

    dfs((source,))
    return tuple(out)


def norm_edge(u, v):
    return (u, v) if u < v else (v, u)


def row_edges(row):
    return frozenset(norm_edge(u, v) for u, v in zip(row, row[1:]))


def tuple_state(n, support_edges, rows, owner):
    selected_vertices = set().union(*(set(row) for row in rows))
    selected_support = set().union(*(set(row_edges(row)) for row in rows))
    active = {edge for edge in support_edges
              if edge[0] in selected_vertices and edge[1] in selected_vertices
              and edge not in selected_support}
    incident_active = sorted(edge for edge in active if owner in edge)
    adj = adjacency(n, support_edges)
    row_occ = sum(owner in row for row in rows)
    pair_count = Counter()
    for row in rows:
        for x in row:
            for y in row:
                pair_count[(x, y)] += 1
    neighbors = sorted(adj[owner])
    all_neighbors_selected = all(x in selected_vertices for x in neighbors)
    profile = False
    active_neighbor = None
    r4 = row_occ == 4
    active1 = len(incident_active) == 1
    coverage = False
    if active1:
        edge = incident_active[0]
        active_neighbor = edge[0] if edge[1] == owner else edge[1]
        coverage = all(pair_count[(active_neighbor, s)] > 0
                       for s in neighbors if s != active_neighbor)
    profile_no_r = all_neighbors_selected and active1 and coverage
    profile = r4 and profile_no_r
    return {
        "selectedSupport": frozenset(selected_support),
        "active": frozenset(active),
        "rowOccurrences": row_occ,
        "r4": r4,
        "allNeighborsSelected": all_neighbors_selected,
        "activeDegree": len(incident_active),
        "active1": active1,
        "coverage": coverage,
        "profile": profile,
        "profileNoR": profile_no_r,
        "activeNeighbor": active_neighbor,
    }


def one_middle_swap(rows_a, rows_b, v, m):
    changed = [i for i, (a, b) in enumerate(zip(rows_a, rows_b)) if a != b]
    if len(changed) != 1:
        return None
    i = changed[0]
    a, b = rows_a[i], rows_b[i]
    if a[0] != b[0] or a[4] != b[4]:
        return None
    if a[1] != b[1] or a[3] != b[3]:
        return None
    if {a[2], b[2]} != {v, m}:
        return None
    return {"atomIndex": i, "rowA": a, "rowB": b}


def process_hit(hit):
    n, support_edges_tuple = decode_graph6(hit["graph6"].encode("ascii"))
    support_edges = frozenset(support_edges_tuple)
    bad_edges = tuple(tuple(edge) for edge in hit["badEdges"])
    families = tuple(all_shortest_rows(n, support_edges_tuple, *edge)
                     for edge in bad_edges)
    assert tuple(map(len, families)) == tuple(hit["rowCounts"])
    v, m = hit["owner"]["v"], hit["owner"]["m"]
    forced_v = sum(all(v in row for row in family) for family in families)
    forced_m = sum(all(m in row for row in family) for family in families)
    choices = []
    profile_v = []
    profile_m = []
    profile_v_no_r = []
    profile_m_no_r = []
    counts = Counter()
    counts[f"forcedThroughV_{forced_v}"] += 1
    counts[f"forcedThroughM_{forced_m}"] += 1
    if forced_v < 8 or forced_m < 8:
        counts["forcedThroughBelowEight"] += 1
    for indices in product(*(range(len(family)) for family in families)):
        rows = tuple(families[i][indices[i]] for i in range(16))
        state_v = tuple_state(n, support_edges, rows, v)
        state_m = tuple_state(n, support_edges, rows, m)
        idx = len(choices)
        choices.append((indices, rows, state_v, state_m))
        counts["rowTuples"] += 1
        for label, state in (("V", state_v), ("M", state_m)):
            counts[f"rowOcc{label}_{state['rowOccurrences']}"] += 1
            counts[f"activeDeg{label}_{state['activeDegree']}"] += 1
            if state["r4"]:
                counts[f"stage{label}_r4"] += 1
                if state["allNeighborsSelected"]:
                    counts[f"stage{label}_r4_allSelected"] += 1
                    if state["active1"]:
                        counts[f"stage{label}_r4_allSelected_active1"] += 1
                        if state["coverage"]:
                            counts[f"stage{label}_r4_allSelected_active1_covered"] += 1
        if state_v["profile"]:
            profile_v.append(idx)
            counts["profileV"] += 1
        if state_m["profile"]:
            profile_m.append(idx)
            counts["profileM"] += 1
        if state_v["profileNoR"]:
            profile_v_no_r.append(idx)
            counts["profileNoRV"] += 1
        if state_m["profileNoR"]:
            profile_m_no_r.append(idx)
            counts["profileNoRM"] += 1
    raw_transitions = []
    no_r_transitions = []
    for ia in range(len(choices)):
        indices_a, rows_a, state_va, state_ma = choices[ia]
        for ib in range(ia + 1, len(choices)):
            indices_b, rows_b, state_vb, state_mb = choices[ib]
            swap = one_middle_swap(rows_a, rows_b, v, m)
            if swap is None:
                continue
            counts["rawMiddleTransitions"] += 1
            if len(raw_transitions) < 4:
                raw_transitions.append({
                    "choiceA": list(indices_a), "choiceB": list(indices_b), **swap})
            forward = state_va["profileNoR"] and state_mb["profileNoR"]
            reverse = state_ma["profileNoR"] and state_vb["profileNoR"]
            if forward or reverse:
                counts["noRProfileMiddleTransitions"] += 1
                if len(no_r_transitions) < 4:
                    no_r_transitions.append({
                        "choiceA": list(indices_a), "choiceB": list(indices_b),
                        "direction": "v_to_m" if forward else "m_to_v", **swap})
    transitions = []
    common_blue = set(hit["owner"]["commonBlue"])
    for ia in profile_v:
        indices_a, rows_a, state_va, _ = choices[ia]
        for ib in profile_m:
            indices_b, rows_b, _, state_mb = choices[ib]
            swap = one_middle_swap(rows_a, rows_b, v, m)
            if swap is None:
                continue
            counts["profileMiddleTransitions"] += 1
            central = (state_va["activeNeighbor"] in common_blue and
                       state_mb["activeNeighbor"] in common_blue and
                       state_va["activeNeighbor"] != state_mb["activeNeighbor"])
            if central:
                counts["centralProfileTransitions"] += 1
            if len(transitions) < 8:
                transitions.append({
                    "choiceV": list(indices_a),
                    "choiceM": list(indices_b),
                    "activeNeighborV": state_va["activeNeighbor"],
                    "activeNeighborM": state_mb["activeNeighbor"],
                    "central": central,
                    **swap,
                })
    sample = None
    if transitions or no_r_transitions or raw_transitions:
        sample = {
            "graph6": hit["graph6"],
            "n": n,
            "owner": hit["owner"],
            "badEdges": hit["badEdges"],
            "rowCounts": hit["rowCounts"],
            "transitions": transitions,
            "noRTransitions": no_r_transitions,
            "rawTransitions": raw_transitions,
        }
    return dict(counts), sample


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    ns = parser.parse_args()
    assert 1 <= ns.workers <= 8
    source = json.loads(ns.input.read_text())
    with mp.Pool(ns.workers) as pool:
        parts = pool.map(process_hit, source["hits"])
    counts = Counter()
    samples = []
    hit_circuits = 0
    central_circuits = 0
    no_r_circuits = 0
    raw_circuits = 0
    for part_counts, sample in parts:
        counts.update(part_counts)
        if part_counts.get("profileMiddleTransitions", 0):
            hit_circuits += 1
        if part_counts.get("centralProfileTransitions", 0):
            central_circuits += 1
        if part_counts.get("noRProfileMiddleTransitions", 0):
            no_r_circuits += 1
        if part_counts.get("rawMiddleTransitions", 0):
            raw_circuits += 1
        if sample is not None and len(samples) < 32:
            samples.append(sample)
    payload = {
        "schema": "T4_PROFILE_TRANSITION_CENSUS_V1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "circuits": len(source["hits"]),
        "counts": dict(sorted(counts.items())),
        "circuitsWithProfileMiddleTransition": hit_circuits,
        "circuitsWithCentralProfileTransition": central_circuits,
        "circuitsWithNoRProfileMiddleTransition": no_r_circuits,
        "circuitsWithRawMiddleTransition": raw_circuits,
        "samples": samples,
        "scope": (
            "complete shortest-row tuples on support graph only; profile is "
            "r=4, one internal active support edge, all four neighbours "
            "selected, active-neighbour pairs covered; no full production ledger"
        ),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["canonicalSha256"] = sha256(canonical.encode("ascii")).hexdigest()
    ns.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["counts"], sort_keys=True))
    print("circuits_with_transition=" + str(hit_circuits))
    print("central_circuits=" + str(central_circuits))
    print("canonical_sha256=" + payload["canonicalSha256"])


if __name__ == "__main__":
    main()
