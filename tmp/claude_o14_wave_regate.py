#!/usr/bin/env python3
"""CLAUDE independent wave re-gate (2026-07-09) of the SCALED O14 sharded chart payloads (Chart001..Chart107;
Chart000 already accepted) + PayloadRegistry. Codex's local Lean is toolchain-blocked, so this is the ONLY
gate. Phases: (0) forbidden-token scan of all new Chart*.lean; (1) supports; (2) all shards (32 workers,
resumable: skip if olean newer than source); (3) 107 aggregators; (4) PayloadRegistry.
Summary -> tmp/claude_o14_wave_regate_summary.json (updated after each phase)."""
import os, json, time, re, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path("E:/Projects/ErdosProblems")
FORMAL = ROOT / "formal-conjectures"
SRC = ROOT / "problems/23/lean"
BASE = ROOT / "tmp/claude_lean_o_base_v1"
CP = SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
SUMMARY = ROOT / "tmp/claude_o14_wave_regate_summary.json"

def mod_name(p): return ".".join(p.relative_to(SRC).with_suffix("").parts)
def olean_of(p): return BASE / p.relative_to(SRC).with_suffix(".olean")

def run_lean(p):
    out = olean_of(p); out.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(BASE) + os.pathsep + env.get("LEAN_PATH", "")
    t0 = time.time()
    r = subprocess.run(["lake", "env", "lean", f"--root={SRC}", f"--o={out}", str(p)],
                       cwd=FORMAL, env=env, text=True, capture_output=True)
    ok = (r.returncode == 0) and ("error:" not in r.stderr.lower())
    return {"module": mod_name(p), "rc": r.returncode, "ok": ok, "sec": round(time.time() - t0, 1),
            "err": ("" if ok else (r.stdout[-400:] + r.stderr[-1200:]))}

def fresh(p):
    o = olean_of(p)
    return o.exists() and o.stat().st_mtime > p.stat().st_mtime

summary = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "phases": {}}
def save(): SUMMARY.write_text(json.dumps(summary, indent=1))

all_new = sorted(f for f in CP.glob("Chart*.lean") if not f.name.startswith("Chart000"))
aggs = [f for f in all_new if re.fullmatch(r"Chart\d{3}Cone\.lean", f.name)]
supports = [f for f in all_new if "Support" in f.name]
shards = [f for f in all_new if f not in aggs and f not in supports and f.name != "Chart000Bridge.lean"]
print(f"[scope] {len(all_new)} files = {len(supports)} supports + {len(shards)} shards + {len(aggs)} aggregators", flush=True)

# Phase 0: token scan
tok = re.compile(rb"sorry|admit|native_decide|sorryAx")
hits = []
for f in all_new:
    data = f.read_bytes()
    if tok.search(data):
        for m in tok.finditer(data):
            hits.append({"file": f.name, "off": m.start()})
            if len(hits) > 20: break
    if len(hits) > 20: break
summary["phases"]["tokens"] = {"files": len(all_new), "hits": hits}
print(f"[0] token scan: {len(all_new)} files, {len(hits)} hits", flush=True)
save()
if hits:
    print("VERDICT all_ok=False (token hits)", flush=True); raise SystemExit(1)

def wave(name, files, workers):
    res = {"ok": 0, "skip": 0, "fail": []}
    t0 = time.time()
    todo = [f for f in files if not fresh(f)]
    res["skip"] = len(files) - len(todo)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_lean, f): f for f in todo}
        done = 0
        for fut in as_completed(futs):
            r = fut.result(); done += 1
            if r["ok"]: res["ok"] += 1
            else: res["fail"].append(r)
            if done % 200 == 0 or not r["ok"]:
                print(f"[{name}] {done}/{len(todo)} ok={res['ok']} fail={len(res['fail'])} ({round(time.time()-t0)}s)", flush=True)
                save()
    res["sec"] = round(time.time() - t0)
    print(f"[{name}] DONE ok={res['ok']} skip={res['skip']} fail={len(res['fail'])} in {res['sec']}s", flush=True)
    return res

summary["phases"]["supports"] = wave("supports", supports, 16); save()
if summary["phases"]["supports"]["fail"]: print("VERDICT all_ok=False (supports)", flush=True); raise SystemExit(1)
summary["phases"]["shards"] = wave("shards", shards, 32); save()
if summary["phases"]["shards"]["fail"]: print("VERDICT all_ok=False (shards)", flush=True); raise SystemExit(1)
summary["phases"]["aggregators"] = wave("aggregators", aggs, 16); save()
if summary["phases"]["aggregators"]["fail"]: print("VERDICT all_ok=False (aggregators)", flush=True); raise SystemExit(1)
reg = run_lean(SRC / "Erdos23Delta0/O14/Generated/PayloadRegistry.lean")
summary["phases"]["registry"] = reg
summary["all_ok"] = reg["ok"]
summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
save()
print(f"[registry] rc={reg['rc']} ok={reg['ok']}", flush=True)
print(f"VERDICT all_ok={summary['all_ok']}", flush=True)
