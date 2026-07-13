"""Exact source-level audit of the production FullBank provider surface."""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import subprocess


ROOT = Path(__file__).resolve().parents[4]
LEAN = ROOT / "problems/23/lean/Erdos23Delta0"
OUT = Path(__file__).resolve().parent

FILES = {
    "global": LEAN / "Gamma/FullBankToLengthSurplusCharge.lean",
    "typed": LEAN / "Gamma/TypedFullBankSources.lean",
    "ports": LEAN / "Gamma/FullBankPortSinks.lean",
    "interface": LEAN / "Ell5FullBankInterface.lean",
    "activeHall": LEAN / "Ell5ActiveComponentBankHall.lean",
    "noIncidence": LEAN / "AggregateLedgerNoIncidenceCounterexample.lean",
    "scoped": LEAN / "Gamma/ActiveScopedMinimumExchange.lean",
    "checkedC5Base": LEAN / "Gamma/CheckedC5BaseTransfer.lean",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def main() -> None:
    txt = {k: p.read_text(encoding="utf-8") for k, p in FILES.items()}
    cap = block(txt["global"], "inductive CapKind", "deriving DecidableEq")
    tags = re.findall(r"^\s*\|\s*([A-Za-z0-9_]+)\s*$", cap, re.MULTILINE)
    assert tags == ["door", "vertexSlack", "c5Base", "prune"], tags

    package = block(txt["global"], "structure FullBankGlobalPackage", "namespace FullBankGlobalPackage")
    checked = block(txt["global"], "structure Checked", "theorem localSurplus_le_localDemand")
    package_fields = re.findall(r"^\s{2}([A-Za-z0-9_]+)\s*:", package, re.MULTILINE)
    checked_fields = re.findall(r"^\s{2}([A-Za-z0-9_]+)\s*:", checked, re.MULTILINE)
    assert not any(name.lower() in {"inc", "incidence", "legal"} for name in package_fields)
    assert not any(name.lower() in {"inc", "incidence", "legal"} for name in checked_fields)
    assert "no_double_spend" in checked and "no_cross_component_spend" in checked
    assert "token_source_unique" in checked

    assert "Connecting these typed tokens to the existing wall `Sink` type is a\nseparate adapter obligation" in txt["typed"]
    assert "legal edge-to-token incidence is still absent from this package" in txt["ports"]
    assert "checkedAggregatePackage_and_noHalfLayerRouting" in txt["noIncidence"]
    assert "remaining open theorem `Ell5FullBankRelaxedCover_exists`" in txt["interface"]
    assert "structure FullBankRelaxedCoverCert" in txt["interface"]
    assert "hqinc" in txt["interface"]
    assert "ActiveComponentBankHall" in txt["activeHall"]
    assert "blueb G c T.sourceX T.owner = true" in txt["checkedC5Base"]
    assert "blueb G c T.sourceY T.owner = true" in txt["checkedC5Base"]
    assert "dM G c T.switch + 2 <= dB G c T.switch" in txt["checkedC5Base"]

    def rg_definition(symbol: str, heads: str) -> bool:
        pattern = rf"\b(?:{heads})\s+{symbol}\b"
        proc = subprocess.run(
            ["rg", "-n", "-g", "*.lean", pattern, str(LEAN)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        if proc.returncode not in (0, 1):
            raise RuntimeError(proc.stderr)
        return proc.returncode == 0

    definitions = {
        "CheckedTransferMatching": rg_definition(
            "CheckedTransferMatching", "def|structure|abbrev|inductive"),
        "CheckedPruneStep": rg_definition(
            "CheckedPruneStep", "def|structure|abbrev|inductive"),
        "Ell5FullBankRelaxedCover_exists": rg_definition(
            "Ell5FullBankRelaxedCover_exists", "def|theorem|lemma"),
    }
    assert definitions == {
        "CheckedTransferMatching": False,
        "CheckedPruneStep": False,
        "Ell5FullBankRelaxedCover_exists": False,
    }, definitions

    result = {
        "capKinds": tags,
        "definitionsPresent": definitions,
        "aggregatePackageHasPortIncidenceField": False,
        "aggregatePackageFields": package_fields,
        "aggregateCheckedFields": checked_fields,
        "typedSinkAdapterStatus": "separate obligation",
        "doorPortPackageStatus": "finite capacities only; legal incidence absent",
        "compiledLogicalSeparation": "checkedAggregatePackage_and_noHalfLayerRouting",
        "checkedC5BaseTerminalPresent": True,
        "verdict": (
            "CheckedC5BaseTransfer is a concrete common-blue terminal and can be audited on R29. "
            "No current production definition determines prune or constructs the complete FullBank provider."
        ),
        "sha256": {k: sha(p) for k, p in FILES.items()},
    }
    path = OUT / "interface_audit_result.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
