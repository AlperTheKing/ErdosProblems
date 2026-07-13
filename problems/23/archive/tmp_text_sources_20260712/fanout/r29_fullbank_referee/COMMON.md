# Lead C R29 FullBank referee brief

Workspace: `E:\Projects\ErdosProblems`.

Mission: independently determine whether the exact 2,943-vertex R29 all-anchor
tuple's hub shore `{0,1,2}` remains deficient under the real production
`CheckedTransferMatching` / FullBank architecture, or which production source
class absorbs its 28-unit deficit.

Authoritative inputs you may read:

- active goal attachment at
  `C:\Users\a\.codex\attachments\3aa50e6d-e625-4228-a811-b3ced146f994\pasted-text-1.txt`;
- `GOAL_LOOP.md`;
- `problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md` (construction spec);
- `problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md` (claimed numbers only);
- production Lean definitions and archived R20/R23 design notes.

Independence rule: do NOT read or import any file under
`tmp/fanout/r29_fullbank*`, `tmp/fanout/r29_gate`,
`tmp/fanout/global_min_proof`, or
`problems/23/writeup/_codex_r29_fullbank_semantic_audit.py`. Do not import
Lead B scripts or JSON. Reconstruct from the archival R29 specification and
production definitions.

Exactness: integer/Fraction only. Floats are forbidden as theorem evidence.
Distinguish proved structural invariants from sampled checks. Never use
`sorry`, `admit`, or `native_decide`.

Repository safety: do not modify production files, mailboxes, progress logs,
or another lane. Write only in your assigned
`tmp/fanout/r29_fullbank_referee/child_XX/` directory. Include exact commands,
numbers, SHA256 hashes, and a final `REPORT.md`. Run every script you create.

Known claim to audit, not assume: all-anchor scoped score 23115; shore demand
19953; scoped reach 19925; defect 28; 707 rigid one-row families plus 676
selector families of size 680. The selector space has size `680^676`.

The production capacity kinds are `door`, `vertexSlack`, `c5Base`, and
`prune`. The auxiliary `ActiveScoped` relation uses only `FreeHalf` sources
with same-owner/row-companion-style eligibility and `ScopedReserved`; it is
not itself the complete FullBank package.

