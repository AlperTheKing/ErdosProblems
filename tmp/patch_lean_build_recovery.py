from pathlib import Path
files = [
    Path('problems/23/writeup/_codex_branchb_lean_build.py'),
    Path('problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py'),
]
new = '''    cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={out}", str(path)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=formal_root, env=env, text=True, capture_output=True)
    returncode = proc.returncode
    stdout = proc.stdout
    stderr = proc.stderr
    recovery_olean = None
    recovery_method = None
    if returncode != 0 and "failed to write" in stderr and "Permission denied" in stderr:
        retry_out = out.parent / f"{out.stem}.retry.{os.getpid()}.{time.time_ns()}{out.suffix}"
        retry_cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={retry_out}", str(path)]
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
    start = text.index('    cmd = ["lake", "env", "lean"')
    end = text.index('\n\ndef main() -> None:', start)
    path.write_text(text[:start] + new + text[end:], encoding='utf-8')
    print(path)
