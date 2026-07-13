"""Exact finite check of the R37 saturation-only obstruction.

The models use one physical base with exactly two half keys.  Assignments are
injective and obey the production BaseKeyComponentCoherent rule exactly.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def coherent(assign, components):
    by_base = {}
    for obligation, key in assign.items():
        base, _half = key
        label = components[obligation]
        old = by_base.setdefault(base, label)
        if old != label:
            return False
    return True


def enumerate_model(name, components):
    obligations = tuple(components)
    keys = (("b", 0), ("b", 1))
    relation = {obligation: keys for obligation in obligations}
    assignments = []
    for size in range(len(obligations) + 1):
        for matched in itertools.combinations(obligations, size):
            for chosen_keys in itertools.permutations(keys, size):
                assign = dict(zip(matched, chosen_keys))
                if all(assign[d] in relation[d] for d in matched) and coherent(
                    assign, components
                ):
                    assignments.append(assign)
    maximum = max(map(len, assignments))
    maximizers = [a for a in assignments if len(a) == maximum]
    witness = min(
        maximizers,
        key=lambda a: tuple(sorted((d, key[1]) for d, key in a.items())),
    )
    used = set(witness.values())
    labels = {components[d] for d in witness}
    return {
        "name": name,
        "obligations": list(obligations),
        "components": components,
        "physicalBases": ["b"],
        "halfKeys": [["b", 0], ["b", 1]],
        "relation": {d: [["b", 0], ["b", 1]] for d in obligations},
        "coherentAssignments": len(assignments),
        "maximumMatched": maximum,
        "defect": len(obligations) - maximum,
        "optimalAssignment": {
            d: [key[0], key[1]] for d, key in sorted(witness.items())
        },
        "allHalfKeysSaturated": used == set(keys),
        "usedBaseLabels": sorted(labels),
        "baseCoherent": coherent(witness, components),
        "totalCoherentAssignmentExists": maximum == len(obligations),
        "neutralStateGraph": {"states": ["omega"], "edges": [["omega", "omega"]]},
        "sinkScc": ["omega"],
    }


def main():
    models = [
        enumerate_model("single_component", {"x1": "A", "x2": "A", "x3": "A"}),
        enumerate_model("component_conflict", {"x1": "A", "x2": "A", "y": "B"}),
    ]
    for model in models:
        assert model["maximumMatched"] == 2
        assert model["defect"] == 1
        assert model["allHalfKeysSaturated"]
        assert model["baseCoherent"]
        assert not model["totalCoherentAssignmentExists"]
    payload = {
        "schema": "R37_SATURATION_OBSTRUCTION_V1",
        "arithmetic": "finite exhaustive enumeration",
        "models": models,
        "verdict": "SATURATION_ALONE_DOES_NOT_FORCE_AUGMENTATION",
        "scope": "abstract matching/coherence/local-probe surface; not a real-graph counterexample",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    payload["canonicalPayloadSha256"] = hashlib.sha256(canonical).hexdigest()
    output = HERE / "result.json"
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "output": str(output),
        "verdict": payload["verdict"],
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
