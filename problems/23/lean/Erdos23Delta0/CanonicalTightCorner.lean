import Erdos23Delta0.Ell5FullBankWallAdapter
import Erdos23Delta0.MaxCutVertexIneq

/-!
# Canonical tight-corner algebra

This file proves only the algebraic part of the canonical tight-corner route.
Labels are summed before mapping to graph edges, so coincident labels are not
deduplicated. Closing tight rows to canonical root rows and proving purity or
properness of an innermost corner remain open.
-/

namespace Erdos23Delta0
namespace CanonicalTightCorner

open scoped BigOperators
open MaxCutVertexIneq

variable {V L : Type*} [DecidableEq V]

def edgeBetween (Q R : Finset V) : Sym2 V → Bool :=
  Sym2.lift ⟨fun u v =>
      decide ((u ∈ Q ∧ v ∈ R) ∨ (u ∈ R ∧ v ∈ Q)), by
    intro u v
    by_cases huQ : u ∈ Q <;> by_cases huR : u ∈ R <;>
      by_cases hvQ : v ∈ Q <;> by_cases hvR : v ∈ R <;>
      simp [huQ, huR, hvQ, hvR]⟩

def weightedCut (labels : Finset L) (edge : L → Sym2 V)
    (weight : L → ℚ) (X : Finset V) : ℚ :=
  ∑ i ∈ labels, if edgeBoundary X (edge i) = true then weight i else 0

def weightedBetween (labels : Finset L) (edge : L → Sym2 V)
    (weight : L → ℚ) (Q R : Finset V) : ℚ :=
  ∑ i ∈ labels, if edgeBetween Q R (edge i) = true then weight i else 0

private theorem weightedEdge_four_corner (edge : Sym2 V) (weight : ℚ)
    (X Y : Finset V) :
    (if edgeBoundary X edge = true then weight else 0) +
        (if edgeBoundary Y edge = true then weight else 0) -
        (if edgeBoundary (X ∩ Y) edge = true then weight else 0) -
        (if edgeBoundary (X ∪ Y) edge = true then weight else 0) =
      2 * (if edgeBetween (X \ Y) (Y \ X) edge = true then weight else 0) := by
  refine Sym2.inductionOn edge ?_
  intro u v
  by_cases hux : u ∈ X <;> by_cases huy : u ∈ Y <;>
    by_cases hvx : v ∈ X <;> by_cases hvy : v ∈ Y <;>
    simp [edgeBoundary, edgeBool, memBool, edgeBetween, hux, huy, hvx, hvy,
      Sym2.lift_mk] <;> ring

/-- Weighted four-corner identity, preserving edge-label multiplicity. -/
theorem weightedCut_four_corner (labels : Finset L) (edge : L → Sym2 V)
    (weight : L → ℚ) (X Y : Finset V) :
    weightedCut labels edge weight X + weightedCut labels edge weight Y -
        weightedCut labels edge weight (X ∩ Y) -
        weightedCut labels edge weight (X ∪ Y) =
      2 * weightedBetween labels edge weight (X \ Y) (Y \ X) := by
  classical
  unfold weightedCut weightedBetween
  rw [← Finset.sum_add_distrib, ← Finset.sum_sub_distrib,
    ← Finset.sum_sub_distrib, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  exact weightedEdge_four_corner (edge i) (weight i) X Y

def actualCutWeight (edges : Finset (Sym2 V)) (weight : Sym2 V → ℚ)
    (X : Finset V) : ℚ :=
  weightedCut edges id weight X

def actualWeightBetween (edges : Finset (Sym2 V))
    (weight : Sym2 V → ℚ) (Q R : Finset V) : ℚ :=
  weightedBetween edges id weight Q R

/-- Four-corner identity for weighted actual graph edges. -/
theorem actualCutWeight_four_corner (edges : Finset (Sym2 V))
    (weight : Sym2 V → ℚ) (X Y : Finset V) :
    actualCutWeight edges weight X + actualCutWeight edges weight Y -
        actualCutWeight edges weight (X ∩ Y) -
        actualCutWeight edges weight (X ∪ Y) =
      2 * actualWeightBetween edges weight (X \ Y) (Y \ X) :=
  weightedCut_four_corner edges id weight X Y

def signedD1Slack {A F P : Type*}
    (S : Finset A) (shorts : Finset F) (ports : Finset P)
    (badEdge : A → Sym2 V) (shortEdge : F → Sym2 V)
    (portEdge : P → Sym2 V) (alpha : A → ℚ) (beta : F → ℚ)
    (gamma : P → ℚ) (X : Finset V) : ℚ :=
  weightedCut shorts shortEdge beta X +
    weightedCut ports portEdge gamma X -
    weightedCut S badEdge alpha X

theorem signedD1Slack_four_corner {A F P : Type*}
    (S : Finset A) (shorts : Finset F) (ports : Finset P)
    (badEdge : A → Sym2 V) (shortEdge : F → Sym2 V)
    (portEdge : P → Sym2 V) (alpha : A → ℚ) (beta : F → ℚ)
    (gamma : P → ℚ) (X Y : Finset V) :
    signedD1Slack S shorts ports badEdge shortEdge portEdge alpha beta gamma X +
        signedD1Slack S shorts ports badEdge shortEdge portEdge alpha beta gamma Y -
        signedD1Slack S shorts ports badEdge shortEdge portEdge alpha beta gamma
          (X ∩ Y) -
        signedD1Slack S shorts ports badEdge shortEdge portEdge alpha beta gamma
          (X ∪ Y) =
      2 * (weightedBetween shorts shortEdge beta (X \ Y) (Y \ X) +
        weightedBetween ports portEdge gamma (X \ Y) (Y \ X) -
        weightedBetween S badEdge alpha (X \ Y) (Y \ X)) := by
  have hS := weightedCut_four_corner S badEdge alpha X Y
  have hF := weightedCut_four_corner shorts shortEdge beta X Y
  have hO := weightedCut_four_corner ports portEdge gamma X Y
  unfold signedD1Slack
  linarith

/-- Exact opposite-corner balance for two D1-tight rows, with halves cleared. -/
theorem badBetween_balance_of_tight_corners {A F P : Type*}
    (S : Finset A) (shorts : Finset F) (ports : Finset P)
    (badEdge : A → Sym2 V) (shortEdge : F → Sym2 V)
    (portEdge : P → Sym2 V) (alpha : A → ℚ) (beta : F → ℚ)
    (gamma : P → ℚ) (X Y : Finset V)
    (hX : signedD1Slack S shorts ports badEdge shortEdge portEdge
      alpha beta gamma X = 0)
    (hY : signedD1Slack S shorts ports badEdge shortEdge portEdge
      alpha beta gamma Y = 0) :
    2 * weightedBetween S badEdge alpha (X \ Y) (Y \ X) =
      2 * weightedBetween shorts shortEdge beta (X \ Y) (Y \ X) +
      2 * weightedBetween ports portEdge gamma (X \ Y) (Y \ X) +
      signedD1Slack S shorts ports badEdge shortEdge portEdge
        alpha beta gamma (X ∩ Y) +
      signedD1Slack S shorts ports badEdge shortEdge portEdge
        alpha beta gamma (X ∪ Y) := by
  have hcorner := signedD1Slack_four_corner S shorts ports badEdge
    shortEdge portEdge alpha beta gamma X Y
  rw [hX, hY] at hcorner
  linarith

/-- Positive opposite-corner gamma forces positive opposite-corner alpha. -/
theorem exists_positive_bad_between_of_tight_corners {A F P : Type*}
    (S : Finset A) (shorts : Finset F) (ports : Finset P)
    (badEdge : A → Sym2 V) (shortEdge : F → Sym2 V)
    (portEdge : P → Sym2 V) (alpha : A → ℚ) (beta : F → ℚ)
    (gamma : P → ℚ) (X Y : Finset V)
    (hbeta : ∀ f ∈ shorts, 0 ≤ beta f)
    (hgamma : ∀ p ∈ ports, 0 ≤ gamma p)
    (hX : signedD1Slack S shorts ports badEdge shortEdge portEdge
      alpha beta gamma X = 0)
    (hY : signedD1Slack S shorts ports badEdge shortEdge portEdge
      alpha beta gamma Y = 0)
    (hI : 0 ≤ signedD1Slack S shorts ports badEdge shortEdge portEdge
      alpha beta gamma (X ∩ Y))
    (hJ : 0 ≤ signedD1Slack S shorts ports badEdge shortEdge portEdge
      alpha beta gamma (X ∪ Y))
    (p : P) (hp : p ∈ ports)
    (hpBetween : edgeBetween (X \ Y) (Y \ X) (portEdge p) = true)
    (hpGamma : 0 < gamma p) :
    ∃ a ∈ S,
      edgeBetween (X \ Y) (Y \ X) (badEdge a) = true ∧ 0 < alpha a := by
  have hBetaNonneg :
      0 ≤ weightedBetween shorts shortEdge beta (X \ Y) (Y \ X) := by
    unfold weightedBetween
    apply Finset.sum_nonneg
    intro f hf
    split <;> simp_all
  have hGammaPos :
      0 < weightedBetween ports portEdge gamma (X \ Y) (Y \ X) := by
    unfold weightedBetween
    apply Finset.sum_pos'
    · intro q hq
      split <;> simp_all
    · exact ⟨p, hp, by simp [hpBetween, hpGamma]⟩
  have hcorner := signedD1Slack_four_corner S shorts ports badEdge
    shortEdge portEdge alpha beta gamma X Y
  rw [hX, hY] at hcorner
  have hAlphaPos :
      0 < weightedBetween S badEdge alpha (X \ Y) (Y \ X) := by
    linarith
  have hsum :
      (∑ a ∈ S, (0 : ℚ)) <
        ∑ a ∈ S, if edgeBetween (X \ Y) (Y \ X) (badEdge a) = true
          then alpha a else 0 := by
    simpa [weightedBetween] using hAlphaPos
  obtain ⟨a, haS, haPos⟩ := Finset.exists_lt_of_sum_lt hsum
  have haBetween : edgeBetween (X \ Y) (Y \ X) (badEdge a) = true := by
    by_contra hn
    have hfalse : edgeBetween (X \ Y) (Y \ X) (badEdge a) = false :=
      Bool.eq_false_of_not_eq_true hn
    simp [hfalse] at haPos
  have haAlpha : 0 < alpha a := by simpa [haBetween] using haPos
  exact ⟨a, haS, haBetween, haAlpha⟩

namespace DualMinimality

open Erdos23Delta0.Wall
open Erdos23Delta0.Ell5FullBankWallAdapter

variable {I : BankedWallLP}

def d1Slack (d : Dual I) (X : I.Cut) : ℚ :=
  cutBeta d X + cutGamma d X - cutAlpha d X

noncomputable def lowerGamma (d : Dual I) (p : I.Port)
    (eps : ℚ) : Dual I := by
  classical
  exact { d with gamma := fun q => d.gamma q - if q = p then eps else 0 }

theorem lowerGamma_cutAlpha (d : Dual I) (p : I.Port)
    (eps : ℚ) (X : I.Cut) :
    cutAlpha (lowerGamma d p eps) X = cutAlpha d X := rfl

theorem lowerGamma_cutBeta (d : Dual I) (p : I.Port)
    (eps : ℚ) (X : I.Cut) :
    cutBeta (lowerGamma d p eps) X = cutBeta d X := rfl

theorem lowerGamma_cutGamma (d : Dual I) (p : I.Port)
    (eps : ℚ) (X : I.Cut) :
    cutGamma (lowerGamma d p eps) X =
      cutGamma d X - I.cutPort X p * eps := by
  classical
  simp [cutGamma, lowerGamma, mul_sub, Finset.sum_sub_distrib]

/-- Explicit minimality; this file does not assert that such a dual exists. -/
def GammaCoordinatewiseMinimal (d : Dual I) : Prop :=
  ∀ p eps, 0 < eps → eps ≤ d.gamma p →
    ¬ (lowerGamma d p eps).Checked

private theorem exists_uniform_positive_lower {T : Type*} [DecidableEq T]
    (s : Finset T) (f : T → ℚ) (hf : ∀ x ∈ s, 0 < f x) :
    ∃ eps : ℚ, 0 < eps ∧ ∀ x ∈ s, eps ≤ f x := by
  induction s using Finset.induction_on with
  | empty => exact ⟨1, by norm_num, by simp⟩
  | @insert a s ha ih =>
      have hfa : 0 < f a := hf a (Finset.mem_insert_self a s)
      have hfs : ∀ x ∈ s, 0 < f x := by
        intro x hx
        exact hf x (Finset.mem_insert_of_mem hx)
      obtain ⟨eps, heps, hbound⟩ := ih hfs
      refine ⟨min (f a) eps, lt_min hfa heps, ?_⟩
      intro x hx
      rcases Finset.mem_insert.mp hx with rfl | hx
      · exact min_le_left _ _
      · exact (min_le_right _ _).trans (hbound x hx)

/-- In any finite 0/1-port wall, essential positive gamma has a tight row. -/
theorem essentialGamma_has_tightD1
    (h01 : ∀ X : I.Cut, ∀ p : I.Port,
      I.cutPort X p = 0 ∨ I.cutPort X p = 1)
    (d : Dual I) (hd : d.Checked)
    (hmin : GammaCoordinatewiseMinimal d)
    (p : I.Port) (hp : 0 < d.gamma p) :
    ∃ X : I.Cut, I.cutPort X p = 1 ∧ d1Slack d X = 0 := by
  classical
  by_contra hex
  have hNo : ∀ X : I.Cut,
      ¬ (I.cutPort X p = 1 ∧ d1Slack d X = 0) := by
    simpa only [not_exists] using hex
  let active : Finset I.Cut :=
    Finset.univ.filter fun X => I.cutPort X p = 1
  have hslack_nonneg : ∀ X : I.Cut, 0 ≤ d1Slack d X := by
    intro X
    exact sub_nonneg.mpr (hd.d1 X)
  have hslack_pos : ∀ X ∈ active, 0 < d1Slack d X := by
    intro X hX
    have hcut : I.cutPort X p = 1 := (Finset.mem_filter.mp hX).2
    have hnonneg := hslack_nonneg X
    by_contra hnot
    have hzero : d1Slack d X = 0 :=
      le_antisymm (le_of_not_gt hnot) hnonneg
    exact hNo X ⟨hcut, hzero⟩
  obtain ⟨eta, heta_pos, heta_le⟩ :=
    exists_uniform_positive_lower active (d1Slack d) hslack_pos
  let eps : ℚ := min (d.gamma p / 2) eta
  have heps_pos : 0 < eps := by
    dsimp [eps]
    exact lt_min (half_pos hp) heta_pos
  have heps_le_gamma : eps ≤ d.gamma p := by
    calc
      eps ≤ d.gamma p / 2 := min_le_left _ _
      _ ≤ d.gamma p := by linarith
  have heps_le_eta : eps ≤ eta := min_le_right _ _
  have hlower : (lowerGamma d p eps).Checked := by
    refine
      { alpha_nonneg := ?_
        beta_nonneg := ?_
        gamma_nonneg := ?_
        delta_nonneg := ?_
        cap_nonneg := ?_
        d1 := ?_
        d2 := ?_ }
    · simpa [lowerGamma] using hd.alpha_nonneg
    · simpa [lowerGamma] using hd.beta_nonneg
    · intro q
      by_cases hqp : q = p
      · subst q
        simp only [lowerGamma, if_pos]
        exact sub_nonneg.mpr heps_le_gamma
      · simpa [lowerGamma, hqp] using hd.gamma_nonneg q
    · simpa [lowerGamma] using hd.delta_nonneg
    · exact hd.cap_nonneg
    · intro X
      rcases h01 X p with hzero | hone
      · simpa [lowerGamma_cutAlpha, lowerGamma_cutBeta,
          lowerGamma_cutGamma, hzero] using hd.d1 X
      · have hXactive : X ∈ active := by simp [active, hone]
        have heta_slack := heta_le X hXactive
        rw [lowerGamma_cutAlpha, lowerGamma_cutBeta,
          lowerGamma_cutGamma, hone]
        dsimp [d1Slack] at heta_slack
        linarith
    · intro q s hlegal
      by_cases hqp : q = p
      · subst q
        simp only [lowerGamma, if_pos]
        exact (sub_le_self _ (le_of_lt heps_pos)).trans (hd.d2 p s hlegal)
      · simpa [lowerGamma, hqp] using hd.d2 q s hlegal
  exact hmin p eps heps_pos heps_le_gamma hlower

/-- Canonical wallLP specialization. The result is a full cut row, not yet a
closed root row; that closure remains part of the open geometric wall. -/
theorem essentialGamma_has_tightD1_wallLP
    {R E JT KTy : Type} [instR : DecidableEq R] [instE : DecidableEq E]
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset KTy)
    (sep : KTy → Finset R) (dB : KTy → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (d : Dual (@wallLP R E JT KTy instR instE S F O J K sep dB inc kap))
    (hd : d.Checked)
    (hmin : GammaCoordinatewiseMinimal
      (I := @wallLP R E JT KTy instR instE S F O J K sep dB inc kap) d)
    (p : (@wallLP R E JT KTy instR instE
      S F O J K sep dB inc kap).Port) (hp : 0 < d.gamma p) :
    ∃ X : (@wallLP R E JT KTy instR instE
      S F O J K sep dB inc kap).Cut,
      (@wallLP R E JT KTy instR instE
        S F O J K sep dB inc kap).cutPort X p = 1 ∧
      d1Slack
        (I := @wallLP R E JT KTy instR instE
          S F O J K sep dB inc kap) d X = 0 := by
  let WI := @wallLP R E JT KTy instR instE S F O J K sep dB inc kap
  have h01 : ∀ X : WI.Cut, ∀ q : WI.Port,
      WI.cutPort X q = 0 ∨ WI.cutPort X q = 1 := by
    intro X q
    change (if q.1 ∈ dB X.1 then (1 : ℚ) else 0) = 0 ∨
      (if q.1 ∈ dB X.1 then (1 : ℚ) else 0) = 1
    by_cases h : q.1 ∈ dB X.1
    · right
      simp [h]
    · left
      simp [h]
  exact essentialGamma_has_tightD1 (I := WI) h01 d hd hmin p hp

end DualMinimality
end CanonicalTightCorner
end Erdos23Delta0

