import json
import sys
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_lean_build as lean_build


root = Path.cwd()
formal = (root / "formal-conjectures").resolve()
src = (root / "problems/23/lean").resolve()
build = (root / "tmp/a1proper_lean_o_v2").resolve()
build.mkdir(parents=True, exist_ok=True)

modules = [
    "Erdos23Delta0/PolyCert.lean",
    "Erdos23Delta0/CertGraph.lean",
    "Erdos23Delta0/A1MaskSymmetry.lean",
    "Erdos23Delta0/A1ProperWrapper.lean",
]

results = []
ok = True
for module in modules:
    result = lean_build.run_lean(formal, src, build, src / module)
    results.append(result)
    print(f"{result['module']} rc={result['returncode']} sec={result['seconds']}", flush=True)
    if result["returncode"] != 0:
        ok = False
        break

out = root / "tmp/a1proper_targeted_lean_build_deps_codex_v1.json"
out.write_text(
    json.dumps(
        {
            "schema": "a1proper_targeted_lean_build_deps_v1",
            "modules": modules,
            "results": results,
            "ok": ok,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(
    json.dumps(
        {
            "summary": str(out),
            "ok": ok,
            "results": [(r["module"], r["returncode"], r["seconds"]) for r in results],
        },
        sort_keys=True,
    )
)
raise SystemExit(0 if ok else 1)
