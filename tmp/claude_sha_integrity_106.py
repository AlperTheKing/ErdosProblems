#!/usr/bin/env python3
"""FAST conjunct-3 integrity dry-run: for every certified row in the latest ledger, locate its newest
exact_ok SHA-pinned manifest and verify the solution-file SHA matches the manifest's claim. SHA-only
(no re-solve) — validates manifest integrity + the aggregate-reverify locate/SHA machinery before the
108 endgame. Reports any missing manifest / missing solution file / SHA mismatch."""
import json, hashlib, glob
from pathlib import Path

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def latest_ledger():
    leds = sorted(glob.glob("tmp/eq_odl1_rung2_chart_batch_ledger_v*.json"), key=lambda p: Path(p).stat().st_mtime)
    return leds[-1] if leds else None

# index all manifests once (newest exact_ok per (chart,dom))
manifests = {}
for p in glob.glob("tmp/*certificate_manifest*.json"):
    try:
        c = json.loads(Path(p).read_text())
    except Exception:
        continue
    if c.get("exact_ok"):
        key = (c.get("chart"), c.get("dominant"))
        mt = Path(p).stat().st_mtime
        if key not in manifests or mt > manifests[key][1]:
            manifests[key] = (p, mt, c)

led = latest_ledger()
j = json.loads(Path(led).read_text())
rows = j.get("certified_rows", [])
print(f"ledger {Path(led).name}: certified_rows={len(rows)} certified_count={j.get('certified_count')}", flush=True)

ok = 0; issues = []
for r in rows:
    ch, d = r.get("chart"), r.get("dominant")
    m = manifests.get((ch, d))
    if not m:
        issues.append((ch, d, "NO-MANIFEST")); continue
    mpath, _mt, c = m
    sol = c.get("solution_jsonl") or c.get("source_solution")
    claimed = (c.get("solution_jsonl_sha256") or c.get("source_solution_sha256") or "").lower()
    if not sol or not Path(sol).exists():
        issues.append((ch, d, f"NO-SOLUTION-FILE({sol})")); continue
    if claimed:
        actual = sha256(sol).lower()
        if actual != claimed:
            issues.append((ch, d, f"SHA-MISMATCH claimed={claimed[:12]} actual={actual[:12]}")); continue
        ok += 1
    else:
        ok += 1; issues.append((ch, d, "NO-CLAIMED-SHA(soft)"))

print(f"INTEGRITY: sha_ok={ok}/{len(rows)}  hard_issues={len([i for i in issues if 'soft' not in i[2]])}", flush=True)
for i in issues[:40]:
    print("  ISSUE", i, flush=True)
