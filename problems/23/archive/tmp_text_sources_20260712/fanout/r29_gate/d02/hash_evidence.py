import hashlib, json
from pathlib import Path

paths = [
    Path("problems/23/writeup/WALL_ATTACK_R28_GPTPRO56.md"),
    Path("problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md"),
    Path("coordination/CLAUDE_TO_CODEX.md"),
    Path("tmp/fanout/r29_gate/d03/gate_maxcut.py"),
]
result = {str(p): {"bytes": len(p.read_bytes()),
                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
          for p in paths}
print(json.dumps(result, sort_keys=True, indent=2))
