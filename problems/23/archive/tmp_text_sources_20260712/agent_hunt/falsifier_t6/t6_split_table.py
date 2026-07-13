#!/usr/bin/env python3
"""The t=6 rooted-kernel split table.

Hand bounds (proof sketches in comments, machine-checked against the grid):
  left >= t+4:  v's t d4-partners lie in left \ {v,m,a,b}  (m,a at blue
                distance 2 via x; b at blue distance 2 via y; distances are
                exact-4 for partners) -> left >= 4 + t.
  right >= t+1: every v-partner's blue neighbourhood avoids N_B(v) (else
                distance 2), is nonempty (connectivity) -> right > t.
Machine bound (CP-SAT INFEASIBLE per cell, t6_support_grid.json):
  left + right >= 20.
Table = all (l, r) with l >= 10, r >= 7, 20 <= l+r <= 30.
"""
import json
import sys

t = 6
grid = json.load(open(sys.argv[1]))  # t6_support_grid.json

# Consistency: every probed INFEASIBLE cell must violate one of the hand
# bounds or have order <= 19; every probed feasible cell must satisfy all.
violations = []
for key, rec in grid.items():
    l, r = map(int, key.split("+"))
    feasible = rec["status"] == "OPTIMAL"
    hand_ok = l >= t + 4 and r >= t + 1
    if feasible and (not hand_ok or l + r < 20):
        violations.append((key, "feasible cell outside claimed window"))
    if not feasible and hand_ok and l + r >= 20:
        violations.append((key, "infeasible cell inside claimed window"))
print("violations:", violations)
assert not violations

table = [
    (l, r)
    for n in range(20, 31)
    for l in range(10, n - 6)
    if (r := n - l) >= 7
]
by_order = {}
for l, r in table:
    by_order.setdefault(l + r, []).append(f"{l}+{r}")
out = {
    "handBounds": {"leftMin": t + 4, "rightMin": t + 1},
    "machineOrderMin": 20,
    "orderMax": 30,
    "cellCount": len(table),
    "cellsByOrder": {str(k): v for k, v in sorted(by_order.items())},
}
print(json.dumps(out, indent=2, sort_keys=True))
json.dump(out, open(sys.argv[2], "w"), indent=2, sort_keys=True)
