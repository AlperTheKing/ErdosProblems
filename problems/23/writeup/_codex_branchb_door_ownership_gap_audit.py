"""Codex audit: Branch-B cactus door-ownership wiring evidence.

This script does not prove the door-ownership certificate.  It records whether
the current repository contains an explicit checker/theorem/artifact for the
finite cactus door-credit ownership obligation described in the July 7 mailbox:

  every cactus d_C / 2 door credit is assigned exactly once and is counted once
  in the PacketExchange packet door count d.

The output is a small JSON gap audit for coordination and future CI wiring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "problems" / "23" / "lean" / "Erdos23Delta0"
WRITEUP_ROOT = ROOT / "problems" / "23" / "writeup"
TMP_ROOT = ROOT / "tmp"


DOOR_TERMS = [
    "CactusDoorOwnership",
    "DoorOwnership",
    "cactus door",
    "door-credit ownership",
    "door ownership",
]

LATEST_REQUIRED_TERMS = [
    "CactusDoorOwnership",
    "cactus d_C/2 credit",
    "door-credit ownership",
    "finite door-ownership wiring",
]


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def scan_files(root: Path, suffixes: tuple[str, ...], terms: list[str]) -> list[dict]:
    hits: list[dict] = []
    if not root.exists():
        return hits
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for term in terms:
                if term.lower() in line.lower():
                    hits.append(
                        {
                            "file": str(path.relative_to(ROOT)),
                            "line": lineno,
                            "term": term,
                            "text": line.strip()[:240],
                        }
                    )
    return hits


def file_contains(path: Path, terms: list[str]) -> dict:
    out = {
        "path": str(path.relative_to(ROOT)) if path.exists() else str(path),
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "terms": {},
    }
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    for term in terms:
        out["terms"][term] = term.lower() in low
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default=str(TMP_ROOT / "branchb_door_ownership_gap_audit_codex_v1.json"),
    )
    args = ap.parse_args()

    lean_hits = scan_files(LEAN_ROOT, (".lean",), DOOR_TERMS)
    writeup_hits = scan_files(WRITEUP_ROOT, (".md", ".py"), DOOR_TERMS)

    assembly_script = WRITEUP_ROOT / "_claude_branchB_assembly_audit.py"
    latest_assembly_note = WRITEUP_ROOT / "BRANCH_B_BANKED_UPO_ASSEMBLY_GPTPRO.md"
    soundness_audit = WRITEUP_ROOT / "LEAN_SOUNDNESS_AUDIT_GPTPRO.md"
    current_audit = TMP_ROOT / "branchb_lean_artifact_audit_codex_now_with_scan.json"

    assembly_script_terms = file_contains(assembly_script, DOOR_TERMS)
    latest_note_terms = file_contains(latest_assembly_note, LATEST_REQUIRED_TERMS)
    soundness_terms = file_contains(soundness_audit, LATEST_REQUIRED_TERMS)
    current_audit_terms = file_contains(current_audit, DOOR_TERMS)

    # Current evidence is sufficient only if Lean or the active assembly checker
    # contains an explicit door-ownership hook.  Writeup mentions alone are not a
    # machine-checkable certificate.
    lean_has_explicit = any(
        h["term"] in {"CactusDoorOwnership", "DoorOwnership"} for h in lean_hits
    )
    assembly_checks_explicit = any(
        assembly_script_terms["terms"].get(term, False)
        for term in ("CactusDoorOwnership", "DoorOwnership", "door ownership")
    )
    latest_requires = any(latest_note_terms["terms"].values()) or any(
        soundness_terms["terms"].values()
    )

    result = {
        "schema": "codex_branchb_door_ownership_gap_audit_v1",
        "utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "verdict": "MISSING_MACHINE_CHECKABLE_DOOR_OWNERSHIP"
        if latest_requires and not (lean_has_explicit or assembly_checks_explicit)
        else "CHECK_PRESENT_OR_NOT_REQUIRED",
        "latest_writeup_requires_door_ownership": latest_requires,
        "lean_has_explicit_door_ownership_symbol": lean_has_explicit,
        "assembly_audit_checks_door_ownership": assembly_checks_explicit,
        "lean_hits": lean_hits,
        "writeup_hits_sample": writeup_hits[:80],
        "files": {
            "assembly_script": assembly_script_terms,
            "branchb_assembly_note": latest_note_terms,
            "lean_soundness_audit": soundness_terms,
            "current_lean_artifact_audit": current_audit_terms,
        },
        "interpretation": [
            "Current Branch-B Lean/data audits build and scan existing BranchBData shards.",
            "The active assembly audit script does not include an explicit cactus door-ownership check.",
            "The writeup/mailbox state requires finite door-credit ownership wiring before Branch-B is closed.",
        ],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {out}")
    print(result["verdict"])
    return 0 if result["verdict"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
