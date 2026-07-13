from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
WALL = ROOT / "problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md"
LEAN = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean"

def H(p): return sha256(p.read_bytes()).hexdigest()

# Local collision delta for one ordered pair when P is replaced by Q.
# p,q are membership bits of that coordinate-pair in P,Q, and c is its old count.
def local_collision_delta(c, p, q):
    assert c >= p and p in (0, 1) and q in (0, 1)
    return max(c - p + q - 1, 0) - max(c - 1, 0)

# Exhaustively validate the symbolic piecewise formula over a domain wider than
# any one-row membership change requires.
table = []
for c in range(8):
    for p in (0, 1):
        if c < p: continue
        for q in (0, 1):
            d = local_collision_delta(c, p, q)
            expected = (1 if q and not p and c >= 1 else
                        -1 if p and not q and c >= 2 else 0)
            assert d == expected
            table.append([c, p, q, d])

# Exact diagonal criterion: adding a genuinely new vertex v creates score +2
# from (v,v) iff its old selected-row multiplicity is exactly one.
diagonal = []
for old_mult in range(8):
    delta_score = 2 * local_collision_delta(old_mult, 0, 1)
    assert (delta_score == 2) == (old_mult >= 1)
    diagonal.append([old_mult, delta_score])

needles = ["00186166", "459004", "30811", "30813"]
hits = {}
claim_candidates = [
    WALL,
    ROOT / "LOOP_STATE.md",
    ROOT / "coordination/CLAUDE_TO_CODEX.md",
    ROOT / "tmp/fanout/r29_gate/d06/aggregate_claim.json",
]
for p in claim_candidates:
    if not p.is_file():
        continue
    s = p.read_text(encoding="utf-8", errors="replace")
    got = [n for n in needles if n in s]
    if got:
        hits[p.relative_to(ROOT).as_posix()] = got

out = {
  "symbolic_formula": "sum_xy ([c_xy-p_xy+q_xy-1]_+ - [c_xy-1]_+)",
  "formula_cases": table,
  "diagonal_old_multiplicity_to_score_delta": diagonal,
  "required_instance_fields_absent": ["graph edges", "cut", "676x680 rows", "selected tuple"],
  "source_hits": hits,
  "sha256": {WALL.relative_to(ROOT).as_posix(): H(WALL), LEAN.relative_to(ROOT).as_posix(): H(LEAN)},
}
(HERE / "audit.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"formula_cases": len(table), "hits": hits, "sha256": out["sha256"]}, sort_keys=True))
