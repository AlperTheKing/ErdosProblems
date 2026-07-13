"""Replay the exact R35 real-24 collision trade certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import evaluate_trade as model


HERE = Path(__file__).resolve().parent


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"


def verify_state(name, claimed):
    replay = model.evaluate(tuple(claimed["state"]), certificate=True)
    assert replay == claimed, name
    assignments = claimed["assignments"]
    obligations = [tuple(item["obligation"]) for item in assignments]
    sources = [tuple(item["source"]) for item in assignments]
    assert len(obligations) == len(set(obligations)) == claimed["matched"]
    assert len(sources) == len(set(sources)) == claimed["matched"]
    base_components = {}
    for item in assignments:
        obligation = item["obligation"]
        source = item["source"]
        base = tuple(source[:2])
        component = obligation[-1]
        if base in base_components:
            assert base_components[base] == component
        base_components[base] = component
    cut = claimed["mincut"]
    assert cut["shore_reach"] == len(cut["hall_neighborhood"])
    assert cut["capacity"] == claimed["demand"] - cut["shore_demand"] + cut["shore_reach"]
    assert cut["capacity"] == claimed["matched"]
    assert claimed["defect"] == claimed["demand"] - claimed["matched"]


def main():
    path = HERE / "certificate.json"
    raw = path.read_bytes().decode("ascii")
    cert = json.loads(raw)
    assert raw == canonical(cert)
    assert cert["schema"] == "r35-real24-no-common-blue-collision-trade-v1"
    assert cert["displayed_state"] == list(model.DISPLAYED)
    assert cert["row_family_sizes"] == list(model.RADICES)
    verify_state("old", cert["old"])
    verify_state("new", cert["new"])
    old, new, trade = cert["old"], cert["new"], cert["trade"]
    assert old["defect"] == 68
    assert old["mincut"]["shore_owners"] == [7, 8]
    assert old["mincut"]["shore_demand"] == 144
    assert old["mincut"]["shore_reach"] == 76
    assert new["defect"] == 0 and new["matched"] == new["demand"] == 250
    assert trade["changed_atoms"] == [9]
    assert trade["defect_improves"] and trade["defect_nonincreasing"]
    assert trade["tuple_rank_decreases"] and trade["zero_defect_exists"]
    assert new["tuple_rank"] < old["tuple_rank"]
    digest = hashlib.sha256(raw.encode("ascii")).hexdigest()
    print("REPLAY=PASS")
    print(f"old=demand:{old['demand']} matched:{old['matched']} defect:{old['defect']}")
    print(f"old_min_cut=shore:{old['mincut']['shore_owners']} demand:{old['mincut']['shore_demand']} reach:{old['mincut']['shore_reach']}")
    print(f"new=demand:{new['demand']} matched:{new['matched']} defect:{new['defect']}")
    print(f"changed_atoms={trade['changed_atoms']} rank:{old['tuple_rank']}->{new['tuple_rank']}")
    print(f"certificate_sha256={digest}")


if __name__ == "__main__":
    main()
