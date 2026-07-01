# Schur Absorption-Hall Target

Status: strongest current Schur-side proof target.

This strengthens the singleton minority-current lemma to subsets of overloaded
vertices.  It is still a graph-theoretic statement about the Hardy Schur
complement; it is not a generic M-matrix theorem.

## Setup

Let

```text
H = diag(N - T) + Lstar,
O = {v : T(v) > N},
U = V \ O,
S = H_OO - H_OU H_UU^{-1} H_UO.
```

Write

```text
S = L_c + diag(rho),
rho_o = sum_p S[o,p],
a_o = T(o)-N,
A = sum_{o in O} a_o,
b_o = a_o + rho_o.
```

With `h_O=1` and `H_UU h_U=-H_UO 1`, the quantity `b_o` is the Hardy normal
current from overloaded terminal `o` into the non-overloaded block:

```text
b_o = I_o = (Lstar h)_o.
```

## Absorption-Hall Inequality

For every subset `X subset O`,

```text
a(X) <= A - a(X)   ==>   b(X) >= a(X).
```

Equivalently,

```text
a(X) <= A - a(X)   ==>   rho(X) >= 0.
```

This says every non-strict-majority overload set absorbs at least its own
overload through the harmonic Hardy current.

## Quantitative Candidate

The current strongest exact-tested form is the `1/25` strengthening:

```text
a(X) <= A-a(X)  ==>  rho(X) >= (A-2a(X))/25.
```

Equivalently,

```text
b(X) >= a(X) + (A-2a(X))/25.
```

This strictly implies Absorption-Hall for every non-strict-majority subset.
The constant is natural for the Erdős `N^2/25` scale, and it is much more
proof-facing than the bare nonnegativity statement because the right side is a
linear overload-imbalance term.

It is enough to prove the singleton form:

```text
a_o <= A-a_o  ==>  rho_o >= (A-2a_o)/25.
```

Indeed, if `X` is non-strict-majority then it contains no strict-majority
vertex, so the singleton inequality applies to every `o in X`.  Summing gives

```text
rho(X) >= (|X|A - 2a(X))/25 >= (A - 2a(X))/25.
```

Thus the quantitative subset Hall statement reduces to a pointwise minority
current inequality.

The singleton case is exactly the strict-majority row-shunt implication:

```text
rho_o < 0  ==>  a_o > A-a_o.
```

Since at most one overload vertex can be a strict majority, this gives

```text
|{o : rho_o < 0}| <= 1.
```

## What It Does And Does Not Prove

Absorption-Hall is not, by itself, a generic PSD criterion for an arbitrary
Z-matrix.  A one-vertex strict-majority set may still have `rho<0`, and a
generic Z-matrix can fail PSD there if the conductance from that apex to the
positive-shunt reservoir is too small.

Therefore the Schur proof package remains:

```text
1. S is a symmetric Z-matrix.
2. Absorption-Hall holds, hence R={rho<0} has size at most one.
3. If R={a}, the direct star rescue holds:

   rho_a + sum_{p != a} c_ap rho_p/(c_ap+rho_p) >= 0.
```

Then `S >= 0` follows from the algebraic one-negative-star lemma.

## Algebraic Bridge

The exact linear-algebra package needed after the graph-theoretic
Absorption-Hall lemma is the following.

### Lemma: absorption plus one-star implies PSD

Let `S` be a symmetric Z-matrix indexed by `O`, and write

```text
c_ij = -S_ij >= 0,
rho_i = sum_j S_ij,
S = L_c + diag(rho).
```

Let `a_i>0`, `A=sum_i a_i`, and assume:

```text
(AH)   a(X) <= A-a(X)  ==>  rho(X) >= 0       for every X subset O.
```

Then `R={i:rho_i<0}` has size at most one.  Indeed, if `rho_i<0`, then the
singleton `X={i}` cannot satisfy `a_i<=A-a_i`, so `a_i>A-a_i`; two such
vertices cannot coexist.

If `R` is empty, then

```text
S = L_c + diag(rho)
```

is a sum of a PSD Laplacian and a nonnegative diagonal matrix, so `S>=0`.

If `R={a}`, assume additionally the star condition

```text
rho_a + sum_{p != a} c_ap*rho_p/(c_ap+rho_p) >= 0,
```

omitting zero-denominator terms.  Split

```text
S = S_star + L_extra,
```

where `S_star` keeps only the conductances incident with `a` and all shunts
`rho_p` for `p!=a`, while `L_extra` is the PSD Laplacian on `O\{a}` formed by
all conductances not incident with `a`.  Schur-eliminating the leaves
`p!=a` in `S_star` gives the scalar

```text
rho_a + sum_p c_ap*rho_p/(c_ap+rho_p).
```

So the star condition gives `S_star>=0`, hence `S>=0`.

Thus the remaining graph theory can be cleanly split into:

```text
G1. Absorption-Hall for non-majority subsets.
G2. Star rescue for the unique strict-majority deficient apex, if it exists.
```

No statement about arbitrary Z-matrices beyond this algebraic bridge is being
used.

## Exact Gates

The current gate is

```text
python problems/23/writeup/_schur_absorption_hall_gate.py
```

It checks every subset of `O` satisfying `a(X)<=A-a(X)` and asserts
`rho(X)>=0`.

Claude's independent acceptance run reported:

```text
708 O-nonempty gamma-min cuts
12043 subset checks
0 absorption-Hall failures
R_hist = {0:707, 1:1}
```

Local gates on overlapping batteries reported the same zero-failure behavior.

The quantitative `1/25` gate is

```text
python problems/23/writeup/_schur_absorption_coeff_gate.py
```

Local result:

```text
Ocuts = 713
subset checks = 12053
coefficient = 1/25
failures = 0
minimum margin ≈ 0.13385187584101116
minimum case = MycGrotzsch_N23, minority singleton
```

Claude's full acceptance run independently confirmed:

```text
O-cuts = 708
non-majority subset checks = 12043
coefficient = 1/25
failures = 0
minimum slack in 25*rho(X) - (A-2a(X)) is positive
```

A local coefficient sweep gives a sharper finite-battery bracket:

```text
coefficient = 1/22: failures = 0, minimum margin ≈ 0.002664821008652903
coefficient = 1/21: fails on MycGrotzsch_N23, minority singleton
```

These coefficient gates are finite-battery observations only.  Larger C5
blowups falsify every fixed positive coefficient of this singleton form.

The diagnostic ratio probe is

```text
python problems/23/writeup/_schur_absorption_ratio_probe.py
```

It records the smallest exact value of `rho(X)/(A-2a(X))` over positive-gap
subsets.  Local result:

```text
positive-gap checks = 6581
minimum ratio ≈ 0.04556534439990252
minimum case = MycGrotzsch_N23, minority singleton
```

This agrees with the `1/22` pass and `1/21` failure on the finite battery, but
it is not graphon-stable.

## Larger Blowup Falsification

For canonical C5 blowups with sizes

```text
[k+1,k,k+1,k,k+1]
```

and a gamma-minimal maxcut leaving one minimum-product edge bad, the quotient
calculation gives, for a minority overloaded vertex,

```text
a_o = 2,
A = 4k,
g_o = A - 2a_o = 4k - 4,
psi0 = 3/(3+BETA[5]*k),
psi2 = 3/(3+2*BETA[5]*k),
rho_o = BETA[5]*(k+1)*(psi0+psi2) - 2.
```

Thus the pointwise `1/25` margin is

```text
25*rho_o - g_o.
```

Exact scan with the repository rational `BETA[5]`:

```text
k=13, N=68:  margin  +8.4838246968
k=14, N=73:  margin  +4.8568737145
k=15, N=78:  margin  +1.1863529360
k=16, N=83:  margin  -2.5205246417  <-- first failure
k=20, N=103: margin -17.6129970708
k=100,N=503: margin -334.3912356816
```

So the quantitative `1/25` Absorption-Hall target and the pointwise
minority-current lemma are false at blowup scale.  The surviving Schur target,
if this route is kept, is the bare non-majority absorption statement

```text
rho(X) >= 0
```

or an equivalent effective-shunt/PSD condition, not a uniform positive
coefficient bound.

## Machine-Checked Algebra Reduction

The subset form is reduced to a pointwise minority-current lemma in:

```text
problems/23/lean/SchurAbsorptionScratch.lean
```

Compiled by:

```text
cd workers/codex/formal-conjectures
lake env lean E:/Projects/ErdosProblems/problems/23/lean/SchurAbsorptionScratch.lean
```

Result:

```text
EXIT=0, no sorry/admit/axiom hits.
```

The theorem `pointwise_minority_implies_subset` proves the following rational
algebra wrapper.  If every vertex in a nonempty subset has nonnegative
overload, the subset total overload is non-majority, and every individually
minority vertex satisfies

```text
25*rho_o >= A - 2*a_o,
```

then the whole subset satisfies

```text
25*rho(X) >= A - 2*a(X).
```

This wrapper remains a valid algebra lemma, but its hypothesis is false in
general.  It is therefore no longer a live proof route.  The remaining Schur
proof target must be weaker than the pointwise quantitative statement, for
example bare non-majority absorption:

```text
rho(X) >= 0 whenever a(X) <= A-a(X).
```

## Proof Direction

The formerly proposed graph-theoretic lemma was:

> In a connected-`B`, `Gamma`-minimal maximum cut of a triangle-free graph,
> every non-strict-majority overloaded vertex has Schur normal current at least
> `(A-2a_o)/25`.

The C5 blowup quotient above falsifies that lemma.  A harmonic-threshold proof
must target bare absorption or PSD directly, without a uniform `(A-2a)/25`
surplus.

A plausible proof should use a threshold-switch/coarea argument on the harmonic
defect `psi=1-h`:

1. A violation `rho(X)<0` is a positive current deficit of `X`.
2. The deficit selects a family of shortest-row terminal shadows crossing from
   `X` into positive `psi`.
3. Since `X` is not a strict overload majority, the complement overload can
   pay the cut-neutrality tax.
4. The selected threshold switch is then connected-`B`, maximum, and
   `Gamma`-decreasing, contradicting `Gamma`-minimality.

This is the spectral analogue of the residual-Hall terminal-shadow mechanism,
but it avoids the false no-two-hole/single-miss statement by selecting shadows
from the harmonic current deficit rather than from arbitrary corridor holes.

## Local Probe Notes

The following exact probes constrain the proof shape.

### Dead shortcuts

Raw harmonic threshold flips are too naive.  On the out-of-scope hard-H3 side
of `h_blowup(3)`, `_descent_negmode_gate.scan_maxcut` finds `S` indefinite and
an exact negative Schur mode, but no neutral threshold set, and no threshold set
at all, has `dGamma <= phi^T H phi`.  Thus a proof cannot simply take
`{phi>t}` from an arbitrary negative Schur direction.

The overload-balanced two-level derivative shortcut is also false.  For
`z=1_X-(a(X)/(A-a(X)))1_{O\X}`, the inequality

```text
z^T S 1_O >= 0
```

fails already in small gamma-min census cases, even though Absorption-Hall
itself holds.  So `1_O` is not a minimizer under all overload-balanced
two-level perturbations.

Fixed explicit Schur supervectors do not close the problem.  The candidate
`phi=T+1` fails on `MycGrotzsch_N23`, and the simple Schur boundary vectors
`1`, `a`, `1/a`, `diag(S)`, and `1/diag(S)` all have exact failures on the
current gate battery.

### Surviving foothold

The vertex-local Hardy diagonal inequality

```text
T(v)-N <= Lstar[v,v]
```

has zero failures in `_gmin_local_flip.py` on 2446 gamma-min cuts / 22353
vertex rows, including the Mycielskian guardrail.  This does not imply Schur
Absorption-Hall by generic matrix theory, but it is a concrete
Gamma-minimality consequence that any final Schur proof should probably use.
