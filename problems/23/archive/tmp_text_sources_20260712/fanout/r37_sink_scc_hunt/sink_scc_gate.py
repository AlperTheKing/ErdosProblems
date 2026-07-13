"""Bounded exact R37 sink-neutral-SCC hunt on real 24-vertex cage mutations.

The acceptance target is deliberately stronger than positive defect.  A graph
is called decisive only after every row tuple is enumerated, the global defect
minimum is positive, and a sink SCC of equal-minimum one-row transitions is
identified.  Zero-defect and over-bound instances are retained in the
manifest, never silently counted as counterexamples.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import random
import sys
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL_PATH = ROOT / "tmp/fanout/r35_24_trade/evaluate_trade.py"


def load_model():
    spec = importlib.util.spec_from_file_location("r35_trade_model", MODEL_PATH)
    model = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    return model


M = load_model()
BASE_EDGES = frozenset(M.EDGES)
BASE_BAD = frozenset(M.BAD)
BASE_BLUE = frozenset(M.BLUE)
DISPLAYED_ROWS = tuple(M.DISPLAYED_ROWS)
SUPPORT = frozenset(
    M.edge(row[i], row[i + 1]) for row in DISPLAYED_ROWS for i in range(4)
)
OPTIONAL_BLUE = tuple(sorted(BASE_BLUE - SUPPORT))


def adjacency(edges):
    out = [set() for _ in range(M.N)]
    for x, y in edges:
        out[x].add(y)
        out[y].add(x)
    return out


def connected(edges):
    adj = adjacency(edges)
    seen = {0}
    todo = [0]
    while todo:
        x = todo.pop()
        for y in adj[x] - seen:
            seen.add(y)
            todo.append(y)
    return len(seen) == M.N


def configure(blue):
    """Install one deletion mutation into the imported exact evaluator."""
    edges = set(BASE_BAD) | set(blue)
    M.EDGES = edges
    M.BLUE = set(blue)
    M.BAD = set(BASE_BAD)
    M.BLUE_ADJ = adjacency(blue)
    M.SIGNED_DEGREE = [0] * M.N
    M.EDGE_SIGN = {}
    for sign, family in ((1, M.BLUE), (-1, M.BAD)):
        for x, y in family:
            M.SIGNED_DEGREE[x] += sign
            M.SIGNED_DEGREE[y] += sign
            M.EDGE_SIGN[M.edge(x, y)] = sign
    M.ROW_FAMILIES = [M.shortest_rows(*bad) for bad in M.BADS]
    if any(not rows for rows in M.ROW_FAMILIES):
        return None
    try:
        displayed = tuple(
            M.ROW_FAMILIES[i].index(row) for i, row in enumerate(DISPLAYED_ROWS)
        )
    except ValueError:
        return None
    M.RADICES = tuple(len(rows) for rows in M.ROW_FAMILIES)
    M.DISPLAYED = displayed
    return displayed


def exact_maxcut(edges):
    """Exact Gray-code maxcut with vertex 0 fixed."""
    adj = [tuple(xs) for xs in adjacency(edges)]
    side = [0] * M.N
    cut = best = 0
    count = 1
    for step in range(1, 1 << (M.N - 1)):
        bit = (step & -step).bit_length() - 1
        v = bit + 1
        old = side[v]
        crossing = sum(side[u] != old for u in adj[v])
        cut += len(adj[v]) - 2 * crossing
        side[v] ^= 1
        if cut > best:
            best, count = cut, 1
        elif cut == best:
            count += 1
    return best, count


def product(values):
    out = 1
    for value in values:
        out *= value
    return out


def tarjan(vertices, edges):
    index = 0
    stack = []
    on_stack = set()
    indices = {}
    low = {}
    components = []

    def visit(v):
        nonlocal index
        indices[v] = low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in edges[v]:
            if w not in indices:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            component = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.append(w)
                if w == v:
                    break
            components.append(tuple(sorted(component)))

    for vertex in vertices:
        if vertex not in indices:
            visit(vertex)
    return components


def neutral_sink_sccs(min_states):
    states = set(min_states)
    edges = {state: set() for state in states}
    for state in states:
        for atom, radix in enumerate(M.RADICES):
            for choice in range(radix):
                if choice == state[atom]:
                    continue
                nxt = list(state)
                nxt[atom] = choice
                nxt = tuple(nxt)
                if nxt in states:
                    edges[state].add(nxt)
    components = tarjan(states, edges)
    owner = {state: i for i, comp in enumerate(components) for state in comp}
    sinks = []
    for i, comp in enumerate(components):
        exits = sorted(
            {owner[nxt] for state in comp for nxt in edges[state] if owner[nxt] != i}
        )
        if not exits:
            sinks.append({"states": [list(s) for s in comp], "outgoing_sccs": exits})
    return sinks


def find_zero(start, budget):
    """Deterministic defect-first beam; a hit is conclusive, exhaustion is not."""
    cache = {}

    def evaluate(state):
        state = tuple(state)
        if state not in cache:
            cache[state] = M.evaluate(state, include_common_blue=True)["defect"]
        return cache[state]

    start = tuple(start)
    if evaluate(start) == 0:
        return start, len(cache)
    frontier = [start]
    seen = {start}
    while frontier and len(cache) < budget:
        candidates = []
        for state in frontier:
            for atom, radix in enumerate(M.RADICES):
                for choice in range(radix):
                    if choice == state[atom]:
                        continue
                    nxt = list(state)
                    nxt[atom] = choice
                    nxt = tuple(nxt)
                    if nxt in seen:
                        continue
                    seen.add(nxt)
                    defect = evaluate(nxt)
                    if defect == 0:
                        return nxt, len(cache)
                    candidates.append(nxt)
                    if len(cache) >= budget:
                        break
                if len(cache) >= budget:
                    break
            if len(cache) >= budget:
                break
        candidates.sort(key=lambda state: (evaluate(state), M.tuple_rank(state)))
        frontier = candidates[:128]
    return None, len(cache)


def masks(limit, seed):
    """Deterministic lock, join-like, and random optional-edge mutations."""
    full = (1 << len(OPTIONAL_BLUE)) - 1
    seen = {full, 0}
    yield "base", full
    yield "support_only", 0

    # Single-edge locks and complements exercise local detour suppression.
    for i in range(len(OPTIONAL_BLUE)):
        for name, mask in ((f"drop_{i}", full ^ (1 << i)), (f"keep_{i}", 1 << i)):
            if mask not in seen:
                seen.add(mask)
                yield name, mask

    # Keep edges incident to selected owner sets: double-star locks and joins.
    owner_sets = ({7}, {6, 7, 8}, {7, 8}, {6, 7}, {7, 12, 13, 14})
    for k, owners in enumerate(owner_sets):
        mask = sum(
            1 << i for i, edge in enumerate(OPTIONAL_BLUE) if owners & set(edge)
        )
        if mask not in seen:
            seen.add(mask)
            yield f"owner_lock_{k}", mask

    rng = random.Random(seed)
    while len(seen) < limit:
        density = rng.choice((0.2, 0.35, 0.5, 0.65, 0.8))
        mask = sum(1 << i for i in range(len(OPTIONAL_BLUE)) if rng.random() < density)
        if mask not in seen:
            seen.add(mask)
            yield f"random_{len(seen)}", mask


def graph_digest(blue):
    payload = json.dumps(sorted(map(list, set(BASE_BAD) | set(blue))), separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def run(args):
    manifest = {
        "schema": "r37-real-sink-neutral-attachment-scc-hunt-v1",
        "relation": "P1/P3/strict-P4/P5/common-blue; exact FreeHalf reservation",
        "acceptance": "positive global defect minimum plus sink neutral tuple SCC",
        "tuple_bound": args.tuple_bound,
        "mutation_limit": args.mutation_limit,
        "optional_blue_edges": [list(e) for e in OPTIONAL_BLUE],
        "counts": Counter(),
        "instances": [],
        "decisive_witnesses": [],
    }
    for mutation_index, (name, mask) in enumerate(masks(args.mutation_limit, args.seed)):
        if mutation_index >= args.mutation_limit:
            break
        blue = set(SUPPORT)
        blue.update(e for i, e in enumerate(OPTIONAL_BLUE) if mask & (1 << i))
        record = {"name": name, "graph_sha256": graph_digest(blue), "blue_edges": len(blue)}
        if not connected(blue):
            record["status"] = "reject_blue_disconnected"
            manifest["counts"][record["status"]] += 1
            manifest["instances"].append(record)
            continue
        displayed = configure(blue)
        if displayed is None:
            record["status"] = "reject_incomplete_displayed_rows"
            manifest["counts"][record["status"]] += 1
            manifest["instances"].append(record)
            continue
        record["row_family_sizes"] = list(M.RADICES)
        record["tuple_product"] = product(M.RADICES)
        shown = M.evaluate(displayed, certificate=True, include_common_blue=True)
        record["displayed_defect"] = shown["defect"]
        if shown["defect"] == 0:
            record["status"] = "zero_witness"
            record["zero_method"] = "displayed"
            record["zero_state"] = list(displayed)
            manifest["counts"][record["status"]] += 1
            manifest["instances"].append(record)
            continue
        if record["tuple_product"] > args.tuple_bound:
            zero_state, searched = find_zero(displayed, args.beam_budget)
            record["beam_states_evaluated"] = searched
            if zero_state is not None:
                record["status"] = "zero_witness"
                record["zero_method"] = "bounded_beam"
                record["zero_state"] = list(zero_state)
            else:
                record["status"] = "inconclusive_tuple_bound"
            manifest["counts"][record["status"]] += 1
            manifest["instances"].append(record)
            continue

        minimum = None
        min_states = []
        evaluated = 0
        zero_state = None
        for state in itertools.product(*(range(r) for r in M.RADICES)):
            result = M.evaluate(state, include_common_blue=True)
            evaluated += 1
            defect = result["defect"]
            if minimum is None or defect < minimum:
                minimum, min_states = defect, [state]
            elif defect == minimum:
                min_states.append(state)
            if defect == 0:
                zero_state = state
                break
        record["tuples_evaluated"] = evaluated
        record["minimum_defect"] = minimum
        if zero_state is not None:
            record["status"] = "zero_witness"
            record["zero_method"] = "exhaustive_prefix"
            record["zero_state"] = list(zero_state)
        else:
            sinks = neutral_sink_sccs(min_states)
            record["minimum_states"] = len(min_states)
            record["neutral_sink_sccs"] = sinks
            record["status"] = "positive_minimum_sink_candidate"
            # Section 11 also requires matching-cursor closure.  Until that
            # layer is emitted, tuple-level sinks remain candidates, not CEs.
            record["matching_cursor_closure"] = "not_emitted"
        manifest["counts"][record["status"]] += 1
        manifest["instances"].append(record)

    # Audit all positive candidates and a bounded representative set of zero
    # witnesses.  This separates genuine real cages from exploratory locks.
    preferred = ["base", "drop_24", "drop_25", "owner_lock_0", "owner_lock_1", "owner_lock_4"]
    for method in ("bounded_beam", "exhaustive_prefix"):
        hit = next((r["name"] for r in manifest["instances"] if r.get("zero_method") == method), None)
        if hit is not None:
            preferred.append(hit)
    audit_names = set(preferred[:args.maxcut_audit])
    for record in manifest["instances"]:
        audit_zero = record["status"] == "zero_witness" and record["name"] in audit_names
        if record["status"] != "positive_minimum_sink_candidate" and not audit_zero:
            continue
        blue = None
        for name, mask in masks(args.mutation_limit, args.seed):
            candidate = set(SUPPORT)
            candidate.update(e for i, e in enumerate(OPTIONAL_BLUE) if mask & (1 << i))
            if name == record["name"]:
                blue = candidate
                break
        assert blue is not None
        intended = len(blue)
        maximum, maxcut_count = exact_maxcut(set(BASE_BAD) | blue)
        record["intended_cut"] = intended
        record["exact_maxcut"] = maximum
        record["maxcuts_vertex0_fixed"] = maxcut_count
        record["real_canonical"] = intended == maximum
        if (
            record["status"] == "positive_minimum_sink_candidate"
            and record["real_canonical"]
            and record["matching_cursor_closure"] == "proved"
        ):
            manifest["decisive_witnesses"].append(record["name"])

    manifest["counts"] = dict(sorted(manifest["counts"].items()))
    manifest["verdict"] = (
        "DECISIVE_WITNESS" if manifest["decisive_witnesses"]
        else "BOUNDED_ZERO_FAILURE"
    )
    text = json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
    (HERE / "manifest.json").write_bytes(text.encode("ascii"))
    print(json.dumps({
        "verdict": manifest["verdict"],
        "counts": manifest["counts"],
        "decisive_witnesses": manifest["decisive_witnesses"],
        "manifest_sha256": hashlib.sha256(text.encode("ascii")).hexdigest(),
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-limit", type=int, default=256)
    parser.add_argument("--tuple-bound", type=int, default=250_000)
    parser.add_argument("--seed", type=int, default=370024)
    parser.add_argument("--beam-budget", type=int, default=20_000)
    parser.add_argument("--maxcut-audit", type=int, default=8)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
