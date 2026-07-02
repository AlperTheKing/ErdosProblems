# PMS-5 Equal-Length Crux

Status: exact-supported, not proved.

## Current Reduction State

Claude independently confirmed the rowwise split:

```text
positive row debt appears only in:
  1. L>5 unique rows,
  2. L=5 multi rows.
```

The `L>5` unique branch is expected to be handled by the GM-switch /
Gamma-descent mechanism: the relevant switch changes lengths and can be
strict in `sum lambda(e)^2 < sum ell(f)^2`.

The remaining crux is the equal-length branch:

```text
L=5 multi rows.
```

Here Gamma is blind: if every crossing bad edge and every witnessed new bad
edge has length 5, then

```text
sum lambda(e)^2 = sum ell(f)^2
```

and Gamma-minimality gives no descent. The overload has to be paid by a
pentagonal reciprocal-slack / PMS-5 stability inequality.

## PMS-5 Target

For a length-5 row `P` in a positive K-component, with

```text
I(P) = sum_g (1/|cyc[g]|) * sum_{Q in cyc[g]} |P cap Q|,
eta = N^2/25 - |M|,
```

the needed coefficient is

```text
I(P) <= N + (2/3) eta.
```

Equivalently:

```text
75 * (I(P)-N) <= 2 * (N^2 - 25|M|).
```

This is exactly the coefficient needed for the multi branch of
`ROWWISE_SPLIT_PACKAGE_CODEX.md`.

## Equality Atom

The sharp finite atom is:

```text
graph6 = I?BD@g]Qo
row    = (7,5,8,6,9)
N      = 10
m      = 3
eta    = 1
I(P)   = 32/3
I(P)-N = 2/3
```

Thus PMS-5 is tight:

```text
I(P)-N = (2/3) eta.
```

## Seven-Cut Weighted Equality-Atom Subtarget

For the weighted quotient of the equality atom with weights `w0,...,w9`,
the current smallest algebraic PMS target is the seven-cut implication
recorded in `OC_PMS_PROOF_TARGET.md`.

Let

```text
m = w1*w9 + w2*w7 + w7*w9.
```

The seven quotient flip inequalities are:

```text
w5 >= w9
w6 >= w7
w3 + w5 >= w2 + w9
w4 + w6 >= w1 + w7
w0*w6 + w3*w8 + w5*w8 >= m
w0*w5 + w3*w8 + w5*w8 >= m
w0*w6 + w4*w8 + w6*w8 >= m
```

Target:

```text
75*(I(P)-N) <= 2*(N^2 - 25m)
```

for positive integer weights, or real weights with the natural normalization

```text
w_i >= 1.
```

The lower bound `w_i>=1` is essential: the all-equal ray `w_i=t<1` violates
the inequality.

## Current Exact Gates

Script:

```text
problems/23/writeup/_codex_ocpms_sevencut_gate.py
```

Fresh local exact rerun:

```text
python problems/23/writeup/_codex_ocpms_sevencut_gate.py \
  --mode exhaustive --max-weight 4
```

Result:

```text
total=1048576
selected=202898
min_numer=0 at all-ones
first_fail=None
VERDICT PASS
```

Fresh random stress:

```text
python problems/23/writeup/_codex_ocpms_sevencut_gate.py \
  --mode random --samples 300000 --max-weight 100 --workers 1 --seed 70128
```

Result:

```text
selected=36735
first_fail=None
VERDICT PASS
```

The attempted 32-worker run failed on this Windows sandbox with `WinError 5`
while creating a multiprocessing queue; this is an execution environment
issue, not a mathematical failure.

## Proof Shape

The current viable proof shape is not coordinate descent and not a simple
low-degree coefficientwise LP; both routes were gated and failed as proof
methods.

The promising route from `OC_PMS_PROOF_TARGET.md` is fixed-core endpoint KKT:

1. Fix the six core weights controlling the path denominators.
2. Reduce the four endpoint weights to a product of two quadrilaterals with
   one active quadratic cap.
3. Prove nonnegativity leafwise after clearing denominators.
4. Use the shifted positive coefficient-deficit reservoirs
   `(7/3-c27)`, `(7/3-c19)`, and `(2-c79)` to pay core nonuniformity.

This is now the concrete PMS-5 proof front.
