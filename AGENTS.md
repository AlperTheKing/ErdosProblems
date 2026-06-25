# Erdős Program — Execution & Reporting Protocol (solo)
(The registered /goal defines mission, novelty gate, dead-end protocol,
compute policy, and success. This file defines execution.)

## LOOP (repeat until the GOAL success condition is met; never idle, never simulate activity)
1. SELECT: most tractable open erdosproblems.com candidate with a concrete
   attack surface, excluding the Known statuses listed in the goal.
   One line: problem #, why tractable.
2. GATE: run the novelty gate. Fail -> log "DEAD: <citation>", go to 1.
3. PLAN: minimal lemma tree; identify the single highest-leverage open lemma
   (the frontier).
4. ATTACK: computation FIRST — counterexample search and small-case
   verification (use at most 64 CPU workers / RTX 5090, and at most 50%
   of 384 GB RAM, about 192 GB) before proof effort;
   then proof work on the frontier lemma.
5. VERIFY: referee pass + numeric/computational check where applicable +
   Lean 4 for key lemmas when feasible (no native_decide).
6. CHECK: verifiable new fact this cycle? Yes -> stall=0, go to 7.
   No -> stall+1. At stall=3 -> Dead-end protocol: DEAD -> log obstruction,
   go to 1; ALIVE -> execute the named experiment, continue at 4.
   No other exit, no time limit.
7. DECIDE: result complete? Re-run the novelty gate. Still novel -> write up
   + prior-art comparison -> PR -> STOP. Otherwise -> go to 4.

## Reporting Protocol (append-only to E:\Projects\ErdosProblems\PROGRESS_CODEX.md)
Before each major action:
`[ISO-8601] > <PHASE> | NEXT: <concrete action and objective, one sentence>`
After each major action:
`[ISO-8601] OK/FAIL <PHASE> | DID: <what executed> | RESULT: <verifiable: file path / lemma name / compiler error / number / citation> | D: <status change or "none">`

Major action =
- any phase transition in the LOOP (state old -> new explicitly)
- starting or finishing a Lean 4 build / proof attempt (name the lemma)
- launching any computation or search (include exact parameters)
- abandoning an approach (state the single falsifying fact that killed it)

Rules:
1. Report ACTIONS and OUTCOMES only — facts, not reflections.
2. RESULT must be independently verifiable. The words "progress",
   "promising", "almost", "good news" are banned in RESULT.
3. If a step produced nothing, write `RESULT: nothing`.
4. One line per event, <=200 chars. Append-only — never overwrite or
   summarize past entries. No headers, no recaps, no closing summaries.
5. These lines are in addition to doing the work, never a substitute for it.
   A protocol line claiming an action that did not occur is a critical failure.
