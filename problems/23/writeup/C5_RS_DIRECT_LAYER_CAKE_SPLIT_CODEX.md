# C5-RS Direct Layer-Cake Proof Split

Date: 2026-07-01

This file records the current live route after Claude exact-falsified row-majorization (RM). It is a proof-obligation split, not a completed proof.

## Target

For an all-length-5 K-component row `Q=(q0,...,q4)`, define

```text
s_i = Tw_C(q_i)
tau = 5m/N
eta = N^2/25 - m
B_C5 = (1 + 25/N) eta
```

C5-RS is

```text
sum_i max(0, s_i - tau) <= B_C5.
```

Equivalently, for every nonempty `A subset {0,...,4}`,

```text
L(A) := sum_{i in A}(s_i - tau) <= B_C5.        (subset C5-RS)
```

The full mask is

```text
A = {0,1,2,3,4},
L(A) = row_sum(Q) - 5tau.
```

Since `5tau = N - 25eta/N`, full-mask C5-RS is exactly

```text
row_sum(Q) <= N + eta.                          (full row-sum)
```

Thus the equal-length C5 branch can be split into:

1. proper masks: `A != full`, a genuine layer-set/high-coordinate bound;
2. full mask: row-sum stability.

## Stronger proper-mask candidate

The sharper candidate now isolated for exact testing is:

```text
C5 PROPER-MASK LIFT:
for every nonempty proper A,
  L(A) <= (25/N + 2/3) eta.                     (proper lift)
```

This is stronger than C5-RS on proper masks. It deliberately excludes the full mask, because Claude reported that global C5-LIFT can fail on non-C5-hom scale examples, and those failures may be full-mask row-sum failures only.

If C5 PROPER-MASK LIFT is true, then the only remaining all-length-5 obstruction is the full row-sum inequality.

## Full-mask branch

Full-mask C5-RS is:

```text
row_sum(Q) <= N + eta.
```

The sharper C5-HOM/seven-cut/PMS branch asks for

```text
row_sum(Q) <= N + (2/3) eta
```

in the sharp C5-hom/weighted pentagonal setting, tight at the sparse equality atom `I?BD@g]Qo`.

For non-C5-hom components, do not assume C5-LIFT. The safe full-mask target remains `row_sum<=N+eta`.

## Guardrails

Dead routes:

1. Do not use `sum_i(s_i-N/5)_+ <= eta`; Claude exact-falsified it.
2. Do not use row-majorization by C5 class sizes; Claude exact-falsified RM on `H?AFBo]`.
3. Do not assume every length-5 component has a C5 homomorphism; Grotzsch refutes it.
4. Do not rely on a fixed non-C5-hom slack floor; Claude's MycGrotzsch stress suggests the margin can shrink.

## Current exact evidence for proper masks

Local census `N<=11`, positive eta only:

```text
proper-mask C5 PROPER-MASK LIFT: 0 fails.
```

Weighted quotient seeds, qmax only, weights in `{1,2}`:

```text
equality seed: proper-mask C5 PROPER-MASK LIFT 0 fails, full mask tight at all-ones.
sibling seed:  proper-mask C5 PROPER-MASK LIFT 0 fails, full mask min margin 1/3 at all-ones.
```

Pending: Claude broad-battery gate for C5 PROPER-MASK LIFT.
