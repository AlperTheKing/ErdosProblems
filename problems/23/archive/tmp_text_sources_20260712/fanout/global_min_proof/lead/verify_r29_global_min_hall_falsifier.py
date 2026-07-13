"""Cross-check independent R29 global-minimum and owner-Hall certificates."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
D09 = ROOT / "tmp/fanout/r29_gate/d09/retry2"
D05 = ROOT / "tmp/fanout/r29_gate/d05/retry2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_lead():
    spec = importlib.util.spec_from_file_location("r29_lead", LEAD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_hall_certificate(cert):
    sources = cert["sources"]
    keys = [(s["x"], s["y"], s["half"]) for s in sources]
    assert len(keys) == len(set(keys))
    hist = Counter(s["owner_mask"] for s in sources)
    demand = {int(o): rec["demand"] for o, rec in cert["owners"].items()}
    for cut in cert["cuts"]:
        mask = cut["shore_mask"]
        d = sum(demand[o] for o in range(3) if mask & (1 << o))
        reach = sum(value for owner_mask, value in hist.items() if owner_mask & mask)
        assert [d, reach, d - reach] == [
            cut["demand"], cut["neighborhood"], cut["gap"]
        ]
    witness = cert["maximum_deficiency_cut"]
    assert witness == max(cert["cuts"], key=lambda z: (z["gap"], -z["shore_mask"]))
    assert [witness["demand"], witness["neighborhood"], witness["gap"]] == [
        19953, 19925, 28
    ]
    return witness


def main():
    module = load_lead()
    data = module.build()
    best = json.loads((D09 / "best_tuple.json").read_text())
    global_cert = json.loads((D09 / "certificate.json").read_text())
    hall_cert = json.loads((D05 / "cut_certificate.json").read_text())

    choices = best["selector_choices"]
    assert len(choices) == 676
    assert all(55 in choice["row"] for choice in choices)
    assert [tuple(choice["row"]) for choice in choices] == [
        tuple(meta["anchorRow"]) for meta in data["selectorMeta"]
    ]
    rows = list(data["rows"])
    for i, choice in enumerate(choices):
        rows[data["selectorStart"] + i] = tuple(choice["row"])
    state = module.scoped_state(data, tuple(rows))
    assert state["score"] == best["score"] == 23115
    assert global_cert["exact_state"]["score"] == 23115
    assert global_cert["lower_bound"]["minimum"] == 23115
    assert global_cert["lower_bound"]["unique_argmin_local_counts"] == [0, 0]
    assert hall_cert["active_scope"]["active_vertices"] == len(
        global_cert["exact_state"]["active_vertices"]
    )
    witness = verify_hall_certificate(hall_cert)

    # PHT at this tuple would require mean <= score-defect, while global
    # minimality forces mean >= score.  The exact contradiction is K*28 > 0.
    payload = {
        "status": "FALSIFIER",
        "globalScopedScore": 23115,
        "hallDemand": witness["demand"],
        "hallNeighborhood": witness["neighborhood"],
        "hallDefect": witness["gap"],
        "shore": witness["shore"],
        "omegaCardinality": "680^676",
        "phtUpperPerTuple": 23115 - 28,
        "phtLowerPerTupleFromGlobalMinimum": 23115,
        "phtContradictionNumerator": "28*680^676",
        "hashes": {
            "lead": sha(LEAD),
            "bestTuple": sha(D09 / "best_tuple.json"),
            "globalCertificate": sha(D09 / "certificate.json"),
            "hallCertificate": sha(D05 / "cut_certificate.json"),
        },
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
