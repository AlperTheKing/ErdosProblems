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
    returncode = proc.returncode
    stdout = proc.stdout
    stderr = proc.stderr
    recovery_olean = None
    recovery_method = None

    def write_permission_only(err: str) -> bool:
        lowered = err.lower()
        return "failed to write" in lowered and "permission denied" in lowered and "error:" not in lowered

    if returncode != 0 and write_permission_only(stderr):
        retry_out = out.parent / f"{out.stem}.retry.{os.getpid()}.{time.time_ns()}{out.suffix}"
        retry_cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={retry_out}", str(path)]
        retry_start = time.time()
        retry = subprocess.run(retry_cmd, cwd=formal_root, env=env, text=True, capture_output=True)
        stdout = stdout + retry.stdout
        stderr = stderr + "\nWRITE_PERMISSION_RETRY_OLEAN=" + str(retry_out) + "\n" + retry.stderr
        if retry.returncode == 0:
            try:
                if out.exists():
                    out.unlink()
                shutil.copyfile(retry_out, out)
                returncode = 0
                recovery_olean = retry_out
                recovery_method = "fresh_rerun"
                stderr = stderr + "\nRECOVERED_OLEAN_FROM_FRESH_RERUN=" + str(retry_out) + "\n"
            except OSError as exc:
                returncode = 1
                stderr = stderr + "\nRECOVERY_COPY_FAILED=" + repr(exc) + "\n"
        elif write_permission_only(retry.stderr):
            source_mtime = path.stat().st_mtime
            fresh_tmps = [
                p for p in retry_out.parent.glob(retry_out.name + ".tmp.*")
                if p.stat().st_mtime >= source_mtime and p.stat().st_mtime >= retry_start
            ]
            fresh_tmps.sort(key=lambda p: p.stat().st_mtime)
            if fresh_tmps:
                retry_tmp = fresh_tmps[-1]
                try:
                    if out.exists():
                        out.unlink()
                    shutil.copyfile(retry_tmp, out)
                    returncode = 0
                    recovery_olean = retry_tmp
                    recovery_method = "fresh_rerun_tmp_copy"
                    stderr = stderr + "\nRECOVERED_OLEAN_FROM_FRESH_RERUN_TMP=" + str(retry_tmp) + "\n"
                except OSError as exc:
                    returncode = 1
                    stderr = stderr + "\nRECOVERY_COPY_FAILED=" + repr(exc) + "\n"
            else:
                returncode = retry.returncode
                stderr = stderr + "\nFRESH_RERUN_TMP_NOT_FOUND_OR_STALE\n"
        else:
            returncode = retry.returncode
            stderr = stderr + "\nFRESH_RERUN_FAILED\n"
    return {
        "module": mod,
        "file": str(path),
        "olean": str(out),
        "returncode": returncode,
        "seconds": round(time.time() - t0, 3),
        "stdout": stdout[-2000:],
        "stderr": stderr[-4000:],
        "recovered_tmp": None,
        "recovery_olean": str(recovery_olean) if recovery_olean else None,
        "recovery_method": recovery_method,
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
    dictionary = src_root / "Erdos23Delta0/Cert/BranchBDictionaryAudit.lean"
    pilot = src_root / "Erdos23Delta0/Cert/BranchBData/Pilot.lean"
    shards = sorted((src_root / "Erdos23Delta0/Cert/BranchBData").glob("Shard*.lean"))
    index = src_root / "Erdos23Delta0/Cert/BranchBData.lean"

    results: list[dict] = []
    prelude = [support] + ([dictionary] if dictionary.exists() else []) + [pilot]
    for path in prelude:
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
