from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKBENCH = ROOT / "apn-gpt55-workbench" / "workbench"
sys.path.insert(0, str(WORKBENCH))

from apn_runner import call_openai  # noqa: E402


def main() -> int:
    here = Path(__file__).resolve().parent
    prompt = (here / "gpt_structural_query_2026-06-11.md").read_text(encoding="utf-8")
    out = here / "gpt_structural_answer_2026-06-11.md"

    model = os.environ.get("OPENAI_MODEL", "gpt-5.5")
    effort = os.environ.get("OPENAI_REASONING_EFFORT", "high")
    os.environ.setdefault("OPENAI_REQUEST_TIMEOUT", "1200")
    os.environ.setdefault("OPENAI_MAX_OUTPUT_TOKENS", "16000")

    answer = call_openai(prompt, model, effort, max_output_tokens=16000)
    out.write_text(answer + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
