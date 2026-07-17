# C76: image-LP dual schema and the exact TU/TDI obstruction

## Verdict

The C75 constraint matrix is **not totally unimodular**, and its bounded
integer-RHS formulation is **not TDI**.  Both failures occur already at
cutoff `21`.  The TDI failure is exact: the integral objective

\[
        2s_{11}-2q_{11}-q_{21}
\tag{1}
\]

has LP optimum `-1/2` and integer optimum `0`.  An exact rational primal and
dual attain `-1/2`, and a `7 x 7` active submatrix has determinant `2`.
Thus the integral optima seen for the C75 objective cannot follow from a
matrix-wide TU or TDI theorem.

This is not a counterexample to the C23 inequality: (1) rewards boundary
variables, whereas the C75 objective penalizes them.  No cutoff-uniform dual
for the C75 objective was found.  The weakest exact replacement obtained is:

1. the stored C75 duals at `54,74,186,362` replay over the rationals and prove
   the image inequality at those four cutoffs for every source set;
2. every feasible C75 point projects to the splitless-closed C56 relaxation;
   consequently every uniform C56 dual certificate lifts mechanically to a
   C75 dual certificate.

The missing uniform object is therefore the global C56/C65 bank certificate,
not an integrality theorem for the C75 matrix.  Finite survival through
`200000` does not supply that object.

## 1. What the C75 objective proves

Fix a cutoff `X`.  Let `V_X` be the allowed values through `X`, and let `K_X`
be the hard-shaped values.  Denote the C75 polytope by `P_X`.  It has source
variables `s`, image variables `f`, pair-witness variables `w`, and seed-2
boundary variables `q`.

For a Boolean point arising from a forward-closed source `S`, the
linearizations give

\[
 f_n=1_{n\in F(S)},\qquad
 q_{2m-1}=1_{m\notin F(S),\,2m-1\in F(S)}.
\]

Hence its objective is exactly

\[
 \begin{aligned}
 J_X
   &=\sum_{h\in K_X}f_h+\sum_{2m-1\le X}q_{2m-1}\\
   &=|K_X|-H_{F(S)}(X)+Q_{F(S)}(X).
 \end{aligned}                                      \tag{2}
\]

Therefore, for every `X`, the relaxation bound

\[
       \min_{x\in P_X}J_X(x)\ge |K_X|               \tag{3}
\]

implies the C23 unconditional image inequality at `X`, simultaneously for
every forward-closed allowed `S` containing `2,3`.  This explains why a dual
lower bound is useful even when the optimizing primal point is fractional.

## 2. Projection and uniform dual lifting

Let `R_X` be the C56 splitless-closed relaxation in variables `(t,q)`:

* `t_2=t_3=1`;
* `t_n=0` for every splitless nonseed;
* `t_a+t_b-t_n<=1` whenever `n+1=ab` is admissible; and
* `t_{2m-1}-t_m-q_{2m-1}<=0` on every seed-2 edge.

All variables have bounds `[0,1]`.

### Proposition 2.1 (projection)

For every integer cutoff `X>=3` and every `(s,f,w,q) in P_X`, the point
`(t,q)=(f,q)` belongs to `R_X`.

### Proof

The seed and splitless conditions follow directly from the C75 bounds.  Fix
an admissible pair `a<b` with `n=ab-1<=X`, and let `w` be its C75 witness.
For a nonseed factor C75 has `f_a<=s_a`; for a seed, `f_a=s_a=1`.  The same
holds for `b`.  The witness rows give

\[
       s_a+s_b-w\le1,\qquad w\le f_n.
\]

Adding these four inequalities, with seed equalities substituted where
needed, yields

\[
       f_a+f_b-f_n\le1.                              \tag{4}
\]

Finally, the C75 `boundary_lower` row is precisely

\[
       f_{2m-1}-f_m-q_{2m-1}\le0.                    \tag{5}
\]

Thus every defining row of `R_X` holds.  QED.

The objectives in (2) and in `R_X` are the same, so Proposition 2.1 gives

\[
       \min_{P_X}J_X\ \ge\ \min_{R_X}J_X.            \tag{6}
\]

It also gives an explicit dual lift.  Replace a multiplier `mu>=0` on the
C56 closure row (4) by multiplier `mu` on each of the corresponding C75
rows

```text
image_subset_a, image_subset_b, and_lower_n_pair, support_lower_n_pair.
```

When a factor is `2` or `3`, use its fixed equality instead of an
`image_subset` row.  Boundary multipliers lift through (5), and box/fixed
multipliers lift directly.  Thus, for every cutoff `X`, any C56 dual of value
at least `|K_X|` produces a C75 dual of the same value.  This is a uniform
schema, conditional on constructing the C56 multipliers; it is not itself a
construction of them.

## 3. Exact non-TU minor

At cutoff `21`, take the rows

```text
closure_11_2_6, and_right_11_0, support_upper_11,
and_right_21_0, support_upper_21,
boundary_parent_21, boundary_child_21
```

and columns

```text
s_6, s_11, w_11_0, f_11, w_21_0, f_21, q_21.
```

The resulting submatrix is

\[
\begin{pmatrix}
 1&-1& 0& 0& 0& 0&0\\
-1& 0& 1& 0& 0& 0&0\\
 0& 0&-1& 1& 0& 0&0\\
 0&-1& 0& 0& 1& 0&0\\
 0& 0& 0& 0&-1& 1&0\\
 0& 0& 0& 1& 0& 0&1\\
 0& 0& 0& 0& 0&-1&1
\end{pmatrix},
\qquad \det=2.                                      \tag{7}
\]

These are actual C75 rows and unfixed columns.  Equation (7) is an exact
counterexample to total unimodularity.

## 4. Exact non-TDI objective

Still at cutoff `21`, the unique admissible support of `11` is `2*6`, and
the unique support of `21` is `2*11`.  Since `s_2=f_2=1`, the C75 rows force

\[
 f_{11}=s_6,\qquad f_{21}=s_{11},\qquad s_6\le s_{11}.
\tag{8}
\]

Also `f_6=0`, so the boundary linearizations force

\[
 q_{11}=s_6,qquad
 q_{21}\le1-s_6,qquad q_{21}\le s_{11}.             \tag{9}
\]

Put `d=s_11-s_6>=0`.  Adding the last two bounds gives
`2q_21<=1+d`.  Therefore every fractional feasible point satisfies

\[
 \begin{aligned}
 2s_{11}-2q_{11}-q_{21}
   &=2d-q_{21}\\
   &\ge 2d-\frac{1+d}{2}
    =\frac{3d-1}{2}\ge-\frac12.                     \tag{10}
 \end{aligned}
\]

Equality is feasible.  Set the following variables to `1/2`:

```text
s_6 s_11 s_21 f_11 f_21 w_11_0 w_17_1 w_21_0 q_11 q_21
```

set `s_n=f_n=1` for `n in {2,3,5,9,14,17}`, set
`w_5_0=w_9_0=w_14_0=w_17_0=1`, and set all remaining variables to zero.
Every C75 row and bound then holds exactly.

For a Boolean point, `(s_6,s_11)` can only be `(0,0),(0,1),(1,1)`.  The
three objective values are respectively `0,1,0`.  Thus

\[
      \min_{P_{21}}(2s_{11}-2q_{11}-q_{21})=-\frac12,
      \qquad \min_{P_{21}\cap\{0,1\}^N}=0.           \tag{11}
\]

The exact dual attaining `-1/2` has the following nonzero SciPy-sign
multipliers (`y<=0` for `<=` rows):

| row or bound | multiplier |
|---|---:|
| `closure_11_2_6` | `-3/2` |
| `and_right_11_0` | `-3/2` |
| `support_upper_11` | `-3/2` |
| `and_right_21_0` | `-1/2` |
| `support_upper_21` | `-1/2` |
| `boundary_child_11` | `-2` |
| `boundary_parent_21` | `-1/2` |
| `boundary_child_21` | `-1/2` |
| lower bound `s_2>=1` | `3/2` |

Exact stationarity holds in every column, and the dual objective is
`-3/2-1/2+3/2=-1/2`.  Since the complete bounded description has integral
right-hand side and (1) is integral, a TDI description would have an
integral optimal dual and hence an integral dual objective.  Equation (11)
rules this out.

The obstruction is the glued boundary block: fractional equality
`f_11=f_21=1/2` permits `q_21=1/2`, although the corresponding Boolean
boundary is zero when both image values agree.  Each individual AND block is
ideal; their arithmetic identification creates the determinant-two cycle.

## 5. Rational replay of the tight duals

The stored C75 dual JSON was replayed without floating-point acceptance.
For each row below, the verifier reconstructs every multiplier as a
`Fraction`, checks its sign, checks stationarity in every column against the
integer matrix, and checks the exact dual objective.  It also reconstructs
an integral optimizer and checks every primal row with fractions.

| cutoff | hard shapes | primal = dual | nonzero row/lower/upper | max denominator |
|---:|---:|---:|---:|---:|
| 54 | 1 | 1 | 19 / 19 / 6 | 1 |
| 74 | 2 | 2 | 26 / 24 / 8 | 1 |
| 186 | 8 | 8 | 68 / 58 / 18 | 1 |
| 362 | 19 | 19 | 128 / 112 / 33 | 1 |

Consequently, for every

\[
 X\in\{54,74,186,362\}
\]

and every forward-closed allowed source `S` containing `2,3`, one has

\[
        H_{F(S)}(X)\le Q_{F(S)}(X).                   \tag{12}
\]

This is a finite exact theorem, not a uniform proof.

## 6. Remaining uniform frontier

Proposition 2.1 identifies the smallest surviving certificate route.  It is
enough to prove, for every cutoff `X` and every forward-closed
`T subseteq V_X` containing `2,3` and excluding every splitless nonseed,

\[
 \#\{h\in K_X:h\notin T\}
 \le
 \#\{m:m\notin T,\ 2m-1\in T,\ 2m-1\le X\}.          \tag{13}
\]

This is the C56 splitless-closed boundary theorem.  The C65 endpoint
bank/min-cut statement is a still stronger sufficient formulation.  A proof
of either gives the desired cutoff-uniform C75 multipliers through the lift
in Section 2 and proves C23.  The determinant and TDI counterexample show
that generic Horn acyclicity or LP integrality cannot be that proof; the
certificate must use the global arithmetic transfers isolated in C65.

## 7. Reproduction

```powershell
python -m py_compile problems/424/compute/wave5/C76_lp_dual_schema.py

python problems/424/compute/wave5/C76_lp_dual_schema.py `
  --output problems/424/compute/wave5/C76_lp_dual_schema.json

python -O problems/424/compute/wave5/C76_lp_dual_schema.py `
  --output problems/424/compute/wave5/C76_lp_dual_schema_replay.json
```

The checker uses explicit exceptions rather than `assert`; optimization only
rediscovers the four integral tight-cutoff primals.  All accepted primal and
dual equalities, the projection identities, and determinant (7) are checked
with exact integer or rational arithmetic.
