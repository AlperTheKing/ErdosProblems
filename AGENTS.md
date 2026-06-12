# CODEX — Erdős Program: LOOP & Reporting Protocol
(The registered /goal defines mission, novelty gate, dead-end protocol,
coordination, and success. This file defines execution.)

## LOOP (repeat until the GOAL success condition is met; never idle, never simulate activity)
1. SELECT: most tractable open erdosproblems.com candidate with a concrete
   attack surface, excluding Known statuses and active CLAUDE claims.
   Append CODEX CLAIM to CLAIMS.md.
2. GATE: run the novelty gate. Fail -> RELEASE DEAD with citation, go to 1.
3. PLAN: minimal lemma tree; identify the single highest-leverage open lemma
   (the frontier).
4. ATTACK: computation FIRST — counterexample search and small-case
   verification (<=32 CPU workers) before proof effort; then proof work on
   the frontier lemma.
5. VERIFY: referee pass + numeric/computational check where applicable +
   Lean 4 for key lemmas when feasible (no native_decide).
6. CHECK: verifiable new fact this cycle? Yes -> stall=0, go to 7.
   No -> stall+1. At stall=3 -> Dead-end protocol: DEAD -> RELEASE, go to 1;
   ALIVE -> execute the named experiment, continue at 4. No other exit,
   no time limit.
7. DECIDE: result complete? Re-run the novelty gate. Still novel -> write up
   + prior-art comparison -> PR -> STOP. Otherwise -> go to 4.

## Reporting Protocol (append-only to E:\Projects\ErdosProblems\PROGRESS_CODEX.md)
Before each major action:
`[ISO-8601] > <PHASE> | NEXT: <concrete action and objective, one sentence>`
After:
`[ISO-8601] OK/FAIL <PHASE> | DID: <what executed> | RESULT: <verifiable: file path / lemma name / error / number / citation> | D: <status change or "none">`

Major action = phase transition; Lean build or proof attempt; any computation
launch (with exact parameters); abandoning an approach (state the falsifying
fact).

Rules: actions and outcomes only. The words "progress", "promising", "almost"
are banned in RESULT. If a step produced nothing, write `RESULT: nothing`.
One line per event, <=200 chars. Append-only — never overwrite or summarize
past entries. A protocol line claiming an action that did not occur is a
critical failure.
