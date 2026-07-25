# Erdős Problem 307 — Approach Registry

## DIRECT ROUTE R1: union-first arithmetic-derivative 2-cycle

### 1. Exact final deliverable

Two explicit, finite, disjoint sets of primes `P` and `Q` satisfying

`A(P) = Pi(Q)` and `A(Q) = Pi(P)`,

where `Pi(S) = product_{p in S} p` and
`A(S) = sum_{p in S} Pi(S)/p`.

The certificate must include both sets, primality certificates or
independently replayed deterministic primality checks, and exact integer
evaluation of both identities by two independently implemented verifiers.

### 2. Current frontier certificate

Find one finite squarefree union `U = P union Q` for which

`Delta(U) = A(U)^2 - 4 Pi(U)^2`

is a square and the two roots

`(A(U) + sqrt(Delta(U)))/2` and
`(A(U) - sqrt(Delta(U)))/2`

are the coprime squares `Pi(P)^2` and `Pi(Q)^2` induced by a partition of
the prime divisors of `U`. The full identities `A(P)=Pi(Q)` and
`A(Q)=Pi(P)` must then be checked; a square discriminant alone is not a
certificate.

### 3. Logical bridge

For a prime set `S`, `gcd(A(S),Pi(S))=1`. If

`(A(P)/Pi(P)) (A(Q)/Pi(Q)) = 1`

and `P,Q` are disjoint, coprimality forces
`A(P)=Pi(Q)` and `A(Q)=Pi(P)`, and conversely these identities immediately
give the required reciprocal-sum product. Thus one verified finite
2-cycle resolves the existential problem completely.

For a valid 2-cycle, writing `x=Pi(P)` and `y=Pi(Q)` gives
`A(U)=x^2+y^2` and `Pi(U)=xy`; hence
`Delta(U)=(x^2-y^2)^2`. This supplies a necessary union-first filter.

### 4. Next falsifiable action

Build a GMP/C++ calibration engine that enumerates a declared finite family
of squarefree unions, applies independent modular-square filters followed by
an exact square test, and replays any survivor through both original
2-cycle identities. Calibrate the detector on synthetic planted
Pythagorean data and compare its retained state count and throughput against
the existing forward `P -> A(P)` engines in `open307/` and `search307/`.

### 5. Exit condition

Mark R1 `DEAD` immediately if either:

1. the union-first filter gives no material state-space reduction over the
   existing forward engines on the calibration family; or
2. the predeclared bounded union family is exhausted without an exact
   2-cycle.

A bounded `NO_HIT` is not a partial solution and does not authorize a
cascade to larger prime pools, larger cardinalities, or new equivalent
encodings.

## Status

R1 is `CALIBRATION_PENDING`. No search is authorized beyond the calibration
until all detector, parser, exact-arithmetic, and planted-case checks pass.
