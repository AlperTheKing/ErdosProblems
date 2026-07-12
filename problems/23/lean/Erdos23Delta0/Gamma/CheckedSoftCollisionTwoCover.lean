import Erdos23Delta0.CollisionResidualIdentity
import Erdos23Delta0.Gamma.MinimumDemandCollisionHall

/-!
# Coherence-free collision flow with adaptive active-edge caps

This module records only the new R53 capacity layer. It does not duplicate
the ordinary matching and Hall interfaces already provided by
`MinimumDemandCollisionHall` and `ActiveScopedMinimumExchange`.

An active undirected edge has two orientations and two half keys, hence four
physical keys. Every physical key has capacity one, while the four keys over
one active edge have aggregate capacity two. A non-active ordered base has
two half keys, each retaining its direct unit capacity.

The counting theorem is independent of component coherence and of the
eligibility relation. Once collision obligations account for twice the
signed collision mass and represented source bases fit inside the signed
free mass, a feasible fractional flow gives
`collisionMass + card ActiveEdge <= freeMass` and hence residual
nonnegativity through the existing exact identity.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedSoftCollisionTwoCover

open scoped BigOperators
open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

universe uObligation uEdge uBase

/-- Physical keys in the adaptive-reservation model. The active summand has
an orientation bit and every base then has a half bit. -/
abbrev EdgeCappedPhysicalKey
    (ActiveEdge : Type uEdge) (DirectBase : Type uBase) :=
  ((ActiveEdge × Fin 2) ⊕ DirectBase) × Fin 2

/-- A fractional collision flow on caller-supplied eligibility arcs.
Eligibility is retained for the graph provider, but the counting proof uses
only demand, nonnegativity, and the two capacity constraints. -/
structure FractionalCollisionFlowWithEdgeCaps
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation → EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) where
  flow : Obligation → EdgeCappedPhysicalKey ActiveEdge DirectBase → ℚ
  nonneg : ∀ obligation key, 0 ≤ flow obligation key
  obligation_demand : ∀ obligation, ∑ key, flow obligation key = 1
  key_capacity : ∀ key, (∑ obligation, flow obligation key) ≤ 1
  active_edge_capacity : ∀ edge,
    (∑ orientation : Fin 2, ∑ half : Fin 2,
      ∑ obligation, flow obligation ((Sum.inl (edge, orientation)), half)) ≤ 2
  supported : ∀ obligation key, 0 < flow obligation key → Eligible obligation key

namespace FractionalCollisionFlowWithEdgeCaps

variable {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
variable {DirectBase : Type uBase}
variable [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
variable {Eligible : Obligation → EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop}

variable (F : FractionalCollisionFlowWithEdgeCaps Eligible)

/-- Integrality is a property of the same flow object, not a second matching
interface. The counting theorem below does not require it. -/
def Integral : Prop :=
  ∀ obligation key, F.flow obligation key = 0 ∨ F.flow obligation key = 1

/-- Load on one literal physical key. -/
def keyLoad (key : EdgeCappedPhysicalKey ActiveEdge DirectBase) : ℚ :=
  ∑ obligation, F.flow obligation key

/-- Summing the active aggregate caps and the direct physical-key caps gives
the exact global half-capacity `2|ActiveEdge| + 2|DirectBase|`. -/
theorem total_load_le_edgeCapped_capacity :
    (∑ key, F.keyLoad key) ≤
      2 * (Fintype.card ActiveEdge : ℚ) +
        2 * (Fintype.card DirectBase : ℚ) := by
  have hactive :
      (∑ edge : ActiveEdge, ∑ orientation : Fin 2, ∑ half : Fin 2,
          F.keyLoad ((Sum.inl (edge, orientation)), half)) ≤
        ∑ _edge : ActiveEdge, (2 : ℚ) := by
    exact Finset.sum_le_sum fun edge _ => F.active_edge_capacity edge
  have hdirect :
      (∑ base : DirectBase, ∑ half : Fin 2,
          F.keyLoad ((Sum.inr base), half)) ≤
        ∑ _base : DirectBase, ∑ _half : Fin 2, (1 : ℚ) := by
    exact Finset.sum_le_sum fun base _ =>
      Finset.sum_le_sum fun half _ => F.key_capacity ((Sum.inr base), half)
  calc
    (∑ key, F.keyLoad key) =
        (∑ edge : ActiveEdge, ∑ orientation : Fin 2, ∑ half : Fin 2,
          F.keyLoad ((Sum.inl (edge, orientation)), half)) +
        ∑ base : DirectBase, ∑ half : Fin 2,
          F.keyLoad ((Sum.inr base), half) := by
            simp only [EdgeCappedPhysicalKey, Fintype.sum_prod_type,
              Fintype.sum_sum_type]
    _ ≤ (∑ _edge : ActiveEdge, (2 : ℚ)) +
        ∑ _base : DirectBase, ∑ _half : Fin 2, (1 : ℚ) :=
      add_le_add hactive hdirect
    _ = 2 * (Fintype.card ActiveEdge : ℚ) +
        2 * (Fintype.card DirectBase : ℚ) := by
      simp
      ring

/-- A feasible fractional flow cannot cover more obligations than the exact
adaptive half-capacity. -/
theorem obligation_card_le_edgeCapped_capacityQ
    (F : FractionalCollisionFlowWithEdgeCaps Eligible) :
    (Fintype.card Obligation : ℚ) ≤
      2 * (Fintype.card ActiveEdge : ℚ) +
        2 * (Fintype.card DirectBase : ℚ) := by
  calc
    (Fintype.card Obligation : ℚ) =
        ∑ obligation : Obligation, ∑ key : EdgeCappedPhysicalKey ActiveEdge DirectBase, F.flow obligation key := by
      calc
        (Fintype.card Obligation : ℚ) =
            ∑ _obligation : Obligation, (1 : ℚ) := by simp
        _ = ∑ obligation : Obligation, ∑ key : EdgeCappedPhysicalKey ActiveEdge DirectBase, F.flow obligation key := by
          apply Finset.sum_congr rfl
          intro obligation _
          exact (F.obligation_demand obligation).symm
    _ = ∑ key : EdgeCappedPhysicalKey ActiveEdge DirectBase, F.keyLoad key := by
      rw [Finset.sum_comm]
      rfl
    _ ≤ 2 * (Fintype.card ActiveEdge : ℚ) +
        2 * (Fintype.card DirectBase : ℚ) :=
      total_load_le_edgeCapped_capacity F

theorem obligation_card_le_edgeCapped_capacity
    (F : FractionalCollisionFlowWithEdgeCaps Eligible) :
    Fintype.card Obligation ≤
      2 * Fintype.card ActiveEdge + 2 * Fintype.card DirectBase := by
  exact_mod_cast (obligation_card_le_edgeCapped_capacityQ F)

end FractionalCollisionFlowWithEdgeCaps

section Counting

variable {V : Type*} [Fintype V]
variable {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
variable {DirectBase : Type uBase}
variable [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
variable {Eligible : Obligation → EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop}

/-- Exact adaptive-reservation count. `hobligation` says collision debits
have two half-obligations. `hsource` says the two oriented bases of each
active edge, together with the direct non-active bases, are genuine free
ordered-pair sources. -/
theorem collision_add_active_le_free
    (n : V → V → Nat)
    (F : FractionalCollisionFlowWithEdgeCaps Eligible)
    (hobligation :
      (Fintype.card Obligation : ℤ) =
        2 * CollisionResidualIdentity.collisionMass n)
    (hsource :
      2 * (Fintype.card ActiveEdge : ℤ) +
          (Fintype.card DirectBase : ℤ) ≤
        CollisionResidualIdentity.freeMass n) :
    CollisionResidualIdentity.collisionMass n +
        (Fintype.card ActiveEdge : ℤ) ≤
      CollisionResidualIdentity.freeMass n := by
  have hcapNat :=
    FractionalCollisionFlowWithEdgeCaps.obligation_card_le_edgeCapped_capacity F
  have hcap :
      (Fintype.card Obligation : ℤ) ≤
        2 * (Fintype.card ActiveEdge : ℤ) +
          2 * (Fintype.card DirectBase : ℤ) := by
    exact_mod_cast hcapNat
  rw [hobligation] at hcap
  omega

/-- The exact coherence-free counting consumer. This is only a wrapper
around `CollisionResidualIdentity.residual_nonneg_of_collision_le_free`;
all graph work is confined to supplying a feasible edge-capped flow. -/
theorem residual_nonneg_of_fractionalCollisionFlowWithEdgeCaps
    (n : V → V → Nat) (m : Nat)
    (F : FractionalCollisionFlowWithEdgeCaps Eligible)
    (htotal :
      (∑ v : V, ∑ z : V, (n v z : ℤ)) = 25 * (m : ℤ))
    (hobligation :
      (Fintype.card Obligation : ℤ) =
        2 * CollisionResidualIdentity.collisionMass n)
    (hsource :
      2 * (Fintype.card ActiveEdge : ℤ) +
          (Fintype.card DirectBase : ℤ) ≤
        CollisionResidualIdentity.freeMass n) :
    0 ≤ (Fintype.card V : ℤ) ^ 2 - 25 * (m : ℤ) := by
  apply CollisionResidualIdentity.residual_nonneg_of_collision_le_free n m htotal
  have hstrong := collision_add_active_le_free n F hobligation hsource
  omega

end Counting

/-! ## Sole graph provider

`ActiveEdge`, `DirectBase`, and `SixRelationEligible` are the production
source partition and six-relation eligibility for each existing row tuple.
The proposition below deliberately contains no coherence field. Proving it
for the concrete production arguments is the sole unproved graph theorem in
this module; no axiom asserts it.
-/

section Provider

variable (G : GraphData) (c : CutData) (bads : List BadEdgeData)
variable (ActiveEdge DirectBase : RowChoice bads → Type*)
variable [∀ omega, Fintype (ActiveEdge omega)]
variable [∀ omega, Fintype (DirectBase omega)]
variable (SixRelationEligible : ∀ omega : RowChoice bads,
  CollisionHalf G omega →
    EdgeCappedPhysicalKey (ActiveEdge omega) (DirectBase omega) → Prop)

/-- Exact remaining provider statement: some real row tuple has a feasible
coherence-free fractional collision flow under physical-key and adaptive
active-edge capacities. -/
def canonicalSoftEdgeCapFeasibleTuple_exists : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
      ∃ omega : RowChoice bads,
        Nonempty
          (FractionalCollisionFlowWithEdgeCaps
            (SixRelationEligible omega))

end Provider

#print axioms FractionalCollisionFlowWithEdgeCaps.total_load_le_edgeCapped_capacity
#print axioms FractionalCollisionFlowWithEdgeCaps.obligation_card_le_edgeCapped_capacity
#print axioms collision_add_active_le_free
#print axioms residual_nonneg_of_fractionalCollisionFlowWithEdgeCaps

end CheckedSoftCollisionTwoCover
end Gamma
end Erdos23Delta0
