# R29 FullBank source audit common brief

Goal: audit the canonical N=2943 all-anchor R29 tuple. The active-scoped four-pattern matcher has score 23115 and hub shore A={0,1,2} with demand 19953, reach 19925, defect 28. This is not yet a FullBank failure.

Read the mission attachment, latest `coordination/CLAUDE_TO_CODEX.md`, R20/R23/R28/R29 writeups, `R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md`, `WIRING_SPECS_GPTPRO.md`, and relevant Lean APIs. Reuse the deterministic builder in `tmp/fanout/r29_gate/lead/r29_lead_gate.py` and the owner-Hall replay in `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py`.

Rules: exact integer/Fraction arithmetic only; no float evidence; no sorry/admit/native_decide. Do not invent token kinds: allowed FullBank kinds are Door, vertexSlack, c5Base, prune. Distinguish FreeHalf matching units from actual FullBank port/capacity units. Prove no-double-spend and source uniqueness for any absorber. If no absorber exists in your audited universe, emit an exact finite dual/Farkas certificate. Write only in your assigned subdirectory under `tmp/fanout/r29_fullbank/E_source_search`; do not edit coordination/progress or any existing file. Include exact commands, counts, SHA-256 hashes, and the smallest theorem or falsifier statement. Do not spawn descendants.
