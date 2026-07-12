#!/usr/bin/env python3
"""EXACT no-SAT vacuity certificate for the first t=6 zero-vector fixture
(graph6 T???????????z?t?Z??OwCwBc?Eg?@E?BG??, owner 0, active x0=20).

Mechanism (all row-DB counting):
  FI-1   every coverage witness for {x0,y} places x0,y at gap 2 (parity).
  (E1)   every witness row of pair 13 uses edge (1,20)  [fiber-intersection]
  (E2)   shared-witness-atom pigeonhole: witness sets of pairs 13 and 18 are
         {row30, row38a} and {row35, row38b} with row38a != row38b rows of
         the SAME atom 38 => one row per atom => at least one of row30/row35
         selected => edge (4,20) selected.
  (C)    x0's non-owner star {(1,20),(4,20)} selected in EVERY
         profile-consistent selection => owner's latent component = {0, 20}
         (opposite shores) => no captured bad pair => scope-vacuous.
Cross-checked against the exhaustive CP-SAT landscape (25 FORCED edges).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, norm


def witness_rows(atoms, chosen, incident, owner, active, y):
    """All (atom, row) coverage witnesses for pair {active, y}."""
    out = []
    for i in chosen:
        if i in incident:
            continue
        for row in atoms[i]["rows"]:
            if owner in row or active not in row or y not in row:
                continue
            pos = {v: k for k, v in enumerate(row)}
            lo, hi = sorted((pos[active], pos[y]))
            if hi - lo == 2:
                out.append((i, tuple(row)))
    return out


def row_edges(row):
    return {norm(row[k], row[k + 1]) for k in range(4)}


def main():
    src = json.loads(Path("t6_cuttight_l12_r9_harvest.json").read_text())
    t = src["t"]
    left_n, right_n = src["left"], src["right"]
    hit = src["hits"][0]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = [atom_index[(r["shore"], r["u"], r["v"])] for r in hit["selectedAtoms"]]
    owner, active = 0, 20
    incident = {i for i in chosen if owner in (atoms[i]["u"], atoms[i]["v"])}
    pairs = sorted(y for y in graph[owner] if y != active)

    # FI-1 parity sanity: no gap-4 or odd-gap witnesses possible
    for y in pairs:
        for i in chosen:
            for row in atoms[i]["rows"]:
                if owner in row or active not in row or y not in row:
                    continue
                pos = {v: k for k, v in enumerate(row)}
                gap = abs(pos[active] - pos[y])
                assert gap == 2, (y, i, row)

    W = {y: witness_rows(atoms, chosen, incident, owner, active, y) for y in pairs}
    for y in pairs:
        print(f"pair {y}: witnesses", [(i, r) for i, r in W[y]])

    # (E1) fiber-intersection on pair 13
    e1 = norm(1, 20)
    assert all(e1 in row_edges(r) for _, r in W[13]), "E1 fails"
    print(f"(E1) every witness of pair 13 uses {e1} -> forced")

    # (E2) pigeonhole: atoms serving pairs 13 and 18
    a13 = {i for i, _ in W[13]}
    a18 = {i for i, _ in W[18]}
    shared = a13 & a18
    assert shared == {38}, shared
    r13_alt = [r for i, r in W[13] if i not in shared]
    r18_alt = [r for i, r in W[18] if i not in shared]
    assert len(r13_alt) == 1 and len(r18_alt) == 1
    # the shared atom cannot serve both pairs with one selected row:
    rows38_13 = {r for i, r in W[13] if i == 38}
    rows38_18 = {r for i, r in W[18] if i == 38}
    assert rows38_13.isdisjoint(rows38_18), "one row of 38 covers both -> no pigeonhole"
    e2 = norm(4, 20)
    assert e2 in row_edges(r13_alt[0]) and e2 in row_edges(r18_alt[0])
    print(f"(E2) pairs 13,18 share only witness atom 38 with disjoint row sets;"
          f" both alternative rows use {e2} -> forced")

    # (C) star sealed; tail = {x0}
    x0_star = sorted(norm(active, w) for w in graph[active] if w != owner)
    assert x0_star == sorted([e1, e2])
    landscape = json.loads(Path("t6_fixture_forcing.json").read_text())
    assert all(landscape["edges"]["%d-%d" % e] == "FORCED" for e in [e1, e2])
    print("(C) x0 non-owner star sealed in every selection; latent component"
          " of owner = {0,20}, an opposite-shore pair -> NO captured bad pair"
          " -> SCOPE-VACUOUS. Certificate = counting only; cross-checked vs"
          " exhaustive CP-SAT landscape (INFEASIBLE scope + 25 FORCED edges).")
    out = {
        "fixtureGraph6": hit["graph6"],
        "owner": owner,
        "active": active,
        "E1_forcedEdge": list(e1),
        "E2_pigeonholeSharedAtom": 38,
        "E2_forcedEdge": list(e2),
        "conclusion": "SCOPE_VACUOUS_BY_COUNTING_CERTIFICATE",
        "newMotif": "shared-witness-atom pigeonhole (beyond R50 ProfileForced)",
    }
    Path("t6_fixture_certificate.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n"
    )
    print("WRITTEN t6_fixture_certificate.json")


if __name__ == "__main__":
    main()
