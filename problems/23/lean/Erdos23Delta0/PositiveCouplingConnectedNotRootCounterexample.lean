import Erdos23Delta0.PositiveCapacityCornerSplit

/-!
# Connected positive coupling does not force a legal-component root

This two-port model separates the primitive full-escape closure from the
legal-sink component partition. Primitive coupling connects the two ports
and exactly describes the closed shores, while the two ports have distinct
positive-capacity legal sinks. Consequently the positive coupling graph is
connected, but a two-block legal-component partition still exists.

Thus primitive-block closure plus positive-coupling connectedness is
insufficient for the split-or-root classifier. A real extractor theorem must
also make legal-component blocks primitive-saturated, or make every primitive
coupling visible through a common positive-capacity sink.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore
namespace PositiveCouplingConnectedNotRootCounterexample

open PortHall

def tinyLP : BankedWallLP where
  Cut := PUnit
  Atom := PUnit
  Short := PUnit
  Port := Fin 2
  Sink := Fin 2
  cutFintype := inferInstance
  atomFintype := inferInstance
  shortFintype := inferInstance
  portFintype := inferInstance
  sinkFintype := inferInstance
  cov := fun _ _ => 0
  useShort := fun _ _ => 0
  cutPort := fun _ _ => 0
  legal := fun p s => p = s
  legalDecidable := fun _ _ => inferInstance
  cap := fun _ => 1

def allClosure (U : Finset (Fin 2)) : Finset (Fin 2) :=
  if U.Nonempty then Finset.univ else ∅

theorem allClosure_extensive (U : Finset (Fin 2)) :
    U ⊆ allClosure U := by
  by_cases hU : U.Nonempty
  · simp [allClosure, hU]
  · have hUempty : U = ∅ := Finset.not_nonempty_iff_eq_empty.mp hU
    simp [allClosure, hU, hUempty]

theorem allClosure_idempotent (U : Finset (Fin 2)) :
    allClosure (allClosure U) = allClosure U := by
  by_cases hU : U.Nonempty
  · simp [allClosure, hU]
  · simp [allClosure, hU]

theorem allClosure_monotone (U W : Finset (Fin 2)) (hUW : U ⊆ W) :
    allClosure U ⊆ allClosure W := by
  by_cases hU : U.Nonempty
  · have hW : W.Nonempty := hU.mono hUW
    simp [allClosure, hU, hW]
  · simp [allClosure, hU]

def tinyQ : AbstractEscapeQuotient tinyLP where
  QComp := Fin 2
  qDecEq := inferInstance
  qFintype := inferInstance
  fullClosure := allClosure
  exposedPorts := id
  closure_extensive := allClosure_extensive
  closure_idempotent := allClosure_idempotent
  closure_monotone := allClosure_monotone

def primitive (_p _q : Fin 2) : Prop := True

instance primitiveDecidable : DecidableRel primitive :=
  fun _ _ => isTrue trivial

def parent : Finset (Fin 2) := Finset.univ

def load (_p : Fin 2) : ℚ := 2

theorem closed_iff_empty_or_parent (S : Finset (Fin 2)) :
    ClosedPortSet tinyQ S ↔ S = ∅ ∨ S = parent := by
  constructor
  · rintro ⟨U, hUclosed, rfl⟩
    by_cases hU : U.Nonempty
    · right
      have huniv : U = Finset.univ := by
        simpa [tinyQ, allClosure, hU] using hUclosed.symm
      simpa [parent] using huniv
    · left
      exact Finset.not_nonempty_iff_eq_empty.mp hU
  · rintro (rfl | rfl)
    · exact ⟨∅, by simp [tinyQ, allClosure], rfl⟩
    · exact ⟨Finset.univ, by simp [tinyQ, allClosure], rfl⟩

theorem primitiveBlockClosureExact :
    PrimitiveBlockClosureExactOn tinyQ primitive parent := by
  intro S hSparent
  constructor
  · intro hclosed
    rcases (closed_iff_empty_or_parent S).mp hclosed with rfl | rfl
    · intro p q hp
      exact False.elim (by simpa using hp)
    · intro p q _hp _hq _hpq
      simp [parent]
  · intro hsaturated
    by_cases hS : S.Nonempty
    · have huniv : S = Finset.univ := by
        apply Finset.eq_univ_of_forall
        intro q
        obtain ⟨p, hp⟩ := hS
        exact hsaturated hp (by simp [parent])
          (Or.inl (by simp [primitive]))
      apply (closed_iff_empty_or_parent S).2
      exact Or.inr (by simpa [parent] using huniv)
    · apply (closed_iff_empty_or_parent S).2
      exact Or.inl (Finset.not_nonempty_iff_eq_empty.mp hS)

theorem legalNbr_parent :
    legalNbr tinyLP parent = (Finset.univ : Finset (Fin 2)) := by
  ext s
  constructor
  · intro _
    simp
  · intro _
    exact mem_legalNbr.mpr ⟨s, by simp [parent], by simp [tinyLP]⟩

theorem parent_deficiency :
    deficiencyQ tinyLP load parent = 2 := by
  unfold deficiencyQ loadQ capQ load
  rw [legalNbr_parent]
  change (∑ _p : Fin 2, (2 : ℚ)) - ∑ _s : Fin 2, (1 : ℚ) = 2
  norm_num [Fin.sum_univ_two]

theorem parent_hallDeficient :
    HallDeficient tinyLP load parent := by
  unfold HallDeficient
  rw [parent_deficiency]
  norm_num

theorem parent_minimalClosedDeficient :
    MinimalClosedDeficient tinyQ load parent := by
  refine ⟨(closed_iff_empty_or_parent parent).2 (Or.inr rfl),
    parent_hallDeficient, ?_⟩
  intro P hPclosed hPproper
  rcases (closed_iff_empty_or_parent P).mp hPclosed with rfl | rfl
  · rw [show deficiencyQ tinyLP load ∅ = 0 by
      simp [deficiencyQ, loadQ, legalNbr_empty, capQ]]
  · exact False.elim (hPproper.ne rfl)

theorem positiveCoupling_connected (p q : Fin 2) :
    (couplingGraph (positiveCapacityLP tinyLP) primitive parent).Reachable p q := by
  apply coupled_reachable
  exact ⟨by simp [parent], by simp [parent],
    Or.inl (Or.inl (by simp [primitive]))⟩

noncomputable def twoLegalComponents :
    LegalComponentPartition tinyLP parent where
  K := Fin 2
  kDecEq := inferInstance
  kFintype := inferInstance
  ports := fun k => {k}
  sinks := fun k => {k}
  ports_subset := by
    intro k p hp
    simp [parent]
  ports_pairwise_disjoint := by
    intro k l hkl
    simpa using Finset.disjoint_singleton.mpr hkl
  sinks_pairwise_disjoint := by
    intro k l hkl
    simpa using Finset.disjoint_singleton.mpr hkl
  ports_cover := by
    ext p
    simp [parent]
  sinks_cover := by
    rw [legalNbr_parent]
    ext s
    simp
  sinks_eq_nbr := by
    intro k
    ext s
    constructor
    · intro hs
      have hsk : s = k := by simpa using hs
      subst s
      exact mem_legalNbr.mpr ⟨k, by simp, by simp [tinyLP]⟩
    · intro hs
      obtain ⟨p, hp, hleg⟩ := mem_legalNbr.mp hs
      have hpk : p = k := by simpa using hp
      have hps : p = s := by simpa [tinyLP] using hleg
      subst p
      subst s
      simp
  nonempty_ports := by
    intro k
    simp

theorem twoLegalComponents_card :
    Fintype.card twoLegalComponents.K = 2 := by
  change Fintype.card (Fin 2) = 2
  norm_num

theorem noProperSplit :
    ¬Nonempty (ProperClosedBankSplit tinyQ load parent) := by
  rintro ⟨S⟩
  exact no_properClosedBankSplit_of_minimal (Q := tinyQ) load parent
    parent_minimalClosedDeficient S

theorem not_closedPositiveSplitOrRootAt :
    ¬ClosedPositiveSplitOrRootAt tinyQ load := by
  intro hclass
  have hclosed : tinyQ.fullClosure (Finset.univ : Finset (Fin 2)) =
      (Finset.univ : Finset (Fin 2)) := by
    simp [tinyQ, allClosure]
  have h :=
    hclass (Finset.univ : Finset (Fin 2)) hclosed parent_hallDeficient
  rcases h with hsplit | hroot
  · exact noProperSplit hsplit
  · have hone := hroot twoLegalComponents
    rw [twoLegalComponents_card] at hone
    norm_num at hone

/-- Exact two-port obstruction to the connected-positive-component shortcut. -/
theorem connectedPositiveCoupling_but_not_splitOrRoot :
    PrimitiveBlockClosureExactOn tinyQ primitive parent ∧
      (∀ p q : Fin 2,
        (couplingGraph (positiveCapacityLP tinyLP) primitive parent).Reachable p q) ∧
      MinimalClosedDeficient tinyQ load parent ∧
      (∃ D : LegalComponentPartition tinyLP parent, Fintype.card D.K = 2) ∧
      ¬ClosedPositiveSplitOrRootAt tinyQ load := by
  exact ⟨primitiveBlockClosureExact, positiveCoupling_connected,
    parent_minimalClosedDeficient, ⟨twoLegalComponents, twoLegalComponents_card⟩,
    not_closedPositiveSplitOrRootAt⟩

#print axioms primitiveBlockClosureExact
#print axioms parent_minimalClosedDeficient
#print axioms positiveCoupling_connected
#print axioms not_closedPositiveSplitOrRootAt
#print axioms connectedPositiveCoupling_but_not_splitOrRoot

end PositiveCouplingConnectedNotRootCounterexample
end ClosedShore
end Wall
end Erdos23Delta0
