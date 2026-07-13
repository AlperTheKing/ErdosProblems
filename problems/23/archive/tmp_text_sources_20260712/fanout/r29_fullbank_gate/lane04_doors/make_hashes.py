#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAMES=["audit_doors.py","door_audit.json","AuditDoorDefinitions.lean","REPORT.md","make_hashes.py"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out={name:sha(HERE/name) for name in NAMES}
(HERE/"HASHES.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,sort_keys=True,indent=2))
