"""Replay the lane-01 semantics audit without modifying production files."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[3]
SEMANTICS = LANE / "SEMANTICS.json"
REPORT = LANE / "REPORT.md"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def citations(value):
    if isinstance(value, dict):
        if {"path", "line", "expect"} <= value.keys():
            yield value
        for child in value.values():
            yield from citations(child)
    elif isinstance(value, list):
        for child in value:
            yield from citations(child)

def run_search(pattern: str) -> list[str]:
    cmd = [
        "rg", "-n", "--glob", "*.lean", "--glob", "!Cert/**",
        "--glob", "!O14/**", pattern, "problems/23/lean/Erdos23Delta0",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr)
    return [line for line in proc.stdout.splitlines() if line]

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main() -> None:
    data = json.loads(SEMANTICS.read_text(encoding="utf-8"))
    assert data["status"] == "UNDEFINED"
    checked = []
    for cite in citations(data):
        path = ROOT / cite["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        line = lines[cite["line"] - 1]
        assert cite["expect"] in line, (cite, line)
        checked.append({
            "path": cite["path"], "line": cite["line"],
            "expect": cite["expect"],
            "line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
        })
    for module in data["consumer_chain_definitions"]:
        path = ROOT / module["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        for definition in module["definitions"]:
            line = lines[definition["line"] - 1]
            symbol = definition["name"].rsplit(".", 1)[-1]
            assert symbol in line, (module["path"], definition, line)
            checked.append({
                "path": module["path"], "line": definition["line"],
                "expect": symbol,
                "line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
            })
    probes = {
        "r29_or_2943": run_search(r"\bR29\b|\br29\b|\b2943\b"),
        "claimed_transfer_api": run_search(
            r"CheckedTransferMatching|CheckedOutsideAttachmentBaseTerminal|"
            r"outsideAttachment|FreeHalfKey|TransferObligation"
        ),
        "fullbank_constructors": run_search(
            r"FullBankGlobalPackage|certificate_of_activeComponent_mixedDoorBankHall"
        ),
    }
    rebuild = load_module(
        ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py",
        "lane01_rebuild_owner_hall",
    )
    incidence = rebuild.load_untrusted_incidence()
    rebuilt = rebuild.rebuild_scope(incidence)
    _, pair, _, _, active_edges, active_vertices, _, collision, hit = rebuilt
    masks, reasons, companions = rebuild.owner_sources(
        incidence, pair, active_edges, active_vertices
    )
    owners = rebuild.OWNERS
    owner_demand = {
        str(owner): collision.get(owner, 0) + hit.get(owner, 0)
        for owner in owners
    }
    r29_replay = {
        "n": incidence["n"],
        "canonical_incidence_sha256": rebuild.incidence_sha(incidence),
        "owners": list(owners),
        "owner_demand": owner_demand,
        "demand": sum(owner_demand.values()),
        "reachable_freehalf_sources": len(masks),
        "defect": sum(owner_demand.values()) - len(masks),
        "reasoned_source_count": len(reasons),
        "companion_counts": {str(o): len(companions[o]) for o in owners},
    }
    assert r29_replay["n"] == 2943
    assert r29_replay["demand"] == 19953
    assert r29_replay["reachable_freehalf_sources"] == 19925
    assert r29_replay["defect"] == 28
    source_paths = data["source_manifest_scope"]
    for rel in source_paths:
        assert (ROOT / rel).is_file(), rel
    check = {
        "schema": "r29-fullbank-semantics-audit-check-v1",
        "status": data["status"],
        "citation_count": len(checked),
        "citations": checked,
        "lean_search_probes": probes,
        "r29_exact_reconstruction": r29_replay,
        "assertions": {
            "all_citations_match": True,
            "status_is_undefined": True,
            "semantics_is_valid_json": True,
            "no_float_tokens_in_semantics": not bool(re.search(
                r"(?<![A-Za-z0-9_])\d+\.\d+(?![A-Za-z0-9_])",
                SEMANTICS.read_text(encoding="utf-8"),
            )),
        },
    }
    assert all(check["assertions"].values())
    check_path = LANE / "AUDIT_CHECK.json"
    check_path.write_text(
        json.dumps(check, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest_paths = [ROOT / rel for rel in source_paths] + [
        SEMANTICS, REPORT, Path(__file__).resolve(), check_path,
    ]
    manifest = {
        "schema": "r29-fullbank-semantics-sha256-v1",
        "algorithm": "SHA256",
        "files": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in sorted(set(manifest_paths))
        },
    }
    (LANE / "SHA256SUMS.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": data["status"],
        "citation_count": len(checked),
        "manifest_file_count": len(manifest["files"]),
        "assertions": check["assertions"],
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
