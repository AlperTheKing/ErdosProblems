from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

import _codex_internal_offsupport_gate as gate
from _codex_internal_offsupport_resume import graph_records


def check(task):
    n, g6 = task
    try:
        witness = gate.find_atoms_with_chord((g6, "flowdichotomy", 14))
        return {"n": n, "g6": g6, "status": "witness" if witness else "ok", "witness": witness}
    except RuntimeError as exc:
        return {"n": n, "g6": g6, "status": "node_cap", "error": str(exc)}


def main():
    missing = []
    by_n = {}
    for n in range(8, 16):
        saved_path = ROOT / "tmp" / f"codex_active_hall_m15_n{n:02d}.jsonl"
        saved = {
            json.loads(line)["g6"]
            for line in saved_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        absent = sorted(set(graph_records(n, 15)) - saved)
        by_n[n] = len(absent)
        missing.extend((n, g6) for g6 in absent)

    out_path = ROOT / "tmp" / "codex_agent_m15_missing_results.jsonl"
    counts = {"ok": 0, "witness": 0, "node_cap": 0}
    with out_path.open("w", encoding="utf-8", buffering=1) as stream:
        with ProcessPoolExecutor(max_workers=8) as pool:
            for row in pool.map(check, missing, chunksize=1):
                counts[row["status"]] += 1
                stream.write(json.dumps(row, separators=(",", ":")) + "\n")
    print("M15_MISSING", json.dumps({"by_n": by_n, "total": len(missing), "counts": counts}, separators=(",", ":")))


if __name__ == "__main__":
    main()
