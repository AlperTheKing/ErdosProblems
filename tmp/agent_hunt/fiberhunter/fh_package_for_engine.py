#!/usr/bin/env python3
"""Package the fiberhunter falsifier candidate in the engine's source-JSON format,
then the engine's own gate script (check_t5_active_scope_profile.py) can be run on it
unmodified.  Expected verdict if the falsifier is real: HIT_POSITIVE_ACTIVE_SCOPE_PROFILE."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

OUT = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\fiberhunter")


def e(u, v):
    return (u, v) if u < v else (v, u)


def bfs(adj, src, n):
    d = [-1] * n
    d[src] = 0
    q = [src]
    h = 0
    while h < len(q):
        c = q[h]
        h += 1
        for x in adj[c]:
            if d[x] == -1:
                d[x] = d[c] + 1
                q.append(x)
    return d


def four_paths(adj, a, b):
    out = []
    for m1 in adj[a]:
        if m1 == b:
            continue
        for m2 in adj[m1]:
            if m2 in (a, b):
                continue
            for m3 in adj[m2]:
                if m3 in (a, b, m1):
                    continue
                if b in adj[m3]:
                    out.append((a, m1, m2, m3, b))
    return out


def row_edges(r):
    return sorted({tuple(sorted((r[k], r[k + 1]))) for k in range(4)})


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def g6_encode(n, edges):
    bits = []
    es = {tuple(sorted(x)) for x in edges}
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in es else 0)
    while len(bits) % 6:
        bits.append(0)
    chars = [chr(63 + n)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        chars.append(chr(63 + v))
    return "".join(chars)


def main():
    data = json.loads((OUT / "fh_FALSIFIER.json").read_text(encoding="utf-8"))
    support = sorted(e(*x) for x in data["edges"])
    chosen = sorted(e(*p) for p in data["atoms"])
    n, n1 = 18, 9
    adj = [set() for _ in range(n)]
    for a, b in support:
        adj[a].add(b)
        adj[b].add(a)
    shore = ["L" if z < n1 else "R" for z in range(n)]
    sel_atoms = []
    for a, b in chosen:
        rows = sorted(four_paths(adj, a, b))
        fpr = sorted({tuple(x) for r in rows for x in row_edges(r)})
        sel_atoms.append({
            "u": a, "v": b, "shore": shore[a],
            "rows": [list(r) for r in rows],
            "footprintEdges": [list(x) for x in fpr],
        })
    payload = {
        "schema": "fiberhunter-falsifier-package-v1",
        "left": 9, "right": 9,
        "hit": {
            "graph6": g6_encode(n, support),
            "supportEdges": [list(x) for x in support],
            "selectedAtoms": sel_atoms,
            "selectionMeta": {
                "localClassifiers": {"0": {"activeNeighbour": 9}},
            },
        },
    }
    payload["canonicalSha256"] = canonical_sha(payload)
    out = OUT / "fh_falsifier_engine_format.json"
    out.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("written:", out)
    print("canonicalSha256:", payload["canonicalSha256"])
    print("graph6:", payload["hit"]["graph6"])


if __name__ == "__main__":
    main()
