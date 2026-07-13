"""Independent integer verifier for the Pattern-5 fixture gate artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def verify_relation(record: dict) -> dict:
    owners = record["owners"]
    owner_index = {owner: i for i, owner in enumerate(owners)}
    demand = {int(k): v for k, v in record["demand_by_owner"].items()}
    hist = {int(k): v for k, v in record["source_owner_masks"].items()}
    expected_count = (1 << len(owners)) - 1
    shore_path = ROOT / record["shore_file"] if record["shore_file"] else None
    if expected_count == 0:
        assert shore_path is None
        assert record["total_demand"] == record["max_flow"] == 0
        assert record["full"]
        return {"shores": 0, "minimum_slack": None, "sha256": None}

    assert shore_path is not None and shore_path.is_file()
    digest = hashlib.sha256()
    rows = 0
    minimum = None
    zero = []
    negative = []
    seen = set()
    with shore_path.open("r", encoding="ascii") as handle:
        for line in handle:
            row = json.loads(line)
            canonical = json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            digest.update(canonical.encode())
            mask = row["mask"]
            assert 0 < mask <= expected_count and mask not in seen
            seen.add(mask)
            expected_owners = [
                owner for owner in owners if mask & (1 << owner_index[owner])
            ]
            expected_demand = sum(demand[owner] for owner in expected_owners)
            expected_reach = sum(count for source_mask, count in hist.items()
                                 if source_mask & mask)
            expected_slack = expected_reach - expected_demand
            assert row == {
                "mask": mask,
                "owners": expected_owners,
                "demand": expected_demand,
                "reach": expected_reach,
                "slack": expected_slack,
            }
            minimum = expected_slack if minimum is None else min(minimum, expected_slack)
            if expected_slack == 0:
                zero.append(mask)
            if expected_slack < 0:
                negative.append(mask)
            rows += 1
    assert rows == expected_count and seen == set(range(1, expected_count + 1))
    assert minimum == record["minimum_shore_slack"]
    assert zero == record["zero_slack_masks"]
    assert negative == record["negative_shore_masks"]
    assert digest.hexdigest() == record["shore_table_sha256"]
    maximum_deficiency = max(0, -minimum)
    assert record["max_flow"] == record["total_demand"] - maximum_deficiency
    assert record["full"] == (maximum_deficiency == 0)
    return {"shores": rows, "minimum_slack": minimum,
            "sha256": digest.hexdigest()}


def main() -> None:
    result_path = HERE / "result.json"
    payload = json.loads(result_path.read_text(encoding="ascii"))
    assert payload["schema"] == "p5-fixture-regate-v1"
    assert payload["integer_only"] and payload["workers"] == 1
    assert not payload["native_decide"] and not payload["sorry"]
    gate_path = HERE / "gate.py"
    assert hashlib.sha256(gate_path.read_bytes()).hexdigest() == payload["gate_sha256"]

    expected = [
        ("2943", "active"), ("24", "active"), ("24", "legacy_all"),
        ("167", "active"), ("175", "active"), ("311", "active"),
        ("3892", "active"), ("89", "active"), ("89", "legacy_all"),
    ]
    assert [(x["fixture"], x["scope"]) for x in payload["fixtures"]] == expected
    verified = []
    for fixture in payload["fixtures"]:
        relation_results = {}
        for key in ("old_relation", "semantic_p5_relation", "checked_certificate"):
            relation_results[key] = verify_relation(fixture[key])
        assert fixture["checked_certificate"]["full"]
        verified.append({
            "fixture": fixture["fixture"],
            "scope": fixture["scope"],
            "relations": relation_results,
        })

    r2943 = payload["fixtures"][0]
    special = r2943["special_2943"]
    assert r2943["owners"][:3] == [0, 1, 2]
    assert r2943["old_relation"]["negative_shore_masks"] == [7]
    assert r2943["checked_certificate"]["zero_slack_masks"] == [7]
    assert special["hub_shores"]["old"] == {
        "mask": 7, "owners": [0, 1, 2], "demand": 19953,
        "reach": 19925, "slack": -28,
    }
    assert special["hub_shores"]["certificate"] == {
        "mask": 7, "owners": [0, 1, 2], "demand": 19953,
        "reach": 19953, "slack": 0,
    }
    keys = special["selected_keys"]
    expected_keys = [[3, x, half] for x in range(56, 84, 2) for half in (0, 1)]
    assert keys == expected_keys and len({tuple(key) for key in keys}) == 28
    assert special["globally_new_selected_key_count"] == 28
    assert special["selected_key_global_old_owners"] == {}
    assert special["all_selected_keys_unreserved"]
    assert (special["component_size"], special["boundary"], special["loss"]) == (
        1379, [1, 55], 26
    )
    assert r2943["checked_certificate"]["distinct_reachable_sources"] == (
        r2943["old_relation"]["distinct_reachable_sources"] + 28
    )

    verification = {
        "schema": "p5-fixture-regate-verification-v1",
        "integer_only": True,
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        "gate_sha256": payload["gate_sha256"],
        "verified": verified,
        "2943": {
            "active_owners": len(r2943["owners"]),
            "owner_shores": r2943["checked_certificate"]["owner_shores_checked"],
            "old_hub_defect": 28,
            "selected_p5_keys": 28,
            "certificate_hub_slack": 0,
        },
    }
    output = HERE / "verification.json"
    output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n",
                      encoding="ascii")
    print(json.dumps(verification["2943"], sort_keys=True, separators=(",", ":")))
    print(f"verified fixtures={len(verified)} result_sha256={verification['result_sha256']}")


if __name__ == "__main__":
    main()
