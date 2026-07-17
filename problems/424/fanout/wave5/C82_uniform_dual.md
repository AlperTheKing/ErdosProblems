# C82: uniform-dual obstruction at the base closure

## Verdict

There is no cutoff-uniform dual with eventually fixed local row
multipliers.  In every C56/C79 certificate, the multiplier on the base
closure

\[
u_5\le u_2+u_3
\qquad\text{or equivalently}\qquad
t_2+t_3-t_5\le1                                      \tag{1}
\]

is at least the number `K_X` of hard shapes through the cutoff.  Moreover,

\[
K_X\ge \max\left(0,\left\lfloor {X-24\over30}\right\rfloor\right). \tag{2}
\]

Thus this multiplier tends to infinity.  Any append-only, bounded-window,
or coefficient-at-row-birth recurrence is impossible: a successful dual
construction must revisit the row `5 <- (2,3)` globally as `X` grows.

For the full C75 dual, the same obstruction holds for the sum of the two
base multipliers on `closure_5_2_3` and `and_lower_5_0`.  This does not rule
out a globally updated recurrence, and no such uniform construction was
found.

## 1. Dual-gap lemma

Consider a minimization LP with rows `A_i x <= b_i`.  Write its row duals
in SciPy sign as `y_i<=0`, and put `alpha_i=-y_i>=0`.  Let `D` be the dual
objective.  Exact stationarity gives, for every point `x` inside the box,

\[
c\mathbin\cdot x-D
=\sum_i y_i(A_i x-b_i)
 +\sum_j \lambda_j(x_j-\ell_j)
 +\sum_j \nu_j(x_j-r_j),                              \tag{3}
\]

where `lambda_j>=0` and `nu_j<=0`.  Every term on the right is nonnegative
when its row is feasible.  If only rows in `J` are violated, with exact
residuals `delta_j>0`, then

\[
D\le c\mathbin\cdot x+
\sum_{j\in J}\alpha_j\delta_j.                        \tag{4}
\]

This is only exact weak duality and stationarity; no TU or TDI claim is
used.

## 2. C79 and C56 base load

For C79, set

```text
u_2=u_3=0,
u_n=1 for every other allowed n,
q_c=0 on every seed-2 edge.
```

All bounds hold.  A subadditivity row for an output `n>5` has at least one
nonseed factor, so `u_n<=u_a+u_b`.  Every boundary row also holds: it is
`0<=0` after both endpoints are nonseeds, and the two seed-end rows have
nonpositive drops.  The unique violated row is

```text
subadd_5_2_3:  u_5-u_2-u_3 <= 0,
```

with residual exactly `1`.  The objective is exactly `-K_X`.  Applying
(4) to any C79 dual of value at least zero proves

\[
\alpha_{5,2,3}\ge K_X.                                \tag{5}
\]

Under `t=1-u`, the C56 probe is

```text
t_2=t_3=1,
t_n=0 for every other allowed n,
q_c=0.
```

It satisfies every row except `closure_5_2_3`, again with residual `1`,
and its C56 objective is zero.  A C56 certificate must have dual value at
least `K_X`, so (4) gives the same lower bound (5) for its base-closure
multiplier.

## 3. Full C75 base load

In C75 set `s_2=s_3=f_2=f_3=1` and every other source, image, witness, and
boundary variable to zero.  The only positive row residuals are

```text
closure_5_2_3:  1
and_lower_5_0:  1
```

Every later factor pair contains a nonseed, so all later closure and AND
rows hold.  The image objective is zero.  Therefore every C75 dual proving
value at least `K_X` obeys

\[
\alpha_{\mathrm{closure}(5)}+
\alpha_{\mathrm{andLower}(5)}\ge K_X.                 \tag{6}
\]

Thus the obstruction is intrinsic to the full image LP, not an artifact of
the C56 projection or its lift.

## 4. Unboundedness

For every integer `k>=1`, put

\[
h_k=30k+24.
\]

Then `h_k` is even and \(h_k\equiv0\pmod3\), while

\[
h_k+1=5(6k+5).
\]

The factors are distinct and both are allowed.  Since `h_k+1` is not
divisible by `3`, `h_k` is hard-shaped.  The values `h_k<=X` give (2).
Combining (2), (5), and (6) proves that the base load is unbounded.

In particular, any recurrence under which the multiplier of each fixed old
row eventually stops changing is falsified.  A bounded shell update has
this property for row (1), so no fixed shell radius can emit the required
duals.  A surviving recurrence must carry an explicitly cutoff-dependent
global accumulator all the way back to the seed closure.

C60 Section 6 observed `closure_5_2_3=43371` in one saved dual at
`X=100000`, but explicitly did not exclude a different globally chosen dual
basis with bounded coefficient.  Inequality (5) is basis-independent and
closes that loophole: every valid C56/C79 certificate has unbounded base
load.

## 5. Stronger exact finite obstruction

The companion audit minimizes `alpha_5` over all current C79 duals satisfying
the exact stationarity equations, multiplier signs, and dual objective
`>=0`.  HiGHS is used only to discover both sides of this secondary LP;
every value is reconstructed as a `Fraction`, and both secondary primal and
dual stationarity are replayed exactly.

| `X` | `K_X` | exact minimum `alpha_5` |
|---:|---:|---:|
| 54 | 1 | 1 |
| 74 | 2 | 3 |
| 186 | 8 | 13 |
| 362 | 19 | 35 |
| 2000 | 147 | 310 |

Hence even the natural recurrence "add one unit to the base row per new
hard demand", namely `alpha_5=K_X`, is exactly false already at `X=74`.
At `X=2000`, stationarity forces `alpha_5>=310` although there are only
`147` hard objective coordinates.

## 6. Stored-dual audit and reproduction

The old discovery file `C79_fractional_boundary_tight_duals.json` is not a
certificate for the current unbounded-`q` model.  At `X=186` it has
`boundary_35_69=-2` and a listed lower multiplier `q_69=-1`.  In the current
model, q-column stationarity forces a boundary load at most `1` and every
lower-bound multiplier to be nonnegative.  Fresh current-model duals at
`54,74,186,362,2000` all replay exactly with objective zero and boundary
loads at most one.

```powershell
python -O problems/424/compute/wave5/C82_base_row_obstruction.py `
  --limits 54 74 186 362 2000 `
  --output problems/424/compute/wave5/C82_base_row_obstruction.json

python -O problems/424/compute/wave5/C82_uniform_dual_audit.py `
  --limits 54 74 186 362 2000 `
  --output problems/424/compute/wave5/C82_seed_coefficient_minima.json

python -O problems/424/compute/wave5/C79_exact_dual.py `
  --limits 54 74 186 362 2000 `
  --output problems/424/compute/wave5/C82_C79_current_exact_replay.json
```

All obstruction probes use integer arithmetic.  The secondary coefficient
audit uses exact rational replay and contains no `native_decide` step.
