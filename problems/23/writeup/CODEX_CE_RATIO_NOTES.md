# Codex CE / fan-averaging notes

Status: diagnostic only.  These are not proof gates; they identify the
boundary conditions for a proof of the corridor-energy / LPD form.

## 1. Pointwise path-load cap is false

ROWSUM-O for a bad edge `f` is the average, over uniformly chosen shortest
`B`-geodesics `P` for `f`, of

```text
sum_{v in P} S(v).
```

The tempting strengthening

```text
sum_{v in P} S(v) <= N
```

for every individual shortest geodesic is false.

Exact witness:

```text
g6   = I?BD@g]Qo
N    = 10
side = 0001111000
f    = (7, 9)
P    = (7, 5, 8, 6, 9)
sum_{v in P} S(v) = 32/3 > 10.
```

For the same row, geodesic averaging repairs it:

```text
f=(7,9), #geodesics=5
path loads: 38/5, 137/15, 137/15, 32/3, 47/5
average / ROWSUM = 689/75 < 10.
```

So any direct ROWSUM proof must use fan averaging; a pathwise injection or
pathwise corridor cap is too strong.

## 2. Corridor-energy ratio has no large slack

For LPD' / corridor energy,

```text
<T-N,y> <= E(y)

E(y) = sum_f sum_{i<j} (sqrt(w[f,i]) - sqrt(w[f,j]))^2.
```

The diagnostic script `_codex_energy_ratio_landscape.py` maximizes
`<T-N,y>/E(y)` over the simplex using SLSQP.  This is only a float landscape
scanner, not an acceptance gate.

N=10 scan:

```text
python problems/23/writeup/_codex_energy_ratio_landscape.py -n 10 --starts 4 --workers 32 --chunksize 32 --keep 20

graphs = 5800
cuts   = 16016
best ratio = 0.8893716427059782
```

Sharpest record:

```text
g6        = I?BD@g]Qo
side      = 0100101110
M         = ((0,5), (4,8), (6,8))
support   = (0,4,5,6,7,8,9)
T_support = (5,5,34/3,10,32/3,10,34/3)
left      = 0.4722134560605036
energy    = 0.5309517791952075
ratio     = 0.8893716427059782
```

This suggests there is little room for a universal strengthening
`<T-N,y> <= c E(y)` with a comfortable constant `c<1`.  The proof likely
needs the exact constant-one corridor-energy inequality.

## 3. Tight boundary calibration

The N=10 all-tie record

```text
g6   = I?rFf_{N?
side = 1111000000
M    = ((4,8), (4,9), (5,8), (5,9))
```

has four length-5 bad edges, all vertices have `T=N=10`, and the uniform
dual vector gives `E(y)=0`, `<T-N,y>=0`, and LPD value exactly `10`.

Thus the corridor-energy proof must be zero-margin on uniform product
corridors while still handling the near-sharp three-edge theta core above.

## 4. Sharp theta core becomes an exact PSD form

For the sharp `I?BD@g]Qo` CE-ratio core with

```text
side = 0100101110
M    = ((0,5), (4,8), (6,8))
```

the optimizer support has the symmetry classes

```text
A = {0,4},  T=5
B = {5,9},  T=34/3
C = {6,8},  T=10
D = {7},    T=32/3.
```

Let the per-vertex weights on these classes be `x,y,z,u`, and write

```text
a=sqrt(x), b=sqrt(y), c=sqrt(z), d=sqrt(u).
```

The CE left side is

```text
<T-N,y> = -10 a^2 + (8/3)b^2 + (2/3)d^2.
```

The layer-root vectors for the three bad edges are:

```text
(0,5): (a, c, sqrt(2/3)b, sqrt(2/3)d, b)
(4,8): (a, b, sqrt(2/3)d, sqrt(2/3)b, c)
(6,8): (c, sqrt(3/5)b, sqrt(4/5)d, sqrt(3/5)b, c)
```

Therefore the CE gap is a homogeneous quadratic form in `(a,b,c,d)`.
Its exact symmetric matrix is

```text
[[18, -2-2sqrt(6)/3, -2, -2sqrt(6)/3],
 [-2-2sqrt(6)/3, 214/15-4sqrt(6)/3,
  -4sqrt(15)/5-2-2sqrt(6)/3, -2sqrt(6)/3-4sqrt(3)/5-4/3],
 [-2, -4sqrt(15)/5-2-2sqrt(6)/3, 14,
  -4sqrt(5)/5-2sqrt(6)/3],
 [-2sqrt(6)/3, -2sqrt(6)/3-4sqrt(3)/5-4/3,
  -4sqrt(5)/5-2sqrt(6)/3, 118/15]]
```

All principal minors are positive; the smallest eigenvalue is approximately
`0.0912227065`.  So this near-sharp core has an exact quotient-PSD
certificate.

This suggests a possible proof style:

1. Reduce a KKT core to finitely many corridor quotient patterns.
2. For each quotient pattern, write CE in square-root class variables.
3. Prove the resulting radical/quadratic form is PSD.

The immediate obstruction is that literal layer-thinness is false.  In the
N=12 no-good witness and the `J?`Db_{N?]?` price witness, an active layer can
contain two active vertices.  Those cases still look quotient-thin, but not
per-vertex layer-thin.
