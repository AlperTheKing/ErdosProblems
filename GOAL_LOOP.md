# GOAL_LOOP.md — read FIRST on every resume/compaction (FINAL GENERAL VERSION, 2026-07-04)
# Volatile state lives in LOOP_STATE.md — read it immediately after this file.
# Resume flow: (1) this file; (2) LOOP_STATE.md; (3) PROGRESS.md last ~30 lines;
# (4) MEMORY.md ACTIVE block; (5) newest CODEX -> CLAUDE posts; (6) resume the LOOP below.

================================================================================
GOAL  (the /goal Stop-hook text; ALL FOUR conjuncts must hold before stopping)
================================================================================
Erdős #23 δ=0: prove that every triangle-free graph on N vertices satisfies β ≤ N²/25, via the
GERSH program (per-bad-edge row bound ROWSUM(f) ≤ N + η on B-connected Γ-minimal maximum cuts,
η = (N²−25m)/25; chain GERSH ⟹ Γ ≤ N² ⟹ β ≤ N²/25). Do not stop until ALL FOUR hold:
(1) Branch A (L=5) is proven rigorously: every node of its ledger (Bank0 B0-B10; ODL O0-O21 as
    archived in the master ledger, WRITEUP_REDTEAM_GPTPRO.md) is PROVEN as a Lean-ready lemma,
    or CERTIFIED as a finite machine artifact verified by its named checker, or ROUTED to a
    certified source — with zero unrouted or hand-waved cases.
(2) Branch B (L>5) is proven rigorously to the same standard (Banked-UPO chain with the repaired
    single-spend CombinedHBD ledger).
(3) Every lemma and certificate is exact-verified (rational Fraction arithmetic only) on the full
    battery: census N≤11 (never N≤10-only), two-lane L≥12 + p198, C7/C9/C11, W1-W4, glued cactus,
    klane, blowups, heuristic cuts certified TRUE max — with census results used as validation
    annotations only, never as proof ingredients.
(4) The whole proof is formalized sorry-free in Lean 4 (native_decide forbidden) and shipped as
    ONE formal-conjectures PR, committed as the user alone (never any Anthropic/Claude co-author
    trailer). All-or-nothing: nothing ships until everything is done.
If a decisive obstruction is found (falsifier, refuted lemma, dead architecture), document it in
PROGRESS.md + memory, surface it to the user, and pivot per GPT-Pro guidance — the goal only
completes on full success or a documented decisive obstruction accepted by the user.

================================================================================
LOOP  (the /loop text; general — never needs updating; state lives in LOOP_STATE.md)
================================================================================
Autonomous Erdős #23 δ=0 proof loop. ENGLISH ONLY. Roles: GPT-Pro (two ChatGPT threads via Chrome
MCP) designs theorems and prose — NEVER let either thread idle; Codex (append-only mailboxes
coordination/CODEX_TO_CLAUDE.md ↔ CLAUDE_TO_CODEX.md) grinds certificates and big compute; I am
the exact-verification gate, Lean formalizer, archivist, and coordinator. EVERY TICK, in order:
(0) Read E:\Projects\ErdosProblems\LOOP_STATE.md and the tail of PROGRESS.md — they hold ALL
    volatile state (mailbox byte marker, thread URLs/tab IDs, in-flight tasks, retask queues,
    extraction queue, Lean next-increment, ledger snapshot). Reconcile before acting.
(1) Check both GPT-Pro threads. Landed replies: extract (offset-stitch with ZZEQZZ/ZZPLUSZZ
    transform when needed), EXACT-GATE every checkable claim (sympy/Fraction; falsifier-first),
    archive verbatim-or-marked to the writeup tree, then IMMEDIATELY retask the thread from the
    retask queue or the master ledger's highest-leverage open node. Route risky designs to the
    other thread for independent adversarial review before trusting them.
(2) Scan the Codex mailbox from the stored marker. Reproduce every numeric claim exactly before
    acting on it; independently re-verify batch certificate artifacts at a ~1-in-10 sample plus
    EVERY repaired/hard row (SHA recompute + exact checker rerun from repo root), with a full
    aggregate re-verification at assembly; answer ASKs with rulings grounded in the archived
    specs; keep the bench aligned with the master ledger's critical paths; advance the marker in
    LOOP_STATE.md.
(3) Advance Lean per the checker blueprint order in LOOP_STATE.md. Write the increment, build in
    background — HONEST CAPTURE ONLY: PowerShell `cd formal-conjectures; lake env lean '<abs
    path>' *> log; "EXIT=$LASTEXITCODE"` with NO pipes between lean and the exit code; green =
    EXIT=0 AND empty log (inspect any nonzero log; grep new modules for sorry/admit/axiom/
    native_decide before recording green). Fix to zero errors (prefer zero warnings), never
    commit a sorry.
(4) Bookkeeping: append protocol lines to PROGRESS.md for every major action (►/✔, ≤200 chars,
    verifiable RESULT); update LOOP_STATE.md (markers, in-flight, queues); update memory on
    milestones/verdicts/pivots; checkpoint-commit accumulated batches as the user alone.
(5) USER SURFACE (one-liners) only on: a ledger node flipping to PROVEN/CERTIFIED, any falsifier
    or refutation, major solver verdicts, Lean module milestones, P(math)/P(Lean) moving ≥5
    points, or decisions only the user can make. Otherwise stay silent and work.
(6) Hard rules: EXACT rational arithmetic is the only acceptance gate; battery pass ≠ proof;
    native_decide FORBIDDEN (decide/rfl/norm_num/ring/nlinarith/positivity + reflective checkers
    only); commit as user alone, no Anthropic/Claude trailer; compute ≤64-100 threads; native
    clang++, never WSL; PowerShell syntax (temp-file + Get-Content -Raw for pipe-laden appends);
    graph6 via files, never inline; heuristic cuts must be certified TRUE max; browser quirks:
    tabs die on restart (find/recreate from URLs in LOOP_STATE.md), reply node is usually
    lastUserIdx+2 (+1 may be a thinking stub; single-node replies at +1), dead stub (len ≤10) ⟹
    compact regenerate nudge, send = insert then click #composer-submit-button (retry the click
    once if 'inserted only'), display cap ~1000 chars/result ⟹ paired calls + offset-stitch.
(7) Re-arm ScheduleWakeup (~1500s; shorter only when actively polling an external event) with
    THIS SAME /loop text verbatim. Do not stop until the /goal's four conjuncts hold or a
    decisive obstruction is documented and surfaced.
