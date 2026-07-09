#!/usr/bin/env python3
"""CLAUDE per-chart STAGED re-gate (2026-07-10) of Chart001..107 sharded payloads.
Disk-wall workaround: oleans avg ~81MB => full set ~3.4TB impossible. Per chart: build support -> shards
(20 workers) -> aggregator -> axiom-probe -> record verdict+SHAs -> DELETE the chart's oleans. Verdict ledger
(append, resume-key) = tmp/claude_o14_staged_ledger.jsonl. NOTE: registry-level compile needs ALL shard oleans
transitively -> awaits Codex compact re-emission (lane 0); this run = per-chart verification evidence only.
Disk guard: abort if E: free < 60GB before a chart."""
import os, json, time, re, subprocess, shutil, hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path("E:/Projects/ErdosProblems")
FORMAL = ROOT / "formal-conjectures"
SRC = ROOT / "problems/23/lean"
BASE = ROOT / "tmp/claude_lean_o_base_v1"
CP = SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
OCP = BASE / "Erdos23Delta0/O14/Generated/ChartPayloads"
LEDGER = ROOT / "tmp/claude_o14_staged_ledger.jsonl"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}

def mod_name(p): return ".".join(p.relative_to(SRC).with_suffix("").parts)

def run_lean(p, olean=True):
    out = BASE / p.relative_to(SRC).with_suffix(".olean")
    out.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(BASE) + os.pathsep + env.get("LEAN_PATH", "")
    cmd = ["lake", "env", "lean", f"--root={SRC}"] + ([f"--o={out}"] if olean else []) + [str(p)]
    r = subprocess.run(cmd, cwd=FORMAL, env=env, text=True, capture_output=True)
    ok = (r.returncode == 0) and ("error:" not in r.stderr.lower())
    return ok, r.returncode, r.stdout, (r.stdout[-300:] + r.stderr[-900:] if not ok else "")

done = set()
if LEDGER.exists():
    for line in LEDGER.read_text().splitlines():
        try: done.add(json.loads(line)["chart"])
        except Exception: pass

charts = sorted({m.group(1) for f in CP.glob("Chart*.lean")
                 for m in [re.match(r"(Chart\d{3})", f.name)] if m and m.group(1) != "Chart000"})
print(f"[scope] {len(charts)} charts, {len(done)} already in ledger", flush=True)

for chart in charts:
    if chart in done: continue
    free_gb = shutil.disk_usage("E:/").free / 2**30
    if free_gb < 60:
        print(f"ABORT: only {free_gb:.1f}GB free before {chart}", flush=True); break
    files = sorted(CP.glob(f"{chart}*.lean"))
    agg = CP / f"{chart}Cone.lean"
    bridge = CP / f"{chart}Bridge.lean"
    support = [f for f in files if "Support" in f.name]
    shards = [f for f in files if f not in support and f != agg and f != bridge]
    rec = {"chart": chart, "t": time.strftime("%H:%M:%S"), "n_shards": len(shards),
           "sha_agg": hashlib.sha256(agg.read_bytes()).hexdigest().upper()[:16] if agg.exists() else None}
    t0 = time.time(); ok_all = True; fails = []
    for f in support:
        ok, rc, _, err = run_lean(f)
        if not ok: ok_all = False; fails.append({"m": mod_name(f), "rc": rc, "err": err})
    if ok_all:
        with ThreadPoolExecutor(max_workers=20) as ex:
            for fut in as_completed({ex.submit(run_lean, f): f for f in shards}):
                ok, rc, _, err = fut.result()
                if not ok: ok_all = False; fails.append({"rc": rc, "err": err})
    if ok_all and agg.exists():
        ok, rc, _, err = run_lean(agg)
        rec["agg_rc"] = rc
        if not ok: ok_all = False; fails.append({"m": "AGG", "rc": rc, "err": err})
    # axiom probe on the aggregator's witness decls
    if ok_all:
        text = agg.read_text(encoding="utf-8", errors="replace")
        stack, decls = [], []
        for line in text.splitlines():
            mns = re.match(r"^namespace\s+([\w.]+)", line)
            mend = re.match(r"^end\s+([\w.]+)", line)
            md = re.match(r"^(?:noncomputable\s+)?(?:theorem|def|lemma)\s+([\w'.]+)", line)
            if mns: stack.append(mns.group(1))
            elif mend and stack and stack[-1] == mend.group(1): stack.pop()
            elif md and any(k in md.group(1) for k in ("Witness", "witness", "chunk", "mult", "combo")):
                decls.append(".".join(stack + [md.group(1)]))
        decls = list(dict.fromkeys(decls))[:6]
        probe = ROOT / "tmp/claude_staged_probe.lean"
        probe.write_text("import " + mod_name(agg) + "\n" +
                         "".join(f"#print axioms {d}\n" for d in decls), encoding="utf-8")
        ok, rc, out, err = run_lean(probe, olean=False)
        bad = [m.group(1) for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", out)
               if not {a.strip() for a in m.group(2).split(",") if a.strip()} <= ALLOWED]
        rec["probe"] = {"rc": rc, "decls": len(decls), "bad": bad, "sorryAx": "sorryAx" in out}
        if rc != 0 or bad or "sorryAx" in out: ok_all = False; fails.append({"m": "PROBE", "rc": rc, "err": str(bad) + err})
    rec["ok"] = ok_all; rec["sec"] = round(time.time() - t0); rec["fails"] = fails[:4]
    # cleanup this chart's oleans (keep nothing; verification evidence = this ledger)
    n_del = 0
    for o in OCP.glob(f"{chart}*.olean"):
        o.unlink(); n_del += 1
    rec["oleans_deleted"] = n_del
    with LEDGER.open("a") as fh: fh.write(json.dumps(rec) + "\n")
    print(f"[{chart}] ok={ok_all} shards={len(shards)} {rec['sec']}s del={n_del} fails={len(fails)}", flush=True)

n_ok = sum(1 for line in LEDGER.read_text().splitlines() if json.loads(line).get("ok"))
print(f"STAGED VERDICT: {n_ok}/{len(charts)} charts ok -> {LEDGER}", flush=True)
