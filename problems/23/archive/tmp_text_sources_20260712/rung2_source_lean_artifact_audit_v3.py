import json
from pathlib import Path

root = Path.cwd()
summary_path = root / "tmp/eq_odl1_rung2_source_lean_build_k5_G6_near_lexsmall_96prime_v3_summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))

tokens = ["native_decide", "sorry", "admit", "axiom", "unsafe"]
src_root = Path(summary["src_root"])
files = []
for result in summary["results"]:
    module = result["module"]
    rel = Path(*module.split(".")).with_suffix(".lean")
    path = src_root / rel
    files.append(path)

hits = []
for path in files:
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        for tok in tokens:
            if tok in line:
                hits.append({"file": str(path), "line": lineno, "token": tok, "text": line.strip()})

failures = [r for r in summary["results"] if r["returncode"] != 0]
audit = {
    "schema": "eq_odl1_rung2_source_lean_artifact_audit_v1",
    "build_summary": str(summary_path),
    "files": [str(p) for p in files],
    "file_count": len(files),
    "forbidden_tokens": tokens,
    "forbidden_hits": hits,
    "forbidden_hit_count": len(hits),
    "build_failures": failures,
    "build_failure_count": len(failures),
    "pass": not hits and not failures,
}

out = root / "tmp/eq_odl1_rung2_source_lean_artifact_audit_k5_G6_near_lexsmall_96prime_v3.json"
out.write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(json.dumps({"pass": audit["pass"], "files": len(files), "forbidden_hits": len(hits), "build_failures": len(failures), "out": str(out)}, indent=2))
