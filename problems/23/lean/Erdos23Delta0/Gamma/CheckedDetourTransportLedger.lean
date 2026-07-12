import Erdos23Delta0.Gamma.CheckedCollisionDefectTrade

/-!
# Checked detour transport ledger

This module implements the exact R42 Section 6 bookkeeping identity for one
change of row state.  It deliberately does not construct a detour, an optimal
matching, or a graph-realized source.  Instead, a supplied ledger records the
old and new optimal coherent partial matchings and serializes the six turnover
sets used by the identity.

The physical source key is always `(base, half)`.  A carried edge keeps that
same physical key across the two states; source realization and component
coherence are rechecked at the new state.  The reflected checker has four
groups: optimality, obligation turnover, physical-key turnover, and the carry
partition.  From them we reconstruct a coherent carry matching and prove

`defect(new) - defect(old) = born + brokenLive - deadUnmatched - reoptimized`.

No existence theorem is asserted here.
-/

namespace Erdos23Delta0
namespace Gamma

open CheckedCollisionDefectTrade
open Pattern5StaticOwnership

set_option linter.dupNamespace false

universe uState uObligation uSource uComp

/-- A physical source half together with the row state in which it is viewed.
The state tag is audit data; `physical` is the key on which injectivity and
base-component coherence are enforced. -/
structure StateIndexedPhysicalKey (State : Type uState)
    (SourceBase : Type uSource) where
  state : State
  physical : SourceBase × Fin 2

/-- Serialized R42 transport data for one ordered pair of row states. -/
structure CheckedDetourTransportLedger
    {State : Type uState} {Obligation : Type uObligation}
    {SourceBase : Type uSource} {Comp : Type uComp}
    [DecidableEq Obligation]
    (D : CheckedCollisionDefectTrade.Data
      State Obligation SourceBase Comp)
    (oldState newState : State) where
  oldOptimal : CoherentPartialMatching D oldState
  newOptimal : CoherentPartialMatching D newState
  persistObligation : Finset Obligation
  persistSource : Finset Obligation
  carry : Finset Obligation
  born : Finset Obligation
  deadUnmatched : Finset Obligation
  brokenLive : Finset Obligation

namespace CheckedDetourTransportLedger

variable {State : Type uState} {Obligation : Type uObligation}
variable {SourceBase : Type uSource} {Comp : Type uComp}
variable [DecidableEq Obligation]
variable {D : CheckedCollisionDefectTrade.Data
  State Obligation SourceBase Comp}
variable {oldState newState : State}

abbrev Ledger :=
  CheckedDetourTransportLedger D oldState newState

/-- The old assignment viewed at its original state. -/
def oldPhysicalKey (L : Ledger) (d : Obligation)
    (hd : d ∈ L.oldOptimal.matched) :
    StateIndexedPhysicalKey State SourceBase :=
  ⟨oldState, L.oldOptimal.assign ⟨d, hd⟩⟩

/-- The same old physical key transported to the new state.  This does not
claim that the key remains graph-realized; that fact is checked separately. -/
def transportedPhysicalKey (L : Ledger) (d : Obligation)
    (hd : d ∈ L.oldOptimal.matched) :
    StateIndexedPhysicalKey State SourceBase :=
  ⟨newState, L.oldOptimal.assign ⟨d, hd⟩⟩

@[simp] theorem transportedPhysicalKey_physical
    (L : Ledger) (d : Obligation) (hd : d ∈ L.oldOptimal.matched) :
    (L.transportedPhysicalKey d hd).physical =
      (L.oldPhysicalKey d hd).physical := rfl

/-- The old assigned physical key remains a legal source for the same
obligation in the new state. -/
def SourcePersists (L : Ledger) (d : Obligation) : Prop :=
  ∃ hd : d ∈ L.oldOptimal.matched,
    D.sourceRealized newState d (L.oldOptimal.assign ⟨d, hd⟩)

/-- Carrying a base key is legal only when its destination component label is
unchanged. -/
def ComponentPersists (d : Obligation) : Prop :=
  D.component newState d = D.component oldState d

noncomputable def expectedPersistObligation (L : Ledger) :
    Finset Obligation := by
  classical
  exact D.obligations oldState ∩ D.obligations newState

noncomputable def expectedPersistSource (L : Ledger) :
    Finset Obligation := by
  classical
  exact L.oldOptimal.matched.filter L.SourcePersists

noncomputable def expectedCarry (L : Ledger) : Finset Obligation := by
  classical
  exact L.oldOptimal.matched.filter fun d =>
    d ∈ D.obligations newState ∧ L.SourcePersists d ∧ ComponentPersists d

noncomputable def expectedBorn (L : Ledger) : Finset Obligation := by
  classical
  exact D.obligations newState \ D.obligations oldState

noncomputable def expectedDeadMatched (L : Ledger) :
    Finset Obligation := by
  classical
  exact L.oldOptimal.matched \ D.obligations newState

noncomputable def expectedDeadObligation (L : Ledger) :
    Finset Obligation := by
  classical
  exact D.obligations oldState \ D.obligations newState

noncomputable def expectedDeadUnmatched (L : Ledger) :
    Finset Obligation := by
  classical
  exact L.expectedDeadObligation \ L.expectedDeadMatched

noncomputable def expectedPersistentMatched (L : Ledger) :
    Finset Obligation := by
  classical
  exact L.oldOptimal.matched ∩ D.obligations newState

noncomputable def expectedBrokenLive (L : Ledger) :
    Finset Obligation := by
  classical
  exact L.expectedPersistentMatched \ L.expectedCarry

/-- The four reflected audit groups in the archived R42 specification. -/
structure Checked (L : Ledger) : Prop where
  optimality :
    D.collisionDefect oldState = L.oldOptimal.unmatchedCount ∧
      D.collisionDefect newState = L.newOptimal.unmatchedCount
  obligation_turnover :
    L.persistObligation = L.expectedPersistObligation ∧
      L.born = L.expectedBorn ∧
      L.deadUnmatched = L.expectedDeadUnmatched
  physical_key_turnover :
    L.persistSource = L.expectedPersistSource
  carry_partition :
    L.carry = L.expectedCarry ∧
      L.brokenLive = L.expectedBrokenLive

/-- Kernel-reflected checker.  It checks only a supplied finite ledger; it
does not search for states, matchings, or graph sources. -/
noncomputable def check (L : Ledger) : Bool := by
  classical
  exact decide L.Checked

theorem check_eq_true_iff (L : Ledger) :
    L.check = true ↔ L.Checked := by
  classical
  simp [check]

theorem carry_mem_oldMatched (L : Ledger) (h : L.Checked)
    {d : Obligation} (hd : d ∈ L.carry) :
    d ∈ L.oldOptimal.matched := by
  rw [h.carry_partition.1] at hd
  simpa [expectedCarry] using hd.1

theorem carry_mem_newObligations (L : Ledger) (h : L.Checked)
    {d : Obligation} (hd : d ∈ L.carry) :
    d ∈ D.obligations newState := by
  rw [h.carry_partition.1] at hd
  simpa [expectedCarry] using hd.2.1

theorem carry_source_persists (L : Ledger) (h : L.Checked)
    {d : Obligation} (hd : d ∈ L.carry) :
    L.SourcePersists d := by
  rw [h.carry_partition.1] at hd
  simpa [expectedCarry] using hd.2.2.1

theorem carry_component_persists (L : Ledger) (h : L.Checked)
    {d : Obligation} (hd : d ∈ L.carry) :
    ComponentPersists (D := D) (oldState := oldState)
      (newState := newState) d := by
  rw [h.carry_partition.1] at hd
  simpa [expectedCarry] using hd.2.2.2

/-- Every carried obligation keeps one literal physical key, remains realized
at both states, and keeps its base-component destination. -/
def EveryCarryPreservesPhysicalKey (L : Ledger) : Prop :=
  ∀ d (hd : d ∈ L.carry),
    ∃ hold : d ∈ L.oldOptimal.matched,
      D.sourceRealized oldState d (L.oldOptimal.assign ⟨d, hold⟩) ∧
      D.sourceRealized newState d (L.oldOptimal.assign ⟨d, hold⟩) ∧
      ComponentPersists (D := D) (oldState := oldState)
        (newState := newState) d

theorem everyCarryPreservesPhysicalKey (L : Ledger) (h : L.Checked) :
    L.EveryCarryPreservesPhysicalKey := by
  intro d hd
  let hold := L.carry_mem_oldMatched h hd
  refine ⟨hold, L.oldOptimal.source_realized ⟨d, hold⟩, ?_,
    L.carry_component_persists h hd⟩
  rcases L.carry_source_persists h hd with ⟨hold', hsource⟩
  simpa only [Subsingleton.elim hold' hold] using hsource

/-- The inherited old physical-key injection on the carry domain. -/
noncomputable def carryAssign (L : Ledger) (h : L.Checked) :
    {d // d ∈ L.carry} ↪ (SourceBase × Fin 2) where
  toFun d := L.oldOptimal.assign
    ⟨d.1, L.carry_mem_oldMatched h d.2⟩
  inj' := by
    intro d e hkey
    have hold :
        (⟨d.1, L.carry_mem_oldMatched h d.2⟩ :
          {x // x ∈ L.oldOptimal.matched}) =
        ⟨e.1, L.carry_mem_oldMatched h e.2⟩ :=
      L.oldOptimal.assign.injective hkey
    exact Subtype.ext (congrArg Subtype.val hold)

theorem carryAssign_source_realized (L : Ledger) (h : L.Checked)
    (d : {x // x ∈ L.carry}) :
    D.sourceRealized newState d.1 (L.carryAssign h d) := by
  rcases L.carry_source_persists h d.2 with ⟨hold, hsource⟩
  simpa only [carryAssign, Subsingleton.elim hold
    (L.carry_mem_oldMatched h d.2)] using hsource

/-- Base-component coherence survives transport because both the physical
base key and every carried obligation's component label survive. -/
theorem carryAssign_base_component_coherent (L : Ledger) (h : L.Checked) :
    BaseKeyComponentCoherent (L.carryAssign h)
      (fun d => D.component newState d.1) := by
  intro d e hbase
  have hold := L.oldOptimal.base_component_coherent
    ⟨d.1, L.carry_mem_oldMatched h d.2⟩
    ⟨e.1, L.carry_mem_oldMatched h e.2⟩ hbase
  have hd := L.carry_component_persists h d.2
  have he := L.carry_component_persists h e.2
  exact hd.trans (hold.trans he.symm)

/-- The old matching restricted to physically persistent, component-coherent
edges is a valid coherent matching at the new state. -/
noncomputable def carryMatching (L : Ledger) (h : L.Checked) :
    CoherentPartialMatching D newState where
  matched := L.carry
  matched_subset := fun _ hd => L.carry_mem_newObligations h hd
  assign := L.carryAssign h
  source_realized := L.carryAssign_source_realized h
  base_component_coherent := L.carryAssign_base_component_coherent h

private theorem card_sdiff_add_card_of_subset
    {alpha : Type*} [DecidableEq alpha] {s t : Finset alpha}
    (h : t ⊆ s) : (s \ t).card + t.card = s.card := by
  rw [Finset.card_sdiff, Finset.inter_eq_right.mpr h]
  exact Nat.sub_add_cancel (Finset.card_le_card h)

private theorem expectedDeadMatched_subset_expectedDeadObligation
    (L : Ledger) : L.expectedDeadMatched ⊆ L.expectedDeadObligation := by
  intro d hd
  simp only [expectedDeadMatched, expectedDeadObligation,
    Finset.mem_sdiff] at hd ⊢
  exact ⟨L.oldOptimal.matched_subset hd.1, hd.2⟩

private theorem expectedCarry_subset_expectedPersistentMatched
    (L : Ledger) : L.expectedCarry ⊆ L.expectedPersistentMatched := by
  intro d hd
  simp only [expectedCarry, expectedPersistentMatched, Finset.mem_filter,
    Finset.mem_inter] at hd ⊢
  exact ⟨hd.1, hd.2.1⟩

private theorem oldObligation_card (L : Ledger) (h : L.Checked) :
    (D.obligations oldState).card =
      L.persistObligation.card + L.expectedDeadMatched.card +
        L.deadUnmatched.card := by
  have hpOld : L.expectedPersistObligation ⊆ D.obligations oldState := by
    intro d hd
    simpa [expectedPersistObligation] using hd.1
  have hOldSplit := card_sdiff_add_card_of_subset hpOld
  have hOldDiff :
      D.obligations oldState \ L.expectedPersistObligation =
        L.expectedDeadObligation := by
    ext d
    simp [expectedPersistObligation, expectedDeadObligation]
  rw [hOldDiff] at hOldSplit
  have hDeadSplit := card_sdiff_add_card_of_subset
    (L.expectedDeadMatched_subset_expectedDeadObligation)
  rw [← h.obligation_turnover.2.2] at hDeadSplit
  rw [h.obligation_turnover.1, h.obligation_turnover.2.2]
  omega

private theorem newObligation_card (L : Ledger) (h : L.Checked) :
    (D.obligations newState).card =
      L.persistObligation.card + L.born.card := by
  have hpNew : L.expectedPersistObligation ⊆ D.obligations newState := by
    intro d hd
    simpa [expectedPersistObligation] using hd.2
  have hNewSplit := card_sdiff_add_card_of_subset hpNew
  have hNewDiff :
      D.obligations newState \ L.expectedPersistObligation =
        L.expectedBorn := by
    ext d
    simp [expectedPersistObligation, expectedBorn]
  rw [hNewDiff] at hNewSplit
  rw [h.obligation_turnover.1, h.obligation_turnover.2.1]
  omega

private theorem oldMatched_card (L : Ledger) (h : L.Checked) :
    L.oldOptimal.matched.card =
      L.carry.card + L.expectedDeadMatched.card + L.brokenLive.card := by
  have hpOld : L.expectedPersistentMatched ⊆ L.oldOptimal.matched := by
    intro d hd
    simpa [expectedPersistentMatched] using hd.1
  have hOldSplit := card_sdiff_add_card_of_subset hpOld
  have hOldDiff :
      L.oldOptimal.matched \ L.expectedPersistentMatched =
        L.expectedDeadMatched := by
    ext d
    simp [expectedPersistentMatched, expectedDeadMatched]
  rw [hOldDiff] at hOldSplit
  have hCarrySplit := card_sdiff_add_card_of_subset
    (L.expectedCarry_subset_expectedPersistentMatched)
  rw [← h.carry_partition.2] at hCarrySplit
  rw [h.carry_partition.1, h.carry_partition.2]
  omega

theorem carry_card_le_newOptimal_matched_card
    (L : Ledger) (h : L.Checked) :
    L.carry.card ≤ L.newOptimal.matched.card := by
  have hminimum := D.collisionDefect_le_unmatchedCount (L.carryMatching h)
  rw [h.optimality.2] at hminimum
  rw [CoherentPartialMatching.unmatchedCount_eq_card_sub_matched,
    CoherentPartialMatching.unmatchedCount_eq_card_sub_matched] at hminimum
  have hcarry := Finset.card_le_card (L.carryMatching h).matched_subset
  have hnew := Finset.card_le_card L.newOptimal.matched_subset
  change L.carry.card ≤ L.newOptimal.matched.card
  omega

/-- Matches gained after retaining every carry edge.  This includes newly
free keys, rematching, and coherent relabeling, exactly as in R42. -/
def reoptimizedGain (L : Ledger) : Nat :=
  L.newOptimal.matched.card - L.carry.card

private theorem newMatched_card (L : Ledger) (h : L.Checked) :
    L.newOptimal.matched.card = L.carry.card + L.reoptimizedGain := by
  unfold reoptimizedGain
  omega

/-- The exact signed R42 transport identity.  `expectedDeadMatched` cancels
between obligation and matched-edge turnover, leaving precisely the four
public ledger channels `B + L - U - A_reopt`. -/
theorem defect_delta (L : Ledger) (h : L.Checked) :
    (D.collisionDefect newState : Int) -
        (D.collisionDefect oldState : Int) =
      (L.born.card : Int) + (L.brokenLive.card : Int) -
        (L.deadUnmatched.card : Int) - (L.reoptimizedGain : Int) := by
  have holdLe : L.oldOptimal.matched.card ≤
      (D.obligations oldState).card :=
    Finset.card_le_card L.oldOptimal.matched_subset
  have hnewLe : L.newOptimal.matched.card ≤
      (D.obligations newState).card :=
    Finset.card_le_card L.newOptimal.matched_subset
  have holdDef :
      (D.collisionDefect oldState : Int) =
        ((D.obligations oldState).card : Int) -
          (L.oldOptimal.matched.card : Int) := by
    rw [h.optimality.1,
      CoherentPartialMatching.unmatchedCount_eq_card_sub_matched]
    omega
  have hnewDef :
      (D.collisionDefect newState : Int) =
        ((D.obligations newState).card : Int) -
          (L.newOptimal.matched.card : Int) := by
    rw [h.optimality.2,
      CoherentPartialMatching.unmatchedCount_eq_card_sub_matched]
    omega
  have holdObligation := L.oldObligation_card h
  have hnewObligation := L.newObligation_card h
  have holdMatched := L.oldMatched_card h
  have hnewMatched := L.newMatched_card h
  rw [holdDef, hnewDef]
  omega

/-- Semantic output of a successful checker.  The existential matching keeps
all graph/source realization and base-component coherence inside the production
`CoherentPartialMatching` type. -/
structure Sound (L : Ledger) : Prop where
  exact_ledger : L.Checked
  physical_key_turnover : L.EveryCarryPreservesPhysicalKey
  coherent_carry_exists :
    ∃ M : CoherentPartialMatching D newState, M.matched = L.carry
  defect_delta :
    (D.collisionDefect newState : Int) -
        (D.collisionDefect oldState : Int) =
      (L.born.card : Int) + (L.brokenLive.card : Int) -
        (L.deadUnmatched.card : Int) - (L.reoptimizedGain : Int)

theorem sound_of_check_eq_true (L : Ledger) (hcheck : L.check = true) :
    L.Sound := by
  have h := L.check_eq_true_iff.mp hcheck
  exact
    { exact_ledger := h
      physical_key_turnover := L.everyCarryPreservesPhysicalKey h
      coherent_carry_exists := ⟨L.carryMatching h, rfl⟩
      defect_delta := L.defect_delta h }

theorem defect_delta_of_check_eq_true (L : Ledger)
    (hcheck : L.check = true) :
    (D.collisionDefect newState : Int) -
        (D.collisionDefect oldState : Int) =
      (L.born.card : Int) + (L.brokenLive.card : Int) -
        (L.deadUnmatched.card : Int) - (L.reoptimizedGain : Int) :=
  (L.sound_of_check_eq_true hcheck).defect_delta

#print axioms check_eq_true_iff
#print axioms carryAssign_base_component_coherent
#print axioms defect_delta
#print axioms sound_of_check_eq_true
#print axioms defect_delta_of_check_eq_true

end CheckedDetourTransportLedger
end Gamma
end Erdos23Delta0
