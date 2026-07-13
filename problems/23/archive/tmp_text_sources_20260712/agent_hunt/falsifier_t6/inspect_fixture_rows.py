#!/usr/bin/env python3
"""Full row-DB inspection of the forcing of (4,20) on the t=6 fixture:
which chosen atoms hold edge (4,20) in some/every OWNER-FREE row, and what
the singleton-pair witnesses and endpoint-x0 atoms look like."""

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
    incident = {i for i in chosen if owner in (atoms[i]["u"], atoms[i]["v"])}

    print("x0 neighbours:", sorted(graph[active]))
    print("chosen atoms with endpoint 20:")
    for i in chosen:
        if active not in (atoms[i]["u"], atoms[i]["v"]):
            continue
        print(f" atom {i} = ({atoms[i]['u']},{atoms[i]['v']}) rows:")
        for row in atoms[i]["rows"]:
            has_owner = owner in row
            print(f"   {row} {'OWNER' if has_owner else 'owner-free'}")

    # which nonincident chosen atoms have ALL owner-free rows using (4,20)?
    e = (4, 20)
    print(f"\nnonincident chosen atoms whose EVERY owner-free row uses {e}:")
    for i in chosen:
        if i in incident:
            continue
        free = [row for row in atoms[i]["rows"] if owner not in row]
        if not free:
            print(f" atom {i} ({atoms[i]['u']},{atoms[i]['v']}): NO owner-free rows at all!")
            continue
        if all(e in {norm(r[k], r[k + 1]) for k in range(4)} for r in free):
            print(f" atom {i} ({atoms[i]['u']},{atoms[i]['v']}): all {len(free)} owner-free rows use {e}")

    # singleton-pair witness forms
    for y in (13, 17, 18):
        print(f"\npair (20,{y}) owner-free witness rows (gap-2):")
        for i in chosen:
            if i in incident:
                continue
            for row in atoms[i]["rows"]:
                if owner in row or active not in row or y not in row:
                    continue
                pos = {v: k for k, v in enumerate(row)}
                lo, hi = sorted((pos[active], pos[y]))
                if hi - lo != 2:
                    continue
                print(f"  atom {i} ({atoms[i]['u']},{atoms[i]['v']}): {row}")


if __name__ == "__main__":
    main()
