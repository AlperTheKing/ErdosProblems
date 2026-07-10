import Erdos23Delta0.FiniteFarkasRatElim
import Erdos23Delta0.BankedWallLPRestrictedDual

/-!
# Finite rational Farkas for the restricted banked wall LP

This module instantiates the generic constructive theorem of alternatives with
the exact four squeeze rows.  Two zero-right-side support row families force
disallowed cut weights and illegal routing weights to vanish.
-/

namespace Erdos23Delta0
namespace Wall

open scoped BigOperators

variable {I : BankedWallLP}

local instance legalDecidable (p : I.Port) (s : I.Sink) :
    Decidable (I.legal p s) := I.legalDecidable p s

abbrev FarkasVar (I : BankedWallLP) := Sum I.Cut (I.Port × I.Sink)

abbrev FarkasRow (I : BankedWallLP) :=
  Sum Unit (Sum I.Short (Sum I.Port
    (Sum I.Sink (Sum I.Cut (I.Port × I.Sink)))))

def alphaRow : FarkasRow I := Sum.inl ()
def shortRow (f : I.Short) : FarkasRow I := Sum.inr (Sum.inl f)
def portRow (p : I.Port) : FarkasRow I := Sum.inr (Sum.inr (Sum.inl p))
def sinkRow (s : I.Sink) : FarkasRow I :=
  Sum.inr (Sum.inr (Sum.inr (Sum.inl s)))
def cutSupportRow (X : I.Cut) : FarkasRow I :=
  Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl X))))
def arcSupportRow (p : I.Port) (s : I.Sink) : FarkasRow I :=
  Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (p, s)))))

def cutVar (X : I.Cut) : FarkasVar I := Sum.inl X
def routeVar (p : I.Port) (s : I.Sink) : FarkasVar I := Sum.inr (p, s)

@[simp] theorem sum_prod_fst_eq
    [DecidableEq I.Port]
    (f : I.Port -> I.Sink -> ℚ) (p0 : I.Port) :
    (Finset.univ.sum fun ps : I.Port × I.Sink =>
      if ps.1 = p0 then f ps.1 ps.2 else 0) =
      Finset.univ.sum fun s => f p0 s := by
  classical
  rw [Fintype.sum_prod_type]
  simp

@[simp] theorem sum_prod_snd_eq
    [DecidableEq I.Sink]
    (f : I.Port -> I.Sink -> ℚ) (s0 : I.Sink) :
    (Finset.univ.sum fun ps : I.Port × I.Sink =>
      if ps.2 = s0 then f ps.1 ps.2 else 0) =
      Finset.univ.sum fun p => f p s0 := by
  classical
  rw [Fintype.sum_prod_type]
  simp

theorem sum_cut_support
    {Allowed : I.Cut -> Prop} [DecidableEq I.Cut] [DecidablePred Allowed]
    (w : I.Cut -> ℚ) (X : I.Cut) :
    (Finset.univ.sum fun Y =>
      w Y * (if Not (Allowed Y) ∧ X = Y then (1 : ℚ) else 0)) =
      if Not (Allowed X) then w X else 0 := by
  classical
  simp only [mul_ite, mul_one, mul_zero]
  have hterm : forall Y : I.Cut,
      (if Not (Allowed Y) ∧ X = Y then w Y else 0) =
        if Y = X then (if Not (Allowed X) then w X else 0) else 0 := by
    intro Y
    by_cases hYX : Y = X
    · subst Y
      simp
    · have hXY : X ≠ Y := fun h => hYX h.symm
      simp [hYX, hXY]
  simp_rw [hterm]
  simp

theorem sum_arc_support
    [DecidableEq I.Port] [DecidableEq I.Sink]
    (w : I.Port -> I.Sink -> ℚ) (p : I.Port) (s : I.Sink) :
    (Finset.univ.sum fun qs : I.Port × I.Sink =>
      w qs.1 qs.2 *
        (if Not (I.legal qs.1 qs.2) ∧ (p, s) = qs then (1 : ℚ) else 0)) =
      if Not (I.legal p s) then w p s else 0 := by
  classical
  simp only [mul_ite, mul_one, mul_zero]
  have hterm : forall qs : I.Port × I.Sink,
      (if Not (I.legal qs.1 qs.2) ∧ (p, s) = qs then w qs.1 qs.2 else 0) =
        if qs = (p, s) then
          (if Not (I.legal p s) then w p s else 0) else 0 := by
    intro qs
    by_cases hqs : qs = (p, s)
    · subst qs
      simp
    · have hsq : (p, s) ≠ qs := fun h => hqs h.symm
      simp [hqs, hsq]
  simp_rw [hterm]
  simp

/-- Matrix of the squeeze feasibility system. -/
noncomputable def squeezeA
    (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ) :
    FarkasRow I -> FarkasVar I -> ℚ := by
  classical
  intro r v
  exact match r, v with
    | Sum.inl _, Sum.inl X => -cutAlpha (Dual.ofAlpha alpha) X
    | Sum.inl _, Sum.inr _ => 0
    | Sum.inr (Sum.inl f), Sum.inl X => I.useShort X f
    | Sum.inr (Sum.inl _), Sum.inr _ => 0
    | Sum.inr (Sum.inr (Sum.inl p)), Sum.inl X => I.cutPort X p
    | Sum.inr (Sum.inr (Sum.inl p)), Sum.inr ps => if ps.1 = p then -1 else 0
    | Sum.inr (Sum.inr (Sum.inr (Sum.inl _))), Sum.inl _ => 0
    | Sum.inr (Sum.inr (Sum.inr (Sum.inl s))), Sum.inr ps => if ps.2 = s then 1 else 0
    | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl Y)))), Sum.inl X =>
        if Not (Allowed Y) ∧ X = Y then 1 else 0
    | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl _)))), Sum.inr _ => 0
    | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr _)))), Sum.inl _ => 0
    | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr qs)))), Sum.inr ps =>
        if Not (I.legal qs.1 qs.2) ∧ ps = qs then 1 else 0

/-- Right-hand side of the squeeze feasibility system. -/
def squeezeB (alpha : I.Atom -> ℚ) : FarkasRow I -> ℚ
  | Sum.inl _ => -totalAlpha (Dual.ofAlpha alpha)
  | Sum.inr (Sum.inl _) => 1
  | Sum.inr (Sum.inr (Sum.inl _)) => 0
  | Sum.inr (Sum.inr (Sum.inr (Sum.inl s))) => I.cap s
  | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl _)))) => 0
  | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr _)))) => 0

abbrev SqueezeFeasible
    (I : BankedWallLP) (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ) :=
  FiniteFarkasRat.Feasible (squeezeA Allowed alpha) (squeezeB alpha)

namespace SqueezeFeasible

/-- Matrix feasibility gives the existing alpha-only squeeze. -/
noncomputable def toAlphaSqueeze
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (P : SqueezeFeasible I Allowed alpha) : AlphaSqueeze I Allowed alpha := by
  classical
  refine
    { theta := fun X => P.x (cutVar X)
      rho := fun p s => P.x (routeVar p s)
      theta_nonneg := fun X => P.x_nonneg (cutVar X)
      theta_allowed := ?_
      rho_nonneg := fun p s => P.x_nonneg (routeVar p s)
      rho_legal := ?_
      alpha_dominated := ?_
      short_coeff := ?_
      port_coeff_routed := ?_
      sink_coeff := ?_ }
  · intro X hne
    by_contra hallowed
    have hs := P.row_le (cutSupportRow X)
    have hx : P.x (cutVar X) <= 0 := by
      simpa [squeezeA, squeezeB, cutSupportRow, cutVar, routeVar, hallowed] using hs
    exact hne (le_antisymm hx (P.x_nonneg (cutVar X)))
  · intro p s hne
    by_contra hlegal
    have hs := P.row_le (arcSupportRow p s)
    have hx : P.x (routeVar p s) <= 0 := by
      simpa [squeezeA, squeezeB, arcSupportRow, cutVar, routeVar, hlegal] using hs
    exact hne (le_antisymm hx (P.x_nonneg (routeVar p s)))
  · have h := P.row_le (alphaRow (I := I))
    have h' :
        -(Finset.univ.sum fun X =>
            P.x (cutVar X) * cutAlpha (Dual.ofAlpha alpha) X) <=
          -totalAlpha (Dual.ofAlpha alpha) := by
      simpa [squeezeA, squeezeB, alphaRow, cutVar, routeVar, mul_comm,
        Finset.sum_neg_distrib] using h
    linarith
  · intro f
    simpa [squeezeA, squeezeB, shortRow, cutVar, routeVar, mul_comm] using
      P.row_le (shortRow f)
  · intro p
    have h := P.row_le (portRow p)
    have h0 :
        (Finset.univ.sum fun X => P.x (cutVar X) * I.cutPort X p) +
            (Finset.univ.sum fun ps : I.Port × I.Sink =>
              if ps.1 = p then -P.x (routeVar ps.1 ps.2) else 0) <= 0 := by
      simpa [squeezeA, squeezeB, portRow, cutVar, routeVar, mul_comm] using h
    rw [sum_prod_fst_eq (f := fun p s => -P.x (routeVar p s)) p,
      Finset.sum_neg_distrib] at h0
    linarith
  · intro s
    have h := P.row_le (sinkRow s)
    have h0 :
        (Finset.univ.sum fun ps : I.Port × I.Sink =>
          if ps.2 = s then P.x (routeVar ps.1 ps.2) else 0) <= I.cap s := by
      simpa [squeezeA, squeezeB, sinkRow, cutVar, routeVar, mul_comm] using h
    rw [sum_prod_snd_eq (f := fun p s => P.x (routeVar p s)) s] at h0
    exact h0

end SqueezeFeasible

namespace AlphaSqueeze

/-- The existing alpha-only squeeze supplies a point of the exact matrix
system. -/
noncomputable def toFiniteFeasible
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (Z : AlphaSqueeze I Allowed alpha) : SqueezeFeasible I Allowed alpha := by
  classical
  refine
    { x := fun v => match v with
        | Sum.inl X => Z.theta X
        | Sum.inr ps => Z.rho ps.1 ps.2
      x_nonneg := ?_
      row_le := ?_ }
  · intro v
    cases v with
    | inl X => exact Z.theta_nonneg X
    | inr ps => exact Z.rho_nonneg ps.1 ps.2
  · intro r
    rcases r with _ | r
    · have h := Z.alpha_dominated
      simpa [squeezeA, squeezeB, cutVar, routeVar, Finset.sum_neg_distrib,
        mul_comm] using neg_le_neg h
    · rcases r with f | r
      · simpa [squeezeA, squeezeB, cutVar, routeVar, mul_comm] using Z.short_coeff f
      · rcases r with p | r
        · have hp := Z.port_coeff_routed p
          have h0 :
              (Finset.univ.sum fun X => Z.theta X * I.cutPort X p) +
                  (Finset.univ.sum fun s => -Z.rho p s) <= 0 := by
            rw [Finset.sum_neg_distrib]
            linarith
          have hprod :
              (Finset.univ.sum fun ps : I.Port × I.Sink =>
                if ps.1 = p then -Z.rho ps.1 ps.2 else 0) =
                  Finset.univ.sum fun s => -Z.rho p s :=
            sum_prod_fst_eq (fun p s => -Z.rho p s) p
          simpa [squeezeA, squeezeB, cutVar, routeVar, mul_comm, hprod] using h0
        · rcases r with s | r
          · have hprod :
                (Finset.univ.sum fun ps : I.Port × I.Sink =>
                  if ps.2 = s then Z.rho ps.1 ps.2 else 0) =
                    Finset.univ.sum fun p => Z.rho p s :=
              sum_prod_snd_eq (fun p s => Z.rho p s) s
            simpa [squeezeA, squeezeB, cutVar, routeVar, mul_comm, hprod] using
              Z.sink_coeff s
          · rcases r with X | ps
            · by_cases hallowed : Allowed X
              · simp [squeezeA, squeezeB, hallowed]
              · have hz : Z.theta X = 0 := by
                  by_contra hne
                  exact hallowed (Z.theta_allowed X hne)
                simp [squeezeA, squeezeB, hallowed, hz]
            · by_cases hlegal : I.legal ps.1 ps.2
              · simp [squeezeA, squeezeB, hlegal]
              · have hz : Z.rho ps.1 ps.2 = 0 := by
                  by_contra hne
                  exact hlegal (Z.rho_legal ps.1 ps.2 hne)
                simp [squeezeA, squeezeB, hlegal, hz]

end AlphaSqueeze

abbrev SqueezeCertificate
    (I : BankedWallLP) (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ) :=
  FiniteFarkasRat.Certificate (squeezeA Allowed alpha) (squeezeB alpha)

namespace SqueezeCertificate

/-- A generic matrix separator is exactly a homogeneous restricted dual after
discarding the zero-right-side support-row multipliers. -/
noncomputable def toRestrictedFarkasCert
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (C : SqueezeCertificate I Allowed alpha) :
    RestrictedFarkasCert I Allowed alpha := by
  classical
  refine
    { tau := C.y (alphaRow (I := I))
      beta := fun f => C.y (shortRow f)
      gamma := fun p => C.y (portRow p)
      delta := fun s => C.y (sinkRow s)
      tau_nonneg := C.y_nonneg (alphaRow (I := I))
      beta_nonneg := fun f => C.y_nonneg (shortRow f)
      gamma_nonneg := fun p => C.y_nonneg (portRow p)
      delta_nonneg := fun s => C.y_nonneg (sinkRow s)
      d1_allowed := ?_
      d2 := ?_
      strict := ?_ }
  · intro X hallowed
    have hcol := C.column_nonneg (cutVar X)
    have hsupport :
        (Finset.univ.sum fun Y : I.Cut =>
          if Not (Allowed Y) ∧ X = Y then C.y (cutSupportRow Y) else 0) = 0 := by
      apply Finset.sum_eq_zero
      intro Y _
      by_cases hXY : X = Y
      · subst Y
        simp [hallowed]
      · simp [hXY]
    simp [squeezeA, cutVar] at hcol
    have hsupportRaw :
        (Finset.univ.sum fun Y : I.Cut =>
          if Not (Allowed Y) ∧ X = Y then
            C.y (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl Y))))) else 0) = 0 := by
      simpa [cutSupportRow] using hsupport
    rw [hsupportRaw] at hcol
    simpa [alphaRow, shortRow, portRow, cutAlpha, Dual.ofAlpha, mul_comm] using hcol
  · intro p s hlegal
    have hcol := C.column_nonneg (routeVar p s)
    have hsupport :
        (Finset.univ.sum fun qs : I.Port × I.Sink =>
          if Not (I.legal qs.1 qs.2) ∧ (p, s) = qs then
            C.y (arcSupportRow qs.1 qs.2) else 0) = 0 := by
      apply Finset.sum_eq_zero
      intro qs _
      by_cases hqs : (p, s) = qs
      · subst qs
        simp [hlegal]
      · simp [hqs]
    simp [squeezeA, routeVar] at hcol
    have hsupportRaw :
        (Finset.univ.sum fun qs : I.Port × I.Sink =>
          if Not (I.legal qs.1 qs.2) ∧ (p, s) = qs then
            C.y (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr qs))))) else 0) = 0 := by
      simpa [arcSupportRow] using hsupport
    rw [hsupportRaw] at hcol
    simpa [portRow, sinkRow] using hcol
  · simpa [squeezeB, totalAlpha, Dual.ofAlpha, mul_comm] using C.rhs_neg

end SqueezeCertificate

namespace RestrictedFarkasCert

private def cutBase
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (H : RestrictedFarkasCert I Allowed alpha) (X : I.Cut) : ℚ :=
  ((Finset.univ.sum fun f => I.useShort X f * H.beta f) +
      Finset.univ.sum fun p => I.cutPort X p * H.gamma p) -
    H.tau * cutAlpha (Dual.ofAlpha alpha) X

private def arcBase
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (H : RestrictedFarkasCert I Allowed alpha) (p : I.Port) (s : I.Sink) : ℚ :=
  H.delta s - H.gamma p

set_option maxHeartbeats 1000000 in
/- Add zero-cost support multipliers to turn a homogeneous restricted dual
into a generic matrix Farkas certificate. -/
noncomputable def toSqueezeCertificate
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (H : RestrictedFarkasCert I Allowed alpha) :
    SqueezeCertificate I Allowed alpha := by
  classical
  let cutSlack : I.Cut -> ℚ := fun X =>
    if Allowed X then 0 else max 0 (-cutBase H X)
  let arcSlack : I.Port -> I.Sink -> ℚ := fun p s =>
    if I.legal p s then 0 else max 0 (-arcBase H p s)
  let y : FarkasRow I -> ℚ
    | Sum.inl _ => H.tau
    | Sum.inr (Sum.inl f) => H.beta f
    | Sum.inr (Sum.inr (Sum.inl p)) => H.gamma p
    | Sum.inr (Sum.inr (Sum.inr (Sum.inl s))) => H.delta s
    | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl X)))) => cutSlack X
    | Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr ps)))) => arcSlack ps.1 ps.2
  refine
    { y := y
      y_nonneg := ?_
      column_nonneg := ?_
      rhs_neg := ?_ }
  · intro r
    rcases r with _ | r
    · exact H.tau_nonneg
    · rcases r with f | r
      · exact H.beta_nonneg f
      · rcases r with p | r
        · exact H.gamma_nonneg p
        · rcases r with s | r
          · exact H.delta_nonneg s
          · rcases r with X | ps
            · by_cases hallowed : Allowed X
              · change 0 <= cutSlack X
                simp [cutSlack, hallowed]
              · change 0 <= cutSlack X
                simp [cutSlack, hallowed]
            · by_cases hlegal : I.legal ps.1 ps.2
              · change 0 <= arcSlack ps.1 ps.2
                simp [arcSlack, hlegal]
              · change 0 <= arcSlack ps.1 ps.2
                simp [arcSlack, hlegal]
  · intro v
    cases v with
    | inl X =>
        by_cases hallowed : Allowed X
        · have hd1 := H.d1_allowed X hallowed
          have hbase : 0 <= cutBase H X := by
            exact sub_nonneg.mpr hd1
          have hs :
              (Finset.univ.sum fun Y : I.Cut =>
                if Not (Allowed Y) ∧ X = Y then cutSlack Y else 0) = 0 := by
            apply Finset.sum_eq_zero
            intro Y _
            by_cases hXY : X = Y
            · subst Y
              simp [hallowed]
            · simp [hXY]
          simpa [squeezeA, y, cutBase, hs, mul_comm] using hbase
        · have hmax : -cutBase H X <= max 0 (-cutBase H X) := le_max_right _ _
          have hbase : 0 <= cutBase H X + cutSlack X := by
            simp [cutSlack, hallowed]
            linarith
          have hs :
              (Finset.univ.sum fun Y : I.Cut =>
                if Not (Allowed Y) ∧ X = Y then cutSlack Y else 0) = cutSlack X := by
            simpa [hallowed] using
              (sum_cut_support (Allowed := Allowed) cutSlack X)
          have hle :
              H.tau * cutAlpha (Dual.ofAlpha alpha) X <=
                ((Finset.univ.sum fun f => I.useShort X f * H.beta f) +
                  (Finset.univ.sum fun p => I.cutPort X p * H.gamma p)) + cutSlack X := by
            apply sub_nonneg.mp
            unfold cutBase at hbase
            simpa [sub_eq_add_neg, add_assoc, add_comm, add_left_comm] using hbase
          simpa [squeezeA, y, hs, mul_comm, add_assoc] using hle
    | inr ps =>
        by_cases hlegal : I.legal ps.1 ps.2
        · have hd2 := H.d2 ps.1 ps.2 hlegal
          have hbase : 0 <= arcBase H ps.1 ps.2 :=
            sub_nonneg.mpr hd2
          have hs :
              (Finset.univ.sum fun qs : I.Port × I.Sink =>
                if Not (I.legal qs.1 qs.2) ∧ ps = qs then
                  arcSlack qs.1 qs.2 else 0) = 0 := by
            apply Finset.sum_eq_zero
            intro qs _
            by_cases hqs : ps = qs
            · subst qs
              simp [hlegal]
            · simp [hqs]
          simpa [squeezeA, y, arcBase, hs, mul_comm] using hbase
        · have hmax : -arcBase H ps.1 ps.2 <=
              max 0 (-arcBase H ps.1 ps.2) := le_max_right _ _
          have hbase : 0 <= arcBase H ps.1 ps.2 + arcSlack ps.1 ps.2 := by
            simp [arcSlack, hlegal]
            linarith
          have hs :
              (Finset.univ.sum fun qs : I.Port × I.Sink =>
                if Not (I.legal qs.1 qs.2) ∧ ps = qs then
                  arcSlack qs.1 qs.2 else 0) = arcSlack ps.1 ps.2 := by
            simpa [hlegal] using
              (sum_arc_support (I := I) (fun p s => arcSlack p s) ps.1 ps.2)
          have hle : H.gamma ps.1 <= H.delta ps.2 + arcSlack ps.1 ps.2 := by
            unfold arcBase at hbase
            linarith
          simpa [squeezeA, y, hs, mul_comm] using hle
  · simpa [squeezeB, y, mul_comm] using H.strict

end RestrictedFarkasCert

/-- The exact restricted finite-Farkas equivalence for a fixed alpha vector. -/
theorem alphaSqueeze_exists_iff_no_restrictedStrict
    (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ)
    (hcap : forall s, 0 <= I.cap s) :
    Nonempty (AlphaSqueeze I Allowed alpha) <->
      Not (Exists fun R : RestrictedDual I Allowed alpha => R.Strict) := by
  constructor
  · rintro ⟨Z⟩ hstrict
    obtain ⟨R, hR⟩ := hstrict
    let H : RestrictedFarkasCert I Allowed alpha :=
      RestrictedFarkasCert.ofRestricted R hR
    let C : SqueezeCertificate I Allowed alpha := H.toSqueezeCertificate
    exact C.refutes_feasible ⟨Z.toFiniteFeasible⟩
  · intro hstrict
    have hcert : Not (Nonempty (SqueezeCertificate I Allowed alpha)) := by
      rintro ⟨C⟩
      let H : RestrictedFarkasCert I Allowed alpha := C.toRestrictedFarkasCert
      obtain ⟨R, hR⟩ := H.normalize hcap
      exact hstrict ⟨R, hR⟩
    have hfeas : Nonempty (SqueezeFeasible I Allowed alpha) :=
      (FiniteFarkasRat.feasible_iff_no_certificate).2 hcert
    exact ⟨hfeas.some.toAlphaSqueeze⟩

/-- API-compatible form of `dualSqueeze_exists_iff_no_restrictedStrict`: the
squeeze parameter may be any dual carrying the fixed alpha vector. -/
theorem dualSqueeze_exists_iff_no_restrictedStrict
    (Allowed : I.Cut -> Prop) (d : Dual I)
    (hcap : forall s, 0 <= I.cap s) :
    Nonempty (DualSqueeze I Allowed d) <->
      Not (Exists fun R : RestrictedDual I Allowed d.alpha => R.Strict) := by
  constructor
  · rintro ⟨Z⟩
    exact (alphaSqueeze_exists_iff_no_restrictedStrict Allowed d.alpha hcap).1
      ⟨Z.toAlphaSqueeze⟩
  · intro h
    obtain ⟨Z⟩ :=
      (alphaSqueeze_exists_iff_no_restrictedStrict Allowed d.alpha hcap).2 h
    exact ⟨Z.forDual⟩

end Wall
end Erdos23Delta0
