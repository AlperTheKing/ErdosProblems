# Schur Minority-Current Lemma (Falsified Quantitative Target)

Status: the quantitative pointwise target in this note is falsified by larger
C5 blowups.  The note is kept as a record of the finite-battery mirage and of
the weaker bare Schur absorption target that may still survive.

This note rewrites the strict-majority Schur row-shunt gate as a current
statement.  It is the smallest target I currently see that is strong enough to
prove `|R| <= 1` and weak enough to match the exact guardrails.

## Setup

Let `G` be triangle-free and let `B` be a connected maximum cut chosen
`Gamma`-minimal among connected maximum cuts.  Let

```text
H = diag(N - T) + Lstar,
O = {v : T(v) > N},
U = V \ O.
```

Assume `H_UU` is nonsingular Stieltjes, and let `h` be the harmonic extension
of the boundary value `1` on `O`:

```text
h_o = 1                         (o in O),
H_UU h_U = -H_UO 1_O.
```

Because `H_UU^{-1} >= 0` and

```text
H_UU (1_U - h_U) = (N - T)_U >= 0,
```

we have

```text
0 <= h_u <= 1                   (u in U).
```

Write

```text
a_o := T(o) - N > 0,
A := sum_{p in O} a_p.
```

Since `H = diag(N-T)+Lstar` and `Lstar` is a weighted Laplacian, the Schur row
sum is

```text
rho_o = (Hh)_o
      = -a_o + I_o,
```

where the normal Hardy current from `o` to `U` is

```text
I_o := sum_{u in U} w^*_ou (1 - h_u).
```

Here `w^*_ou` is the aggregate `Lstar` conductance between `o` and `u`, after
collecting parallel cycle-laplacian edges.  Direct `O-O` conductances contribute
zero normal current because all overloaded boundary vertices have potential
`1`.

Thus

```text
rho_o < 0  <=>  I_o < a_o.
```

## Falsified Candidate Lemma

### Quantitative Minority Hardy-Current Lemma

The candidate was: for every overloaded vertex `o`,

```text
a_o <= A - a_o    ==>    I_o >= a_o + (A-2a_o)/25.
```

Equivalently,

```text
a_o <= A-a_o    ==>    rho_o >= (A-2a_o)/25.
```

This would imply the original strict-majority row-shunt gate and therefore at
most one negative Schur row sum.

The pointwise quantitative form also implies the full subset Absorption-Hall
inequality.  If `X subset O` is non-strict-majority, then `X` contains no
strict-majority vertex, so the singleton inequality applies to every
`o in X`.  Summing gives

```text
rho(X) >= (|X|A - 2a(X))/25 >= (A - 2a(X))/25 >= 0.
```

So the quantitative subset statement would reduce to this pointwise
minority-current lemma.

The lemma is false in general.  Exact finite gates up to the previous battery
passed, but scalable C5 blowups below falsify it.

## C5 Blowup Falsification

Consider the C5 blowup with sizes

```text
[k+1,k,k+1,k,k+1]
```

and a gamma-minimal maxcut leaving one minimum-product edge bad.  For a
minority overloaded vertex in the adjacent overloaded class, with the repository
rational `b = BETA[5]`, the quotient calculation gives

```text
a_o = 2,
A = 4k,
g_o = A - 2a_o = 4k - 4,
psi0 = 3/(3+b*k),
psi2 = 3/(3+2*b*k),
I_o = b*(k+1)*(psi0+psi2),
rho_o = I_o - 2.
```

The pointwise quantitative margin is

```text
25*rho_o - g_o.
```

Exact values:

```text
k=13, N=68:  +8.4838246968
k=14, N=73:  +4.8568737145
k=15, N=78:  +1.1863529360
k=16, N=83:  -2.5205246417   first failure
k=20, N=103: -17.6129970708
k=100,N=503: -334.3912356816
```

Thus no proof of the quantitative pointwise lemma can exist under the stated
hypotheses.  The live Schur route, if pursued, must prove a weaker blowup-stable
condition such as bare non-majority absorption:

```text
rho(X) >= 0 whenever a(X) <= A-a(X),
```

or the equivalent effective-shunt/PSD condition.

## Why This Is the Right Shape

The total normal current is

```text
sum_{o in O} I_o = sum_{u in U} (N - T(u)) h_u,
```

obtained by summing the harmonic equations on `U`.  So a deficient overloaded
vertex is not a simple shortage of total underload; it is a shortage in the
harmonic current allocation.  The exact gates say this shortage can occur only
when one vertex owns a strict majority of the overload mass.

This rules out two tempting but false strengthenings:

```text
I_o >= A - a_o
rho_o >= A - 2a_o.
```

They fail on the `MycGrotzsch_N23` guardrail at the apex: the apex is a strict
majority, but its current is still smaller than the total overload outside the
apex.

## Superseded Proof Strategy

Assume a minority vertex `o` has `I_o < a_o`.  Let `h` be the harmonic extension
above and consider the clipped potential

```text
psi = 1 - h.
```

Then `psi=0` on `O`, `0 <= psi <= 1` on `U`, and `I_o` is the `Lstar` flux from
`o` into positive `psi`.  A current deficit at a minority `o` means the rows
through `o` carry more overload than can be drained through their positive
`psi` boundary.

The intended Gamma-minimality argument is a threshold-switch coarea:

1. Decompose the `Lstar` energy of `psi` over shortest odd cycles.
2. For rows through `o`, use the deficit `a_o-I_o>0` to select a terminal
   prefix/suffix switch whose old bad-edge square mass exceeds the replacement
   boundary square mass.
3. Because `o` is not a strict-majority overload, the overload outside `o`
   supplies enough opposite-side positive row mass to make the selected switch
   cut-neutral, not cut-positive.
4. The switch is then connected-B, maximum, and Gamma-decreasing, contradicting
   the `Gamma` tie-break.

This is the Schur analogue of the row-side terminal-shadow argument, but with
the harmonic gauge `psi` replacing a hard row prefix.  It avoids the false
no-two-hole claim: the selected object is not an arbitrary corridor endpoint,
it is a threshold component of the harmonic current deficit.

## Finite Gate That Was Too Weak

The falsified lemma is gateable from existing objects:

```text
build H, O, U, h;
for o in O:
    a_o = T[o] - N
    I_o = a_o + rho_o
    assert a_o > A-a_o or rho_o >= (A-2*a_o)/25
```

Equivalently:

```text
25*rho_o >= A-2*a_o for every minority overloaded o.
```

This was verified locally by `_schur_absorption_coeff_gate.py` and independently
by Claude's former full Schur acceptance battery for all subsets.  The larger
C5 blowup quotient shows that battery did not cover the graphon-scale
obstruction.

## Falsified Split Attempt

The pointwise target was temporarily split into a static conductance-excess
inequality and a broad current-harvest inequality.  This split survives the
small census-style battery, but it is false on larger gamma-minimal C5 blowups.
It should not be used as a proof target.

For a minority overloaded vertex `o`, set

```text
cU_o = sum_{u in U} (-H[o,u]),
e_o  = cU_o - a_o,
g_o  = A - 2a_o.
```

The static conductance-excess inequality is

```text
g_o <= 5e_o.
```

Equivalently,

```text
5*cU_o >= A + 3a_o.
```

This remains useful structure, but it is not enough by itself: the false
companion

```text
rho_o >= e_o/5
```

fails on blowups, so the proof must keep the harmonic redistribution through
`U`.

The broader current-harvest candidate was

```text
25*rho_o >= 4e_o.
```

Let `h_U` be the harmonic extension with boundary value `h=1` on `O`, and
put

```text
psi_u = 1 - h_u        (u in U).
```

Then

```text
I_o   = sum_{u in U} c_ou psi_u,
rho_o = I_o - a_o,
cU_o  = sum_{u in U} c_ou,
```

where `c_ou=-H[o,u]`.  Thus the current-harvest inequality is exactly

```text
sum_{u in U} c_ou (25*psi_u - 4) >= 21*a_o.
```

Equivalently, the `c_ou`-weighted average of `psi` over the direct
`o`-to-`U` conductance must satisfy

```text
avg_o(psi) >= 4/25 + (21/25)*(a_o/cU_o).
```

Small local exact gate result:

```text
minority vertices = 1352
failures = 0
minimum margin ≈ 0.36264021139699065
minimum case = blowup(5,4,5,4,5)
```

Larger blowup stress kills this candidate.  On canonical C5 blowups with sizes
`[k+1,k,k+1,k,k+1]`, the four maxcut patterns leaving a minimum product edge
bad are gamma-minimal among the tied connected-B maxcuts.  They have:

```text
[6,5,6,5,6], N=28:
  min(25*rho_o - 4e_o)       ≈ -8.6044531659
  min(25*rho_o - (A-2a_o))   ≈ +33.7268039209

[10,9,10,9,10], N=48:
  min(25*rho_o - 4e_o)       ≈ -48.2312657103
  min(25*rho_o - (A-2a_o))   ≈ +22.3208294343

[14,13,14,13,14], N=68:
  min(25*rho_o - 4e_o)       ≈ -90.2891085056
  min(25*rho_o - (A-2a_o))   ≈ +8.4838246968
```

Thus the harvest split is a small-battery artifact.  The following direct
pointwise inequality was the next attempted target:

```text
a_o <= A-a_o  ==>  25*rho_o >= A-2a_o.
```

The C5 quotient above falsifies this pointwise inequality for `k>=16`, so this
is also only a negative datum.  The surviving Schur target is coefficient-free
bare absorption/PSD, not a singleton positive-margin statement.

### Bottleneck Diagnostics

The nonuniform `C5` blowup `blow(5,4,5,4,5)` explains why the false harvest
candidate looked plausible in the small battery.  For a weakest minority
vertex:

```text
a_o       = 2
cU_o      ≈ 13.8190118931
rho_o     ≈ 1.9055475113
avg_o(psi)≈ 0.2826213293
required  ≈ 0.2815716444
```

The direct neighbors split into two equal-conductance shells with
`psi≈0.2134439901` and `psi≈0.3517986686`.

The small-battery unique high-ratio corner was `MycGrotzsch_N23`, vertex `2`;
after larger blowup stress, this is no longer the right decomposition:

```text
a_o       ≈ 5.5473530136
cU_o      ≈ 10.4006158674
rho_o     ≈ 1.0958902779
avg_o(psi)≈ 0.6387355688
harvest required ≈ 0.6080289043
target required  ≈ 0.6258659582
```

The fixed cloned side of the uniform `2`-blowup of `MycGrotzsch_N23` violates
the pointwise target, but CP-SAT proves that side is not maximum:

```text
fixed cloned cut = 216
optimal cut      = 220
```

On the optimal `46`-vertex side found by CP-SAT, the split has:

```text
|O|=4, high_ratio=0, target_fail=0, harvest_fail=0.
```

So the cloned-side failure is an out-of-scope guardrail, not a counterexample
to the maxcut/gamma-min scoped target.

## Remaining Singleton-Apex Target

Once the minority-current lemma gives `|R|<=1`, the only remaining
graph-theoretic target is the singleton star rescue:

```text
rho_a + sum_{p != a} c_ap rho_p/(c_ap + rho_p) >= 0.
```

In current exact gates this is only exercised by `MycGrotzsch_N23`.  A proof
should probably use the same harmonic threshold framework, but now with the
strict-majority apex as the only current-deficient terminal and the other
overloaded vertices as positive shunt reservoirs.
