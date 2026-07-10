import Erdos23Delta0.Ell5CSReduction

/-!
# Dual strict Hall law for a minimal defect-one support circuit

If an atom family is an inclusion-minimal Hall obstruction of deficiency one,
then every nonempty set of support edges touches at least one more atom than
its own cardinality.  This is the support-side form of factor-criticality.

For the active-component attack, the remaining graph lemma may therefore
produce a nonempty support set `W` touched by at most `|W|` atoms; the theorem
below converts that local witness directly into a contradiction.
-/

namespace Erdos23Delta0
namespace Ell5MinimalCircuitDualHall

open Finset

variable {Atom Edge : Type*} [DecidableEq Atom] [DecidableEq Edge]

/-- Atoms in `S` whose support meets the support-edge set `W`. -/
def incidentAtoms (Erow : Atom → Finset Edge) (S : Finset Atom)
    (W : Finset Edge) : Finset Atom :=
  S.filter fun a => (Erow a ∩ W).Nonempty

/-- **Support-side strict Hall.** Every nonempty edge set in a minimal
defect-one circuit has at least `|W|+1` incident atoms. -/
theorem card_add_one_le_incidentAtoms
    (Erow : Atom → Finset Edge) (S : Finset Atom)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (W : Finset Edge) (hWne : W.Nonempty)
    (hWU : W ⊆ S.biUnion Erow) :
    W.card + 1 ≤ (incidentAtoms Erow S W).card := by
  let U : Finset Edge := S.biUnion Erow
  let I : Finset Atom := incidentAtoms Erow S W
  let T : Finset Atom := S \ I
  obtain ⟨hcard, _hnoPrivate⟩ :=
    Ell5CSReduction.minimal_hall_obstruction_no_private_edge Erow S hlt hmin
  have hISub : I ⊆ S := by
    intro a ha
    exact (Finset.mem_filter.mp ha).1
  obtain ⟨w, hwW⟩ := hWne
  have hwU : w ∈ U := hWU hwW
  change w ∈ S.biUnion Erow at hwU
  rw [Finset.mem_biUnion] at hwU
  obtain ⟨a, haS, hwa⟩ := hwU
  have haI : a ∈ I := by
    change a ∈ incidentAtoms Erow S W
    rw [incidentAtoms, Finset.mem_filter]
    exact ⟨haS, ⟨w, Finset.mem_inter.mpr ⟨hwa, hwW⟩⟩⟩
  have hTSub : T ⊆ S := by
    exact Finset.sdiff_subset
  have hTNe : T ≠ S := by
    intro hEq
    have haT : a ∈ T := by simpa [hEq] using haS
    exact (Finset.mem_sdiff.mp haT).2 haI
  have hTProper : T ⊂ S :=
    Finset.ssubset_iff_subset_ne.mpr ⟨hTSub, hTNe⟩
  have hTU : T.biUnion Erow ⊆ U \ W := by
    intro e he
    rw [Finset.mem_biUnion] at he
    obtain ⟨b, hbT, heb⟩ := he
    change b ∈ S \ I at hbT
    have hbDiff := Finset.mem_sdiff.mp hbT
    have hbS : b ∈ S := hbDiff.1
    have heU : e ∈ U := by
      change e ∈ S.biUnion Erow
      rw [Finset.mem_biUnion]
      exact ⟨b, hbS, heb⟩
    have heNotW : e ∉ W := by
      intro heW
      have hbI : b ∈ I := by
        change b ∈ incidentAtoms Erow S W
        rw [incidentAtoms, Finset.mem_filter]
        exact ⟨hbS, ⟨e, Finset.mem_inter.mpr ⟨heb, heW⟩⟩⟩
      exact hbDiff.2 hbI
    exact Finset.mem_sdiff.mpr ⟨heU, heNotW⟩
  have hTBound : T.card ≤ (U \ W).card :=
    le_trans (hmin T hTProper) (Finset.card_le_card hTU)
  have hTCard : T.card = S.card - I.card := by
    change (S \ I).card = S.card - I.card
    rw [Finset.card_sdiff]
    rw [Finset.inter_eq_left.mpr hISub]
  have hUWCard : (U \ W).card = U.card - W.card := by
    rw [Finset.card_sdiff]
    rw [Finset.inter_eq_left.mpr hWU]
  have hICard : I.card = (incidentAtoms Erow S W).card := rfl
  have hUCard : S.card = U.card + 1 := by
    change S.card = (S.biUnion Erow).card + 1
    exact hcard
  have hICardLe : I.card ≤ S.card := Finset.card_le_card hISub
  have hWCardLe : W.card ≤ U.card := Finset.card_le_card hWU
  rw [hTCard, hUWCard, hICard] at hTBound
  omega

/-- Contrapositive form used by the active-detour proof. -/
theorem not_minimal_of_small_incident_support
    (Erow : Atom → Finset Edge) (S : Finset Atom)
    (hlt : (S.biUnion Erow).card < S.card)
    (W : Finset Edge) (hWne : W.Nonempty)
    (hWU : W ⊆ S.biUnion Erow)
    (hsmall : (incidentAtoms Erow S W).card ≤ W.card) :
    ¬(∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card) := by
  intro hmin
  have hstrict := card_add_one_le_incidentAtoms Erow S hlt hmin W hWne hWU
  omega

end Ell5MinimalCircuitDualHall
end Erdos23Delta0
