# Branch-A completeness for length-five rows (GPT-Pro SIBLING, 2026-07-07)

TRANSCRIBED (head+mid+tail, symbol-decoded, faithful). Companion to BRANCH_B_BANKED_UPO_ASSEMBLY_GPTPRO.md.
This is the manuscript Branch-A completeness certificate. Maps exactly to the compiled Lean (ODLFull.lean +
A1ProperWrapper.lean, 11 green increments).

## Statement
Branch A proves the GERSH bound for every bad edge whose shortest rows have length 5, consuming ONLY the scalar
input `etaNonneg : η ≥ 0` (supplied by Bank0 in the pure all-L5 case, by Bank-L when a longer positive row
exists). Let f∈M, ℓ(f)=5, Q=(q_0,…,q_4)∈cyc(f); s_i=s(q_i), τ=5m/N. Active mask P={i∈Z/5 : s_i>τ}.

## Trichotomy (empty / proper / full mask)
- **PROPER mask** (∅≠P⊊Z/5) — a1Proper: X_P ≤ (25/N + 2/3)·η. With η≥0, (2/3)η≤η, so X_P ≤ (25/N+1)·η.
  Since X_P = Σ_i (s_i−τ)_+, this gives  Σ_i (s_i−τ)_+ ≤ (1+25/N)·η  = C5-RS in the proper-mask case.
  [Lean: A1Proper.a1Proper_of_six_cones + xmask_bound_of_clearedDefect; the (2/3→1) step = c5RS_of_branchA_inputs.]
- **FULL mask** (P=Z/5) — odlFull: every row vertex active, Σ_i(s_i−τ)_+ = Σ_i(s_i−τ); discharged by ODL.
  odlFull theorem: for every full-mask ODL node of a length-5 row Q,  rowSum(Q) ≤ N + η.
  [Lean: ODLFull.ODLFull_of_semantic_tree via the Seed3 route tree + semantic core + leaf providers.]
- (empty mask: trivial, all s_i≤τ.)
- net-DW assembly then gives I(Q) ≤ N + η. Since Q∈cyc(f) arbitrary, **ROWSUM(f) ≤ N + η for every ℓ(f)=5**.

## Finite certificate families needed for Branch A (exactly)
1. the six A1 ConeCerts M0,…,M5;
2. the PMTS slack dictionary;
3. the Seed3 ODL route trees;
4. the ODL semantic core + internal excess-monotonicity links;
5. the CONE/Bank/Lens/NoOverfull terminal leaf providers;
6. the O14 EQ chart cover of 108 rows;
+ the associated seed and quotient well-formedness certificates.

"There is NO open extremal inequality in Branch A beyond these finite certificate families and the scalar input
η≥0. The scalar input is supplied by Bank0 in the pure all-length-five case and by Bank-L whenever a longer
positive row exists."

## Lean mapping (this session, 11 green increments, axioms [propext,Classical.choice,Quot.sound])
- (1)+(2): a1Proper reduced in Lean to bounding six canonical XMasks (A1ProperWrapper.a1Proper_of_six_cones);
  cones = the finite family Codex emits (PMTS tooling). c5RS coefficient step green.
- (3)+(4)+(5): odlFull provider framework COMPLETE — ODLFull_of_semantic_tree (assembly) + internalLinks_of_
  coreExcess (excess-monotonicity) + leafProviders_of_concreteChecks / coreODLGoal_of_coneCert (CONE leaf) +
  coreDefect layer. Concrete per-row emission (ODLRowSemanticsPayload) is the data-instantiation step.
- (6): O14 = full 108-row chart cover (Codex; 45/108, k6/F6 reproduction from 22-family pool in flight).
=> Branch-A = PROVEN modulo the six enumerated finite certificate families (all compiled-Lean-consumable).
