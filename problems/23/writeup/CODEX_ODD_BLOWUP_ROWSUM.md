# Odd-Cycle Blow-Up ROWSUM-O Lemma

Status: proved for the single-bad-edge-class odd-cycle blow-up family.

This family is now mandatory in the stress gate because the non-uniform
`C7(3,423,173,7,176,7,423)` example refutes the overloaded-vertex diagonal
Schur surrogate.  The actual bad-edge Gram row-sum `ROWSUM-O` still holds
for the whole one-bad-class odd-cycle blow-up family.

## Setup

Let `G=C_m[x_0,...,x_{m-1}]`, where `m` is odd and all `x_i>0`.  Suppose
the maximum cut leaves the adjacent class edge `V_0V_1` monochromatic, and
that this is a minimum adjacent product:

```text
x_0 x_1 <= x_i x_{i+1}       for every i mod m.
```

Every bad edge has one endpoint in `V_0` and one in `V_1`, and its unique
class geodesic follows the complementary path through

```text
V_0,V_{m-1},...,V_2,V_1.
```

For a fixed bad edge `f`, the overlap row sum is

```text
(O 1)_f
  = x_0 + x_1 + x_0 x_1 * sum_{i=2}^{m-1} 1/x_i.
```

Indeed, another bad edge shares the `V_0` endpoint in `x_1` choices, shares
the `V_1` endpoint in `x_0` choices, and every intermediate class contributes
`x_0 x_1 / x_i`.

## Lemma

```text
(O 1)_f <= N = sum_i x_i.
```

Equivalently,

```text
x_0 x_1 * sum_{i=2}^{m-1} 1/x_i <= sum_{i=2}^{m-1} x_i.
```

## Proof

Put

```text
y_i := x_0 x_1 / x_i       (2 <= i <= m-1).
```

Since `x_0x_1` is a minimum adjacent product, for every `2<=i<=m-1`,

```text
x_{i-1} x_i >= x_0 x_1,
x_i x_{i+1} >= x_0 x_1,
```

where indices are cyclic.  Hence

```text
y_i <= x_{i-1},
y_i <= x_{i+1}.
```

Therefore

```text
sum_{i=2}^{m-1} y_i
  <= 1/2 * sum_{i=2}^{m-1} (x_{i-1}+x_{i+1})
  = 1/2*(x_0+x_1+x_2+x_{m-1}) + sum_{i=3}^{m-2} x_i.
```

It remains to compare the two endpoint terms.  The minimum-product
conditions on the edges `V_1V_2` and `V_{m-1}V_0` give

```text
x_1 x_2 >= x_0 x_1  =>  x_2 >= x_0,
x_{m-1} x_0 >= x_0 x_1  =>  x_{m-1} >= x_1.
```

Thus

```text
x_0+x_1 <= x_2+x_{m-1}.
```

Substituting into the previous bound gives

```text
sum_{i=2}^{m-1} y_i <= sum_{i=2}^{m-1} x_i,
```

which is exactly `ROWSUM-O` for this row.  Equality forces the usual
uniform/tight conditions along the path.

## Exact Diagnostics

Script:

```text
problems/23/writeup/_codex_odd_blowup_full_inverse.py
```

The script now reports three different margins:

```text
spec_margin        = N - (O1)_f
row_min            = overloaded-vertex diagonal Schur surrogate
full_min           = canonical full-inverse overloaded-row surrogate
```

The large GPT-Pro `C7` counterexample has:

```text
spec_margin = +32960131/74448
row_min     = -3540476630161/3271659686685
full_min    = +39947678772/63012307
```

Targeted `C7` obstruction-family sweep:

```text
samples=200000
quotient_instances=131198
spec_rowsum_fails=0
diagonal_rowsum_fails=95
```

Random quotient sweep over `m=5,7,9,11`, `100000` samples each:

```text
spec_rowsum_fails=0 for all four odd lengths.
```

So odd-cycle blow-ups are now explained: they are harmless for the actual
`ROWSUM-O/SPEC` target, but they are fatal for overloaded-row diagonal
surrogates.

Claude Step-2 independently confirmed the same formula and proof
(`2026-06-28T16:50:00Z`): `~526000` large odd-cycle blow-ups
`C5..C13`, `N` up to `4000`, had `SPEC/ROWSUM-O` failures `0`; the
quotient formula matched this note exactly.
