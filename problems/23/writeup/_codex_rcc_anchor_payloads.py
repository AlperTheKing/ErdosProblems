"""Emit exact RCC primal payloads for the current Gap#1 anchor cases.

The emitted JSON files use the schema consumed by
`_claude_rcc_dual_verify.py`. They are deliberately tiny regression
fixtures: no floating point, no optimization, just the known exact primal
cover data from the anchor gate.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from _claude_rcc_anchors_gate import c5t_build, support_edges
from _claude_residual_hall_gate import residuals
from _codex_k2t_switch_probe import adj_from_edges


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "tmp" / "codex_rcc_anchor_payloads"
VERIFY = Path(__file__).with_name("_claude_rcc_dual_verify.py")


def edge_key(e):
    a, b = e
    return [min(a, b), max(a, b)]


def b_edges(n, adj, side):
    return [
        edge_key((a, b))
        for a in range(n)
        for b in adj[a]
        if a < b and side[a] != side[b]
    ]


def support_union(adj, side, rows):
    out = set()
    for e in rows:
        out.update(support_edges(adj, side, e))
    return sorted(edge_key(e) for e in out)


def write_payload(name, payload):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def c5_payload(t):
    n, adj, side = c5t_build(t)
    cd = residuals(n, adj, side)
    rows = sorted(e for e in cd["M"] if cd["ell"][e] == 5)
    a4 = [v for v in range(n) if v // t == 4]
    return {
        "n": n,
        "cut_edges": b_edges(n, adj, side),
        "rows": [edge_key(e) for e in rows],
        "F": support_union(adj, side, rows),
        "cuts": [[x] for x in a4],
        "sinks": {},
        "primal": {
            "lambda": {str(x): "1" for x in a4},
            "q": {},
        },
    }


def cp11_payload():
    vertices = ["p", "q", "a", "b", "bb", "c", "y", "w", "r1", "r2", "r3"]
    idx = {v: i for i, v in enumerate(vertices)}
    side_name = {v: 0 for v in ["p", "q", "b", "bb", "y", "w", "r2"]}
    for v in ["a", "c", "r1", "r3"]:
        side_name[v] = 1
    blue = [
        ("p", "a"),
        ("a", "b"),
        ("b", "c"),
        ("c", "y"),
        ("q", "c"),
        ("c", "bb"),
        ("bb", "a"),
        ("a", "w"),
        ("p", "r1"),
        ("r1", "r2"),
        ("r2", "r3"),
        ("r3", "q"),
    ]
    bad = [("p", "y"), ("q", "w"), ("p", "q")]
    edges = [edge_key((idx[a], idx[b])) for a, b in blue + bad]
    adj = adj_from_edges(len(vertices), edges)
    side = [side_name[v] for v in vertices]
    rows = [tuple(edge_key((idx[a], idx[b]))) for a, b in bad]
    return {
        "n": len(vertices),
        "cut_edges": b_edges(len(vertices), adj, side),
        "rows": [edge_key(e) for e in rows],
        "F": support_union(adj, side, rows),
        "cuts": [[idx["p"]], [idx["q"]]],
        "sinks": {},
        "primal": {
            "lambda": {str(idx["p"]): "1", str(idx["q"]): "1"},
            "q": {},
        },
        "names": {str(i): v for v, i in idx.items()},
    }


def bare_sse_24_payload():
    """The 24-vertex real counterexample to bare SSE, with a banked cover.

    Bad rows are the K3,3 cluster l_i-r_j. The multi-geodesic support is
    the eight-edge double-star l-u-w-v-r. The cover uses singleton cuts on
    the left cluster vertices. These saturate the three left support spokes
    and route the nine anchor-web off-support exits to one door sink.
    """
    n = 24
    left = [0, 1, 2]
    right = [3, 4, 5]
    u, w, v = 6, 7, 8
    a_left = [9, 10, 11]
    z_left = [12, 13, 14]
    middle = [15, 16, 17]
    z_right = [18, 19, 20]
    a_right = [21, 22, 23]

    edges = []

    def add(a, b):
        edges.append(tuple(edge_key((a, b))))

    def link(A, B):
        for a in A:
            for b in B:
                add(a, b)

    for x in left:
        add(x, u)
    add(u, w)
    add(w, v)
    for y in right:
        add(v, y)
    link(left, right)
    link(left, a_left)
    link(a_left, z_left)
    link(z_left, middle)
    link(middle, z_right)
    link(z_right, a_right)
    link(a_right, right)
    edges = sorted(set(edges))
    adj = adj_from_edges(n, edges)

    # This is the unique max-cut side recovered by _claude_verify_24vtx_ce.py:
    # K3,3 is bad; the double-star and anchor web are blue.
    side = [0] * n
    for block in [a_left, middle, a_right, [u, v]]:
        for x in block:
            side[x] = 1

    rows = [tuple(edge_key((x, y))) for x in left for y in right]
    support = support_union(adj, side, rows)
    cut_edges = b_edges(n, adj, side)
    support_set = {tuple(e) for e in support}
    off_support = [tuple(e) for e in cut_edges if tuple(e) not in support_set]

    routed = {}
    for x in left:
        for a in a_left:
            routed[f"{min(x, a)},{max(x, a)}|door"] = "1"

    return {
        "n": n,
        "cut_edges": cut_edges,
        "rows": [edge_key(e) for e in rows],
        "F": support,
        "cuts": [[x] for x in left],
        "sinks": {"door": {"kappa": "53", "inc": "all"}},
        "primal": {
            "lambda": {str(x): "1" for x in left},
            "q": routed,
        },
        "meta": {
            "name": "bare_sse_24_k33_doublestar",
            "off_support_count": len(off_support),
            "routed_count": len(routed),
            "sigma": 53,
        },
    }


def run_verify(path):
    proc = subprocess.run(
        [sys.executable, str(VERIFY), str(path)],
        cwd=str(Path(__file__).parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(proc.stdout, end="")
    ok = proc.returncode == 0 and "PRIMAL CERT: VERIFIED" in proc.stdout
    if not ok:
        raise SystemExit(f"verifier rejected {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "verifier": str(VERIFY.relative_to(ROOT)),
        "verified": True,
    }


def main():
    paths = [
        write_payload("c5_t1", c5_payload(1)),
        write_payload("c5_t2", c5_payload(2)),
        write_payload("c5_t3", c5_payload(3)),
        write_payload("cp11", cp11_payload()),
        write_payload("bare_sse_24", bare_sse_24_payload()),
    ]
    manifest = {
        "schema": "codex_rcc_anchor_payloads_v1",
        "verifier": str(VERIFY.relative_to(ROOT)),
        "payloads": [],
    }
    for path in paths:
        print(f"=== {path} ===")
        manifest["payloads"].append(run_verify(path))
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"manifest: {manifest_path} sha256={sha256(manifest_path)}")


if __name__ == "__main__":
    main()