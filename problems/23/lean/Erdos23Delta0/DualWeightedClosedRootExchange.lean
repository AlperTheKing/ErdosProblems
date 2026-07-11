import Erdos23Delta0.DualWeightedPrimitiveW3

/-!
# Exact certificate for the dual-weighted closed-root exchange

The scaled Hall reduction leaves one quantitative graph obligation: a minimal
closed one-root deficient shore must produce an allowed cut violating D1.
This module factors that obligation through the smallest exact arithmetic
certificate used by the proof.

The certificate contains one cut and a nonnegative reserve, together with the
rational identity

`cutAlpha - cutBeta - cutGamma = scaledDeficiency + reserve`.

Since the selected shore is Hall-deficient, this identity makes the cut gap
strictly positive.  All graph geometry is now confined to constructing these
finite certificates.
-/

namespace Erdos23Delta0
namespace Wall
namespace DualWeightedClosedRootExchange

open PortHall ClosedShore DualWeightedHallReduction DualWeightedW3

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- One exact cut/reserve witness for a scaled deficient port shore. -/
structure ExchangeCertificate (Allowed : I.Cut -> Prop) (d : Dual I)
    (L : I.Port -> ℚ) (P : Finset I.Port) where
  cut : I.Cut
  allowed : Allowed cut
  reserve : ℚ
  reserve_nonneg : 0 <= reserve
  gap_identity :
    cutAlpha d cut - cutBeta d cut - cutGamma d cut =
      deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P + reserve

/-- Provider-facing finite certificate family.  The closure and unique-root
premises select exactly the shores consumed by W3. -/
def ScaledClosedRootExchangeCertificates
    (Allowed : I.Cut -> Prop) (Q : AbstractEscapeQuotient I)
    (d : Dual I) (L : I.Port -> ℚ) : Prop :=
  forall U : Finset Q.QComp,
    Q.fullClosure U = U ->
      MinimalClosedDeficient (dualScaledQuotient Q d)
        (dualScaledLoad d L) ((dualScaledQuotient Q d).exposedPorts U) ->
        (forall D : LegalComponentPartition (dualScaledLP I d)
            ((dualScaledQuotient Q d).exposedPorts U),
          Fintype.card D.K = 1) ->
          Nonempty (ExchangeCertificate Allowed d L
            ((dualScaledQuotient Q d).exposedPorts U))

/-- The exact certificate converts mechanically to the strict D1 violation
required by the scaled W3 skeleton. -/
theorem scaledClosedRootCutViolatesD1_of_certificates
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I}
    {d : Dual I} {L : I.Port -> ℚ}
    (hCert : ScaledClosedRootExchangeCertificates Allowed Q d L) :
    ScaledClosedRootCutViolatesD1 Allowed Q d L := by
  intro U hUclosed hMin hUnique
  obtain ⟨C⟩ := hCert U hUclosed hMin hUnique
  have hDef :
      0 < deficiencyQ (dualScaledLP I d) (dualScaledLoad d L)
        ((dualScaledQuotient Q d).exposedPorts U) :=
    hMin.2.1
  have hGap :
      0 < cutAlpha d C.cut - cutBeta d C.cut - cutGamma d C.cut := by
    rw [C.gap_identity]
    exact add_pos_of_pos_of_nonneg hDef C.reserve_nonneg
  refine ⟨C.cut, C.allowed, ?_⟩
  linarith

/-- Primitive-compatible W3 theorem consuming only exact exchange
certificates. -/
theorem noStrictRestrictedDual_of_primitiveRoot_and_exchangeCertificates
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hClosedUniv : ClosedExposesUniv Q)
    (primitive : I.Port -> I.Port -> Prop)
    (hRoot : DualWeightedPrimitiveW3.PrimitiveRootCompatibility Q primitive)
    (hCert : ScaledClosedRootExchangeCertificates Allowed Q d Z.portLoad) :
    ¬ d.StrictGap :=
  DualWeightedPrimitiveW3.noStrictRestrictedDual_of_primitiveRoot_and_scaledExchange
    hd Z hClosedUniv primitive hRoot
      (scaledClosedRootCutViolatesD1_of_certificates hCert)

#print axioms scaledClosedRootCutViolatesD1_of_certificates
#print axioms noStrictRestrictedDual_of_primitiveRoot_and_exchangeCertificates

end DualWeightedClosedRootExchange
end Wall
end Erdos23Delta0
