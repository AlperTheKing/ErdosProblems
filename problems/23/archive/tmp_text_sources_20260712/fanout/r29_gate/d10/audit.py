from hashlib import sha256
from pathlib import Path
import json

root = Path(__file__).resolve().parents[4]
archive = root / "problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md"
mailbox = root / "coordination/CLAUDE_TO_CODEX.md"
state = root / "LOOP_STATE.md"

checks = {
    "maxcut_class_sum": 4110 + 2704 + 12 + 207 + 6,
    "uncut_edges_if_partition_exhaustive": 8422 - 7039,
    "rigid_atom_sum": 676 + 28 + 3,
    "selector_total_rows": 676 * 680,
    "nontrivial_hamming_one_replacements": 676 * (680 - 1),
    "hall_demand_parts_inferred": 3 * 6651,
    "hall_reach_sum": 17325 + 2600,
    "hall_gap": 19953 - (17325 + 2600),
    "score_sum": 19953 + 52 * 200 + 458,
    "claimed_min_delta": 30813 - 30811,
    "active_component_complement": 2943 - 2775,
}

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

out = {
    "checks": checks,
    "hashes": {
        str(archive.relative_to(root)): digest(archive),
        str(mailbox.relative_to(root)): digest(mailbox),
        str(state.relative_to(root)): digest(state),
    },
    "claimed_sha_prefix_00186166_occurrences": [],
}
for p in (archive, mailbox, state):
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if "00186166" in line:
            out["claimed_sha_prefix_00186166_occurrences"].append(
                {"file": str(p.relative_to(root)), "line": i, "text": line.strip()}
            )

print(json.dumps(out, indent=2, sort_keys=True))
