#!/usr/bin/env python3
"""CANONICAL aggregate re-verification of the full 108-row O14 chart batch (conjunct 3).

Reads the final SHA-pinned ledger, and for EVERY certified row:
  1. locates its certificate manifest (source_solution_jsonl + claimed SHA256),
  2. recomputes the solution-file SHA256 and checks it matches the manifest (SHA-pinned integrity),
  3. re-runs the OFFICIAL exact source_solution_check (Fraction arithmetic) and asserts
     exact_ok == true, full_negative_residual_count == 0, solution_negative_count == 0.
Emits AGGREGATE_RESULT with pass/fail per row; ANY failure or SHA mismatch => NOT all-verified.
Run this once the ledger reads 108/108. No float acceptance; exact rational only.

Usage: python claude_aggregate_reverify.py [ledger.json]
"""
from __future__ import annotations
import sys, json, hashlib, subprocess, glob, re
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

def find_manifest(chart, dom):
    # newest exact_ok manifest for this (chart,dom)
    best = None; bestmt = -1
    for p in glob.glob("tmp/*certificate_manifest*.json"):
        try:
            c = json.loads(Path(p).read_text())
        except Exception:
            continue
        if c.get("chart") == chart and c.get("dominant") == dom and c.get("exact_ok"):
            mt = Path(p).stat().st_mtime
            if mt > bestmt:
                bestmt = mt; best = (p, c)
    return best

def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else latest_ledger()
    j = json.loads(Path(ledger).read_text())
    print(f"ledger {ledger}: certified={j.get('certified_count')} pending={j.get('pending_count')}", flush=True)
    rows = j.get("certified_rows", [])
    band = j.get("band", "near_2s_minus_1"); support = j.get("support", "negative")
    passed = 0; failed = []
    for r in rows:
        ch, d = r["chart"], r["dominant"]
        m = find_manifest(ch, d)
        if not m:
            failed.append((ch, d, "no-manifest")); continue
        mpath, c = m
        sol = c.get("solution_jsonl")
        claimed = (c.get("solution_jsonl_sha256") or "").lower()
        if not sol or not Path(sol).exists():
            failed.append((ch, d, "no-solution-file")); continue
        if claimed and sha256(sol).lower() != claimed:
            failed.append((ch, d, "SHA-mismatch")); continue
        chk = f"tmp/agg_check_k{ch}_d{d}.json"
        subprocess.run([sys.executable, "-B", "problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py",
                        "--chart", str(ch), "--dominant", str(d), "--band", band, "--support", support,
                        "--solution", sol, "--summary", chk],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not Path(chk).exists():
            failed.append((ch, d, "check-failed-to-run")); continue
        cc = json.loads(Path(chk).read_text())
        ok = cc.get("exact_ok") and cc.get("full_negative_residual_count") == 0 and cc.get("solution_negative_count") == 0
        if ok:
            passed += 1
        else:
            failed.append((ch, d, f"exact_ok={cc.get('exact_ok')} negres={cc.get('full_negative_residual_count')} negco={cc.get('solution_negative_count')}"))
        if (passed + len(failed)) % 10 == 0:
            print(f"  progress: {passed} pass, {len(failed)} fail", flush=True)
    print("AGGREGATE_RESULT " + json.dumps({
        "total_rows": len(rows), "passed": passed, "failed_count": len(failed),
        "all_verified": len(failed) == 0 and passed == len(rows) == 108,
        "failures": failed[:20]}))

if __name__ == "__main__":
    main()
