#!/usr/bin/env python3
"""CLAUDE independent gate (2026-07-09): (A) forbidden-token scan of T8 ConcreteCage + Chart000Cone* sources;
(B) rebuild T8 ConcreteCage 6 modules (sequential, dep order); (C) rebuild the CURRENT sharded Chart000Cone
set: support -> shards (32 workers) -> aggregator; (D) axiom-probe key aggregator decls.
Oleans go to tmp/claude_lean_o_t8c000_regate layered over tmp/claude_lean_o_base_v1 via LEAN_PATH (no Codex
olean is trusted). green = rc==0 AND no 'error:' in stderr.
Summary -> tmp/claude_t8_chart000_regate_summary.json
"""
import os, json, time, re, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path("E:/Projects/ErdosProblems")
FORMAL = ROOT / "formal-conjectures"
SRC = ROOT / "problems/23/lean"
BASE = ROOT / "tmp/claude_lean_o_base_v1"
# Build INTO the base cache (single-dir pattern: Lean expects dep oleans in the first LEAN_PATH entry;
# my rebuild overwrites Codex's oleans with my own — that IS the independent gate).
MINE = BASE
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

def mod_name(p: Path) -> str:
    return ".".join(p.relative_to(SRC).with_suffix("").parts)

def run_lean(p: Path) -> dict:
    mod = mod_name(p)
    out = MINE / (mod.replace(".", "/") + ".olean")
    out.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(MINE) + os.pathsep + str(BASE) + os.pathsep + env.get("LEAN_PATH", "")
    t0 = time.time()
    r = subprocess.run(["lake", "env", "lean", f"--root={SRC}", f"--o={out}", str(p)],
                       cwd=FORMAL, env=env, text=True, capture_output=True)
    ok = (r.returncode == 0) and ("error:" not in r.stderr.lower())
    return {"module": mod, "rc": r.returncode, "ok": ok, "sec": round(time.time() - t0, 1),
            "stdout": r.stdout, "err": ("" if ok else (r.stdout[-500:] + r.stderr[-1500:]))}

summary = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "phases": {}}

# ---- Phase A: forbidden-token scan --------------------------------------------------------------
tok = re.compile(rb"sorry|admit|native_decide|sorryAx")
scan_hits = []
cc_dir = SRC / "Erdos23Delta0/Ell5/ConcreteCage"
cp_dir = SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
scan_files = sorted(cc_dir.glob("*.lean")) + sorted(cp_dir.glob("Chart000Cone*.lean"))
for f in scan_files:
    data = f.read_bytes()
    for m in tok.finditer(data):
        line_no = data.count(b"\n", 0, m.start()) + 1
        line = data[data.rfind(b"\n", 0, m.start()) + 1:data.find(b"\n", m.start())][:160]
        scan_hits.append({"file": str(f.relative_to(ROOT)), "line": line_no,
                          "text": line.decode("utf-8", "replace")})
summary["phases"]["token_scan"] = {"files": len(scan_files), "hits": scan_hits}
print(f"[A] token scan: {len(scan_files)} files, {len(scan_hits)} hits", flush=True)

# ---- Phase B: T8 ConcreteCage (sequential dep order) ---------------------------------------------
t8_order = ["Basic", "Bank", "Proper", "Restrict", "PureSplit", "PureLensSplit"]
t8_results = []
for name in t8_order:
    r = run_lean(cc_dir / f"{name}.lean")
    r.pop("stdout", None)
    t8_results.append(r)
    print(f"[B] {'OK ' if r['ok'] else 'FAIL'} {r['module']} rc={r['rc']} {r['sec']}s", flush=True)
    if not r["ok"]:
        break
t8_ok = all(r["ok"] for r in t8_results) and len(t8_results) == len(t8_order)
summary["phases"]["t8"] = {"ok": t8_ok, "results": t8_results}

# ---- Phase C: Chart000Cone sharded set -----------------------------------------------------------
all_c000 = sorted(cp_dir.glob("Chart000Cone*.lean"))
agg = cp_dir / "Chart000Cone.lean"
support = [f for f in all_c000 if "Support" in f.name and f != agg]
shards = [f for f in all_c000 if f != agg and f not in support]
print(f"[C] chart000 set: {len(all_c000)} files = {len(support)} support + {len(shards)} shards + 1 aggregator", flush=True)

c000 = {"support": [], "shards_ok": 0, "shards_fail": [], "aggregator": None,
        "counts": {"total": len(all_c000), "support": len(support), "shards": len(shards)}}
ok_so_far = True
for f in support:
    r = run_lean(f); r.pop("stdout", None)
    c000["support"].append(r)
    print(f"[C] {'OK ' if r['ok'] else 'FAIL'} support {r['module']} {r['sec']}s", flush=True)
    ok_so_far = ok_so_far and r["ok"]

if ok_so_far:
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=32) as ex:
        futs = {ex.submit(run_lean, f): f for f in shards}
        done = 0
        for fut in as_completed(futs):
            r = fut.result(); r.pop("stdout", None)
            done += 1
            if r["ok"]:
                c000["shards_ok"] += 1
            else:
                c000["shards_fail"].append(r)
            if done % 50 == 0 or not r["ok"]:
                print(f"[C] shards {done}/{len(shards)} ok={c000['shards_ok']} fail={len(c000['shards_fail'])} ({round(time.time()-t0,1)}s)", flush=True)
    ok_so_far = ok_so_far and not c000["shards_fail"]
    print(f"[C] shard wave done: {c000['shards_ok']}/{len(shards)} ok in {round(time.time()-t0,1)}s", flush=True)

if ok_so_far:
    r = run_lean(agg); r.pop("stdout", None)
    c000["aggregator"] = r
    print(f"[C] {'OK ' if r['ok'] else 'FAIL'} aggregator rc={r['rc']} {r['sec']}s", flush=True)
    ok_so_far = ok_so_far and r["ok"]
summary["phases"]["chart000"] = {"ok": ok_so_far, **c000}

# ---- Phase D: axiom probe of aggregator key decls ------------------------------------------------
probe_result = {"ok": False, "decls": [], "note": ""}
if ok_so_far:
    text = agg.read_text(encoding="utf-8", errors="replace")
    stack, decls = [], []
    for line in text.splitlines():
        mns = re.match(r"^namespace\s+([\w.]+)", line)
        mend = re.match(r"^end\s+([\w.]+)", line)
        mdecl = re.match(r"^(?:noncomputable\s+)?(?:theorem|def|lemma)\s+([\w'.]+)", line)
        if mns:
            stack.append(mns.group(1))
        elif mend and stack and stack[-1] == mend.group(1):
            stack.pop()
        elif mdecl:
            name = mdecl.group(1)
            if any(k in name for k in ("chunk", "mult", "Witness", "witness", "combo")):
                decls.append(".".join(stack + [name]))
    decls = list(dict.fromkeys(decls))[:8]
    probe_result["decls"] = decls
    if decls:
        probe = ROOT / "tmp/claude_chart000cone_probe.lean"
        probe.write_text("import " + mod_name(agg) + "\n" +
                         "".join(f"#print axioms {d}\n" for d in decls), encoding="utf-8")
        env = os.environ.copy()
        env["LEAN_PATH"] = str(MINE) + os.pathsep + str(BASE) + os.pathsep + env.get("LEAN_PATH", "")
        r = subprocess.run(["lake", "env", "lean", f"--root={SRC}", str(probe)],
                           cwd=FORMAL, env=env, text=True, capture_output=True)
        probe_result["rc"] = r.returncode
        probe_result["stdout"] = r.stdout[-4000:]
        bad = []
        for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", r.stdout):
            axs = {a.strip() for a in m.group(2).split(",") if a.strip()}
            if not axs.issubset(ALLOWED_AXIOMS):
                bad.append({"decl": m.group(1), "axioms": sorted(axs)})
        probe_result["bad"] = bad
        probe_result["ok"] = (r.returncode == 0) and not bad and ("sorryAx" not in r.stdout)
    else:
        probe_result["note"] = "no matching decls found in aggregator"
summary["phases"]["axiom_probe"] = probe_result
print(f"[D] axiom probe ok={probe_result['ok']} decls={len(probe_result['decls'])}", flush=True)

summary["all_ok"] = (not scan_hits) and t8_ok and summary["phases"]["chart000"]["ok"] and probe_result["ok"]
summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
(ROOT / "tmp/claude_t8_chart000_regate_summary.json").write_text(json.dumps(summary, indent=1))
print(f"VERDICT all_ok={summary['all_ok']} (token_hits={len(scan_hits)} t8={t8_ok} "
      f"chart000={summary['phases']['chart000']['ok']} probe={probe_result['ok']}) "
      f"-> tmp/claude_t8_chart000_regate_summary.json", flush=True)
