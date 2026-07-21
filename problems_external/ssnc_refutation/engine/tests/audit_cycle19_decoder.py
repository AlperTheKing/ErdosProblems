#!/usr/bin/env python3
"""Non-production audit probes for decode_cycle19_model.py."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ENGINE = Path(__file__).resolve().parent.parent
DECODER_PATH = ENGINE / "decode_cycle19_model.py"
MANIFEST_PATH = ENGINE / "instances" / "cycle19-fixed-v1" / "manifest.json"


def load_decoder():
    spec = importlib.util.spec_from_file_location("cycle19_decoder_under_audit", DECODER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    decoder = load_decoder()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    captured = decoder.parse_solution(
        ENGINE / "logs" / "audit-final-sat-v1" / "solution.txt"
    )
    assert captured == {1: True, 2: True}
    assert captured[1] and captured[2]  # satisfies (1) and (2) in tiny_sat.cnf

    signed = decoder.parse_solution(Path(__file__).with_name("audit_solution_negative.txt"))
    assert signed == {1: True, 2: False}
    try:
        decoder.parse_solution(Path(__file__).with_name("audit_solution_conflict.txt"))
    except ValueError as exc:
        conflict_rejection = str(exc)
    else:
        raise AssertionError("conflicting assignments were accepted")

    assert manifest["edge_variable_semantics"] == (
        "edge(a,b), a<b, is true iff the arc is a->b; false iff b->a"
    )
    edge_variables: dict[int, tuple[int, int]] = {}
    for identifier, name in manifest["variable_map"].items():
        match = decoder.EDGE_NAME.fullmatch(name)
        if match is not None:
            edge_variables[int(identifier)] = tuple(map(int, match.groups()))
    missing = {tuple(edge) for edge in manifest["missing_edges"]}
    complete_pairs = {(a, b) for a in range(19) for b in range(a + 1, 19)}
    assert len(edge_variables) == 152
    assert set(edge_variables.values()) == complete_pairs - missing

    # A deterministic regular orientation checks both signs, support, and degree handling.
    # It is intentionally only a decoder probe, not a solve of the production CNF.
    assignment = {
        variable: ((b - a) % 19) in range(2, 10)
        for variable, (a, b) in edge_variables.items()
    }
    assert any(assignment.values()) and not all(assignment.values())
    assert assignment[1] is True  # manifest variable 1 is edge(0,2), hence 0->2
    try:
        certificate = decoder.decode(manifest, assignment)
    except ValueError as exc:
        regular_probe = {"accepted": False, "rejection": str(exc)}
    else:
        assert set(certificate) == {"n", "out_neighbors"}
        regular_probe = {"accepted": True, "certificate": certificate}

    print(
        json.dumps(
            {
                "status": "PASS",
                "captured_assignment": captured,
                "negative_assignment": signed,
                "conflict_rejection": conflict_rejection,
                "manifest_orientation_variables": len(edge_variables),
                "manifest_support_matches": True,
                "sign_convention_matches": True,
                "verifier_schema_keys": ["n", "out_neighbors"],
                "regular_orientation_probe": regular_probe,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
