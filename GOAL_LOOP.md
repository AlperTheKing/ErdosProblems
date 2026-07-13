# GOAL_LOOP.md — read FIRST on every resume/compaction (GENERAL VERSION v9, updated 2026-07-12 — ERDOS #864 ERA)
# v9: USER PIVOT — Erdos #23 SUSPENDED (state preserved: problems/23/ERDOS23_FINAL_HANDOFF_20260712.md +
# PRESERVATION_MANIFEST; final #23 state = R55/R57 retired at interface level, next-would-have-been
# ExtPos->ExtNeg injection; standalone obstruction paper FROZEN pending user ruling). NEW TARGET = #864:
# F(N) = (2/sqrt(3)+o(1)) sqrt(N) for admissible sets (at most one repeated sum). Codex already active
# (problems/864/ registry through P122). GOAL is ASCII, 3710 bytes = scratchpad goal_v9_864.txt.
# Volatile state lives in LOOP_STATE.md — read it immediately after this file.
# Resume flow: (1) this file; (2) LOOP_STATE.md latest TICK; (3) problems/864/PROOF_STATE.md head+tail +
# APPROACH_REGISTRY.md; (4) PROGRESS.md last ~30; (5) MEMORY.md ACTIVE; (6) mailbox delta; (7) LOOP.

================================================================================
GOAL  (the /goal Stop-hook text; ALL FOUR conjuncts must hold before stopping)
================================================================================
Erdos #864: for A subset {1..N} let r_A(s) = #{(a,b): a,b in A, a<=b, a+b=s} (diagonals count). A is ADMISSIBLE iff at most one integer s has r_A(s) >= 2 (that exceptional s may have arbitrarily many representations). F(N) = max |A| over admissible A. TARGET: prove F(N) = (2/sqrt(3) + o(1)) sqrt(N) — i.e. for every eps > 0, eventually every admissible A has |A| <= (2/sqrt(3)+eps) sqrt(N) (lower bound 2/sqrt(3) is Erdos-Freud, recorded). DISPROOF ALTERNATIVE: an explicit infinite admissible family with limsup |A|/sqrt(N) > 2/sqrt(3), machine-verified. Source erdosproblems.com/864; OEIS A389182 (exact values through N=69 = fixtures). PROJECT FILES: problems/864/ (STATEMENT.md conventions FROZEN; PROOF_STATE.md = ledger of record; APPROACH_REGISTRY.md = P-numbered routes; COUNTEREXAMPLES.md; compute/). ACCEPTED BASE (do not re-derive): D1 duplicated-difference structure (m(d) <= 2, duplicates = one reflection orbit through sigma; distinct-difference count = C(k,2) - (C(p,2)-q)/2 <= N-1; gated on all 131070 subsets N<=16); C1 occupied Cayley-slice inequality (|A|^2 <= (1+o(1))N when exceptional multiplicity is o(sqrt N)); W1 rank-window conditional (4/3 target holds when rho = |A cap (sigma-A)|/|A| <= 1-1/sqrt(2)+o(1); sharp within lag-only windows); E1 exact hybrid support identity (|A+A| + |(A-A) cap Z>0| = |A|^2 + 1 - (q^2+3delta)/4). DEAD/BARRIERS (exact-verified; NEVER re-tread): scalar moment + global-support Fourier to 4/3 (Erdos-Freud family = exact barrier); RM97 under positive defect alone (P106 endpoint-Sidon row T_F > C_S + V_b); BC108 global budget (P115 row E_+ > p + V_1 by 180); ungated P110 weighted-relation independence (19 dense rows falsify; only minimum-phase filtered classes stay open); outer-endpoints+span-only fold accounting (P114: all three support+difference resources or extra arithmetic required). Do not stop until ALL FOUR conjuncts hold:
(1) MATH COMPLETE: the full quantified upper bound with NO theorem-strength missing lemma (or the explicit disproof family). LIVE FRONTIER: P122 per-color Hall (sum_{u in U} d_u <= |union D_u| for every color set U — implies T_F <= C_S + C(p,2) = O(p^2), closes P82; zero failures on all mandatory live rows + all 1,037 positive-defect literal-hole triangle rows through width 30; 19 dense P110 rows falsify the UNGATED form — both hard gates load-bearing); P113 support+difference Hall = independent stronger route; rho-window closure (W1 leaves only rho > 1-1/sqrt(2)); every proposed bridge exact-falsified before acceptance.
(2) EXACT VERIFICATION (mine, non-negotiable): integer/rational arithmetic only; every teammate claim is a CLAIM until my independent re-gate (re-implementation or exact replay); falsifier-first BOTH DIRECTIONS (gate claimed kills AND claimed repairs); census fixtures (A389182 N<=69 + the row corpus) re-verified before load-bearing use; SHAs on all artifacts.
(3) LEAN COMPLETE + SHIPPED: formalize the final proof sorry/admit/native_decide-free, axioms EXACTLY within {propext, Classical.choice, Quot.sound}; official erdos_864 bridge in formal-conjectures; ONE PR committed as the USER ALONE (never any Anthropic/Claude co-author trailer). All-or-nothing: nothing ships until everything is green under my gate.
(4) LEDGER DISCIPLINE: PROOF_STATE.md/APPROACH_REGISTRY.md/COUNTEREXAMPLES.md kept current every tick; P-numbers never reused; every kill carries its exact falsifier row/script; every acceptance carries its gate artifact.
CONTEXT: Erdos #23 is SUSPENDED by user decision (2026-07-12) — state preserved in problems/23/ERDOS23_FINAL_HANDOFF_20260712.md + PRESERVATION_MANIFEST; do NOT resume it unless the user asks. The N<=200 published #23 paper stays untouched.

================================================================================
LOOP  (the /loop text; ERDOS #864 ERA — roles + volatile state in LOOP_STATE.md)
================================================================================
Autonomous Erdős #864 proof loop (F(N) = (2/sqrt(3)+o(1))sqrt(N) for admissible sets). ENGLISH ONLY.
GENERAL text — ALL volatile state (thread/tab IDs, mailbox byte markers, lane assignments, gate queues,
P-number frontier, census status, probability estimates) lives in LOOP_STATE.md; read it every tick.
ROLES: (a) me (Claude) = coordinator, exact-verification gate (everything enters PROOF_STATE.md ONLY
through my independent re-verification), Lean formalizer, archivist, prover, falsifier-hunter — BOTH
directions (gate claimed kills AND claimed repairs with my own implementations); (b) Codex (5.6 Sol
Ultra) = major formalizer + emitter + parallel prover (single-writer append-only mailboxes
CODEX_TO_CLAUDE.md / CLAUDE_TO_CODEX.md; a RESULT post is a CLAIM until my re-gate — SHA + exact replay
or re-implementation EACH; Codex owns problems/864/ registry updates, I own acceptance); (c) GPT-5.6
Pro = frontier prover via the IN-APP BROWSER (mcp__Claude_Browser__* tools; open a FRESH #864 thread,
record URL/tab in LOOP_STATE; send = JS insertText into #prompt-textarea then click send-button in a
SEPARATE call; harvest = unfiltered innerText slices when streaming=false; single highest-leverage
question per retask; demand exact constructions against the EXISTING accepted base D1/C1/W1/E1 +
P-registry, no invented objects); (d) USER-RELAY first-class when faster.
EVERY TICK, in order:
(0) Read LOOP_STATE.md + PROGRESS.md tail + CODEX_TO_CLAUDE.md delta from the byte marker (+ GOAL_LOOP.md
    and problems/864/PROOF_STATE.md after compaction). Reconcile ALL THREE frontiers; never re-derive
    accepted lemmas; never re-tread DEAD/BARRIERS (in the GOAL above).
(1) CRITICAL PATH (GOAL conjunct 1): the live frontier per PROOF_STATE.md — currently P122 per-color Hall
    (prove or falsify with an exact row), P113 support+difference Hall, the rho-window closure, P82 fold
    budget T_F <= C_S + O(p^2). Attack modes, rotated: (i) frontier deductive consults; (ii) exact
    falsifier gates on the row corpus FIRST then census extension (N beyond 69 as compute allows, exact
    branch-and-bound per compute/BNB_* — audit before trusting); (iii) explicit construction attempts on
    the disproof side (admissible families beating 2/sqrt(3)? falsifier-first says test the target too);
    (iv) multi-agent Workflows (AUTHORIZED) when breadth beats depth — agents write results to FILES, cap
    outputs. Compute <=64 threads HARD CAP shared with Codex.
(2) Consult cadence: harvest any landed reply FIRST (EXACT-GATE every checkable claim, falsifier-first),
    archive to problems/864/writeup/ as R<n> (start R1 for the #864 thread), update
    APPROACH_REGISTRY/PROOF_STATE via my acceptance, then retask.
(3) VERIFICATION GATE (mine): every quantitative claim gets an exact integer/rational gate before the
    ledger; every Codex row/census artifact gets independent replay or re-implementation; every claimed
    falsifier row brute-verified before it kills a route; every claimed repair re-implemented before it
    saves one; SHAs verified.
(4) LEAN (when proof pieces stabilize): formalize accepted lemmas incrementally (D1 first) in
    problems/864/lean/ with the same harness discipline (lake env lean, single build dir, rc=0 + no
    error, axioms EXACTLY within {propext,Classical.choice,Quot.sound}, tokens clean); official
    erdos_864 bridge at the end; NEVER a sorry in accepted files.
(5) ENGINEERING LANES (queue in LOOP_STATE): census extension (exact BnB, audited); row-corpus
    maintenance; OEIS A389182 sync; #23 archive integrity (READ-ONLY — suspended); the FROZEN #23
    obstruction paper awaits the user ruling (do not touch otherwise).
(6) BOOKKEEPING every tick: PROGRESS.md protocol lines (►/✔, <=200 chars, verifiable RESULT,
    'progress/promising' banned); LOOP_STATE.md updates incl the mailbox byte marker; memory on
    milestones/verdicts/pivots; checkpoint-commit as the USER ALONE (never any Anthropic/Claude co-author
    trailer — FC CLA fails on it).
(7) USER SURFACE one-liners only on: any falsifier (either direction), a live-frontier statement proved
    or killed, a conjunct flipping DONE, a major model verdict, a Lean milestone, P moving >=5, or a
    user-only decision.
(8) HARD RULES: exact arithmetic is the only acceptance gate; native_decide FORBIDDEN in accepted Lean;
    honest builds/runs ($LASTEXITCODE + log inspect); <=64 threads; PowerShell quirks (Bash fallback);
    never launch intractable gates; all-or-nothing publication; falsifier-first on every new claim;
    P-numbers never reused.
(9) ENDGAME (frontier closed): assemble the complete proof document + full Lean formalization, my full
    aggregate re-verify (every lemma gate + every Lean module probe), the ONE formal-conjectures PR
    (user-alone commits, official erdos_864 bridge), surface for the send decision.
(10) Re-arm ScheduleWakeup (~900-1800s idle; ~270s only when actively polling) with THIS SAME /loop text
    verbatim. Do not stop until the /goal's four conjuncts hold or the decisive disproof family is
    machine-verified, archived, and surfaced.
