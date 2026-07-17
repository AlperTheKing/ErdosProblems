"""Independent replay of the decisive forced-through-owner exclusion."""

from __future__ import annotations

import json
from collections import Counter, deque
from hashlib import sha256
from pathlib import Path


HERE = Path(__file__).resolve().parent
ATOM_PATH = HERE / "t4_atom_circuit_census.json"
PROFILE_PATH = HERE / "t4_profile_transition_census.json"


def verify_hash(payload):
    payload = dict(payload)
    claimed = payload.pop("canonicalSha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("ascii")).hexdigest() == claimed
    return claimed


def decode_graph6(text):
    raw = text.encode("ascii")
    n = raw[0] - 63
    bits = []
    for c in raw[1:]:
        value = c - 63
        for shift in range(5, -1, -1):
            bits.append((value >> shift) & 1)
    edges = []
    k = 0
    for high in range(1, n):
        for low in range(high):
            if bits[k]:
                edges.append((low, high))
            k += 1
    return n, tuple(edges)


def all_rows(n, edges, source, target):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    dist = [-1] * n
    dist[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    assert dist[target] == 4
    rows = []

    def visit(path):
        if len(path) == 5:
            if path[-1] == target:
                rows.append(path)
            return
        for v in adj[path[-1]]:
            if v not in path and dist[v] == dist[path[-1]] + 1:
                visit(path + (v,))

    visit((source,))
    return tuple(sorted(rows))


def main():
    atom = json.loads(ATOM_PATH.read_text())
    profile = json.loads(PROFILE_PATH.read_text())
    atom_hash = verify_hash(atom)
    profile_hash = verify_hash(profile)
    hist_v = Counter()
    hist_m = Counter()
    graph6s = set()
    raw_middle_swaps = 0
    for hit in atom["hits"]:
        n, edges = decode_graph6(hit["graph6"])
        assert n == 15 and len(edges) == 15
        graph6s.add(hit["graph6"])
        bad_edges = tuple(tuple(edge) for edge in hit["badEdges"])
        assert len(bad_edges) == len(set(bad_edges)) == 16
        v = hit["owner"]["v"]
        m = hit["owner"]["m"]
        forced_v = forced_m = 0
        counts = []
        for bad in bad_edges:
            rows = all_rows(n, edges, *bad)
            counts.append(len(rows))
            forced_v += all(v in row for row in rows)
            forced_m += all(m in row for row in rows)
            for i, row_a in enumerate(rows):
                for row_b in rows[i + 1:]:
                    if (row_a[0] == row_b[0] and row_a[4] == row_b[4]
                            and row_a[1] == row_b[1]
                            and row_a[3] == row_b[3]
                            and {row_a[2], row_b[2]} == {v, m}):
                        raw_middle_swaps += 1
        assert counts == hit["rowCounts"]
        assert forced_v >= 8 and forced_m >= 8
        hist_v[forced_v] += 1
        hist_m[forced_m] += 1
    assert len(atom["hits"]) == 576
    assert len(graph6s) == 4
    assert profile["circuits"] == 576
    assert profile["circuitsWithProfileMiddleTransition"] == 0
    assert profile["circuitsWithCentralProfileTransition"] == 0
    assert profile["circuitsWithRawMiddleTransition"] == 0
    assert profile["circuitsWithNoRProfileMiddleTransition"] == 0
    assert raw_middle_swaps == 0
    result = {
        "verdict": "PASS_T4_RAW_MIDDLE_SWAP_EXCLUSION",
        "atomCanonicalSha256": atom_hash,
        "profileCanonicalSha256": profile_hash,
        "circuitsChecked": 576,
        "supportIsomorphismTypes": 4,
        "minimumForcedThroughV": min(hist_v),
        "minimumForcedThroughM": min(hist_m),
        "rawMiddleSwaps": raw_middle_swaps,
        "forcedHistogramV": dict(sorted(hist_v.items())),
        "forcedHistogramM": dict(sorted(hist_m.items())),
        "contradiction": (
            "no complete row family contains a live v<->m middle swap; "
            "additionally every row choice has r(owner)>=8"
        ),
        "scope": "replay of emitted candidate circuits; geng coverage verified separately",
    }
    out = HERE / "t4_profile_exclusion_verification.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
