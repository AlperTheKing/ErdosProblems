#!/usr/bin/env python3
"""Exact integer replay of the R50/R51 t=6 arithmetic used by this hunt."""
from fractions import Fraction
import json
import sys

t = 6
out = {}
out["N"] = 5 * t                                   # 30
out["atoms_M"] = t * t                             # 36
out["supportEdges_Fstar"] = t * t - 1              # 35
# R50 selected-support mechanism: (t-1) star + (t-1) first-middle + t terminal
# pairwise-distinct + >=1 coverage edge at x0, all distinct.
out["selectedSupport_lower"] = (t - 1) + (t - 1) + t + 1   # 17
assert out["selectedSupport_lower"] == 3 * t - 1
out["latentBudget"] = out["supportEdges_Fstar"] - out["selectedSupport_lower"]
assert out["latentBudget"] == t * (t - 3) == 18
# R47/R51 raw ambient capacity coefficient ~ 21 t^2 / 4 vs switch demand <= t^2.
out["rawAmbientCapacity_21t2_4"] = str(Fraction(21 * t * t, 4))  # 189
out["rawCapacity_5_28t2"] = str(Fraction(528, 100) * t * t)      # 190.08
out["switchDemand_max"] = t * t                                   # 36
out["capacity_over_demand"] = str(Fraction(21 * t * t, 4) / (t * t))  # 21/4
# Mantel-live shore condition for 36 bad edges: floor(l^2/4)+floor(r^2/4) >= 36.
mantel = {}
for l in range(6, 24):
    for r in range(6, 24):
        if 17 <= l + r <= 30:
            mantel[f"{l}+{r}"] = (l * l) // 4 + (r * r) // 4 >= 36
out["order17_mantel_live"] = sorted(
    k for k, v in mantel.items() if v and sum(map(int, k.split("+"))) == 17
)
# My grid result (CP-SAT proofs) tightens the window: first support-feasible
# order is 20; orders 17-19 all INFEASIBLE in the rooted two-owner form.
out["gridWindow"] = "20 <= |V_support| <= 30 (rooted two-owner, exact-d4)"
json.dump(out, open(sys.argv[1], "w"), indent=2, sort_keys=True)
print(json.dumps(out, indent=2, sort_keys=True))
