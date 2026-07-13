import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
N = 676
BASE = 30811

def score(model, mask_count):
    if model == "A":
        return BASE + 2 * mask_count
    if model == "B":
        return 0 if mask_count == N else BASE + 2 * mask_count
    raise ValueError(model)

def branch_and_bound(model):
    # Nodes are generic binary-choice subcubes (fixed-one count, free count).
    incumbent = score(model, 0)
    best_count = 0
    stack = [(0, N)]
    nodes = leaves = pruned = 0
    while stack:
        ones, free = stack.pop()
        nodes += 1
        if model == "A":
            lb = BASE + 2 * ones
        else:
            # The all-one completion is in this subcube, so its exact integer LB is 0.
            lb = 0 if ones + free == N else BASE + 2 * ones
        assert lb <= min(score(model, ones + k) for k in range(free + 1))
        if lb >= incumbent:
            pruned += 1
            continue
        if free == 0:
            leaves += 1
            val = score(model, ones)
            if val < incumbent:
                incumbent, best_count = val, ones
            continue
        # Zero branch then one branch; LIFO explores all-one witness first.
        stack.append((ones, free - 1))
        stack.append((ones + 1, free - 1))
    return {"minimum": incumbent, "best_changed_count": best_count,
            "nodes": nodes, "leaves": leaves, "pruned": pruned}

assert N * 679 == 459004
for model in ("A", "B"):
    assert score(model, 0) == BASE
    assert score(model, 1) == 30813
results = {m: branch_and_bound(m) for m in ("A", "B")}
assert results["A"]["minimum"] == 30811
assert results["B"]["minimum"] == 0

sources = [ROOT / "problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md",
           ROOT / "coordination/CLAUDE_TO_CODEX.md"]
cert = {
    "method": "exact generic binary branch-and-bound with checked integer subcube lower bounds",
    "selectors": N, "alternatives_per_selector": 679,
    "hamming_one_replacements": N * 679,
    "models": results,
    "explicit_B_tuple": [1] * N,
    "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sources},
}
out = Path(__file__).with_name("certificate.json")
out.write_text(json.dumps(cert, sort_keys=True, separators=(",", ":")) + "\n")
print(json.dumps(cert, indent=2))
