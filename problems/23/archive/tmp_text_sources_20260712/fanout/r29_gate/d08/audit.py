from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
SOURCES = [
    ROOT / "problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md",
    ROOT / "problems/23/writeup/WALL_ATTACK_R28_GPTPRO56.md",
]

def H(p):
    return sha256(p.read_bytes()).hexdigest()

# Exact orbit-compressed countermodels.  k is the number of changed selector rows.
# Both agree with S(0)=30811 and all 676*679=459004 Hamming-one moves having
# minimum 30813.  They differ only at the unreported multi-row interaction.
def model_a(k):
    assert 0 <= k <= 676
    return 30811 + 2*k, False

def model_b(k):
    assert 0 <= k <= 676
    return ((30811 + 2*k, False) if k < 676 else (0, True))

assert 676 * 679 == 459004
assert model_a(0) == model_b(0) == (30811, False)
assert model_a(1)[0] == model_b(1)[0] == 30813
assert min(model_a(k)[0] for k in range(677)) == 30811
assert min(model_b(k)[0] for k in range(677)) == 0

out = {
    "source_sha256": {str(p.relative_to(ROOT)).replace('\\\\','/'): H(p) for p in SOURCES},
    "archived_constraints": {"selectors": 676, "rows_each": 680,
        "nontrivial_hamming_one": 459004, "baseline": 30811,
        "hamming_one_min": 30813},
    "compressed_state": "k in {0,...,676}; permutation orbit of changed selectors",
    "model_a": {"minimum": 30811, "argmin_k": [0], "deactivates": False},
    "model_b": {"minimum": 0, "argmin_k": [676], "deactivates": True,
        "descending_tuple": "choose any fixed nonbaseline row for every selector"},
    "conclusion": "available archived constraints underdetermine global minimum and deactivation"
}
Path(__file__).with_name("certificate.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
