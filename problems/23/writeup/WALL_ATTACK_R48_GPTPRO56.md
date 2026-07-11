# WALL ATTACK — R48: LOCAL PROFILE ⟺ FOUR-NUMBER CLASSIFIER (forced-through + two bipartite matchings);
# FROZEN SUPPORT LEMMA = t5_localProfile_forces_badTriangle (GPT cannot prove — engine decides);
# RELAXATION LADDER; k=3 not faster; P ~4%
# (GPT-5.6 Pro, 2026-07-12, "worked 12m36s"; harvested ~13.4k ch)

**[CLAUDE GATE HEADER — the three equivalence proofs verified by inspection: (1) forced-through sharpness
(∃ω r_ω(v)=5 ⟺ Forced(v)=Inc(v); ≥6 forced ⟹ impossible — and the t=4 mechanism does NOT generalize: the
near-candidate has Forced=Inc exactly); (2) first-step matching (active edge survives ⟺ R_step covers Y;
multiplicities forced (2,1,1,1)); (3) ONE owner-avoiding row covers AT MOST ONE star pair (parity: three
same-shore blue nbrs of v at positions 0,2,4 would make the row's endpoints blue nbrs of v at blue distance
2 through v, contradicting distance 4) ⟹ ν(R_cov)=4 needs 4 DISTINCT nonincident atoms. The
T5LocalOwnerProfile ⟺ (9) equivalence removes the CP-SAT from the local stage — hand the classifier to the
sweep VERBATIM. GPT explicitly cannot prove the frozen lemma; the near-candidate realizes the profile with
30 triangles AND scope-vacuity (two independent failures) so minimality+multiplicity+completeness alone are
insufficient — triangle-freeness must interact. Engine decides: a triangle-free zero-vector candidate
falsifies the support lemma (next discriminator = active-scope realizability); exhaustion supports compile.]**

## 1-4. The exact local-profile reduction
Forced(v) = atoms whose EVERY row contains v; Inc(v) ⊆ Forced(v) (anchoring). **∃ω r_ω(v)=5 ⟺ Forced(v) =
Inc(v)** (sharp). First-step relation R_step (incident atom a → y ∈ Y if some row of a starts v−y): active
edge vx₀ unselected ∧ all four vy selected ⟺ every incident atom has a step ∧ ν(R_step) = 4; multiplicities
(2,1,1,1). Coverage relation R_cov (y → nonincident a with a row Q: v ∉ Q, x₀,y ∈ Q): one row covers ≤ 1
pair ⟹ need ν(R_cov) = 4 (4 distinct atoms). **T5LocalOwnerProfile(v,x₀) ⟺ Forced=Inc ∧ steps nonempty ∧
ν(R_step)=4 ∧ ν(R_cov)=4.** Lean shapes: ForcedThroughAtoms, rowCount_eq_badDegree_iff_forced_eq_incident,
t5_localOwnerProfile_iff.

## 5-6. Profile consequences + the near-miss
Coverage subgraph: 9+q edges / 6+q vertices ⟹ cycle rank exactly 4 (cycles v−x₀−q_i−y_i, independent via
vy_i) ⟹ μ(F*) ≥ 4, |V| ≤ 21 (sharp, no contradiction). Latent-vs-selected gap: supportMultiplicity(vx₀) ≥ 4
(each coverage row's v-detour) while selectedMultiplicity = 0 — defect-one PERMITS it. The R46 near-candidate
satisfies ALL THREE local conditions and realizes the full profile (r=5, vx₄ unselected, all pairs covered)
BUT: I_ω = {vx₄} is a 2-vertex component with NO bad endpoints ⟹ v ∉ ActiveVerts (scope-vacuous) AND the
atom graph has 30 triangles. Forced-row arithmetic alone CANNOT close. Script SHA 806a06b8.

## 7. THE FROZEN LEMMA (support-level target)
`t5_localProfile_forces_badTriangle : (connected, 24 edges, 25 atoms, minimal, complete DB, anchoring,
dB=dM=5) → T5LocalOwnerProfile D v x₀ → ¬ atomEndpointGraph.CliqueFree 3` — equivalently: triangle-free
25/24 circuit ⟹ NO degree-five local owner profile. Stronger than the active-scoped need; finite-checkable;
consistent with all hits; sharp vs the near-candidate. **GPT cannot currently prove it.** Fallback (weaker):
t5_triangleFree_localProfile_is_scopeVacuous (v ∉ activeVerts). No example distinguishes them yet.

## 8-9. Relaxation ladder + k=3
Classifier: (e_forced, i_step, d_step, d_cov) per (15); profile ⟺ (0,0,0,0). Near-miss lex order; first
relaxation ν(R_cov) 4→3, then step 4→3, then |Forced|=6. Zero-vector candidates: build the tuple from the
matchings → selected internal graph → active-component test → only then second owner + transport ledger.
k=3 NOT faster (coverage atoms shareable across owners; no 15+12>25 count) but rooted k=3 is small (15 fixed
owner edges, 9 free); the triangle lemma would kill k=2 AND k=3 at once. μ ≥ 6, |V| ≤ 19 for k=3.

## Verdict
profile ⟺ forced-through equality + step matching + coverage matching — none contradicted by defect-one
alone. Remaining support theorem: those three conditions force a bad triangle in every 25/24 circuit.
**P(falsifier) ≈ 4%** (zero integrated hits so far + the reduction + the near-candidate needing BOTH
failures).
