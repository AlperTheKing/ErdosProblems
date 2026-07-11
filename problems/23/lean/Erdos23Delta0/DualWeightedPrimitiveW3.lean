import Erdos23Delta0.DualWeightedW3Skeleton
import Erdos23Delta0.PrimitiveCompatibleRootExtraction

/-!
# Dual-weighted W3 with primitive-compatible roots

Diagonal dual scaling changes only port loads and sink capacities.  It leaves
the escape closure, exposed ports, legal incidence, and primitive coupling
unchanged.  Consequently the primitive-compatible unique-root argument can be
used directly on the scaled Hall instance.

This removes positive-root extraction as a separate hypothesis once the real
transfer constructor supplies primitive-block closure and saturation of every
legal component.  The quantitative closed-root exchange remains open.
-/

namespace Erdos23Delta0
namespace Wall
namespace DualWeightedPrimitiveW3

open ClosedShore PortHall DualWeightedHallReduction DualWeightedW3

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Structural root compatibility for every closed shore.  It contains no
load or capacity value. -/
def PrimitiveRootCompatibility (Q : AbstractEscapeQuotient I)
    (primitive : I.Port -> I.Port -> Prop) : Prop :=
  forall U : Finset Q.QComp, Q.fullClosure U = U ->
    PrimitiveBlockClosureExactOn Q primitive (Q.exposedPorts U) /\
      forall D : LegalComponentPartition I (Q.exposedPorts U),
        LegalComponentsPrimitiveCompatible primitive (Q.exposedPorts U) D

/-- The same structural contract on the copied dual-scaled quotient. -/
def ScaledPrimitiveRootCompatibility (Q : AbstractEscapeQuotient I)
    (d : Dual I) (primitive : I.Port -> I.Port -> Prop) : Prop :=
  PrimitiveRootCompatibility (dualScaledQuotient Q d) primitive

/-- Copy a legal-component partition to the scaled LP.  Capacity values do
not occur in this record. -/
def toScaledLegalComponentPartition (d : Dual I) {P : Finset I.Port}
    (D : LegalComponentPartition I P) :
    LegalComponentPartition (dualScaledLP I d) P where
  K := D.K
  kDecEq := D.kDecEq
  kFintype := D.kFintype
  ports := D.ports
  sinks := D.sinks
  ports_subset := D.ports_subset
  ports_pairwise_disjoint := D.ports_pairwise_disjoint
  sinks_pairwise_disjoint := D.sinks_pairwise_disjoint
  ports_cover := D.ports_cover
  sinks_cover := D.sinks_cover
  sinks_eq_nbr := D.sinks_eq_nbr
  nonempty_ports := D.nonempty_ports

/-- Forget the scaled capacities in a legal-component partition. -/
def fromScaledLegalComponentPartition (d : Dual I) {P : Finset I.Port}
    (D : LegalComponentPartition (dualScaledLP I d) P) :
    LegalComponentPartition I P where
  K := D.K
  kDecEq := D.kDecEq
  kFintype := D.kFintype
  ports := D.ports
  sinks := D.sinks
  ports_subset := D.ports_subset
  ports_pairwise_disjoint := D.ports_pairwise_disjoint
  sinks_pairwise_disjoint := D.sinks_pairwise_disjoint
  ports_cover := D.ports_cover
  sinks_cover := D.sinks_cover
  sinks_eq_nbr := D.sinks_eq_nbr
  nonempty_ports := D.nonempty_ports

/-- Primitive-root compatibility is invariant under dual diagonal scaling. -/
theorem scaledPrimitiveRootCompatibility_iff
    (Q : AbstractEscapeQuotient I) (d : Dual I)
    (primitive : I.Port -> I.Port -> Prop) :
    ScaledPrimitiveRootCompatibility Q d primitive <->
      PrimitiveRootCompatibility Q primitive := by
  constructor
  · intro hScaled U hU
    obtain ⟨hBlocks, hCompatible⟩ := hScaled U hU
    constructor
    · simpa [dualScaledQuotient, ClosedPortSet] using hBlocks
    · intro D
      simpa [toScaledLegalComponentPartition,
        LegalComponentsPrimitiveCompatible] using
        hCompatible (toScaledLegalComponentPartition d D)
  · intro hRoot U hU
    obtain ⟨hBlocks, hCompatible⟩ := hRoot U hU
    constructor
    · simpa [dualScaledQuotient, ClosedPortSet] using hBlocks
    · intro D
      simpa [fromScaledLegalComponentPartition,
        LegalComponentsPrimitiveCompatible] using
        hCompatible (fromScaledLegalComponentPartition d D)

/-- W3 consumption theorem using primitive-compatible legal components in
place of the broader positive-root extraction hypothesis. -/
theorem noStrictRestrictedDual_of_primitiveRoot_and_scaledExchange
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hClosedUniv : ClosedExposesUniv Q)
    (primitive : I.Port -> I.Port -> Prop)
    (hRoot : PrimitiveRootCompatibility Q primitive)
    (hExchange : ScaledClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap := by
  intro hstrict
  have hFail : WeightedRoutingFailure d Z.portLoad :=
    strictRestrictedDual_gives_weightedRoutingFailure hd Z hstrict
  obtain ⟨U, hUclosed, hMin⟩ :=
    weightedRoutingFailure_gives_minimalClosedDeficient
      Q hd hClosedUniv hFail
  have hScaled : ScaledPrimitiveRootCompatibility Q d primitive :=
    (scaledPrimitiveRootCompatibility_iff Q d primitive).2 hRoot
  obtain ⟨hBlocks, hCompatible⟩ := hScaled U hUclosed
  have hUnique :
      forall D : LegalComponentPartition (dualScaledLP I d)
          ((dualScaledQuotient Q d).exposedPorts U),
        Fintype.card D.K = 1 := by
    intro D
    exact minimalClosedDeficient_has_unique_root_of_primitiveCompatible
      (dualScaledLoad d Z.portLoad) primitive
      ((dualScaledQuotient Q d).exposedPorts U)
      hMin hBlocks D (hCompatible D)
  obtain ⟨X, hAllowed, hbad⟩ :=
    hExchange U hUclosed hMin hUnique
  exact (not_lt_of_ge (hd.d1_allowed X hAllowed)) hbad

/-- All-cut convenience wrapper. -/
theorem noStrictDual_of_primitiveRoot_and_scaledExchange
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I Allowed d)
    (hClosedUniv : ClosedExposesUniv Q)
    (primitive : I.Port -> I.Port -> Prop)
    (hRoot : PrimitiveRootCompatibility Q primitive)
    (hExchange : ScaledClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap :=
  noStrictRestrictedDual_of_primitiveRoot_and_scaledExchange
    hd.restrict Z hClosedUniv primitive hRoot hExchange

#print axioms scaledPrimitiveRootCompatibility_iff
#print axioms noStrictRestrictedDual_of_primitiveRoot_and_scaledExchange
#print axioms noStrictDual_of_primitiveRoot_and_scaledExchange

end DualWeightedPrimitiveW3
end Wall
end Erdos23Delta0
