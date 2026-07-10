import Erdos23Delta0.HornSplitOrHalfLayerChecker
import Erdos23Delta0.ClosedShoreBankPrime

/-!
# Directed Horn closure alone does not imply split or TwoCover

This exact finite model has:

* a checked strict wall dual;
* injective legal own Doors of unit capacity;
* a minimal deficient parent for a one-way Horn closure;
* no proper closed-bank split; and
* no routed positive-alpha TwoCover for any listed wall family.

It is an abstract-interface countermodel, not a real graph extractor.  Hence a
split-or-TwoCover theorem must consume additional checked corridor geometry.
-/

namespace Erdos23Delta0
namespace HornSplitOrTwoCoverCounterexample

open scoped BigOperators
open Wall
open Wall.PortHall
open Wall.ClosedShore

def wall : BankedWallLP where
  Cut := Fin 2
  Atom := Fin 2
  Short := PUnit
  Port := Fin 2
  Sink := Fin 2
  cutFintype := inferInstance
  atomFintype := inferInstance
  shortFintype := inferInstance
  portFintype := inferInstance
  sinkFintype := inferInstance
  cov := fun X a => if X = a then 1 else 0
  useShort := fun _ _ => 1
  cutPort := fun _ _ => 0
  legal := fun p s => p = s
  legalDecidable := fun _ _ => inferInstance
  cap := fun _ => 1

def dual : Dual wall where
  alpha := fun _ => 1
  beta := fun _ => 1
  gamma := fun _ => 0
  delta := fun _ => 0

theorem dual_checked : dual.Checked := by
  refine
    { alpha_nonneg := by intro; norm_num [dual]
      beta_nonneg := by intro; norm_num [dual]
      gamma_nonneg := by intro; norm_num [dual]
      delta_nonneg := by intro; norm_num [dual]
      cap_nonneg := by intro; change (0 : ℚ) ≤ 1; norm_num
      d1 := ?_
      d2 := ?_ }
  · intro X
    fin_cases X
    · change
        (∑ a : Fin 2, (if (0 : Fin 2) = a then 1 else 0) * 1) ≤
          (∑ _f : PUnit, 1 * 1) + ∑ _p : Fin 2, 0 * 0
      norm_num
    · change
        (∑ a : Fin 2, (if (1 : Fin 2) = a then 1 else 0) * 1) ≤
          (∑ _f : PUnit, 1 * 1) + ∑ _p : Fin 2, 0 * 0
      norm_num
  · intro p s _
    norm_num [dual]

theorem dual_strictGap : dual.StrictGap := by
  unfold Dual.StrictGap totalBeta totalDeltaCap totalAlpha
  change
    (∑ _f : PUnit, (1 : ℚ)) + ∑ _s : Fin 2, 1 * 0 <
      ∑ _a : Fin 2, 1
  norm_num

def ownDoor (p : Fin 2) : Fin 2 := p

theorem ownDoor_injective : Function.Injective ownDoor := fun _ _ h => h

theorem ownDoor_legal (p : Fin 2) : wall.legal p (ownDoor p) := rfl

theorem ownDoor_capacity (p : Fin 2) : (1 : ℚ) ≤ wall.cap (ownDoor p) := by
  change (1 : ℚ) ≤ 1
  norm_num

def rule01 : HornRule (Fin 2) where
  pre := {(0 : Fin 2)}
  post := 1

def surface : HornEscapeSurface wall where
  QComp := Fin 2
  qDecEq := inferInstance
  qFintype := inferInstance
  ruleList := [rule01]
  exposedPorts := id

def parent : Finset wall.Port := Finset.univ

def load (p : Fin 2) : ℚ := if p = 0 then 2 else 1

theorem legalNbr_eq_self (P : Finset (Fin 2)) : legalNbr wall P = P := by
  ext s
  rw [mem_legalNbr]
  constructor
  · rintro ⟨p, hp, hps⟩
    change p = s at hps
    simpa [hps] using hp
  · intro hs
    exact ⟨s, hs, rfl⟩

theorem parent_hornClosed : HornClosed surface.rules parent := by
  intro r hr _
  simp [parent]

theorem parent_closed : ClosedPortSet surface.toQ parent :=
  surface.closedPortSet_of_hornClosed parent parent_hornClosed

theorem parent_deficient : HallDeficient wall load parent := by
  unfold HallDeficient deficiencyQ
  rw [legalNbr_eq_self]
  have hload : loadQ wall load parent = 3 := by
    simp only [loadQ, parent]
    change (∑ p : Fin 2, load p) = 3
    rw [Fin.sum_univ_two]
    norm_num [load]
  have hcap : capQ wall parent = 2 := by
    simp only [capQ, parent]
    change (∑ _s : Fin 2, (1 : ℚ)) = 2
    rw [Fin.sum_univ_two]
    norm_num
  rw [hload, hcap]
  norm_num

private theorem proper_hornClosed_subset_eq_empty_or_one
    (P : Finset (Fin 2)) (hclosed : HornClosed surface.rules P)
    (hproper : P ⊂ parent) : P = ∅ ∨ P = {(1 : Fin 2)} := by
  have h0 : (0 : Fin 2) ∉ P := by
    intro h0P
    have hrule : surface.rules rule01 := by
      simp [HornEscapeSurface.rules, surface]
    have hpre : rule01.pre ⊆ P := by
      intro x hx
      have hx0 : x = 0 := by simpa [rule01] using hx
      simpa [hx0] using h0P
    have h1P : (1 : Fin 2) ∈ P := hclosed rule01 hrule hpre
    have hparent : P = parent := by
      ext x
      fin_cases x <;> simp [parent, h0P, h1P]
    exact (Finset.ssubset_iff_subset_ne.mp hproper).2 hparent
  by_cases h1 : (1 : Fin 2) ∈ P
  · right
    ext x
    fin_cases x <;> simp [h0, h1]
  · left
    ext x
    fin_cases x <;> simp [h0, h1]

theorem parent_minimalClosedDeficient :
    MinimalClosedDeficient surface.toQ load parent := by
  refine ⟨parent_closed, parent_deficient, ?_⟩
  intro P hPclosed hPproper
  rcases hPclosed with ⟨U, hUfixed, hUexposed⟩
  have hUclosed : HornClosed surface.rules U :=
    (surface.fullClosure_eq_self_iff U).mp hUfixed
  have hUP : U = P := by simpa [surface] using hUexposed
  subst U
  rcases proper_hornClosed_subset_eq_empty_or_one P hUclosed hPproper with
    rfl | rfl
  · simp [deficiencyQ, loadQ, capQ, legalNbr]
  · unfold deficiencyQ
    rw [legalNbr_eq_self]
    have hload : loadQ wall load ({(1 : Fin 2)} : Finset (Fin 2)) = 1 := by
      simp [loadQ, load]
    have hcap : capQ wall ({(1 : Fin 2)} : Finset (Fin 2)) = 1 := by
      simp [capQ, wall]
    rw [hload, hcap]
    norm_num

theorem no_properClosedBankSplit :
    ¬ Nonempty (ProperClosedBankSplit surface.toQ load parent) := by
  rintro ⟨split⟩
  exact no_properClosedBankSplit_of_minimal load parent
    parent_minimalClosedDeficient split

theorem no_routed_positiveAlphaTwoCover {q : Nat}
    (walls : Fin q → wall.Cut)
    (htwo : ∀ a : wall.Atom, 0 < dual.alpha a →
      ∑ i : Fin q, wall.cov (walls i) a = 2) :
    ¬ Nonempty (HalfLayerRouted wall walls) := by
  rintro ⟨routed⟩
  exact
    (noStrictDual_of_halfLayerTwoCover dual dual_checked walls htwo routed)
      dual_strictGap

/-- Neither branch follows from the current abstract Horn and wall interfaces,
even when every port has an injective legal own Door. -/
theorem no_abstract_split_or_routedTwoCover {q : Nat}
    (walls : Fin q → wall.Cut) :
    ¬ (Nonempty (ProperClosedBankSplit surface.toQ load parent) ∨
      ((∀ a : wall.Atom, 0 < dual.alpha a →
          ∑ i : Fin q, wall.cov (walls i) a = 2) ∧
        Nonempty (HalfLayerRouted wall walls))) := by
  rintro (hsplit | ⟨htwo, hrouted⟩)
  · exact no_properClosedBankSplit hsplit
  · exact no_routed_positiveAlphaTwoCover walls htwo hrouted

#print axioms dual_checked
#print axioms dual_strictGap
#print axioms parent_minimalClosedDeficient
#print axioms no_properClosedBankSplit
#print axioms no_routed_positiveAlphaTwoCover
#print axioms no_abstract_split_or_routedTwoCover

end HornSplitOrTwoCoverCounterexample
end Erdos23Delta0
