#!/usr/bin/env python3
"""CP-SAT cross-checks on the falsifier + regenerate the engine-format package
from scratch (my own rows) and compare with fiberhunter's package sha."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from v5_core import available_atoms, build_adj, canonical_sha, norm  # noqa: E402
from v5_cpsat import gate_capture, gate_edge_unused  # noqa: E402
from v5_check_falsifier import CHOSEN, EDGES, GRAPH6, LEFT, N, OWNER, ACTIVE  # noqa: E402

adj = build_adj(N, EDGES)
atoms_all = available_atoms(N, EDGES, LEFT)
atom_by_pair = {(a["u"], a["v"]): a for a in atoms_all}
chosen_atoms = [atom_by_pair[p] for p in CHOSEN]

# 1. my CP-SAT capture gate
status, selection = gate_capture(chosen_atoms, adj, OWNER, ACTIVE, N)
print("my-cpsat capture status:", status)
assert status in ("OPTIMAL", "FEASIBLE"), "expected SAT on falsifier"

# 2. per-edge cross-check against the factored map
from v5_core import per_edge_latent_feasible  # noqa: E402

feas = per_edge_latent_feasible(chosen_atoms, adj, OWNER, ACTIVE)
mismatch = []
for e in sorted(feas):
    s = gate_edge_unused(chosen_atoms, adj, OWNER, ACTIVE, N, e)
    sat = s in ("OPTIMAL", "FEASIBLE")
    if sat != feas[e]:
        mismatch.append((e, s, feas[e]))
print("per-edge factored-vs-cpsat mismatches:", mismatch)
assert not mismatch

# 3. regenerate engine-format package from scratch
sel_atoms = []
for a in chosen_atoms:
    sel_atoms.append(
        {
            "footprintEdges": [list(e) for e in a["footprint"]],
            "rows": [list(r) for r in a["rows"]],
            "shore": a["shore"],
            "u": a["u"],
            "v": a["v"],
        }
    )
package = {
    "hit": {
        "atomCountAvailable": len(atoms_all),
        "graph6": GRAPH6,
        "selectedAtoms": sel_atoms,
        "selectionMeta": {
            "localClassifiers": {"0": {"activeNeighbour": ACTIVE}}
        },
        "supportEdges": [list(e) for e in EDGES],
    },
    "left": LEFT,
    "right": N - LEFT,
    "schema": "v5-independent-falsifier-package-v1",
}
package["canonicalSha256"] = canonical_sha(package)
out = Path(__file__).with_name("v5_falsifier_package.json")
out.write_text(json.dumps(package, indent=1, sort_keys=True), encoding="utf-8")
print("my package sha:", package["canonicalSha256"])

# 4. compare content with fiberhunter's engine package (rows completeness audit)
fh = json.loads(
    Path(
        r"E:\Projects\ErdosProblems\tmp\agent_hunt\fiberhunter\fh_falsifier_engine_format.json"
    ).read_text(encoding="utf-8")
)
fh_sha_claimed = fh.get("canonicalSha256")
fh_copy = dict(fh)
fh_copy.pop("canonicalSha256", None)
print("fh package sha recomputed:", canonical_sha(fh_copy), "claimed:", fh_sha_claimed)
same_edges = sorted(map(tuple, fh["hit"]["supportEdges"])) == EDGES
fh_atoms = {
    (a["u"], a["v"]): sorted(map(tuple, a["rows"])) for a in fh["hit"]["selectedAtoms"]
}
my_atoms = {(a["u"], a["v"]): sorted(map(tuple, a["rows"])) for a in chosen_atoms}
rows_equal = fh_atoms == my_atoms
print("fh package edges match:", same_edges, "| complete row DBs match:", rows_equal)
print(
    "fh activeNeighbour:",
    fh["hit"]["selectionMeta"]["localClassifiers"]["0"]["activeNeighbour"],
)
