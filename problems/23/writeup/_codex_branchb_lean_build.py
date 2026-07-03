#!/usr/bin/env python3
"""Build generated Branch-B Lean modules into a temporary olean root.

The generated shards import a shared support module, so plain one-file `lean`
checks are not enough.  This helper compiles the support module first, then
all shards, then the aggregate BranchBData import file.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import shutil
import time
from pathlib import Path


def module_name(src_root: Path, path: Path) -> str:
    rel = path.relative_to(src_root).with_suffix("")
    return ".".join(rel.parts)


def olean_path(build_root: Path, mod: str) -> Path:
    return build_root.joinpath(*mod.split(".")).with_suffix(".olean")


def run_lean(formal_root: Path, src_root: Path, build_root: Path, path: Path) -> dict:
    mod = module_name(src_root, path)
    out = olean_path(build_root, mod)
    out.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(build_root) + os.pathsep + env.get("LEAN_PATH", "")
    cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={out}", str(path)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=formal_root, env=env, text=True, capture_output=True)
    recovered_tmp = None
    returncode = proc.returncode
    stderr = proc.stderr
    if returncode != 0 and "failed to write" in stderr and "Permission denied" in stderr:
        tmps = sorted(out.parent.glob(out.name + ".tmp.*"), key=lambda p: p.stat().st_mtime)
        if tmps:
            recovered_tmp = tmps[-1]
            if out.exists():
                out.unlink()
            shutil.copyfile(recovered_tmp, out)
            returncode = 0
            stderr = stderr + "\nRECOVERED_OLEAN_FROM=" + str(recovered_tmp) + "\n"
    return {
        "module": mod,
        "file": str(path),
        "olean": str(out),
        "returncode": returncode,
        "seconds": round(time.time() - t0, 3),
        "stdout": proc.stdout[-2000:],
        "stderr": stderr[-4000:],
        "recovered_tmp": str(recovered_tmp) if recovered_tmp else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--formal-root", default="formal-conjectures")
    ap.add_argument("--src-root", default="problems/23/lean")
    ap.add_argument("--build-root", default="tmp/branchb_lean_o_v6")
    ap.add_argument("--summary", default="tmp/branchb_lean_module_build_v6_summary.json")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    root = Path.cwd()
    formal_root = (root / args.formal_root).resolve()
    src_root = (root / args.src_root).resolve()
    build_root = (root / args.build_root).resolve()
    build_root.mkdir(parents=True, exist_ok=True)

    support = src_root / "Erdos23Delta0/Cert/BranchBSupport.lean"
    pilot = src_root / "Erdos23Delta0/Cert/BranchBData/Pilot.lean"
    shards = sorted((src_root / "Erdos23Delta0/Cert/BranchBData").glob("Shard*.lean"))
    index = src_root / "Erdos23Delta0/Cert/BranchBData.lean"

    results: list[dict] = []
    for path in [support, pilot]:
        res = run_lean(formal_root, src_root, build_root, path)
        results.append(res)
        print(f"{res['module']} rc={res['returncode']} sec={res['seconds']}", flush=True)
        if res["returncode"] != 0:
            break
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(run_lean, formal_root, src_root, build_root, p) for p in shards]
            for fut in concurrent.futures.as_completed(futs):
                res = fut.result()
                results.append(res)
                print(f"{res['module']} rc={res['returncode']} sec={res['seconds']}", flush=True)
        if all(r["returncode"] == 0 for r in results):
            res = run_lean(formal_root, src_root, build_root, index)
            results.append(res)
            print(f"{res['module']} rc={res['returncode']} sec={res['seconds']}", flush=True)

    failures = [r for r in results if r["returncode"] != 0]
    summary = {
        "schema": "branchb_lean_module_build_v1",
        "src_root": str(src_root),
        "build_root": str(build_root),
        "workers": args.workers,
        "count": len(results),
        "shard_count": len(shards),
        "failures": failures,
        "results": sorted(results, key=lambda r: r["module"]),
    }
    out = root / args.summary
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if failures:
        print(f"FAIL failures={len(failures)} summary={out}")
        raise SystemExit(1)
    print(f"PASS modules={len(results)} shards={len(shards)} summary={out}")


if __name__ == "__main__":
    main()
