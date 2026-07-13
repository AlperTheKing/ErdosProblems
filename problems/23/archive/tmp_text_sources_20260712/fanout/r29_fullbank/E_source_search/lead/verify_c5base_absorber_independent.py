"""Independent literal-edge verifier for the 28-key R29 c5Base absorber."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BUILDER = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
OLD_CERT = ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json"
EXPECTED_OLD_CERT_SHA = "dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def boundary_count(edges: set[tuple[int, int]], shore: set[int]) -> int:
    return sum((u in shore) != (v in shore) for u, v in edges)


def main() -> None:
    assert sha(OLD_CERT.read_bytes()) == EXPECTED_OLD_CERT_SHA
    old = json.loads(OLD_CERT.read_text(encoding="utf-8"))
    assert old["maximum_deficiency_cut"] == {
        "demand": 19953,
        "gap": 28,
        "neighborhood": 19925,
        "shore": [0, 1, 2],
        "shore_mask": 7,
    }

    spec = importlib.util.spec_from_file_location("r29_builder_independent", BUILDER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    data = module.build()
    rows = list(data["rows"])
    for j, meta in enumerate(data["selectorMeta"]):
        rows[data["selectorStart"] + j] = tuple(meta["anchorRow"])

    old_masks = {
        (rec["x"], rec["y"], rec["half"]): rec["owner_mask"]
        for rec in old["sources"]
    }
    assert len(old_masks) == 19925
    absorber = [(x, 2930, h) for x in range(29, 43) for h in (0, 1)]
    source_ids = [2 * (data["n"] * x + y) + h for x, y, h in absorber]
    assert len(set(absorber)) == len(set(source_ids)) == 28

    terminal_records = []
    for x, y, h in absorber:
        assert (x, y, h) not in old_masks
        assert module.edge(x, 2) in data["blue"]
        assert module.edge(y, 2) in data["blue"]
        assert all(not (x in row and y in row) for row in rows)
        shore = {x, y}
        d_b = boundary_count(data["blue"], shore)
        d_m = boundary_count(data["bad"], shore)
        assert (d_b, d_m, d_b - d_m, d_b - d_m - 2) == (30, 27, 3, 1)
        assert module.edge(x, y) not in data["blue"]
        terminal_records.append({
            "source": [x, y, h],
            "sourceId": 2 * (data["n"] * x + y) + h,
            "dB": d_b,
            "dM": d_m,
            "adjustedSurplus": d_b - d_m - 2,
        })

    repaired = dict(old_masks)
    repaired.update({key: 4 for key in absorber})
    demands = {int(k): rec["demand"] for k, rec in old["owners"].items()}
    cuts = []
    for shore_mask in range(8):
        demand = sum(d for owner, d in demands.items() if shore_mask & (1 << owner))
        reach = sum(bool(mask & shore_mask) for mask in repaired.values())
        cuts.append({"shoreMask": shore_mask, "demand": demand,
                     "reach": reach, "margin": reach - demand})
    assert all(rec["margin"] >= 0 for rec in cuts)
    assert cuts[7] == {"shoreMask": 7, "demand": 19953,
                       "reach": 19953, "margin": 0}

    by_mask: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for key, mask in repaired.items():
        by_mask[mask].append(key)
    for keys in by_mask.values():
        keys.sort()
    assert {mask: len(keys) for mask, keys in by_mask.items()} == {
        1: 5775, 2: 5775, 4: 5803, 7: 2600
    }
    assignment = []
    assignment += [(key, 0) for key in by_mask[1]]
    assignment += [(key, 1) for key in by_mask[2]]
    assignment += [(key, 2) for key in by_mask[4]]
    assignment += [(key, 0) for key in by_mask[7][:876]]
    assignment += [(key, 1) for key in by_mask[7][876:1752]]
    assignment += [(key, 2) for key in by_mask[7][1752:]]
    assert len(assignment) == len({key for key, _ in assignment}) == 19953
    assert Counter(owner for _, owner in assignment) == Counter(demands)
    assert all(repaired[key] & (1 << owner) for key, owner in assignment)
    assignment_raw = json.dumps(
        [[*key, owner] for key, owner in assignment], separators=(",", ":")
    ).encode()
    assert sha(assignment_raw) == "43e50aee99b019df6804aa173ba5456f4de2e5ec08b540e13f08349f1398012a"

    result = {
        "oldCertificateSha256": EXPECTED_OLD_CERT_SHA,
        "absorberCount": len(absorber),
        "sourceIds": source_ids,
        "terminalRecords": terminal_records,
        "cuts": cuts,
        "assignmentSha256": sha(assignment_raw),
        "injective": True,
        "verdict": "PASS",
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    output = HERE / "independent_verification.json"
    output.write_bytes(raw)
    print(json.dumps({
        "verdict": "PASS",
        "absorberCount": 28,
        "fullShoreMargin": 0,
        "assignmentSha256": result["assignmentSha256"],
        "verificationSha256": sha(raw),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
