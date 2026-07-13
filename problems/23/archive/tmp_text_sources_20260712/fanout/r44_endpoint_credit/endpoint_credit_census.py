"""Exact real-cage census for R44 endpoint alternatives.

The input stream is the pinned `geng -tc` connected triangle-free stream used
by the production N<=12 gates.  `loads` exhaustively chooses a connected
Gamma-minimum maximum cut.  On all-ell=5 cages every complete shortest-row
tuple is reconstructed directly; every genuine support-constant detour is
checked against the production pair, reservation, and common-blue predicates.

This is a finite audit, not a universal proof.
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
for path in (WRITEUP, P5, PHT):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
import p5_core as p5  # noqa: E402


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def canonical_sha(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def detour_specs(family: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, int], ...]:
    """Pairs (old index, new index) of literal two-edge middle detours."""
    out = []
    for old_index, old in enumerate(family):
        for new_index, new in enumerate(family):
            if old_index == new_index:
                continue
            if old[:2] == new[:2] and old[3:] == new[3:] and old[2] != new[2]:
                out.append((old_index, new_index))
    return tuple(out)


def endpoint_record(ctx, old, new, m: int, z: int, owner: int, side: list[int]) -> dict:
    count = old.pair[m][z]
    target_count = new.pair[m][z]
    singleton = count == 1
    repeated = count >= 2
    pair_edge = edge(m, z)
    same_side = side[m] == side[z]
    no_graph_edge = pair_edge not in ctx.blue and pair_edge not in ctx.bad
    unreserved = all(
        not p5._reserved(new, m, z, half) and not p5._reserved(new, z, m, half)
        for half in (0, 1)
    )
    common_blue = owner in ctx.blue_adj[m] and owner in ctx.blue_adj[z]
    sigma = ctx.sigma_pair[m][z]
    p2_valid = singleton and common_blue and sigma >= 2 and unreserved
    old_fiber = 2 * max(count - 1, 0)
    new_fiber = 2 * max(target_count - 1, 0)
    return {
        "count": count,
        "targetCount": target_count,
        "kind": (
            "singleton_strong" if singleton and sigma >= 2
            else "singleton_weak" if singleton
            else "repeated"
        ),
        "sigma": sigma,
        "sameSide": same_side,
        "noGraphEdge": no_graph_edge,
        "unreserved": unreserved,
        "commonBlueOwner": owner,
        "commonBlue": common_blue,
        "productionCommonBlue": p2_valid,
        "rawFreeHalves": 4 if singleton else 0,
        "pairedFiberDrop": 2 * (old_fiber - new_fiber),
        "mFiberDrop": old_fiber - new_fiber,
        "zFiberDrop": old_fiber - new_fiber,
    }


def record_witness(order: int, ordinal: int, g6: str, choice: tuple[int, ...], atom: int,
                   replacement: int, old_row: tuple[int, ...], new_row: tuple[int, ...],
                   old, new, endpoint_a: dict, endpoint_b: dict) -> dict:
    record = {
        "order": order,
        "graphOrdinal": ordinal,
        "g6": g6,
        "choice": list(choice),
        "atom": atom,
        "replacement": replacement,
        "oldRow": list(old_row),
        "newRow": list(new_row),
        "oldActiveEdges": [list(item) for item in sorted(old.active_edges)],
        "newActiveEdges": [list(item) for item in sorted(new.active_edges)],
        "endpoints": {"a": endpoint_a, "b": endpoint_b},
    }
    record["recordSha256"] = canonical_sha(record)
    return record


def empty_result() -> dict:
    return {
        "counts": Counter(),
        "endpointKinds": Counter(),
        "sigmaHistogram": Counter(),
        "weakPairHistogram": Counter(),
        "firstWeakWeakSingleton": None,
        "firstStructuralFailure": None,
    }


def merge(target: dict, source: dict) -> None:
    for key in ("counts", "endpointKinds", "sigmaHistogram", "weakPairHistogram"):
        target[key].update(source[key])
    for key in ("firstWeakWeakSingleton", "firstStructuralFailure"):
        candidate = source[key]
        if candidate is None:
            continue
        current = target[key]
        ckey = (candidate["order"], candidate["graphOrdinal"], candidate["choice"], candidate["atom"], candidate["replacement"])
        if current is None or ckey < (current["order"], current["graphOrdinal"], current["choice"], current["atom"], current["replacement"]):
            target[key] = candidate


def analyze_graph(task: tuple[int, int, str]) -> dict:
    order, ordinal, g6 = task
    result = empty_result()
    counts = result["counts"]
    n, graph_edges = dec(g6)
    if n != order:
        raise AssertionError("graph6 order mismatch")
    info = loads(n, graph_edges)
    if info is None:
        counts["skipNoConnectedGammaMinCut"] += 1
        return result
    if any(length != 5 for length in info["ell"].values()):
        counts["skipNotAllEll5"] += 1
        return result

    families = shortest_row_families(info)
    specs = tuple(detour_specs(family) for family in families)
    sizes = tuple(len(family) for family in families)
    counts["eligibleGraphs"] += 1
    counts["availableTuples"] += math.prod(sizes)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])

    for tuple_index, choice in enumerate(itertools.product(*(range(size) for size in sizes))):
        rows = rows_for_choice(families, choice)
        old = p5.reconstruct_state(ctx, rows)
        counts["examinedTuples"] += 1
        for atom, family_specs in enumerate(specs):
            for old_index, replacement in family_specs:
                if choice[atom] != old_index:
                    continue
                old_row = rows[atom]
                new_row = families[atom][replacement]
                a, x, m, y, b = old_row
                v = new_row[2]
                entering = {edge(x, v), edge(v, y)}
                if not entering <= old.active_edges:
                    continue
                counts["genuineActiveDetours"] += 1
                if old.pair[m][x] != 1 or old.pair[m][y] != 1:
                    counts["supportGrowingDetours"] += 1
                    continue

                new_choice = list(choice)
                new_choice[atom] = replacement
                new_rows = rows_for_choice(families, tuple(new_choice))
                new = p5.reconstruct_state(ctx, new_rows)
                leaving = {edge(x, m), edge(m, y)}
                support_constant = len(old.support) == len(new.support)
                expected_support = (old.support - leaving) | entering
                counts["supportConstantDetours"] += int(support_constant)
                if not support_constant or new.support != expected_support:
                    counts["structuralFailures"] += 1
                    if result["firstStructuralFailure"] is None:
                        result["firstStructuralFailure"] = record_witness(
                            order, ordinal, g6, choice, atom, replacement, old_row, new_row,
                            old, new, {}, {}
                        )
                    continue

                endpoint_a = endpoint_record(ctx, old, new, m, a, x, info["side"])
                endpoint_b = endpoint_record(ctx, old, new, m, b, y, info["side"])
                counts["endpointAlternativesChecked"] += 2
                for endpoint in (endpoint_a, endpoint_b):
                    result["endpointKinds"][endpoint["kind"]] += 1
                    result["sigmaHistogram"][endpoint["sigma"]] += 1
                    if endpoint["kind"] == "singleton_weak":
                        result["weakPairHistogram"][endpoint["sigma"]] += 1
                    structural_ok = (
                        endpoint["targetCount"] == endpoint["count"] - 1
                        and endpoint["sameSide"]
                        and endpoint["noGraphEdge"]
                        and endpoint["unreserved"]
                        and endpoint["commonBlue"]
                        and endpoint["pairedFiberDrop"] == (4 if endpoint["count"] >= 2 else 0)
                    )
                    if endpoint["count"] == 1:
                        structural_ok = structural_ok and endpoint["rawFreeHalves"] == 4
                        structural_ok = structural_ok and (
                            endpoint["productionCommonBlue"] == (endpoint["sigma"] >= 2)
                        )
                    if not structural_ok:
                        counts["structuralFailures"] += 1
                        if result["firstStructuralFailure"] is None:
                            result["firstStructuralFailure"] = record_witness(
                                order, ordinal, g6, choice, atom, replacement, old_row, new_row,
                                old, new, endpoint_a, endpoint_b
                            )

                # Exact R43 local owner ledger.  It only needs the two retained
                # singleton pairs m-x,m-y and the diagonal count of m.
                expected_balance = 6 + 2 * int(old.row_count[m] >= 2)
                actual_balance = 4 + 2 + 2 * int(old.row_count[m] >= 2)
                if actual_balance != expected_balance:
                    raise AssertionError("R43 endpoint balance identity failed")
                counts["ownerBalanceGain6"] += int(expected_balance == 6)
                counts["ownerBalanceGain8"] += int(expected_balance == 8)

                if endpoint_a["kind"] == endpoint_b["kind"] == "singleton_weak":
                    counts["weakWeakSingletonDetours"] += 1
                    if result["firstWeakWeakSingleton"] is None:
                        result["firstWeakWeakSingleton"] = record_witness(
                            order, ordinal, g6, choice, atom, replacement, old_row, new_row,
                            old, new, endpoint_a, endpoint_b
                        )
    return result


def analyze_chunk(tasks: list[tuple[int, int, str]]) -> dict:
    out = empty_result()
    for task in tasks:
        merge(out, analyze_graph(task))
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--progress-every", type=int, default=1000)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--graph6", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 5 <= args.n_min <= args.n_max <= 12:
        parser.error("orders must satisfy 5 <= n-min <= n-max <= 12")
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    if args.chunk_size <= 0:
        parser.error("chunk-size must be positive")
    if args.limit_graphs is not None and args.limit_graphs <= 0:
        parser.error("limit-graphs must be positive")
    return args


def main() -> int:
    args = parse_args()
    started = time.time()
    if args.graph6:
        graph6 = args.graph6
        generated = Counter(dec(item)[0] for item in graph6)
    else:
        graph6, generated = graph6_for_orders(args.n_min, args.n_max)
    by_order: dict[int, list[str]] = {order: [] for order in range(args.n_min, args.n_max + 1)}
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
    aggregate = empty_result()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for index, result in enumerate(pool.map(analyze_chunk, chunks, chunksize=1), start=1):
            merge(aggregate, result)
            if index % args.progress_every == 0 or index == len(chunks):
                print(json.dumps({
                    "chunk": index,
                    "chunks": len(chunks),
                    "eligible": aggregate["counts"]["eligibleGraphs"],
                    "tuples": aggregate["counts"]["examinedTuples"],
                    "supportConstant": aggregate["counts"]["supportConstantDetours"],
                    "weakWeak": aggregate["counts"]["weakWeakSingletonDetours"],
                }, sort_keys=True), flush=True)

    payload = {
        "schema": "R44_ENDPOINT_CREDIT_CENSUS_V1",
        "scope": "all connected triangle-free geng -tc graphs; loads selects an exhaustive connected Gamma-minimum maximum cut; all ell=5 complete shortest-row tuples",
        "orders": [args.n_min, args.n_max],
        "workers": args.workers,
        "generatedByOrder": {str(key): value for key, value in sorted(generated.items())},
        "inputStreams": streams,
        "counts": {key: value for key, value in sorted(aggregate["counts"].items())},
        "endpointKinds": {key: value for key, value in sorted(aggregate["endpointKinds"].items())},
        "sigmaHistogram": {str(key): value for key, value in sorted(aggregate["sigmaHistogram"].items())},
        "weakSingletonSigmaHistogram": {str(key): value for key, value in sorted(aggregate["weakPairHistogram"].items())},
        "firstWeakWeakSingleton": aggregate["firstWeakWeakSingleton"],
        "firstStructuralFailure": aggregate["firstStructuralFailure"],
        "elapsedSeconds": round(time.time() - started, 3),
        "verdict": "PASS" if aggregate["firstStructuralFailure"] is None else "FAIL",
    }
    payload["canonicalSha256"] = canonical_sha(payload)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
