from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
NEEDLES = (
    "00186166",
    "Gamma = 34575",
    "Gamma=34575",
    "707 rigid",
    "676 selector",
    "cable-seed",
)
SKIP_PARTS = {".git", ".deps", "elan-dist", "third_party"}
ALLOWED_SUFFIXES = {".md", ".txt", ".py", ".json", ".jsonl", ".csv", ".tsv", ".lean"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


pattern = "|".join(NEEDLES)
proc = subprocess.run(
    ["rg", "-l", "-S", pattern, "problems/23", "coordination", "tmp/fanout",
     "--glob", "!r29_gate/d04/**"],
    cwd=ROOT, text=True, encoding="utf-8", errors="replace",
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
)
hits: list[dict[str, object]] = []
for rel in proc.stdout.splitlines():
    path = ROOT / rel
    if not path.is_file() or path.stat().st_size > 20_000_000:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    found = [needle for needle in NEEDLES if needle in text]
    hits.append({
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "needles": found,
    })

hits.sort(key=lambda x: str(x["path"]))
payload = {"needles": NEEDLES, "rg_exit": proc.returncode, "rg_stderr": proc.stderr, "hits": hits}
(OUT / "input_audit.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
