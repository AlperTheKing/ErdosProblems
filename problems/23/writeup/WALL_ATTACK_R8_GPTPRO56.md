# WALL ATTACK — R8: strict-dual split falsified at abstract-bank level; rescue = atomic bank ownership
# (GPT-5.6 Pro, 2026-07-10, RELAYED VERBATIM BY USER)

**[CLAUDE GATE HEADER:**
- VERDICT: StrictDualRootCrossingPureLensSplit_exists is FALSE at the unrestricted abstract-bank level.
  **2-atom/1-sink countermodel (arithmetic verified by my inspection, exact)**: A={a0,a1}, P={p0,p1}, T={t},
  both ports route to t, κ_t=1, t retained at FULL capacity by parent AND both one-atom children. Dual
  α=γ=δ≡1: every D1 row tight (|X| ≤ |X|), D2 tight (1≤1), Gap = 1+1−1 = 1 > 0; extreme + support-minimal.
  Parent primal infeasible (coverage forces load ≥2 into cap 1); each child feasible (λ=1, y=1) ⟹
  deletion-minimal; Defect(parent)=1, Defect(children)=0. Even a PERFECT geometric split (noDouble,
  cover-or-zero, proper, support/vertex-disjoint) fails PureLensBankSingleOwner: q_t(L)+q_t(R)=2>1=q_t(P).
- **THE SHARED-SINK IDENTITY (decisive sign)**: Defect(L∪R) = Defect(L) + Defect(R) + Σ_{t∈N(L)∩N(R)} κ_t
  (here 1 = 0+0+1). A shared sink makes the union MORE deficient than the sum; a positive δ_t prices exactly
  that shared bottleneck ⟹ strict duality cannot oppose double ownership — it can be CAUSED by it.
- Also settled: raw dual support is geometrically meaningless (ε-perturbation makes all β,γ,δ positive while
  keeping Gap>0); no ordinary complementary slackness (no feasible primal exists); the strict dual does NOT
  break R7's 4·x₅=1 parity (rational inequalities; x=1/4 stays feasible; an ExactOneIdentity
  0 = Σ α_a(k_a(U)−1) with termwise signs would be needed and D1/StrictGap don't produce it).
- **THE RESCUE (concrete, real-bank, duality-free)**: `OfficialBankTerm.atomicOwner` — every official bank
  term has owner : Term → SupportAtom (vertex/support-edge/root-token primitive) with
  owner_mem_of_retained_pos (positively retained in an inherited cage ⟹ owner in its support atoms) +
  retained_le_parent. Then for support-disjoint children, q_t(L)=0 ∨ q_t(R)=0 TERMWISE ⟹
  PureLensBankSingleOwner follows from support disjointness alone. The countermodel fails exactly this (its
  term has support on both sides, no owner). Door(edge) and VertexSlack(vertex) are atomically owned by
  construction; **THE AUDIT = do the compiled C5Base/prune term constructors carry atomic owners?** If yes:
  promote the rejection to a Lean lemma, bank side CLOSES, and the wall shrinks to the dual-tight
  root-layer purity lemma. If no: the checker gains the atomicOwner field (definitional for door/vs; a real
  decision for c5Base/prune) — flag for cage-legality.
- REMAINING GENUINE GEOMETRY after the bank fix: ExtremeDualTightRootLayer_exists (tight D1 rows + unique-
  root shore ⟹ concrete layer/lens seed — needs a real argument, NOT complementary slackness) +
  TightRootLayer_pure (noDouble/cover-or-zero — must supply the nonnegative-deviation identity; the R7
  parity is the obstacle) + TightRootLayer_children (proper, disjoint). Algebraic/provable helpers:
  StrictDual.normalizedExtreme_exists; StrictDual.alpha_pos_of_atomDeletionMinNeg (atom-deletion child +
  dual restriction ⟹ α_a > 0 — still no lens).
- **FALSIFIER SEARCH RECIPE (§c, adopted)**: enumerate defect-one footprints (recompute ALL predicates,
  quotient by root-preserving iso) × OFFICIAL bank support profiles only (term rows: kind, port mask,
  owner primitive, parent+per-child retention; capacities from the defect-one polytope: c_t ≥ 0,
  Surplus(C) − Σ ρ_{C,t} c_t = 1, Surplus(D) − Σ ρ_{D,t} c_t ≤ 0 per proper child; enumerate basic feasible
  solutions) × EXHAUST the conclusion (all real lens candidates via the actual constructors; retain only
  ¬∃U (split ∧ singleOwner)) × exact strict-dual LP (normalize Σ=1, maximize Gap; feasible point with g>0
  suffices). Decisive hit = all 9 checks; cage-illegal = any official-constructor/owner/realizability
  failure. FIRST UNIT TEST = the 2-atom manifest vs the abstract hypotheses. TARGETED R7 TEST = one official
  term with port mask meeting both sides of every lens split, capacity from the polytope, then the full LP —
  tests whether a shared official bottleneck turns the fiberless R7 geometry into a strict-dual CE.
- Output record fields + checker additions listed verbatim in §c/§d (normalized-dual checker, atom-deletion
  restriction, official owner audit, retention tables, exhaustive lens generation, exact single-owner,
  per-child MinNeg, realizability).
- MY NEXT ACTIONS: (1) AUDIT Ell5/ConcreteCage/Bank.lean term constructors for atomic ownership (THE cheap
  decisive step); (2) run the 2-atom manifest as the unit test against the abstract hypotheses; (3) hand
  Codex the atomicOwner frame + checker additions; (4) retask 5.6-Pro on TightRootLayer_pure ONLY IF the
  bank audit closes; else on the owner rule for c5Base/prune.**]
