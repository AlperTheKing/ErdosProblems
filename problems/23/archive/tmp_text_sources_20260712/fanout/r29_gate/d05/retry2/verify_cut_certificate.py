"""Certificate-only integer verifier; does not import the lead or rebuilder."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = HERE / "cut_certificate.json"
C = json.loads(p.read_text(encoding="utf-8"))
sources = C["sources"]
keys = [(s["x"], s["y"], s["half"]) for s in sources]
assert len(keys) == len(set(keys))
assert all(s["x"] != s["y"] and s["half"] in (0, 1) and 1 <= s["owner_mask"] <= 7 for s in sources)
hist = Counter(s["owner_mask"] for s in sources)
assert {str(k): v for k, v in sorted(hist.items())} == C["source_histogram_by_owner_mask"]
demand_by_owner = {int(o): x["demand"] for o, x in C["owners"].items()}
for cut in C["cuts"]:
    m = cut["shore_mask"]
    demand = sum(demand_by_owner[o] for o in range(3) if m & (1 << o))
    reach = sum(v for mask, v in hist.items() if mask & m)
    assert (demand, reach, demand - reach) == (cut["demand"], cut["neighborhood"], cut["gap"])
w = C["maximum_deficiency_cut"]
assert w == max(C["cuts"], key=lambda z: (z["gap"], -z["shore_mask"]))
assert (w["demand"], w["neighborhood"], w["gap"]) == (19953, 19925, 28)
flow = C["flow_certificate_by_source_mask_to_owner"]
used_by_mask = Counter()
received = Counter()
for key, amount in flow.items():
    mask, owner = map(int, key.split("->"))
    assert mask & (1 << owner) and amount >= 0
    used_by_mask[mask] += amount; received[owner] += amount
assert all(used_by_mask[m] <= hist[m] for m in used_by_mask)
assert sum(received.values()) == 19925
assert all(received[o] <= demand_by_owner[o] for o in received)
print(json.dumps({"certificate_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                  "sources": len(sources), "verified_cuts": len(C["cuts"]),
                  "maximum_deficiency": w}, sort_keys=True))
