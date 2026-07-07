import Mathlib.Tactic

/-!
# Route-B CAP interface — the A-derivation, machine-checked (2026-07-08)

Erdős #23 gap#1 door-only closure. GPT-Pro reduced the "no long side-door annulus" lemma A
(`NoLongSideDoorAnnulus`) to a 3-case argument over a minimal CAP primitive interface. The single load-bearing
primitive is `hFirstSplit` (= `AnnularAtom_has_firstSplit` = `S1S2_annularLayer_cover`): a level-`≥1` owned annular
atom of a minimal two-door side-door subcage forces a proper interior first-split subcage, classified PS ∨ ZT ∨ BAD.

The 2026-07-08 adversarial S1 re-audit (verdict WALL, high confidence, `S2_FROZEN_STATEMENT.md:168` spot-verified)
found that `hFirstSplit` is **NOT discharged by the archived S1/S2 theory** — S1 gives only Ferrers ordering and S2
gives a disjunction with door-existence demoted to an application case-split. So `hFirstSplit` is the genuine open
geometric residual (battery-validated only: 17757 census+glue cases, 0 fail).

This module makes the **derivation** honest and machine-checked: given the primitives as explicit hypotheses, every
owned atom of a minimal side-door subcage is level 0 (hence owns no `ell ≥ 9` bad edge). No `sorry`. The primitives —
above all `hFirstSplit` — remain the named obligations; nothing here claims them.
-/

namespace Erdos23Delta0
namespace RouteBCAP

/-- **A = `NoLongSideDoorAnnulus`, derivation only** (GPT-Pro's 3-case argument, machine-checked). Over abstract
    `Cage`/`Atom` types and abstract CAP predicates, from the four primitives:
    * `hFirstSplit` (= `AnnularAtom_has_firstSplit`, the OPEN residual): a level-`≥1` owned atom of a minimal
      side-door cage yields a proper subcage classified `PS ∨ (ZT ∧ atom inside) ∨ BAD`;
    * `hMinNoProperPS`: a proper positive-slack side-door subcage contradicts minimality;
    * `hTerminality`: an atom inside a proper zero-slack core is not owned by the parent;
    * `hNoViolation` (= `ValidCAPFrame_no_violation`): a valid CAP frame has no boundary/S2 violation;
    the conclusion is that every owned atom of a minimal side-door subcage has level `0`. Pure logic, non-circular
    (no Γ-minimality, no switch, no reserve). -/
theorem noLongSideDoor_of_primitives
    {Cage Atom : Type}
    (level : Atom → Nat)
    (OwnedAtom AtomInCage : Cage → Atom → Prop)
    (ProperSub : Cage → Cage → Prop)
    (IsMinSideDoor IsPosSlackSideDoor IsZeroSlackTypeBCore CAPViolation : Cage → Prop)
    (hFirstSplit : ∀ (D : Cage) (x : Atom), IsMinSideDoor D → OwnedAtom D x → 1 ≤ level x →
        ∃ D', ProperSub D' D ∧
          (IsPosSlackSideDoor D' ∨ (IsZeroSlackTypeBCore D' ∧ AtomInCage D' x) ∨ CAPViolation D'))
    (hMinNoProperPS : ∀ (D D' : Cage), IsMinSideDoor D → ProperSub D' D → ¬ IsPosSlackSideDoor D')
    (hTerminality : ∀ (D D' : Cage) (x : Atom),
        ProperSub D' D → IsZeroSlackTypeBCore D' → AtomInCage D' x → ¬ OwnedAtom D x)
    (hNoViolation : ∀ (D' : Cage), ¬ CAPViolation D') :
    ∀ (D : Cage) (x : Atom), IsMinSideDoor D → OwnedAtom D x → level x = 0 := by
  intro D x hMin hOwn
  by_contra hne
  have hLong : 1 ≤ level x := Nat.one_le_iff_ne_zero.mpr hne
  obtain ⟨D', hProp, hcls⟩ := hFirstSplit D x hMin hOwn hLong
  rcases hcls with hPS | hZT | hBAD
  · exact hMinNoProperPS D D' hMin hProp hPS
  · exact hTerminality D D' x hProp hZT.1 hZT.2 hOwn
  · exact hNoViolation D' hBAD

/-- **Door-only surplus bound from `NoLongSideDoor` + mass ≤ sigma** (rational arithmetic). If every owned atom is
    level 0 then the cage surplus is `24 * mass`; with `mass ≤ sigma` and `0 ≤ sigma` this gives `Surplus ≤ 25*sigma`,
    the exact hypothesis consumed by `RouteBAssembly.doorOnly_balance_nonneg`. Non-circular. -/
theorem surplus_le_25sigma_of_level0
    (mass sigma : ℚ)
    (hmass : mass ≤ sigma) (hsig : 0 ≤ sigma) :
    (24 : ℚ) * mass ≤ 25 * sigma := by nlinarith

end RouteBCAP
end Erdos23Delta0
