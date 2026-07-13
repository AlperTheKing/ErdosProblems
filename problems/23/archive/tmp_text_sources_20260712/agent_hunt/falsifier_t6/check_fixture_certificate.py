#!/usr/bin/env python3
"""Kernel-cheap vacuity certificate for the t=6 fixture (matching arithmetic,
no SAT):

  (i)  singleton-fiber pairs force edge (m*, x0) selected      [SC mechanism]
  (ii) restricted-middle Hall deficiency: the coverage matching needs t-1
       DISTINCT non-incident atoms; if the bipartite relation
         pairs -> atoms-with-witness-through-middle-1-only
       has max matching < t-1, some pair must route through the OTHER middle
       => edge (4, x0) selected                                 [NEW mechanism]
  (iii) then x0's whole non-owner star is selected in EVERY profile-consistent
       selection => owner's latent component = {owner, x0} (opposite shores)
       => no captured bad pair => scope-vacuous.

Cross-checks against the per-edge forcing landscape (t6_fixture_forcing.json)
and the engine's scope INFEASIBLE.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, matching_size, norm


def main():
    src = json.loads(Path("t6_cuttight_l12_r9_harvest.json").read_text())
    t = src["t"]
    left_n, right_n = src["left"], src["right"]
    hit = src["hits"][0]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = [atom_index[(r["shore"], r["u"], r["v"])] for r in hit["selectedAtoms"]]
    owner = 0
    active = hit["selectionMeta"]["localClassifiers"]["0"]["activeNeighbour"]
    neighbours = sorted(graph[owner])
    pairs = [y for y in neighbours if y != active]
    incident = {i for i in chosen if owner in (atoms[i]["u"], atoms[i]["v"])}
    nonincident = [i for i in chosen if i not in incident]

    # coverage witness middles per pair
    middles = {}          # y -> set of middles w (position-2 vertex between x0,y)
    witness_atoms = {}    # (y, middle) -> set of atoms
    for y in pairs:
        middles[y] = set()
        for i in nonincident:
            for row in atoms[i]["rows"]:
                if owner in row or active not in row or y not in row:
                    continue
                # x0,y at distance 2 in the row; middle = vertex between them
                pos = {v: k for k, v in enumerate(row)}
                lo, hi = sorted((pos[active], pos[y]))
                if hi - lo != 2:
                    continue
                w = row[lo + 1]
                middles[y].add(w)
                witness_atoms.setdefault((y, w), set()).add(i)

    print("pair middles:", {y: sorted(m) for y, m in middles.items()})
    fiber = {y: sorted(m) for y, m in middles.items()}
    singleton_pairs = [y for y in pairs if len(fiber[y]) == 1]
    m_star = fiber[singleton_pairs[0]][0] if singleton_pairs else None
    assert all(fiber[y] == [m_star] for y in singleton_pairs), "mixed singletons"
    other_middles = sorted({w for y in pairs for w in fiber[y] if w != m_star})
    print("singleton pairs:", singleton_pairs, "forced middle m* =", m_star)
    print("other middles:", other_middles)

    # (i) SC forcing of (m*, x0): every witness for singleton pairs uses
    # edge (x0, m*), so it is selected in every realization.
    edge_i = norm(active, m_star)
    print(f"(i) SC: edge {edge_i} forced by pairs {singleton_pairs}")

    # (ii) restricted-middle Hall: pairs -> atoms with a middle-m*-witness
    incidence = []
    for y in pairs:
        for i in witness_atoms.get((y, m_star), ()):
            incidence.append((y, i))
    rank = matching_size(pairs, sorted(set(i for _, i in incidence)), incidence)
    print(f"(ii) max matching pairs->middle-{m_star}-atoms = {rank} vs needed {t-1}")
    hall_deficient = rank < t - 1
    forced_second = None
    if hall_deficient:
        assert len(other_middles) == 1, "certificate needs a unique second middle"
        forced_second = norm(active, other_middles[0])
        print(f"     Hall-deficient => edge {forced_second} forced")

    # (iii) conclusion
    landscape = json.loads(Path("t6_fixture_forcing.json").read_text())
    x0_star = [norm(active, w) for w in graph[active] if w != owner]
    all_forced_in_landscape = all(
        landscape["edges"]["%d-%d" % e] == "FORCED" for e in x0_star
    )
    print("x0 non-owner star:", x0_star, "landscape FORCED:", all_forced_in_landscape)
    cert_covers = set(x0_star) == {edge_i} | ({forced_second} if forced_second else set())
    print("certificate covers the full x0-star:", cert_covers)
    verdict = {
        "singletonPairs": singleton_pairs,
        "forcedMiddle": m_star,
        "scForcedEdge": list(edge_i),
        "restrictedMiddleMatchingRank": rank,
        "needed": t - 1,
        "hallDeficient": hall_deficient,
        "hallForcedEdge": None if forced_second is None else list(forced_second),
        "x0Star": [list(e) for e in x0_star],
        "certificateCoversStar": bool(cert_covers),
        "crossCheckLandscapeForced": bool(all_forced_in_landscape),
        "conclusion": "SCOPE_VACUOUS_BY_MATCHING_CERTIFICATE"
        if cert_covers and all_forced_in_landscape
        else "CERTIFICATE_INCOMPLETE",
    }
    print(json.dumps(verdict, indent=1))
    Path("t6_fixture_certificate.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
