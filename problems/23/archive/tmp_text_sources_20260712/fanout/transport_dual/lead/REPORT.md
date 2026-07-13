# Lead report: full-product owner-shore transport

## Exact no-go for scalar one-row weights

Let `Delta(i,q) = S(omega[i:=q]) - S(omega)`. If `omega` is a Hamming-one
local minimum, then `Delta(i,q) >= 0` for every alternative. Hence for every
family of nonnegative rational weights `lambda(i,q)`,

`sum_(i,q) lambda(i,q) Delta(i,q) >= 0`.

Thus no scalar heat bath supported only on one-row moves can prove negative
drift at the R29 strict local-minimum cage. This is an algebraic falsifier,
independent of coordinate collision/HitNeed decomposition. The R29 cage
itself remains ungated by this lane.

## Product transport target

Let `Omega = product_i R_i`, `K = |Omega|`, `S(eta)` be the active-scoped
score, and let `A` be a deficient owner shore at `omega`. Put

`d_A = |Demand_A(omega)| - |Source_A(omega)| > 0`.

The exact scalar target is

`sum_(eta in Omega) S(eta) <= K * (S(omega) - d_A)`.                 (PHT)

It implies `S(omega)` is strictly above the uniform product mean and therefore
cannot be a global minimum. Unlike the one-row average, (PHT) permits all
coordinates to change simultaneously.

The cardinal transport realizing (PHT) has

`D* = Sigma eta : Omega, Demand(eta)`

and

`T* = (Omega x OutsideShoreDemand(omega,A)) +
      (Omega x ShoreSource(omega,A))`.

Any injection `D* -> T*` gives (PHT) by exact cardinal arithmetic. For a
component-aware legal-edge relation, finite Farkas/Hall duality says the
injection exists exactly when every `X subset D*` satisfies

`|X| <= K * |OutsideShoreDemand(omega,A)| + K * |N_A(X)|`.         (FH)

Equivalently,

`max(0, |X| - K*|OutsideShoreDemand|) <= K*|N_A(X)|`.

The natural legal relation sends a new demand to an old shore source when its
new active component either intersects an eligible old shore component or
touches a row changed between `omega` and `eta`. Persistent-component
embedding justifies that dichotomy when the component avoids every changed
row.

## Exact gate

`full_heatbath_gate.py` exhaustively evaluated every row tuple in every
order-10/11 graph containing an active-scoped Hall failure. Arithmetic is
integer exact; the reported means are numerator/denominator pairs.

- Hall failures: 705 in 16 graphs.
- Failures satisfying strict mean separation: 705/705.
- Failures satisfying (PHT): 705/705.
- Smallest exact instance: graph6 `I?`ebRodO`, choice `(1,4,4)`, `K=108`,
  `S=19`, `d_A=2`, `K*S-sum S=2020`, residual after `K*d_A` is `1804`.
- The normalized residual is `1804/108 = 451/27`.

## Hashes

- `full_heatbath_gate.py`: `2b7cc737f15f8bd0d2fd679ca18899c26c5b5aa684331268788bcb51443a2dcc`
- `n10_n11_defect.json`: `c986093a3af0cf1e85bae9cca97478bf4e6d775ec2d8ddc53fe3e54c2cac187b`

## Proof gaps

1. (FH) has not been proved from triangle-freeness, changed-row locality,
   persistent-component embedding, and inclusion-minimality of `A`.
2. The product legal relation has not been exact-gated on N=12 or the R29
   2943 cage.
3. Component persistence controls each demand separately; it does not yet
   bound simultaneous congestion into a shared old shore source. This is the
   precise missing lemma.
