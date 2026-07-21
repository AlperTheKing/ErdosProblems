#!/usr/bin/env python3
"""WOWII 144 ORACLE - exhaustive small-n verification sweep (EXACT arithmetic).

Claims verified on ALL connected simple graphs with 3 <= n <= 9 (nauty geng -c):

  (a) C144      : cyclic G          ==>  tree(G) >= girth - 1 + e
                  (e = ecc(G, center) in the FC sense, invariants.ecc_of_set)
  (b) E_exists  : cyclic G          ==>  e <= max over shortest cycles K of M(K)
  (c) E_forall4 : cyclic G, g >= 4  ==>  e <= min over shortest cycles K of M(K)
  (d) P2        : cyclic G          ==>  tree(G) >= diam + ceil(g/2) - 1

Tools: exact bitmask library problems_external/wowii_141/oracle/invariants.py
(largest_induced_tree, girth, all_pairs_dist, eccentricities, ecc_of_set) and
M_of_cycle from problems_external/wowii_144/wave2/lemma_e_tests.py.

Shortest cycles: since girth(G) = g, a vertex set S with |S| = g whose induced
subgraph is 2-regular and connected is exactly the vertex set of a (shortest,
hence chordless) cycle of length g; conversely every shortest cycle is
chordless so its vertex set has this form.  M_of_cycle only consumes the
vertex SET of K, so enumerating these sets enumerates all shortest cycles
(up to rotation/reflection, which M(K) does not see).  Enumeration is capped
at CYCLE_CAP = 5000 per graph; cap hits are recorded (none can occur for
n <= 9: #g-subsets <= C(9,4) = 126).

Graph source: geng -c n for n = 3..9 (tools/nauty2_8_9/geng.exe, nauty 2.8.9).
graph6 is parsed directly (n <= 62 short form).  Multiprocessing: 8 workers.

Output: results JSON + SHA256, written next to this script.
Run:  python run_sweep.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
W141 = HERE.parent.parent / "wowii_141" / "oracle"
W144O = HERE.parent / "oracle"
W144W2 = HERE.parent / "wave2"
sys.path.insert(0, str(W141))
sys.path.insert(0, str(W144O))
sys.path.insert(0, str(W144W2))

from invariants import (  # noqa: E402
    all_pairs_dist,
    ecc_of_set,
    eccentricities,
    girth,
    graph_connected,
    largest_induced_tree,
)
from lemma_e_tests import M_of_cycle  # noqa: E402

GENG = Path("E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")
CYCLE_CAP = 5000
WORKERS = 8
OUT = HERE / "results_n3_9.json"

CLAIMS = ("a_C144", "b_E_exists", "c_E_forall_g4", "d_P2")


def parse_graph6(line: str) -> tuple[int, list[int]]:
    """Parse a short-form graph6 string (n <= 62) into (n, adj bitmasks)."""
    data = [ord(ch) - 63 for ch in line.strip()]
    n = data[0]
    if not (0 <= n <= 62):
        raise ValueError(f"unsupported graph6 header: {line!r}")
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


def shortest_cycle_vertex_sets(n: int, adj: list[int], g: int,
                               cap: int) -> tuple[list[list[int]], bool]:
    """All vertex sets of shortest (length-g) cycles; (sets, cap_hit).

    S is the vertex set of a g-cycle in G with girth g  iff  |S| = g and the
    induced subgraph G[S] is connected and 2-regular (any such subgraph is a
    cycle of length g = girth, necessarily shortest; any shortest cycle is
    chordless hence induces exactly this)."""
    out = []
    cap_hit = False
    for combo in combinations(range(n), g):
        mask = 0
        for v in combo:
            mask |= 1 << v
        if all((adj[v] & mask).bit_count() == 2 for v in combo):
            # 2-regular on g vertices; connected <=> single cycle
            # (2-regular graph on g vertices with girth g cannot split into
            #  shorter cycles, but check connectivity anyway for rigor)
            start = mask & -mask
            reached = start
            frontier = start
            while frontier:
                new = 0
                f = frontier
                while f:
                    b = f & -f
                    f ^= b
                    new |= adj[b.bit_length() - 1]
                new &= mask & ~reached
                reached |= new
                frontier = new
            if reached == mask:
                out.append(list(combo))
                if len(out) >= cap:
                    cap_hit = True
                    break
    return out, cap_hit


def check_graph(line: str) -> dict | None:
    """Return per-graph verdicts, or None for acyclic graphs (no claim applies)."""
    n, adj = parse_graph6(line)
    assert graph_connected(n, adj), f"geng -c produced disconnected {line!r}"
    g = girth(n, adj)
    if g == 0:
        return None  # acyclic: all four claims are restricted to cyclic G
    dist = all_pairs_dist(n, adj)
    ecc_v = eccentricities(n, dist)
    r = min(ecc_v)
    diam = max(ecc_v)
    center_mask = 0
    for v in range(n):
        if ecc_v[v] == r:
            center_mask |= 1 << v
    e = ecc_of_set(n, dist, center_mask)
    t = largest_induced_tree(n, adj)[0]

    cycles, cap_hit = shortest_cycle_vertex_sets(n, adj, g, CYCLE_CAP)
    assert cycles, f"girth {g} but no shortest cycle found in {line!r}"
    m_vals = [M_of_cycle(n, adj, K) for K in cycles]
    m_max, m_min = max(m_vals), min(m_vals)

    slacks = {
        "a_C144": t - (g - 1 + e),
        "b_E_exists": m_max - e,
        "c_E_forall_g4": (m_min - e) if g >= 4 else None,
        "d_P2": t - (diam + (g + 1) // 2 - 1),
    }
    return {
        "g6": line.strip(), "n": n, "girth": g, "e": e, "tree": t,
        "diam": diam, "radius": r, "m_max": m_max, "m_min": m_min,
        "n_shortest_cycles": len(cycles), "cap_hit": cap_hit,
        "e_ge_1": e >= 1,
        "slacks": slacks,
    }


def new_section() -> dict:
    return {"checked": 0, "violations": 0, "violating_graph6": [],
            "min_slack": None, "min_slack_graph6": None, "slack_hist": {}}


def fold(sec: dict, slack: int, g6: str) -> None:
    sec["checked"] += 1
    key = str(slack)
    sec["slack_hist"][key] = sec["slack_hist"].get(key, 0) + 1
    if sec["min_slack"] is None or slack < sec["min_slack"]:
        sec["min_slack"] = slack
        sec["min_slack_graph6"] = g6
    if slack < 0:
        sec["violations"] += 1
        if len(sec["violating_graph6"]) < 1000:
            sec["violating_graph6"].append(g6)


def main() -> None:
    t0 = time.time()
    summary = {
        "test": "WOWII144_exhaustive_oracle_n3_9",
        "date": "2026-07-18",
        "generator": "geng -c (nauty 2.8.9, tools/nauty2_8_9/geng.exe)",
        "cycle_cap": CYCLE_CAP,
        "cycle_cap_ever_hit": False,
        "per_n": {},
        "claims": {c: new_section() for c in CLAIMS},
        "totals": {"connected": 0, "cyclic": 0, "acyclic": 0,
                   "cyclic_e_ge_1": 0},
    }
    pool = Pool(WORKERS)
    try:
        for n in range(3, 10):
            proc = subprocess.run(
                [str(GENG), "-c", "-q", str(n)],
                capture_output=True, text=True, check=True)
            lines = proc.stdout.split()
            per_n = {"connected": len(lines), "cyclic": 0, "acyclic": 0,
                     "claims": {c: new_section() for c in CLAIMS}}
            for res in pool.imap_unordered(check_graph, lines,
                                           chunksize=256):
                if res is None:
                    per_n["acyclic"] += 1
                    continue
                per_n["cyclic"] += 1
                if res["cap_hit"]:
                    summary["cycle_cap_ever_hit"] = True
                if res["e_ge_1"]:
                    summary["totals"]["cyclic_e_ge_1"] += 1
                for c in CLAIMS:
                    s = res["slacks"][c]
                    if s is None:
                        continue
                    fold(per_n["claims"][c], s, res["g6"])
                    fold(summary["claims"][c], s, res["g6"])
            summary["per_n"][str(n)] = per_n
            summary["totals"]["connected"] += per_n["connected"]
            summary["totals"]["cyclic"] += per_n["cyclic"]
            summary["totals"]["acyclic"] += per_n["acyclic"]
            print(f"n={n}: connected={per_n['connected']} "
                  f"cyclic={per_n['cyclic']} "
                  + " ".join(f"{c}:viol={per_n['claims'][c]['violations']}"
                             f"/min={per_n['claims'][c]['min_slack']}"
                             for c in CLAIMS),
                  flush=True)
    finally:
        pool.close()
        pool.join()
    summary["elapsed_sec"] = round(time.time() - t0, 1)
    encoded = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    sha = hashlib.sha256(encoded).hexdigest().upper()
    (OUT.with_suffix(".json.sha256")).write_text(sha + "  " + OUT.name + "\n")
    print("wrote", OUT)
    print("sha256:", sha)
    for c in CLAIMS:
        sec = summary["claims"][c]
        print(f"{c}: checked={sec['checked']} viol={sec['violations']} "
              f"min_slack={sec['min_slack']} at {sec['min_slack_graph6']}")
    print("cycle_cap_ever_hit:", summary["cycle_cap_ever_hit"])


if __name__ == "__main__":
    main()
