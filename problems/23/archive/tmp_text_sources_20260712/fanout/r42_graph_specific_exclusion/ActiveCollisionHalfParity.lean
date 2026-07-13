import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-!
# R42 production collision-half parity

The abstract R42 source-swap countermodel has five collision obligations.
This file records the first literal production invariant that it violates:
after active-scope filtering, collision obligations still occur in exact
`Fin 2` half-pairs.
-/

namespace Erdos23Delta0
namespace Gamma
namespace R42GraphSpecificExclusion

noncomputable section

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

attribute [local instance] Classical.propDecidable

/-- A collision obligation with the physical half bit erased. -/
structure ActiveCollisionStem (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  owner : Fin G.n
  other : Fin G.n
  copy : Fin (pairCount omega owner.1 other.1 - 1)
  active_owner : ActiveOwner G c omega owner
deriving Fintype

/-- Active-scope filtering depends on the owner, not on the physical half.
Consequently the real collision carrier is exactly a stem times `Fin 2`. -/
noncomputable def activeCollisionHalfEquivStemProd
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    ActiveCollisionHalf G c omega ≃
      ActiveCollisionStem G c omega × Fin 2 where
  toFun d :=
    ( { owner := d.1.owner
        other := d.1.other
        copy := d.1.copy
        active_owner := d.2 },
      d.1.half )
  invFun d :=
    ⟨{ owner := d.1.owner
       other := d.1.other
       copy := d.1.copy
       half := d.2 },
      d.1.active_owner⟩
  left_inv d := by
    cases d with
    | mk d hd =>
        cases d
        rfl
  right_inv d := by
    cases d with
    | mk stem half =>
        cases stem
        rfl

theorem activeCollisionHalf_card_eq_stem_mul_two
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    Fintype.card (ActiveCollisionHalf G c omega) =
      Fintype.card (ActiveCollisionStem G c omega) * 2 := by
  rw [Fintype.card_congr (activeCollisionHalfEquivStemProd G c omega)]
  simp

/-- In particular, the complete production collision-obligation set cannot
have the five elements used by the abstract R42 matching countermodel. -/
theorem activeCollisionHalf_card_ne_five
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    Fintype.card (ActiveCollisionHalf G c omega) ≠ 5 := by
  rw [activeCollisionHalf_card_eq_stem_mul_two]
  omega

theorem pairCount_comm {bads : List BadEdgeData}
    (omega : RowChoice bads) (x y : Nat) :
    pairCount omega x y = pairCount omega y x := by
  unfold pairCount
  congr 2
  funext row
  simp only [decide_eq_decide]
  tauto

private def halfOne : Fin 2 := ⟨1, by omega⟩

private def turnoverSource
    {G : GraphData} {bads : List BadEdgeData} {omega : RowChoice bads}
    (left right : Fin G.n) (hne : left ≠ right)
    (hfree : pairCount omega left.1 right.1 = 0) :
    FreeHalf G omega where
  sourceX := left
  sourceY := right
  half := halfOne
  distinct := hne
  free := hfree

/-- Once P2/P4/P5 are geometrically unavailable on the two active-edge
bases, universal eligibility for all four turnover orientations forces a
single external P3 owner seeing all three square vertices. -/
theorem four_turnover_p13_owner_classification
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (omega : RowChoice bads) (owner m x y : Fin G.n)
    (hmx_ne : m ≠ x) (hmy_ne : m ≠ y)
    (hmx : pairCount omega m.1 x.1 = 0)
    (hmy : pairCount omega m.1 y.1 = 0)
    (h_mx : EligibleOwner G c owner
      (turnoverSource m x hmx_ne hmx))
    (h_xm : EligibleOwner G c owner
      (turnoverSource x m hmx_ne.symm
        (by simpa [pairCount_comm] using hmx)))
    (h_my : EligibleOwner G c owner
      (turnoverSource m y hmy_ne hmy))
    (h_ym : EligibleOwner G c owner
      (turnoverSource y m hmy_ne.symm
        (by simpa [pairCount_comm] using hmy))) :
    owner ≠ m ∧ owner ≠ x ∧ owner ≠ y ∧
      0 < pairCount omega owner.1 m.1 ∧
      0 < pairCount omega owner.1 x.1 ∧
      0 < pairCount omega owner.1 y.1 := by
  change m = owner ∨
    (0 < pairCount omega owner.1 m.1 ∧
      0 < pairCount omega owner.1 x.1 ∧
      0 ≤ sigma G c [m.1, x.1]) at h_mx
  change x = owner ∨
    (0 < pairCount omega owner.1 x.1 ∧
      0 < pairCount omega owner.1 m.1 ∧
      0 ≤ sigma G c [x.1, m.1]) at h_xm
  change m = owner ∨
    (0 < pairCount omega owner.1 m.1 ∧
      0 < pairCount omega owner.1 y.1 ∧
      0 ≤ sigma G c [m.1, y.1]) at h_my
  change y = owner ∨
    (0 < pairCount omega owner.1 y.1 ∧
      0 < pairCount omega owner.1 m.1 ∧
      0 ≤ sigma G c [y.1, m.1]) at h_ym
  have hom : owner ≠ m := by
    intro heq
    subst owner
    rcases h_xm with hfirst | hcomp
    · exact hmx_ne hfirst.symm
    · omega
  have hox : owner ≠ x := by
    intro heq
    subst owner
    rcases h_mx with hfirst | hcomp
    · exact hmx_ne hfirst
    · have hzero : pairCount omega x.1 m.1 = 0 := by
        simpa [pairCount_comm] using hmx
      omega
  have hoy : owner ≠ y := by
    intro heq
    subst owner
    rcases h_my with hfirst | hcomp
    · exact hmy_ne hfirst
    · have hzero : pairCount omega y.1 m.1 = 0 := by
        simpa [pairCount_comm] using hmy
      omega
  rcases h_mx with hfirst | hcomp
  · exact (hom hfirst.symm).elim
  · rcases h_my with hfirst' | hcomp'
    · exact (hom hfirst'.symm).elim
    · exact ⟨hom, hox, hoy, hcomp.1, hcomp.2.1, hcomp'.2.1⟩

/-- Arithmetic core of the graph-specific cut-parity obstruction.  If two
alternating five-vertex rows share a triple with `k` vertices on one shore,
and their two private vertices lie respectively on that shore and its
opposite, then both rows cannot have the required `2/3` shore split. -/
theorem shared_triple_opposite_pairs_impossible
    (k : Nat)
    (first_row_balanced : k + 2 = 2 ∨ k + 2 = 3)
    (second_row_balanced : k = 2 ∨ k = 3) : False := by
  omega

#print axioms activeCollisionHalfEquivStemProd
#print axioms activeCollisionHalf_card_eq_stem_mul_two
#print axioms activeCollisionHalf_card_ne_five
#print axioms four_turnover_p13_owner_classification
#print axioms shared_triple_opposite_pairs_impossible

end
end R42GraphSpecificExclusion
end Gamma
end Erdos23Delta0
