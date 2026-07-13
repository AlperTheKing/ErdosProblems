"""Exact replay verifier for the R29 extended owner-source injection."""

from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r29_referee_gate", HERE / "r29_referee_gate.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def main() -> None:
    cage = MOD.construct()
    rows = cage.rigid_rows[:676] + cage.selector_anchor + cage.rigid_rows[676:]
    state = MOD.scoped(cage, rows)
    counts = state["counts"]
    aB = MOD.adj(cage.n, cage.blue)
    aM = MOD.adj(cage.n, cage.bad)
    cert_path = HERE / "r29_extended_owner_matching.json"
    raw = cert_path.read_bytes().rstrip(b"\n")
    cert = json.loads(raw)
    assert cert["schema"] == "r29-owner-source-injection-v1"
    assert cert["allAnchor"] is True
    used = set()
    by_owner = Counter()
    by_relation = Counter()

    def surplus(x: int, y: int) -> int:
        dB = len(aB[x]) + len(aB[y]) - (2 if y in aB[x] else 0)
        dM = len(aM[x]) + len(aM[y]) - (2 if y in aM[x] else 0)
        return dB - dM

    for owner, index, x, y, half, relation in cert["assignments"]:
        assert index == by_owner[owner]
        assert half in (0, 1)
        key = (x, y, half)
        assert key not in used
        used.add(key)
        assert x != y and counts[x, y] == 0
        assert not (half == 0 and MOD.E(x, y) in state["active_edges"] and
                    x in state["active_vertices"])
        if relation == "sameFirst":
            assert x == owner
        elif relation == "rowCompanion":
            assert counts[owner, x] > 0 and counts[owner, y] > 0
            assert surplus(x, y) >= 0
        elif relation == "checkedC5Base":
            assert x in aB[owner] and y in aB[owner]
            assert surplus(x, y) >= 2
        else:
            raise AssertionError(relation)
        by_owner[owner] += 1
        by_relation[relation] += 1

    demand = {v: state["collision"].get(v, 0) + state["hitneed"].get(v, 0)
              for v in state["active_vertices"]}
    demand = {v: n for v, n in demand.items() if n}
    assert dict(by_owner) == demand
    assert len(used) == sum(demand.values()) == 23115
    out = {
        "status": "PASS",
        "assignments": len(used),
        "relations": dict(sorted(by_relation.items())),
        "certificateSHA256": hashlib.sha256(raw).hexdigest(),
    }
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

