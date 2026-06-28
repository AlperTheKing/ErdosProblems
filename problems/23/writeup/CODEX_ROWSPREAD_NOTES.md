# ROWSUM Average-To-Max Obstructions

Claude verified the averaged Gram-trace inequality

```text
sum_f ROWSUM(f) = sum_v S(v)^2 <= N * |M|.
```

This leaves the gap from average row sum to maximum row sum.  I tested
several exact strengthenings; the following are dead.

## 1. Dilution Correction Dies

Candidate:

```text
ROWSUM(f) + c * (ell(f) - <p_f,p_f>) <= N
```

for any fixed `c > 0`.

Reason: the N=10 odd-blowup calibration `I?rFf_{N?` has a row with
`ROWSUM(f)=N=10` and `ell(f)-<p_f,p_f>=3/2`.  Therefore every positive
coefficient is impossible.

The stronger `c=1` candidate also fails earlier:

```text
N=8, G?bF`w, row (2,7):
ROWSUM=65/9, self=37/9, ell=5.
```

## 2. Load-Variance Correction Dies

Candidate:

```text
ROWSUM(f) + c * Var_{p_f}(S) <= N,
Var_{p_f}(S)=sum_v p_f(v)*(S(v)-ROWSUM(f)/ell(f))^2.
```

It passed the local N<=11 census for `c=1/N`, but fails on the full N=12
census:

```text
g6 = K??CB@OBDOAp
side = 111111000000
M = {(6,11),(10,11)}
f = (6,11)
unique path = [6,0,10,4,9,5,11]
S on path = [1,1,2,2,2,2,2]
ell = 7
ROWSUM = 12 = N
Var = 10/7
```

So equality in ROWSUM-O is not only the constant-load all-tie blow-up
mode.  It also occurs in nested unique-path configurations: the shorter
bad path `[10,4,9,5,11]` is contained in the longer equality path.

## 3. Naive Geodesic-Interval Charging Dies

Candidate structural fact: intersections of shortest bad-edge geodesics
are contiguous on each geodesic.

False at N=7:

```text
g6 = F?bbo
side = 1111000
f = (4,6)
P = [4,0,5,1,6]
Q = [4,0,5,2,6]
intersection = {4,0,5,6}
```

The intersection has a shared prefix and a shared endpoint with a split in
the middle.  Any intersection-charging proof must handle branching geodesic
families, not just intervals on a path.

## Consequence

The average-to-max route needs a correction that vanishes both on:

1. all-tie odd blow-ups, and
2. nested-path equality configurations such as `K??CB@OBDOAp`.

Simple positive row penalties based on dilution or load variance cannot
prove ROWSUM-O.
