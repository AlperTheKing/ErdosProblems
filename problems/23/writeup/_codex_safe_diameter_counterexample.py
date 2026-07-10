"""Independent exact verifier for the first SAFE-DIAMETER<=2 falsifier."""

from __future__ import annotations

import hashlib
import json

import _codex_internal_offsupport_gate as gate
import _codex_random_active_component_search as random_gate
from _codex_safe_component_signature_probe import inspect


N = 22
SUPPORT = [
    (0, 1), (0, 2), (1, 3), (3, 4), (3, 5), (1, 6), (1, 7),
    (4, 8), (0, 9), (5, 10), (2, 11), (4, 12), (4, 13),
    (3, 14), (7, 15), (5, 16), (4, 17), (0, 18), (6, 19),
    (7, 20), (5, 21),
]
ATOMS = [
    (2, 15), (2, 20), (4, 15), (6, 11), (6, 12), (7, 11),
    (7, 13), (7, 16), (8, 10), (8, 16), (9, 14), (9, 19),
    (10, 17), (12, 21), (13, 21), (14, 15), (14, 20),
    (15, 18), (15, 19), (16, 17), (18, 20), (19, 20),
]
FORCED_PATH = [2, 10, 18, 17]


def support_masks():
    adj = [set() for _ in range(N)]
    for u, v in SUPPORT:
        adj[u].add(v)
        adj[v].add(u)
    masks = []
    for a, b in ATOMS:
        da, db = gate.bfs(adj, a), gate.bfs(adj, b)
        assert da[b] == 4
        mask = 0
        for i, (u, v) in enumerate(SUPPORT):
            if da[u] + 1 + db[v] == 4 or da[v] + 1 + db[u] == 4:
                mask |= 1 << i
        masks.append(mask)
    return masks


def main():
    masks = support_masks()
    assert len(ATOMS) == len(SUPPORT) + 1
    assert random_gate.exact_minimal_circuit(masks, len(SUPPORT))
    full = [set() for _ in range(N)]
    for u, v in SUPPORT + ATOMS:
        full[u].add(v)
        full[v].add(u)
    assert all(not (full[u] & full[v]) for u, v in SUPPORT + ATOMS)
    for i in range(len(FORCED_PATH) - 1):
        chord = tuple(sorted((FORCED_PATH[i], FORCED_PATH[i + 1])))
        assert gate.valid_offsupport_set(N, SUPPORT, ATOMS, {chord})
    probe = inspect(N, SUPPORT, ATOMS)
    assert probe["maxSafeDiameter"] == 3
    active, nodes, capped = random_gate.active_path(
        N, SUPPORT, ATOMS, node_cap=10_000_000)
    assert active is None and not capped
    payload = json.dumps({
        "n": N, "support": SUPPORT, "atoms": ATOMS,
        "forcedPath": FORCED_PATH,
    }, sort_keys=True, separators=(",", ":")).encode("ascii")
    print(json.dumps({
        "exactMinimalCircuit": True,
        "triangleFree": True,
        "forcedSingletonChordsSafe": True,
        "maxSafeDiameter": probe["maxSafeDiameter"],
        "diameterWitness": probe["diameterWitness"],
        "jointActive": active,
        "activeSearchNodes": nodes,
        "payloadSHA256": hashlib.sha256(payload).hexdigest(),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
