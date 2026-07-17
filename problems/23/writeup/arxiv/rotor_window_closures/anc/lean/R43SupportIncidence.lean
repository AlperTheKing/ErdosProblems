import Mathlib

/-!
# Shape-independent support-incidence closure of the t = 3 rotor window

The authoritative 9/8 hypothesis fixes an eight-edge complete-row support
union.  A fully covered rotating owner contributes three distinct incident
support edges.  Two rotating owners also force three support edges external
to both; three owners already contribute three disjoint incident triples.
This finite core records exactly those graph-derived inputs.
-/

namespace Erdos23Delta0
namespace Gamma
namespace R43SupportIncidence

/-- Three named, pairwise distinct members of a finite edge set. -/
structure ThreeMembers (Edge : Type*) [DecidableEq Edge]
    (edges : Finset Edge) where
  e0 : Edge
  e1 : Edge
  e2 : Edge
  mem0 : e0 ∈ edges
  mem1 : e1 ∈ edges
  mem2 : e2 ∈ edges
  ne01 : e0 ≠ e1
  ne02 : e0 ≠ e2
  ne12 : e1 ≠ e2

namespace ThreeMembers

variable {Edge : Type*} [DecidableEq Edge] {edges : Finset Edge}

theorem three_le_card (T : ThreeMembers Edge edges) : 3 ≤ edges.card := by
  have hsub : {T.e0, T.e1, T.e2} ⊆ edges := by
    intro e he
    simp only [Finset.mem_insert, Finset.mem_singleton] at he
    rcases he with rfl | rfl | rfl
    · exact T.mem0
    · exact T.mem1
    · exact T.mem2
  have hcard := Finset.card_le_card hsub
  have hthree : ({T.e0, T.e1, T.e2} : Finset Edge).card = 3 := by
    simp [T.ne01, T.ne02, T.ne12]
  omega

end ThreeMembers

/-- The complete support union and the three star edges forced by one fully
covered live owner. -/
structure FullyCoveredLiveStar (Edge : Type*) [DecidableEq Edge] where
  support : Finset Edge
  incident : Finset Edge
  incident_subset : incident ⊆ support
  witnesses : ThreeMembers Edge incident

/-- A fully covered live star has support degree at least three. -/
theorem fullyCoveredLiveStar_fullSupportDegree_ge_three
    {Edge : Type*} [DecidableEq Edge]
    (F : FullyCoveredLiveStar Edge) : 3 ≤ F.incident.card :=
  F.witnesses.three_le_card

/-- Exact incidence carrier for two rotating owners.  `external` is the
three-edge tail forced by the three distance-four bad endpoints of the first
owner. -/
structure TwoRotatingOwners (Edge : Type*) [DecidableEq Edge] where
  support : Finset Edge
  atV : Finset Edge
  atM : Finset Edge
  external : Finset Edge
  atV_subset : atV ⊆ support
  atM_subset : atM ⊆ support
  external_subset : external ⊆ support
  disjointVM : Disjoint atV atM
  disjointVE : Disjoint atV external
  disjointME : Disjoint atM external
  vWitnesses : ThreeMembers Edge atV
  mWitnesses : ThreeMembers Edge atM
  externalWitnesses : ThreeMembers Edge external

namespace TwoRotatingOwners

variable {Edge : Type*} [DecidableEq Edge]

private theorem disjoint_union_left
    {a b c : Finset Edge} (hac : Disjoint a c) (hbc : Disjoint b c) :
    Disjoint (a ∪ b) c := by
  rw [Finset.disjoint_left]
  intro e he hec
  rcases Finset.mem_union.mp he with hea | heb
  · exact (Finset.disjoint_left.mp hac) hea hec
  · exact (Finset.disjoint_left.mp hbc) heb hec

theorem nine_le_support_card (F : TwoRotatingOwners Edge) :
    9 ≤ F.support.card := by
  have hsub : (F.atV ∪ F.atM) ∪ F.external ⊆ F.support := by
    intro e he
    simp only [Finset.mem_union] at he
    rcases he with (heV | heM) | heE
    · exact F.atV_subset heV
    · exact F.atM_subset heM
    · exact F.external_subset heE
  have hcard := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint
      (disjoint_union_left F.disjointVE F.disjointME),
    Finset.card_union_of_disjoint F.disjointVM] at hcard
  have hV := F.vWitnesses.three_le_card
  have hM := F.mWitnesses.three_le_card
  have hE := F.externalWitnesses.three_le_card
  omega

/-- Two rotating owners cannot fit inside an eight-edge 9/8 support union. -/
theorem twoRotatingOwners_force_nine_supportEdges
    (F : TwoRotatingOwners Edge) (height : F.support.card = 8) : False := by
  have := F.nine_le_support_card
  omega

end TwoRotatingOwners

/-- Exact incidence carrier for three rotating owners. -/
structure ThreeRotatingOwners (Edge : Type*) [DecidableEq Edge] where
  support : Finset Edge
  at0 : Finset Edge
  at1 : Finset Edge
  at2 : Finset Edge
  at0_subset : at0 ⊆ support
  at1_subset : at1 ⊆ support
  at2_subset : at2 ⊆ support
  disjoint01 : Disjoint at0 at1
  disjoint02 : Disjoint at0 at2
  disjoint12 : Disjoint at1 at2
  witnesses0 : ThreeMembers Edge at0
  witnesses1 : ThreeMembers Edge at1
  witnesses2 : ThreeMembers Edge at2

namespace ThreeRotatingOwners

variable {Edge : Type*} [DecidableEq Edge]

private theorem disjoint_union_left
    {a b c : Finset Edge} (hac : Disjoint a c) (hbc : Disjoint b c) :
    Disjoint (a ∪ b) c := by
  rw [Finset.disjoint_left]
  intro e he hec
  rcases Finset.mem_union.mp he with hea | heb
  · exact (Finset.disjoint_left.mp hac) hea hec
  · exact (Finset.disjoint_left.mp hbc) heb hec

theorem nine_le_support_card (F : ThreeRotatingOwners Edge) :
    9 ≤ F.support.card := by
  have hsub : (F.at0 ∪ F.at1) ∪ F.at2 ⊆ F.support := by
    intro e he
    simp only [Finset.mem_union] at he
    rcases he with (he0 | he1) | he2
    · exact F.at0_subset he0
    · exact F.at1_subset he1
    · exact F.at2_subset he2
  have hcard := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint
      (disjoint_union_left F.disjoint02 F.disjoint12),
    Finset.card_union_of_disjoint F.disjoint01] at hcard
  have h0 := F.witnesses0.three_le_card
  have h1 := F.witnesses1.three_le_card
  have h2 := F.witnesses2.three_le_card
  omega

/-- Three rotating owners cannot fit inside an eight-edge 9/8 support union. -/
theorem threeRotatingOwners_force_nine_supportEdges
    (F : ThreeRotatingOwners Edge) (height : F.support.card = 8) : False := by
  have := F.nine_le_support_card
  omega

end ThreeRotatingOwners

/-- After the four-owner `|M| >= 12` exclusion, a nontrivial t=3 bounce has
exactly two or three owners.  These are the two graph-derived incidence
carriers above. -/
inductive T3BalancedDeficiencyRotor (Edge : Type*) [DecidableEq Edge] where
  | two (data : TwoRotatingOwners Edge) (support_card : data.support.card = 8)
  | three (data : ThreeRotatingOwners Edge) (support_card : data.support.card = 8)

/-- Shape-independent finite closure of the t=3 balanced live rotor. -/
theorem no_t3_balancedDeficiencyRotor
    {Edge : Type*} [DecidableEq Edge]
    (R : T3BalancedDeficiencyRotor Edge) : False := by
  cases R with
  | two data h => exact data.twoRotatingOwners_force_nine_supportEdges h
  | three data h => exact data.threeRotatingOwners_force_nine_supportEdges h

#print axioms fullyCoveredLiveStar_fullSupportDegree_ge_three
#print axioms TwoRotatingOwners.twoRotatingOwners_force_nine_supportEdges
#print axioms ThreeRotatingOwners.threeRotatingOwners_force_nine_supportEdges
#print axioms no_t3_balancedDeficiencyRotor

end R43SupportIncidence
end Gamma
end Erdos23Delta0
