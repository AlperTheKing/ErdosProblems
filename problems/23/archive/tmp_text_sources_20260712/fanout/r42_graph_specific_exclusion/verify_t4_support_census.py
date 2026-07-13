"""Independent NetworkX/geng replay of the 153,978 support-graph census."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from hashlib import sha256
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"
SOURCE = HERE / "t4_support_graph_census.json"


def verify_hash(payload):
    body = dict(payload)
    claimed = body.pop("canonicalSha256")
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("ascii")).hexdigest() == claimed
    return claimed


def owner_embeddings(graph):
    colors = nx.algorithms.bipartite.color(graph)
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    degree4 = [v for v, d in graph.degree if d == 4]
    out = []
    for pos, v in enumerate(degree4):
        dv = {z for z in graph if colors[z] == colors[v] and distances[v].get(z) == 4}
        if len(dv) < 4:
            continue
        for m in degree4[pos + 1:]:
            if colors[m] != colors[v]:
                continue
            dm = {z for z in graph if colors[z] == colors[m] and distances[m].get(z) == 4}
            common_blue = set(graph[v]) & set(graph[m])
            common_bad = dv & dm
            if len(dm) >= 4 and len(common_blue) >= 2 and common_bad:
                out.append({
                    "v": v,
                    "m": m,
                    "commonBlue": sorted(common_blue),
                    "dist4V": sorted(dv),
                    "dist4M": sorted(dm),
                    "commonBadCandidates": sorted(common_bad),
                })
    return out


def main():
    source = json.loads(SOURCE.read_text())
    claimed_hash = verify_hash(source)
    expected = {(row["graph6"], json.dumps(row["ownerEmbeddings"], sort_keys=True))
                for row in source["candidates"]}
    observed = set()
    by_n = {}
    for n in range(8, 16):
        proc = subprocess.Popen(
            [str(GENG), "-q", "-c", "-b", str(n), "15:15"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert proc.stdout is not None
        counts = Counter()
        for raw in proc.stdout:
            graph = nx.from_graph6_bytes(raw.strip())
            assert len(graph) == n and graph.number_of_edges() == 15
            assert nx.is_connected(graph) and nx.is_bipartite(graph)
            counts["graphs"] += 1
            owners = owner_embeddings(graph)
            if owners:
                counts["graphsWithOwnerEmbedding"] += 1
                counts["ownerEmbeddings"] += len(owners)
                observed.add((raw.decode("ascii").strip(),
                              json.dumps(owners, sort_keys=True)))
        stderr = proc.stderr.read().decode("ascii", errors="replace") if proc.stderr else ""
        assert proc.wait() == 0, stderr
        by_n[str(n)] = dict(counts)
        for key in ("graphs", "graphsWithOwnerEmbedding", "ownerEmbeddings"):
            by_n[str(n)].setdefault(key, 0)
            assert by_n[str(n)][key] == source["byN"][str(n)][key]
    assert observed == expected
    result = {
        "verdict": "PASS_INDEPENDENT_NETWORKX_SUPPORT_CENSUS",
        "sourceCanonicalSha256": claimed_hash,
        "graphs": sum(row["graphs"] for row in by_n.values()),
        "graphsWithOwnerEmbedding": sum(row["graphsWithOwnerEmbedding"] for row in by_n.values()),
        "ownerEmbeddings": sum(row["ownerEmbeddings"] for row in by_n.values()),
        "candidatePayloadsEqual": True,
        "decoder": "networkx.from_graph6_bytes",
    }
    out = HERE / "t4_support_census_verification.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
