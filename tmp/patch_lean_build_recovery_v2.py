from pathlib import Path
files = [
    Path('problems/23/writeup/_codex_branchb_lean_build.py'),
    Path('problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py'),
]
new_func = '''def run_lean(formal_root: Path, src_root: Path, build_root: Path, path: Path) -> dict:
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
        stderr = stderr + "\\nWRITE_PERMISSION_RETRY_OLEAN=" + str(retry_out) + "\\n" + retry.stderr
        if retry.returncode == 0:
            try:
                if out.exists():
                    out.unlink()
                shutil.copyfile(retry_out, out)
                returncode = 0
                recovery_olean = retry_out
                recovery_method = "fresh_rerun"
                stderr = stderr + "\\nRECOVERED_OLEAN_FROM_FRESH_RERUN=" + str(retry_out) + "\\n"
            except OSError as exc:
                returncode = 1
                stderr = stderr + "\\nRECOVERY_COPY_FAILED=" + repr(exc) + "\\n"
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
                    stderr = stderr + "\\nRECOVERED_OLEAN_FROM_FRESH_RERUN_TMP=" + str(retry_tmp) + "\\n"
                except OSError as exc:
                    returncode = 1
                    stderr = stderr + "\\nRECOVERY_COPY_FAILED=" + repr(exc) + "\\n"
            else:
                returncode = retry.returncode
                stderr = stderr + "\\nFRESH_RERUN_TMP_NOT_FOUND_OR_STALE\\n"
        else:
            returncode = retry.returncode
            stderr = stderr + "\\nFRESH_RERUN_FAILED\\n"
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
'''
for path in files:
    text = path.read_text(encoding='utf-8')
    start = text.index('def run_lean(')
    end = text.index('\n\ndef main() -> None:', start)
    path.write_text(text[:start] + new_func + text[end:], encoding='utf-8')
    print(path)
