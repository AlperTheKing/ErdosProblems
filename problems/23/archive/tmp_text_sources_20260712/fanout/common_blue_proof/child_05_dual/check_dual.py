#!/usr/bin/env python3
from fractions import Fraction
import json, sys
def q(x):
    if isinstance(x, int): return Fraction(x)
    if isinstance(x, str): return Fraction(x)
    raise TypeError(f"not an exact rational: {x!r}")
def check(data):
    demands, sources = data["demands"], data["sources"]
    owners = set(data["owner_shore"])
    A = {d for d, v in demands.items() if v in owners}
    N = {s for s, vs in sources.items() if owners.intersection(vs)}
    a = {d: Fraction(d not in A) for d in demands}
    b = {s: Fraction(s in N) for s in sources}
    for d, v in demands.items():
        for s, vs in sources.items():
            if v in vs:
                assert a[d] >= 0 and b[s] >= 0
                assert a[d] + b[s] >= 1, (d, s)
    objective = sum(a.values()) + sum(b.values())
    defect = len(A) - len(N)
    assert objective == len(demands) - defect
    assert defect == q(data["claimed_defect"])
    for arc, value in data.get("adjusted_surplus", {}).items():
        d, s = arc.split("|")
        assert demands[d] in sources[s]
        assert q(value) >= 0
    return {"owner_shore": sorted(owners), "demand_shore": sorted(A), "neighborhood": sorted(N), "defect": defect, "dual_objective": str(objective), "primal_target": len(demands), "strict_farkas": objective < len(demands)}
if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "abstract_countermodel.json"
    with open(path, encoding="utf-8") as f: result = check(json.load(f))
    print(json.dumps(result, sort_keys=True, indent=2))