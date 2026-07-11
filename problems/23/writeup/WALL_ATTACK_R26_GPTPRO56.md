# WALL ATTACK — R26: k≥6 normal form — killer rows ⟺ radius-3 producer bridges;
# frontier = (16): scoped deficiency forces a selected edge at active-I radius 3
# (GPT-5.6 Pro, 2026-07-11)

**[CLAUDE GATE HEADER — reduction verified by inspection (path/parity/count arguments airtight):**
- **PROVEN — radiusThreeProducerBridge_to_row**: J_ω = union of active I-components; ρ_ω(f,e) =
  min oriented sum of J-distances from atom endpoints to the selected edge e's ends. If ρ = 3:
  concatenation P_L + e + P_R is a blue s-t walk of length ≤ 4; d_B(s,t) = 4 forces length EXACTLY 4 and
  simplicity (repeat ⟹ s-t walk ≤ 2); DB completeness ⟹ Q ∈ Geo₄(f); edges = 3 J-edges + 1 S-edge;
  Q ≠ R_f automatic. ✓
- **PROVEN — normal form under hfar** (all active atoms at internal distance ≥ 6): every internal killer
  row has exactly 3 active + 1 selected edge (4 active would make f active at dist ≤ 4, contra hfar), and
  removing the unique selected edge splits Q into segments summing to 3 ⟹ ρ(f,e) = 3. Full Lean
  equivalence internalKiller_iff_absorbingRadiusThreeBridge (structures ActiveRadiusThreeProducerBridge +
  Absorbing… with constructed-not-supplied row; proof = path/edge-count identities). Absorption (15) =
  the existing activeComponents-empty check, applied after.
- **THE FRONTIER (16)**: ¬ScopedOwnerHall(ω) ⟹ ∃ f, ∃ e ∈ S_ω with ρ_ω(f,e) = 3
  (scopedHallFailure_has_radiusThreeProducerBridge, full hypothesis list). Proven-en-route sparsity:
  (17) adjacent I-path vertices have DISJOINT producer sets; (18) no selected row contains z_i, z_{i+2},
  z_{i+4} of a shortest I-path (under hfar; else the row's ends would be a dist-≤2 bad pair or a dist-4
  active atom).
- **WHY FACTS STOP BEFORE (16)**: minimality (19) gives LATENT producers (∪_{g≠f} F_g = F) but (20)
  latent ∈ F_g ⇏ currently SELECTED ∈ E(R_g) — the latent→selected upgrade near the atom is the exact
  unresolved selection step; max-cut prices only existing edges (a five-vertex I-window need not be an
  atom). **KEY HONEST DATUM: the archived 28/27 active circuit (length-12 active I-path, minimal
  defect-one, rigid DB) has NO radius-3 bridge — and its scoped Hall network is FEASIBLE.** So (16)'s
  burden rests entirely on the deficiency hypothesis; bridge-absence alone is consistent with Hall.
- **THREE-OUTCOME FALSIFIER GATE** (per hfar-failing tuple): (i) no ρ=3 pair ⟹ falsifies (16);
  (ii) ρ=3 rows exist but none absorbs ⟹ falsifies the killer-row theorem, one-row descent still open;
  (iii) no one-row replacement descends ⟹ kills Ell5ScopedOneRowDescent. Full record spec given.
- NEXT: Codex = implement the three-outcome gate + hunt hfar-failures (do they even exist? census so far:
  failures come with dist-4 atoms); compile the normal-form module (mechanical). GPT R27 = prove (16) via
  quantitative pressure counting on the path using (17)/(18), or prove hfar ∧ deficiency = contradiction
  directly (equivalent closure), or construct outcome-(i) CE.**]
