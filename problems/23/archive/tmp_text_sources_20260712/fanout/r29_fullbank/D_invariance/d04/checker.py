from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROMPT_SHA256 = "20dd3fd57f29dd99ab6b2504bfc3810335339125a86f0253a6dc48853be671ad"
REQUIRED_DEFINITIONS = (
    "R29 ground-set/incidence data for N=2943",
    "the arbitrary-selector domain and admissibility rule",
    "rowCompanion relation (including direction/multiplicity)",
    "sameOwner map/relation",
    "sameFirst map/relation",
    "reservation set and when reservations are removed",
    "ordered-half rule and its boundary/tie convention",
    "anchor set and the definition of an anchor contribution",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    prompt = ROOT / "prompt.txt"
    files = sorted(
        p.name for p in ROOT.iterdir()
        if p.is_file() and p.name not in {"checker.py", "checker.out", "hashes.sha256", "report.md"}
    )
    prompt_hash = sha256(prompt) if prompt.exists() else None
    evidence_files = [
        name for name in files
        if name not in {"prompt.txt", "events.jsonl", "stderr.log"}
        and (ROOT / name).stat().st_size != 0
    ]
    result = {
        "arithmetic": {
            "claimed_all_anchor": 2600,
            "claimed_non_anchor_remainder": 19925 - 2600,
            "claimed_total": 19925,
        },
        "evidence_files": evidence_files,
        "hub_shore": [0, 1, 2],
        "n": 2943,
        "prompt_sha256": prompt_hash,
        "prompt_sha256_matches_checker": prompt_hash == PROMPT_SHA256,
        "required_definitions_absent": list(REQUIRED_DEFINITIONS) if not evidence_files else [],
        "status": "UNDERDETERMINED" if not evidence_files else "INPUT_PRESENT_REVIEW_REQUIRED",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"
    if sys.argv[1:] == ["--verify-output"]:
        expected = (ROOT / "checker.out").read_text(encoding="utf-8")
        if rendered != expected:
            raise SystemExit("checker.out mismatch")
        print("checker.out exact: true")
        return
    sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
