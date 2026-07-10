# Finite rational Farkas iff for the restricted banked wall LP

Date: 2026-07-09

Status: implementation design against the live `BankedWallLP` and
`BankedWallLPRestricted` APIs.

## Decision

Use a constructive Fourier-Motzkin theorem directly over `Rat`.

Do not base the proof on `ProperCone.relative_hyperplane_separation` over
`Real`. That theorem gives a real separator for membership in a closed cone.
The banked wall needs an exact rational restricted dual. Turning a real
separator into a rational one while preserving active non-strict inequalities
requires a rational-polyhedron transfer theorem; formalizing that transfer is
at least as hard as the direct rational elimination theorem.

The Mathlib Fourier-Motzkin oracle is metaprogramming used by `linarith`; it is
not a theorem-level finite Farkas API and cannot prove the generic existential
statement for arbitrary finite index types.

## Generic theorem

The generic system has finitely many variables and rows:

```lean
namespace FiniteFarkasRat

variable {Row Var : Type*} [Fintype Row] [Fintype Var]

def Feasible (A : Row -> Var -> Rat) (b : Row -> Rat) : Prop :=
  Exists fun x : Var -> Rat =>
    (forall j, 0 <= x j) /\
    forall i, (Finset.univ.sum fun j => A i j * x j) <= b i

def Certificate (A : Row -> Var -> Rat) (b : Row -> Rat) : Prop :=
  Exists fun y : Row -> Rat =>
    (forall i, 0 <= y i) /\
    (forall j, 0 <= Finset.univ.sum fun i => y i * A i j) /\
    (Finset.univ.sum fun i => y i * b i) < 0

theorem certificate_refutes_feasible
    (hcert : Certificate A b) : not (Feasible A b)

theorem certificate_of_not_feasible
    (h : not (Feasible A b)) : Certificate A b

theorem feasible_iff_no_certificate :
    Feasible A b <-> not (Certificate A b)

end FiniteFarkasRat
```

The first theorem is weak duality and finite-sum rearrangement. The second is
the only new duality kernel.

## Constructive elimination kernel

First prove the theorem for variables `Fin n`, then transport an arbitrary
finite `Var` with `Fintype.equivFin Var`.

Append one base inequality `-x_j <= 0` for every variable. A Farkas
combination of the enlarged ordinary inequality system has zero total variable
coefficient. Splitting its nonnegative weights into original rows `y` and
nonnegativity rows `z` yields

```text
sum_i y_i A_ij - z_j = 0,
```

and therefore `0 <= sum_i y_i A_ij`.

Use a certified inequality record during elimination:

```lean
structure CertifiedIneq (Base : Type*) [Fintype Base] (n : Nat) where
  coeff : Fin n -> Rat
  rhs : Rat
  weight : Base -> Rat
  weight_nonneg : forall i, 0 <= weight i
  coeff_eq : forall j,
    coeff j = Finset.univ.sum fun i => weight i * baseCoeff i j
  rhs_eq : rhs = Finset.univ.sum fun i => weight i * baseRhs i
```

To eliminate the last variable, retain every zero-coefficient inequality and,
for every positive/negative pair, take the nonnegative linear combination

```text
(-a_neg) * positive_row + a_pos * negative_row.
```

Its last coefficient is zero. Divide is unnecessary, so certificate weights
stay manifestly rational and nonnegative.

The projection lemma is exact over `Rat`: the remaining variables satisfy all
paired inequalities iff there is a last coordinate satisfying the original
system. Construct the coordinate by taking the maximum finite lower bound;
when no lower bound exists, use the minimum upper bound or zero. Paired
inequalities prove every lower bound is at most every upper bound.

At dimension zero, infeasibility means some certified inequality has negative
right-hand side. Its stored nonnegative base weights are the Farkas
certificate. Recursion on `n` proves `certificate_of_not_feasible`.

No reflection, `native_decide`, or untrusted arithmetic is used.

## Banked LP matrix

For fixed `alpha : I.Atom -> Rat` and `Allowed : I.Cut -> Prop`, use classical
finite subtype instances:

```lean
AllowedCut := {X : I.Cut // Allowed X}
LegalArc := {ps : I.Port x I.Sink // I.legal ps.1 ps.2}
Var := AllowedCut Sum LegalArc
Row := Unit Sum I.Short Sum I.Port Sum I.Sink
```

The row nesting in Lean may use a named inductive type to keep simplification
stable.

Write every squeeze condition as `A*x <= b`:

```text
alpha row:
  - sum_X theta_X * cutAlpha(alpha,X) <= - totalAlpha(alpha)

short f:
    sum_X theta_X * useShort(X,f) <= 1

port p:
    sum_X theta_X * cutPort(X,p) - sum_s rho(p,s) <= 0

sink s:
    sum_p rho(p,s) <= cap(s)
```

Thus a generic Farkas multiplier has components

```text
tau >= 0, beta_f >= 0, gamma_p >= 0, delta_s >= 0.
```

The theta column condition is exactly

```text
tau * cutAlpha(alpha,X) <= cutBeta(beta,X) + cutGamma(gamma,X)
```

for every allowed cut. The legal rho column condition is exactly

```text
gamma_p <= delta_s.
```

The negative right-hand-side condition is

```text
totalBeta(beta) + totalDeltaCap(delta) < tau * totalAlpha(alpha).
```

## Normalization

Prove `0 < tau`. If `tau = 0`, the strict condition becomes

```text
totalBeta(beta) + totalDeltaCap(delta) < 0.
```

Both summands are nonnegative because `beta`, `delta`, and `cap` are
nonnegative. This is impossible. Since `tau >= 0`, `tau != 0` gives `0 < tau`.

Normalize

```text
beta' f = beta f / tau
gamma' p = gamma p / tau
delta' s = delta s / tau.
```

Division by the positive rational `tau` preserves D1, D2, and nonnegativity,
and the strict objective becomes

```text
totalBeta(beta') + totalDeltaCap(delta') < totalAlpha(alpha).
```

The reverse translation sets `tau = 1`.

## API adapters

Do not duplicate `DualSqueeze`. Add a zero-cost dual carrying only alpha:

```lean
def Dual.ofAlpha (alpha : I.Atom -> Rat) : Dual I where
  alpha := alpha
  beta := 0
  gamma := 0
  delta := 0

abbrev AlphaSqueeze (Allowed) (alpha) :=
  DualSqueeze I Allowed (Dual.ofAlpha alpha)
```

Add the alpha-fixed restricted witness:

```lean
structure RestrictedDual
    (I : BankedWallLP) (Allowed : I.Cut -> Prop)
    (alpha : I.Atom -> Rat) where
  beta : I.Short -> Rat
  gamma : I.Port -> Rat
  delta : I.Sink -> Rat
  beta_nonneg : forall f, 0 <= beta f
  gamma_nonneg : forall p, 0 <= gamma p
  delta_nonneg : forall s, 0 <= delta s
  d1_allowed : forall X, Allowed X ->
    cutAlpha (Dual.ofAlpha alpha) X <=
      cutBeta (toDual ...) X + cutGamma (toDual ...) X
  d2 : forall p s, I.legal p s -> gamma p <= delta s

def RestrictedDual.Strict (R) : Prop :=
  totalBeta R.toDual + totalDeltaCap R.toDual <
    totalAlpha (Dual.ofAlpha alpha)
```

The final banked theorem is:

```lean
theorem alphaSqueeze_exists_iff_no_restrictedStrict
    (Allowed : I.Cut -> Prop)
    (alpha : I.Atom -> Rat)
    (hcap : forall s, 0 <= I.cap s) :
    Nonempty (AlphaSqueeze (I := I) Allowed alpha) <->
      not (Exists fun R : RestrictedDual I Allowed alpha => R.Strict)
```

`alpha_nonneg` is not needed by finite Farkas itself. It is carried separately
when adapting a checked wall dual.

For an existing `d : Dual I`, alpha-extensionality gives

```lean
AlphaSqueeze Allowed d.alpha ~= DualSqueeze I Allowed d
```

because `DualSqueeze` depends on `d` only through `totalAlpha d` and
`cutAlpha d`; beta/gamma/delta are absent from all squeeze fields.

## Module staging

1. `FiniteFarkasRatBasic.lean`
   - `Feasible`, `Certificate`, weak duality, finite-index transport.
2. `FiniteFarkasRatElim.lean`
   - certified inequalities, one-variable projection, recursive alternative.
3. `BankedWallLPRestrictedDual.lean`
   - `Dual.ofAlpha`, `RestrictedDual`, normalization and adapters.
4. `BankedWallLPFiniteFarkas.lean`
   - matrix encoding, feasibility/squeeze equivalence, certificate/restricted
     dual equivalence, final iff.

The first compiled increment should be modules 1 and 3 plus the matrix
coefficient definitions. This exposes every sign and normalization obligation
before the elimination recursion is added.

## Acceptance gates

- `lake env lean` on each module with the project root and accepted cache.
- forbidden-token grep: zero `sorry`, `admit`, `native_decide`.
- `#print axioms` on the final iff: subset of
  `[propext, Classical.choice, Quot.sound]`.
- finite exact smoke tests where both alternatives are exercised, including a
  zero-multiplier candidate rejected only by `cap_nonneg`.
