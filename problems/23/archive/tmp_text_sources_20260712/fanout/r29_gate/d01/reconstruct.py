"""Exact, deterministic reconstruction of every R29 class fixed by local sources.

The output deliberately stops where the R29 archive is under-specified.
No floating-point operations are used.
"""
from collections import deque
from hashlib import sha256
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

def E(u, v): return tuple(sorted((u, v)))

def shortest_path(edges, s, t):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v); adj.setdefault(v, []).append(u)
    for v in adj: adj[v].sort()
    parent = {s: None}; q = deque([s])
    while q:
        u = q.popleft()
        if u == t: break
        for v in adj.get(u, ()):
            if v not in parent: parent[v] = u; q.append(v)
    assert t in parent
    p = []; u = t
    while u is not None: p.append(u); u = parent[u]
    return tuple(reversed(p))

def build():
    edges = set(); classes = {}
    hubs = ("T:r", "T:cL", "T:cR")
    left = [f"T:L:{i:02d}" for i in range(26)]
    right = [f"T:R:{i:02d}" for i in range(26)]
    anchor = "T:anchor"
    traffic_core = {E(hubs[0], hubs[1]), E(hubs[0], hubs[2])}
    traffic_core |= {E(hubs[1], x) for x in left} | {E(hubs[2], x) for x in right}
    traffic_bad = {E(x, y) for x in left for y in right}
    arms = set()
    for side, leaves in (("L", left), ("R", right)):
        for i, leaf in enumerate(leaves):
            for j in range(26):
                x, y = f"T:A:{side}:{i:02d}:{j:02d}:0", f"T:A:{side}:{i:02d}:{j:02d}:1"
                arms |= {E(anchor, x), E(x, y), E(y, leaf)}
    classes["traffic"] = traffic_core | traffic_bad | arms
    edges |= classes["traffic"]
    assert len(traffic_core) == 54 and len(traffic_bad) == 676 and len(arms) == 4056
    assert len(classes["traffic"]) == 4786

    # Exact circuit from _codex_pro_active_cycle_counterexample_verify.py.
    w = 26
    support_i = {tuple(sorted((i, (i + 1) % 26))) for i in range(26)} | {(0, w)}
    atoms_i = {tuple(sorted((i, (i + 4) % 26))) for i in range(26)} | {(3, w), (23, w)}
    av = [(9 * k) % 26 for k in range(13)]
    active_i = {tuple(sorted((av[i], av[i+1]))) for i in range(12)}
    blue_i = support_i | active_i
    selected_circuit_rows = []
    nxt = 27
    for a, b in sorted(atoms_i):
        internal = list(range(nxt, nxt + 5)); nxt += 5
        path = [a] + internal + [b]
        blue_i |= {tuple(sorted(e)) for e in zip(path, path[1:])}
    assert nxt == 167 and len(blue_i) == 207
    c = lambda i: f"C:{i:03d}"
    circuit_blue = {E(c(u), c(v)) for u, v in blue_i}
    circuit_bad = {E(c(u), c(v)) for u, v in atoms_i}
    classes["circuit"] = circuit_blue | circuit_bad
    edges |= classes["circuit"]
    assert len(classes["circuit"]) == 235
    for a, b in sorted(atoms_i):
        p = shortest_path(circuit_blue, c(a), c(b))
        assert len(p) == 5
        selected_circuit_rows.append(p)

    double_rows = [(left[i], hubs[1], hubs[0], hubs[2], right[j]) for i in range(26) for j in range(26)]
    vertices = sorted({x for e in edges for x in e})
    assert len(vertices) == 2927 and len(edges) == 5021
    known_rows = sorted(double_rows + selected_circuit_rows)
    graph_obj = {"format":"r29-known-subgraph-v1", "vertices":vertices,
                 "edges":[list(e) for e in sorted(edges)],
                 "selected_rows":[list(r) for r in known_rows],
                 "class_counts":{"traffic":4786,"circuit":235}}
    raw = (json.dumps(graph_obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (OUT / "known_subgraph.json").write_bytes(raw)
    cert = {
      "format":"r29-reconstruction-gate-v1", "arithmetic":"integers-only",
      "status":"UNDERDETERMINED", "reconstructed":{"vertices":2927,"edges":5021,
      "selected_rows":len(known_rows),"double_star_rows":676,"circuit_rows":28},
      "claimed":{"vertices":2943,"edges":8422,"selected_atoms":1383,
      "class_edge_counts":[4786,3380,15,235,6]},
      "missing":{"vertices":16,"edges":3401,"selected_rows":679,
      "classes":{"selector_C5":3380,"cable_seed_C5":15,"cable":6}},
      "exact_identities":{"edge_sum":4786+3380+15+235+6,
      "maxcut_sum":4110+2704+12+207+6,"rigid_atoms":676+28+3,
      "nontrivial_replacements":676*679},
      "canonicalization":"UTF-8 JSON; sorted vertex labels; undirected endpoints sorted; edges and rows lexicographically sorted; compact keys sorted; LF terminator",
      "sha256":{"known_subgraph.json":sha256(raw).hexdigest()},
      "falsifier":"Any source-complete constructor must specify all 3380 selector-C5 edges, 15 cable-seed-C5 edges, 6 cable edges, their 16 new vertices, and 679 omitted selected rows.",
      "proof_gaps":["selector incidence map and qL/qR partition","14/16 new-vertex accounting ambiguity","three private C5 layouts","cable endpoint labels into circuit","canonical selected selector rows"]
    }
    cert_raw = (json.dumps(cert, sort_keys=True, indent=2) + "\n").encode()
    (OUT / "certificate.json").write_bytes(cert_raw)
    print(json.dumps(cert, sort_keys=True))

if __name__ == "__main__": build()
