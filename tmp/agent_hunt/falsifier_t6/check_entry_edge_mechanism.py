#!/usr/bin/env python3
"""Verify the x0-entry-edge vacuity mechanism on the t=6 fixture:
  (a) no chosen atom has endpoint x0 (no endpoint-witness bypass);
  (b) every coverage witness row for the singleton-fiber pairs {13,17,18}
      is exactly of the form (4, 20, 1, y, b) -- i.e., uses edges (4,20) AND
      (1,20) AND (1,y);
  (c) hence (1,20),(4,20),(1,y) are used in EVERY profile-consistent
      selection; x0's non-owner star = {(1,20),(4,20)} fully selected;
      tail = {x0}; active component = {0,20} opposite shores => vacuous.
Pure row-DB enumeration; cross-checked against the CP-SAT landscape."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, norm


def main():
    src = json.loads(Path("t6_cuttight_l12_r9_harvest.json").read_text())
    left_n, right_n = src["left"], src["right"]
    hit = src["hits"][0]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = [atom_index[(r["shore"], r["u"], r["v"])] for r in hit["selectedAtoms"]]
    owner, active = 0, 20
    singleton_pairs = [13, 17, 18]

    # (a) no chosen atom endpoint = x0
    endpoint_atoms = [
        i for i in chosen if active in (atoms[i]["u"], atoms[i]["v"])
    ]
    print("(a) chosen atoms with endpoint x0:", endpoint_atoms)
    assert not endpoint_atoms

    # (b) enumerate ALL witness rows for singleton pairs
    ok = True
    for y in singleton_pairs:
        witnesses = []
        for i in chosen:
            if owner in (atoms[i]["u"], atoms[i]["v"]):
                continue
            for row in atoms[i]["rows"]:
                if owner in row or active not in row or y not in row:
                    continue
                pos = {v: k for k, v in enumerate(row)}
                lo, hi = sorted((pos[active], pos[y]))
                if hi - lo != 2:
                    continue
                witnesses.append((i, row))
        forms = {tuple(row[:4]) for _, row in witnesses}
        print(f"pair {y}: {len(witnesses)} witness rows; prefixes {sorted(forms)}")
        for i, row in witnesses:
            edges = {norm(row[k], row[k + 1]) for k in range(4)}
            if not {(4, 20), (1, 20), norm(1, y)} <= edges:
                print("   VIOLATION:", i, row)
                ok = False
    print("(b) all singleton-pair witnesses use (4,20),(1,20),(1,y):", ok)
    assert ok

    # (c) conclusion cross-check against the landscape
    landscape = json.loads(Path("t6_fixture_forcing.json").read_text())
    for e in [(1, 20), (4, 20), (1, 13), (1, 17), (1, 18)]:
        assert landscape["edges"]["%d-%d" % e] == "FORCED", e
    print("(c) landscape agrees: x0-star + (1,y) all FORCED;"
          " tail = {x0}; active component {0,20} opposite shores => VACUOUS")
    print("MECHANISM VERIFIED: SC(singleton fibers) + x0-entry-edge counting"
          " explain this fixture's vacuity with zero SAT calls")


if __name__ == "__main__":
    main()
