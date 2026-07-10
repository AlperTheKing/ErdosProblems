import Erdos23Delta0.ClosedShoreProperSplit

/-!
# Conditional locality adapter for a real extractor

This module records an open provider contract for the still-missing real
extractor.  A provider must supply a nonempty finite vertex support for every
bank sink.  Nothing in this module constructs such a provider, supplies a
value of the provider type, or proves that one exists.

Conditionally on that supplied data, localization of two port sets to
vertex-disjoint shores forces their legal sink neighborhoods to be disjoint.
The final definition only adapts that fact to the existing
`ClosedShore.properClosedBankSplitOfDisjointNeighbors` constructor.
-/

namespace Erdos23Delta0
namespace Wall

open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Open real-extractor provider contract.  Its fields are assumptions supplied
by a future concrete extractor; this module provides no inhabitant or existence
theorem for this structure. -/
structure RealExtractorSupportProvider (I : BankedWallLP) (V : Type*)
    [Fintype V] [DecidableEq V] where
  /-- The finite vertex support assigned by the external extractor to a sink. -/
  sinkSupport : I.Sink → Finset V
  /-- Every supplied sink support contains at least one vertex. -/
  sinkSupport_nonempty : ∀ s, (sinkSupport s).Nonempty

/-- Every legal sink reached from a port in `P` has its supplied vertex support
contained in the shore `U`. -/
def PortsLocalizedTo {V : Type*} [DecidableEq V]
    (support : I.Sink → Finset V) (P : Finset I.Port) (U : Finset V) : Prop :=
  ∀ p ∈ P, ∀ s, I.legal p s → support s ⊆ U

/-- Port sets localized to disjoint vertex shores have disjoint legal sink
neighborhoods, provided every sink support supplied by the provider is
nonempty. -/
theorem disjoint_legalNbr_of_portsLocalizedTo
    {V : Type*} [Fintype V] [DecidableEq V]
    (R : RealExtractorSupportProvider I V)
    {left right : Finset I.Port} {U W : Finset V}
    (hleft : PortsLocalizedTo R.sinkSupport left U)
    (hright : PortsLocalizedTo R.sinkSupport right W)
    (hshores : Disjoint U W) :
    Disjoint (legalNbr I left) (legalNbr I right) := by
  rw [Finset.disjoint_left]
  intro s hsleft hsright
  obtain ⟨p, hp, hps⟩ := mem_legalNbr.mp hsleft
  obtain ⟨q, hq, hqs⟩ := mem_legalNbr.mp hsright
  obtain ⟨v, hv⟩ := R.sinkSupport_nonempty s
  exact
    (Finset.disjoint_left.mp hshores
      (hleft p hp s hps hv))
      (hright q hq s hqs hv)

namespace ClosedShore

variable {Q : AbstractEscapeQuotient I}

/-- Conditional adapter from a proper closed port partition localized to
disjoint supplied vertex shores.  This definition consumes a provider value;
it does not construct one or assert that a real extractor exists. -/
noncomputable def properClosedBankSplitOfLocalizedSupports
    {V : Type*} [Fintype V] [DecidableEq V]
    (R : RealExtractorSupportProvider I V)
    (L : I.Port → ℚ) {parent left right : Finset I.Port}
    {U W : Finset V}
    (hports : Disjoint left right) (hcover : left ∪ right = parent)
    (hleftClosed : ClosedPortSet Q left)
    (hrightClosed : ClosedPortSet Q right)
    (hleftProper : left ⊂ parent) (hrightProper : right ⊂ parent)
    (hleftLocal : PortsLocalizedTo R.sinkSupport left U)
    (hrightLocal : PortsLocalizedTo R.sinkSupport right W)
    (hshores : Disjoint U W) :
    ProperClosedBankSplit Q L parent :=
  ClosedShore.properClosedBankSplitOfDisjointNeighbors (I := I) (Q := Q) L
    hports hcover hleftClosed hrightClosed hleftProper hrightProper
    (disjoint_legalNbr_of_portsLocalizedTo R hleftLocal hrightLocal hshores)

end ClosedShore
end Wall
end Erdos23Delta0
