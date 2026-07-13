"""Complete the 34 t=4 support cores by exact bad-atom circuits.

For each retained owner embedding, choose sixteen distinct same-shore
distance-four endpoint pairs, exactly four incident with each owner and at
least one common bad neighbour.  The bad-edge graph must stay triangle-free.
For each atom, its support is the union of ALL shortest length-four paths.
Inclusion-minimal defect one is checked by a 15-edge SDR after deleting each
of the sixteen atoms, which is equivalent to Hall on every proper atom subset.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations
from pathlib import Path

from enumerate_t4_support_graphs import decode_graph6, adjacency, bipartition, distances


HERE = Path(__file__).resolve().parent


def shortest_footprint(n, edges, source, target):
    adj = [[] for _ in range(n)]
    edge_id = {}
    for i, (u, v) in enumerate(edges):
        adj[u].append(v)
        adj[v].append(u)
        edge_id[(min(u, v), max(u, v))] = i
    ds = distances([set(xs) for xs in adj], source)
    dt = distances([set(xs) for xs in adj], target)
    assert ds[target] == 4
    footprint = 0
    row_count = 0

    def dfs(u, path):
        nonlocal footprint, row_count
        if len(path) == 5:
            if u == target:
                row_count += 1
                for a, b in zip(path, path[1:]):
                    footprint |= 1 << edge_id[(min(a, b), max(a, b))]
            return
        for w in adj[u]:
            if w in path:
                continue
            if ds[w] != ds[u] + 1:
                continue
            if ds[w] + dt[w] != 4:
                continue
            dfs(w, path + (w,))

    dfs(source, (source,))
    assert row_count > 0 and footprint
    return footprint, row_count


def triangle_free(n, support_edges, bad_edges):
    adj = [set() for _ in range(n)]
    for u, v in tuple(support_edges) + tuple(bad_edges):
        if v in adj[u]:
            return False
        adj[u].add(v)
        adj[v].add(u)
    return all(not (adj[u] & adj[v]) for u in range(n) for v in adj[u] if u < v)


def has_sdr(atom_masks, deleted):
    right_match = [-1] * 15

    def augment(a, seen):
        mask = atom_masks[a]
        while mask:
            bit = mask & -mask
            e = bit.bit_length() - 1
            mask ^= bit
            if seen[e]:
                continue
            seen[e] = True
            if right_match[e] < 0 or augment(right_match[e], seen):
                right_match[e] = a
                return True
        return False

    matched = 0
    for a in range(16):
        if a == deleted:
            continue
        if augment(a, [False] * 15):
            matched += 1
        else:
            return False
    return matched == 15


def deletion_sdrs(atom_masks):
    return all(has_sdr(atom_masks, deleted) for deleted in range(16))


def process_candidate(task):
    record, owner = task
    n, support_edges = decode_graph6(record["graph6"].encode("ascii"))
    adj = adjacency(n, support_edges)
    side = bipartition(adj)
    dists = tuple(distances(adj, u) for u in range(n))
    pairs = tuple((u, v) for u in range(n) for v in range(u + 1, n)
                  if side[u] == side[v] and dists[u][v] == 4)
    footprints = {}
    row_counts = {}
    for pair in pairs:
        footprints[pair], row_counts[pair] = shortest_footprint(
            n, support_edges, *pair)
    v, m = owner["v"], owner["m"]
    dv = tuple(owner["dist4V"])
    dm = tuple(owner["dist4M"])
    remaining_pairs = tuple(pair for pair in pairs if v not in pair and m not in pair)
    counts = Counter()
    hits = []
    if len(remaining_pairs) < 8:
        counts["insufficientRemainingPairs"] += 1
        return dict(counts), hits
    for bv in combinations(dv, 4):
        v_edges = {tuple(sorted((v, b))) for b in bv}
        for bm in combinations(dm, 4):
            if not (set(bv) & set(bm)):
                continue
            counts["ownerChoices"] += 1
            m_edges = {tuple(sorted((m, b))) for b in bm}
            forced = v_edges | m_edges
            assert len(forced) == 8
            if not triangle_free(n, support_edges, forced):
                counts["forcedTriangleReject"] += 1
                continue
            for extra in combinations(remaining_pairs, 8):
                counts["extraChoices"] += 1
                bad_edges = tuple(sorted(forced | set(extra)))
                if len(bad_edges) != 16:
                    continue
                if not triangle_free(n, support_edges, bad_edges):
                    counts["triangleReject"] += 1
                    continue
                counts["trianglePass"] += 1
                atom_masks = tuple(footprints[pair] for pair in bad_edges)
                union = 0
                degrees = [0] * 15
                for mask in atom_masks:
                    union |= mask
                    for e in range(15):
                        degrees[e] += (mask >> e) & 1
                if union != (1 << 15) - 1 or min(degrees) < 2:
                    counts["unionOrMultiplicityReject"] += 1
                    continue
                counts["unionMultiplicityPass"] += 1
                if not deletion_sdrs(atom_masks):
                    counts["circuitReject"] += 1
                    continue
                counts["circuitPass"] += 1
                hits.append({
                    "n": n,
                    "graph6": record["graph6"],
                    "owner": owner,
                    "selectedBadNeighboursV": list(bv),
                    "selectedBadNeighboursM": list(bm),
                    "badEdges": [list(pair) for pair in bad_edges],
                    "atomFootprints": [
                        [e for e in range(15) if (footprints[pair] >> e) & 1]
                        for pair in bad_edges
                    ],
                    "rowCounts": [row_counts[pair] for pair in bad_edges],
                    "edgeMultiplicities": degrees,
                })
    return dict(counts), hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    ns = parser.parse_args()
    assert 1 <= ns.workers <= 8
    source = json.loads(ns.input.read_text())
    tasks = [(record, owner) for record in source["candidates"]
             for owner in record["ownerEmbeddings"]]
    with mp.Pool(ns.workers) as pool:
        parts = pool.map(process_candidate, tasks)
    counts = Counter()
    hits = []
    for part_counts, part_hits in parts:
        counts.update(part_counts)
        hits.extend(part_hits)
    payload = {
        "schema": "T4_ATOM_CIRCUIT_CENSUS_V1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "supportEmbeddings": len(tasks),
        "counts": dict(sorted(counts.items())),
        "hits": hits,
        "scope": (
            "support graph + complete shortest footprints + 16 bad atoms + "
            "triangle-free + deletion SDRs; no maxcut/row-choice/Hall-ledger gate"
        ),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["canonicalSha256"] = sha256(canonical.encode("ascii")).hexdigest()
    ns.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["counts"], sort_keys=True))
    print("hits=" + str(len(hits)))
    print("canonical_sha256=" + payload["canonicalSha256"])


if __name__ == "__main__":
    main()
