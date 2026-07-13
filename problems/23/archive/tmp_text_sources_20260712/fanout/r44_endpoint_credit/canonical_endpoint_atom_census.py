"""Exact N<=12 census of the live endpoint P2 atom at defect minima.

For Q=(a,x,m,y,b) -> Q'=(a,x,v,y,b), retain only live R37 detours:
old xv is active, old vy is selected support, and support cardinality is
constant.  The canonical selector is the exact coherent collision defect used
by the R40 production gate (P1/P3/strict-P4/P5); all global minimizers are
checked, not merely a lexicographic representative.

Finite output is evidence only; the local iff itself follows directly from
the literal P2 checker conditions and the row replacement incidence change.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
R40 = ROOT / "tmp" / "fanout" / "r40_strong_probe_census"
for path in (WRITEUP, P5, PHT, R40):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from strong_probe_census import matching_analysis  # noqa: E402
import p5_core as p5  # noqa: E402


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def canonical_sha(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def detour_specs(family: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, int], ...]:
    """Literal middle replacements with all four retained row positions fixed."""
    out = []
    for old_index, old in enumerate(family):
        for new_index, new in enumerate(family):
            if old_index != new_index and old[:2] == new[:2] and old[3:] == new[3:]:
                out.append((old_index, new_index))
    return tuple(out)


def endpoint_atom(ctx, old, new, m: int, z: int, owner: int, side: list[int]) -> dict:
    """Exact P2/common-blue status of the two orientations of (m,z)."""
    count = old.pair[m][z]
    target = new.pair[m][z]
    singleton = count == 1
    pair_edge = edge(m, z)
    sigma = ctx.sigma_pair[m][z]
    common_blue = owner in ctx.blue_adj[m] and owner in ctx.blue_adj[z]
    unreserved = all(
        not p5._reserved(new, m, z, half) and not p5._reserved(new, z, m, half)
        for half in (0, 1)
    )
    valid_p2 = singleton and common_blue and unreserved and sigma >= 2
    old_fiber = 2 * max(count - 1, 0)
    new_fiber = 2 * max(target - 1, 0)
    return {
        "count": count,
        "targetCount": target,
        "sigma": sigma,
        "sameSide": side[m] == side[z],
        "noGraphEdge": pair_edge not in ctx.blue and pair_edge not in ctx.bad,
        "commonBlueOwner": owner,
        "commonBlue": common_blue,
        "unreserved": unreserved,
        "p2CommonBlueHalves": 4 if valid_p2 else 0,
        "pairedCollisionFiberDrop": 2 * (old_fiber - new_fiber),
        "kind": (
            "singleton_p2" if valid_p2
            else "singleton_weak" if singleton
            else "repeated_endpoint"
        ),
    }


def witness(order, ordinal, g6, choice, atom, replacement, old_row, new_row, left, right) -> dict:
    value = {
        "order": order,
        "graphOrdinal": ordinal,
        "g6": g6,
        "choice": list(choice),
        "atom": atom,
        "replacement": replacement,
        "oldRow": list(old_row),
        "newRow": list(new_row),
        "endpointAtX": left,
        "endpointAtY": right,
    }
    value["recordSha256"] = canonical_sha(value)
    return value


def empty_bucket() -> dict:
    return {
        "counts": Counter(),
        "endpointKinds": Counter(),
        "sigmaHistogram": Counter(),
        "firstWeakSingleton": None,
        "firstFailure": None,
    }


def record_key(value: dict) -> tuple:
    return (
        value["order"], value["graphOrdinal"], value["choice"],
        value["atom"], value["replacement"],
    )


def merge_bucket(target: dict, source: dict) -> None:
    for key in ("counts", "endpointKinds", "sigmaHistogram"):
        target[key].update(source[key])
    for key in ("firstWeakSingleton", "firstFailure"):
        candidate = source[key]
        if candidate is not None and (
            target[key] is None or record_key(candidate) < record_key(target[key])
        ):
            target[key] = candidate


def check_minimum_tuple(
    bucket: dict,
    *,
    order: int,
    ordinal: int,
    g6: str,
    info: dict,
    ctx,
    families,
    specs,
    choice: tuple[int, ...],
    state,
) -> None:
    counts = bucket["counts"]
    counts["canonicalMinimizers"] += 1
    rows = rows_for_choice(families, choice)
    for atom, atom_specs in enumerate(specs):
        for old_index, replacement in atom_specs:
            if choice[atom] != old_index:
                continue
            old_row = rows[atom]
            new_row = families[atom][replacement]
            a, x, m, y, b = old_row
            v = new_row[2]
            if edge(x, v) not in state.active_edges or edge(v, y) not in state.support:
                continue
            counts["r37GeometryDetours"] += 1
            unique_count = int(state.pair[m][x] == 1) + int(state.pair[m][y] == 1)
            if unique_count != 1:
                counts["nonconstantSupportDetours"] += 1
                continue
            new_choice = list(choice)
            new_choice[atom] = replacement
            new = p5.reconstruct_state(ctx, rows_for_choice(families, tuple(new_choice)))
            if len(state.support) != len(new.support):
                counts["supportConstancyFailures"] += 1
                if bucket["firstFailure"] is None:
                    bucket["firstFailure"] = witness(
                        order, ordinal, g6, choice, atom, replacement,
                        old_row, new_row, {}, {}
                    )
                continue
            left = endpoint_atom(ctx, state, new, m, a, x, info["side"])
            right = endpoint_atom(ctx, state, new, m, b, y, info["side"])
            counts["liveSupportConstantDetours"] += 1
            for endpoint in (left, right):
                counts["endpointAtoms"] += 1
                bucket["endpointKinds"][endpoint["kind"]] += 1
                bucket["sigmaHistogram"][endpoint["sigma"]] += 1
                valid_shape = (
                    endpoint["targetCount"] == endpoint["count"] - 1
                    and endpoint["sameSide"]
                    and endpoint["noGraphEdge"]
                    and endpoint["commonBlue"]
                    and endpoint["unreserved"]
                    and endpoint["pairedCollisionFiberDrop"] ==
                        (4 if endpoint["count"] >= 2 else 0)
                )
                if endpoint["count"] == 1:
                    valid_shape = valid_shape and (
                        endpoint["p2CommonBlueHalves"] ==
                            (4 if endpoint["sigma"] >= 2 else 0)
                    )
                if not valid_shape:
                    counts["endpointFormulaFailures"] += 1
                    if bucket["firstFailure"] is None:
                        bucket["firstFailure"] = witness(
                            order, ordinal, g6, choice, atom, replacement,
                            old_row, new_row, left, right
                        )
                if endpoint["kind"] == "singleton_weak":
                    counts["weakSingletonAtoms"] += 1
                    if bucket["firstWeakSingleton"] is None:
                        bucket["firstWeakSingleton"] = witness(
                            order, ordinal, g6, choice, atom, replacement,
                            old_row, new_row, left, right
                        )


def analyze_graph(task: tuple[int, int, str]) -> dict:
    order, ordinal, g6 = task
    bucket = empty_bucket()
    counts = bucket["counts"]
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        counts["skipNoConnectedGammaMinCut"] += 1
        return bucket
    if any(length != 5 for length in info["ell"].values()):
        counts["skipNotAllEll5"] += 1
        return bucket
    families = shortest_row_families(info)
    specs = tuple(detour_specs(family) for family in families)
    sizes = tuple(len(family) for family in families)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    counts["eligibleGraphs"] += 1
    counts["availableTuples"] += math.prod(sizes)
    minimum = None
    positive_minima: list[tuple[int, tuple[int, ...]]] = []
    for tuple_index, choice in enumerate(itertools.product(*(range(size) for size in sizes))):
        state = p5.reconstruct_state(ctx, rows_for_choice(families, choice))
        defect = matching_analysis(ctx, state)["defect"]
        counts["selectorTuples"] += 1
        if defect == 0:
            if minimum != 0:
                minimum = 0
                positive_minima.clear()
            check_minimum_tuple(
                bucket, order=order, ordinal=ordinal, g6=g6, info=info,
                ctx=ctx, families=families, specs=specs, choice=choice, state=state,
            )
        elif minimum != 0 and (minimum is None or defect < minimum):
            minimum = defect
            positive_minima = [(tuple_index, choice)]
        elif defect == minimum:
            positive_minima.append((tuple_index, choice))
    if minimum is None:
        raise AssertionError("eligible graph had no row tuple")
    counts["minimumDefectZeroGraphs"] += int(minimum == 0)
    if minimum > 0:
        for _, choice in positive_minima:
            state = p5.reconstruct_state(ctx, rows_for_choice(families, choice))
            if matching_analysis(ctx, state)["defect"] != minimum:
                raise AssertionError("minimum selector replay changed")
            check_minimum_tuple(
                bucket, order=order, ordinal=ordinal, g6=g6, info=info,
                ctx=ctx, families=families, specs=specs, choice=choice, state=state,
            )
    return bucket


def analyze_chunk(tasks: list[tuple[int, int, str]]) -> dict:
    out = empty_bucket()
    for task in tasks:
        merge_bucket(out, analyze_graph(task))
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--progress-every", type=int, default=1000)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 5 <= args.n_min <= args.n_max <= 12:
        parser.error("orders must satisfy 5 <= n-min <= n-max <= 12")
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    return args


def main() -> int:
    args = parse_args()
    started = time.time()
    graph6, generated = graph6_for_orders(args.n_min, args.n_max)
    by_order = {order: [] for order in range(args.n_min, args.n_max + 1)}
    for item in graph6:
        by_order[dec(item)[0]].append(item)
    tasks = []
    streams = {}
    for order in sorted(by_order):
        rows = by_order[order]
        if args.limit_graphs is not None:
            rows = rows[:args.limit_graphs]
        streams[str(order)] = {
            "graphs": len(rows),
            "sha256": hashlib.sha256("".join(item + "\n" for item in rows).encode("ascii")).hexdigest(),
        }
        tasks.extend((order, ordinal, item) for ordinal, item in enumerate(rows))
    chunks = [tasks[index:index + args.chunk_size] for index in range(0, len(tasks), args.chunk_size)]
    aggregate = empty_bucket()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for index, result in enumerate(pool.map(analyze_chunk, chunks, chunksize=1), start=1):
            merge_bucket(aggregate, result)
            if index % args.progress_every == 0 or index == len(chunks):
                print(json.dumps({
                    "chunk": index, "chunks": len(chunks),
                    "selectorTuples": aggregate["counts"]["selectorTuples"],
                    "live": aggregate["counts"]["liveSupportConstantDetours"],
                    "weak": aggregate["counts"]["weakSingletonAtoms"],
                }, sort_keys=True), flush=True)
    payload = {
        "schema": "R44_CANONICAL_ENDPOINT_ATOM_CENSUS_V1",
        "selector": "exact coherent collision defect of R40: P1/P3/strict-P4/P5, all global minimizers",
        "scope": "connected triangle-free geng -tc graphs; loads exact connected Gamma-minimum maximum cuts; complete all-ell=5 rows; live R37 support-constant detours",
        "orders": [args.n_min, args.n_max],
        "workers": args.workers,
        "generatedByOrder": {str(key): value for key, value in sorted(generated.items())},
        "inputStreams": streams,
        "counts": {key: value for key, value in sorted(aggregate["counts"].items())},
        "endpointKinds": {key: value for key, value in sorted(aggregate["endpointKinds"].items())},
        "sigmaHistogram": {str(key): value for key, value in sorted(aggregate["sigmaHistogram"].items())},
        "firstWeakSingleton": aggregate["firstWeakSingleton"],
        "firstFormulaFailure": aggregate["firstFailure"],
        "elapsedSeconds": round(time.time() - started, 3),
        "verdict": "PASS" if aggregate["firstFailure"] is None else "FAIL",
    }
    payload["canonicalSha256"] = canonical_sha(payload)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
