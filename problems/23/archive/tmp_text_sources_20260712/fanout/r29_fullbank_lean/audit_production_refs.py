#!/usr/bin/env python3
"""Exact textual reachability audit for the production Lean tree."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "problems" / "23" / "lean" / "Erdos23Delta0"
OUT = Path(__file__).resolve().parent / "production_reference_audit.json"

TERMS = [
    "CheckedTransferMatching",
    "CommonBlueExtendedMatching",
    "CommonBlueOwner",
    "ExtendedAvailable",
    "CheckedRowCompanionBaseTerminal",
    "CheckedQuiescentAttachmentBaseTerminal",
    "checkedFivePatternMatching_to_activeFullBank",
    "ActiveComponentFullBankCert",
    "checkedTransferMatching_to_activeFullBank",
    "CollisionTokenAssignment.Assignment",
    "OwnEdgeDoorSourceData",
    "ActiveComponentBankHall",
    "FullBankRelaxedCoverCert",
    "FullBankGlobalPackage",
    "DoorWallAdapter",
    "CapSource.c5Base",
    "CapSource.prune",
    "CapSource.vertexSlack",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    files = sorted(
        p for p in LEAN_ROOT.rglob("*.lean")
        if "Generated" not in p.parts
    )
    result: dict[str, object] = {
        "lean_root": str(LEAN_ROOT),
        "file_count": len(files),
        "terms": {},
    }
    terms: dict[str, list[dict[str, object]]] = {}
    for term in TERMS:
        hits: list[dict[str, object]] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), 1):
                if term in line:
                    hits.append({
                        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                        "line": line_no,
                        "text": line.strip(),
                    })
        terms[term] = hits
    result["terms"] = terms
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "file_count": len(files),
        "hit_counts": {term: len(hits) for term, hits in terms.items()},
        "output": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "output_sha256": sha256(OUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
