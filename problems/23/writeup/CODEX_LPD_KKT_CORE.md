# LPD KKT-Core Reformulation

This note records the exact obstruction form for the surviving layer-price /
LPD route.  It replaces the false selected-SPLIT/tight-cap certificates.

## LPD

For `y >= 0`, define

```text
w_{f,i}(y) = sum_{v in I_i(f)} y_v p_f(v)
H_f(y)     = sum_i sqrt(w_{f,i}(y)).
```

The dual layer-price inequality is

```text
sum_f H_f(y)^2 <= N sum_v y_v.                 (LPD)
```

The left side is homogeneous of degree one, so it is enough to normalize

```text
sum_v y_v = 1.
```

Then the target is

```text
F(y) := sum_f H_f(y)^2 <= N.
```

## KKT Equations

Assume first that all active layer masses `w_{f,i}` are positive.  Then

```text
dF/dy_v =
sum_f sum_{i: v in I_i(f)} p_f(v) H_f / sqrt(w_{f,i}).
```

Set

```text
b_{f,i}(y) = H_f / sqrt(w_{f,i}).
```

Then

```text
sum_i 1/b_{f,i} = 1
```

for every bad edge `f`, and

```text
dF/dy_v =
sum_{f,i: v in I_i(f)} b_{f,i} p_f(v).
```

So the KKT gradient is exactly the layer-price vertex budget.

By Euler homogeneity,

```text
sum_v y_v dF/dy_v = F(y).
```

Thus if `y` maximizes `F` on the simplex, there is a scalar `tau=F(y)` such
that

```text
y_v > 0  =>  budget_y(v) = tau,
y_v = 0  =>  budget_y(v) <= tau.
```

The LPD theorem is therefore equivalent to excluding a KKT core with

```text
tau > N.
```

## Exact Obstruction To Exclude

A counterexample to LPD can be sought as a finite support `U` and positive
weights `y_v` on `U` with `sum_U y_v=1`, satisfying:

```text
budget_y(v) = tau       for v in U,
budget_y(v) <= tau      for v notin U,
tau = F(y) > N.
```

Here every quantity is computed from square roots of rational linear forms in
`y`.  Equivalently, after introducing variables

```text
r_{f,i} = sqrt(w_{f,i}),
H_f = sum_i r_{f,i},
```

the equations are algebraic:

```text
r_{f,i}^2 = sum_{v in I_i(f)} y_v p_f(v),
budget_y(v) = sum_{f,i: v in I_i(f)} p_f(v) H_f / r_{f,i}.
```

The proof target is:

> No triangle-free connected-B gamma-min configuration admits such a KKT core
> with `tau > N`.

This is the corridor-capacity/KKT-core exclusion form of LPD.

## Corridor-Energy Form

LPD can be rewritten without prices.  For a bad edge `f` of length `L_f`,

```text
sum_i w_{f,i} = sum_v y_v p_f(v),
T(v) = sum_f L_f p_f(v).
```

Use the identity

```text
sum_{i<j} (sqrt(w_i)-sqrt(w_j))^2
  = L_f sum_i w_i - (sum_i sqrt(w_i))^2.
```

Summing over bad edges gives the equivalent inequality

```text
sum_v (T(v)-N) y_v
  <=
sum_f sum_{i<j} (sqrt(w_{f,i})-sqrt(w_{f,j}))^2.      (CE)
```

The right side is a corridor layer-spread energy.  Thus a counterexample is a
positive `y`-load whose overload mass cannot be routed through layer imbalance.

This is the clean proof target:

> For every nonnegative `y`, the weighted overload `sum_v (T(v)-N)y_v`
> is at most the total layer-spread energy of the shortest bad-edge corridors.

This form explains why rigid SPLIT fails: a single row can have bad shell
allocation, but the global layer-spread energy over all rows still pays for the
weighted overload.

## False Shortcuts

Current exact/float probes rule out the following simple price formulas:

1. `c_{f,i} proportional sqrt(A_{f,i})`, where
   `A_{f,i}=sum_{v in I_i(f)}p_f(v)S(v)`.
   This fails already at `N=11`:

   ```text
   graph6 = J?`Db_{N?]?
   side   = 00001111000
   worst gap = 7/3.
   ```

2. Length-only `L=5` central boost

   ```text
   c=(3/16,3/16,1/4,3/16,3/16)
   ```

   with uniform prices on other lengths.  This also fails at `N=11`:

   ```text
   graph6 = J???E?pNu\?
   side   = 00111111000
   worst gap = 5.
   ```

So a proof of `(CE)` must use the interaction of corridors, not only the
one-row layer profile or the row length.

## Diagnostic Witnesses

### Selected-SPLIT no-good witness

For

```text
graph6 = K??CE@A{?]Fc
cut 3  = 000011111100
```

the selected-SPLIT certificate fails, but float KKT/price optimization gives

```text
primal t* = 10.6375543317 < 12.
dual max = 10.6375543333 < 12.
```

The approximate active support is

```text
8,1,9,11,2,3,6,10
```

with weights roughly

```text
0.27361987, 0.22340499, 0.20302653, 0.19562064,
0.03840211, 0.03840211, 0.01720235, 0.01032141.
```

### Fixed-power price witness

For

```text
graph6 = J?`Db_{N?]?
side   = 00001111000
```

the simple price rule `c_{f,i} proportional sqrt(A_{f,i})` fails, but the full
layer-price optimizer gives

```text
primal t* = 32/3 = 10.666... < 11.
```

The optimal length-5 prices are clean:

```text
c = (3/16, 3/16, 1/4, 3/16, 3/16),
b = (16/3, 16/3, 4, 16/3, 16/3).
```

The active support in the float dual is approximately

```text
10 with weight 1/4,
2,3,4,5,6,7,8,9 with weight 3/32 each.
```

This case shows that universal prices must depend on global congestion, not
only on the row layer loads `A_{f,i}` or on the length.

## Claude Gate Request Shape

A useful exact gate is not a generic "LP" solver, because the primal is convex
with terms `p/c` and the dual has square roots.  The exact finite certificate
for a candidate price rule is:

```text
for every f: sum_i c_{f,i} <= 1,
for every v: sum_{f,i: v in I_i(f)} p_f(v)/c_{f,i} <= N,
c_{f,i} > 0,
```

with all `c_{f,i}` rational.  Claude can verify such a rule by Fraction.

For the proof search, the right exact-testable claims are KKT-core exclusions:
state a structural class of possible supports `U`, or a corridor inequality
that upper-bounds `F(y)` for all `y` supported on `U`, and test it against:

```text
K??CE@A{?]Fc,
J?`Db_{N?]?,
J???E?pNu\?,
iterated Mycielskians.
```
