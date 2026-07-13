import Erdos23Delta0.Gamma.LiveDetourEndpointSource

/-!
# Bad-edge incidence forced by a cut-tight active four-state rotor

This file isolates the finite counting core of the graph-specific exclusion.
The graph adapter supplies four pairwise disjoint bad-edge stars, one at each
square vertex.  Cut-tightness and the external active neighbour forced by the
opposite-edge rotor state give at least three edges in each star.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CutTightActiveRotorIncidence

/-- Four bad-edge stars inside one ambient bad-edge set.  Pairwise
disjointness is the exact conclusion of the rotor square geometry: adjacent
square pairs are blue, while opposite pairs have a common blue neighbour and
therefore cannot be edges in a triangle-free graph. -/
structure FourBadStars (Edge : Type*) [DecidableEq Edge] where
  ambient : Finset Edge
  star0 : Finset Edge
  star1 : Finset Edge
  star2 : Finset Edge
  star3 : Finset Edge
  star0_subset : star0 ⊆ ambient
  star1_subset : star1 ⊆ ambient
  star2_subset : star2 ⊆ ambient
  star3_subset : star3 ⊆ ambient
  disjoint01 : Disjoint star0 star1
  disjoint02 : Disjoint star0 star2
  disjoint03 : Disjoint star0 star3
  disjoint12 : Disjoint star1 star2
  disjoint13 : Disjoint star1 star3
  disjoint23 : Disjoint star2 star3
  three_le_star0 : 3 ≤ star0.card
  three_le_star1 : 3 ≤ star1.card
  three_le_star2 : 3 ≤ star2.card
  three_le_star3 : 3 ≤ star3.card

namespace FourBadStars

variable {Edge : Type*} [DecidableEq Edge]

private theorem disjoint_union_left
    {a b c : Finset Edge} (hac : Disjoint a c) (hbc : Disjoint b c) :
    Disjoint (a ∪ b) c := by
  rw [Finset.disjoint_left]
  intro e he habsurd
  rcases Finset.mem_union.mp he with hea | heb
  · exact (Finset.disjoint_left.mp hac) hea habsurd
  · exact (Finset.disjoint_left.mp hbc) heb habsurd

/-- The union of the four stars has the sum of their cardinalities. -/
theorem card_allStars (F : FourBadStars Edge) :
    (((F.star0 ∪ F.star1) ∪ F.star2) ∪ F.star3).card =
      F.star0.card + F.star1.card + F.star2.card + F.star3.card := by
  have h01_2 : Disjoint (F.star0 ∪ F.star1) F.star2 :=
    disjoint_union_left F.disjoint02 F.disjoint12
  have h012_3 : Disjoint ((F.star0 ∪ F.star1) ∪ F.star2) F.star3 :=
    disjoint_union_left
      (disjoint_union_left F.disjoint03 F.disjoint13) F.disjoint23
  rw [Finset.card_union_of_disjoint h012_3,
    Finset.card_union_of_disjoint h01_2,
    Finset.card_union_of_disjoint F.disjoint01]

/-- Four disjoint bad-edge stars of size at least three force twelve ambient
bad edges. -/
theorem twelve_le_ambient_card (F : FourBadStars Edge) :
    12 ≤ F.ambient.card := by
  have hsub : ((F.star0 ∪ F.star1) ∪ F.star2) ∪ F.star3 ⊆ F.ambient := by
    intro e he
    simp only [Finset.mem_union] at he
    rcases he with ((he0 | he1) | he2) | he3
    · exact F.star0_subset he0
    · exact F.star1_subset he1
    · exact F.star2_subset he2
    · exact F.star3_subset he3
  have hcard := Finset.card_le_card hsub
  rw [F.card_allStars] at hcard
  have h0 := F.three_le_star0
  have h1 := F.three_le_star1
  have h2 := F.three_le_star2
  have h3 := F.three_le_star3
  omega

/-- In particular, the proposed `t = 3`, nine-bad-edge rotor window is
empty. -/
theorem not_ambient_card_nine (F : FourBadStars Edge)
    (hnine : F.ambient.card = 9) : False := by
  have := F.twelve_le_ambient_card
  omega

end FourBadStars

/-- Four pairwise-disjoint bad-edge stars with no degree lower bound.  This
weaker carrier is needed for the nonvacuous slack alternative. -/
structure FourDisjointBadStars (Edge : Type*) [DecidableEq Edge] where
  ambient : Finset Edge
  star0 : Finset Edge
  star1 : Finset Edge
  star2 : Finset Edge
  star3 : Finset Edge
  star0_subset : star0 ⊆ ambient
  star1_subset : star1 ⊆ ambient
  star2_subset : star2 ⊆ ambient
  star3_subset : star3 ⊆ ambient
  disjoint01 : Disjoint star0 star1
  disjoint02 : Disjoint star0 star2
  disjoint03 : Disjoint star0 star3
  disjoint12 : Disjoint star1 star2
  disjoint13 : Disjoint star1 star3
  disjoint23 : Disjoint star2 star3

namespace FourDisjointBadStars

variable {Edge : Type*} [DecidableEq Edge]

private theorem disjoint_union_left
    {a b c : Finset Edge} (hac : Disjoint a c) (hbc : Disjoint b c) :
    Disjoint (a ∪ b) c := by
  rw [Finset.disjoint_left]
  intro e he habsurd
  rcases Finset.mem_union.mp he with hea | heb
  · exact (Finset.disjoint_left.mp hac) hea habsurd
  · exact (Finset.disjoint_left.mp hbc) heb habsurd

theorem card_allStars (F : FourDisjointBadStars Edge) :
    (((F.star0 ∪ F.star1) ∪ F.star2) ∪ F.star3).card =
      F.star0.card + F.star1.card + F.star2.card + F.star3.card := by
  have h01_2 : Disjoint (F.star0 ∪ F.star1) F.star2 :=
    disjoint_union_left F.disjoint02 F.disjoint12
  have h012_3 : Disjoint ((F.star0 ∪ F.star1) ∪ F.star2) F.star3 :=
    disjoint_union_left
      (disjoint_union_left F.disjoint03 F.disjoint13) F.disjoint23
  rw [Finset.card_union_of_disjoint h012_3,
    Finset.card_union_of_disjoint h01_2,
    Finset.card_union_of_disjoint F.disjoint01]

/-- Quantitative slack form of the four-star incidence bound.  The graph
adapter supplies `4 <= dM(z) + sigma({z})` at each square vertex. -/
theorem sixteen_le_ambient_card_add_lossSum
    (F : FourDisjointBadStars Edge) (loss0 loss1 loss2 loss3 : Nat)
    (h0 : 4 ≤ F.star0.card + loss0)
    (h1 : 4 ≤ F.star1.card + loss1)
    (h2 : 4 ≤ F.star2.card + loss2)
    (h3 : 4 ≤ F.star3.card + loss3) :
    16 ≤ F.ambient.card + loss0 + loss1 + loss2 + loss3 := by
  have hsub : ((F.star0 ∪ F.star1) ∪ F.star2) ∪ F.star3 ⊆ F.ambient := by
    intro e he
    simp only [Finset.mem_union] at he
    rcases he with ((he0 | he1) | he2) | he3
    · exact F.star0_subset he0
    · exact F.star1_subset he1
    · exact F.star2_subset he2
    · exact F.star3_subset he3
  have hcard := Finset.card_le_card hsub
  rw [F.card_allStars] at hcard
  omega

/-- With nine ambient bad edges, some square singleton loss is at least two.
Unlike the cut-tight exclusion, this conclusion is a genuine alternative. -/
theorem exists_two_le_loss_of_ambient_card_nine
    (F : FourDisjointBadStars Edge) (loss0 loss1 loss2 loss3 : Nat)
    (h0 : 4 ≤ F.star0.card + loss0)
    (h1 : 4 ≤ F.star1.card + loss1)
    (h2 : 4 ≤ F.star2.card + loss2)
    (h3 : 4 ≤ F.star3.card + loss3)
    (hnine : F.ambient.card = 9) :
    2 ≤ loss0 ∨ 2 ≤ loss1 ∨ 2 ≤ loss2 ∨ 2 ≤ loss3 := by
  have hsum := F.sixteen_le_ambient_card_add_lossSum
    loss0 loss1 loss2 loss3 h0 h1 h2 h3
  omega

end FourDisjointBadStars

/-- Arithmetic adapter used at each square vertex.  Four distinct blue
neighbours and singleton cut loss at most one force at least three bad
neighbours. -/
theorem three_le_badDegree_of_four_le_blueDegree_of_cutTight
    (blueDegree badDegree : Nat)
    (hblue : 4 ≤ blueDegree)
    (htight : (blueDegree : Int) - badDegree ≤ 1) :
    3 ≤ badDegree := by
  omega

#print axioms FourBadStars.twelve_le_ambient_card
#print axioms FourBadStars.not_ambient_card_nine
#print axioms FourDisjointBadStars.sixteen_le_ambient_card_add_lossSum
#print axioms FourDisjointBadStars.exists_two_le_loss_of_ambient_card_nine
#print axioms three_le_badDegree_of_four_le_blueDegree_of_cutTight

end CutTightActiveRotorIncidence
end Gamma
end Erdos23Delta0
