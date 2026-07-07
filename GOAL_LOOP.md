# GOAL_LOOP.md — read FIRST on every resume/compaction (FINAL GENERAL VERSION, updated 2026-07-07 — SOLO MODE)
# Volatile state lives in LOOP_STATE.md — read it immediately after this file.
# Resume flow: (1) this file; (2) LOOP_STATE.md; (3) PROGRESS.md last ~30 lines;
# (4) MEMORY.md ACTIVE block; (5) newest CODEX->CLAUDE posts (only after Codex returns Thu); (6) resume the LOOP below.

================================================================================
GOAL  (the /goal Stop-hook text; ALL FOUR conjuncts must hold before stopping)
================================================================================
Erdős #23 δ=0: prove that every triangle-free graph on N vertices satisfies β = e − maxcut ≤ N²/25, via the
GERSH program (per-bad-edge row bound ROWSUM(f) ≤ N + η on B-connected Γ-minimal maximum cuts, η = (N²−25m)/25;
chain GERSH ⟹ Γ ≤ N² ⟹ β ≤ N²/25). Do not stop until ALL FOUR conjuncts hold simultaneously:
(1) Branch A (all rows L=5): the full O14 chart batch (108 rows) CERTIFIED as exact machine artifacts verified by
    the official source_solution_check (exact Fraction, 0 neg residual, 0 neg coeff), plus the coverage/assembly
    theorems (O14 structural chart cover = EQODL1Classifier ClassifierComplete + EQODL1CoverCert; Seed3 route tree)
    PROVEN as Lean-ready lemmas — zero hand-waves, no census-only coverage.
(2) Branch B (some row L>5) to the same standard: the Banked-UPO per-row bound + single-spend CombinedHBD ledger
    + CD telescope + 24-signature dictionary, each a separate PROVEN/CERTIFIED layer.
(3) Every lemma and certificate EXACT-verified (rational Fraction only, never float; battery pass = annotation,
    never proof): independent re-verification of ~1-in-10 batch rows + EVERY repaired/hard row, and a FULL
    aggregate re-verification from SHA-pinned manifests at assembly (tmp/claude_aggregate_reverify.py). Anti-fake-
    progress: research milestones (aggregation reserve, M6 providers, package construction) advance ONLY via
    compiled Lean lemmas or exact certificates, never via data volume or battery counts.
(4) The complete proof formalized sorry/admit/axiom-free in Lean 4 (axioms ⊆ {propext, Classical.choice,
    Quot.sound}; native_decide FORBIDDEN; honest builds EXIT=0 + empty log, no pipes), INCLUDING the bridge to the
    official formal-conjectures erdos_23 shape (∃ bipartite H ≤ G, deletion card ≤ n²), shipped as ONE
    formal-conjectures PR committed as the USER ALONE (never any Anthropic/Claude co-author trailer).
All-or-nothing: nothing ships until all four hold. Stop only when all four hold, OR a decisive mathematical
obstruction (exact rational falsifier of a needed chart row, or a refuted core lemma) is documented in PROGRESS.md
+ memory and surfaced to the user. The published N≤200 paper stays untouched.

--- CURRENT STATE SNAPSHOT (2026-07-07, keep updated in LOOP_STATE.md) ---
- Conjunct 1: 106/108 certs. PENDING = chart-8 k8/d8 (G1_UV_T), k8/d9 (G2_UZ_T); dim~31k, reconstruct exactly but
  land DEGENERATE (thousands neg coeffs); genuinely hard (Codex failed ~3h over many seeds). The 106 are SHA-
  integrity clean (tmp/claude_sha_integrity_106.py, 106/106). Coverage/assembly theorems UNBUILT.
- Conjunct 4 Lean: green + axiom-clean [propext,Classical.choice,Quot.sound] under my honest harness
  (tmp/claude_build_base_and_odlbridge.py, oleans tmp/claude_lean_o_base_v1): all 19 base modules 00-18,
  CertGraph.erdos23_fcForm_of_bipartization (official FC bridge), erdos23_delta0 (package-conditional top),
  GammaAggregation.gammaUpper_from_chargeCertV2, BranchB/ODLBridge.branchB_to_coreODLGoal, GammaChargeGraft
  .gammaBetaProvider_of_chargeCert (satisfiable aggregation route). BUT the whole chain is CONDITIONAL on the
  certificate PACKAGE, whose construction is largely UNBUILT. Honest P(Lean-complete unconditional) ~30-40%.
- THE aggregation crux (gap #1 = Γ≤N² = reserveResidual_nonneg = TerminalCageReserve): GPT-Pro reduced it to FOUR
  residual sublemmas R1-R4 (archived problems/23/writeup/GAP1_COMPLETED_SWITCH_ASSEMBLY_GPTPRO.md):
    R1 TerminalCage_K2Component_ExhaustiveAccounting; R2 PositiveDebtImpliesActiveTypeB;
    R3 CompletedSwitch_NoCrossGammaAccounting; R4 CompletedSwitch_DoorQuotientConnected.
  ESSENTIAL claim (a σ=0 positive-debt deficient-cap switch STRICTLY decreases Γ ⟹ Γ-minimality contradiction ⟹
  reserve≥0 ⟹ Γ≤N²) VALIDATED by my gate 42800/42800 (problems/23/writeup/_claude_multiatom_gammadrop_gate.py).
  GPT-Pro's quantitative bound Γ-drop ≥ (L+2)²=49 was FALSIFIED by the gate (measured global drop = 24); the
  correct sufficient lemma is STRICT DECREASE (dG<0). R1-R4 are all UNPROVEN — this is the top open node.
- Other open Lean package nodes: M6 good-cut existence provider (largest missing construction, uninhabited except
  Toy C5); Branch-B stack 21-26 (needs the Pure-UPO k=0 core; ODLBridge=27 done); O14 structural coverage module 29
  (design archived O14_STRUCTURAL_COVER_MODULE29_GPTPRO.md); the 108-gated O14 data modules 31-45.
- Conjunct 2 Branch-B: designed (BRANCH_B_LEAN_LAYERS_GPTPRO.md) but layers 21-26 not written.
- Conjunct 3: 106 SHA-clean; full aggregate re-verify runs at 108.
- NO falsifier documented. Four conjuncts all OPEN.

================================================================================
LOOP  (the /loop text; SOLO MODE 2026-07-07 — Codex out until Thu ~08:00, GPT-Pro via USER-RELAY)
================================================================================
Autonomous Erdős #23 δ=0 proof loop, SOLO MODE. ENGLISH ONLY. Roles now: (a) GPT-Pro MAIN thread
(https://chatgpt.com/c/6a4c8b1a-439c-83eb-8f49-427107d01d61) designs the theorems/proofs — reached via CHROME MCP
when connected, otherwise via USER-RELAY (I compose a message, user pastes it into GPT-Pro, user pastes the reply
back). If ToolSearch "claude-in-chrome" returns tools, drive it directly; else give the user the exact message to
relay. SIBLING thread is depleted. (b) CODEX is OUT until Thursday ~08:00 (usage limit) — do NOT expect mailbox
posts until then; I do any certificate compute SOLO with my own tools, capped ≤64 threads. (c) I am the exact-
verification gate, Lean formalizer, archivist, coordinator. EVERY TICK, in order:
(0) Read LOOP_STATE.md + PROGRESS.md tail (mailbox marker, thread state, in-flight bg tasks, Lean next-increment,
    gap#1/R1-R4 status, ledger). Reconcile before acting.
(1) GPT-Pro MAIN: if a reply landed (via Chrome or user-relay), extract fully, EXACT-GATE every checkable claim
    (sympy/Fraction, falsifier-first — GPT-Pro HAS made wrong proofs, e.g. the falsified 49-bound; NEVER accept a
    quantitative claim without gating it), archive verbatim-or-marked to problems/23/writeup/, then compose the
    NEXT retask (highest-leverage open node). CURRENT MAIN priority: nail the gap#1 completed-switch assembly —
    define U_C precisely, prove/gate R1-R4, target the STRICT-DECREASE lemma (dG<0), NOT the wrong 49-bound. Then
    M6 good-cut existence; Branch-B Pure-UPO k=0; module-29 structural coverage. If Chrome is down, hand the retask
    text to the user to relay.
(2) Certificates (SOLO): the only pending certs are chart-8 k8/d8, k8/d9. Codex is out, so EITHER (parked) leave
    them for Codex Thursday, OR (if the user asks) grind them solo — my tools: tmp/claude_modular_solve_parallel.py
    (48-worker CRT) + the HiGHS febc extraction with a fresh --highs-objective-seed (degenerate ⟹ retry a new
    seed), capped ≤48-56 workers. Verify ANY new cert exactly (official source_solution_check: exact_ok + 0 neg
    residual + 0 neg coeff), SHA-pin, update the ledger. At 108: run tmp/claude_aggregate_reverify.py (must be
    all_verified 108/108) then surface the 108-CERTIFIED milestone.
(3) Lean/gap#1 (THE critical path): exact-gate GPT-Pro's R1-R4 pieces where checkable (extend
    _claude_multiatom_gammadrop_gate.py / _defcap_component_mine.py; e.g. R2 = "every deficient cap has ≥1 type-B
    5/7 core"). Formalize proven pieces in Lean, honest form = a NAMED hypothesis/obligation isolated as the
    non-fake gate, NEVER a sorry. Buildable-now Lean: GammaChargeGraft + ODLBridge DONE; do NOT write structure-
    without-soundness (anti-fake-progress). Harness: reuse tmp/claude_build_base_and_odlbridge.py (run_lean = lake
    env lean --root=problems/23/lean --o=<olean>, cwd=formal-conjectures, LEAN_PATH=tmp/claude_lean_o_base_v1);
    green = rc=0 AND no 'error:'; grep sorry/admit/axiom/native_decide + #print axioms ⊆ {propext,Classical.choice,
    Quot.sound} before recording green. Do NOT launch intractable gates (glue 5,5,5 = 2^25).
(4) Bookkeeping: PROGRESS.md protocol lines (►/✔, ≤200 char, verifiable RESULT, 'progress/promising' banned);
    LOOP_STATE.md updates; memory on milestones/verdicts/pivots (correct stale memories); checkpoint-commit as the
    USER ALONE (no Anthropic/Claude trailer).
(5) USER SURFACE (one-liners) only on: a cert flipping to CERTIFIED / reaching 108, any falsifier, a major GPT-Pro
    verdict, a Lean module milestone, P(math)/P(Lean) moving ≥5, or a user-only decision. Otherwise work quietly.
(6) Hard rules: EXACT rational arithmetic is the only acceptance gate; battery pass ≠ proof; native_decide
    FORBIDDEN; commit as USER ALONE (no Anthropic/Claude trailer — FC CLA fails on it); compute ≤64 threads (Codex
    is gone, the machine is mine — but stay ≤64); native clang++ never WSL; PowerShell syntax (temp-file +
    Get-Content -Raw for pipe-laden appends); graph6 via files. Chrome MCP: browser responding ≠ MCP server
    connected; if ToolSearch finds no claude-in-chrome tools, use USER-RELAY and tell the user to reconnect the
    extension / MCP.
(7) ENDGAME (when conjuncts 1-3 read done and the Lean module set is complete): full aggregate re-verify, honest
    builds + forbidden-token greps of ALL modules, axioms probe ⊆ {propext,Classical.choice,Quot.sound}, assemble
    the ONE formal-conjectures PR (branch, user-alone commits, official-statement bridge), assemble the paper
    package, surface to the user for the send decision.
(8) Re-arm ScheduleWakeup (~700-1500s; shorter only when actively polling) with THIS SAME /loop text verbatim. Do
    not stop until the /goal's four conjuncts hold or a decisive obstruction is documented and surfaced.
