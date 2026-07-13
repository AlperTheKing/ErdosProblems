#!/usr/bin/env python3
"""Replay the wave-1 N24 singleton fixture under coherence-free P4."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CORE_PATH = HERE / "selector_core.py"
SOFT_DIR = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
SOFT_PATH = SOFT_DIR / "global_softcap.py"
OUTPUT = HERE / "n24_unscoped_p4_replay.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    core = load_module("codex_wave1_selector_core", CORE_PATH)
    soft = load_module("codex_wave1_global_softcap", SOFT_PATH)
    graph = core.n24_fixture()
    row_db = core.complete_row_database(graph)
    if not all(len(family) == 1 for _edge, family in row_db):
        raise AssertionError("fixture row database is not singleton")
    rows = tuple(family[0] for _edge, family in row_db)
    context = soft.make_graph_context(graph.n, graph.blue, graph.bad)
    summary, certificate = soft.analyze_global(
        context, rows, extract_certificate=True
    )
    if certificate is None:
        raise AssertionError("expected a complete assignment certificate")
    assignments = certificate["assignments"]
    sources = [tuple(record["source"]) for record in assignments]
    payload = {
        "schema": "R53_WAVE1_N24_UNSCOPED_P4_REPLAY_V1",
        "fixture": {
            "order": graph.n,
            "badEdges": len(graph.bad),
            "rowFamilies": len(row_db),
            "singletonRowDatabase": True,
        },
        "model": summary["model"],
        "evaluatedFamilies": summary["evaluatedFamilies"],
        "notEnumeratedFamilies": summary["notEnumeratedFamilies"],
        "globalDemand": summary["state"]["globalCollisionHalfDemand"],
        "maximumFlow": summary["maximumFlow"],
        "defect": summary["minimumDefect"],
        "assignmentCount": len(assignments),
        "distinctSourceCount": len(set(sources)),
        "certificateChecks": certificate["checks"],
        "sourceSha256": {
            str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"): sha256(CORE_PATH),
            str(SOFT_PATH.relative_to(ROOT)).replace("\\", "/"): sha256(SOFT_PATH),
        },
    }
    checks = {
        "zeroDefect": payload["defect"] == 0,
        "flowSaturatesDemand": payload["maximumFlow"] == payload["globalDemand"],
        "literalSourcesDistinct": (
            payload["assignmentCount"]
            == payload["distinctSourceCount"]
            == payload["globalDemand"]
        ),
        "certificateChecksPass": all(payload["certificateChecks"].values()),
        "correctedP4Used": "P4_outsideAttachment" in payload["evaluatedFamilies"],
    }
    payload["checks"] = checks
    if not all(checks.values()):
        raise AssertionError(checks)
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    OUTPUT.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "defect": payload["defect"],
                "demand": payload["globalDemand"],
                "flow": payload["maximumFlow"],
                "payloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
