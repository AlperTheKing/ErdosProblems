#!/usr/bin/env python3
"""Add the final README/verifier hashes to the replay manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["audit_artifacts"]["README.md"] = sha(HERE / "README.md")
manifest["audit_artifacts"]["verify_manifest.py"] = sha(HERE / "verify_manifest.py")
manifest["audit_artifacts"]["seal_audit.py"] = sha(Path(__file__))
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
print("SEALED_AUDIT_ARTIFACT_HASHES")
