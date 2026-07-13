"""Static referee audit of the production FullBank Lean surface."""
from hashlib import sha256
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
FILES = {
 "ledger": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",
 "sinks": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean",
 "typed": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean"}
needles = {
 "ledger": ["| c5Base", "| prune", "c5BaseCapQ : ℚ", "pruneCapQ : ℚ", "token_source_unique :", "no_double_spend :", "componentReserveIdentity :"],
 "sinks": ["legal edge-to-token incidence is still absent from this package", "do not assert a Hall condition"],
 "typed": ["source_injective : Function.Injective", "separate adapter obligation; no such adapter is assumed here"]}
for tag, path in FILES.items():
 raw = path.read_bytes(); source = raw.decode()
 assert not [s for s in needles[tag] if s not in source]
 print(f"{tag} sha256={sha256(raw).hexdigest()} bytes={len(raw)}")
all_text = "\n".join(p.read_text(encoding="utf-8") for p in FILES.values())
for absent in ("structure CheckedTransferMatching", "outsideAttachment", "sameFirst", "commonBad", "rowCompanion", "slotTransport"):
 assert absent not in all_text
print("PASS abstract c5Base/prune caps exist but no checked transfer relation")
print("PASS source-key injectivity is a provider field; legal sink incidence/adapter is absent")
