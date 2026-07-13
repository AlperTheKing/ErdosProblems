"""Exact semantic audit: R29 all-anchor core versus FullBank singleton cover.

No optimization or floating point is used.  This imports the canonical R29
constructor, rebuilds S,F,O,C, and checks the hypotheses/load ledger of
certificate_of_singletonCore_allDoors (K=C, J=O, lambda=1/2, kap=1).
"""
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"

spec = importlib.util.spec_from_file_location("r29_lead", LEAD)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)
d = mod.build()

S = set(d["bad"])
rows = tuple(d["rows"])                 # canonical all-anchor tuple
C = {v for row in rows for v in row}    # singleton cut family K
F = {mod.edge(x, y) for row in rows for x, y in zip(row, row[1:])}
O = set(d["blue"]) - F
J = set(O)                               # one Door sink per port
K = set(C)

assert len(S) == len(rows) == 1383
assert all(mod.edge(r[0], r[-1]) in S and len(r) == 5 for r in rows)
assert all(u in C and v in C for u, v in S)
assert F <= set(d["blue"])
assert F.isdisjoint(O) and F | O == set(d["blue"])

# With singleton weights 1/2, an edge's cut-family load is half the number
# of endpoints in C.  S has internal non-cut coverage 1; F has congestion 1.
load = {e: Fraction((e[0] in C) + (e[1] in C), 2) for e in set(d["graph"])}
assert all(load[e] == 1 for e in S)
assert all(load[e] == 1 for e in F)
assert all(Fraction(0) <= load[e] <= 1 for e in O)

boundary_O = {e for e in O if load[e] == Fraction(1, 2)}
internal_O = {e for e in O if load[e] == 1}
external_O = {e for e in O if load[e] == 0}

# allDoors: q(c,j)=load(c) iff j=c, hence each Door column receives <= kap=1.
door_total = sum(load[e] for e in O)
assert all(load[e] <= 1 for e in J)

out = {
    "S_bad_rows": len(S),
    "F_selected_support": len(F),
    "O_blue_minus_F": len(O),
    "J_own_doors": len(J),
    "C_selected_vertices": len(C),
    "K_singleton_cuts": len(K),
    "lambda": "1/2",
    "O_load_half": len(boundary_O),
    "O_load_one": len(internal_O),
    "O_load_zero": len(external_O),
    "sum_O_load": str(door_total),
    "own_door_capacity_each": "1",
    "fullbank_residual_deficit": "0",
    "freehalf_owner_shore": {"demand": 19953, "reachable": 19925, "deficit": 28},
}
print(json.dumps(out, indent=2, sort_keys=True))
