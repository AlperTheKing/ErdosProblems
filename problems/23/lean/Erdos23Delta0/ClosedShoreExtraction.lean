import Mathlib
import Erdos23Delta0.BankedWallLP
import Erdos23Delta0.PortHallUncrossing

/-!
# Closed-shore extraction: unique root from positive-block extraction (2026-07-09)

WALL ATTACK R3 (`WALL_ATTACK_R3_GPTPRO.md`) refuted W2-as-stated (RootBlockClosureSeparable) by an abstract
2-component counterexample (exact-gated `_claude_w2_ce_gate.py`): a closure step can cross legal root blocks
while the legal sink neighborhoods stay disjoint. The surviving reduction is the WEAKER extraction hypothesis
`PositiveRootBlockClosedExtraction` (§5): if a closed deficient exposed-port set has ≥ 2 legal root
components, SOME positive-deficiency root block is itself realized by a proper closed subshore. This module
compiles that reduction against the compiled uncrossing algebra:

* `AbstractEscapeQuotient` — the closure interface actually used (extensive/monotone/idempotent closure +
  exposure map on an abstract finite quotient; the concrete `ForcedEll5EscapeStep` model instantiates it);
* `ClosedPortSet`, `MinimalClosedDeficient` — R2's corrected minimality predicate;
* `minimalClosedDeficient_has_unique_root_of_positiveExtraction` — the unique-root theorem: extraction +
  minimal closed deficiency ⟹ exactly ONE legal component.

Root-locality itself (why the real forced-ℓ=5 escape closure satisfies the extraction) is THE open graph-side
obligation — deliberately a hypothesis here.
No `sorry`/`admit`/`native_decide`; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open scoped BigOperators
open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- The abstract escape-quotient interface: a finite quotient-component type with a full-escape closure
operator and an exposure map. The concrete cage model instantiates `QComp` with the components of `B \ F`,
`fullClosure` with the forced-ℓ=5 escape closure, and `exposedPorts` with the off-support port exposure. -/
structure AbstractEscapeQuotient (I : BankedWallLP) where
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp
  fullClosure : Finset QComp → Finset QComp
  exposedPorts : Finset QComp → Finset I.Port
  closure_extensive : ∀ U, U ⊆ fullClosure U
  closure_idempotent : ∀ U, fullClosure (fullClosure U) = fullClosure U
  closure_monotone : ∀ U V, U ⊆ V → fullClosure U ⊆ fullClosure V

attribute [instance] AbstractEscapeQuotient.qDecEq AbstractEscapeQuotient.qFintype

variable {Q : AbstractEscapeQuotient I}

/-- A port set realized as the exposure of a full-escape-closed shore. -/
def ClosedPortSet (Q : AbstractEscapeQuotient I) (P : Finset I.Port) : Prop :=
  ∃ U : Finset Q.QComp, Q.fullClosure U = U ∧ Q.exposedPorts U = P

/-- R2's corrected minimality predicate: minimal among CLOSED deficient port sets (plain
`InclusionMinimalDeficient` + closure is refuted by R3 falsifier 1). -/
def MinimalClosedDeficient (Q : AbstractEscapeQuotient I) (L : I.Port → ℚ)
    (P : Finset I.Port) : Prop :=
  ClosedPortSet Q P ∧ HallDeficient I L P ∧
    ∀ P' : Finset I.Port, ClosedPortSet Q P' → P' ⊂ P → deficiencyQ I L P' ≤ 0

/-- **The weaker separability that the unique-root Hall argument needs** (R3 §5): from any closed deficient
exposed-port set with ≥ 2 legal components, extract ONE positive-deficiency component realized as a proper
closed subshore. Genuinely stronger than W1 (the R3 counterexample); the open graph-side obligation. -/
def PositiveRootBlockClosedExtraction (Q : AbstractEscapeQuotient I) : Prop :=
  ∀ (L : I.Port → ℚ) (U : Finset Q.QComp), Q.fullClosure U = U →
    ∀ D : LegalComponentPartition I (Q.exposedPorts U),
      HallDeficient I L (Q.exposedPorts U) → 2 ≤ Fintype.card D.K →
        ∃ (k : D.K) (Ur : Finset Q.QComp),
          Q.fullClosure Ur = Ur ∧ Q.exposedPorts Ur = D.ports k ∧
            D.ports k ⊂ Q.exposedPorts U ∧ HallDeficient I L (D.ports k)

/-- **Unique root from positive-block extraction**: a minimal closed deficient exposed-port set has exactly
one legal-incidence component. (The ≥2 case dies by extraction + minimality; the 0 case dies because a
deficient set is nonempty.) -/
theorem minimalClosedDeficient_has_unique_root_of_positiveExtraction
    (hExtract : PositiveRootBlockClosedExtraction Q)
    (L : I.Port → ℚ) (U : Finset Q.QComp) (hUclosed : Q.fullClosure U = U)
    (hMin : MinimalClosedDeficient Q L (Q.exposedPorts U))
    (D : LegalComponentPartition I (Q.exposedPorts U)) :
    Fintype.card D.K = 1 := by
  obtain ⟨hClosedP, hDefP, hMinimal⟩ := hMin
  -- K is nonempty: the deficient port set is nonempty and covered by the blocks.
  have hPne : (Q.exposedPorts U).Nonempty := nonempty_of_hallDeficient hDefP
  obtain ⟨x, hx⟩ := hPne
  have hxcov : x ∈ Finset.univ.biUnion D.ports := by
    rw [D.ports_cover]; exact hx
  obtain ⟨k0, -, hk0⟩ := Finset.mem_biUnion.mp hxcov
  have hpos : 0 < Fintype.card D.K := Fintype.card_pos_iff.mpr ⟨k0⟩
  -- Rule out ≥ 2 by extraction + minimality.
  by_contra hne
  have hTwo : 2 ≤ Fintype.card D.K := by omega
  obtain ⟨k, Ur, hUrClosed, hExpUr, hProper, hDefBlock⟩ :=
    hExtract L U hUclosed D hDefP hTwo
  have hClosedBlock : ClosedPortSet Q (D.ports k) := ⟨Ur, hUrClosed, hExpUr⟩
  have hle : deficiencyQ I L (D.ports k) ≤ 0 := hMinimal (D.ports k) hClosedBlock hProper
  exact absurd (hDefBlock : 0 < deficiencyQ I L (D.ports k)) (not_lt.mpr hle)

#print axioms minimalClosedDeficient_has_unique_root_of_positiveExtraction

end ClosedShore
end Wall
end Erdos23Delta0
