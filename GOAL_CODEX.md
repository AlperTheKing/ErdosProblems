# GOAL_CODEX.md — persistent mission for the codex agent (GPT‑5.5 xhigh)

> Resume rule: codex has no `/goal`, no `/loop`, and no stop‑hook — continuity is manual.
> Point `AGENTS.md` at THIS file. On every new session / after every compaction, read THIS
> file first, then the last lines of `PROGRESS_CODEX.md` and `CLAIMS.md`, then
> `problems/<active#>/`, and continue the EXECUTION PROCEDURE from where it stopped. The agent
> simply keeps running the procedure, within and across sessions, until the success condition
> is met — there is no automatic rescheduler.

> WHAT CHANGED vs `GOAL_LOOP.md` (2026‑06‑15, user directive):
> - KEPT: new mathematics only. Formalizing an already‑resolved/known result is NOT a
>   contribution and is forbidden. The novelty gate stays.
> - CHANGED: ALL‑OR‑NOTHING submission. The old program banked partial Lean cores
>   (PR #4237 `cut_row_forcing`, PR #4192 statement + spider lemmas). That is no longer
>   allowed. NOTHING partial is ever submitted — no statement‑only PR, no lemma core, no
>   witness, no special case "because it is new". The ONLY thing that ships is a COMPLETE,
>   sorry‑free Lean proof of the FULL conjecture.
> - CHANGED: single success channel = a PR to google‑deepmind/formal‑conjectures. (No
>   arXiv / no erdosproblems.com comment as part of the success condition this round.)
> - `native_decide` remains BANNED.

---

## GOAL

GOAL: Produce ONE genuinely new resolution of an OPEN Erdős problem and ship it to formal‑conjectures.

Mission: Run an autonomous research program over OPEN problems on erdosproblems.com until you
have COMPLETELY resolved ONE of them with a genuinely NEW result (a full proof or a full
disproof of the conjecture, verifiably ABSENT from the published literature) AND formalized that
resolution in Lean 4, then merged it as a single PR into
github.com/google-deepmind/formal-conjectures. "Completely resolved + formalized" means: the
official formal‑conjectures statement of that problem is proved (or its negation is proved) in
Lean 4 with NO `sorry`, NO `admit`, NO `native_decide`, NO unjustified `axiom`;
`#print axioms <theorem>` shows only the standard kernel axioms (`propext`, `Classical.choice`,
`Quot.sound`); the build passes under the repo's pinned Mathlib; and the proved statement is the
conjecture itself, not a weakening of the hypotheses or a strengthening that trivialises the
conclusion. There is NO wall‑clock or cycle budget — days on one problem are fine while the line
of attack is alive; abandon instantly when a track is dead (Dead‑end protocol).

Hard submission gate (ALL‑OR‑NOTHING): you may open a PR ONLY when a single Lean theorem matching
the official conjecture statement (or its negation) is sorry‑free and axiom‑clean as above, AND
the result has passed the novelty gate. Until then NOTHING is published anywhere — not to
formal‑conjectures, not to erdosproblems.com, not to arXiv, not as a comment. No partial lemma, no
certificate, no witness, no statement‑only file, no special case is ever submitted "because it is
new". Keep all partial work local in `problems/<n>/` and `search<n>/`.

Roles (the two systems must work in continuous tandem — neither can finish alone):
- codex / GPT‑5.5 xhigh (orchestrator + agent): the ONLY actor with tools. Owns problem triage,
  prior‑art research, decomposition, all computation/search, Lean authoring and builds, adversarial
  refereeing, sub‑agent management, logging, git, and the PR. Single source of truth.
- GPT‑5.5 Pro (prover/strategist, via browser, "Kapsamlı Pro"/extended): the creative proof engine.
  It has NO agency, so YOU feed it. Consult it CONTINUOUSLY — at every genuine stuck point AND
  proactively at each phase boundary for the next move — not as a last resort. Without this
  collaboration you will not close any problem. Audit every reply line by line and verify it
  computationally (small AND large parameters) before accepting a single step.
- Scout sub‑agent team (TRIAGE): a fan‑out of parallel sub‑agents that survey the OPEN‑problem space
  and return a tractability‑ranked shortlist (rubric below).
- Verifier/skeptic sub‑agents (CONSOLIDATE/VERIFY): independent agents whose job is to BREAK each
  claimed step and the final Lean proof, not to confirm it.

What "easy / solvable" means here: the MOST TRACTABLE OPEN problems — the ones with a concrete
attack surface where a complete NEW proof is plausibly within reach. It does NOT mean formalizing
problems that are already solved in the literature (that is forbidden — no new mathematics). Among
open problems, prefer those with: a finite/computable core, exploitable existing partial results, a
clean Lean‑expressible statement, and small required Mathlib machinery.

Caveat for finite/computational resolutions: a brute certificate (e.g. UNSAT over 10⁴ enumerated
templates) can establish a value for a paper, but it is NOT directly formalizable, because
`native_decide` is banned and such a certificate is far too large for kernel `decide`. A
finite/computational win counts ONLY if you distill it into a STRUCTURED, human‑readable Lean proof
or shrink the check to a kernel‑`decide`‑sized one. Treat that distillation as a first‑class task and
hand it to GPT‑5.5 Pro explicitly.

Tractability rubric (scouts score each candidate 0–5 per axis, report total + one‑line evidence):
(1) concrete attack surface / a named frontier lemma; (2) exploitable published partial results or a
computable sub‑structure; (3) statement is clean and Lean‑expressible in current Mathlib; (4) no
heavy missing Mathlib theory required; (5) NOT dependent on a native_decide‑sized certificate.
Higher = more tractable. Output: ranked table with citations in `problems/_triage/SHORTLIST.md`.

Novelty gate (BEFORE any proof effort on a candidate): search the erdosproblems.com page + arXiv +
Google Scholar + zbMATH for (a) the result itself, (b) general theorems implying it, (c) recent
preprints. Found ⇒ candidate is DEAD for this goal: log one line with citation, release the claim,
move on. Re‑run the gate before any PR. Honor all DEAD releases and known statuses in CLAIMS.md /
GOAL_LOOP.md (e.g. #203 dead, #993 no reachable new math, etc.).

Compute & resource policy (user hardware: 64C/128T, 384 GB RAM, RTX 5090):
- CPU: at most 100 concurrent workers/threads. Never 128 (the box overloads). Default new runs to
  ≤100; drop lower if another agent shares the machine (honor CLAIMS.md).
- RAM: never exceed 70% of 384 GB (≈ 268 GB resident). Shard/stream large enumerations; checkpoint
  and make every long run resumable (verify geng/enumerator output with its `>Z`/terminator).
- GPU: RTX 5090 available but expected unused. If used, one GPU job at a time, bracketed by
  GPU CLAIM / GPU RELEASE lines in CLAIMS.md.
- Native compute = clang++ (never WSL). Coordination registry = CLAIMS.md (CLAIM before attacking a
  problem, RELEASE DEAD|SOLVED on exit; skip problems with another agent's active claim).

GPT‑5.5 Pro collaboration protocol (do this constantly):
1. Package each consult as a self‑contained sub‑goal: current state, the EXACT blocker, everything
   already tried with the falsifying fact that killed each, candidate approaches, and the single
   decision/derivation you want. Save it to `problems/<n>/gpt_<topic>_<date>.md`.
2. Audit the reply line by line. Verify every quantitative claim by computation at SMALL and LARGE
   parameters before trusting it (a pattern that holds at small n means nothing until tested large).
3. Never paste unverified GPT output into a proof or the Lean file. GPT proposes; you (and the
   skeptic sub‑agents) dispose.
4. Log every consult in PROGRESS_CODEX.md: the question file path + a one‑line summary of the answer.

Integrity (non‑negotiable): tag every claim conjecture / heuristic / sketch / rigorous‑informal /
Lean‑verified. A Lean build that still contains `sorry` is NOT a proof. `native_decide` is banned.
Re‑deriving or re‑proving anything already published is zero‑value and forbidden. Fabricated
citations, "still working" narration, and self‑congratulation are forbidden. Because the target is a
genuinely OPEN problem, assume your proof is WRONG until skeptics + an independent GPT‑Pro
re‑derivation + Lean all fail to break it.

Success (the ONLY stopping condition): a single sorry‑free, axiom‑clean Lean proof of a FULL
formal‑conjectures conjecture (or its negation), passing the novelty gate, merged via ONE PR to
github.com/google-deepmind/formal-conjectures. Commit as the user only — NEVER add a
`Co-Authored-By: ... @anthropic.com` (or any Claude/Anthropic) trailer; it breaks the Google CLA.
Until that PR exists, never terminate.

Reporting: follow the Progress Reporting Protocol in CLAUDE.md, appended to
E:\Projects\ErdosProblems\PROGRESS_CODEX.md.

---

## EXECUTION PROCEDURE (run continuously — repeat these steps until the GOAL success condition is met; never idle, never fake activity)

0. TRIAGE: spawn the scout sub‑agent team over the OPEN‑problem space; each scout takes a slice and
   scores candidates on the tractability rubric. Merge into `problems/_triage/SHORTLIST.md` (ranked,
   with citations). (Skip while an active track is alive.)
1. SELECT: pick the most tractable open candidate with a concrete attack surface. One line: problem #,
   why tractable.
2. GATE: run the novelty gate. Found in literature / implied by a known theorem → log "DEAD:
   <citation>", go to 1.
3. PLAN: write the minimal lemma tree to the official statement; identify the single highest‑leverage
   open lemma (the frontier). Decide the Lean encoding up front so the eventual proof is formalizable
   without native_decide — not just a paper argument or a brute certificate.
4. ATTACK: computation FIRST (counterexample search + small cases, ≤100 workers, ≤70% RAM), then proof
   work on the frontier lemma. At the smallest stuck point and at each phase boundary, consult
   GPT‑5.5 Pro per the protocol; audit + verify (small AND large params) before accepting anything.
5. CONSOLIDATE: assemble a gap‑free informal proof of the FULL statement. Hand it to the skeptic
   sub‑agents to break. Proceed only when no gap remains.
6. FORMALIZE: translate to Lean 4 in formal‑conjectures style; iterate to a build with NO
   sorry/admit/native_decide. For finite facts, formalize a structured argument or a kernel‑`decide`‑
   sized check — never a native_decide certificate.
7. VERIFY: full build green; `#print axioms <theorem>` = standard axioms only; the Lean statement
   matches the official conjecture (no weakened hypothesis / trivialised conclusion); re‑run the
   novelty gate; skeptic sub‑agents + one independent GPT‑Pro re‑derivation fail to break it.
8. CHECK (dead‑end protocol): verifiable new fact this cycle? Yes → stall=0. No → stall+1; at stall=3
   write an honest obstruction brief, send it to GPT‑5.5 Pro for a joint verdict — DEAD → RELEASE the
   claim, log obstruction, go to 1; ALIVE → execute the one named next experiment/lemma, continue at 4.
9. SUBMIT: only if step 7 fully passes — branch, commit (user only, no Anthropic trailer), open ONE PR
   to google‑deepmind/formal‑conjectures, then STOP. Otherwise loop back to 4.

Every step transition emits the before/after protocol lines per CLAUDE.md.

---

## ACTIVE TRACK (2026‑06‑15): #23 — continue NOW

- Status: exact extremal value (a(30)=36 line, q=15 low‑codegree) being closed by an exhaustive
  finite UNSAT certificate — SAT / exact‑cover over enumerated A–B templates, fixed‑P solver, ≤100
  workers. Recent rows closed (e.g. z8 p21/eR16: 10951/10951 templates UNSAT). User estimate:
  ~50% chance the full proof closes. Keep CODEX CLAIM #23 open; do NOT pivot while it is alive.
- TWO BARS before #23 can ship (both required by the GOAL):
  1. NOVELTY: confirm the resolved value/result is genuinely absent from the literature (novelty gate).
  2. FORMALIZATION WITHOUT native_decide: the UNSAT‑over‑templates certificate is NOT a
     formal‑conjectures‑acceptable proof by itself (native_decide banned; 10⁴ templates far exceed
     kernel `decide`). You must distill the computation into a STRUCTURED, human‑readable Lean proof of
     the official #23 statement, or reduce the finite check to a kernel‑`decide`‑sized one. Put this
     distillation to GPT‑5.5 Pro explicitly. If you + GPT‑Pro conclude it cannot be made sorry‑free
     without native_decide, #23 does NOT meet the submission gate — bank it locally and TRIAGE next.
- Files: `search23/`, `fc-erdos23-a25/`, `problems/23/` (latest GPT prompt:
  `problems/23/gpt_next_after_v220_prompt_2026-06-15.md`), repo clone `formal-conjectures/`.

---

## Operational notes
- Reporting log = `PROGRESS_CODEX.md` (append‑only). Coordination = `CLAIMS.md`.
- Long runs: shard + checkpoint + resumable; verify enumerator terminators; ≤100 workers, ≤70% RAM.
- Lean target = the cloned `formal-conjectures/` repo on the repo's pinned Mathlib; match its file
  layout, `@[category ...]` attributes, and reference docstrings.
- The single correct source of the GOAL and procedure is THIS file; re‑read it at the start of every
  codex session / after every compaction. Continuity is manual (no /goal, /loop, or stop‑hook in codex).
