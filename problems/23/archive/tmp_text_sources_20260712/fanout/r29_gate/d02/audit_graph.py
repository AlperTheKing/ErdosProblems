#!/usr/bin/env python3
"""Independent exact audit of a canonical finite simple graph JSON file.

Accepted schema: {"vertices": [JSON scalars...], "edges": [[u,v], ...]}.
No graph library and no floating-point arithmetic are used.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def audit(obj):
    vertices = obj["vertices"]
    if len(vertices) != len(set(map(canon, vertices))):
        raise ValueError("duplicate vertex")
    keys = {canon(v): v for v in vertices}
    adj = {k: set() for k in keys}
    edge_keys = set()
    for i, edge in enumerate(obj["edges"]):
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"edge {i} is not a pair")
        a, b = map(canon, edge)
        if a not in keys or b not in keys:
            raise ValueError(f"edge {i} has unknown endpoint")
        if a == b:
            raise ValueError(f"loop at edge {i}: {keys[a]!r}")
        e = tuple(sorted((a, b)))
        if e in edge_keys:
            raise ValueError(f"duplicate undirected edge at index {i}")
        edge_keys.add(e)
        adj[a].add(b)
        adj[b].add(a)

    triangle = None
    for a, b in sorted(edge_keys):
        common = adj[a].intersection(adj[b])
        if common:
            c = min(common)
            triangle = [keys[a], keys[b], keys[c]]
            break

    components = []
    unseen = set(adj)
    while unseen:
        root = min(unseen)
        q, seen = deque([root]), {root}
        unseen.remove(root)
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v); seen.add(v); q.append(v)
        components.append(sorted((keys[k] for k in seen), key=canon))
    components.sort(key=lambda c: canon(c[0]) if c else "")
    disconnected_witness = None
    if len(components) > 1:
        disconnected_witness = [components[0][0], components[1][0]]
    return {
        "vertex_count": len(vertices), "edge_count": len(edge_keys),
        "triangle_free": triangle is None, "triangle_witness": triangle,
        "connected": len(components) <= 1,
        "component_count": len(components),
        "component_sizes": [len(c) for c in components],
        "disconnected_witness": disconnected_witness,
    }


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    out = {"arithmetic": "integer/set logic only"}
    if args.self_test:
        tri = audit({"vertices": [0,1,2], "edges": [[0,1],[1,2],[0,2]]})
        disc = audit({"vertices": [0,1,2], "edges": [[0,1]]})
        assert tri["triangle_witness"] == [0,1,2]
        assert disc["disconnected_witness"] == [0,2]
        out["self_test"] = {"triangle_witness": tri["triangle_witness"],
                            "disconnected_witness": disc["disconnected_witness"]}
    if args.input:
        raw = args.input.read_bytes()
        obj = json.loads(raw)
        out["input_path"] = str(args.input)
        out["input_sha256"] = sha256_bytes(raw)
        out["audit"] = audit(obj)
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
