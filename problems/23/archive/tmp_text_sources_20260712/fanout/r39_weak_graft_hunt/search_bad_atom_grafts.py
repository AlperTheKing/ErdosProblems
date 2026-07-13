"""Exact N20 weak-attachment graft search with added bad atoms.

The fixed blue graph is the R36 sigma=1 attachment cage.  We add same-shore
distance-four edges as bad atoms, enumerate their complete shortest-row
families, and minimize the full P1/P3/P4/P5/common-blue collision Hall defect
over every row tuple.  All arithmetic is integral.
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
sys.path.insert(0, str(ROOT / "tmp/fanout/p5_n12_census"))
import p5_core as p5  # noqa: E402


N = 20
BASE_ROWS = (
    (0, 2, 3, 4, 1),
    (5, 7, 8, 9, 6),
    (10, 12, 13, 14, 11),
    (15, 17, 18, 19, 16),
)
BASE_BAD = ((0, 1), (5, 6), (10, 11), (15, 16))
EXTRA_BLUE = ((0, 7), (7, 10), (10, 15), (15, 1))
SIDE_ZERO = {0, 1, 3, 5, 6, 8, 10, 11, 13, 17, 19}


def edge(x, y):
    return (x, y) if x < y else (y, x)


BASE_EDGES = {edge(row[i], row[(i + 1) % 5]) for row in BASE_ROWS for i in range(5)}
BASE_EDGES |= {edge(*e) for e in EXTRA_BLUE}
BASE_BAD_SET = {edge(*e) for e in BASE_BAD}
BLUE = BASE_EDGES - BASE_BAD_SET


def adjacency(edges):
    out = [set() for _ in range(N)]
    for x, y in edges:
        out[x].add(y)
        out[y].add(x)
    return out


BLUE_ADJ = adjacency(BLUE)


def distances(start):
    dist = [-1] * N
    dist[start] = 0
    todo = deque([start])
    while todo:
        x = todo.popleft()
        for y in BLUE_ADJ[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                todo.append(y)
    return dist


DIST = [distances(x) for x in range(N)]


def shortest_rows(x, y):
    if DIST[x][y] != 4:
        return []
    rows = []
    for a in sorted(BLUE_ADJ[x]):
        for b in sorted(BLUE_ADJ[a] - {x}):
            for c in sorted(BLUE_ADJ[b] - {x, a}):
                row = (x, a, b, c, y)
                if y in BLUE_ADJ[c] and len(set(row)) == 5:
                    rows.append(row)
    return sorted(set(rows))


def triangle_free(edges):
    adj = adjacency(edges)
    return not any(adj[x] & adj[y] for x, y in edges)


def candidate_atoms():
    out = []
    for x in range(N):
        for y in range(x + 1, N):
            e = (x, y)
            if (x in SIDE_ZERO) != (y in SIDE_ZERO) or e in BASE_EDGES:
                continue
            rows = shortest_rows(x, y)
            if rows and not (BLUE_ADJ[x] & BLUE_ADJ[y]):
                out.append((e, rows))
    return out


def collision_hall(state, relation):
    owners = tuple(o for o in state.owners if state.collision[o] > 0)
    if not owners:
        return {"defect": 0, "demand": 0, "reach": 0, "shore": []}
    old_index = {o: state.owners.index(o) for o in owners}
    projected = []
    for mask in relation.values():
        new = 0
        for i, owner in enumerate(owners):
            if mask & (1 << old_index[owner]):
                new |= 1 << i
        if new:
            projected.append(new)
    best = (0, 0, 0, 0)
    for shore in range(1, 1 << len(owners)):
        demand = sum(state.collision[o] for i, o in enumerate(owners) if shore & (1 << i))
        reach = sum(bool(mask & shore) for mask in projected)
        best = max(best, (demand - reach, demand, -reach, shore))
    defect, demand, neg_reach, shore_mask = best
    shore = [o for i, o in enumerate(owners) if shore_mask & (1 << i)]
    return {"defect": max(0, defect), "demand": demand, "reach": -neg_reach, "shore": shore}


def evaluate(ctx, rows):
    state = p5.reconstruct_state(ctx, rows)
    masks = p5.relation_masks(ctx, state)
    hall = collision_hall(state, masks["five"])
    comps = {state.selected_comp[o] for o in state.owners if state.collision[o] > 0}
    hall["coherenceSingleComponent"] = len(comps) <= 1
    hall["state"] = state
    hall["masks"] = masks
    return hall


def cut_sigma(edges, bad, x, y):
    switch = {x, y}
    db = sum(((a in switch) != (b in switch)) for a, b in edges - bad)
    dm = sum(((a in switch) != (b in switch)) for a, b in bad)
    return db, dm, db - dm


def trace_audit(edges, bad, families, rows, hall):
    state = hall["state"]
    probes = []
    support_adj = adjacency(state.support)
    active_adj = adjacency(state.demanded_active_edges)
    for owner in hall["shore"]:
        for x in sorted(active_adj[owner]):
            for y in sorted(support_adj[owner]):
                if x == y:
                    continue
                covers = [(i, row, abs(row.index(x) - row.index(y)))
                          for i, row in enumerate(rows) if x in row and y in row]
                if not covers:
                    db, dm, sigma = cut_sigma(edges, bad, x, y)
                    probes.append({"owner": owner, "x": x, "y": y,
                                   "kind": "weak" if sigma in (0, 1) else "strong",
                                   "dB": db, "dM": dm, "sigma": sigma})
                    continue
                detours = []
                for atom, row, separation in covers:
                    if separation != 2:
                        continue
                    i, j = sorted((row.index(x), row.index(y)))
                    replacement = list(row)
                    replacement[i + 1] = owner
                    replacement = tuple(replacement)
                    if replacement != row and replacement in families[atom]:
                        detours.append({"atom": atom, "row": list(replacement)})
                probes.append({"owner": owner, "x": x, "y": y,
                               "kind": "detour" if detours else "covered",
                               "detours": detours})
    return {
        "probes": probes,
        "nonempty": bool(probes),
        "allWeakSigma01": bool(probes) and all(p["kind"] == "weak" for p in probes),
        "detourCount": sum(p["kind"] == "detour" for p in probes),
    }


def exact_maxcut(edges):
    adj = [tuple(xs) for xs in adjacency(edges)]
    side = [0] * N
    cut = best = 0
    count = 1
    for step in range(1, 1 << (N - 1)):
        bit = (step & -step).bit_length() - 1
        v = bit + 1
        crossing = sum(side[u] != side[v] for u in adj[v])
        cut += len(adj[v]) - 2 * crossing
        side[v] ^= 1
        if cut > best:
            best, count = cut, 1
        elif cut == best:
            count += 1
    return best, count


def maxcut_constraints(candidates):
    """Compress all fixed-v0 cuts into exact added-atom subset constraints."""
    candidate_index = {e: i for i, (e, _) in enumerate(candidates)}
    base_adj = [tuple(xs) for xs in adjacency(BASE_EDGES)]
    side = [0] * N
    base_cut = 0
    constraints = {}
    cut_masks = Counter()
    for step in range(1 << (N - 1)):
        if step:
            bit = (step & -step).bit_length() - 1
            v = bit + 1
            crossing = sum(side[u] != side[v] for u in base_adj[v])
            base_cut += len(base_adj[v]) - 2 * crossing
            side[v] ^= 1
        mask = 0
        for e, index in candidate_index.items():
            if side[e[0]] != side[e[1]]:
                mask |= 1 << index
        slack = len(BLUE) - base_cut
        constraints[mask] = min(constraints.get(mask, slack), slack)
        cut_masks[(mask, slack)] += 1
    return tuple(sorted(constraints.items())), cut_masks


def subset_is_maxcut(mask, constraints):
    return all((mask & crossing).bit_count() <= slack for crossing, slack in constraints)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-added", type=int, default=5)
    ap.add_argument("--tuple-bound", type=int, default=200000)
    args = ap.parse_args()
    candidates = candidate_atoms()
    constraints, cut_masks = maxcut_constraints(candidates)
    records = []
    zero_examples = []
    counts = Counter()
    witnesses = []
    for size in range(1, args.max_added + 1):
        for indices in itertools.combinations(range(len(candidates)), size):
            subset_mask = sum(1 << i for i in indices)
            if not subset_is_maxcut(subset_mask, constraints):
                counts["not_maxcut"] += 1
                continue
            added = {candidates[i][0] for i in indices}
            bad = BASE_BAD_SET | added
            edges = BASE_EDGES | added
            if not triangle_free(edges):
                counts["triangle_reject"] += 1
                continue
            bads = tuple(sorted(bad))
            families = tuple(shortest_rows(*e) for e in bads)
            tuple_count = math.prod(map(len, families))
            if tuple_count > args.tuple_bound:
                counts["tuple_bound"] += 1
                continue
            ctx = p5.make_graph_context(N, BLUE, bad)
            minimum = None
            minima = []
            for choice in itertools.product(*(range(len(f)) for f in families)):
                rows = tuple(families[i][choice[i]] for i in range(len(families)))
                result = evaluate(ctx, rows)
                if not result["coherenceSingleComponent"]:
                    raise AssertionError("candidate needs coherent multi-component solver")
                defect = result["defect"]
                if minimum is None or defect < minimum:
                    minimum, minima = defect, [(choice, rows, result)]
                elif defect == minimum:
                    minima.append((choice, rows, result))
                if minimum == 0:
                    break
            record = {"added": [list(e) for e in sorted(added)],
                      "familySizes": [len(f) for f in families],
                      "tupleCount": tuple_count, "minimumDefect": minimum,
                      "minimumStates": len(minima)}
            if minimum == 0:
                counts["zero_minimum"] += 1
                if len(zero_examples) < 20:
                    zero_examples.append({"added": [list(e) for e in sorted(added)],
                                          "familySizes": [len(f) for f in families],
                                          "zeroChoice": list(minima[0][0])})
                continue
            audits = [trace_audit(edges, bad, families, rows, result)
                      for _, rows, result in minima]
            record["audits"] = audits
            record["allMinimumExitsWeak"] = all(a["allWeakSigma01"] and a["detourCount"] == 0 for a in audits)
            maxcut, cut_count = exact_maxcut(edges)
            intended = len(BLUE)
            record.update({"edges": len(edges), "intendedCut": intended,
                           "exactMaxcut": maxcut, "maxcutCountFixedV0": cut_count,
                           "maxcutCertified": maxcut == intended})
            records.append(record)
            if record["maxcutCertified"] and record["allMinimumExitsWeak"]:
                witnesses.append(len(records) - 1)
                counts["witness"] += 1
            else:
                counts["positive_reject"] += 1
    payload = {
        "schema": "r39-n20-added-bad-atom-graft-v1",
        "candidateAtoms": [{"edge": list(e), "rows": len(rows)} for e, rows in candidates],
        "parameters": vars(args), "maxcutConstraintCount": len(constraints),
        "enumeratedCutsFixedV0": sum(cut_masks.values()),
        "counts": dict(sorted(counts.items())), "zeroExamples": zero_examples,
        "positiveRecords": records, "witnessIndices": witnesses,
        "verdict": "DECISIVE_WITNESS" if witnesses else "BOUNDED_NO_WITNESS",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    (HERE / "manifest.json").write_bytes(raw)
    print(json.dumps({"verdict": payload["verdict"], "candidateAtoms": len(candidates),
                      "counts": payload["counts"], "witnessIndices": witnesses,
                      "sha256": hashlib.sha256(raw).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
