import Erdos23Delta0.Gamma.Pattern5StaticOwnership

/-!
# Checked collision-defect trades

This module isolates the finite argument used by the R33 row-selection
frontier.  A row state supplies a finite set of collision obligations, a
component label for each obligation, and an explicit graph-realization
relation for source halves.  A partial matching chooses some obligations,
injects them into canonical `(base, half)` keys, proves every chosen source is
graph-realized, and imposes the existing base-key component coherence law.

The collision defect is the minimum number of unmatched obligations among
such coherent partial matchings.  A checked trade contains an arbitrary
simultaneous row change, an old matching witnessing the old defect, and a new
coherent matching with fewer unmatched obligations.  Its defect decrease is
then purely finite bookkeeping.

No row state, graph realization, source relation, or checked trade is
constructed here.  In particular, this module does not assert canonical
collision feasibility.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedCollisionDefectTrade

set_option linter.dupNamespace false

universe uState uObligation uSource uComp uChange

/-- Finite collision data attached to each row state.  `sourceRealized` is a
caller-supplied graph predicate; it should include all source-family legality
and reservation conditions required by the concrete application. -/
structure Data
    (State : Type uState) (Obligation : Type uObligation)
    (SourceBase : Type uSource) (Comp : Type uComp) where
  obligations : State → Finset Obligation
  component : State → Obligation → Comp
  sourceRealized : State → Obligation → (SourceBase × Fin 2) → Prop

variable {State : Type uState} {Obligation : Type uObligation}
variable {SourceBase : Type uSource} {Comp : Type uComp}
variable [DecidableEq Obligation]

/-- A partial no-reuse assignment into canonical source halves.  The
assignment is checked only on `matched`; all remaining obligations are the
defect certificate. -/
structure CoherentPartialMatching
    (D : Data State Obligation SourceBase Comp) (state : State) where
  matched : Finset Obligation
  matched_subset : matched ⊆ D.obligations state
  assign : {d // d ∈ matched} ↪ (SourceBase × Fin 2)
  source_realized : ∀ d, D.sourceRealized state d.1 (assign d)
  base_component_coherent :
    Pattern5StaticOwnership.BaseKeyComponentCoherent assign
      (fun d => D.component state d.1)

namespace CoherentPartialMatching

variable {D : Data State Obligation SourceBase Comp} {state : State}

/-- Obligations not covered by this partial matching. -/
def unmatched (M : CoherentPartialMatching D state) : Finset Obligation :=
  D.obligations state \ M.matched

/-- The checked defect of one partial matching. -/
def unmatchedCount (M : CoherentPartialMatching D state) : Nat :=
  M.unmatched.card

theorem unmatchedCount_eq_card_sub_matched
    (M : CoherentPartialMatching D state) :
    M.unmatchedCount = (D.obligations state).card - M.matched.card := by
  rw [unmatchedCount, unmatched, Finset.card_sdiff]
  rw [Finset.inter_eq_left.mpr M.matched_subset]

/-- The empty assignment supplies the nonempty candidate family used to
define collision defect.  It claims no graph source exists. -/
def empty (D : Data State Obligation SourceBase Comp) (state : State) :
    CoherentPartialMatching D state where
  matched := ∅
  matched_subset := by simp
  assign :=
    { toFun := fun d => (Finset.notMem_empty d.1 d.2).elim
      inj' := fun d _ => (Finset.notMem_empty d.1 d.2).elim }
  source_realized := by
    intro d
    exact (Finset.notMem_empty d.1 d.2).elim
  base_component_coherent := by
    intro d
    exact (Finset.notMem_empty d.1 d.2).elim

@[simp] theorem unmatched_empty
    (D : Data State Obligation SourceBase Comp) (state : State) :
    (empty D state).unmatched = D.obligations state := by
  simp [unmatched, empty]

@[simp] theorem unmatchedCount_empty
    (D : Data State Obligation SourceBase Comp) (state : State) :
    (empty D state).unmatchedCount = (D.obligations state).card := by
  simp [unmatchedCount]

end CoherentPartialMatching

namespace Data

private theorem exists_unmatchedCount
    (D : Data State Obligation SourceBase Comp) (state : State) :
    ∃ n, ∃ M : CoherentPartialMatching D state, M.unmatchedCount = n := by
  let M := CoherentPartialMatching.empty D state
  exact ⟨M.unmatchedCount, M, rfl⟩

/-- Honest collision defect: the minimum unmatched count over all coherent,
graph-realized partial matchings for this row state. -/
noncomputable def collisionDefect
    (D : Data State Obligation SourceBase Comp) (state : State) : Nat :=
  by
    classical
    exact Nat.find (exists_unmatchedCount D state)

/-- Every supplied coherent partial matching is an upper bound on the honest
collision defect. -/
theorem collisionDefect_le_unmatchedCount
    (D : Data State Obligation SourceBase Comp)
    {state : State} (M : CoherentPartialMatching D state) :
    D.collisionDefect state ≤ M.unmatchedCount := by
  classical
  exact Nat.find_min' (exists_unmatchedCount D state) ⟨M, rfl⟩

/-- The minimum has a finite matching witness.  This is only minimization
inside a fixed caller-supplied row state; it constructs neither a row state nor
a graph realization. -/
theorem exists_matching_realizing_collisionDefect
    (D : Data State Obligation SourceBase Comp) (state : State) :
    ∃ M : CoherentPartialMatching D state,
      D.collisionDefect state = M.unmatchedCount := by
  classical
  rcases Nat.find_spec (exists_unmatchedCount D state) with ⟨M, hM⟩
  exact ⟨M, hM.symm⟩

/-- Zero defect at a fixed caller-supplied state is exactly the existence of
a total coherent matching.  The right side still contains every concrete
`sourceRealized` proof; no graph realization or row state is constructed. -/
theorem collisionDefect_eq_zero_iff_exists_total
    (D : Data State Obligation SourceBase Comp) (state : State) :
    D.collisionDefect state = 0 ↔
      ∃ M : CoherentPartialMatching D state,
        M.matched = D.obligations state := by
  constructor
  · intro hzero
    obtain ⟨M, hM⟩ := D.exists_matching_realizing_collisionDefect state
    refine ⟨M, Finset.eq_of_subset_of_card_le M.matched_subset ?_⟩
    apply Nat.le_of_sub_eq_zero
    rw [← CoherentPartialMatching.unmatchedCount_eq_card_sub_matched M,
      ← hM, hzero]
  · rintro ⟨M, htotal⟩
    apply Nat.eq_zero_of_le_zero
    calc
      D.collisionDefect state ≤ M.unmatchedCount :=
        D.collisionDefect_le_unmatchedCount M
      _ = 0 := by
        rw [CoherentPartialMatching.unmatchedCount_eq_card_sub_matched,
          htotal]
        simp

theorem collisionDefect_le_obligationCard
    (D : Data State Obligation SourceBase Comp) (state : State) :
    D.collisionDefect state ≤ (D.obligations state).card := by
  simpa using D.collisionDefect_le_unmatchedCount
    (CoherentPartialMatching.empty D state)

end Data

/-- A graph-checked simultaneous row change together with old and new
coherent partial matchings.  The old matching certifies the exact old defect;
the new matching need not be optimal. -/
structure CheckedCollisionDefectTrade
    (D : Data State Obligation SourceBase Comp)
    (stateRealized : State → Prop)
    (ChangeWitness : Type uChange)
    (simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop)
    (oldState : State) where
  old_state_realized : stateRealized oldState
  newState : State
  new_state_realized : stateRealized newState
  rowChange : ChangeWitness
  row_change_realized :
    simultaneousRowChangeRealized oldState newState rowChange
  oldMatching : CoherentPartialMatching D oldState
  old_defect_eq_unmatched :
    D.collisionDefect oldState = oldMatching.unmatchedCount
  newMatching : CoherentPartialMatching D newState
  fewer_unmatched : newMatching.unmatchedCount < oldMatching.unmatchedCount

/-- A checked simultaneous trade strictly lowers the honest collision defect.
The only graph content used is the realization evidence already stored in the
trade and its two matchings. -/
theorem defect_lt
    {D : Data State Obligation SourceBase Comp}
    {stateRealized : State → Prop}
    {ChangeWitness : Type uChange}
    {simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop}
    {oldState : State}
    (T : CheckedCollisionDefectTrade D stateRealized ChangeWitness
      simultaneousRowChangeRealized oldState) :
    D.collisionDefect T.newState < D.collisionDefect oldState := by
  calc
    D.collisionDefect T.newState ≤ T.newMatching.unmatchedCount :=
      D.collisionDefect_le_unmatchedCount T.newMatching
    _ < T.oldMatching.unmatchedCount := T.fewer_unmatched
    _ = D.collisionDefect oldState := T.old_defect_eq_unmatched.symm

/-- The old exact-defect field can equivalently be audited as demand minus
the number of obligations covered by the old coherent matching. -/
theorem old_defect_eq_demand_sub_matched
    {D : Data State Obligation SourceBase Comp}
    {stateRealized : State → Prop}
    {ChangeWitness : Type uChange}
    {simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop}
    {oldState : State}
    (T : CheckedCollisionDefectTrade D stateRealized ChangeWitness
      simultaneousRowChangeRealized oldState) :
    D.collisionDefect oldState =
      (D.obligations oldState).card - T.oldMatching.matched.card := by
  rw [T.old_defect_eq_unmatched,
    CoherentPartialMatching.unmatchedCount_eq_card_sub_matched]

end CheckedCollisionDefectTrade
end Gamma
end Erdos23Delta0
