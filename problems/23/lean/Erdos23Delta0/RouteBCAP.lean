import Mathlib.Tactic

/-!
# Route-B CAP interface — the A-derivation, machine-checked (2026-07-08)

Erdős #23 gap#1 door-only closure. GPT-Pro reduced the "no long side-door annulus" lemma A
(`NoLongSideDoorAnnulus`) to a 3-case argument over a minimal CAP primitive interface. The single load-bearing
primitive is `hFirstSplit` (= `AnnularAtom_has_firstSplit` = `S1S2_annularLayer_cover`): a level-`≥1` owned annular
atom of a minimal two-door side-door subcage forces a proper interior first-split subcage, classified PS ∨ ZT ∨ BAD.

The 2026-07-08 adversarial S1 re-audit (verdict WALL, high confidence, `S2_FROZEN_STATEMENT.md:168` spot-verified)
found that `hFirstSplit` is **NOT discharged by the archived S1/S2 theory** — S1 gives only Ferrers ordering and S2
gives a disjunction with door-existence demoted to an application case-split. So `hFirstSplit` is the genuine open
geometric residual (battery-validated only: 17757 census+glue cases, 0 fail).

This module makes the **derivation** honest and machine-checked: given the primitives as explicit hypotheses, every
owned atom of a minimal side-door subcage is level 0 (hence owns no `ell ≥ 9` bad edge). No placeholders. The primitives —
above all `hFirstSplit` — remain the named obligations; nothing here claims them.
-/

namespace Erdos23Delta0
namespace RouteBCAP

/-- **A = `NoLongSideDoorAnnulus`, derivation only** (GPT-Pro's 3-case argument, machine-checked). Over abstract
    `Cage`/`Atom` types and abstract CAP predicates, from the four primitives:
    * `hFirstSplit` (= `AnnularAtom_has_firstSplit`, the OPEN residual): a level-`≥1` owned atom of a minimal
      side-door cage yields a proper subcage classified `PS ∨ (ZT ∧ atom inside) ∨ BAD`;
    * `hMinNoProperPS`: a proper positive-slack side-door subcage contradicts minimality;
    * `hTerminality`: an atom inside a proper zero-slack core is not owned by the parent;
    * `hNoViolation` (= `ValidCAPFrame_no_violation`): a valid CAP frame has no boundary/S2 violation;
    the conclusion is that every owned atom of a minimal side-door subcage has level `0`. Pure logic, non-circular
    (no Γ-minimality, no switch, no reserve). -/
theorem noLongSideDoor_of_primitives
    {Cage Atom : Type}
    (level : Atom → Nat)
    (OwnedAtom AtomInCage : Cage → Atom → Prop)
    (ProperSub : Cage → Cage → Prop)
    (IsMinSideDoor IsPosSlackSideDoor IsZeroSlackTypeBCore CAPViolation : Cage → Prop)
    (hFirstSplit : ∀ (D : Cage) (x : Atom), IsMinSideDoor D → OwnedAtom D x → 1 ≤ level x →
        ∃ D', ProperSub D' D ∧
          (IsPosSlackSideDoor D' ∨ (IsZeroSlackTypeBCore D' ∧ AtomInCage D' x) ∨ CAPViolation D'))
    (hMinNoProperPS : ∀ (D D' : Cage), IsMinSideDoor D → ProperSub D' D → ¬ IsPosSlackSideDoor D')
    (hTerminality : ∀ (D D' : Cage) (x : Atom),
        ProperSub D' D → IsZeroSlackTypeBCore D' → AtomInCage D' x → ¬ OwnedAtom D x)
    (hNoViolation : ∀ (D' : Cage), ¬ CAPViolation D') :
    ∀ (D : Cage) (x : Atom), IsMinSideDoor D → OwnedAtom D x → level x = 0 := by
  intro D x hMin hOwn
  by_contra hne
  have hLong : 1 ≤ level x := Nat.one_le_iff_ne_zero.mpr hne
  obtain ⟨D', hProp, hcls⟩ := hFirstSplit D x hMin hOwn hLong
  rcases hcls with hPS | hZT | hBAD
  · exact hMinNoProperPS D D' hMin hProp hPS
  · exact hTerminality D D' x hProp hZT.1 hZT.2 hOwn
  · exact hNoViolation D' hBAD

/-- **S2-disjunct forcing: the interior door is forced given `ApplicationGeometry`** (2026-07-08, reconciling the S1
    re-audit WALL verdict with GPT-Pro's refinement). The archived S2 theory (`S2_FROZEN_STATEMENT.md`) proves, for a
    strict reduced terminal theta, the disjunction `IntermediateDoor ∨ Triangle ∨ (a B-walk saving ≥2)` — but the
    disjunction is **application-supplied** (`:154-159`, `:225`), so it is NOT itself proved by S2. This theorem
    machine-checks the CLOSING step: given that disjunction (`hS2`), triangle-freeness (`hTriFree`, kills S2-Core 2's
    real triangle), and distance-minimality (`hDistMin`: the true cut-distance `dist_B(a,b)` is ≤ any B-walk between
    the same endpoints — this is S2-Core 1 composed with walk→path→dist), the interior door is FORCED. The remaining
    obligation is exactly `hS2` (= `ApplicationGeometry` = a valid replacement arm saving ≥2 for the level-`j≥1`
    transition), which S1/S2 do NOT discharge for a general minimal side-door subcage (battery-only: 17757 cases). -/
theorem intermediateDoor_forced_of_S2disjunction
    (IntermediateDoor Triangle : Prop)
    (walkLen dist : Nat)
    (hS2 : IntermediateDoor ∨ Triangle ∨ walkLen + 2 ≤ dist)
    (hTriFree : ¬ Triangle)
    (hDistMin : dist ≤ walkLen) :
    IntermediateDoor := by
  rcases hS2 with h | h | h
  · exact h
  · exact absurd h hTriFree
  · omega

/-- **Door-only surplus bound from `NoLongSideDoor` + mass ≤ sigma** (rational arithmetic). If every owned atom is
    level 0 then the cage surplus is `24 * mass`; with `mass ≤ sigma` and `0 ≤ sigma` this gives `Surplus ≤ 25*sigma`,
    the exact hypothesis consumed by `RouteBAssembly.doorOnly_balance_nonneg`. Non-circular. -/
theorem surplus_le_25sigma_of_level0
    (mass sigma : ℚ)
    (hmass : mass ≤ sigma) (hsig : 0 ≤ sigma) :
    (24 : ℚ) * mass ≤ 25 * sigma := by nlinarith

/-- **R-D door-only absorption, assembled from the CAP primitives** (machine-checks the whole door-only chain).
    Composing `noLongSideDoor_of_primitives` (A: every owned atom of a minimal side-door subcage is level 0) with the
    surplus model (`Surplus = 24·mass` when all owned atoms are level 0), `mass ≤ sigma`, and the door-slack bank
    (`25·sigma ≤ BankCap`), a minimal side-door subcage has nonnegative balance: `0 ≤ BankCap − Surplus`. This is
    `PositiveSlackAbsorption` for the prunable side-door subcages — the R-D result — derived (No placeholders) from the
    CAP primitives, of which the single OPEN one is `hFirstSplit` (= `AnnularAtom_has_firstSplit`, whose sole
    remaining input is `ApplicationGeometry`; battery-only, 17757 cases). Route-independent (shared by A and B). -/
theorem sideDoor_balance_nonneg_of_primitives
    {Cage Atom : Type}
    (level : Atom → Nat)
    (OwnedAtom AtomInCage : Cage → Atom → Prop)
    (ProperSub : Cage → Cage → Prop)
    (IsMinSideDoor IsPosSlackSideDoor IsZeroSlackTypeBCore CAPViolation : Cage → Prop)
    (Surplus BankCap sigmaC mass : Cage → ℚ)
    (hFirstSplit : ∀ (D : Cage) (x : Atom), IsMinSideDoor D → OwnedAtom D x → 1 ≤ level x →
        ∃ D', ProperSub D' D ∧
          (IsPosSlackSideDoor D' ∨ (IsZeroSlackTypeBCore D' ∧ AtomInCage D' x) ∨ CAPViolation D'))
    (hMinNoProperPS : ∀ (D D' : Cage), IsMinSideDoor D → ProperSub D' D → ¬ IsPosSlackSideDoor D')
    (hTerminality : ∀ (D D' : Cage) (x : Atom),
        ProperSub D' D → IsZeroSlackTypeBCore D' → AtomInCage D' x → ¬ OwnedAtom D x)
    (hNoViolation : ∀ (D' : Cage), ¬ CAPViolation D')
    (hSurplusModel : ∀ D, (∀ x, OwnedAtom D x → level x = 0) → Surplus D = 24 * mass D)
    (hMassSig : ∀ D, mass D ≤ sigmaC D)
    (hSigNN : ∀ D, 0 ≤ sigmaC D)
    (hDoorBank : ∀ D, 25 * sigmaC D ≤ BankCap D)
    (D : Cage) (hMin : IsMinSideDoor D) :
    0 ≤ BankCap D - Surplus D := by
  have hlvl : ∀ x, OwnedAtom D x → level x = 0 := fun x hx =>
    noLongSideDoor_of_primitives level OwnedAtom AtomInCage ProperSub IsMinSideDoor
      IsPosSlackSideDoor IsZeroSlackTypeBCore CAPViolation
      hFirstSplit hMinNoProperPS hTerminality hNoViolation D x hMin hx
  have hsurp : Surplus D = 24 * mass D := hSurplusModel D hlvl
  have hbound : Surplus D ≤ 25 * sigmaC D := by
    rw [hsurp]; nlinarith [hMassSig D, hSigNN D]
  linarith [hDoorBank D]

/-- **Pruning drops balance below the parent** (pure ledger algebra). Given the prune balance identity
    `Balance C = Balance C' + Balance D + PruneRemainder D` with a nonnegative prunable block (`0 ≤ Balance D`) and
    nonnegative prune remainder (`0 ≤ PruneRemainder D`), the pruned descendant `C'` has `Balance C' ≤ Balance C`;
    in particular a strictly-negative parent forces a strictly-negative descendant. -/
theorem pruned_balance_le
    {Cage : Type} (Balance PruneRem : Cage → ℚ)
    (C C' D : Cage)
    (hBal : Balance C = Balance C' + Balance D + PruneRem D)
    (hDnn : 0 ≤ Balance D) (hRem : 0 ≤ PruneRem D) :
    Balance C' ≤ Balance C := by linarith

/-- **Minimality lever: no nonnegative prunable subcage inside a minimal negative-balance cage** (2026-07-08,
    GPT-Pro's `no_nonneg_prunable_subcage_in_minNeg`, the one piece that survived Claude's falsification of the clean
    ambient reduction). It is pure ledger algebra, independent of the (false) `cap_X(v)=Γ_X` ambient split, and stays
    valid with the corrected full bank `Door + vertexSlack(N−T) + C5 + Prune`. Given a minimal negative-balance cage
    `C` (every proper subcage has nonnegative balance, `hMinNoNeg`), a proper prunable subcage `C'` obtained from a
    nonnegative block `D`, the prune balance identity, and `Balance C < 0`, we reach a contradiction: the algebra
    forces `Balance C' < 0`, contradicting minimality. This excludes a tight full-support block (`Balance D = 0`,
    e.g. the C₂ₖ₊₁ / C_25 escape) from sitting inside the minimal negative-balance cage. -/
theorem no_nonneg_prunable_subcage_in_minNeg
    {Cage : Type} (Balance PruneRem : Cage → ℚ) (ProperSub : Cage → Cage → Prop)
    (C C' D : Cage)
    (hMinNoNeg : ∀ E, ProperSub E C → 0 ≤ Balance E)
    (hProper : ProperSub C' C)
    (hBal : Balance C = Balance C' + Balance D + PruneRem D)
    (hDnn : 0 ≤ Balance D) (hRem : 0 ≤ PruneRem D)
    (hCneg : Balance C < 0) :
    False := by
  have hle : Balance C' ≤ Balance C := pruned_balance_le Balance PruneRem C C' D hBal hDnn hRem
  have hnn : 0 ≤ Balance C' := hMinNoNeg C' hProper
  linarith

/-- **Leaf demand bound from the graph fact `ell ≤ N`** (2026-07-08). For a single-bad-edge (leaf) full-support
    cage the surplus demand is `ell² − 25`, where `ell` = shortest odd-cycle length ≤ `N` (a geometric fact: the odd
    cycle has `ell` vertices, `ell ≤ |V| = N`). Hence `demand = ell² − 25 ≤ N² − 25·1`. This is the hypothesis feeding
    `fullSupport_leaf_absorbed_by_density`, and it is NON-circular — it uses `ell ≤ N`, not the conjecture. -/
theorem leaf_demand_le_of_ell_le_N
    (Nq ell : ℚ) (hpos : 0 ≤ ell) (hell : ell ≤ Nq) :
    ell ^ 2 - 25 ≤ Nq ^ 2 - 25 * (1 : ℚ) := by nlinarith [hell, hpos]

/-- **Full-support leaf absorbed by the density (C5) bank** (2026-07-08, GPT-Pro's
    `fullSupport_leaf_absorbed_by_density`, exact-gated by Claude: 47369 census single-bad-edge cages 0 fail, odd cycles
    `C₂ₖ₊₁` all `Balance ≥ 0`). The C5/density capacity is `25·max(0, c5mass)` with `c5mass = N²/25 − m − σ`, stated
    division-free via `hc5 : 25·c5mass = N² − 25m − 25σ`. Given the leaf demand bound `demand ≤ N² − 25m` (from
    `ell ≤ N`, `leaf_demand_le_of_ell_le_N`), the door+C5 bank absorbs the demand:
    `demand ≤ 25σ + 25·max(0, c5mass)`. The single inequality `c5mass ≤ max(0, c5mass)` handles both regimes at once
    (C5 spends when `c5mass ≥ 0`; the door alone over-covers when `c5mass < 0`). This CLOSES the tight full-support
    leaf case — the `C₂₅⁺` cages that defeated the graph-computable `25σ + R_full` bank. NON-circular. -/
theorem fullSupport_leaf_absorbed_by_density
    (Nsq m sigma demand c5mass : ℚ)
    (hc5 : 25 * c5mass = Nsq - 25 * m - 25 * sigma)
    (hDemand : demand ≤ Nsq - 25 * m) :
    demand ≤ 25 * sigma + 25 * max 0 c5mass := by
  have h : c5mass ≤ max 0 c5mass := le_max_right 0 c5mass
  nlinarith [h, hc5, hDemand]

/-- **Short-atom square bound** (2026-07-08, the option-3 arithmetic core for `NoReducedOverdoorFullSupportMultiShell`).
    For an odd-cycle length `ell` in the range `[5, 23]` (the shortest odd cycle in a triangle-free graph has `ell ≥ 5`;
    `ell ≥ 25` atoms are the base leaves handled by `fullSupport_leaf_absorbed_by_density`), the atom's squared length is
    dominated by 25 times its geodesic cut-edge count `ell − 1`:  `ell² ≤ 25·(ell − 1)`. Exact rational; the first
    failure is `ell = 24` (`576 > 575`), so `ell ≤ 23` is the exact short-atom window. -/
theorem atom_sq_le_25_shortAtom (ell : ℚ) (h5 : 5 ≤ ell) (h23 : ell ≤ 23) :
    ell ^ 2 ≤ 25 * (ell - 1) := by nlinarith

/-- **Full-support door dominance from short atoms + geodesic disjointness** (2026-07-08, the option-3 derivation of
    `Γ_X ≤ 25·b_X`, machine-checked). If every atom of the shell has `ell ∈ [5,23]` (short: `ell ≥ 25` atoms are pruned as
    base leaves) and the geodesic cut-edge counts `(ell−1)` sum to at most the shell's distinct cut-edge count `b`
    (`hb`: the geodesic edge-disjointness / cut-edge-forcing structural input), then `Γ_X = Σ ell² ≤ 25·b = 25·b_X`, i.e.
    `Demand ≤ Door`. Pure summation over `atom_sq_le_25_shortAtom`; the two hypotheses (all atoms short after leaf-pruning,
    and `Σ(ell−1) ≤ b`) are the remaining structural obligations of `NoReducedOverdoorFullSupportMultiShell`. -/
theorem fullSupport_doorDominance_of_shortAtoms {α : Type} (s : Finset α) (ell : α → ℚ) (b : ℚ)
    (h5 : ∀ a ∈ s, 5 ≤ ell a) (h23 : ∀ a ∈ s, ell a ≤ 23)
    (hb : (∑ a ∈ s, (ell a - 1)) ≤ b) :
    (∑ a ∈ s, (ell a) ^ 2) ≤ 25 * b := by
  have hstep : (∑ a ∈ s, (ell a) ^ 2) ≤ ∑ a ∈ s, 25 * (ell a - 1) :=
    Finset.sum_le_sum (fun a ha => atom_sq_le_25_shortAtom (ell a) (h5 a ha) (h23 a ha))
  have hpull : (∑ a ∈ s, 25 * (ell a - 1)) = 25 * ∑ a ∈ s, (ell a - 1) := by
    rw [Finset.mul_sum]
  calc (∑ a ∈ s, (ell a) ^ 2) ≤ ∑ a ∈ s, 25 * (ell a - 1) := hstep
    _ = 25 * ∑ a ∈ s, (ell a - 1) := hpull
    _ ≤ 25 * b := by linarith

end RouteBCAP
end Erdos23Delta0
