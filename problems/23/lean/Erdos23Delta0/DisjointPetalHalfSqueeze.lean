import Erdos23Delta0.RootLayerHalfSqueeze
import Erdos23Delta0.MaxCutVertexIneq

/-!
# Pairwise-disjoint petal half-layer

This module proves the concrete finite-set facts behind the fractional
root-layer argument. Pairwise-disjoint vertex shores put half-load at most
one on every graph edge. If every abstract short/port coefficient is the
actual boundary indicator and every port has an injective legal own Door of
capacity at least one, these facts instantiate `HalfLayerRouted`.

The module does not assert that a root-layer witness exists.
-/

namespace Erdos23Delta0
namespace DisjointPetalHalfSqueeze

open scoped BigOperators
open MaxCutVertexIneq
open Wall

variable {V : Type*} [DecidableEq V]

def containingIndices {q : Nat} (shore : Fin q → Finset V) (v : V) : Finset (Fin q) :=
  Finset.univ.filter fun i => v ∈ shore i

def boundaryIndices {q : Nat} (shore : Fin q → Finset V)
    (e : Sym2 V) : Finset (Fin q) :=
  Finset.univ.filter fun i => edgeBoundary (shore i) e = true

def halfBoundaryLoad {q : Nat} (shore : Fin q → Finset V) (e : Sym2 V) : ℚ :=
  ∑ i : Fin q, if edgeBoundary (shore i) e = true then 1 / 2 else 0

theorem containingIndices_card_le_one {q : Nat} (shore : Fin q → Finset V)
    (hdisjoint : ∀ i j, i ≠ j → Disjoint (shore i) (shore j)) (v : V) :
    (containingIndices shore v).card ≤ 1 := by
  rw [Finset.card_le_one]
  intro i hi j hj
  have hiv : v ∈ shore i := (Finset.mem_filter.mp hi).2
  have hjv : v ∈ shore j := (Finset.mem_filter.mp hj).2
  by_contra hij
  exact (Finset.disjoint_left.mp (hdisjoint i j hij)) hiv hjv

private theorem boundaryIndices_subset_endpoints {q : Nat}
    (shore : Fin q → Finset V) {u v : V} :
    boundaryIndices shore s(u, v) ⊆
      containingIndices shore u ∪ containingIndices shore v := by
  intro i hi
  have hb : edgeBoundary (shore i) s(u, v) = true :=
    (Finset.mem_filter.mp hi).2
  by_cases hu : u ∈ shore i
  · exact Finset.mem_union_left _ (Finset.mem_filter.mpr ⟨Finset.mem_univ _, hu⟩)
  · have hv : v ∈ shore i := by
      by_contra hv
      simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hu, hv] at hb
    exact Finset.mem_union_right _ (Finset.mem_filter.mpr ⟨Finset.mem_univ _, hv⟩)

theorem boundaryIndices_card_le_two {q : Nat} (shore : Fin q → Finset V)
    (hdisjoint : ∀ i j, i ≠ j → Disjoint (shore i) (shore j))
    (e : Sym2 V) :
    (boundaryIndices shore e).card ≤ 2 := by
  refine Sym2.inductionOn e ?_
  intro u v
  calc
    (boundaryIndices shore s(u, v)).card ≤
        (containingIndices shore u ∪ containingIndices shore v).card :=
      Finset.card_le_card (boundaryIndices_subset_endpoints shore)
    _ ≤ (containingIndices shore u).card + (containingIndices shore v).card :=
      Finset.card_union_le _ _
    _ ≤ 1 + 1 := Nat.add_le_add
      (containingIndices_card_le_one shore hdisjoint u)
      (containingIndices_card_le_one shore hdisjoint v)
    _ = 2 := rfl

theorem halfBoundaryLoad_nonneg {q : Nat} (shore : Fin q → Finset V)
    (e : Sym2 V) :
    0 ≤ halfBoundaryLoad shore e := by
  unfold halfBoundaryLoad
  exact Finset.sum_nonneg fun i _ => by split <;> norm_num

theorem halfBoundaryLoad_le_one {q : Nat} (shore : Fin q → Finset V)
    (hdisjoint : ∀ i j, i ≠ j → Disjoint (shore i) (shore j))
    (e : Sym2 V) :
    halfBoundaryLoad shore e ≤ 1 := by
  have hcard : (boundaryIndices shore e).card ≤ 2 :=
    boundaryIndices_card_le_two shore hdisjoint e
  have hcardQ : ((boundaryIndices shore e).card : ℚ) ≤ 2 := by
    exact_mod_cast hcard
  unfold halfBoundaryLoad
  change (∑ i ∈ Finset.univ,
    if edgeBoundary (shore i) e = true then (1 / 2 : ℚ) else 0) ≤ 1
  rw [← Finset.sum_filter]
  change (∑ _i ∈ boundaryIndices shore e, (1 / 2 : ℚ)) ≤ 1
  simp only [Finset.sum_const, nsmul_eq_mul]
  nlinarith

variable {I : BankedWallLP} {q : Nat}

/-- Concrete graph-shore data for a half-layer over an abstract wall LP. -/
structure DisjointPetalRouteData (I : BankedWallLP) (walls : Fin q → I.Cut) where
  shore : Fin q → Finset V
  shortEdge : I.Short → Sym2 V
  portEdge : I.Port → Sym2 V
  petals_disjoint : ∀ i j, i ≠ j → Disjoint (shore i) (shore j)
  short_is_boundary : ∀ i f,
    I.useShort (walls i) f = if edgeBoundary (shore i) (shortEdge f) = true then 1 else 0
  port_is_boundary : ∀ i p,
    I.cutPort (walls i) p = if edgeBoundary (shore i) (portEdge p) = true then 1 else 0
  door : I.Port → I.Sink
  door_injective : Function.Injective door
  door_legal : ∀ p, I.legal p (door p)
  door_capacity : ∀ p, 1 ≤ I.cap (door p)
  sink_capacity_nonneg : ∀ s, 0 ≤ I.cap s

private theorem half_sum_boundary_indicator {q : Nat}
    (shore : Fin q → Finset V) (e : Sym2 V) :
    (1 / 2 : ℚ) *
        ∑ i : Fin q, (if edgeBoundary (shore i) e = true then 1 else 0) =
      halfBoundaryLoad shore e := by
  unfold halfBoundaryLoad
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  by_cases h : edgeBoundary (shore i) e = true <;> simp [h]

/-- Pairwise-disjoint actual petal shores with injective own Doors provide all
half-layer routing inequalities required by `RootLayerHalfSqueeze`. -/
noncomputable def routedOfDisjointPetals (walls : Fin q → I.Cut)
    (D : DisjointPetalRouteData (V := V) I walls) :
    HalfLayerRouted I walls := by
  classical
  let load : I.Port → ℚ := fun p => halfBoundaryLoad D.shore (D.portEdge p)
  let rho : I.Port → I.Sink → ℚ := fun p s => if D.door p = s then load p else 0
  refine
    { rho := rho
      rho_nonneg := ?_
      rho_legal := ?_
      short_half_le := ?_
      port_half_routed := ?_
      sink_capacity := ?_ }
  · intro p s
    by_cases h : D.door p = s
    · simp [rho, h, load, halfBoundaryLoad_nonneg]
    · simp [rho, h]
  · intro p s hrs
    by_cases h : D.door p = s
    · simpa [h] using D.door_legal p
    · simp [rho, h] at hrs
  · intro f
    rw [show (∑ i : Fin q, I.useShort (walls i) f) =
        ∑ i : Fin q,
          (if edgeBoundary (D.shore i) (D.shortEdge f) = true then 1 else 0) by
      exact Finset.sum_congr rfl fun i _ => D.short_is_boundary i f]
    rw [half_sum_boundary_indicator]
    exact halfBoundaryLoad_le_one D.shore D.petals_disjoint (D.shortEdge f)
  · intro p
    rw [show (∑ i : Fin q, I.cutPort (walls i) p) =
        ∑ i : Fin q,
          (if edgeBoundary (D.shore i) (D.portEdge p) = true then 1 else 0) by
      exact Finset.sum_congr rfl fun i _ => D.port_is_boundary i p]
    rw [half_sum_boundary_indicator]
    change load p ≤ ∑ s : I.Sink, rho p s
    rw [Finset.sum_eq_single (D.door p)]
    · simp [rho]
    · intro s _ hs
      have hne : D.door p ≠ s := Ne.symm hs
      simp [rho, hne]
    · simp
  · intro s
    by_cases hs : ∃ p, D.door p = s
    · obtain ⟨p, hp⟩ := hs
      change (∑ p' : I.Port, rho p' s) ≤ I.cap s
      rw [Finset.sum_eq_single p]
      · have hload : load p ≤ 1 :=
          halfBoundaryLoad_le_one D.shore D.petals_disjoint (D.portEdge p)
        simp [rho, hp]
        exact hload.trans (by simpa [hp] using D.door_capacity p)
      · intro p' _ hp'ne
        have hdoor : D.door p' ≠ s := by
          intro heq
          apply hp'ne
          exact D.door_injective (heq.trans hp.symm)
        simp [rho, hdoor]
      · simp
    · change (∑ p : I.Port, rho p s) ≤ I.cap s
      have hzero : (∑ p : I.Port, rho p s) = 0 := by
        apply Finset.sum_eq_zero
        intro p _
        have hdoor : D.door p ≠ s := fun h => hs ⟨p, h⟩
        simp [rho, hdoor]
      rw [hzero]
      exact D.sink_capacity_nonneg s

/-- Concrete disjoint-petal/own-Door corollary of the generic half-layer
theorem. -/
theorem noStrictDual_of_disjointPetalTwoCover
    (d : Dual I) (hd : d.Checked) (walls : Fin q → I.Cut)
    (htwo : ∀ a : I.Atom, 0 < d.alpha a →
      ∑ i : Fin q, I.cov (walls i) a = 2)
    (D : DisjointPetalRouteData (V := V) I walls) :
    ¬ d.StrictGap :=
  noStrictDual_of_halfLayerTwoCover d hd walls htwo
    (routedOfDisjointPetals walls D)

#print axioms boundaryIndices_card_le_two
#print axioms halfBoundaryLoad_le_one
#print axioms routedOfDisjointPetals
#print axioms noStrictDual_of_disjointPetalTwoCover

end DisjointPetalHalfSqueeze
end Erdos23Delta0
