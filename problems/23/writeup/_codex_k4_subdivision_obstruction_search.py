"""Exact targeted search for a local obstruction on a subdivided K4.

Every graph generated here is a bipartite subdivision of K4, hence has a K4
minor and is not series-parallel.  A witness would therefore falsify the
conjecture suggested by the m <= 15 census that every minimal local support
obstruction has series-parallel supply support.
"""

from __future__ import annotations

import itertools
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _claude_d3_local_obstruction as d3
from _codex_multiflow_footprint_gate import adjacency_masks, tw2_order_cached


BRANCH_EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def graph6(n: int, edges: list[tuple[int, int]]) -> str:
    if not 0 <= n <= 62:
        raise ValueError("the compact graph6 encoder supports n <= 62")
    edge_set = {tuple(sorted(edge)) for edge in edges}
    bits = [int((i, j) in edge_set) for j in range(1, n) for i in range(j)]
    bits.extend([0] * ((-len(bits)) % 6))
    chars = []
    for start in range(0, len(bits), 6):
        value = 0
        for bit in bits[start:start + 6]:
            value = (value << 1) | bit
        chars.append(chr(value + 63))
    return chr(n + 63) + "".join(chars)


def subdivision(lengths: tuple[int, ...]) -> str:
    next_vertex = 4
    edges: list[tuple[int, int]] = []
    for (u, v), length in zip(BRANCH_EDGES, lengths, strict=True):
        previous = u
        for _ in range(length - 1):
            current = next_vertex
            next_vertex += 1
            edges.append((previous, current))
            previous = current
        edges.append((previous, v))
    return graph6(next_vertex, edges)


def bipartite_parities(lengths: tuple[int, ...]) -> bool:
    length = dict(zip(BRANCH_EDGES, lengths, strict=True))

    def path(u: int, v: int) -> int:
        return length[tuple(sorted((u, v)))]

    return all(
        (path(a, b) + path(a, c) + path(b, c)) % 2 == 0
        for a, b, c in itertools.combinations(range(4), 3)
    )


def canonical_lengths(lengths: tuple[int, ...]) -> tuple[int, ...]:
    edge_index = {edge: index for index, edge in enumerate(BRANCH_EDGES)}
    images = []
    for permutation in itertools.permutations(range(4)):
        image = []
        for u, v in BRANCH_EDGES:
            preimage = tuple(sorted((permutation[u], permutation[v])))
            image.append(lengths[edge_index[preimage]])
        images.append(tuple(image))
    return min(images)


def init_worker(node_cap: int) -> None:
    d3.NODE_CAP = node_cap


def check_case(item: tuple[tuple[int, ...], str]) -> dict[str, object]:
    lengths, encoded = item
    witness, aborted, pair_count = d3.check_F((encoded,))
    order = tw2_order_cached(adjacency_masks(encoded))
    if order is not None:
        raise AssertionError("a K4 subdivision was incorrectly classified as treewidth <= 2")
    return {
        "lengths": lengths,
        "g6": encoded,
        "edges": sum(lengths),
        "m": sum(lengths) + 1,
        "distance4Pairs": pair_count,
        "aborted": aborted,
        "hasWitness": witness is not None,
        "witness": witness,
    }


def main() -> None:
    if len(sys.argv) not in (2, 3, 4):
        raise SystemExit("usage: script MAX_PATH_LENGTH [WORKERS] [NODE_CAP]")
    maximum = int(sys.argv[1])
    workers = int(sys.argv[2]) if len(sys.argv) >= 3 else 60
    node_cap = int(sys.argv[3]) if len(sys.argv) >= 4 else 5_000_000
    if not 1 <= maximum <= 9:
        raise SystemExit("MAX_PATH_LENGTH must be in 1..9 (graph6 n <= 62)")
    if not 1 <= workers <= 60:
        raise SystemExit("Windows multiprocessing pool requires 1..60 workers")

    representatives: dict[tuple[int, ...], str] = {}
    for lengths in itertools.product(range(1, maximum + 1), repeat=6):
        if not bipartite_parities(lengths):
            continue
        key = canonical_lengths(lengths)
        representatives.setdefault(key, subdivision(key))

    items = sorted(representatives.items(), key=lambda item: (sum(item[0]), item[0]))
    rows = []
    with Pool(workers, initializer=init_worker, initargs=(node_cap,)) as pool:
        for row in pool.imap_unordered(check_case, items, chunksize=max(1, len(items) // (workers * 8))):
            rows.append(row)

    rows.sort(key=lambda row: (row["m"], row["lengths"]))
    witnesses = [row for row in rows if row["hasWitness"]]
    aborted = [row for row in rows if row["aborted"]]
    result = {
        "maxPathLength": maximum,
        "nodeCap": node_cap,
        "representatives": len(rows),
        "minM": min((row["m"] for row in rows), default=None),
        "maxM": max((row["m"] for row in rows), default=None),
        "witnesses": len(witnesses),
        "aborted": len(aborted),
        "firstWitnesses": witnesses[:5],
        "firstAborted": aborted[:20],
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
