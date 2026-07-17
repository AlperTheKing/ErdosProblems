"""Exact first-pass census for the corrected t=4,k=2 support target.

Enumerates every connected unlabeled bipartite graph with 8..15 vertices and
exactly 15 edges using nauty geng.  It retains owner embeddings forced by the
live rotor geometry, without imposing the refuted ambient<=4 restriction.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import subprocess
from collections import Counter, deque
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def decode_graph6(line: bytes):
    data = line.strip()
    assert data and data[0] != ord(">")
    n = data[0] - 63
    assert 0 <= n <= 62
    bits = []
    for c in data[1:]:
        value = c - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, tuple(edges)


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bipartition(adj):
    side = [-1] * len(adj)
    for root in range(len(adj)):
        if side[root] >= 0:
            continue
        side[root] = 0
        todo = deque([root])
        while todo:
            u = todo.popleft()
            for v in adj[u]:
                if side[v] < 0:
                    side[v] = side[u] ^ 1
                    todo.append(v)
                else:
                    assert side[v] != side[u]
    return tuple(side)


def distances(adj, source):
    dist = [-1] * len(adj)
    dist[source] = 0
    todo = deque([source])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                todo.append(v)
    return tuple(dist)


def owner_embeddings(n, edges):
    adj = adjacency(n, edges)
    side = bipartition(adj)
    dists = tuple(distances(adj, v) for v in range(n))
    out = []
    degree4 = [v for v in range(n) if len(adj[v]) == 4]
    for ix, v in enumerate(degree4):
        dv = {z for z in range(n) if side[z] == side[v] and dists[v][z] == 4}
        if len(dv) < 4:
            continue
        for m in degree4[ix + 1:]:
            if side[m] != side[v]:
                continue
            common_blue = adj[v] & adj[m]
            if len(common_blue) < 2:
                continue
            dm = {z for z in range(n) if side[z] == side[m] and dists[m][z] == 4}
            common_bad_candidates = dv & dm
            if len(dm) < 4 or not common_bad_candidates:
                continue
            out.append({
                "v": v,
                "m": m,
                "commonBlue": sorted(common_blue),
                "dist4V": sorted(dv),
                "dist4M": sorted(dm),
                "commonBadCandidates": sorted(common_bad_candidates),
            })
    return out


def worker(task):
    residue, modulus = task
    counts = Counter()
    candidates = []
    for n in range(8, 16):
        cmd = [str(GENG), "-q", "-c", "-b", str(n), "15:15",
               f"{residue}/{modulus}"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert proc.stdout is not None
        for raw in proc.stdout:
            gn, edges = decode_graph6(raw)
            assert gn == n and len(edges) == 15
            counts[(n, "graphs")] += 1
            owners = owner_embeddings(n, edges)
            if owners:
                counts[(n, "graphsWithOwnerEmbedding")] += 1
                counts[(n, "ownerEmbeddings")] += len(owners)
                candidates.append({
                    "n": n,
                    "graph6": raw.decode("ascii").strip(),
                    "ownerEmbeddings": owners,
                })
        stderr = proc.stderr.read().decode("ascii", errors="replace") if proc.stderr else ""
        rc = proc.wait()
        assert rc == 0, (cmd, rc, stderr)
    return dict(counts), candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    ns = parser.parse_args()
    assert 1 <= ns.workers <= 8
    with mp.Pool(ns.workers) as pool:
        parts = pool.map(worker, [(r, ns.workers) for r in range(ns.workers)])
    total = Counter()
    candidates = []
    for counts, part_candidates in parts:
        total.update(counts)
        candidates.extend(part_candidates)
    by_n = {}
    for n in range(8, 16):
        by_n[str(n)] = {
            "graphs": total[(n, "graphs")],
            "graphsWithOwnerEmbedding": total[(n, "graphsWithOwnerEmbedding")],
            "ownerEmbeddings": total[(n, "ownerEmbeddings")],
        }
    payload = {
        "schema": "T4_SUPPORT_GRAPH_CENSUS_V1",
        "geng": str(GENG.relative_to(ROOT)).replace("\\", "/"),
        "workers": ns.workers,
        "edges": 15,
        "vertexRange": [8, 15],
        "filter": (
            "connected bipartite; deg(v)=deg(m)=4; same shore; at least "
            "two common neighbors; each has >=4 same-shore distance-4 "
            "vertices; common distance-4 vertex exists"
        ),
        "byN": by_n,
        "totals": {
            key: sum(row[key] for row in by_n.values())
            for key in ("graphs", "graphsWithOwnerEmbedding", "ownerEmbeddings")
        },
        "candidates": sorted(candidates, key=lambda row: (row["n"], row["graph6"])),
        "scope": "support-graph first pass; no atom-set or maxcut conclusion",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["canonicalSha256"] = sha256(canonical.encode("ascii")).hexdigest()
    ns.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["totals"], sort_keys=True))
    print("canonical_sha256=" + payload["canonicalSha256"])


if __name__ == "__main__":
    main()
