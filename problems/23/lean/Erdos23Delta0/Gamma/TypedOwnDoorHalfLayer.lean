import Erdos23Delta0.Gamma.TypedFullBankSources
import Erdos23Delta0.DisjointPetalHalfSqueeze

/-!
# Typed own-Door sources to the half-layer routing witness

`TypedFullBankSources` checks that each port has a distinct token whose source
is the exact Door key of that port and whose raw capacity is at least `25`.
This module supplies the small adapter to the real wall sink type and composes
those facts with the existing disjoint-petal half-layer theorem.

The only adapter obligation is the global typed-source interpretation of the
wall: a token embedding preserves capacity, and exact Door-source equality is
a legal wall incidence.  Per-port legality, injectivity, and capacity are then
derived, not supplied separately.
-/

namespace Erdos23Delta0
namespace Gamma
namespace TypedOwnDoorHalfLayer

open Wall
open DisjointPetalHalfSqueeze
open TypedFullBankSources

variable {V : Type*} [DecidableEq V]
variable {I : BankedWallLP} {q componentCount tokenCount : Nat}
variable {VertexKey BaseKey PruneKey : Type*}

abbrev DoorData (VertexKey BaseKey PruneKey : Type*) :=
  OwnEdgeDoorSourceData I.Port (Sym2 V) VertexKey BaseKey PruneKey
    componentCount tokenCount

/-- Global interpretation of typed ledger tokens as sinks of the wall LP. -/
structure DoorWallAdapter
    (D : DoorData (V := V) (I := I) (componentCount := componentCount)
      (tokenCount := tokenCount) VertexKey BaseKey PruneKey) where
  sinkOf : Fin tokenCount -> I.Sink
  sinkOf_injective : Function.Injective sinkOf
  legal_of_door_source : forall p t, D.doorLegal p t -> I.legal p (sinkOf t)
  cap_eq_hallCapQ : forall t, I.cap (sinkOf t) = D.hallCapQ t
  sink_capacity_nonneg : forall s, 0 <= I.cap s

/-- The graph-shore data that is independent of the sink representation. -/
structure TypedPetalGeometry
    (D : DoorData (V := V) (I := I) (componentCount := componentCount)
      (tokenCount := tokenCount) VertexKey BaseKey PruneKey)
    (walls : Fin q -> I.Cut) where
  shore : Fin q -> Finset V
  shortEdge : I.Short -> Sym2 V
  petals_disjoint : forall i j, i ≠ j -> Disjoint (shore i) (shore j)
  short_is_boundary : forall i f,
    I.useShort (walls i) f =
      if MaxCutVertexIneq.edgeBoundary (shore i) (shortEdge f) = true then 1 else 0
  port_is_boundary : forall i p,
    I.cutPort (walls i) p =
      if MaxCutVertexIneq.edgeBoundary (shore i) (D.portEdge p) = true then 1 else 0

/-- Accepted typed own-Door sources and pairwise-disjoint petal shores produce
the exact `HalfLayerRouted` witness. -/
noncomputable def halfLayerRouted_of_checkedEdgeDoorSources
    (D : DoorData (V := V) (I := I) (componentCount := componentCount)
      (tokenCount := tokenCount) VertexKey BaseKey PruneKey)
    (hD : D.Checked)
    (A : DoorWallAdapter D)
    (walls : Fin q -> I.Cut)
    (G : TypedPetalGeometry D walls) :
    HalfLayerRouted I walls := by
  classical
  apply routedOfDisjointPetals (V := V) (I := I) walls
  exact
    { shore := G.shore
      shortEdge := G.shortEdge
      portEdge := D.portEdge
      petals_disjoint := G.petals_disjoint
      short_is_boundary := G.short_is_boundary
      port_is_boundary := G.port_is_boundary
      door := fun p => A.sinkOf (D.doorOf p)
      door_injective := A.sinkOf_injective.comp (D.doorOf_injective hD)
      door_legal := fun p =>
        A.legal_of_door_source p (D.doorOf p) (D.doorOf_legal hD p)
      door_capacity := fun p => by
        rw [A.cap_eq_hallCapQ]
        exact D.one_le_door_hallCapQ hD p
      sink_capacity_nonneg := A.sink_capacity_nonneg }

/-- End-to-end dual contradiction through the typed own-Door fast path. -/
theorem noStrictDual_of_checkedEdgeDoorSources
    (D : DoorData (V := V) (I := I) (componentCount := componentCount)
      (tokenCount := tokenCount) VertexKey BaseKey PruneKey)
    (hD : D.Checked)
    (A : DoorWallAdapter D)
    (walls : Fin q -> I.Cut)
    (G : TypedPetalGeometry D walls)
    (d : Dual I) (hd : d.Checked)
    (htwo : forall a : I.Atom, 0 < d.alpha a ->
      (Finset.univ.sum fun i : Fin q => I.cov (walls i) a) = 2) :
    ¬ d.StrictGap :=
  noStrictDual_of_halfLayerTwoCover d hd walls htwo
    (halfLayerRouted_of_checkedEdgeDoorSources D hD A walls G)

#print axioms halfLayerRouted_of_checkedEdgeDoorSources
#print axioms noStrictDual_of_checkedEdgeDoorSources

end TypedOwnDoorHalfLayer
end Gamma
end Erdos23Delta0
