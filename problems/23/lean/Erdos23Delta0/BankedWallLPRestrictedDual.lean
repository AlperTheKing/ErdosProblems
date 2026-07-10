import Erdos23Delta0.BankedWallLPRestricted
import Erdos23Delta0.FiniteFarkasRatBasic

/-!
# Alpha-fixed restricted duals for the finite-Farkas wall interface

This module separates the alpha data from the three cost multipliers and
formalizes the positive-`tau` normalization used by the finite rational Farkas
alternative.  It does not invoke the hard elimination theorem.
-/

namespace Erdos23Delta0
namespace Wall

open scoped BigOperators

variable {I : BankedWallLP}

/-- A dual carrying alpha and zero cost multipliers. -/
def Dual.ofAlpha (alpha : I.Atom -> ℚ) : Dual I where
  alpha := alpha
  beta := 0
  gamma := 0
  delta := 0

/-- Assemble all four dual components. -/
def Dual.ofParts
    (alpha : I.Atom -> ℚ) (beta : I.Short -> ℚ)
    (gamma : I.Port -> ℚ) (delta : I.Sink -> ℚ) : Dual I where
  alpha := alpha
  beta := beta
  gamma := gamma
  delta := delta

@[simp] theorem Dual.ofAlpha_alpha (alpha : I.Atom -> ℚ) :
    (Dual.ofAlpha alpha).alpha = alpha := rfl

@[simp] theorem Dual.ofParts_alpha
    (alpha : I.Atom -> ℚ) (beta : I.Short -> ℚ)
    (gamma : I.Port -> ℚ) (delta : I.Sink -> ℚ) :
    (Dual.ofParts alpha beta gamma delta).alpha = alpha := rfl

/-- A squeeze whose only dual parameter is the fixed alpha vector. -/
abbrev AlphaSqueeze
    (I : BankedWallLP) (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ) :=
  DualSqueeze I Allowed (Dual.ofAlpha alpha)

/-- The restricted dual alternative with alpha fixed externally. -/
structure RestrictedDual
    (I : BankedWallLP) (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ) where
  beta : I.Short -> ℚ
  gamma : I.Port -> ℚ
  delta : I.Sink -> ℚ
  beta_nonneg : forall f, 0 <= beta f
  gamma_nonneg : forall p, 0 <= gamma p
  delta_nonneg : forall s, 0 <= delta s
  d1_allowed : forall X, Allowed X ->
    (Finset.univ.sum fun a => I.cov X a * alpha a) <=
      (Finset.univ.sum fun f => I.useShort X f * beta f) +
        Finset.univ.sum fun p => I.cutPort X p * gamma p
  d2 : forall p s, I.legal p s -> gamma p <= delta s

namespace RestrictedDual

def toDual {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (R : RestrictedDual I Allowed alpha) : Dual I :=
  Dual.ofParts alpha R.beta R.gamma R.delta

def Strict {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (R : RestrictedDual I Allowed alpha) : Prop :=
  totalBeta R.toDual + totalDeltaCap R.toDual < totalAlpha R.toDual

/-- An alpha-fixed restricted dual becomes the existing checked-dual surface. -/
def toRestrictedChecked
    {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}
    (R : RestrictedDual I Allowed alpha)
    (halpha : forall a, 0 <= alpha a)
    (hcap : forall s, 0 <= I.cap s) :
    R.toDual.RestrictedChecked Allowed where
  alpha_nonneg := halpha
  beta_nonneg := R.beta_nonneg
  gamma_nonneg := R.gamma_nonneg
  delta_nonneg := R.delta_nonneg
  cap_nonneg := hcap
  d1_allowed := by
    intro X hX
    simpa [toDual, Dual.ofParts, cutAlpha, cutBeta, cutGamma] using R.d1_allowed X hX
  d2 := R.d2

end RestrictedDual

/-- The homogeneous separator produced directly by Farkas, before normalizing
the alpha-row multiplier `tau` to one. -/
structure RestrictedFarkasCert
    (I : BankedWallLP) (Allowed : I.Cut -> Prop) (alpha : I.Atom -> ℚ) where
  tau : ℚ
  beta : I.Short -> ℚ
  gamma : I.Port -> ℚ
  delta : I.Sink -> ℚ
  tau_nonneg : 0 <= tau
  beta_nonneg : forall f, 0 <= beta f
  gamma_nonneg : forall p, 0 <= gamma p
  delta_nonneg : forall s, 0 <= delta s
  d1_allowed : forall X, Allowed X ->
    tau * (Finset.univ.sum fun a => I.cov X a * alpha a) <=
      (Finset.univ.sum fun f => I.useShort X f * beta f) +
        Finset.univ.sum fun p => I.cutPort X p * gamma p
  d2 : forall p s, I.legal p s -> gamma p <= delta s
  strict :
    (Finset.univ.sum fun f => beta f) +
        (Finset.univ.sum fun s => I.cap s * delta s)
      < tau * Finset.univ.sum fun a => alpha a

namespace RestrictedFarkasCert

variable {Allowed : I.Cut -> Prop} {alpha : I.Atom -> ℚ}

/-- The Farkas alpha multiplier cannot vanish when capacities and cost
multipliers are nonnegative. -/
theorem tau_pos
    (H : RestrictedFarkasCert I Allowed alpha)
    (hcap : forall s, 0 <= I.cap s) : 0 < H.tau := by
  by_contra hnot
  have htzero : H.tau = 0 := le_antisymm (le_of_not_gt hnot) H.tau_nonneg
  have hbeta : 0 <= Finset.univ.sum fun f => H.beta f :=
    Finset.sum_nonneg fun f _ => H.beta_nonneg f
  have hdelta : 0 <= Finset.univ.sum fun s => I.cap s * H.delta s :=
    Finset.sum_nonneg fun s _ => mul_nonneg (hcap s) (H.delta_nonneg s)
  have hnonneg :
      0 <= (Finset.univ.sum fun f => H.beta f) +
        Finset.univ.sum fun s => I.cap s * H.delta s :=
    add_nonneg hbeta hdelta
  have hstrict := H.strict
  rw [htzero, zero_mul] at hstrict
  exact (not_lt_of_ge hnonneg) hstrict

private theorem sum_mul_div
    {J : Type*} [Fintype J] (c x : J -> ℚ) (t : ℚ) :
    (Finset.univ.sum fun j => c j * (x j / t)) =
      (Finset.univ.sum fun j => c j * x j) / t := by
  simp only [div_eq_mul_inv, mul_assoc, Finset.sum_mul]

/-- Normalize a homogeneous separator by its positive alpha multiplier. -/
def normalize
    (H : RestrictedFarkasCert I Allowed alpha)
    (hcap : forall s, 0 <= I.cap s) :
    {R : RestrictedDual I Allowed alpha // R.Strict} := by
  have ht : 0 < H.tau := H.tau_pos hcap
  let R : RestrictedDual I Allowed alpha :=
    { beta := fun f => H.beta f / H.tau
      gamma := fun p => H.gamma p / H.tau
      delta := fun s => H.delta s / H.tau
      beta_nonneg := fun f => div_nonneg (H.beta_nonneg f) ht.le
      gamma_nonneg := fun p => div_nonneg (H.gamma_nonneg p) ht.le
      delta_nonneg := fun s => div_nonneg (H.delta_nonneg s) ht.le
      d1_allowed := by
        intro X hX
        have hdiv :
            (Finset.univ.sum fun a => I.cov X a * alpha a) <=
              ((Finset.univ.sum fun f => I.useShort X f * H.beta f) +
                Finset.univ.sum fun p => I.cutPort X p * H.gamma p) / H.tau := by
          apply (le_div_iff₀ ht).2
          simpa [mul_comm] using H.d1_allowed X hX
        simpa [sum_mul_div, add_div] using hdiv
      d2 := by
        intro p s hlegal
        exact (div_le_div_iff_of_pos_right ht).2 (H.d2 p s hlegal) }
  refine ⟨R, ?_⟩
  have hdiv :
      ((Finset.univ.sum fun f => H.beta f) +
          Finset.univ.sum fun s => I.cap s * H.delta s) / H.tau
        < Finset.univ.sum fun a => alpha a := by
    apply (div_lt_iff₀ ht).2
    simpa [mul_comm] using H.strict
  have hbetaDiv :
      (Finset.univ.sum fun f => H.beta f / H.tau) =
        (Finset.univ.sum fun f => H.beta f) / H.tau := by
    simpa using sum_mul_div (fun _ : I.Short => (1 : ℚ)) H.beta H.tau
  have hdeltaDiv :
      (Finset.univ.sum fun s => I.cap s * (H.delta s / H.tau)) =
        (Finset.univ.sum fun s => I.cap s * H.delta s) / H.tau :=
    sum_mul_div I.cap H.delta H.tau
  change (Finset.univ.sum fun f => H.beta f / H.tau) +
      (Finset.univ.sum fun s => I.cap s * (H.delta s / H.tau)) <
        Finset.univ.sum fun a => alpha a
  rw [hbetaDiv, hdeltaDiv, ← add_div]
  exact hdiv

/-- A normalized strict restricted dual is a homogeneous Farkas certificate
with `tau = 1`. -/
def ofRestricted
    (R : RestrictedDual I Allowed alpha) (hstrict : R.Strict) :
    RestrictedFarkasCert I Allowed alpha where
  tau := 1
  beta := R.beta
  gamma := R.gamma
  delta := R.delta
  tau_nonneg := zero_le_one
  beta_nonneg := R.beta_nonneg
  gamma_nonneg := R.gamma_nonneg
  delta_nonneg := R.delta_nonneg
  d1_allowed := by
    intro X hX
    simpa using R.d1_allowed X hX
  d2 := R.d2
  strict := by
    simpa [RestrictedDual.Strict, RestrictedDual.toDual, Dual.ofParts,
      totalAlpha, totalBeta, totalDeltaCap] using hstrict

end RestrictedFarkasCert

/-- Reinterpret an alpha-only squeeze as a squeeze for any dual with that
alpha vector. -/
def AlphaSqueeze.forDual
    {Allowed : I.Cut -> Prop} {d : Dual I}
    (Z : AlphaSqueeze I Allowed d.alpha) : DualSqueeze I Allowed d where
  theta := Z.theta
  rho := Z.rho
  theta_nonneg := Z.theta_nonneg
  theta_allowed := Z.theta_allowed
  rho_nonneg := Z.rho_nonneg
  rho_legal := Z.rho_legal
  alpha_dominated := by
    simpa [Dual.ofAlpha, totalAlpha, cutAlpha] using Z.alpha_dominated
  short_coeff := Z.short_coeff
  port_coeff_routed := Z.port_coeff_routed
  sink_coeff := Z.sink_coeff

/-- Forget the unused beta/gamma/delta components of a squeeze parameter. -/
def DualSqueeze.toAlphaSqueeze
    {Allowed : I.Cut -> Prop} {d : Dual I}
    (Z : DualSqueeze I Allowed d) : AlphaSqueeze I Allowed d.alpha where
  theta := Z.theta
  rho := Z.rho
  theta_nonneg := Z.theta_nonneg
  theta_allowed := Z.theta_allowed
  rho_nonneg := Z.rho_nonneg
  rho_legal := Z.rho_legal
  alpha_dominated := by
    simpa [Dual.ofAlpha, totalAlpha, cutAlpha] using Z.alpha_dominated
  short_coeff := Z.short_coeff
  port_coeff_routed := Z.port_coeff_routed
  sink_coeff := Z.sink_coeff

end Wall
end Erdos23Delta0
